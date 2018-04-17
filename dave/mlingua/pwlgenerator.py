# Test out PWL waveform generator

import os
import sys
import re
import sympy as sym
import numpy as np
import matplotlib
#matplotlib.use('Agg')
import matplotlib.pyplot as plt

from dave.common.empyinterface import EmpyInterface
from dave.mlingua.pwlbasisfunction import PWLBasisFunctionExpr
from dave.mlingua.pwlvector import PWLVector
from dave.mlingua.lookuptable import LookUpTable1D, mergeLUT


class PWLWaveGenerator(object):
  ''' PWL waveform generator for verifying the algorithm
        - Load function and generate PWL vector
        - fn is a list of tuples
        - An item in each tuple is ( basis function, scale factor, arg(s) of basis function )
        - Then, the function built is a sum of basis functions listed in this "fn"

    >>> pwlgen = PWLWaveGenerator(0.01)
    ''>>> fn_list = [('exp',1.2,0.5), ('t*exp',0.8,1.2), ('exp*cos', 0.9, 1.5, 6.0)]
    >>> fn_list = [('exp',1.0,1.0)]
    >>> pwlgen.load_fn(fn_list, 0.0, 20, 0.003)
    >>> pwlgen.generate()
  '''
  def __init__(self, etol, wv_suffix=''):
    '''
      etol: truncation error tolerance 
    '''
    self._etol = etol
    self._pwl = PWLVector()
    self.__wv_suffix = wv_suffix # suffix of storing waveform image

  def load_fn(self, f, x0, xmax, dx):
    ''' load function 
      f: function without x offset
      x0: x offset, the output at x0 will be f(x0)
      xmax: [x0,x0+xmax] is the valid range 
    '''
    bf = PWLBasisFunctionExpr(f)
    self._f_str, self._f2_str = bf.get_fn_str()
    self._f, self._f2 = bf.get_fn()
    self._x0 = x0
    self._xmax = x0+xmax
    self._dx = dx
    self._x = [x for x in np.arange(self._x0, self._xmax, dx)] # x-grid
    self._y = [self.f_at(x) for x in self._x]

  def get_fn_str(self):
    return self._f_str

  def get_fn2_str(self):
    return self._f2_str

  def __abs_f2_at(self, x):
    return abs(self.f2_at(x))

  def load_waveform(self):
    ''' load waveform file instead of a function (load_fn) '''
    pass


  def generate(self):
    '''  generate/validate pwl Vector
    '''
    self.generate_pwl(self._x0, self._xmax)
    self.validate()

  def generate_pwl(self, x0, xmax):
    ''' generate PWL Vector '''
    x = x0
    self._pwl.set_init(x, self.f_at(x)) # initial point
    while x < xmax:
      dt=self.calculate_dT(self._etol, x) # calculate time step
      x = min(x+dt, xmax)
      self._pwl.add(x, self.f_at(x))
    self._xlut, self._ylut = self._pwl.get_inflection_pts()


  def validate(self):
    x = self._x
    # plot inflection points of the PWL waveform and the real values 
    fig = self._pwl.plot(x, 'time', 'signal', 'Real waveform and PWL inflection pts', 
                          y=self._y, filename='wv_func%s.png' %self.__wv_suffix, annotate=False)
    xs, ys = self._pwl.get_inflection_pts()
    # save series of time step
    self.__dt = [xs[i+1]-xs[i] for i in range(len(xs)-1)] 
    self.plot_dT(xs[:-1], self.__dt)
    # plot/check error-related stuffs
    err_pass = self.check_error()

  def check_error(self):
    ''' calculate error and report '''
    x = self._x
    self.__err = np.array(self._pwl.predict(x)) - np.array(self._y) # error 
    self.__max_err = max(abs(self.__err))
    self.plot_error(x, self.__err, self.__max_err, self._etol)
    return True if self.__max_err <= self._etol else False

  def calculate_dT(self, etol, x0):
    ''' calculate the next time stamp (or time interval) at x=x0 '''
    dt = self.__estimate_dT(etol, x0)
    return dt

  def __estimate_dT(self, etol, x0):
    '''
      This estimates the time interval of PWL vector at x=x0.
    '''
    dt1 = self.__get_dT_bound(etol, self.f2_at(x0))
    return dt1

  def __get_dT_bound(self, etol, f2_max):
    ''' ref: Li's thesis '''
    #return self._snap_dT(np.sqrt(8.0*abs(etol/f2_max)))
    return np.sqrt(8.0*abs(etol/f2_max))

  def _snap_to_grid(self, x, dx):
    ''' snap the value (x) to the grid (dx) '''
    if x/dx == np.inf:
      return dx
    return dx*int(x/dx)

  def _snap_dT(self, dt):
    dt = self._snap_to_grid(dt, self._dx)
    return dt if dt != 0.0 else self._dx

  def plot_dT(self, x0, dt):
    ''' plot the time intervals of the generated PWL '''
    self.__plot(x0, dt, 'Time', r'$\Delta t$', 
                'PWL time interval vs. time: min(dT)=%s, # of events=%d' % (to_engr(min(dt)), len(dt) ), 'wv_dT%s.png' %self.__wv_suffix)

  def plot_error(self, x, err, max_err, etol):
    ''' plot the residual error '''
    self.__plot(x, err, 'Time', 'Error', 'PWL residual Error: max(Error)=%s,' % to_engr(max_err) + ' ' + r'$e_{tol}$' + '=%s' % to_engr(etol), 'wv_error%s.png' %self.__wv_suffix)

  def __plot(self, x, y, xlabel, ylabel, title, filename):
    plt.figure()
    plt.plot(x, y, 'o-')
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.savefig(filename)
    plt.close()

  def f_at(self, x):
    ''' find the value of f() at x '''
    return self._f(x-self._x0)

  def f2_at(self, x):
    ''' find the value of f''() at x '''
    return self._f2(x-self._x0)

