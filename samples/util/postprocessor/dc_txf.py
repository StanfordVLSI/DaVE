#! /usr/bin/env python 

"""
  Generate PWL DC transfer curve from transient simulation.
  The assumed PWL function consists of two flat regions and a 
  linear region in-between. There are two cases: positive slope 
  and negative slope

                  _________   __ max(y)
                 /
                /
               /
       _______/               __ min(y)
         
              |   |
          x_imin  x_imax

OR
       _______                __ max(y)
              \    
               \   
                \  
                 \_________   __ min(y)
         
              |   |
          x_imin  x_imax

  This script will produce the followings:
    - meas_x_imin.txt : x value that produces min(y) flat value;
    - meas_x_imax.txt : x value that produces max(y) flat value;
    - meas_slope.txt  : slope in the linear region.
  
  In transient simulation, a slow ramp is driven to an input
  port, and the corresponding output ramp is generated. Both
  ramp signals are saved to two files.
    - "ramp_in" variable : ramp input file
    - "ramp_out" variable: ramp output file
  it is assumed that both ramps are sampled at the same time,
  in a regular interval. 
"""

import sys
import numpy as np
import argparse
from scipy.interpolate import interp1d
from lmfit import minimize, Parameters, report_fit
import matplotlib.pylab as plt

def main():

  parser = argparse.ArgumentParser(description='extract pwl model of a pseudo-dc transfer curve from a transient simulation.')
  parser.add_argument('--input', help='ramp input data filename', default='dctxf_in.txt')
  parser.add_argument('--output', help='response output data filename', default='dctxf_out.txt')
  parser.add_argument('--gain', help='variable name for gain in linear region', default='av')
  parser.add_argument('--imax', help='variable name for max input causes gain compression', default='vi_max')
  parser.add_argument('--imin', help='variable name for min input causes gain compression', default='vi_min')
  parser.add_argument('--ictr', help='variable name for input (imax+imin)/2.0', default='vi_ctr')
  parser.add_argument('--omax', help='variable name for max output', default='vo_max')
  parser.add_argument('--omin', help='variable name for min output', default='vo_min')
  parser.add_argument('--octr', help='variable name for output at input=ictr', default='vo_ctr')


  args = parser.parse_args()

  # user parameters
  oversample_rate = 10 # resample simulation data by this oversampling ratio
  input_filename = args.input
  output_filename = args.output
  meas_slope_filename = 'meas_%s.txt' % args.gain      # gain
  meas_vimax_filename = 'meas_%s.txt' % args.imax # max input value compressed
  meas_vimin_filename = 'meas_%s.txt' % args.imin # min input value compressed
  meas_victr_filename = 'meas_%s.txt' % args.ictr # (vi_max+vi_min)/2.0
  meas_vomax_filename = 'meas_%s.txt' % args.omax # max output value
  meas_vomin_filename = 'meas_%s.txt' % args.omin # min output value
  meas_voctr_filename = 'meas_%s.txt' % args.octr # output value at vi_ctr


  # load simulation data
  ramp_in = np.loadtxt(input_filename)
  ramp_out = np.loadtxt(output_filename)

  # find time, x, y, sampling time interval
  t = ramp_in[:,0]   # time
  x = ramp_in[:,1]   # x-axis
  y = ramp_out[:,1]  # y-axis
  ti = t[-1] - t[-2] # sampling interval

  # sniff the region whre x is increasing
  # at the beginning, end of the simulation 
  # it is possible that input signal is not ramping-up.
  x_width = x[-1]-x[0]
  x_max = x[0] + (x_width)*0.95  # max(x): 95% (change if you want)
  x_min = x[0] + (x_width)*0.05  # min(x):  5% (change if you want)
  x_width = x_max - x_min
  indices = np.intersect1d(np.where(x > x_min), np.where(x < x_max))
  t = t[indices]
  x = x[indices]
  y = y[indices]
  xs = x[-1]-x[-2] # x-step

  # create an interpolation function and resample data
  fn_interp = interp1d(x,y)
  x = np.arange(x[1],x[-2]+0.1*xs/oversample_rate,xs/oversample_rate) 
  y = fn_interp(x)

  def generate_pwl(x1o,x2o):
    x1 = min(x1o,x2o);
    x2 = max(x1o,x2o);
    y1 = y[0]
    y2 = y[-1]
    slope = (y2-y1)/(x2-x1)
    y_min = min(y1,y2)
    y_max = max(y1,y2)
    def fn_pwl(x):
      def fn(x):
        return y1 + slope*(x-x1)
      if x <= x1:
        return fn(x1)
      elif x >= x2:
        return fn(x2)
      else:
        return fn(x)

    return fn_pwl, y_min, y_max, slope

  def residual(params):
    ''' minimize residual errors by adjusting 
        linear region width of a dc transfer curve
        using param['p']
    '''
    # 
    x1 = params['x1'].value
    x2 = params['x2'].value
    fn, y_min, y_max, slope = generate_pwl(x1,x2)
  
    y_new = fn_interp(x)
    y_pwl = map(fn, x)
  
    return y_pwl-y_new

  # Get pwl functions of a dc-txf using nonlinear fit
  params = Parameters()
  params.add('x1', value=min(x), vary=True)
  params.add('x2', value=max(x), vary=True)
  result = minimize(residual, params)
  report_fit(params)
  final = y + result.residual
  x1 = result.params['x1'].value
  x2 = result.params['x2'].value
  fn, y_min, y_max, slope = generate_pwl(x1,x2)
  x_imin = min(x1,x2)
  x_imax = max(x1,x2)
  x_center = (x_imin+x_imax)/2.0
  y_center = fn(x_center)
  print result.params
  print '%s =' % args.imin, x_imin
  print '%s =' % args.imax, x_imax
  print '%s =' % args.ictr, x_center
  print '%s =' % args.omin, y_min
  print '%s =' % args.omax, y_max
  print '%s =' % args.octr, y_center
  print '%s =' % args.gain, slope
  
  # save results to a file
  np.savetxt(meas_vomin_filename, [y_min])
  np.savetxt(meas_vomax_filename, [y_max])
  np.savetxt(meas_voctr_filename, [y_center])
  np.savetxt(meas_vimin_filename, [x_imin])
  np.savetxt(meas_vimax_filename, [x_imax])
  np.savetxt(meas_victr_filename, [x_center])
  np.savetxt(meas_slope_filename, [slope])

  # save optimization plots
  plt.plot(x,y)
  plt.plot(x, final,'ro',markersize=1)
  plt.xlabel('X')
  plt.ylabel('Y')
  plt.savefig('dctxf.png')
  plt.close()
  plt.plot(x, result.residual)
  plt.xlabel('X')
  plt.xlabel('Residual error')
  plt.savefig('dctxf_residual.png')
  plt.close()

if __name__ == "__main__":
  main()
