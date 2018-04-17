#!/usr/bin/env python

__doc__ = """ A class 
  1. to run each test defined in a test configuration file
    - to create a report for each test
  2. to store the extracted linear models to a file 
  3. to print out the summary of a checking
"""

import os
import sys
import shutil
import texttable
import yaml
from dave.mprobo.testunit import TestUnit
from dave.mprobo.testconfig import TestConfig
from dave.mprobo.simulatorconfig import SimulatorConfig
from dave.mprobo.reportgen import ReportGenerator
from dave.mprobo.environ import EnvFileLoc
import dave.mprobo.mchkmsg as mcode
from dave.mprobo.modelparameter import LinearModelParameter 
from dave.mprobo.checker import generate_check_summary_table
from dave.common.checkeval import ehdnsxmgor
from dave.common.misc import print_section, make_dir, print_end_msg, featureinfo
from dave.common.davelogger import DaVELogger

class RunChecker(object):
  ''' Run the checking for each test configured in a test configuration file '''
  def __init__(self, args, csocket, logger_id='logger_id'):
    self._testfile = args.test # test configuration file name
    self._simfile = args.sim   # simulator configuration file name
    self._workdir = args.workdir # working directory
    self._rptfile = os.path.abspath(os.path.join(self._workdir,args.rpt)) # report file name
    self._cache = args.use_cache # use cached data if True
    self._no_otfc = args.no_otf_check # no on-the-fly check for pin consistency
    self._np = args.process # num. of threads for simulations
    self._goldenonly = args.extract # run in extraction mode
    self._port_xref = args.port_xref # port cross reference filename of modules
    self._csocket = csocket # client socket if any
    self._logger_id = logger_id # logger id string

    self._logger = DaVELogger.get_logger('%s.%s.%s' % (logger_id, __name__, self.__class__.__name__))
    self._mp = LinearModelParameter()

    self._inv = not ehdnsxmgor(featureinfo())

    self._tcfg = TestConfig(self._testfile, port_xref = self._port_xref, logger_id=logger_id) # get test cfg obj
    self._scfg = SimulatorConfig(self._simfile, self._goldenonly, logger_id=logger_id) # get sim cfg obj
    self._rptgen = ReportGenerator(filename=self._rptfile, logger_id=logger_id) # reportgenerator obj

    self._root_rundir = os.path.join(self._workdir, EnvFileLoc().root_rundir) # for e.g. workdir/.mProbo, this will store all the data for the checking
    make_dir(self._workdir, self._logger)
    make_dir(self._root_rundir, self._logger)

    if self._inv: dlrtmvkdldjem()

  def __call__(self):
    testres = [] # test results
    self._testnames = self._tcfg.get_all_testnames() # get all test names
    map(self._logger.info, print_section(mcode.INFO_012, 1))
    self._logger.info(self._testnames)

    if self._inv: dlrtmvkdldjem()

    # print report header
    self._rptgen.print_report_header( self._testnames, os.getcwd(), self._workdir, self._root_rundir, self._testfile, self._simfile, self._rptfile )

    if self._inv: dlrtmvkdldjem()

    # run the checking for each test
    for idx, t in enumerate(self._testnames):
      test = self._tcfg.get_test(t)
      # print test information
      self._rptgen.print_testname(t)
      self._rptgen.print_test_info(test.get_dut_name(), test.get_description())
      #
      res = self._run_a_test( t, os.path.join(self._root_rundir, t), test, self._scfg, self._rptgen )
      testres.append((t, [(r[1], r[2]['error_flag_pin'], r[2]['error_flag_residue']) for r in res]))

      self._mp.formulate_model_parameters(t, res) # extract parameters of linear models 
    # save the extracted model parameters
    self._mp.save_model_parameters(self._root_rundir)

    # display error summary (suggested model only)
    if not self._goldenonly:
      self._test_error_summary(testres)
    # report gen
    self._rptgen.render()
    self._rptgen.close()

    # print where the report file is
    rptpath = os.path.relpath(self._rptfile, self._workdir)
    map(self._logger.info, print_section(mcode.INFO_013 % rptpath, 1))

    if self._inv: dlrtmvkdldjem()

  def _run_a_test(self, testname, testdir, testcfg, simcfg, rptgen):
    ''' Run the checking of a test '''

    map(self._logger.info, print_section(mcode.INFO_014 % testname, 1))

    if make_dir(testdir, self._logger, not self._cache):
      self._logger.warn(mcode.WARN_002 % os.path.relpath(testdir))


    testrun = TestUnit(testcfg, simcfg, testdir, rptgen, use_cache=self._cache, no_thread=self._np, goldensim_only=self._goldenonly, no_otfc = self._no_otfc, csocket=self._csocket, logger_id=self._logger_id)
    res = testrun.run_test()

    if simcfg.get_sweep(): # sweep==True for either golden or revised 
      shutil.rmtree(testdir)
      self._logger.info(mcode.INFO_015 % os.path.relpath(testdir))

    map(self._logger.info, print_end_msg(mcode.INFO_016 % testname, '=='))
    return res

  def _test_error_summary(self, result):
    ''' logging error summary '''
    msg = mcode.INFO_017 % (mcode.INFO_018) 
    map(self._logger.info,print_section(msg, 1))
    tab = generate_check_summary_table(result)
    self._logger.info(tab.draw())

def dlrtmvkdldjem():
  sys.exit()
