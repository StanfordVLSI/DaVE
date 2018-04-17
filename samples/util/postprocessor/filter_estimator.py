#!/usr/bin/env python 

__doc__ = """
This script estimate a transfer function (a pole or two poles or two poles and a zero) from a step response.
After loading step response waveform, it does fft to get a transfer function (phase data is lost). Then, it will try to fit the transfer function to one of TXF templates.

Assumption:
  1. Input and output are in phase and the input changes from low to high value once anytime after tos
  2. outputs poles and a zero such that p2>p1
"""

from scipy.interpolate import interp1d
from lmfit import minimize, Parameters, Parameter, report_fit
import numpy as np
import pickle as pkl
import os
import sys
import pylab as plt
import scipy
import scipy.fftpack
import math

def ceil_to_power_of_two(value):
  ''' convert a decimal number(value) to a binary string w/ given bit width(bw) '''
  max_bw = 20
  binary_num = "".join(str((int(value)>>i) & 1) for i in range(max_bw-1,-1,-1))
  binary_num = binary_num[binary_num.find('1'):]
  return 2**(len(binary_num)+1)
  

''' objective function '''
def fmin(params, x, y, filter_type):
  ''' objective function 
    param is a dictionary of paramters to fit
    x is frequency in transfer function
    y is magnitude in transfer function
  '''

  f = 1.0j*x
  fp1 = params['fp1'].value
  # step response (zero initial condition)
  if filter_type == 'p1':
    model = abs(1/(1+f/fp1))
  elif filter_type == 'p2z1':
    fp2 = params['fp2'].value # p2z1, p2 only
    fz1 = params['fz1'].value # p2z1 only
    model = abs((1+f/fz1)/(1+f/fp1)/(1+f/fp2))
  elif filter_type == 'p2':
    fp2 = params['fp2'].value # p2z1, p2 only
    model = abs(1/(1+f/fp1)/(1+f/fp2))

  return model-y

def resample_data(filename, ts, ti):
  ''' Resample waveform:
  filename: output waveform file
  ts: time offset to start resampling
  ti: resampling time step
  '''
  data = np.loadtxt(filename)
  t = data[:,0]
  y = data[:,1]
  ti = min(t[-1]-t[-2],ti)
  fn = interp1d(t,y)
  time = np.arange(ts,t[-2],ti)
  return time, fn(time)

def normalize(x, y, t):
  ''' normalize x and y,
      and make time offset be zero 
  '''
  x = x - x[0]
  x = x/x[-1]
  y = y - y[0]
  y = y/y[-1]
  t = t-t[0]
  return x, y, t
  
def normalize_measurement(ifile, ofile, ts, te, ti):
  '''
    ts: time window start
    te: time window end
    ti: resampling time step
  '''
  time, x = resample_data(ifile, ts, ti) # input to a circuit
  time, y = resample_data(ofile, ts, ti) # output out of a circuit


  # see when x starts transitioning and take -1 index offset
  idx = np.argmax(x != x[0]) - 1
  time = time[idx:]
  x    = x[idx:]
  y    = y[idx:]

  # calculate dc gain assuming that simulation time is enough for the output to be settled
  dcgain = (y[-1]-y[0])/(x[-1]-x[0])

  # consider capacitive coupling when starting transition
  if (dcgain <= 0.0): # if gain is negative
    idx = np.argmax(y == max(y)) 
  else:
    idx = np.argmax(y == min(y)) 
  time = time[idx:]
  x    = x[idx:]
  y    = y[idx:]

  # normalize x and y, make time offset 0
  x, y, time = normalize(x,y,time)

  tend = te-ts
  required_bin = tend/ti
  difference = required_bin - len(y)
  # interpolate
  fx = interp1d(time, x)
  fy = interp1d(time, y)
  time = np.arange(0, time[-1], ti)
  x = fx(time)
  y = fy(time)
  if time[-1] > tend:
    x = x[time<=tend]
    y = y[time<=tend]
    time = time[time<=tend]
  elif time[-1] < tend:
    time = np.arange(0, tend, ti)
    x = np.append(x, np.ones(len(time)-len(x))*x[-1])
    y = np.append(y, np.ones(len(time)-len(y))*y[-1])
  np.savetxt(ifile+'.norm',np.vstack((time,x)).T)
  np.savetxt(ofile+'.norm',np.vstack((time,y)).T)
  np.savetxt('time.txt',time)
  plt.plot(time,y,'r-')
  plt.axis([time[0]-10*ti, time[-1]+10*ti, -0.01, max(y)*1.1])
  plt.title('normalized step response, Adc=%.g' %dcgain);
  plt.savefig('stepnorm.png')
  plt.close()
  return time, x, y, dcgain

def guess_p0(f, yf, filter_type, dcgain):
  ''' guess initial condition from the extracted TXF '''

  def find_bw(f, yf, direction):
    yf0 = yf[0]
    threshold = 10.0**((20.0*np.log10(yf0)+direction*1.0)/20.0)
    try:
      if direction==+1:
        f0 = f[yf>=threshold][0]
      else: # direction ==-1
        f0 = f[yf<=threshold][0]
    except:
      f0 = f[-1]
    f0 = f0;
    return f0
      
  if filter_type == 'p2z1':
    if dcgain != 0:
      f0 = find_bw(f, yf, +1)
      return {'fz1': f0, 'fp1': 2.0*f0, 'fp2': 3.0*f0} 
    else:   
      return {'fz1': 0.0, 'fp1': 0.0, 'fp2': 0.0} 
  elif filter_type == 'p1':
    if dcgain != 0:
      f0 = find_bw(f, yf, -1)
      return {'fp1': f0} 
    else: 
      return {'fp1': 0.0}
  elif filter_type == 'p2':
    if dcgain != 0:
      f0 = find_bw(f, yf, -1)
      return {'fp1': f0, 'fp2': 4*f0}
    else:
      return {'fp1': 0.0, 'fp2': 0.0}

