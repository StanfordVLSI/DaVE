# Defines some general functions
import numpy as np
from configobj import ConfigObj
import copy
import os
import sys
import re
import string
import random


def assert_file(filename):
  ''' assert if file exists '''
  assert os.path.exists(filename), 'No %s file exists' % filename

def interpolate_env(value, logger=None):
  ''' interpolate environment variable if exist 
      if logger is None, just print out any warnings
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
        self._logger.warn(msg)
      else:
        print msg
  return newvalue

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
  
def get_abspath(filename):
  val = os.path.abspath(os.path.expandvars(os.path.expanduser(filename)))
  assert_file(val)
  return val

def make_dir(dirname, ignore=True, logger=None):
  try:
    os.mkdir(dirname)
  except:
    if ignore:
      if logger != None:
        logger.debug('Directory %s alreayd exists.' % dirname)
    else:
      raise

def get_class(klass):
  ''' get a class object from klass str '''
  fields = klass.split('.')
  module = '.'.join(fields[:-1])
  m = __import__(module)
  for comp in fields[1:]:
    m = getattr(m, comp)
  return m

def get_snr(signal,noise,mode='power'):
  ''' calculate SNR
      mode: either power or signal 
  '''
  return 10*np.log10(signal/noise) if mode=='power' else 20*np.log10(signal/noise)

def all_positive(data):
  ''' returns True if all elements are >0.0 '''
  return all(x>0.0 for x in data)

def all_negative(data):
  ''' returns True if all elements are <0.0 '''
  return all(x<0.0 for x in data)

def all_zero(data):
  ''' returns True if all elements are == 0.0 '''
  return all(x==0.0 for x in data)

def num2str_list(data):
  ''' convert number into string '''
  return ["%s" %x for x in data]

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
  return val if dtype == 'binary' else [bin2dec(v) for v in val]

def all_bin(bitw, invert=False, dtype='int'):
  val = [dec2bin(v, bitw) for v in range(2**bitw)]
  val = val if not invert else [invbin(v) for v in val]
  return val if dtype == 'binary' else [bin2dec(v) for v in val]

def all_therm(bitw, invert=False, dtype='int'):
  val = ['0'*(bitw-v)+'1'*v for v in range(bitw+1)]
  val = val if not invert else [invbin(v) for v in val]
  return val if dtype == 'binary' else np.array([bin2dec(v) for v in val],dtype=int)

def all_onehot(bitw, include_zero = False, invert=False, dtype='int'):
  val = ['0'*(bitw-v-1)+'1'+'0'*v for v in range(bitw)]
  val = val + ['0'*bitw] if include_zero else val
  val = val if not invert else [invbin(v) for v in val]
  return val if dtype == 'binary' else [bin2dec(v) for v in val]

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

def strictly_increasing(L):
  return all(x<y for x, y in zip(L, L[1:]))

def strictly_decreasing(L):
  return all(x>y for x, y in zip(L, L[1:]))

def non_increasing(L):
  return all(x>=y for x, y in zip(L, L[1:]))

def non_decreasing(L):
  return all(x<=y for x, y in zip(L, L[1:]))

def from_engr (value):
  ''' convert engineering notation to a floating number '''
  suffix = {'a':1e-18,'f':1e-15,'p':1e-12,'n':1e-9,'u':1e-6,'m':1e-3, \
              'k':1e3,'M':1e6,'G':1e9,'T':1e12,'P':1e15,'E':1e18}
  try:
    return float(value[0:-1]) * suffix[value[-1]]
  except:
    return value

def from_engr_spice (value):
  ''' convert engineering notation to a floating number '''
  suffix = {'a':1e-18,'f':1e-15,'p':1e-12,'n':1e-9,'u':1e-6,'m':1e-3, \
              'k':1e3,'x':1e6,'g':1e9,'t':1e12,'p':1e15,'e':1e18}
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

def str2bool(value):
  ''' convert a string to boolean '''
  return value.lower() in ['true','yes','t']

def generate_random_str(prefix,N):
  ''' generate random string with a length of N(>1, including len(prefix)), it starts with X '''
  char_set = string.ascii_uppercase + string.digits
  return prefix+''.join(random.sample(char_set,N-1))

def split_filename(filename):
  ''' 
    1. split directory and file name 
    2. also check whether the file exist or not
  '''
  assert_file(filename)
  (dirname,basename) = os.path.split(os.path.abspath(filename))
  return os.path.exists(filename), dirname, basename

def get_basename(filename):
  (dirname,basename) = os.path.split(os.path.abspath(filename))
  return basename

def lower_list(data):
  ''' lower all strings in a list '''
  return map(lambda x: string.lower(x),data)

def flatten_list(l):
  ''' output list out of lists '''
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

def str2num(value,dtype=int):
  if value[0] == 'b': # binary representation
    try:
      x = bin2dec(value[1:])
    except:
      raise ValueError('Binary number representation, %s, is wrong in test configuration file' %value)
  else:
    x = value
  return dtype(float(x)) if dtype==int else dtype(x)

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

def rmfile(filename):
  if os.path.isfile(filename):
    os.remove(filename)

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

def get_largest_in_abs(values):
  ''' return a value with the largest absolute value in a list '''
  res_neg = min(values)
  res_pos = max(values)
  return res_pos if abs(res_pos) >= abs(res_neg) else res_neg

def get_letter_index(index, upper=False):
  ''' index from 1 '''
  start = ord('A' if upper else 'a')
  return chr(start+index-1)
