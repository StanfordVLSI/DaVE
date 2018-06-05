# test vector generation module

__doc__ = """
Test vector generation block for mProbo. We use three sampling schemes:
  - Orthogonal arrays with the strength of two in a OA table;
  - LatinHyperCube sampling if proper OA doesn't exist;
  - Random sampling.
"""
import numpy as np
import os
from BitVector import BitVector
import copy
from itertools import product, ifilter, ifilterfalse
import pandas as pd
import random
from dave.common.davelogger import DaVELogger
from dave.common.misc import print_section, all_therm, dec2bin, bin2dec, bin2thermdec, flatten_list, assert_file, isNone
from environ import EnvOaTable, EnvFileLoc, EnvTestcfgPort
from port import get_singlebit_name
import oatable
import pyDOE
import dave.mprobo.mchkmsg as mcode

#------------------------------------------------------
class LatinHyperCube(object):
  ''' Perform Latin Hyper Cube sampling using pyDOE 
      and scale the generated samples by depth
      (i.e. number of levels) to make all integers
        - n_var : number of variables
        - depth : Depth applied to all variables
        - sample : number of samples to be generated
  '''
  def __call__(self, n_var, depth, sample):
    lhs_samples = self._get_lhs(n_var, sample)
    return self._scale(lhs_samples, depth)

  def _scale(self, vector, depth): # scale vector by depth 
    return np.ceil(depth*vector)

  def _get_lhs(self, n_var, sample): # get samples using LHS
    return pyDOE.lhs(n_var, sample)
    
#------------------------------------------------------
class OrthogonalArray(object):
  ''' NOT YET IMPLEMENTED for generic OA '''
  def __init__(self, logger_id='logger_id'):
    self._logger = DaVELogger.get_logger('%s.%s.%s' % (logger_id, __name__, self.__class__.__name__))

#------------------------------------------------------
class OrthogonalArrayTable(OrthogonalArray):
  ''' Generates orthogonal array samples from pre-defined tables.  '''
  
  TABLENAME_FORMAT = 'OA_V%d_L%d_tbl'

  def __init__(self, logger_id='logger_id'):
    OrthogonalArray.__init__(self, logger_id)

  @property
  def max_nvar(self): # max # of vars supported by mProbo
    return EnvOaTable().max_oa_var

  @property
  def max_depth(self): # max # oa depth supported by mProbo
    ''' TODO: somehow self._max_oa_depth returns a string, os int() is used '''
    return int(EnvOaTable().max_oa_depth)

  @property
  def vector(self): # generated vector
    return self._vector

  @property
  def length(self): # length of generated vector
    return self._length

  @property
  def depth(self): # depth of generated vector
    return self._depth

  def generate(self, n_var, depth): 
    ''' generate OA+random vector for given # of vars, OA depth '''
    self._depth = depth
    self._vector = self._read_oatable(n_var, depth)
    self._length = self._vector.shape[0] if not isNone(self._vector) else 0
    self._logger.debug(mcode.DEBUG_019 %(self.depth, self.length))

  def test(self, n_var, depth): # test if OA exists for given # of vars, OA depth
    return self._read_oatable(n_var, depth)

  def get_oatable(self, n_var, depth): # return oa table StringIO if exists
    try:
      return getattr(oatable, self.TABLENAME_FORMAT %(n_var, depth))
    except:
      return None

  def _read_oatable(self, n_var, depth): # return OA vector if exists
    table = self.get_oatable(n_var, depth)
    if table:
      strio = copy.deepcopy(table) # copy since StringIO is read more than once
      vector_array = np.loadtxt(strio, dtype=int)-1 # -1 because table starts from 1
      return vector_array.reshape(vector_array.shape[0], n_var)
    else:
      return None



