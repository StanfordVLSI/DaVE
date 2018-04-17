# 
__doc__ = """
Defines miscellaneous functions
"""

import numpy as np
from configobj import ConfigObj
import copy
import os
import sys
import inspect
import re
import string
import random
import yaml
import datetime
from collections import OrderedDict

# FILE ------------------------------------------

def assert_file(filename, strict=False, logger=None):
  ''' assert if file exists '''
  if strict:
    assert os.path.exists(filename), 'No %s file exists' % filename
  else: # display warning to logger
    if not os.path.exists(filename) and logger:
      logger.info('No %s file exists' % filename)

def get_abspath(filename, do_assert=True, logger=None):
  ''' return absolute path with possible assertion '''
  val = os.path.abspath(os.path.expandvars(os.path.expanduser(filename)))
  assert_file(val, do_assert, logger)
  return val

def make_dir(dirname, logger=None, force=False):
  ''' 
  Make a directory. Return True if it is created 
  If force is True and the directory already exists, this will force to create the directory after renaming the existing one to a directory with a random suffix.
  '''
  if not os.path.exists(dirname):
    os.system('mkdir -p %s' % dirname)
    if logger: logger.debug('A directory %s is created.' % dirname)
    return True
  else:
    if logger: logger.debug('Directory %s already exists.' % dirname)
    if force:
      old_dirname = dirname + generate_random_str('_old_', 5)
      os.rename(dirname, old_dirname)
      os.system('mkdir -p %s' % dirname)
      if logger:
        logger.debug('The existing directory is renamed to %s.' % old_dirname)
        logger.debug('A directory %s is created.' % dirname)
      return True
    return False

def split_filename(filename):
  ''' For a given filename,
  Return a flag if it exists, directory name, and base filename
  '''
  assert_file(filename)
  (dirname,basename) = os.path.split(os.path.abspath(filename))
  return os.path.exists(filename), dirname, basename

def get_dirname(filename):
  ''' get directory name only '''
  return split_filename(filename)[1]

def get_basename(filename):
  ''' get basename only '''
  return split_filename(filename)[2]

def rmfile(filename):
  ''' delete a file after checking it is a file '''
  if os.path.isfile(filename):
    os.remove(filename)


# Binary Vector ------------------------------------------

def dec2bin(value, bw):
  ''' convert a decimal number(value) to a binary string w/ given bit width(bw) '''
  return "".join(str((int(value)>>i) & 1) for i in range(bw-1,-1,-1))

def bin2dec(binstr):
  ''' Convert binary string to unsigned decimal number '''
  n = len(binstr)-1
  return int(sum(1<<n-i for i,bit in enumerate(binstr) if bit=='1'))

def invbin(binstr):
  ''' invert binary string '''
  return "".join(str(int(i)^1) for i in binstr)

def bin2thermdec(binstr):
  ''' convert binary string(binstr) to thermometer code '''
  n = len(binstr)-1
  return int(sum(1 for i,bit in enumerate(binstr) if bit=='1'))

def all_gray(bitw, invert=False, dtype='int'):
  ''' returns a list of all possible gray codes for given bit width 'bitw' '''
  G=lambda n:n and['0'+x for x in G(n-1)]+['1'+x for x in G(n-1)[::-1]]or['']
  val = G(bitw)
  val = val if not invert else [invbin(v) for v in val]
  return [bin2dec(v) for v in val]

def all_bin(bitw, invert=False, dtype='int'):
  val = [dec2bin(v, bitw) for v in range(2**bitw)]
  val = val if not invert else [invbin(v) for v in val]
  return [bin2dec(v) for v in val]

def all_therm(bitw, invert=False, dtype='int'): # all thermometer codes including 0
  val = ['0'*(bitw-v)+'1'*v for v in range(bitw+1)]
  val = val if not invert else [invbin(v) for v in val]
  return [bin2dec(v) for v in val]

def all_onehot(bitw, include_zero = False, invert=False, dtype='int'):
  val = ['0'*(bitw-v-1)+'1'+'0'*v for v in range(bitw)]
  val = val + ['0'*bitw] if include_zero else val
  val = val if not invert else [invbin(v) for v in val]
  return [bin2dec(v) for v in val]

