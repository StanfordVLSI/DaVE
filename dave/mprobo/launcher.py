#

__doc__ = """ 
This contains functions related to launching mProbo 

Note:
   - if the tool stops abnormally (e.g. hit Ctrl+C by user). Error messages will be encrypted and dumped to a file, which can be read by an internal script, decode_errmsg.py.
"""

import os
import logging
import sys
import signal
import traceback
import argparse
from dave.mprobo.runchecker import RunChecker
from dave.common.checkeval import ehdnsxmgor
from dave.common.misc import print_section, print_end_msg, generate_random_str, interpolate_env
from dave.mprobo.environ import EnvRunArg, EnvFileLoc, EnvMisc
import dave.mprobo.mchkmsg as mcode
import dave.common.davemsg as davemsg
#from dave.mprobo.mprobogui import run_mProbo_GUI
from dave.common.misc import featureinfo, printToday


def pass_args(client=False):
  ''' process shell command arguments 
      - client : Configure arguments for client mode if True
  '''
  _envarg = EnvRunArg()
  testcfg_filename = _envarg.testcfg_filename
  simcfg_filename = _envarg.simcfg_filename
  rpt_filename = _envarg.rpt_filename
  #port_xref_filename = interpolate_env(_envarg.port_xref_filename)
  port_xref_filename = _envarg.port_xref_filename

  parser = argparse.ArgumentParser(description=mcode.INFO_002)
  parser.add_argument('-e','--extract', action='store_true', help=mcode.INFO_008_1)
  parser.add_argument('-r', '--rpt', help=mcode.INFO_005 % rpt_filename, default=rpt_filename)
  if not client:
    parser.add_argument('-t', '--test', help=mcode.INFO_003 % testcfg_filename, default=testcfg_filename)
    parser.add_argument('-s', '--sim', help=mcode.INFO_004 % simcfg_filename, default=simcfg_filename)
    parser.add_argument('-p', '--process', help=mcode.INFO_006, type=int, default=1)
    parser.add_argument('-c','--use-cache', action='store_true', help=mcode.INFO_007)
    parser.add_argument('-n','--no-otf-check', action='store_true', help=mcode.INFO_007_1)
    parser.add_argument('-w','--workdir', help=mcode.INFO_005_1, type=str, default='.')
    parser.add_argument('-x','--port-xref', help=mcode.INFO_008_2 % port_xref_filename, type=str, default=port_xref_filename)
    #parser.add_argument('-g', '--gui', action='store_true', help=mcode.INFO_008)

  return parser

def sigint_handler(signal, frame):
  ''' Handle user's Ctrl+C '''
  print(mcode.WARN_001)
  sys.exit(0)

def launch(args, csocket=None):
  ''' Launch mProbo '''
  # creating logger
  if csocket != None: # "logger id"s of clients should be different
    logger_id = generate_random_str(EnvMisc().logger_prefix+'_',10)
  else:
    logger_id = EnvMisc().logger_prefix
  logger = logging.getLogger(logger_id)
  ch1 = logging.StreamHandler(open(os.path.join(args.workdir,EnvFileLoc().logfile), 'w'))
  ch1.setLevel(logging.INFO)
  logger.addHandler(ch1)

  # interrupt handler
  if csocket == None:
    signal.signal(signal.SIGINT, sigint_handler)

  try: # normal mode without any error or user interrupt
    # Run checks
    logger.info(davemsg.LOGO_001.format(today=printToday()))
    try:
      if ehdnsxmgor(featureinfo()) != True:
        inv = True
    except:
      sys.exit()
  
    #if args.gui: # launch GUI
    #  logger.info(mcode.INFO_010)
    #  run_mProbo_GUI()
    #  logger.info(mcode.INFO_011)
    #  sys.exit()
  
    # run mProbo
    amschk_obj = RunChecker(args, csocket, logger_id)()
    
    # finishing message
    if not args.extract: # checker mode
      list(map(logger.info, print_end_msg(mcode.INFO_009, '==')))
    else: # extraction mode
      list(map(logger.info, print_end_msg(mcode.INFO_009_1, '==')))
  except: # handle user interrupt
    m = traceback.format_exc()
    logger.info(m.splitlines()[-1])
    edc = lambda ss,cc: ''.join(chr(ord(s)^ord(c)) for s,c in zip(ss,cc*1000))
    #m = edc(m, mcode.INFO_009)
    with open(EnvFileLoc().dump_file, 'w') as f:
      f.write(m)
  logger.removeHandler(ch1)
