#!/usr/bin/env python

# Simulation control and postprocessing

import os
import argparse
import numpy as np
import scipy
import pickle as pkl
import matplotlib.pylab as plt
from readmeas import readmeas
from simulator import pass_args, CircuitSimulation, get_suffix, print_section, get_print, get_tf
from wavemeas import *
from pwlgen.misc import from_engr_spice
from scipy.interpolate import interp1d


class DCSimulation(CircuitSimulation):
  def __init__(self, p, v, t, cached):
    deck_prefix = 'dc'
    description = 'DC simulation'
    default_param = { 'corner': 'tt', 'temp': 50, 'suph': v }

    CircuitSimulation.__init__(self, p, v, t, deck_prefix, default_param, description, cached)

    self.signal = ['vout', 'rout', 'gain', 'isrc', 'imip', 'imim', 'igain', 'iout', 'gm']

    self.run() # run simulation & save data
    self.result = self.postprocess()

  def run(self):
    self.check_cache()

    if not self.cached:

      #ib = np.append(np.arange(10e-6, 35.0e-6, 4.0e-6),np.array([60e-6, 70e-6, 80e-6, 90e-6, 100e-6, 110e-6, 120e-6, 130e-6, 140e-6, 150e-6, 175e-6, 200e-6, 220e-6, 240e-6, 260e-6]))
      #ib = np.append(np.arange(1e-6, 32.0e-6, 10.0e-6),np.arange(40e-6, 260e-6, 60e-6))
      ib = np.append(np.arange(1e-6, 32.0e-6, 10.0e-6),np.arange(40e-6, 281e-6, 120e-6))
      vic = np.array([1.8])

      vout = []
      rout = []
      gain = []
      isrc = []
      imip = []
      imim = []
      igain = []
      iout = []
      gm = []
      for i in ib: 
        for vc in vic:
          print_section('Running ib = %.1f [uA], vcm = %.3f [V]' % (i*1e6, vc), '=')
          self.param.update({'vcm':vc, 'iib':i})
          self.runsim()
          res = readmeas(self.dc_filename())
          res_tf = get_tf(self.lis_filename())
          res_dc = get_print(self.lis_filename())
          _vd = list(res.get_array('v:vd'))
          _isrc = list(res.get_array('i:xdut.msrc'))
          _imip = list(res.get_array('i:xdut.mip'))
          _imim = list(res.get_array('i:xdut.mim'))
          _iout = list(res.get_array('i:mload'))
          _igain = list(res.get_array('i:mload')/i)
          _rout = [float(from_engr_spice(d)) for d in res_tf[2]]
          _gain = [float(from_engr_spice(d)) for d in res_tf[3]]
          _vout = [float(from_engr_spice(d)) for d in res_dc['out'][2]]
          _gm   = list(np.array(_gain)/np.array(_rout))
          interpfn = interp1d(_vout, _rout)
          _vout = list(np.linspace(1.0, 3.3, len(_vd)))
          _rout = list(interpfn(_vout))
          for s in self.signal:
            vars()[s] += vars()['_'+s]
      np.savetxt('ib_dc.txt', ib)
      np.savetxt('vcm_dc.txt', vic)
      np.savetxt('vd_dc.txt', _vd)
      np.savetxt('vout_dc.txt', _vout)
      self.save_simdata(locals())

  def postprocess(self):
    simdata = self.load_simdata() # load simulation data
    gain = simdata['gain']
    vout = simdata['vout']
    isrc = simdata['isrc']
    imip = simdata['imip']
    imim = simdata['imim']
    rout = simdata['rout']
    igain = simdata['igain']
    iout = simdata['iout']
    gm = simdata['gm']
    np.savetxt('pole_dc.txt', 1.0/(np.array(rout)*1.2e-12))
    np.savetxt('gain_dc.txt', gain)
    np.savetxt('igain_dc.txt', igain)
    np.savetxt('iout_dc.txt', iout)
    np.savetxt('gm_dc.txt', iout)
    

def main():

  cached = pass_args().cached

  pvt = [('TT', 3.6, 50)]
  dc = []
  ac = []
  for p in pvt:
    print_section('PVT: %s, %.2f [V], %d [deg]' % (p[0], p[1], p[2]), '=')
    ac.append(DCSimulation(p[0], p[1], p[2], cached))

if __name__=="__main__":
  main()
