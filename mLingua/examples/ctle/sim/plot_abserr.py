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

def plot(index):
  ts = 1e-12  # time resolution 
  tos = 19e-9
  tend = 30e-9
  wz1 = -2.0*np.pi*0.55e9
  wp1 = -2.0*np.pi*1.2e9
  wp2 = -2.0*np.pi*3.4e9
  gain = -1.0*wp1*wp2/wz1
  
  if index == 1:
    simout_filename = 'eq_out1.txt'
    gs_filename = 'ctle_pulse_response_1.eps'
  elif index == 2:
    simout_filename = 'eq_out2.txt'
    gs_filename = 'ctle_pulse_response_2.eps'
  elif index == 3:
    simout_filename = 'eq_out3.txt'
    gs_filename = 'ctle_pulse_response_3.eps'

  # load verilog simulation data and get 1d interpolator
  data1 = np.loadtxt(simout_filename)
  t = data1[:,0]
  yv = data1[:,1]
  fn_vlog = interp1d(t,yv)
  time = np.arange(t[0],t[-1],ts)
  time2 = np.arange(t[0],tend,ts)
  time = time[:-1]
  time2 = time2[:-1]
  no_sample = len(time2)-len(time)

  xdata = np.loadtxt('input.txt')
  xt = np.append(xdata[:,0],t[-1])
  xy = np.append(xdata[:,1],xdata[:,1][-1])
  fn_x = interp1d(xt,xy)
  x=fn_x(time)
  if no_sample > 0:
    x2 = np.array(list(x) + no_sample*[x[-1]])
  else:
    x2 = x[:no_sample]

  # ideal transfer function in s-domain
  t0,y0,x0 = lsim(zpk2tf([wz1],[wp1,wp2],gain), x2, time2)

  # residual error
  y_vlog = fn_vlog(time)
  if no_sample > 0:
    y_vlog = np.array(list(y_vlog) + no_sample*[y_vlog[-1]])
  else:
    y_vlog = y_vlog[:no_sample]

  err = y_vlog - y0
  print 'Max. residual error = %.1f [mV]' % (max(abs(err[t0>tos]))*1000)
 
  # plot time, value pairs at which events occur 
  plt.subplot(2,1,1)
  plt.plot(1e9*t[t>tos],yv[t>tos],'or', label='Verilog', markersize=5)
  plt.plot(1e9*t0[t0>tos],y0[t0>tos], label='Analytic expression')
  plt.xlabel('Time [nsec]')
  plt.ylabel('Output [V]')
  plt.axis([tos*1e9, tend*1e9, -0.20, 0.20])
  #plt.title('Pulse response of CTLE ('+r'$e_{tol}$'+'=1 [mV])')
  plt.legend(loc=0)

  plt.subplot(2,1,2)
  plt.plot(1e9*t0[t0>tos],1000*err[t0>tos],'r')
  plt.xlabel('Time [nsec]')
  plt.ylabel('Residual error [mV]')
  plt.axis([tos*1e9, tend*1e9, -20, 20])
  plt.tight_layout()
  plt.savefig(gs_filename)
  plt.close()

def main():
  plot(1) # plot result of ctle.v sim
  plot(2) # plot result of ctle_pfe.v sim
  plot(3) # plot result of ctle_pfe.v sim

if __name__ == "__main__":
  main()
