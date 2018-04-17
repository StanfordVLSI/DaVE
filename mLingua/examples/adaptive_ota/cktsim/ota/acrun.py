#!/usr/bin/env python

# Simulation control and postprocessing

import os
import argparse
import numpy as np
import scipy
import pickle as pkl
import matplotlib.pylab as plt
from readmeas import readmeas
from simulator import pass_args, CircuitSimulation, get_suffix, print_section, plot1d, plot_2stack, plot1d_overlay
from wavemeas import *
from pwlgen.misc import from_engr


class ACSimulation(CircuitSimulation):
  def __init__(self, p, v, t, cached):
    deck_prefix = 'ac'
    description = 'AC simulation'
    default_param = { 'corner': 'tt', 'temp': 50, 'suph': v }

    CircuitSimulation.__init__(self, p, v, t, deck_prefix, default_param, description, cached)

    self.signal = ['iib', 'vcm', 'gain', 'islew']

    self.run() # run simulation & save data
    self.result = self.postprocess()

  def run(self):
    self.check_cache()

    if not self.cached:

      #ib = np.append(np.arange(10e-6, 35.0e-6, 4.0e-6),np.array([60e-6, 70e-6, 80e-6, 90e-6, 100e-6, 110e-6, 120e-6, 130e-6, 140e-6, 150e-6, 175e-6, 200e-6, 220e-6, 240e-6, 260e-6, 280e-6, 300e-6, 400e-6]))
      #ib = np.append(np.arange(1e-6, 32.0e-6, 10.0e-6),np.arange(40e-6, 260e-6, 60e-6))
      ib = np.append(np.arange(1e-6, 32.0e-6, 10.0e-6),np.arange(40e-6, 281e-6, 120e-6))

      vcm    = []
      iib    = []
      gain   = []
      islew  = []
      for i in ib: 
        print_section('Running ib = %.1f [uA]' % (i*1e6), '=')
        self.param.update({'iib':i})
        self.runsim()
        res = readmeas(self.ac_measfilename())
        res2 = readmeas(self.dc_measfilename())
        _iib    = i
        _vcm = [float(from_engr(d)) for d in list(res.get_array('vcm'))]
        _gain = [float(from_engr(d)) for d in list(res.get_array('dcgain'))]
        _islew = [float(from_engr(d)) for d in list(res2.get_array('islew'))]
        for s in self.signal:
          #vars()[s].append(vars()['_'+s])
          vars()[s] += vars()['_'+s]
      np.savetxt('vcm_ac.txt', _vcm)
      np.savetxt('ib_ac.txt', ib)
      self.save_simdata(locals())

  def postprocess(self):
    simdata = self.load_simdata() # load simulation data
    gain = simdata['gain']
    islew = simdata['islew']
    np.savetxt('gain_ac.txt', gain)
    np.savetxt('islew_ac.txt', islew)

def main():

  cached = pass_args().cached

  pvt = [('TT', 3.6, 50)]
  dc = []
  ac = []
  for p in pvt:
    print_section('PVT: %s, %.2f [V], %d [deg]' % (p[0], p[1], p[2]), '=')
    ac.append(ACSimulation(p[0], p[1], p[2], cached))

if __name__=="__main__":
  main()
