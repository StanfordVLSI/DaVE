#!/usr/bin/env python

# Simulation control and postprocessing

import numpy as np
from scipy.interpolate import interp1d
import matplotlib.pylab as plt
import matplotlib

font = {'size'   : 19, 'family': 'serif'}
matplotlib.rc('font', **font)

ts1 = 15.38e-6
te1 = 15.60e-6
ts2 = 20.38e-6
te2 = 20.60e-6

cktsim = '../cktsim/classAB/wave.dat'
mdlsim = './inm.txt'

def get_wave(ts, te, titlename, loc, wavename):
  # circuit sim 
  res = np.loadtxt(cktsim)
  time = res[:,0]
  inp = res[:,1]
  out = res[:,2]
  time1 = time[time>ts]
  inp1  = inp[time>ts]
  out1  = out[time>ts]
  time1 = time1[time1<te]
  inp1  = inp1[time1<te]
  out1  = out1[time1<te]
  time1 = [ts]+list(time1)+[te]
  inp1  = [inp1[0]]+list(inp1)+[inp1[-1]]
  out1  = [out1[0]]+list(out1)+[out1[-1]]
  
  # verilog sim
  resv = np.loadtxt(mdlsim)
  timev = resv[:,0]
  outv = resv[:,1]
  fn_mdl = interp1d(timev, outv)
  outvnew = fn_mdl(time1)
  
  time1 = np.array(time1)*1e6

  xticks = [20.4, 20.5, 20.6] if wavename == 'dota_fall.eps' else [15.4, 15.5, 15.6]
  
  plt.subplot(2,1,1)
  plt.plot(time1, inp1, 'r', label='Input')
  plt.axis([ts*1e6, te*1e6, 0.9*min(out), 1.1*max(out)])
  plt.ylabel(r'$V_{IN+}$'+' [V]')
  fr1 = plt.gca()
  fr1.set_xlim([ts*1e6, te*1e6,])
  fr1.set_yticks([1.4,2.5])
  fr1.set_xticks(xticks)
  fr1.axes.get_xaxis().set_ticklabels([])
  fr1.axes.get_xaxis().grid(True)
  plt.legend(fontsize=16, loc=loc)

  plt.subplot(2,1,2)
  plt.plot(time1, out1, 'r^-', label='Circuit', markersize=8)
  plt.plot(timev*1e6, outv, '+--', label='Verilog', markeredgecolor='blue', markerfacecolor='none', markersize=14, markeredgewidth=2)
  plt.axis([ts*1e6, te*1e6, 0.9*min(out), 1.1*max(out)])
  plt.ylabel(r'$V_{OUT}$'+' [V]')
  fr1 = plt.gca()
  fr1.set_xlim([ts*1e6, te*1e6,])
  fr1.set_yticks([1.4,2.5])
  fr1.set_xticks(xticks)
  fr1.axes.get_xaxis().grid(True)
  plt.xlabel('Time [usec]')
  fr1 = plt.gca()
  plt.legend(fontsize=16, loc=loc)
  plt.savefig(wavename)
  plt.close()

get_wave(ts1, te1, 'Rise transition ('+r'$t_{rise}=10$'+' [nsec], VDD=3.3 [V])', 'best', 'dota_rise.eps')
get_wave(ts2, te2, 'Fall transition ('+r'$t_{fall}=10$'+' [nsec], VDD=3.3 [V])', 'best', 'dota_fall.eps')
