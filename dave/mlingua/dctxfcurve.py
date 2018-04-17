#!/usr/bin/env python
import numpy as np
import os
import scipy.interpolate
import matplotlib.pylab as plt
import string
import random
import shutil
import subprocess

from empyinterface import EmpyInterface
import txf_template



# This will use a very naive search to reduce the number of data points, since there is no rush for generating a Verilog file; it is not a run-time simulator.

class TxfCurveGeneratorNDim(object):
  _template = os.path.abspath(os.path.join(os.environ['mLINGUA_INST_DIR'], 'pwlgen/resource', 'txfm.empy'))

  def __init__(self, param):
    dim = param['no_input']
    for i in range(dim):
      vars()['x%d'%i] = param['x%d'%i]
    y = param['y']


class TxfCurveGenerator(object):
  vlog_template = txf_template.txf_template

  def __init__(self, param):
    x = param['x']
    y = param['y']
    use_userdata = param['use_userdata'] if 'use_userdata' in param.keys() else False

  def __init__(self, param):
    x = param['x']
    y = param['y']
    use_userdata = param['use_userdata'] if 'use_userdata' in param.keys() else False
    
    self._check_sanity(x, y)
    if use_userdata:
      rx = x
      ry = y
    else:
      rx, ry = self._reduce_data(x, y, param['etol'])
    mname = param['module_name']
    print '=== Generating "%s" ===' % (mname+'.v')
    print '# of original data: %d' % len(x)
    if use_userdata:
      print 'No data reduction is selected'
    else:
      print '# of reduced data: %d' % len(rx)

    lutx, luty = self._generate_lut(rx, ry)
    self._generate(dict(param, **{'lutx': lutx, 'luty': luty, 'ly': ry}))
    self._validate(x, y, rx, ry, mname) # visual check

  def _check_sanity(self, x, y):
    ''' check user data is ok '''
    assert len(x)==len(y), "Number of points for x & y should be the same"

  def _reduce_data(self, x, y, etol):
    ''' reduce data points which meet etol requirement '''
    rx = [x[0]]
    ry = [y[0]]
    i = 1
    while i < len(x):
      if (i%1000==1):
        print '%d/%d' %(i,len(x))
      for j in range(i+1, len(x)):
        slope = (y[j]-ry[-1])/(x[j]-rx[-1])
        fn = lambda x: slope*(x-rx[-1])+ry[-1]
        maxerr = max([abs(fn(x[k])-y[k]) for k in range(i, j)])
        if maxerr > etol:
          assert j > i+0, 'Data is too coarse to meet etol(%e) requirement' % etol
          rx.append(x[j-1])
          ry.append(y[j-1])
          i = j-1
          break
        if j==len(x)-1:
          rx.append(x[j])
          ry.append(y[j])
          i = len(x)
          break
    return rx, ry

  def _generate_lut(self, rx, ry):
    ''' generate gain table '''
    luty = [(ry[i+1]-ry[i])/(rx[i+1]-rx[i]) for i in range(len(rx)-1)]
    return rx[:-1], luty
      
  def _generate(self, param):
    ''' generate Verilog '''
    dev_mode = True
    basename = param['module_name']
    def generate_random_str(prefix,N):
      ''' generate random string with a length of N(>1, including len(prefix)), it starts with X '''
      char_set = string.ascii_uppercase + string.digits
      return prefix+''.join(random.sample(char_set,N-1))

    try:
      tempfile = '/tmp/'+generate_random_str('_',10)
      EmpyInterface(tempfile)(self.vlog_template, param)
      if dev_mode:
        shutil.copyfile(tempfile, basename+'.v')
        os.remove(tempfile)
      else:
        p=subprocess.Popen('vcs '+tempfile+' +protect', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err  = p.communicate()
        shutil.copyfile(tempfile+'p', basename+'.vp')
        os.remove(tempfile)
        os.remove(tempfile+'p')

    except KeyboardInterrupt:
      try:
        os.remove(tempfile)
      except:
        pass
    except:
      os.remove(tempfile)

  def _validate(self, x, y, rx, ry, module_name):
    ''' validate results '''
    fn = scipy.interpolate.interp1d(rx, ry)
    ny = fn(x)
    err = abs(ny-y)
    maxerr = max(err)

    plt.figure()
    plt.scatter(x, y, marker='x', color='r', label='User')
    plt.plot(rx, ry, 'bo-', label='Reduced')
    plt.xlabel('x')
    plt.ylabel('y')
    plt.legend(loc=2)
    plt.title('User data vs Reduced data')
    plt.savefig('%s_data.png' % module_name)
    plt.close()

    plt.figure()
    plt.scatter(x, err, marker='x', color='b')
    plt.xlabel('x')
    plt.ylabel('Absolute Error')
    plt.title('Error in PWL approximation (max=%e)' % maxerr)
    plt.savefig('%s_err.png' % module_name)
    plt.close()

