#!/usr/bin/env python
# Fault simulation
import os
import argparse
import logging
import sys
from multiprocessing import Pool

from dave.common.misc import print_section, make_dir
from dave.mprobo.environ import EnvRunArg
from dave.mprobo.davelogger import DaVELogger

from dave_core.amsfault.runfsim import FaultSimulator, RunFaultSimulation, spawntask
from dave_core.amsfault.faultsimulation import FaultMonteCarloSimulation

logging.basicConfig(filename='amschkfsim_debug.log',
                    filemode='w',
                    level=logging.DEBUG)
logger = logging.getLogger('')
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.INFO)
logger.addHandler(ch)

def pass_args():
  ''' process shell command args '''
  _toolenv = EnvRunArg()
  testcfg_filename = _toolenv.testcfg_filename
  simcfg_filename = _toolenv.simcfg_filename
  rpt_filename = _toolenv.rpt_filename
  verifmc_filename = _toolenv.verif_mcrun_filename

  no_fault = 2
  no_model = 10
  cfg_fault_file = os.path.join(os.environ['DAVE_INST_DIR'], 'dave_core/amsfault/resource/fault.cfg')
  cfg_meas_file = 'measurement.cfg'



  parser = argparse.ArgumentParser(description='Run a fault simulator.')
  parser.add_argument('-t', '--test', help='Test configuration file. Default is "%s"' % testcfg_filename, default=testcfg_filename)
  parser.add_argument('-s', '--sim', help='Simulation configuration file. Default is "%s"' % simcfg_filename, default=simcfg_filename)
  parser.add_argument('-d', '--depth', type=int, help='Number of faults for multiple faults in each faulty circuit. Default is %d' % no_fault, default=no_fault)
  parser.add_argument('-n', '--number', type=int, help='Number of faulty circuits for multiple faults. Default is %d' % no_model, default=no_model)
  parser.add_argument('-f', '--fault-config', help='Fault configuration file. Default is %s' % cfg_fault_file, default=cfg_fault_file)
  parser.add_argument('-m', '--meas-config', help='Measurement configuration file. Default is %s' % cfg_meas_file, default=cfg_meas_file)
  parser.add_argument('-c','--use-cache', action='store_true', help='Use cached data')
  parser.add_argument('-c1','--use-cache1', action='store_true', help='Use cached data for fault simulation only')
  parser.add_argument('-p', help='Number of processes', default=1, type=int)
  parser.add_argument('-i', help='Number of Monte Carlo iterations', default=100, type=int)
  parser.add_argument('-v', '--verif', help='Verification setup file in Python. Default is "%s"' % verifmc_filename, default=verifmc_filename)

  return parser.parse_args()

# logger
logger = DaVELogger.get_logger(__name__)

# Run checks

run_args = pass_args()
use_cached = run_args.use_cache
use_cached1 = run_args.use_cache1

workdir = 'nwork'
make_dir(workdir)

simulator = FaultSimulator(run_args, workdir)

if (not use_cached) and (not use_cached1):
  simulator.preprocess()
  fsim_args = simulator.prepare_run()
  if run_args.p > 1:
    pool = Pool(processes=run_args.p)
    pool.map_async(spawntask, fsim_args, 1).get(99999999)
  else:
    map(RunFaultSimulation(), fsim_args)

fanalyzer = simulator.analyze()

FaultMonteCarloSimulation(simulator, fanalyzer, run_args.verif, run_args.i, run_args.p, use_cached)

# finish
logger.info('\n== Fault simulation is completed ==')