def therm2bin(thermstr):
  ''' convert thermometer-coded string(binstr) to thermometer code '''
  pass

def therm2dec(thermstr):
  ''' convert thermometer code to decimal value '''
  return bin2dec(therm2bin(thermstr))

def is_thermometer(in_str):
  return in_str == 'thermometer'

def is_gray(in_str):
  return in_str == 'gray'

def is_binary(in_str):
  return in_str == 'binary'


# MISC MATH ---------------------------------------

def strictly_increasing(L):
  return all(x<y for x, y in zip(L, L[1:]))

def strictly_decreasing(L):
  return all(x>y for x, y in zip(L, L[1:]))

def non_increasing(L):
  return all(x>=y for x, y in zip(L, L[1:]))

def non_decreasing(L):
  return all(x<=y for x, y in zip(L, L[1:]))

def all_positive(data):
  ''' returns True if all elements are >0.0 '''
  return all(x>0.0 for x in data)

def all_negative(data):
  ''' returns True if all elements are <0.0 '''
  return all(x<0.0 for x in data)

def all_zero(data):
  ''' returns True if all elements are == 0.0 '''
  return all(x==0.0 for x in data)

def get_absmax(values):
  ''' return a value with the largest absolute value in a list '''
  res_neg = min(values)
  res_pos = max(values)
  return res_pos if abs(res_pos) >= abs(res_neg) else res_neg

def get_snr(signal,noise,mode='power'):
  ''' calculate SNR
      mode: either power or signal 
  '''
  return 10*np.log10(signal/noise) if mode=='power' else 20*np.log10(signal/noise)


# CONVERSION/REPLACEMENT ---------------------------------------

def from_engr (value):
  ''' convert engineering notation to a floating number '''
  suffix = {'a':1e-18,'f':1e-15,'p':1e-12,'n':1e-9,'u':1e-6,'m':1e-3, \
              'k':1e3,'M':1e6,'G':1e9,'T':1e12,'P':1e15,'E':1e18}
  try:
    return float(value[0:-1]) * suffix[value[-1]]
  except:
    return value

def to_engr (value,dtype=float):
  ''' convert a floating number to engineering notation 
      if value < 1e-18 , it returns 0.0
  ''' 
  suffix = [('a',1e-18),('f',1e-15),('p',1e-12),('n',1e-9),('u',1e-6),('m',1e-3), \
             ('',1.0),('k',1e3),('M',1e6),('G',1e9),('T',1e12),('P',1e15),('E',1e18)]
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

def str2num(value,dtype=int):
  if value[0] == 'b': # binary representation
    try:
      x = bin2dec(value[1:])
    except:
      raise ValueError('Binary number representation, %s, is wrong in test configuration file' %value)
  else:
    x = value
  return dtype(float(x)) if dtype==int else dtype(x)

def interpolate_env(value, logger=None):
  ''' 
  Interpolate environment variables if exist. An environment variable is expressed as ${VAR} where VAR is the environment variable name.
  '''
  newvalue = copy.deepcopy(value)
  envs = re.findall('\$\{\w+\}', value)
  for e in envs:
    evar = e.strip("$").strip("{").strip("}")
    try:
      newvalue = newvalue.replace(e, os.environ[evar])
    except:
      msg = "Environement variable (%s) does not exist !!!" % evar
      if logger:
        logger.warn(msg)
      else:
        print msg
  return newvalue

def eval_str(value, dtype=int):
  if type(value) != str:
    return dtype(value)
  if value[0] == 'b': # binary representation
    try:
      return bin2dec(value[1:])
    except:
      raise ValueError('Binary number representation, %s, is wrong in test configuration file' % value)
  else:
    return dtype(float(value)) if dtype==int else dtype(value)


# LIST ---------------------------------------

def flatten_list(l):
  ''' flatten list of lists '''
  return [item for sublist in l for item in sublist]

def merge_list(a,b):
  ''' merge two lists, a and b, while removing any duplication '''
  return a+list(set(b)-set(a))

def force_list(val):
  if not isinstance(val, (list,tuple)):
    val = [val]
  return val

