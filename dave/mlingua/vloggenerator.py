# Verilog model generator of PWL filter model

import sys
import os
import numpy as np
import scipy.interpolate
import shutil
import subprocess
import string
import random
import time

from empyinterface import EmpyInterface
from pwlbasisfunction import PWLBasisFunctionExpr
from pwlgenerator import PWLWaveLUTGenerator
from txf2tran import Txf2Tran
import filter_template 

class PWLConfigLoader(object):
  ''' Load python configuration file for Verilog model generation '''
  def __init__(self, cfg_file):
    dirname, basename = os.path.split(cfg_file)
    if dirname == '':
      sys.path.append(os.getcwd()) 
    else:
      sys.path.append(dirname)
    cfg = os.path.splitext(basename)[0] # get verification scirpt file name w/o ext
    __import__(cfg) # import the cfg file 
    self.__cfg = sys.modules[cfg] # get cfg module handle
    self.__param = dict([ (k, getattr(self.__cfg, k)) for k in dir(self.__cfg) if not k.startswith('__') ])
    if self.__param['filter_input_datatype'] == 'pwc':
      self.__param['filter_input_datatype'] = 'real'

  def get_param(self):
    return self.__param

class VerilogPWLGenerator(object):
  ''' Read configuration file and generator PWL filter model in Verilog 
    VerilogPWLGenerator('config.py', 'pwl1.v')
  '''
  dirname= os.path.abspath(os.path.join(os.environ['mLINGUA_DIR'], 'pwlgen'))
  vlog_template = filter_template.filter_template
  def __init__(self, cfg_file):
    self.__set_default()
    self.__param.update(PWLConfigLoader(cfg_file).get_param())
    self.__param.update({'response_function': self.__tf2tran()})
    self.response_function_orig = self.__param['response_function']
    self.__create_port()
    self.__process_function_input()
    self.__process_response_function()
    self.__process_etc()
    self.generate(self.__param['module_name'])
  
  def __tf2tran(self):
    num = self.__param['numerator']
    denum = self.__param['denumerator']
    intype = self.__param['filter_input_datatype']
    tt = Txf2Tran(num, denum, intype)
    return tt.get_yt()

  def __set_default(self):
    ''' set some default '''
    self.__param = {
                    'tmax' : 1,
                    'filter_order' : 1,
                    'is_LUT' : False
                   }

  def __process_response_function(self):
    template = '''
function real fn_{order}_derivative_{module};
input real t; 
input {filter_input_datatype} si; 
input real xi0, xi1, yo0, yo1 {so_derivative} {fn_input};
begin
  return {response};
end
endfunction
    '''
    wf = PWLBasisFunctionExpr(self.__param['response_function'])
    f, f2 = wf.get_fn_str()
    system_order = self.__param['filter_order']
    self.__param.update({
                        'response_function' : self.__fix_fn_expr(f),
                        'response_function_f2max' : self.__fix_fn_expr(f2)
                       })
    so_derivative = ', ' + ', '.join(['so%d' %x for x in range(1, system_order)]) if system_order>1 else ''
    deriv_str = ''
    deriv_str = deriv_str + template.format(order=1, module=self.__param['module_name'],
                                            filter_input_datatype=self.__param['filter_input_datatype'],
                                            fn_input=self.__param['fn_input'],
                                            so_derivative='',
                                            response = self.__fix_fn_expr(str(wf.get_derivative_str(1))))
    self.__param.update({'derivative_functions' : deriv_str,
                         'so_derivative' : so_derivative
                       })

  def __fix_fn_expr(self, expr):
    return expr.replace('si_a', 'si.a').replace('si_b', 'si.b')
    
  def __create_port(self):
    port = ['input %s %s, ' % (v, k) for k, v in self.__param['other_input'].items()]
    port = port + ['input %s si, output %s so' % (self.__param['filter_input_datatype'], self.__param['filter_output_datatype'])]
    self.__param.update({'port_definition' : ''.join(port)})

  def __process_function_input(self):
    other_input = self.__param['other_input']
    self.__param.update({ 'fn_input' : ', ' + ', '.join(other_input.keys()) if len(other_input.keys())>0 else ''})
    other_input_s = ['%s' % (k if v=='real' else k+'_s') for k, v in other_input.items()]
    self.__param.update({ 'fn_input_s' : ', ' + ', '.join(other_input_s) if len(other_input.keys())>0 else ''})

  def __process_etc(self):
    in_dtype = self.__param['filter_input_datatype']
    tunit = self.__param['timeunit']
    self.__param.update({ 'si_sensitivity' : 'si' if in_dtype == 'real' else '`pwl_event(si)',
                          'timeunit_num' : from_engr(tunit.rstrip('s')),
                          'K_etol' : np.sqrt(8.0*abs(self.__param['etol']))
                       })
    
  def generate(self, basename):
    dev_mode = True
    p = self.__param
    if p['is_LUT']==True:
      PWLLUTBuilder(self.response_function_orig,
                  p['etol'],
                  p['tmax'],
                  p['grid'],
                  p['user_param'],
                  p['module_name']
                 )
    def generate_random_str(prefix,N):
      ''' generate random string with a length of N(>1, including len(prefix)), it starts with X '''
      char_set = string.ascii_uppercase + string.digits
      return prefix+''.join(random.sample(char_set,N-1))

    try:
      tempfile = '/tmp/'+generate_random_str('_',10)
      EmpyInterface(tempfile)(self.vlog_template, self.__param)
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

class PWLLUTBuilder(object):
  ''' Build PWL LUT from response function '''
  def __init__(self, response_function, reltol, tmax, grid, param, suffix=''):
    self.rf = response_function
    self.etol = reltol
    self.tmax = tmax
    self.grid = grid
    self.param = param  # user param in config.py
    self.run(suffix)

  def run(self, suffix):
    self._validrf = filter(lambda x: x[0] in ['exp', 't*exp', 'exp*cos', 'cos'], self.rf)
    self.pwl = []
    for f in self._validrf:
      self.pwl.append(PWLWaveLUTGenerator(self.etol/len(self._validrf), ''))
      name = 'lut_'+f[0].replace('*','_')+'_'+suffix
      self.pwl[-1].put_lutname(name)
      if f[0] in ['exp', 't*exp', 'cos']:
        ff=[(f[0], 1.0, self.param[f[2]])]
      self.pwl[-1].load_fn(ff, 0.0, self.tmax, self.grid*self.param[f[2]])
      self.pwl[-1].generate(validate=False)

    # Augment time from all basis function terms
    xs = []
    for p in self.pwl:
      xs = xs + p.get_xlut()
    xall = sorted(list(set(xs)))
    # build LUT for new time
    for p in self.pwl:
      xs = p.get_xlut()
      ys = p.get_ylut()
      interp = scipy.interpolate.interp1d(xs,ys)
      ynew = interp(xall)
      p.generate_LUT(xall, ynew) 

def from_engr (value):
  ''' convert engineering notation to a floating number '''
  suffix = {'a':1e-18,'f':1e-15,'p':1e-12,'n':1e-9,'u':1e-6,'m':1e-3, \
              'k':1e3,'M':1e6,'G':1e9,'T':1e12,'P':1e15,'E':1e18}
  try:
    return float(value[0:-1]) * suffix[value[-1]]
  except:
    pass

def main():
  #import doctest
  #doctest.testmod()
  VerilogPWLGenerator('config.py')

if __name__ == "__main__":
  main()
