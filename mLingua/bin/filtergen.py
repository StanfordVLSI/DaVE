#!/usr/bin/env python
import os
import argparse
import sys
from dave.mlingua.pwlmisc import pass_args
from dave.mlingua.vloggenerator import VerilogPWLGenerator
from dave.mlingua.checkeval import ehdnsxmgor, ghktdjvn

def display_logo():
  logo = '''
-----------------------------------------------------------------
 Continuous-time filter model generator using PWL approximation
-----------------------------------------------------------------
                                                      version 0.5
                             Copyright (c) 2014- by Byongchan Lim
                                              ALL RIGHTS RESERVED

This version is only for evaluation purpose. Any redistribution,
modification, or commercial use is prohibited without permission.
For more information, contact bclim@stanford.edu
'''
  print logo

display_logo()
#if ehdnsxmgor() != True:
#  sys.exit()

args = pass_args('Generate a SystemVerilog model of an analog filter in PWL waveform.', 'cfg_filter.py')

if args.ghktdjvn:
  print ghktdjvn()

VerilogPWLGenerator(args.config)

# finish
print '==Model Generation Complete=='
