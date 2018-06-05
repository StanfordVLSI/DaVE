'''
  Run a unit test
'''

import sys
import os
import copy
import pandas as pd
from pprint import pformat
import numpy as np
import multiprocessing as mp

from port import PortHandler
from vectorgenerator import TestVectorGenerator
from simulation import RunVector
from linearregression import LinearRegressionSM
from testbench import TestBench 
from dave.mprobo.environ import EnvTestcfgOption, EnvFileLoc, EnvSimcfg
from dave.mprobo.checker import UnitChecker, generate_check_summary_table
import dave.mprobo.verilogparser as vp
import dave.mprobo.mchkmsg as mcode
from dave.common.davelogger import DaVELogger
from dave.common.misc import print_section, dec2bin, make_dir, bin2thermdec, print_end_msg, flatten_list, featureinfo
from dave.common.checkeval import ehdnsxmgor

class TestUnit(object):
  ''' Do checking for a test '''
  def __init__(self, test_cfg, sim_cfg, testdir='/tmp', rpt=None, goldensim_only=False, revisedsim_only=False, use_cache=False, no_thread=1, no_otfc=False, csocket=None, logger_id='logger_id'):
    ''' 
      test_cfg : test configuration cls object of a single test
      sim_cfg_(golden,revised) : simulator configuration cls object for golden, revised
      testdir : top directory of this test run
      rpt : report cls object
    '''

    # get system reserved words
    self._tenv = EnvTestcfgOption()
    self._tenvf = EnvFileLoc()
    self._tenvs = EnvSimcfg()
    self._logger_id = logger_id
    self._logger = DaVELogger.get_logger('%s.%s.%s' % (logger_id, __name__, self.__class__.__name__)) # logger
    self._inv = not ehdnsxmgor(featureinfo())
    self._csocket = csocket # client socket for server-client mode

    self._rptgen = rpt # report gen obj
    self._cache = use_cache

    self._np = no_thread # no of threads
    self._no_otfc = no_otfc # no on-the-fly check for pin consistency

    sim_cfg_golden = sim_cfg.get_golden()
    sim_cfg_revised = sim_cfg.get_revised()


    # You can run only either golden sim or revised sim if you need by setting golden(revised)sim_only args
    # But, you can't turn them on both
    assert not (goldensim_only and revisedsim_only), mcode.ERR_003
    self.goldensim_only = goldensim_only
    self.revisedsim_only = revisedsim_only

    # make directories for golden and revised models
    self.testdir = testdir
    self._make_dir()

    # Simulator configuration of both golden and revised model.
    self._sim_cfg_golden = sim_cfg_golden
    self._sim_cfg_revised = sim_cfg_revised

    # Test configuration
    self._test_cfg = test_cfg # get test configuration for this unit test
    self._testname = self._test_cfg.get_test_name() # get a test name

    # generate intermediate testbench
    self._tb_golden = TestBench(
                               self._test_cfg,
                               self._sim_cfg_golden, 
                               self.testdir,
                               logger_id=self._logger_id
                               ).get_raw_filename()
    self._tb_revised = TestBench(
                                self._test_cfg,
                                self._sim_cfg_revised, 
                                self.testdir,
                                logger_id=self._logger_id
                                ).get_raw_filename()

    # display wires used in the instances, let user make sure they are all declared.
    #self._print_wires(self._tb_golden)

    # get a porthandler / create port objects from test cfg info.
    self._ph = PortHandler(logger_id=self._logger_id)
    self._create_port(self._test_cfg)

    # get vector generator obj.
    self._tvh = TestVectorGenerator(self._ph, self._test_cfg, logger_id=self._logger_id)

    # running vector instance
    self._rv_golden = RunVector(self._test_cfg, self._sim_cfg_golden, self._ph, self._tb_golden, self._cache, self._csocket, logger_id=self._logger_id)
    self._rv_revised = RunVector(self._test_cfg, self._sim_cfg_revised, self._ph, self._tb_revised, self._cache, self._csocket, logger_id=self._logger_id)

    # get a linear regressor obj.s for pin discrepancy check
    self._lrg_simple = LinearRegressionSM(self._ph, logger_id=self._logger_id)
    self._lrr_simple = LinearRegressionSM(self._ph, logger_id=self._logger_id)

    # get a linear regressor obj.s for pin discrepancy check (suggested)
    self._lrg_sgt_simple = LinearRegressionSM(self._ph, logger_id=self._logger_id)
    self._lrr_sgt_simple = LinearRegressionSM(self._ph, logger_id=self._logger_id)

    # get a linear regressor obj.s
    self._lrg = LinearRegressionSM(self._ph, logger_id=self._logger_id)
    self._lrr = LinearRegressionSM(self._ph, logger_id=self._logger_id)

    # regressor obj for selected model
    self._lrg_sgt = LinearRegressionSM(self._ph, logger_id=self._logger_id)
    self._lrr_sgt = LinearRegressionSM(self._ph, logger_id=self._logger_id)

    if self._cache:
      self._tvh.load_test_vector(self._ph, self.testdir)
    else:
      self._tvh.dump_test_vector(self._ph, self.testdir)

    # report port information
    if self._rptgen != None:
      self._rptgen.load_porthandler_obj(self._ph) # port object of this test
      self._rptgen.print_port_info() # print out 

  def run_test(self):
    ''' run a test: checks equivalence for all the modes configured by DigitalModePort '''
    mode_result = [] # append each mode result

    digital_mode = self._tvh.get_all_digital_vector()
    modetexts = [self._make_modetext(m) for m in digital_mode]

    if self._rptgen != None:
      self._rptgen.print_testmode_title(self._testname, digital_mode, modetexts)

    for idx, mode in enumerate(digital_mode): # for each mode
      _mode_res = self._run_all_modes(mode, modetexts[idx], idx)
      mode_result.append((mode, modetexts[idx], _mode_res)) # append a mode result

    return mode_result

  def _run_all_modes(self, mode_vector, modetxt, mode_idx):
    ''' run modes configured by true digital inputs '''
    map(self._logger.info, print_section('Testing the mode (%s)' % modetxt, 2))
    if self._rptgen != None:
      self._rptgen.print_testmode(mode_idx+1, modetxt, self._rptgen.make_testmode_link(self._testname, mode_vector)) # create hyperlink for each mode in a report

    return self._run_mode(mode_idx, mode_vector, modetxt) # checks each configuraed system
    
  def _run_mode(self, nth_mode, mode, modetxt): # run analog vectors for each linear circuit mode
    ''' runs a mode out of all possible linear circuit modes
        returns the following sets of golden & revised models
          - test vector with mode inputs being removed
          - output responses
    '''
    map(self._logger.info, print_section(mcode.INFO_022, 3))
    max_run = self._tvh.get_analog_vector_length() # no. of test vector
    if self._cache:
      self._logger.info('\n'+mcode.INFO_023)

    # empty space for vector, measurement
    exec_vector = dict([ (p, np.zeros(max_run)) for p in self._ph.get_input_port_name() ])
    meas_golden = dict([ (p, np.zeros(max_run)) for p in self._ph.get_output_port_name() ])
    meas_revised = dict([ (p, np.zeros(max_run)) for p in self._ph.get_output_port_name() ])

    if self._inv: dlrtmvkdldjem()

    # test vector including digital mode
    vector = [dict(self._tvh.get_analog_vector(i), **mode) for i in range(max_run)]

    # run simulation for each test vector/ gather measurements
    #if self._ph.get_by_name('dummy_analoginput') != None:
    if (not self._no_otfc) and (not self._cache): # unlesss on-the-fly check is disabled
      Nrun_u = max(8, self._tvh.get_unit_no_testvector()) # initial # of runs without on-the-fly
      if self.goldensim_only: # extraction mode
        Nrun_uchk = Nrun_u
      else:
        Nrun_uchk = max(4, self._tvh.get_unit_no_testvector_otf()) # unit # of runs in each on-the-fly
    else:
      Nrun_u = 1
      Nrun_uchk = 1
    #else:
    #  Nrun_u = 1
    #  Nrun_uchk = 1
    sim_idx = 0
    #for i in range(0, max_run, Nrun_u):
    while sim_idx < max_run:
      if sim_idx >= Nrun_u:
        no_run = min(Nrun_uchk, (max_run - sim_idx))
      else:
        no_run = min(Nrun_u, (max_run - sim_idx))
      lastrun = True if (sim_idx+no_run == max_run) else False
    
      simres_golden, simres_revised = self._exercise_unit(nth_mode, mode, sim_idx, no_run, max_run, vector)
      for j in range(sim_idx, sim_idx+no_run): 
        for k, v in vector[j].items():
          exec_vector[k][j] = v
        for k, v in simres_golden[j-sim_idx][1].items():
          meas_golden[k][j] = v
        for k, v in simres_revised[j-sim_idx][1].items():
          meas_revised[k][j] = v

      # chop data upto current run
      _exec_vector = dict([ (p, exec_vector[p][:sim_idx+no_run]) for p in self._ph.get_input_port_name() ])
      _meas_golden = dict([ (p, meas_golden[p][:sim_idx+no_run]) for p in self._ph.get_output_port_name() ])
      _meas_revised = dict([ (p, meas_revised[p][:sim_idx+no_run]) for p in self._ph.get_output_port_name() ])


      # do regression 
      # check on-the-fly equivalence
      if (not self._no_otfc) and (not self._cache): # unlesss on-the-fly check is disabled
        self._logger.info('')
        exec_vector_new=TestVectorGenerator.get_effective_vector(_exec_vector, self._ph)
        lr_formulas = self._run_linear_regression(mode, nth_mode, exec_vector_new, _meas_golden, _meas_revised, quite= True) # linear regression equation of a golden model
        if not self._check_equivalence(): # not equivalent
          break
      sim_idx += no_run

    ## dump vector/measurement 
    exec_vector_new=TestVectorGenerator.get_effective_vector(_exec_vector, self._ph)
    self._dump_vector_measurement(nth_mode, _exec_vector, _meas_golden, is_golden=True, quite=False)
    self._dump_vector_measurement(nth_mode, _exec_vector, _meas_revised, is_golden=False, quite=False)

    lr_formulas = self._run_linear_regression(mode, nth_mode, exec_vector_new, _meas_golden, _meas_revised, quite= False) # linear regression equation of a golden model

    # generate reports
    if self._rptgen != None:
      err_flag_pin, err_flag_residue = self._generate_mode_report()


    res =  {'vector_golden': self._remove_mode_vector(exec_vector_new, mode), 
            'meas_golden': meas_golden, 
            'vector_revised': self._remove_mode_vector(exec_vector_new, mode), 
            'meas_revised': meas_revised, 
            'error_flag_pin': err_flag_pin, 
            'error_flag_residue': err_flag_residue, 
            'lr_formula_suggested': lr_formulas
           }
    if not self.goldensim_only:
      self._print_interim_summary(res, self._testname, mode, modetxt)

    map(self._logger.info, print_end_msg(mcode.INFO_021 % modetxt, '--'))

    return res

  def _print_interim_summary(self, result, test, mode, modetxt):
    ''' logging error summary '''
    map(self._logger.info, print_section(mcode.INFO_058 % modetxt, 3))
    moderes = [(mode, modetxt, result)]
    testres = [(test, [(r[1], r[2]['error_flag_pin'], r[2]['error_flag_residue']) for r in moderes])]
    tab = generate_check_summary_table(testres)
    self._logger.info(tab.draw())


  def _exercise_unit(self, nth_mode, mode, offset, nrun, max_run, vector):
    ''' excercise a mode with generated (quantized) analog vectors 
          - mutiprocessing capability is supported, yet need to be improved 
    '''
    
    np = self._np # number of threads
    for i in range(offset, offset+nrun):
      pretty_vector = dict([ (k, TestVectorGenerator.conv_tobin(self._ph, k, v)) for k, v in vector[i].items() ])
      self._logger.info(mcode.INFO_024 % (i+1, max_run, pformat(pretty_vector, width=1000))) # display running vector

    # run vectors (Multiprocessing enabled)
    if (self._np > 1):
      # Queue
      q_golden = [mp.Queue()]*nrun
      q_revised = [mp.Queue()]*nrun
      q = mp.Manager().Queue(4)
      no_cpu = mp.cpu_count()
      if not self.revisedsim_only:
        p = [mp.Process(target=self._run_vector, args=(q_golden[i], vector[offset+i], nth_mode, offset+i, max_run, True)) for i in range(nrun)]
        for i in range(nrun/np+1):
          for j in range(np):
            if i*np+j < nrun:
              p[i*np+j].start()
          if np < no_cpu:
            for j in range(np):
              if i*np+j < nrun:
                p[i*np+j].join()
  
      if not self.goldensim_only:
        p = [mp.Process(target=self._run_vector, args=(q_revised[i], vector[offset+i], nth_mode, offset+i, max_run, False)) for i in range(nrun)]
        for i in range(nrun/np+1):
          for j in range(np):
            if i*np+j < nrun:
              p[i*np+j].start()
          if np < no_cpu:
            for j in range(np):
              if i*np+j < nrun:
                p[i*np+j].join()

      # get results
      if not self.goldensim_only:
        _tmp = sorted([q_revised[i].get() for i in range(nrun)], key=lambda t:t[0])
        simres_revised = [t[1] for t in _tmp]

      if not self.revisedsim_only:
        _tmp = sorted([q_golden[i].get() for i in range(nrun)], key=lambda t:t[0])
        simres_golden = [t[1] for t in _tmp]


    else:
      if not self.revisedsim_only:
        _x = [self._run_vector(None, vector[offset+i], nth_mode, offset+i, max_run, True) for i in range(nrun)]
        _tmp = sorted([_x[i] for i in range(nrun)], key=lambda t:t[0])
        simres_golden = [t[1] for t in _tmp]

      if not self.goldensim_only:
        _x = [self._run_vector(None, vector[offset+i], nth_mode, offset+i, max_run, False) for i in range(nrun)]
        _tmp = sorted([_x[i] for i in range(nrun)], key=lambda t:t[0])
        simres_revised = [t[1] for t in _tmp]

    if self.revisedsim_only:
      simres_golden = simres_revised

    if self.goldensim_only:
      simres_revised = simres_golden

    return simres_golden, simres_revised

  def _run_vector(self, queue, vector, nth_mode, nth_sim, max_run, is_golden):
    ''' run a simulation with a given vector'''
    rootdir = self.golden_dir if is_golden else self.revised_dir
    rv = self._rv_golden if is_golden else self._rv_revised
    rundir = os.path.join(rootdir, 'run_mode%d_%d' %(nth_mode, nth_sim))
    measurement = rv.run(vector, rundir) # tuple of (success?, dict of output response name/value)
    self._logger.info(mcode.INFO_025 % (self.mdl_msg_header(is_golden), nth_sim+1, max_run, self.print_measurement(measurement)) )
    if self._inv: dlrtmvkdldjem()
    if queue !=None:
      queue.put((nth_sim,measurement))
    else:
      return nth_sim,measurement


  @classmethod
  def print_measurement(cls, meas):
    ''' display output responses from a simulation ''' 
    if meas[0] or meas[1] != None:
      str = pformat(meas[1], width=1000)
      if meas[0] == False:
        str = mcode.MISC_001  + str
    else:
      str = mcode.MISC_002 
    return str


  def _dump_vector_measurement(self, nth_mode, vector, meas, is_golden, quite=False):
    ''' dump vector & measurement data to a .csv file under test directory '''
    mdl_type = 'golden' if is_golden else 'revised'
    csv_file = os.path.join(self.testdir, '_'.join([self._tenvf.csv_vector_meas_prefix, mdl_type, 'mode', str(nth_mode)]) + '.csv')
    df = pd.DataFrame(dict([ (k, TestVectorGenerator.conv_tobin(self._ph, k, v)) for k, v in vector.items() ]))
    df = df.join(pd.DataFrame(meas))
    if not quite:
      map(self._logger.info, print_section(mcode.INFO_026 %(mdl_type), 4))
      self._logger.info(df)
      self._logger.debug("\n"+mcode.DEBUG_001 % (mdl_type, os.path.relpath(csv_file)))
    df.to_csv(csv_file)


  def _run_linear_regression(self, mode, nth_mode, vector, meas_golden, meas_revised, quite=False):
    ''' perform linear regression on the output responses with test vectors of a single mode
    '''
    if self._ph.get_by_name('dummy_analoginput') != None: # duplicates data for the case w/o unpinned analog inputs
      #vector = dict([ (k, [list(v)[0]+i for i in range(20)]) for k,v in vector.items()])
      vector = dict([ (k, [list(v)[0]]*20) for k,v in vector.items()])
      meas_golden = dict([ (k, [list(v)[0]]*20) for k,v in meas_golden.items()])
      meas_revised = dict([ (k, [list(v)[0]]*20) for k,v in meas_revised.items()])

    # load regression option
    regress_opt = self._load_regression_option() # option for deep comparison
    regress_opt_simple = copy.deepcopy(regress_opt) # option for light comparison
    regress_opt_simple.update({self._tenv.regression_en_interact:False, self._tenv.regression_order:1})

    if self._inv: dlrtmvkdldjem()

    # get rid of true digital input vectors from linear regression data
    vector_wo_mode = self._remove_mode_vector(vector, mode)
    lr_param = { 'meas_golden': meas_golden,
                 'meas_revised': meas_revised,
                 'vector_wo_mode': vector_wo_mode }

    #############################################
    # Linear regression to detect pin discrepancy
    #############################################
    lr_param.update({'regression_option': regress_opt_simple})
    self._run_multiphase_linear_regression(True, lr_param, quite)


    ###########################################
    # Linear regression to check model accuracy
    ###########################################
    # do linear regression first
    lr_param.update({'regression_option': regress_opt})
    self._run_multiphase_linear_regression(False, lr_param, quite)


    ############################################
    # dump regression data for debugging purpose
    ############################################
    self._dump_regression_data(nth_mode, is_golden=True)
    self._dump_regression_data(nth_mode, is_golden=False)

    return self._lrg_sgt.get_lr_formulas() # return this for parameter extraction

  def _run_multiphase_linear_regression(self, is_simple, lr_param, quite):
    lrg = self._lrg_simple if is_simple else self._lrg
    lrr = self._lrr_simple if is_simple else self._lrr
    lrg_sgt = self._lrg_sgt_simple if is_simple else self._lrg_sgt
    lrr_sgt = self._lrr_sgt_simple if is_simple else self._lrr_sgt
    if is_simple:
      if not quite: 
        map(self._logger.info, print_section(mcode.INFO_027_1, 3))
      else:
        map(self._logger.debug, print_section(mcode.INFO_027_1, 3))
    else:
      if not quite: 
        map(self._logger.info, print_section(mcode.INFO_027, 3))
      else:
        map(self._logger.debug, print_section(mcode.INFO_027, 3))
    # 1-phase linear regression
    self._run_linear_regression_phase1( lrg, lrr, lr_param, is_simple, quite=quite )

    # Improving models by filtering out insiginicant predictors
    if is_simple:
      if not quite: 
        map(self._logger.info, print_section(mcode.INFO_028_1, 3))
      else:
        map(self._logger.debug, print_section(mcode.INFO_028_1, 3))
    else:
      if not quite: 
        map(self._logger.info, print_section(mcode.INFO_028, 3))
      else:
        map(self._logger.debug, print_section(mcode.INFO_028, 3))

    # filter with normalized input sensitivity
    self._run_linear_regression_phase2( lrg_sgt, lrr_sgt, lr_param, is_simple, no_iter=10, quite=quite )
    # filter with confidence interval
    #self._run_linear_regression_phase3( lrg_sgt, lrr_sgt, lr_param, is_simple )


  def _run_linear_regression_phase1(self, lrg, lrr, param, is_simple=False, quite=False):
    ''' Run 1st pass of linear regression 
    '''
    self._execute_regression(lrg, lrr, param)
    # filter out insignificant predictors using abstol
    p = lrg.suggest_model_using_abstol(is_simple)
    param['regression_option'][self._tenv.regression_user_model].update(p)
    self._execute_regression(lrg, lrr, param)

    # print summary of golden/revised linear regression results
    self._print_linear_equation(lrg, True, is_simple, quite)
    self._print_linear_equation(lrr, False, is_simple, quite)

  def _run_linear_regression_phase2(self, lrg, lrr, param, is_simple=False, no_iter=10, quite=False):
    ''' Run 2nd pass of linear regression with normalized input sensitivity constraint
    '''
    self._logger.debug(mcode.DEBUG_016)
    self._execute_regression(lrg, lrr, param)
    for i in range(no_iter-1):
      # filter out insignificant predictors using sensitivity
      p = lrg.suggest_model_using_sensitivity()
      param['regression_option'][self._tenv.regression_user_model].update(p)
      self._execute_regression(lrg, lrr, param)
      # filter out insignificant predictors using abstol
      p = lrg.suggest_model_using_abstol()
      param['regression_option'][self._tenv.regression_user_model].update(p)
      self._execute_regression(lrg, lrr, param)

    # print summary of golden/revised linear regression results
    self._print_linear_equation(lrg, True, is_simple, quite)
    self._print_linear_equation(lrr, False, is_simple, quite)

  def _run_linear_regression_phase3(self, lrg, lrr, param, is_simple=False):
    ''' Run 3rd pass of linear regression with confidence interval constraint
        Ignore predictors with confidence intervals that embraces 0.0
    '''
    self._logger.debug(mcode.DEBUG_015)
    self._execute_regression(lrg, lrr, param)
    p = lrg.suggest_model_using_confidence_interval()
    param['regression_option'][self._tenv.regression_user_model].update(p)
    self._execute_regression(lrg, lrr, param)

  def _execute_regression(self, lrg, lrr, param):
    ''' execute linear regression of both golden/revised models '''
    lrg.load_data(param['meas_golden'], param['vector_wo_mode'], param['regression_option'])
    lrr.load_data(param['meas_revised'], param['vector_wo_mode'], param['regression_option'])
    lrg.run()
    lrr.run()

  def _load_regression_option(self):
    ''' load options for linear regression '''
    r_opt = copy.deepcopy(self._test_cfg.get_option().items()) # don't want the original one is modified
    r_opt.append(('qaport_name', self._ph.get_quantized_port_name())) # currently, no use
    return dict(r_opt)

  def _print_lr_summary(self, is_golden, suggested=False):
    ''' print linear regression summary '''
    if suggested:
      lr = self._lrg_sgt if is_golden else self._lrr_sgt
    else:
      lr = self._lrg if is_golden else self._lrr
    msg_header = self.mdl_msg_header(is_golden)
    map(self._logger.info, print_section(mcode.INFO_029 % msg_header, 4))
    lr.print_model_summary()

  def _print_linear_equation(self, lr, is_golden=False, is_simple=False, quite=False):
    msg_header = self.mdl_msg_header(is_golden)
    if is_simple:
      if not quite:
        map(self._logger.info, print_section(mcode.INFO_030_1 % msg_header, 4))
      else:
        map(self._logger.debug, print_section(mcode.INFO_030_1 % msg_header, 4))
    else:
      if not quite:
        map(self._logger.info, print_section(mcode.INFO_030 % msg_header, 4))
      else:
        map(self._logger.debug, print_section(mcode.INFO_030 % msg_header, 4))
    lr.print_formula(quite)

  def _dump_regression_data(self, nth_mode, is_golden):
    expand = 'expanded_qanalog' 
    mdl_type = 'golden' if is_golden else 'revised'
    lr = self._lrg if is_golden else self._lrr
    csv_file = os.path.join(self.testdir, '_'.join([self._tenvf.csv_regression_prefix, mdl_type, 'mode', str(nth_mode), expand]) + '.csv')
    lr.export_data(csv_file)
    self._logger.debug('\n' + mcode.INFO_031 % (mdl_type, os.path.relpath(csv_file)))

  def _generate_mode_report(self):
    self._rptgen.load_sensitivity_threshold(self._test_cfg.get_option_regression_input_sensitivity_threshold())
    self._rptgen.load_regression_result(self._lrg_simple, self._lrr_simple, self._lrg, self._lrr, self._lrg_sgt_simple, self._lrr_sgt_simple, self._lrg_sgt, self._lrr_sgt)
    self._rptgen.print_regression_result()

    return self._rptgen.is_pin_error(), self._rptgen.is_residual_error()

  def _remove_mode_vector(self, vector, digital_mode):
    ''' Delete digital mode vector from given vector for linear regression
    '''
    return dict([(k,v) for k,v in vector.items() if k not in digital_mode.keys()])

  def _create_port(self, test_cfg):
    ''' Create port objects specified in a test configuration 
        A dummy digital mode port will also be created if no digital mode port exists
    '''
    map(self._logger.info, print_section(mcode.INFO_032, 2))

    # create port object to port handler
    for p, v in test_cfg.get_port().items():
      self._ph.add_port(p, test_cfg.get_port_type(v), test_cfg.get_port_description(v), test_cfg.get_port_constraint(v) )

    # create dummy digital mode port if necessary
    if self._ph.get_no_of_digitalmode() == 0: 
      self._ph.add_dummy_digitalmode_port()
      self._logger.warn(mcode.WARN_005)
    # create dummy analog input port if necessary
    if self._ph.get_no_of_unpinned_analoginput() == 0: 
      self._ph.add_dummy_analoginput_port()
      self._logger.warn(mcode.WARN_005_1)
    # spit out ports information to logger
    self._logger.info(mcode.INFO_033)
    self._ph.get_info_all() 
  

  def _make_modetext(self, mode):
      return ', '.join(["'%s'=b%s" %(p, dec2bin(v,self._ph.get_by_name(p).bit_width)) for p,v in mode.items()])

  def _make_dir(self):
    ''' make directories for simulating golden & revised models '''
    self.golden_dir = os.path.join(self.testdir,'golden')
    self.revised_dir = os.path.join(self.testdir,'revised')
    if not self._cache:
      make_dir(self.golden_dir, self._logger)
      make_dir(self.revised_dir, self._logger)

  @classmethod
  def mdl_msg_header(cls, is_golden):
    ''' return a message header which indicates "golden" or "revised" '''
    return '[Golden]' if is_golden else '[Revised]'

  def _print_wires(self, tb_filename):
    wires_declared = sorted([w.split()[-1] for w in self._test_cfg.get_wires()])
    wires = []
    for l in vp.getline_verilog(tb_filename):
      if vp.is_instance(l):
        portmap = vp.parse_port_map(l)
        wires.append(portmap.values())
    wires = sorted(list(set(flatten_list(wires))))

    wire_matched = wires_declared == wires

    def printable_wirename(wire_list):
      return ["'%s'" % w for w in wire_list]

    map(self._logger.info, print_section(mcode.INFO_034, 2))
    self._logger.warn(mcode.WARN_006 % ', '.join(printable_wirename(wires)))
    self._logger.warn(mcode.WARN_007 % ', '.join(printable_wirename(wires_declared)))
    self._logger.warn(mcode.WARN_008 % ('matched' if wire_matched else 'unmatched'))
    if wire_matched == False:
      unmatched_wires = list(set(wires_declared)-set(wires))+list(set(wires)-set(wires_declared))
      self._logger.warn(mcode.WARN_009 % ('s are' if len(unmatched_wires)>1 else ' is', ', '.join(printable_wirename(unmatched_wires))))
      self._logger.warn(mcode.WARN_010)

  def _check_equivalence(self):
    ''' on-the-fly equivalence check to stop gathering samples.
        Rules: 
          - It only checks if there is any pin-level inconsistency; 
          - Model accuracy by inspecting residual errors is not checked here.
          - However, if model accuracy is passed, pin inconsistency doesn't 
            matter
    '''
    chkr = UnitChecker(self._test_cfg.get_option_regression_input_sensitivity_threshold(), self._logger_id)
    simple = chkr.run(self._lrg_sgt_simple, self._lrr_sgt_simple, self._ph, True)
    accurate = chkr.run(self._lrg_sgt, self._lrr_sgt, self._ph, False)

    '''
    err_flag_pin = filter(lambda x: x == 'failure', [v['err_flag_pin'] for v in simple.values()])
    err_flag_accurate = filter(lambda x: x == 'failure', [v['err_flag_residue'] for v in accurate.values()])

    #return all([err_flag_pin == [], err_flag_accurate == []])
    return err_flag_pin == []
    '''
    for k in simple.keys():
      if simple[k]['err_flag_pin']=='failure' and accurate[k]['err_flag_residue']=='failure':
        return False
    return True

def dlrtmvkdldjem():
  sys.exit()