def fit(f, yf, param0, filter_type, dcgain):
  '''
  param0: dict with initial conditions of parameters
  '''
  def sort_poles(param):
    ''' sort poles' location if there are more than a pole '''
    poles = sorted(filter(lambda x: x.startswith('fp'), param.keys()))
    zeros = list(set(param.keys())-set(poles))
    print dir(param)
    print param.values
    print param
    if len(poles) > 1:
      pole_loc = sorted([param[p].value for p in poles])
      print pole_loc
      n_param = dict([(poles[k], pole_loc[k]) for k in range(len(poles))])
      n_param.update(dict([(z, param[z].value) for z in zeros]))
      return n_param
    else:
      return dict([(k, v.value) for k,v in param.items()])

  if dcgain !=0:
    for i in range(1):
      # constraints on parameters
      cons = dict([(k,{'min':0}) for k in param0.keys()])
      for k in cons.keys(): cons[k].update({'value': param0[k]})
  
      # set up parameter values
      params = Parameters()
      for k,v in cons.items(): params.add(k, **v)
      result = minimize(fmin, params, args=(f, yf, filter_type) )
      final = yf + result.residual
      report_fit(params)
      param0 = sort_poles(result.params)
      print param0
  
    # compare estimation vs data
    plt.semilogx(f,20.0*np.log10(yf), 'g', label='sim')
    plt.semilogx(f,20.0*np.log10(final), 'r', label='fit')
    plt.legend(loc='best')
    plt.ylabel('Mag [dB]')
    plt.xlabel('Freq [Hz]')
    plt.savefig('fit.png')
    plt.close()
  return param0

def save(params, dcgain):
  param_in_hz = params
  for k,v in param_in_hz.items():
    np.savetxt('meas_%s.txt' % k, [v])
    if k=='fp1':
      np.savetxt('meas_tau1.txt', [(1.0/v/2.0/np.pi)])
  np.savetxt('meas_dcgain.txt', [dcgain])
   
def do_fft(t, y, fmax):
  ''' do fft of (t,y) '''
  yi = np.diff(y) # impulse response
  t = t[:-1]
  ffted = abs(scipy.fft(yi))
  freqs = scipy.fftpack.fftfreq(yi.size,t[1]-t[0])
  ffted = ffted[freqs<fmax]
  freqs = freqs[freqs<fmax]
  ffted = ffted[freqs>=0.0]
  freqs = freqs[freqs>=0.0]
  plt.semilogx(freqs, 20*scipy.log10(ffted))
  plt.savefig('txf.png')
  plt.close()
  return freqs, ffted

def adjust_fmin(f, yf, p0, filter_type, dcgain):
  ''' adjust starting frequency after initial guess of parameters '''
  if dcgain !=0.0:
    if filter_type == 'p2z1':
      yf = yf[f>=p0['fz1']/10.]
      f = f[f>=p0['fz1']/10.]
    elif filter_type in ['p1', 'p2']:
      yf = yf[f>=p0['fp1']/10.]
      f = f[f>=p0['fp1']/10.]
  return f, yf

def adjust_fmax(f, yf, p0, filter_type, dcgain):
  ''' adjust starting frequency after initial guess of parameters '''
  if dcgain !=0.0:
    if filter_type == 'p2z1':
      yf = yf[f<=p0['fz1']*40.]
      f = f[f<=p0['fz1']*40.]
    elif filter_type in ['p1', 'p2']:
      yf = yf[f<=p0['fp1']*40.]
      f = f[f<=p0['fp1']*40.]
  return f, yf

      

def main(args):

  tstart = float(args[0])
  fbin = float(args[1])
  fmax = float(args[2])
  filter_type = args[3]

  fs = fmax*2*2 # sampling rate
  tend  = (1.0+2.0*fmax/fbin)/fs + tstart # required transient time
  N = int(math.ceil((tend-tstart)*fs))
  print 'Rough estimate of transient time end=%.f [ns]' %(tend/1e-9)

  # load step response data and normalize waveforms
  t, x, y, dcgain = normalize_measurement('input.txt', 'output.txt', tstart, tend, 1/fs)
  
  # perform FFT
  if any(np.isnan(y)):
    print 'NaN is found after normalizing step response waveform. All poles and zeros are set to 1e+100 Hz.'
    params = {'fz1':1e100, 'fp1': 1e100, 'fp2': 1e100}
  else:
    if dcgain !=0: 
      f, yf = do_fft(t, y, fmax)
    else:
      f=[]
      yf=[]
  
    # initial condition
    p0 = guess_p0(f, yf, filter_type, dcgain)
  
    # reduce dataset (adjust min. freq.)
    #f, yf = adjust_fmin(f, yf, p0, filter_type, dcgain)
    #f, yf = adjust_fmax(f, yf, p0, filter_type, dcgain)
    params = fit(f, yf, p0, filter_type, dcgain)
  save(params, dcgain)

if __name__=="__main__":
  args = sys.argv[1:]
  main(args)
