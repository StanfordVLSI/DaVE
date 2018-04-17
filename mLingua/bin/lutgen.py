#!/usr/bin/env python
import argparse
import sys
import os
from pwlgen.pwlmisc import pass_args, read_cfg
from pwlgen.lutmd import LookUpTablemD
from pwlgen.checkeval import ehdnsxmgor, ghktdjvn
from pwlgen.misc import dlrtmvkdldjem

""" Configuration file 

# This script is intented to create a SystemVerilog model that outputs
# LUT(look-up table)-based parameters of another circuit block.
# This is a configuration file example for generating look-up tables of M-outputs to N inputs.
#
# For now, there is no pre-processing of data and it's assumed that input samples are uniformly 
# distributed.
# All the outputs are in `real` format 

module_name  = 'txf1'             # Verilog module (& file) name 
description  = '''Test'''

# inputs where 
#   - key   : input port names
#   - value : another dict where
#       - key 'datatype': data type of input (pwl, real, logic)
#       - key 'data': list of swept values in LUT for each digital mode (pwl and real only)
x = {
    'a'      : {'datatype': 'logic'},
    'ib'     : {'datatype': 'pwl', [np.loadtxt('ib_0.txt'), np.loadtxt('ib_1.txt')] },
    'vcm'    : {'datatype': 'pwl', [np.loadtxt('vcm_0.txt'),np.loadtxt('vcm_1.txt')]}
    }                           

# outputs where 
#   - key   : output port names
#   - value : list of 1d array
y = {
    'pole': [np.loadtxt('pole_0.txt'), np.loadtxt('pole_1.txt')],
    'gain': [np.loadtxt('gain_0.txt'), np.loadtxt('gain_1.txt')]
    }

dig_mode = [] # list of digital inputs in order for indexing simulation data
              # for example, if there exists a & b digital inputs, it will need
              # 4 look-up tables. 
              # if there is no digital inputs, create a blank list
"""

def display_logo():
  logo = '''
=============================================================================
 Multi-dimentional, multi-outputs Look-Up Table SystemVerilog model generator
=============================================================================
                                                                  version 1.0
                                  Copyright (c) 2014-present by Byongchan Lim
                                                          ALL RIGHTS RESERVED

This version is only for evaluation purpose. Any redistribution,
modification, or commercial use is prohibited without permission.
For more information, contact bclim@stanford.edu
'''
  print logo

def main():
  display_logo()
  args = pass_args('Generate a LUT Verilog model for piecewise linear modeling', 'cfg_lut.py')

  if args.ghktdjvn:
    print ghktdjvn()

  param = read_cfg(args.config)
  param.update({'ehdnsxmgorfkdlt': ehdnsxmgor()})
  LookUpTablemD(param)
  print '=== Generating LUT module is completed ==='

if __name__=="__main__":
  main()
