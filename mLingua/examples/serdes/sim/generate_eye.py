#! /usr/bin/env python 

"""
  Generate eyediagram and save it to eye.png
"""

import argparse
import numpy as np
from scipy.interpolate import interp1d
import matplotlib.pylab as plt
import matplotlib
from matplotlib.colors import Normalize
font = { 'size'   : 19}
matplotlib.rc('font', **font)

def resample(data, time, tunit):
  xs = data[:,0]/tunit
  ys = data[:,1]
  f = interp1d(xs,ys)
  y = f(time)
  return y

def rollover(sample, time, period, time_offset):
  x = []
  y = []
  for idx,t in enumerate(time):
    x.append((t + time_offset) % period)
    y.append(sample[idx])
  return y,x

def run(filename, imgname, period, time_offset, nbin, ylabel):    
  tunit = 1e-12
  period = period/tunit
  time_offset = time_offset/tunit
  data = np.loadtxt(filename)
  x = data[:,0]/tunit
  t_start = x[0]
  t_stop = x[-1]
  t_step = period/nbin
  time = np.arange(t_start, t_stop, t_step)
  sample = resample(data, time, tunit)
  y,x=rollover(sample, time, period, time_offset)

  H, yedges, xedges = np.histogram2d(y, x, bins=nbin)

  s = sum(H)

  fig = plt.figure(figsize=(8,8),dpi=80)
  ax = plt.gca()
  extent=[min(xedges), max(xedges), min(yedges), max(yedges)]
  aspect = (max(xedges)-min(xedges))/(max(yedges)-min(yedges))
  cax=plt.imshow(H/s,interpolation='nearest',cmap=plt.cm.coolwarm, extent=extent, norm=Normalize(), aspect=aspect)
  plt.grid(color='w')
  plt.xlabel('Time [psec]')
  plt.ylabel(ylabel)
  plt.tight_layout()
  #fig.colorbar(cax)
  ax.set_axis_bgcolor('k')
  ax.set_xticks([0, period/2, period])
  ax.set_ylim(-0.6,0.6)

  plt.savefig(imgname)

if __name__ == "__main__":
  #run('tx_out_new.txt','tx_out.png', 0.4e-9, 0.1e-9, 120)
  run('ch_out.txt','ch_out.eps', 0.4e-9, 0.15e-9, 120, 'CH output [V]')
  run('eq_out.txt','eq_out.eps', 0.4e-9, 0.15e-9, 120, 'CTLE output [V]')
  run('dfe_out.txt','dfe_out.eps', 0.4e-9, 0.15e-9, 120, 'DFE output [V]')
  run('rxclk_out.txt','rxclk_out.eps', 0.4e-9, 0.15e-9, 120, 'Rx clock output [V]')