def add_column_list(srcl,dstl,idx=0):
  ''' assuming that dstl is a list of lists, 
      this function adds srcl list to the column of dstl at the left of the assigned index(idx).
  '''     
  lofl = copy.deepcopy(dstl)
  for i, row in enumerate(lofl): 
    row.insert(idx,srcl[i])
  return lofl

def swap_item_list(data,i,j):
  ''' swap i(th) and j(th) item of the list,data '''
  _tmp = data[i]
  data[i] = data[j]
  data[j] = _tmp
  return data


# MISC ---------------------------------------

def printToday():
  today = datetime.date.today()
  return datetime.date.today().strftime('%b-%d-%Y')

def generate_random_str(prefix,N):
  ''' generate random string with a length of N(>1, including len(prefix)), it starts with X '''
  char_set = string.ascii_uppercase + string.digits
  return prefix+''.join(random.sample(char_set,N-1))

def print_section(msg, level=1, leading_newline=True):
  ''' print a message with a section deliminator at the top/bottom of the message '''
  nc = len(msg)
  newline = '\n' if leading_newline else None
  if level==1:
    return filter(None, [newline, '='*nc, msg, '='*nc])
  elif level==2:
    return filter(None, [newline, msg, '*'*nc])
  elif level==3:
    return filter(None, [newline, msg, '-'*nc])
  else:
    return filter(None, [newline, msg, '^'*nc])

def print_end_msg(msg, char='=', leading_newline=True):
  newline = '\n' if leading_newline else None
  return filter(None, [newline, '%s %s %s' %(char, msg, char)])


def get_letter_index(index, upper=False):
  ''' index from 1 '''
  start = ord('A' if upper else 'a')
  return chr(start+index-1)

def scriptinfo():
  '''
  Returns a dictionary with information about the running top level Python
  script:
  ---------------------------------------------------------------------------
  dir:    directory containing script or compiled executable
  name:   name of script or executable
  source: name of source code file
  ---------------------------------------------------------------------------
  "name" and "source" are identical if and only if running interpreted code.
  When running code compiled by py2exe or cx_freeze, "source" contains
  the name of the originating Python script.
  If compiled by PyInstaller, "source" contains no meaningful information.
  '''

  #---------------------------------------------------------------------------
  # scan through call stack for caller information
  #---------------------------------------------------------------------------
  for teil in inspect.stack():
    # skip system calls
    if teil[1].startswith("<"):
      continue
    if teil[1].upper().startswith(sys.exec_prefix.upper()):
      continue
    trc = teil[1]
      
  # trc contains highest level calling script name
  # check if we have been compiled
  if getattr(sys, 'frozen', False):
    scriptdir, scriptname = os.path.split(sys.executable)
    return {"dir": scriptdir,
            "name": scriptname,
            "source": trc}

  # from here on, we are in the interpreted case
  scriptdir, trc = os.path.split(trc)
  # if trc did not contain directory information,
  # the current working directory is what we need
  if not scriptdir:
    scriptdir = os.getcwd()

  scr_dict ={"name": trc,
             "source": trc,
             "dir": scriptdir}
  return scr_dict
    
def featureinfo(check=False):
  ''' return running script '''
  if check:
    scr = scriptinfo()
    return os.path.splitext(scr['source'])[0]
  else:
    return 'mProbo'

def read_yaml(filename,default={}):
  ''' Read yaml '''
  val=OrderedDict()
  val.update(default)
  f = get_abspath(filename)
  val.update(yaml.load(open(f,'r')))
  for k in default.keys():
    if not val[k]: val.update({k:default[k]})
  return val

def print_order(val):
  val = str(val)
  digit1 = val[-1]
  if digit1 == '1' and val != '11':
    return val + 'st'
  elif digit1 == '2' and val != '12':
    return val + 'nd'
  elif digit1 == '3' and val != '13':
    return val + 'rd'
  else:
    return val + 'th'
  
def get_class(klass):
  ''' get a class object from klass str '''
  fields = klass.split('.')
  module = '.'.join(fields[:-1])
  m = __import__(module)
  for comp in fields[1:]:
    m = getattr(m, comp)
  return m

def isNone(val):
  ''' since direct comparison if val==None gives warning '''
  return True if type(val) == type(None) else False
