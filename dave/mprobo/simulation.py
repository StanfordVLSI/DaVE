# A unit simulation run

import sys
import tempfile
import copy
import os
import shutil
import subprocess
import dave.common.misc as misc
import stat
import numpy as np
import pickle as pkl

from dave.common.davelogger import DaVELogger
from dave.common.misc import get_basename
from simulatorinterface import NCVerilogAMS, NCVerilogD, VCSSimulator
from testbench import TestBench
import dave.mprobo.mchkmsg as mcode
from dave.mprobo.environ import EnvFileLoc

#-----------------------
class RunVector(object):
  ''' Simulate a model with a given test vector '''
  def __init__(self, test_cfg, sim_cfg, port, tb_raw_file, use_cache, csocket, logger_id='logger_id'):
    self._logger_id = logger_id
    self._logger = DaVELogger.get_logger('%s.%s.%s' % (logger_id, __name__, self.__class__.__name__))

    self._test_cfg = test_cfg
    self._sim_cfg = sim_cfg
    self._port = port
    self._tb_raw_file = tb_raw_file
    self._use_cache = use_cache
    self._csocket = csocket
    
    self._create_instance()

  def run(self, vector, workdir):
    ''' Run a simulation with given vector at dir=workdir
        Returns a tuple of ( is successful ?, measurement data) 
        after validating measurement data
    '''
    cached = self._use_cache
    if cached and not os.path.exists(workdir):
      self._logger.warn(mcode.WARN_025 % workdir)
      cached = False

    if not cached: # dump vector if not using cached
      misc.make_dir(workdir, self._logger)
      with open(os.path.join(workdir, 'vector.dat'), 'wb') as f: 
        pkl.dump(vector, f)
    self._sim.run(vector, cached, workdir) # run a simulation
    self._pp.run(workdir, cached) # run postprocessing routine(s) if any
    if self._csocket: # client-server mode, ask for measurement
      relpath = os.path.relpath(workdir)
      self._upload_measurement_client(relpath)
    # read/validate measurement
    meas = self.read_measurement(workdir)
    result = self._validate_measurement(meas, self._port)
    #try:
    #  result = self._validate_measurement(meas, self._port)
    #except: # somehow, simulation was unsuccessful. sys exit.
    #  self._logger.warn(mcode.WARN_014)
    #  self._logger.warn(mcode.WARN_015)
    #  self._logger.warn(self._sim.get_log())
    #  self._logger.warn(mcode.WARN_016)
    #  self._logger.warn(self._pp.get_log())
    #  sys.exit()
    return result

  def read_measurement(self, workdir): # read measurement from simulation or postprocessed result files 
    measurement = {}
    for p in self._port.get_output_port_name():
      fname = 'meas_' + p + '.txt'
      _meas_file = fname if os.path.isfile(fname) else os.path.join(workdir, fname)
      try:
        measurement[p] = (np.loadtxt(_meas_file)).tolist()
      except Exception, e:
        self._logger.debug(mcode.DEBUG_007 % (workdir, e))
        return False, None
    self._logger.debug(mcode.DEBUG_008 % workdir)
    return True, measurement # success, measurement data dictionary

  def _create_instance(self): # create simulation and postprocess classes
    # simulation instance
    self._sim = VerilogSimulation(self._test_cfg, self._sim_cfg, self._tb_raw_file, csocket=self._csocket, logger_id=self._logger_id)
    # post processor instance
    pp_scripts, pp_cmd = self._test_cfg.get_postprocessor()
    self._pp  = PostProcessSimulation(pp_scripts, pp_cmd, self._csocket, self._logger_id) 

  def _validate_measurement(self, measurement, port): # validate if all outputs meets specifications
    return ( all([measurement[0]] + [port.get_by_name(p).is_valid(v) for p,v in measurement[1].items()]), 
             measurement[1] )

  def _upload_measurement_client(self, rel_simpath): # asking client to upload measurement data
    outport = self._port.get_output_port_name()
    files = [os.path.join(rel_simpath,'meas_%s.txt' % k) for k in outport]
    self._csocket.issue_command('@upload %s' % ' '.join(files))

