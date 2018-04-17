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
  wz0 = 3.94e9
  a1 = -1.30e8
  b1 = -4.44e9
  a2 = -1.729e9
  b2 = 3.7611e8
  a3 = 7.263e7
  b3 = 3.086e8
  wp0 = 2.186e9
  c1 = 4.1533e9
  d1 = 6.611e9
  c2 = 4.00e9
  d2 = 1.4995e10
  c3 = 2.252e9
  d3 = 2.382e10


  #gain = abs(wp0*wp10*wp11*wp20*wp21*wp30*wp31/wz0/wz10/wz11/wz20/wz21/wz30/wz31)
  gain = 1

  # load verilog simulation data and get 1d interpolator
  data = np.loadtxt('ch_out.txt')
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
  tf0 = zpk2tf([wz0],[wp0],1.0) 
  t0,y0,x0 = lsim(([wz0],[1,wp0]), x2, time2)
  t0,y1,x0 = lsim([[2.0*a1, 2.0*(a1*c1+b1*d1)],[1.0,2.0*c1,c1*c1+d1*d1]], x2, time2)
  t0,y2,x0 = lsim(([2.0*a2, 2.0*(a2*c2+b2*d2)],[1.0,2.0*c2,c2*c2+d2*d2]), x2, time2)
  t0,y3,x0 = lsim(([2.0*a3, 2.0*(a3*c3+b3*d3)],[1.0,2.0*c3,c3*c3+d3*d3]), x2, time2)

  y0 = y0 + y1 + y2 + y3

  # residual error
  y_vlog = fn_vlog(time)
  if no_sample > 0:
    y_vlog = np.array(list(y_vlog) + no_sample*[y_vlog[-1]])
  else:
    y_vlog = y_vlog[:no_sample]
  err = y_vlog - y0
  print max(abs(err[t0>tos]))*1000
 
  # plot time, value pairs at which events occur 
  plt.subplot(2,1,1)
  plt.plot(t[t>tos]*1e9,yv[t>tos],'or', label='Verilog', markersize=5)
  plt.plot(t0[t0>tos]*1e9,y0[t0>tos], label='Analytic expression')
  #plt.plot(t0[t0>tos],x[t0>tos],'g', label='Ramp Input')
  #plt.xlabel('Time [sec]')
  #plt.axis([tos*1e9, tend*1e9, -0.1, 0.1])
  plt.ylabel('Output [V]')
  #plt.title('Pulse response of channel (abstol=5 [mV])')
  plt.legend(loc=1)

  plt.subplot(2,1,2)
  plt.plot(t0[t0>tos]*1e9,err[t0>tos]*1000,'r')
  #plt.axis([tos*1e9, tend*1e9, -5, 5])
  plt.xlabel('Time [nsec]')
  plt.ylabel('Residual error [mV]')
  plt.tight_layout()
  plt.savefig('channel_5mv.eps')
  plt.close()

  y_max = max(y_vlog)
  y = list(y_vlog)
  idx_ref = list(y_vlog).index(y_max)
  print 'main_cursor =', max(y_vlog)
  print 'pre_cursor =', y[idx_ref - int(200e-12/ts)]
  print 'post_cursor =', y[idx_ref + int(200e-12/ts)]
  


if __name__ == "__main__":
  main()
