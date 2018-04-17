#! /usr/bin/env python 


"""
  Generate eyediagram and save it to eye.png
"""

import numpy as np
from scipy.interpolate import interp1d
import matplotlib.pylab as plt
import matplotlib
from scipy.signal import lsim, zpk2tf
from mpl_toolkits.axes_grid1.inset_locator import inset_axes, zoomed_inset_axes
from mpl_toolkits.axes_grid1.inset_locator import mark_inset
font = { 'size'   : 19}
matplotlib.rc('font', **font)

def main():
  # load verilog simulation data 
  te = 5e-3
  data = np.loadtxt('vout.txt')
  t = data[:,0]
  y = data[:,1]
  y = y[t<=te] 
  t = t[t<=te]

  y1 = y[t>4.0e-3]
  t1 = t[t>4.0e-3]
  y1 = y1[t1<4.004e-3]
  t1 = t1[t1<4.004e-3]

  t = t*1e3
  t1 = t1*1e3

  fig, ax1 = plt.subplots()
  ax1.plot(t,y,'b')
  ax1.set_xlabel('Time [msec]')
  ax1.set_ylabel('Voltage [V]')
  ax1.set_ylim([-0.2, max(y)*1.1])
  ax2 = inset_axes(ax1, width='45%',height='45%', loc=5)
  ax2.plot(t1,y1, 'or-')
  ax2.get_yaxis().get_major_formatter().set_useOffset(False)
  ax2.get_xaxis().get_major_formatter().set_useOffset(False)
  ax2.set_xticks([t1[0],t1[-1]])
  mark_inset(ax1, ax2, loc1=1, loc2=2, fc='none', ec='0.5')


  #plt.show()
  plt.tight_layout()
  plt.savefig('buck.eps')
  plt.close()

  #fig, ax1 = plt.subplots()
  #ax1.plot(t,y,'b')
  #ax1.set_xlabel('Time [msec]')
  #ax1.set_ylabel('Voltage [V]')
  #plt.tight_layout()
  #plt.savefig('buck.eps')
  #plt.close()


if __name__ == "__main__":
  main()