#------------------------------------------------------
class TestVectorGenerator(object):
  def __init__(self, ph, test_cfg, logger_id='logger_id'):
    ''' 
      ph: Port Handler class instance
      test_cfg: TestConfig class instance
    '''

    self._logger_id = logger_id
    self._logger = DaVELogger.get_logger('%s.%s.%s' % (logger_id, __name__, self.__class__.__name__))
    self.option = { # read vector generation options from test config
                   #'oa_depth': test_cfg.get_option_regression_oa_depth(),
                   'oa_depth': int(test_cfg.get_option_regression_min_oa_depth()),
                   'min_oa_depth': int(test_cfg.get_option_regression_min_oa_depth()),
                   'max_sample': int(test_cfg.get_option_regression_max_sample()),
                   'en_interact': test_cfg.get_option_regression_en_interact(),
                   'order': int(test_cfg.get_option_regression_order()) }

    map(self._logger.info, print_section(mcode.INFO_036, 2)) # print section header

    # all possible linear circuit configurations by DigitalModePort
    self._generate_digital_vector(ph.get_digital_input()) 

    # process analog ports
    self._ph = ph
    if self._ph.get_by_name('dummy_analoginput') != None:
      self.option['max_sample'] = 1
    self._count_port(ph) # count number of (pinned, unpinned) ports

    self._update_analog_grid()

    analog_raw_vector = self._generate_analog_raw_vector()

    # analog test vectors by scaling raw vector to real range
    self._a_vector = self._map_analog_vector(analog_raw_vector)

    self._logger.info(mcode.INFO_045 % self.get_analog_vector_length())

  def _count_port(self, ph): # separate unpinned, pinned analog ports and count them
    self.unpin_analog = ph.get_unpinned(ph.get_pure_analog_input())
    self.pin_analog = ph.get_pinned(ph.get_pure_analog_input())
    self.unpin_quantized = ph.get_unpinned(ph.get_quantized_analog())
    self.pin_quantized = ph.get_pinned(ph.get_quantized_analog())

    self.no_unpin_analog = len(self.unpin_analog) + len(self.unpin_quantized)
    self.no_pin_analog = len(self.pin_analog) + len(self.pin_quantized)


  def _update_analog_grid(self):
    ''' calculate required analog grid for given max_sample option 
      max_sample: maximum number of vectors set by user
      Na : # of analog+quantized input ports
      TODO: Decide whether max_bitw affects analog grid or not
    '''
    # adjust grid to (self.max_bitw + 1) if that is smaller than 3 
    self.max_bitw = self._get_max_bitwidth(self.unpin_quantized)
    if self.option['oa_depth'] <= self.max_bitw:
      self.option.update({'oa_depth': self.max_bitw + 1})
      self._logger.info(mcode.INFO_039 % self.option['oa_depth'])

    self._logger.info(mcode.INFO_036_1 % self.option['max_sample'])

    if isNone(self._ph.get_by_name('dummy_analoginput')):
      # Adjust max_sample to 2x no of all the linear terms
      #max_sample_internal = self.get_unit_no_testvector() + min(self.get_unit_no_testvector(), 2*self.get_unit_no_testvector_otf())
      max_sample_internal = max(8,2*self.get_unit_no_testvector())
      if self.option['max_sample'] < max_sample_internal:
        self.option['max_sample'] = max_sample_internal
        self._logger.info(mcode.INFO_036_1_1 % max_sample_internal)
  
      Na = self.no_unpin_analog
      Ng = self.option['oa_depth']
      oa = OrthogonalArrayTable(self._logger_id) 
      if not isNone(oa.get_oatable(Na, Ng)): # caculate # of grid, if oa exists
        max_sample = self.option['max_sample']
        oa_vec0 = oa.test(Na, Ng)
        if len(oa_vec0) <= max_sample:
          max_depth = oa.max_depth+1 if Na > 1 else 100
          for i in range (self.option['oa_depth'], max_depth):
            oa_vec = oa.test(Na, i)
            if isNone(oa_vec):
              Ng = i - 1
              break
            elif len(oa_vec) >= max_sample:
              Ng = i
              break
          #Ng = i
          oa_vec0 = oa.test(Na, Ng)
          if len(oa_vec0) > max_sample:
            self.option['max_sample'] = len(oa_vec0)
        else:
          self.option['max_sample'] = len(oa_vec0)
        self.option['oa_depth'] = Ng
        self._logger.info(mcode.INFO_036_2 % self.option['max_sample'])
        self._logger.info(mcode.INFO_036_3 % self.option['oa_depth'])
        self._logger.info(mcode.INFO_036_4 % (Ng, len(oa.test(Na, Ng))))

  def get_unit_no_testvector_otf(self): # unit number of test vectors for on-the-fly check
    n = len(self.unpin_analog)*self.option['order']
    for p in self.unpin_quantized:
      n += p.bit_width
    return max(4,n)

  def get_unit_no_testvector(self): # N+1 where N is the number of linear terms
    n = len(self.unpin_analog) # number of analog inputs (exclude quantized analog)
    nh = n*(self.option['order']-1) # number of higher-order terms for analog inputs
    nqa = 0
    nqa_int = 0
    for p in self.unpin_quantized:
      nqa += p.bit_width    # total bit width of quantized analog
    if len(self.unpin_quantized) > 1: # if # of quantized analog inputs > 1
      nqa_int = 1
      for p in self.unpin_quantized:
        nqa_int *= p.bit_width # interaction between quantized analog bits
    n_tot = 1 + n + nh + nqa # linear terms
    if self.option['en_interact']: # take into account for interaction terms
      return n_tot + n*(n-1)/2 + nqa*n + nqa_int # linear terms + 1st interaction terms
    else:
      return n_tot

  def dump_test_vector(self, ph, workdir): # dump generated test vectors to a csv file 
    csv_d = os.path.join(workdir, EnvFileLoc().csv_vector_prefix+'_digital.csv') # for digital 
    csv_a = os.path.join(workdir, EnvFileLoc().csv_vector_prefix+'_analog.csv')  # for analog

    d_vector = dict([ (k, self.conv_tobin(ph, k, v)) for k, v in self._d_vector.items() ])
    a_vector = dict([ (k, self.conv_tobin(ph, k, v)) for k, v in self._a_vector.items() ])

    df_d = pd.DataFrame(d_vector)
    df_a = pd.DataFrame(a_vector)

    map(self._logger.info, print_section(mcode.INFO_040, 3))
    self._logger.info(df_d)
    self._logger.debug('\n' + mcode.DEBUG_004 % os.path.relpath(csv_d))
    df_d.to_csv(csv_d)

    map(self._logger.info, print_section(mcode.INFO_041, 3))
    self._logger.info(df_a)
    self._logger.debug('\n' + mcode.DEBUG_005 % os.path.relpath(csv_a))
    df_a.to_csv(csv_a)

  def load_test_vector(self, ph, workdir): # load dumped test vector 
    self._logger.info('\n' + mcode.INFO_042)

    csv_d = os.path.join(workdir, EnvFileLoc().csv_vector_prefix+'_digital.csv') # for digital
    csv_a = os.path.join(workdir, EnvFileLoc().csv_vector_prefix+'_analog.csv')  # for analog

    assert_file(csv_d)
    assert_file(csv_a)
    self._logger.debug(' - %s' % csv_d)
    self._logger.debug(' - %s' % csv_a)

    df = pd.read_csv(csv_a)
    self._a_vector = dict([ (k, self.conv_frombin(ph, k, df[k])) for k in df.keys() if k in flatten_list(ph.get_name().values()) ])

    df = pd.read_csv(csv_d)
    self._d_vector = dict([ (k, self.conv_frombin(ph, k, df[k])) for k in df.keys() if k in flatten_list(ph.get_name().values()) ])
    
  def get_analog_vector_length(self): # get # of analog vectors 
    return self._get_vector_length(self._a_vector)

  def get_digital_vector_length(self): # get # of digital vectors 
    return self._get_vector_length(self._d_vector)
    
  def get_all_digital_vector(self): # return all digital mode vectors 
    return [self.get_digital_vector(n) for n in range(self.get_digital_vector_length())]

  def get_all_analog_vector(self): # return all analog vectors 
    return [self.get_analog_vector(n) for n in range(self.get_analog_vector_length())]

  def get_analog_vector(self, index): # return analog_vector[index] 
    return self._get_vector(index, True)

  def get_digital_vector(self, index): # return digital_vector[index] 
    return self._get_vector(index, False)

  @classmethod
  def conv_tobin(cls, ph, pname, pvalue):
    ''' Convert a number to a binary string with prefix "b" 
        ph: PortHandler obj
        pname: port name
        pvalue: list of test vector for pname
    '''
    if pname in [v.name for v in ph.get_digital()]:
      if type(pvalue) in [np.int64, np.float64, int, float]: # I hate this
        return 'b'+str(dec2bin(pvalue, ph.get_by_name(pname).bit_width))
      else:
        return ['b'+str(dec2bin(v, ph.get_by_name(pname).bit_width)) for v in pvalue]  # convert to bin
    else:
      return pvalue # dont convert

  @classmethod
  def conv_frombin(cls, ph, pname, pvalue):
    ''' Convert a binary string with prefix "b" to a number
        ph: port handler class instance
        pname: port name
        pvalue: value to convert
    '''
    if pname in [v.name for v in ph.get_digital()]:
      if type(pvalue) == str: # I hate this
        return bin2dec(pvalue.lstrip('b'))
      else:
        return [bin2dec(v.lstrip('b')) for v in pvalue]  # convert from bin
    else:
      return pvalue.values # dont convert

  @classmethod
  def encode_quantized_port(cls, vector, ph):
    ''' Encode quantized analog vector for doing linear regression 
        #TODO: only thermometer/binary code are supported now
    '''
    vector_out = copy.deepcopy(vector)
    for p in vector.keys():
      if p in ph.get_quantized_port_name():
        v = ph.get_by_name(p)
        if v.encode == EnvTestcfgPort().thermometer:
          vector_out[p] = map(lambda k: bin2thermdec(dec2bin(k, v.bit_width)), vector_out[p])
    return vector_out

  @classmethod
  def remove_pinned_input(cls, vector, ph): # remove test vectors of pinned input ports 
    return dict([ (k, v) for k, v in vector.items() if not ph.get_by_name(k).is_pinned])

  @classmethod
  def expand_quantized_vector(cls, vector, ph):
    ''' if an input is a quantized analog input, expand bits '''
    vector_new = copy.deepcopy(vector)
    qa = ph.get_unpinned_quantized_port_name()

    for p in filter(lambda x, qa=qa: x in qa, vector_new.keys()):
      vector_p = vector_new[p]
      del vector_new[p]
      bitw = ph.get_by_name(p).bit_width
      vector_new.update( dict([ (get_singlebit_name(p, i), []) for i in range(bitw) ]) )
      for i in range(len(vector_p)):
        for j in range(bitw):
          vector_new[get_singlebit_name(p, j)].append(int(dec2bin(vector_p[i], bitw)[bitw-j-1]))
    return vector_new

  @classmethod
  def get_effective_vector(cls, vector, ph): 
    ''' return (quantized) analog vector for linear regression '''
    _vector = cls.remove_pinned_input(vector, ph) 
    return cls.expand_quantized_vector(_vector, ph) 

  def _get_vector_length(self, test_vector): # return the vector length 
    return len(test_vector[test_vector.keys()[0]])

  def _get_vector(self, index, analog=True): # get a vector with index 
    vectors = self._a_vector if analog else self._d_vector
    assert index < self._get_vector_length(vectors), mcode.ERR_007
    return dict([(p,v[index]) for p,v in vectors.items()])

  def _get_max_bitwidth(self, qport):
    ''' return the max bit-width among digtal inputs (for quantized port) '''
    return max(map(lambda x: x.bit_width, qport)) if len(qport) > 0 else 0

  def _generate_analog_raw_vector(self):
    ''' generate analog raw vector 
        TODO: 
          - yet allow duplicate samples in LHS case
          - Assume that it is unlikely that LHS depth 
            need to be adjusted for large max_sample value
    '''
    max_sample = self.option['max_sample']
    Ng = self.option['oa_depth']
    Na = self.no_unpin_analog
    oa = OrthogonalArrayTable(self._logger_id)
    oa.generate(Na, Ng) # generating orthogonal array 
    vector = oa.vector

    if Na > 0:
      if isNone(vector): # if do full LHS, oa unavailable,
        self._logger.warn(mcode.WARN_011 % (Na, Ng) )
        if Na == 1: # only 1 var
          self.option['oa_depth'] = max_sample
        else:
          self.option['oa_depth'] = np.log(max_sample)/np.log(Na)
        Ng = self.option['oa_depth']
        n_remain = max_sample 
      else: 
        n_remain = max_sample - vector.shape[0]
  
      if n_remain > 0: # add LHS vectors to existing oa vector
        lhs = LatinHyperCube()(Na, Ng-1, n_remain)
        if vector:
          vector = np.vstack(( vector, lhs))
        else:
          vector = lhs
        self._logger.warn(mcode.WARN_013 % n_remain)
      return np.hstack((vector, np.ones((max_sample, self.no_pin_analog)))) if self.no_pin_analog > 0 else vector # add columns for pinned inputs

  def _generate_digital_vector(self, dport):
    ''' return all possible digital modes from DigitalModePort information.  '''
    order   = [p.name for p in dport]
    allowed = [tuple(p.allowed) for p in dport]
    vector_product = zip(*list(product(*allowed))) # cross product and transpose
    self._d_vector = dict([(k,list(vector_product[i])) for i, k in enumerate(order)])

  def _map_analog_vector(self, raw_vector): # scale raw vector to real analog range
    vector = dict()
    idx_os = 0 # index offset
    for idx,p in enumerate(self.unpin_analog): # pure analog 
      raw_ptp = np.ptp(raw_vector[:,idx+idx_os]) # raw vector range
      if raw_ptp != 0.0:
        vector[p.name] = raw_vector[:,idx+idx_os]/float(raw_ptp)*p.ptp + p.lb
      else: 
        vector[p.name] = raw_vector[:,idx+idx_os]/1.0 + p.lb
    idx_os += len(self.unpin_analog)
    for idx,p in enumerate(self.unpin_quantized): # quantized analog 
      vector[p.name] = self._map_quantized_vector(p,raw_vector[:,idx+idx_os])
    idx_os += len(self.unpin_quantized)
    for idx,p in enumerate(self.pin_analog): # pinned analog
      vector[p.name] = raw_vector[:,idx+idx_os]*(p.pinned_value)
    idx_os += len(self.pin_analog)
    for idx,p in enumerate(self.pin_quantized): # pinned quantized analog
      vector[p.name] = raw_vector[:,idx+idx_os]*(p.pinned_value)
    return vector

  def _map_quantized_vector(self, port, raw_vector):
    ''' map raw quantized vector to real vector with these rules:
          - each bit should at least toggle once 
          - generated vector should be in allowed code
    '''
    vlen = len(raw_vector)
    allowed = np.array(port.allowed)
    bitw = port.bit_width
    base_vector = list(all_therm(bitw)) # toggle each bit once
    self._logger.debug(mcode.DEBUG_006 % str(base_vector))

    vector = np.array(filter(lambda x: x in allowed, base_vector)) # allowed base vector
    allowed_ex_vector = list(set(allowed)-set(vector)) # allowed except "vector"

    # find which bits are not toggling and add one among allowed codes
    vector_bin = [dec2bin(v, bitw) for v in vector] # vector in binary
    for i in range(bitw):
      bitvals = list(set([v[i] for v in vector_bin]))
      if len(bitvals) != 2: # not toggled
        for v in allowed_ex_vector: # find one among allowed code
          if dec2bin(v, bitw)[i] != bitvals[0]:
            np.append(vector, v)
            break
        
    # TODO: report which bits are not toggling in the end

    # add random vector, if vector length is stil less than that of raw vector
    n_remain = vlen-len(vector)
    if n_remain > 0:
      # modulo by len(allowed) because n_remain could be larger than size of allowed
      random_idx = np.array(random.sample(range(n_remain), n_remain)) % len(allowed)
      vector = np.concatenate((vector, allowed[random_idx]))
    np.random.shuffle(vector)
    return vector

#------------------------------------------------------
def generate_random_vector(n_var, depth):
  ''' Generate random vectors with
        - number of vector set: depth
        - number of variable: n_var 
      Return 2D array (row: list of vectors, col: variables)
  '''
  vector = np.array( [np.random.shuffle(np.arange(depth)) for i in range(n_var)] )
  vector = np.transpose(vector.reshape(n_var, depth))
  return vector.reshape(depth, n_var)

def generate_additional_random_vector(n_var, depth, n_sample):
  vector = np.array( [np.random.random_integers(0, depth-1, n_sample) for i in range(n_var)] )
  vector = np.transpose(vector.reshape(n_var,n_sample))
  return vector.reshape(n_sample, n_var)

def scale_vector(vector, depth): # scale vector by depth/max(vector) 
  return np.ceil(depth/max(vector)*vector)
