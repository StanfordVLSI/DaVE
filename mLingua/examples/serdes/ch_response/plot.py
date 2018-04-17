#! /usr/bin/env python 

"""
  Generate eyediagram and save it to eye.png
"""

import numpy as np
from scipy.interpolate import interp1d
import matplotlib.pylab as plt
import matplotlib
from scipy.signal import lsim, zpk2tf

font = { 'size'   : 19}
matplotlib.rc('font', **font)

def main():
  ts = 2.0e-9 # time start
  te = 11e-9  # time end

  # load verilog simulation data and get 1d interpolator
  data = np.loadtxt('ch_out.txt')
  t = data[:,0]
  y = data[:,1]
  y = y[t>=ts]
  t = t[t>=ts]
  y = y[t<=te]
  t = t[t<=te]
  data = np.loadtxt('tx_out.txt')
  t1 = data[:,0]
  y1 = data[:,1]
  y1 = y1[t1>=ts]
  t1 = t1[t1>=ts]
  y1 = y1[t1<=te]
  t1 = t1[t1<=te]
  t1 = np.array([ts]+list(t1)+[te])
  y1 = np.array([y1[0]]+list(y1)+[y1[-1]])

 
  # plot time, value pairs at which events occur 
  ax1 = plt.subplot(2,1,1)
  plt.plot(t*1e9,y,'o-r', markersize=5)
  plt.ylabel('Channel output [V]')
  plt.legend(loc=1)
  ax1.set_xlim([ts*1e9,te*1e9])
  plt.title('Pulse (200 psec wide) response')

  ax2 = plt.subplot(2,1,2)
  plt.plot(t1*1e9,y1,'o-b', markersize=5)
  plt.ylabel('Pulse input [V]')
  plt.tight_layout()
  ax2.set_xlim([ts*1e9,te*1e9])
  ax2.set_ylim([-1.1,1.1])
  plt.savefig('channel.eps')
  plt.close()


if __name__ == "__main__":
  main()