class VerilogSimulation(object):
  ''' Run a Verilog simulation by instantiating one of Verilog simulators.
    - sim_cfg is either golden simcfg or revised simcfg
    - raw_tb_file: raw testbench file (vector unbound) including directory info
  '''
  def __init__(self, test_cfg, sim_cfg, raw_tb_file, csocket=None, logger_id='logger_id'):
    self._csocket = csocket
    self._logger_id = logger_id

    self._raw_tb_file = raw_tb_file
    self._model_type = sim_cfg.get_model()
    self._hdl_files = sim_cfg.get_hdl_files()
    self._simulator_name = sim_cfg.get_simulator_name() 
    self._simulator_option = sim_cfg.get_simulator_option()
    self._ams_option = { 'ams_controlfile' : sim_cfg.get_ams_control_filename(),
                         'ams_circuits' : sim_cfg.get_circuits(),
                         'spice_lib' : sim_cfg.get_spice_lib(),
                         'ams_connrules' : sim_cfg.get_ncams_connrules()}

    self._option={'workdir' : '',
                  'sweep_file' : sim_cfg.get_sweep(),
                  'hdl_files' : [], 
                  'ic' : self._get_ic(test_cfg, sim_cfg),
                  'temperature': test_cfg.get_temperature(),
                  'sim_time': test_cfg.get_simulation_time(),
                  'timescale' : test_cfg.get_timescale()
            }

  def run(self, vector, use_cache, workdir='/tmp'):
    ''' run simulation '''
    # list of hdl files with the testbench 
    self._option.update({ 'workdir' : workdir,
                          'hdl_files' : [self._bind_vector_to_testbench(vector, workdir)] + self._hdl_files })
    self._ams_option.update({'vector':vector})
    if self._csocket: # if client-server mode
      rootdir = workdir[:workdir.rfind('%s'%EnvFileLoc().root_rundir)]
      self._ams_option.update({'ams_controlfile': os.path.join(rootdir,'circuit.scs')})

    self._simulator = self._get_simulator(vector, self._model_type, self._simulator_name, 
                                          self._simulator_option, self._ams_option, 
                                          self._option, use_cache)

  def get_log(self):
    return self._simulator.get_log()

  def _get_ic(self, test_cfg, sim_cfg):
    ''' return initial condition '''
    return test_cfg.get_ic_golden() if sim_cfg.is_golden() else test_cfg.get_ic_revised()

  def _get_simulator(self, vector, model_type, simulator_name, simulator_option, ams_option, cls_attribute, use_cache):
    '''
      Returns vendor-specific simulator object
      model_type: modeling language; either ams or verilog
    '''
    invalid_combination = (simulator_name == 'vcs' and model_type == 'ams')
    assert not invalid_combination, mcode.ERR_008 % (simulator_name.upper(), model_type.upper())

    if model_type == 'ams':
      simulator= NCVerilogAMS(vector, simulator_option, cls_attribute, ams_option, use_cache, self._csocket, logger_id=self._logger_id)
    elif model_type == 'verilog' and simulator_name == 'vcs':
      simulator = VCSSimulator(vector, simulator_option, cls_attribute, use_cache, self._csocket, logger_id=self._logger_id)
    elif model_type == 'verilog' and simulator_name == 'ncsim':
      simulator = NCVerilogD(vector, simulator_option, cls_attribute, use_cache, self._csocket, logger_id=self._logger_id)

    return simulator
    
  def _bind_vector_to_testbench(self, vector, workdir):
    ''' return a testbench location after binding a test vector to an intermediate testbench for simulation '''
    return misc.get_basename(TestBench.generate(self._raw_tb_file, vector, misc.get_basename(self._raw_tb_file), workdir))


#-----------------------------------
class PostProcessSimulation(object):
  ''' Run post processing routine of a simulation.
      It supports both standalone and server-client mode. 
  '''

  def __init__(self, pp_files, pp_cmd, csocket=None, logger_id='logger_id'):
    self._logger = DaVELogger.get_logger('%s.%s.%s' % (logger_id, __name__, self.__class__.__name__))
    self._pp_script = pp_files # list of script filenames
    self._pp_cmd = pp_cmd # post-processing run command
    self._csocket = csocket
    self._logger.debug(mcode.DEBUG_009 % str(self._pp_script))
    self._logger.debug(mcode.DEBUG_010 % str(self._pp_cmd))
  
  def run(self, workdir, cached=False): # run post-processing routine
    self._sim_msg = ''
    relpath = workdir[workdir.rfind('%s'%EnvFileLoc().root_rundir):]
    if self._is_exist(): # run pp routines if exsits
      if not cached:
        self._logger.debug(mcode.DEBUG_011 % workdir)
        if self._csocket == None: # standalone mode
          for f in self._pp_script: # copy script files to simulation directory
            shutil.copy(f, workdir) 
          cwd = os.getcwd()
          self._logger.debug(mcode.DEBUG_012 % os.path.relpath(workdir))
          os.chdir(workdir)
          p=subprocess.Popen(self._pp_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE) # run pp scripts
          out, err  = p.communicate()
          self._sim_msg = out + '\n' + err
          os.chdir(cwd)
          self._logger.debug(mcode.DEBUG_013)
        else: # server/client mode
          logfile = os.path.join(relpath,EnvFileLoc().simlogfile)
          self._csocket.issue_command('@pp_list %s' % ' '.join(self._pp_script))
          self._csocket.issue_command('@run_pp %s %s' % (relpath,self._pp_cmd))
      else:
        self._logger.debug(mcode.DEBUG_014)

  def get_log(self): # get simulation log
    return self._sim_msg

  def _is_exist(self): # check if pp rountine actually exists
    return True if self._pp_script != None and self._pp_cmd != '' else False
