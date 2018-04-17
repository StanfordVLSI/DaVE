#! /usr/bin/env python 

"""
  Generate eyediagram and save it to eye.eps
"""

import argparse
import numpy as np
from scipy.interpolate import interp1d
import matplotlib.pylab as plt
from matplotlib.colors import Normalize

def resample(data, time):
  xs = data[:,0]
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

def run(filename, imgname, period, time_offset, nbin):    
  data = np.loadtxt(filename)
  x = data[:,0]
  t_start = x[0]
  t_stop = x[-1]
  t_step = period/nbin
  time = np.arange(t_start, t_stop, t_step)
  sample = resample(data, time)
  y,x=rollover(sample, time, period, time_offset)

  H, yedges, xedges = np.histogram2d(y, x, bins=nbin)

  s = sum(H)

  fig = plt.figure()
  ax = plt.gca()
  extent=[min(xedges), max(xedges), min(yedges), max(yedges)]
  aspect = (max(xedges)-min(xedges))/(max(yedges)-min(yedges))
  cax=plt.imshow(H/s,interpolation='nearest',cmap=plt.cm.coolwarm, extent=extent, norm=Normalize(), aspect=aspect)
  #cax=plt.imshow(H/s,interpolation='gaussian',cmap=plt.cm.coolwarm, extent=extent, norm=Normalize(), aspect=aspect)
  plt.grid(color='w')
  fig.colorbar(cax)
  ax.set_axis_bgcolor('k')

  plt.savefig(imgname)

if __name__ == "__main__":
  run('ch_out.txt','ch_out.eps', 0.4e-9, 0, 120)
