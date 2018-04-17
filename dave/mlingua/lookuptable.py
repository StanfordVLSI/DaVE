# This is a LookUp Table generator for back annotator

import os
import numpy as np
from dave.common.empyinterface import EmpyInterface
from scipy.interpolate import interp1d

class LookUpTable1D(object):
  ''' build a 1D LUT from hspice simulation
  '''
  #(dirname,basename) = os.path.split(os.path.abspath(__file__))
  dirname= os.path.abspath(os.path.join(os.environ['DAVE_INST_DIR'], 'dave/mlingua'))

  def __init__(self, classname, xs, ys, swapxy=False, paired=True):
    ''' 
      classname: class instance name
      xs: x sample
      ys: y sample
      swapxy: swap xs & ys
      paired: Use different LUT class in Verilog depending on this flag
    '''
    if paired:
      self.vlog_template = os.path.join(self.dirname, 'resource/LUT1DPaired.em')
    else:
      self.vlog_template = os.path.join(self.dirname, 'resource/LUT1D.em')

    self.__xs = ys if swapxy else xs
    self.__ys = xs if swapxy else ys
    
    vlog_file = classname + '.v'
    dat_file  = classname + '.dat'
    dy = np.diff(self.__ys)/np.diff(self.__xs)
    self._param = {'xs': self.__xs,
             'ys': self.__ys,
             'dx': np.append(np.diff(self.__xs), [0.0]),
             'dy': np.append(dy, [0.0]),
             'classname' : classname,
             'size' : len(self.__xs)
            }
    EmpyInterface(vlog_file)(self.vlog_template, self._param)
    np.savetxt(dat_file, (self.__xs, self.__ys))
  
  def read(self):
    #return self.__xs, self.__ys
    return self._param

def mergeLUT(file1, file2, pole=1, dT=1e-2):
  dat1 = np.loadtxt(file1)
  dat2 = np.loadtxt(file2)
  name1 = os.path.splitext(os.path.basename(file1))[0]
  name2 = os.path.splitext(os.path.basename(file2))[0]
  xs1 = dat1[0,:]
  xs2 = dat2[0,:]
  ys1 = dat1[1,:]
  ys2 = dat2[1,:]
  xnew  = np.sort(np.array(list(xs1) + list(set(xs2)-set(xs1))))
  xs = []
  for idx, x in enumerate(xnew[:-1]):
    if (abs(x-xnew[idx+1]) >= pole*dT): xs.append(x)

  xs = np.array(xs)

  f = interp1d(xs1, ys1)
  ys = f(xs)
  LookUpTable1D(name1, xs, ys)
  f = interp1d(xs2, ys2)
  ys = f(xs)
  LookUpTable1D(name2, xs, ys)



def main():
  import doctest
  doctest.testmod()
  
  xs = np.array([])
  dt = 30e-12
  tau = 1.2e-9
  no_tau = 10
  samples = zip(*[(v/tau, 1.0/np.exp(v/tau)) for v in np.arange(0.0, no_tau*tau+dt, dt)])
  xs =  np.array(samples[0])
  ys =  np.array(samples[1])
  LookUpTable1D('lut_exp', xs, ys)


if __name__ == "__main__":
  main()
