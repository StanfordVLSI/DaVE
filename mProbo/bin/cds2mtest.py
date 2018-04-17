#!/usr/bin/env python

__doc__ = '''
  Run file to spit out a testbench in structural Verilog from Cadence's Virtuso schematic
'''

import os
import argparse
import logging
import sys
from dave.common.checkeval import ehdnsxmgor
from dave.common.misc import print_section, print_end_msg, printToday
from dave.common.davelogger import DaVELogger
from dave.mprobo.testbench import TestBenchCDSInterface
import dave.mprobo.mchkmsg as mcode
import dave.common.davemsg as davemsg


logging.basicConfig(filename='.cds2mtest.log',
                    filemode='w',
                    level=logging.DEBUG)
logger = logging.getLogger('')
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.INFO)
logger.addHandler(ch)

def display_logo():
  ''' display tool logo '''
  print davemsg.LOGO_002.format(today=printToday())

def pass_args():
  ''' process shell command args '''

  def_portxref = os.path.join(os.environ['DAVE_SAMPLES'],'library/model','port_xref.cfg')

  parser = argparse.ArgumentParser(description=mcode.INFO_046)
  parser.add_argument('cell', help=mcode.INFO_047)
  parser.add_argument('-p', '--cdslibpath', help=mcode.INFO_048, default=os.getcwd())
  parser.add_argument('-x', '--xref', help=mcode.INFO_049 % def_portxref , default=def_portxref)
  return parser.parse_args()

# logger
logger = DaVELogger.get_logger(__name__)

# Run checks
display_logo()

args = pass_args()


# parse cell
lib, cell, view = args.cell.split(':')

# run
tb = TestBenchCDSInterface()(args.cdslibpath, lib, cell, view, args.xref)

if tb != None:
  # display generated testbench
  map(logger.info, print_end_msg(mcode.INFO_050, '--'))
  logger.info('')
  logger.info(tb[0])

  # display extracted port list
  map(logger.info, print_end_msg(mcode.INFO_051, '--'))
  logger.info('')
  logger.info(tb[1])

# finish
map(logger.info, print_end_msg(mcode.INFO_052, '=='))
