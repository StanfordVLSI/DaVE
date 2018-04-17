#!/usr/bin/env python
import argparse
import sys
import os
from pwlgen.pwlmisc import pass_args, read_cfg
from pwlgen.acsimulation import RunACSimulation

""" Configuration file example

# Configuration file for running AC simulation
import numpy as np

# Signal conditioning
signal_in      = 'vin'    # signal name on which sine wave is delivered
signal_out     = 'vout'   # singal name to observe
sine_amp       = 0.1      # amplitude of input sine wave
sine_dc        = 0.0      # dc offset of input sine wave
start_time     = 0.0      # give some settling time for observing the output
skip_cycle     = 2        # in addition to "start_time", skip N sine wave cycles to start observing the output
no_cycle       = 20       # number of sine wave cycle to measure output
sin_etol       = 0.0001   # tolerance of input sine wave
frequency_span = np.logspace(5, 10, 20) # numpy array of frequencies for AC simulation

# DUT instantiation

vlog_code = '''
p2z1 #(.p1(2*`M_PI*100e6), .p2(2*`M_PI*250e6), .z1(2*`M_PI*20e6)) filter1 (.si(vin), .so(vout));
''' # verilog code to place your DUT and necessary stimulus except sine wave in

# other parameters you want to have in
# for ac sweep, we use "ac_frequency" as a parameter name
plot_title = 'Transfer function'
plot_filename = 'ac_sim.png'
show_figure = False # set it to True if you want to see right after the simulation

"""

def run(cfg_file):
  param = read_cfg(cfg_file)
  sim_ac = RunACSimulation(param)
  freq, meas = sim_ac.run()
  gaindB = sim_ac.postprocess(freq, meas, sim_ac.get_param())
  sim_ac.plot(freq, gaindB, sim_ac.get_param())

def main():
  args = pass_args('Run AC simulation of a Verilog model.', 'cfg_ac.py' )
  run(args.config)
  os.remove('test.v')
  print '=== AC simulation is completed ==='

if __name__=="__main__":
  main()
