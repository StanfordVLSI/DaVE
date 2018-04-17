# simulator interface
import tempfile
import os
import stat
import shutil
import glob
import numpy as np
import copy
import re
import subprocess
import dave.common.misc as misc
from dave.common.davelogger import DaVELogger
from environ import EnvSimulatorClassOpt
from dave.common.empyinterface import EmpyInterface
from dave.mprobo.environ import EnvFileLoc

__doc__ = '''
The interface to the actual AMS simulator is defined. Currently, we support NC-Simulator 
for both (System)Verilog and Verilog-AMS, and VCS for (System)Verilog.
This writes a shell script to run a simulation for given options. 
Note that 'sweep_file' option is obsolete now.
'''

#-----------------------
class Simulator(object):
  def __init__(self, cls_attr={}, csocket=None, logger_id='logger_id'):
    ''' initialize '''
    self._logger_id = logger_id
    self._logger = DaVELogger.get_logger('%s.%s.%s' % (logger_id, __name__, self.__class__.__name__))
    self._csocket = csocket

    self.cls_attribute = { 'sweep_file' : True, 
                           'hdl_files' : [], 
                           'workdir' : '/tmp',
                           'ic' : {},
                           'temperature' : 27,
                           'timescale' : '', 
                           'sim_time'  : '' }

    self.cls_attribute.update(cls_attr)

    for k,v in self.cls_attribute.items(): # create class attributes
      setattr(self, '_'+k, v)
    
  def run(self, use_cache): # Run a Verilog simulation, or skip it if use_cache 
    (workdir, basename) = os.path.split(self._runscript)
    self._workdir = workdir
    relpath = workdir[workdir.rfind('%s'%EnvFileLoc().root_rundir):]

    if self._csocket == None: # standalone mode
      self._logger.debug("Changing directory to '%s' for running simulation" % relpath)
      if use_cache:
        self._logger.debug("Using cached resuts.")
        out = 'Use cached data'
        err = ''
      else:
        self._runscript = 'pushd ${PWD}>/dev/null\n cd %s\n' % workdir +self._runscript+'\n popd'
        p=subprocess.Popen(self._runscript, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err  = p.communicate()
      sim_msg = out + '\n' + err
      self._logger.debug("Simulation message: %s" % sim_msg)
      self._logger.debug("Going back to running directory")
      self._sweep_files(workdir) # sweep temporary simulation files
    else: # client-server mode
      files = filter(os.path.isfile, glob.glob(os.path.join(self._workdir,'*')))
      files = [os.path.join(relpath, misc.get_basename(f)) for f in files]
      logfile = os.path.join(relpath,EnvFileLoc().simlogfile)
      self._csocket.issue_command('@download %s' % ' '.join(files))
      self._csocket.issue_command('@run_verilog %s' % relpath)
      self._csocket.issue_command('@upload %s' % logfile)
      with open(os.path.join(workdir,EnvFileLoc().simlogfile), 'r') as f:
        sim_msg = f.readlines()
    return sim_msg

  def get_log(self): # simulation log
    return self._sim_msg

  def _generate_runscript(self, run_cmd, is_vcs, workdir): # generate a run script in C-shell
    filename = os.path.join(workdir, 'run_vlog.csh')
    run_script = run_cmd + '\n nice ./simv' if is_vcs else run_cmd # content of a script
    with open(filename, 'w') as f:
      f.writelines(run_script)
    os.chmod(filename, stat.S_IEXEC | stat.S_IREAD | stat.S_IWRITE) # make a script executable
    return os.path.abspath(filename)

#-----------------------------
class VCSSimulator(Simulator):
  ''' Simulator for Synopsys' VCS '''
  def __init__(self, vector, simulator_option, cls_attr={}, use_cache=False, csocket=None, logger_id='logger_id'):
    Simulator.__init__(self, cls_attr, csocket, logger_id=logger_id)
    sim_cmd = ['nice vcs'] 
    self.run_cmd = ' '.join( sim_cmd + 
                             self._hdl_files + 
                             self._default_simulator_option() + 
                             [simulator_option] )
    self._runscript = self._generate_runscript(self.run_cmd, True, self._workdir)
    self._sim_msg = self.run(use_cache)

  def _default_simulator_option(self):
    return ['-sverilog -top test', '-timescale=' + self._timescale, '-debug_pp'] 

  def _sweep_files(self, workdir):
    shutil.rmtree(os.path.join(workdir, 'simv.daidir'), True)
    shutil.rmtree(os.path.join(workdir, 'csrc'), True)
    for x in ['simv', 'ucli.key', 'vc_hdrs.h', 'vcdplus.vpd']:
      misc.rmfile(os.path.join(workdir, x)) 


#----------------------------
class NCSimulator(Simulator):
  ''' Cadence' NC simulator '''
  HDLTCL_STR = '''# probe tcl for ncsimulator
    database -open test.shm -into test.shm -default
    probe -creat -shm -all -depth all
    run
    exit
  '''
  def __init__(self, vector, simulator_option, cls_attr={}, csocket=None, logger_id='logger_id'):
    ''' initialize '''
    Simulator.__init__(self, cls_attr, csocket, logger_id=logger_id)
    sim_cmd = ['nice ncverilog']
    self.run_cmd = ' '.join( sim_cmd + 
                             self._hdl_files + 
                             self._default_simulator_option() +
                             [simulator_option] )
    self._generate_hdl_tcl(self._workdir)
  
  def _generate_hdl_tcl(self, workdir): # generate hdl.tcl in simulation directory '''
    with open(os.path.join(workdir, 'hdl.tcl'),'w') as f:
      f.write(self.HDLTCL_STR)

  def _default_simulator_option(self): # default simulator option
    return ['+NCTOP+test', '+NCTIMESCALE+' + self._timescale, '-CLEAN +NCUPDATE', '+NCINPUT+hdl.tcl'] 

  def _sweep_files(self, workdir): # sweep temporary simulation files
    # Common to Verilog & VerilogAMS
    shutil.rmtree(os.path.join(workdir, 'INCA_libs'), True)
    shutil.rmtree(os.path.join(workdir, 'test.shm'), True)
    misc.rmfile(os.path.join(workdir, 'ncverilog.key'))

    # VerilogAMS only
    try:
      shutil.rmtree(os.path.join(workdir, '{0}.raw'.format(os.path.splitext(self.scsfile)[0])), True)
      shutil.rmtree(os.path.join(workdir, '{0}.ahdlSimDB'.format(os.path.split(os.path.splitext(self.scsfile)[0])[1])), True)
      shutil.rmtree(os.path.join(workdir, 'portmap_files'), True)
      shutil.rmtree(os.path.join(workdir, '.ams_spice_in'), True)
    except:
      pass

#-----------------------------
class NCVerilogD(NCSimulator):
  ''' Simulator for (S)Verilog-D using NC simulator '''
  def __init__(self, vector, simulator_option, cls_attr={}, use_cache=False, csocket=None, logger_id='logger_id'):
    NCSimulator.__init__(self, vector, simulator_option, cls_attr, csocket, logger_id=logger_id)
    self.run_cmd = self.run_cmd + ' -SV '
    self._runscript = self._generate_runscript(self.run_cmd, False, self._workdir)
    self._sim_msg = self.run(use_cache)


#-------------------------------
class NCVerilogAMS(NCSimulator):
  ''' Simulator for Verilog-AMS using NC simulator '''
  PROP_STR = '''
    cell {cellname} 
    {{
      string prop sourcefile="{netlistfile}";
      string prop sourcefile_opts="-auto_bus -bus_delim <>";
    }}
  '''
  def __init__(self, vector, simulator_option, cls_attr={}, ams_option={}, use_cache=False, csocket=None, logger_id='logger_id'):
    NCSimulator.__init__(self, vector, simulator_option, cls_attr, csocket, logger_id=logger_id)
    self._ams_option = {'ams_controlfile': '', 'ams_circuits': None, 'spice_lib': None, 'ams_connrules': None}
    self._ams_option.update(ams_option)
    self._process_ams_option(self._ams_option, vector)
    self.run_cmd = ' '.join( [self.run_cmd] + self._default_ncams_simulator_option() )
    self._runscript = self._generate_runscript(self.run_cmd, False, self._workdir)
    self._sim_msg = self.run(use_cache)

  def _default_ncams_simulator_option(self): # default NCVerilogAMS option in addition to NCVerilog option 
    return ['+NCAMS +DEFINE+AMS', '+NCANALOGCONTROL+' + self.scsfile, self.param_propspath, self.ams_connrules]

  def _process_ams_option(self, ams_option, vector):
    ''' generate circuit related options including
        1) .ic option, 2) .scs file, and 3) props.cfg file 4) +amsconnrules+ if exists
        biand current vector to .scs if present
    ''' 
    raw_scs = ams_option['ams_controlfile']
    circuits = ams_option['ams_circuits']
    connrules = ams_option['ams_connrules']

    scs_param = { 'sim_time'          : self._sim_time,
                  'initial_condition' : self._generate_ic_deck(self._ic),
                  'temperature'       : self._temperature,
                  'spice_lib'         : self._ams_option['spice_lib'] }
    scs_param.update(vector)

    self.scsfile = self._gen_scs_file(raw_scs, scs_param, self._ams_option['vector'], self._workdir)
    self.param_propspath = '' if circuits == None else \
                           '+NCPROPSPATH+' + self._gen_ckt_propspath(circuits, self._workdir)
    self.ams_connrules = '' if connrules == '' else \
                         '+amsconnrules+' + connrules

  def _generate_ic_deck(self, ic): # generate .ic statement to set inintial condition of circuit nodes
    return '\n'.join(['.ic(test.%s) = %s' %(k, v) for k,v in ic.items()])

  def _gen_scs_file(self, scs_template, param, vector, workdir): # generate analog control file 
    # two step, the second phase bind vectors to initial condition statement in .scs file if any 
    tmp_file = os.path.join(workdir, 'analog_%s.scs' % misc.generate_random_str('',5))
    tmpfile = EmpyInterface(tmp_file)(scs_template, param)
    dst_file = os.path.join(workdir, 'analog_%s.scs' % misc.generate_random_str('',5))
    scsfile = EmpyInterface(dst_file)(tmpfile, vector)
    misc.rmfile(tmpfile)
    return misc.get_basename(scsfile)

  def _gen_ckt_propspath(self, circuit, workdir='/tmp'):
    ''' generate cadence props.cfg file to import circuit netlist 
        TODO: Sometimes, the auto_bus expansion of cadence NCAMS does not work '''
    fid, filename = tempfile.mkstemp(suffix='_prop.cfg', dir=workdir)
    with os.fdopen(fid, 'w') as f:
      for p, v in circuit.items():
        f.write(self.PROP_STR.format(cellname=p, netlistfile=os.path.abspath(v)))
    return misc.get_basename(filename)
