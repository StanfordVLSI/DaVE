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
  ts = 1e-12  # time resolution 
  tos = 19e-9
  tend = 30e-9
  #tos = 28.2e-9
  #tend = 38e-9
  wp1 = -2.0*np.pi*0.5e9
  gain = -1.0*wp1


  # load verilog simulation data and get 1d interpolator
  data = np.loadtxt('output.txt')
  t = data[:,0]
  yv = data[:,1]
  fn_vlog = interp1d(t,yv)
  time = np.arange(t[0],t[-1],ts)
  time2 = np.arange(t[0],tend,ts)
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
  t0,y0,x0 = lsim(zpk2tf([],[wp1],gain), x2, time2, X0=0)

  # residual error
  y_vlog = fn_vlog(time)
  if no_sample > 0:
    y_vlog = np.array(list(y_vlog) + no_sample*[y_vlog[-1]])
  else:
    y_vlog = y_vlog[:no_sample]

  err = y_vlog - y0
  #for i,v in enumerate(err[t0>tos]):
  #  print (t0[t0>tos])[i]*1e15, ':', abs(v)*1000
  print max(abs(err[t0>tos]))*1000
 
  # plot time, value pairs at which events occur 
  plt.subplot(2,1,1)
  plt.plot(1e9*t[t>tos],yv[t>tos],'or', label='Verilog', markersize=5)
  plt.plot(1e9*t0[t0>tos],y0[t0>tos], label='Analytic expression')
  #plt.xlabel('Time [nsec]')
  plt.ylabel('Output [V]')
  plt.axis([tos*1e9, tend*1e9, -0.2, 0.2])
  #plt.title(r'$e_{tol}$'+'=1 mV'+', |maximum error|=%.1f mV' % (max(err[t>tos])*1000))
  plt.legend(loc=4)

  plt.subplot(2,1,2)
  plt.plot(1e9*t0[t0>tos],1000*err[t0>tos],'r')
  plt.xlabel('Time [nsec]')
  plt.ylabel('Residual error [mV]')
  plt.axis([tos*1e9, tend*1e9, -1.0, 1.0])
  plt.tight_layout()
  plt.savefig('spf_step_response.eps')
  plt.close()


if __name__ == "__main__":
  main()
