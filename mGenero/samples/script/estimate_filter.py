#!/usr/bin/env python 

__doc__ = """
This script estimate a transfer function (a pole or two poles or two poles and a zero) from a step response.

Assumption:
  1. Input and output are in phase and the input changes from low to high value once anytime after tos
  2. outputs poles and a zero such that p2>p1
"""

from scipy.interpolate import interp1d
from lmfit import minimize, Parameters, Parameter, report_fit
import numpy as np
import pickle as pkl
import os
import pylab as plt

pi = np.pi

''' objective function '''
def fmin(params, t, y, filter_type):
  ''' objective function 
    param is a dictionary of paramters to fit
    t is time
    y is the output value
  '''

  p1 = params['p1'].value
  # step response (zero initial condition)
  if filter_type == 'p1':
    model =  1.0 + -1.0*np.exp(-p1*t)
  elif filter_type == 'p2z1':
    p2 = params['p2'].value # p2z1 only
    z1 = params['z1'].value # p2z1 only
    model =  1.0 + (p1*p2 -p1*z1)*np.exp(-p2*t)/(z1*(p1 - p2)) - (p1*p2 - p2*z1)*np.exp(-p1*t)/(z1*(p1 - p2))

  return model-y

def resample_data(filename, tos, ti):
  ''' Resample waveform:
  filename: output waveform file
  tos: time offset to start resampling
  ti: resampling time step
  '''
  data = np.loadtxt(filename)
  t = data[:,0]
  y = data[:,1]
  y = y[t>=tos]
  t = t[t>=tos]
  fn = interp1d(t,y)
  time = np.arange(t[0],t[-1],ti)
  return time, fn(time)

def normalize(x, y, t):
  x = x - x[0]
  x = x/x[-1]
  y = y - y[0]
  y = y/y[-1]
  t = t-t[0]
  return x, y, t
  
def normalize_measurement(ifile, ofile, tos, ti, etol):
  '''
    tos: time offset (neglecting data before this time)
    ti: resampling time step
    etol: error tolerance to judge signal settling
  '''
  time, x = resample_data(ifile, tos, ti) # input to a circuit
  time, y = resample_data(ofile, tos, ti) # output out of a circuit

  # calculate dc gain assuming that simulation time is enough for the output to be settled
  dcgain = (y[-1]-y[0])/(x[-1]-x[0])

  # see when x starts transitioning and take -1 index offset
  idx = np.argmax(x != x[0]) - 1
  time = time[idx:]
  x    = x[idx:]
  y    = y[idx:]

  # consider capacitive coupling when starting transition
  idx = np.argmax(y == min(y)) 
  time = time[idx:]
  x    = x[idx:]
  y    = y[idx:]

  # normalize x and y
  x, y, time = normalize(x,y,time)

  # see when y is settled within etol and chop data with some margin
  # note that long steady-state condition in y waveform means more DC component, which affects the estimation result.
  multi = 1.1
  ydiff = y[-1]-y[::-1]
  idx = np.argmax(abs(ydiff) > etol) # see the last index that abs(y-y(inf)) > etol
  #idx = min(y.size, multi*idx) # reduce data set
  idx = y.size # reduce data set
  y = y[:idx]
  x = x[:idx]
  time = time[:idx]

  # normalize x and y
  x, y, time = normalize(x,y,time)
  
  np.savetxt(ifile+'.norm',x)
  np.savetxt(ofile+'.norm',y)
  np.savetxt('time.txt',time)
  return time, x, y, dcgain

def fit(t, y, param0, filter_type):
  '''
  param0: dict with initial conditions of parameters
  '''
  def sort_poles(param):
    ''' sort poles' location if there are more than a pole '''
    poles = sorted(filter(lambda x: x.startswith('p'), param.keys()))
    zeros = list(set(param.keys())-set(poles))
    if len(poles) > 1:
      pole_loc = sorted([param[p].value for p in poles])
      n_param = dict([(poles[k], pole_loc[k]) for k in range(len(poles))])
      n_param.update(dict([(z, param[z].value) for z in zeros]))
      return n_param
    else:
      return dict([(k, v.value) for k,v in param.items()])

  for i in range(1):
    # constraints on parameters
    cons = dict([(k,{'min':0}) for k in param0.keys()])
    for k in cons.keys(): cons[k].update({'value': param0[k]})

    # set up parameter values
    params = Parameters()
    for k,v in cons.items(): params.add(k, **v)
    result = minimize(fmin, params, args=(t, y, filter_type) )
    final = y + result.residual
    report_fit(params)

    # compare estimation vs data
    #plt.plot(t,y, label='sim')
    #plt.plot(t,final, label='fit')
    #plt.legend()
    #plt.savefig('wave.png')

    param0 = sort_poles(params)
  return param0

def save(params, dcgain):
  param_in_hz = dict([('f'+k, params[k]/np.pi/2.0) for k in params.keys()])
  for k,v in param_in_hz.items():
    np.savetxt('meas_%s.txt' % k, [v])
  np.savetxt('meas_dcgain.txt', [dcgain])
   

def main():

  # load step response data
  t, x, y, dcgain = normalize_measurement('input.txt', 'output.txt', 10e-9, 1e-12, 0.0001)

  # initial condition
  # Since it is a nonlinear fit, the initial condition is important.
  # But, you have some idea what those values are (espectially poles)
  p0 = {'p1':1.3598e9, 'p2':7.226e9, 'z1':1.528e9}

  params = fit(t, y, p0, 'p2z1')
  save(params, dcgain)

if __name__=="__main__":
  main()
