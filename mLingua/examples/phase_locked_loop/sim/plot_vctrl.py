#! /usr/bin/env python 

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

  te = 300

  tws = 100
  twe = 300

  # load verilog simulation data 
  data = np.loadtxt('vctrl.txt')
  t = data[:,0]
  t = t*1e9
  y = data[:,1]
  y = y[t<=te]
  t = t[t<=te]

  y1 = y[t>tws]
  t1 = t[t>tws]
  y1 = y1[t1<twe]
  t1 = t1[t1<twe]


  fig, ax1 = plt.subplots()
  ax1.plot(t,y)
  ax1.set_xlabel('Time [nsec]')
  ax1.set_ylabel('Vctrl [V]')
  ax1.set_ylim([0,0.65])
  ax1.set_xlim([0,te])
  if (t[-1]<te):
    ax1.plot([t[-1],te],[y[-1],y[-1]])
  ax2 = inset_axes(ax1, width='40%',height='40%', loc=5)
  ax2.plot(t1,y1,'o-', markersize=2)
  if (t1[-1]<twe):
    ax2.plot([t1[-1],twe],[y1[-1],y1[-1]],'o-', markersize=2)
  if (t1[0]>tws):
    ax2.plot([tws,t1[0]],[y1[0],y1[0]],'o-', markersize=2)
  ax2.get_yaxis().get_major_formatter().set_useOffset(False)
  ax2.get_xaxis().get_major_formatter().set_useOffset(False)
  ax2.set_xticks([tws,twe])
  mark_inset(ax1, ax2, loc1=1, loc2=2, fc='none', ec='0.5')


  #plt.show()
  plt.tight_layout()
  plt.savefig('pll_vctrl.eps')
  plt.close()


if __name__ == "__main__":
  main()