def to_engr (value,dtype=float):
  ''' convert a floating number to engineering notation 
      if value < 1e-18 , it returns 0.0
  ''' 
  suffix = [('a', 1e-18), ('f', 1e-15), ('p', 1e-12), 
            ('n', 1e-9), ('u', 1e-6), ('m', 1e-3),  
            ('', 1.0), ('k', 1e3), ('M', 1e6), 
            ('G', 1e9), ('T', 1e12), ('P', 1e15), 
            ('E', 1e18)]
  try:             
    m = abs(value)
    if m < suffix[0][1]: # if less than 1e-18
      return '0.0'
    elif m >= suffix[-1][1]: # if larger than 1e18
      return '%.3f'%(dtype(value/suffix[-1][1]))+suffix[-1][0]
    else:
      for p,v in enumerate(suffix):
        if m/v[1] < 1.0:
          return '%.3f'%(dtype(value/suffix[p-1][1]))+suffix[p-1][0]
  except:
    return None

class PWLWaveLUTGenerator(PWLWaveGenerator):
  def __init__(self, etol, wv_suffix=''):
    PWLWaveGenerator.__init__(self, etol, wv_suffix)

  def load_fn(self, f, x0, xmax, dx):
    bf = PWLBasisFunctionExpr(f)
    self._f_str, self._f2_str = bf.get_fn_str()
    self._f, self._f2 = bf.get_fn()
    self.res = dx/4 # resolution
    self._x0 = 0.0
    self._xmax = self._snap_to_grid(xmax, dx)
    self._dx = dx
    self._x = [x for x in np.arange(self._x0, self._xmax, self.res)] # x-grid
    self._y = [self.f_at(x) for x in self._x]

  def generate(self, validate=True):
    '''  generate/validate pwl Vector
    '''
    self.generate_pwl(self._xmax)
    if validate:
      self.validate()

  def generate_pwl(self, xmax):
    ''' generate PWL Vector '''
    x = 0.0
    self._pwl.set_init(x, self.f_at(x)) # initial point
    while x < xmax:
      dt=self.calculate_dT(self._etol, x, xmax) # calculate time step
      x = min(x+dt, xmax)
      self._pwl.add(x, self.f_at(x))
    self._xlut, self._ylut = self._pwl.get_inflection_pts()

  def calculate_dT(self, etol, x, xmax):
    ''' naive algorithm '''
    dt = 0.0
    while x < xmax:
      dt = dt + self._dx
      if (x+dt) > xmax:
        return xmax - x
      pwl = PWLVector()
      pwl.set_init(x, self.f_at(x)) 
      pwl.add(x+dt, self.f_at(x+dt))
      xtest = [t for t in np.arange(x, x+dt, self.res)]
      y = map(self.f_at, xtest)
      err = np.array(pwl.predict(xtest)) - np.array(y) # error 
      maxerr = max(abs(err))
      if maxerr > self._etol:
        if dt != self._dx:
          dt = dt - self._dx
        else:
          print "Grid is too large!!! Decrease grid setting."
          sys.exit
        return dt
    return dt

  def put_lutname(self, name):
    self.lutname= name

  def get_xlut(self):
    return list(self._xlut)

  def get_ylut(self):
    return list(self._ylut)

  def save_LUT(self, lutname):
    ''' save xs, ys '''
    self._lut = LookUpTable1D(lutname, self._xlut, self._ylut)

  def read_LUT(self):
    return self._lut.read()

  def load_LUT(self, x, y):
    self._x = x;
    self._y = y;

  def generate_LUT(self, xs, ys):
    LookUpTable1D(self.lutname, xs, ys)

  def generate_verilog(self, module_name):
    template = os.path.abspath(os.path.join(os.environ['DAVE_INST_DIR'], 'dave/mlingua/resource', 'periodic.empy'))
    param = { 'lutx': self._xlut, 
              'luty': self._ylut,
              'LUTSize': len(self._xlut),
              'etol': self._etol,
              'module_name': module_name
            }
    EmpyInterface(module_name+'.v')(template, param)

