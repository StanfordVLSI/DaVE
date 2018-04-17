# This is a multi-dimentional LookUp Table generator 
# inputs are pwl waveform
# outputs are real because they assumed to be parameters to other modules

import os
import numpy as np
from empyinterface import EmpyInterface
import string
import random
import sys
import time
import shutil
import subprocess
import lutmd_template
from misc import to_engr

class LookUpTablemD(object):
  ''' build a multi-D LUT from hspice simulation
  '''
  param_keys = ['module_name', 'description', 'x', 'y', 'dig_mode', 'ehdnsxmgorfkdlt']
  def_param = {
    'licensor': 'Byongchan Lim'
    'contact' : 'dave.ikarus@gmail.com'
    'module_name': 'vlog_lut',
    'description': ''' ''',
    'interpolation': False,
    'suppress_ob_message': False
  }

  def __init__(self, param):
    ''' 
    param keys:
      - module_name     : Module name of a generated verilog
      - description     : Description of a model
      - x               : input info.  (see lutgen.py)
      - y               : output info. (see lutgen.py)
      - dig_mode        : digital enumeration order (see lutgen.py)
      - ehdnsxmgorfkdlt : 
    '''

    self.__check_param_keys(param)
    def_param = copy.deepcopy(self.def_param)
    def_param.update(param)
    self._param = def_param
    self._param['gen_time'] = time.ctime()
    self.__ehdnsxmgorfkdlt = self._param['ehdnsxmgorfkdlt']
    self.vlog_template = lutmd_template.lutmd_template

    if self.__ehdnsxmgorfkdlt:
      pass
    else:
      dlrtmvkdldjem()

    self.__check_x()
    self.__display_config()
    self.__gen()
  
 
  def __check_param_keys(self, param):
    ''' check if input param contains all the necessary keys '''
    missed_keys = [k for k in self.param_keys if k not in param]
    if len(missed_keys) > 0:
      print 'There are missing keys (%s) in the configuration file.' % missed_keys
      self.__terminate_w_error()

  def __process_x(self):
    pass

  def __process_y(self):
    pass

  def __display_config(self):
    print '-'*23, ' Configuration summary ', '-'*23
    print '* Verilog module name  : %s' % self._param['module_name']
    print '* Module description   : %s' % self._param['description']
    print '* List of output ports : %s' %( ', '.join(['"%s"' % p for p in sorted(self._param['y'].keys())]))
    print '* List of input ports  : %s' %( ', '.join(['"%s"' % p for p in sorted(self._param['x'].keys())]))
    print '* Input indexing order : %s' %( ''.join(['[%s]'   % p for p in self._param['index_order']]))
    if self._param['interpolation'] == True:
      if self._param['discretized']:
        print '* Input resolution     : %s' %( ', '.join(['%s(%s)' %(p, to_engr(self._param['input_resolution'][i])) for i, p in enumerate(self._param['index_order'])]))
      else:
        print '* Input resolution     : continuous (no "input_resolution" field exists)'
    else:
      print '* No interpolation will be performed'
    print '* Suppress out of bound message in the generated module: %s' % ('Yes' if self._param['suppress_ob_message'] else 'No')
    print '-'*27, ' End of summary ', '-'*27, '\n'

  def __check_x(self):
    ''' check if 
      1. values in x is in ascending order 
      2. keys of "x" matches with items in "index_order"
      3. adjust input resolution if necessary
    '''
    err = False
    res = []
    for k, v in self._param['x'].items():
      _v = list(v)
      if sorted(_v) != _v:
        res.append(k)
    if res != []:
      print '[Error] x values should be in acending order !!!'
      err = True
    if sorted(self._param['x'].keys())!=sorted(self._param['index_order']):
      print '[Error] input ports in "x" is inconsistent with those in "index_order" !!!'
      err = True
    if err:
      self.__terminate_w_error()

    self._param.update({'discretized': 'input_resolution' in self._param})

  def __terminate_w_error(self):
    print 'The program is terminated with error.'
    sys.exit()
    

  def __gen(self):
    if sorted(self._param['index_order']) != sorted(self._param['x'].keys()):
      print '[Error] configuration file error !!!'
      print '[Error] items in "index_order" does not match with keys in "x"'

    dev_mode = True
    basename = self._param['module_name']
    def generate_random_str(prefix,N):
      ''' generate random string with a length of N(>1, including len(prefix)), it starts with X '''
      char_set = string.ascii_uppercase + string.digits
      return prefix+''.join(random.sample(char_set,N-1))

    tempfile = '/tmp/'+generate_random_str('_',10)
    if self.__ehdnsxmgorfkdlt:
      pass
    else:
      dlrtmvkdldjem()
    EmpyInterface(tempfile)(self.vlog_template, self._param)
    if dev_mode:
      dst_file = basename + '.v'
      shutil.copyfile(tempfile, dst_file)
      os.remove(tempfile)
      print '[Info] %s file is generated' % dst_file
    else:
      try:
        dst_file = basename+'.vp'
        p=subprocess.Popen('vcs '+tempfile+' +protect', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err  = p.communicate()
        shutil.copyfile(tempfile+'p', dst_file)
        os.remove(tempfile)
        os.remove(tempfile+'p')
        print '[Info] %s file is generated' %(dst_file)

      except KeyboardInterrupt:
        try:
          os.remove(tempfile)
          self.__terminate_w_error()
        except:
          pass
      except:
        os.remove(tempfile)
        print '[Error] Unknown error ocurred. Check some of those !!!'
        print ' - Check out VCS environment'
        print ' - x & y data are available'
        self.__terminate_w_error()
    if self.__ehdnsxmgorfkdlt:
      pass
    else:
      dlrtmvkdldjem()

def dlrtmvkdldjem():
  sys.exit()

def main():
  filepath = '/home/bclim/proj/modeling/pwlgen/example/ota_w_bias/cktsim'
  param = {
    'module_name' : 'lut2',
    'x' : {
        'ib': np.loadtxt(os.path.join(filepath,'ib.txt')),
        'vcm': np.loadtxt(os.path.join(filepath,'vcm.txt'))
        },
    'y' : {
        'pole': np.loadtxt(os.path.join(filepath,'pole.txt')),
        'gain': np.loadtxt(os.path.join(filepath,'gain.txt'))
        }
  }

  LookUpTablemD(param)

if __name__ == "__main__":
  main()
