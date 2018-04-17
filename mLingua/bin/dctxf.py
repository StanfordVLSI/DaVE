#!/usr/bin/env python
import argparse
import sys
import os
from pwlgen.pwlmisc import pass_args, read_cfg
from pwlgen.dctxfcurve import TxfCurveGenerator
from pwlgen.checkeval import ehdnsxmgor, ghktdjvn

""" Configuration file 

# A user provides a set of points (x, y) which represents a transfer curve.  Some of the points might be redundant. So, this script first reduces the number of points as long as it meets the error tolerance spec (etol).  The next step is to find the slope in each segment and use the information and the reduced data set to generate a Verilog model having a DC transfer curve.

# The user data might be from either
#   - simulation, or
#   - sampled one from an analytic equation 

# Here is a simple configuration example.

module_name  = txf1             # Verilog module (& file) name will be txf1.v
etol         = 0.00001          # absolute error tolerance of the approximation
x            = [1,2,3]          # x-axis of a transfer curve
y            = [0.5, 0.2, 0.8]  # y-axis of a transfer curve
use_userdata = False            # reduce # of data points for given etol if False, default is False

# NOTE:
#   Depending on the error tolerance, "etol", you may need more data points. If it is the case, the script will complain. One way to solve this problem is to use the interpolation function such as scipy.interpolate.interp1d() so as to generate finer samples.

# Outputs:
# Running this script with a valid configuration file will produce
#   1. a Verilog model processing DC trasnfer curve of a PWL waveform
#   2. two .png pictures (suffix is "module_name") 
#     - one shows the original user data vs reduced data
#     - the other shows the error of the reduced data to the original data

"""

def display_logo():
  logo = '''
-----------------------------------------------------------------
   LUT-based PWL model in SystemVerilog for DC transfer curve   
-----------------------------------------------------------------
                                                      version 0.5
                             Copyright (c) 2014- by Byongchan Lim
                                              ALL RIGHTS RESERVED

This version is only for evaluation purpose. Any redistribution,
modification, or commercial use is prohibited without permission.
For more information, contact bclim@stanford.edu
'''
  print logo

def run(cfg_file):
  param = read_cfg(cfg_file)
  c = TxfCurveGenerator(param)
  freq, meas = sim_ac.run()
  gaindB = sim_ac.postprocess(freq, meas, sim_ac.get_param())
  sim_ac.plot(freq, gaindB, sim_ac.get_param())

def main():
  display_logo()
  if ehdnsxmgor() != True:
    sys.exit()
  args = pass_args('Generate a Verilog model representing a DC transfer curve in PWL waveform', 'cfg_txf.py')

  if args.ghktdjvn:
    print ghktdjvn()

  param = read_cfg(args.config)
  TxfCurveGenerator(param)
  print '=== Generating transfer curve module is completed ==='

if __name__=="__main__":
  main()