#----------------------
# Example function here
#----------------------


def main():
  #import doctest
  #doctest.testmod()

  '''
  fn_list = [[('const',1.0), ('exp', -1.0, 1.0)], 
             [('exp', 1.0, 1.0)],
             [('exp*cos', 1.0, 1.0/0.12, 0.34)],
             [('exp*cos', 1.0, 1.0/0.12, 6.68)],
             [('t*exp', 1.0, 1.0)],
             [('const',1.0), ('exp', -1.0, 1.0), ('exp*cos', 0.4, 1.0/0.12, 3.34)],
             [('exp', -1.0, 1.0/0.12), ('exp', 1.0, 1.0)],
             [('cos', 2.0, 6.68)] ]
  fn_list = [ [('exp', 1.0, 1.0)],
              [('t*exp', 1.0, 1.0)],
              [('exp*cos', 1.0, 6.0, 1.0)],
              [('cos', 1.0, 1.0)]
            ]
  '''
  fn_list = [ [('exp', 1.0, 1.0)]]
  #fn_list = [ [('sqrt',1.0,1.0)]]
  #fn_list = [ [('exp*cos', 1.0, 1.0, 1.5917757215463133)], [('exp*sin', 1.0, 1.0, 1.5917757215463133)] ] # ch1
  #fn_list = [ [('exp*cos', 1.0, 1.0, 3.7468679193989605)], [('exp*sin', 1.0, 1.0, 3.7468679193989605)]] # ch2
  #fn_list = [ [('exp*cos', 1.0, 1.0, 10.578749452189886)], [('exp*sin', 1.0, 1.0, 10.578749452189886)]] # ch3
  for idx, fn in enumerate(fn_list):
    name = 'lut_'+fn[0][0].replace('*','_')
    #pwlgen = PWLWaveLUTGenerator(0.001, wv_suffix='_%s' % name)
    pwlgen = PWLWaveLUTGenerator(0.001, wv_suffix='_%s' % name) # if sqrt
    pwlgen.put_lutname(name)
    pwlgen.load_fn(fn, 0.0, 10, 0.01)
    #pwlgen.load_fn(fn, 0.0, 5e6, 10) # if sqrt
    pwlgen.generate()
    pwlgen.save_LUT(name)
  #mergeLUT("lut_exp_cos.dat", "lut_exp_sin.dat")

if __name__ == "__main__":
  main()
