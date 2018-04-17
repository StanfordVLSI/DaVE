#

__doc__ = """
Functions/Classes related to flow control
"""

import os
import sys
import subprocess


def run_characterization(testcfg='test.cfg', simcfg='sim.cfg', report='report.html', no_processes=1):
  _run_mProbo(testcfg, simcfg, report, True, no_processes)

def run_equivalence(testcfg='test.cfg', simcfg='sim.cfg', report='report.html', no_processes=1):
  _run_mProbo(testcfg, simcfg, report, False, no_processes)

def _run_mProbo(testcfg='test.cfg', simcfg='sim.cfg', report='report.html', is_characterization=False, no_processes=1):
  behavior_msg = 'Circuit characterization' if is_characterization else 'AMS equivalence checking'
  args = ['-t%s'%testcfg,'-s%s'%simcfg,'-r%s'%report,'-p%d'%no_processes]
  if is_characterization:
    args = args + ['-e']

  def run(args, exefile_ext):
    cmd = [os.path.join(os.environ['DAVE_INST_DIR'],'mProbo','bin','mProbo.%s'%exefile_ext)]
    #cmd_w_args = [sys.executable,cmd,'-t%s'%testcfg,'-s%s'%simcfg,'-p%d'%no_processes]
    subprocess.call(cmd+args)#, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  print '%s starts' % behavior_msg
  try:
    run(args, 'exe')
  except:
    run(args, 'py')
  print '%s is complete' % behavior_msg
