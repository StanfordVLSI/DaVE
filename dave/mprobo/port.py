# defines I/O port related stuff
import copy
import numpy as np
from itertools import ifilter, ifilterfalse, chain

from dave.common.misc import flatten_list
from dave.common.davelogger import DaVELogger
from dave.mprobo.environ import EnvPortName, EnvTestcfgPort
import dave.mprobo.mchkmsg as mcode


'''
1. Class Tree
Pin - AnalogPort  - AnalogInputPort - AnalogInputPort (AnalogControlInputPort)
          |       - AnalogOutputPort (PseudoOutputPort)
          |
          AnalogPortConstraint

    - DigitalPort - DigitalInputPort - DigitalModePort
          |                          - QuantizedAnalogPort
          |       - DigitalOutputPort
          DigitalPortConstraint
    - FunctionPort

2. FunctionPort
  If any port is pinned, it becomes a FunctionPort
'''

#-----------------
class Pin(object):
  ''' Pin class defines I/O of a circuit. Note that only "input" and "output" 
  are valid io type of the system. Since Verilog only allows uni-directional
  signal flow, "inout" pin is not allowed.
  '''
  __VALID_PORT_DIR = ['input', 'output']

  def __init__(self, name=None, direction=None, description=''):
    self._name = name
    self._description = description
    self.direction = direction
  
  @property
  def name(self):
    return self._name

  @property
  def description(self):
    return self._description

  @property
  def direction(self):
    return self._direction

  @direction.setter
  def direction(self, val):
    assert val in self.__VALID_PORT_DIR, mcode.ERR_004 % self.name
    self._direction = val
#-----------------

#---------------------
class AnalogPort(Pin):
  ''' AnalogPort is a real-valued signal port '''

  tenv = EnvTestcfgPort()
  __DEF_IN_CONSTR  = { tenv.lower_bound : -np.inf, 
                       tenv.upper_bound : np.inf, 
                       tenv.pinned      : (False,0.0), 
                       tenv.domain      : 'voltage', 
                       tenv.abstol      : 'N/A', 
                       tenv.gaintol     : 'N/A' }
  __DEF_OUT_CONSTR = { tenv.lower_bound : -np.inf, 
                       tenv.upper_bound : np.inf, 
                       tenv.pinned      : (False,0.0), 
                       tenv.domain      : 'voltage', 
                       tenv.abstol      : np.inf, 
                       tenv.gaintol     : 0 }

  def __init__(self, name, direction, description, constraint):
    Pin.__init__(self, name, direction, description)
    # default constraint for input or output
    self.__def_constraint = dict(self.__DEF_IN_CONSTR) if direction=='input' else \
                                dict(self.__DEF_OUT_CONSTR)
    self.__def_constraint.update(constraint)
    self.__def_constraint.pop(self.tenv.domain, None) # remove 'domain' for now
    self.__constraint = self.__def_constraint
    self.update_constraint(self.__def_constraint)

  @property
  def signal(self): # signal type
    return 'analog'

  @property
  def lb(self): # lower bound
    return self.__constraint[self.tenv.lower_bound]

  @property
  def ub(self): # upper bound
    return self.__constraint[self.tenv.upper_bound]

  @property
  def bound(self): # [lower_bound,upper_bound] constraint 
    return self.lb, self.ub

  @property
  def ptp(self): # peak-to-peak 
    return self.ub - self.lb

  @property
  def scale(self): # abs(upper_bound - lower_bound) 
    return abs(self.ub-self.lb)

  @property
  def abstol(self): # absolute tolerance for analog output
    return self.__constraint[self.tenv.abstol]  

  @property
  def gaintol(self): # gain error tolerance in %
    return float(self.__constraint[self.tenv.gaintol])

  @property
  def pinned(self): # pinned ?, pinned value
    ''' get pinned information '''
    return self.__constraint[self.tenv.pinned]

  @property
  def is_pinned(self): # True if it is pinned, else False
    return self.pinned[0]

  @property
  def pinned_value(self): # pinned value if it is pinned, else None
    value = self.pinned[1]
    assert (not self.is_pinned) or self.is_valid(value), mcode.ERR_006 % self.name
    return value if self.is_pinned else None

  def update_constraint(self, constraint): # create constraint checking fuctions 
    self.__constraint.update(constraint) # update constraint

  def is_valid(self, val):  # check if val is within bound
    return val >= self.lb and val <= self.ub

  def get_constraint(self): # get all constraints 
    return self.__constraint
#---------------------
  
#----------------------
class DigitalPort(Pin):
  ''' 
    DigitalPort is a boolean-valued port
  '''
  tenv = EnvTestcfgPort()
  __DEF_CONSTR = { tenv.encode     : '', 
                   tenv.prohibited : [], 
                   tenv.bit_width  : 1, 
                   tenv.pinned     : (False,0) }

  def __init__(self, name, direction, description, constraint):
    Pin.__init__(self, name, direction, description)
    self.__def_constraint = dict(self.__DEF_CONSTR)
    self.__def_constraint.update(constraint)
    self.__constraint = self.__def_constraint
    self.update_constraint(self.__def_constraint)

  @property
  def signal(self): # signal type
    return 'digital'
  
  @property
  def bit_width(self): # get bit_width constraint 
    return self.__constraint[self.tenv.bit_width]

  @property
  def encode(self): # get encoding-style constraint
    return self.__constraint[self.tenv.encode]

  @property
  def prohibited(self): # get prohibited code list 
    return self.__constraint[self.tenv.prohibited]

  @property
  def allowed(self): # return a list of allowed code list in decimal number 
    if self.pinned[0] == True:
      return [self.pinned_value]
    else:
      p = range(2**self.bit_width)
      return filter(lambda x, prohibited=self.prohibited: x not in prohibited, p)

  @property
  def pinned(self): # pinned ?, pinned value
    return self.__constraint[self.tenv.pinned]

  @property
  def is_pinned(self): # True if it is pinned, else False
    ''' get pinned information '''
    return self.pinned[0]

  @property
  def pinned_value(self): # pinned value if it is pinned, else None
    value = self.pinned[1]
    #assert (not self.is_pinned) or self.is_valid(value), mcode.ERR_006 % self.name
    return value if self.is_pinned else None

  def update_constraint(self,constraint): # create constraint checking fuctions 
    self.__constraint.update(constraint)

  def is_valid(self, val):  # check if val is allowed
    return True if (val in self.allowed) and (type(val)==type(0)) else False

  def get_constraint(self): # get all constraint 
    return self.__constraint
#----------------------


#---------------------------------
class AnalogInputPort(AnalogPort):
  def __init__(self, name=None, description='', constraint={}):
    AnalogPort.__init__(self, name, 'input', description, constraint)
    
#----------------------------------
class AnalogOutputPort(AnalogPort):
  def __init__(self, name=None, description='', constraint={}):
    AnalogPort.__init__(self, name, 'output', description, constraint)

#--------------------------------------
class QuantizedAnalogPort(DigitalPort):
  def __init__(self, name=None, description='', constraint={}):
    DigitalPort.__init__(self, name, 'input', description, constraint)

#----------------------------------
class DigitalModePort(DigitalPort):
  def __init__(self, name=None, description='', constraint={}):
    DigitalPort.__init__(self, name, 'input', description, constraint)

#------------------------------------
class DigitalOutputPort(DigitalPort):
  def __init__(self, name=None, description='', constraint={}):
    DigitalPort.__init__(self, name, 'output', description, constraint)



#-------------------------
class PortHandler(object):
  ''' PortHandler class provides methods for ports in a test.
    Vars:
      a. getattr(self, [PCLS_ALIAS.keys()])
        - This dictionary contains all port class aliases (key), where 
          its value contains a dictionary where
            - key: created port name
            - value: created port class instance
  '''
  tenv = EnvPortName()
  tenvtp = EnvTestcfgPort()
  PCLS_ALIAS = { tenv.AnalogInput     : AnalogInputPort, 
                 tenv.AnalogOutput    : AnalogOutputPort,
                 tenv.QuantizedAnalog : QuantizedAnalogPort, 
                 tenv.DigitalMode     : DigitalModePort, 
                 tenv.DigitalOutput   : DigitalOutputPort } # alias for port classes

  def __init__(self, logger_id='logger_id'):
    self._logger = DaVELogger.get_logger('%s.%s.%s' % (logger_id, __name__, self.__class__.__name__))
    self.init_port() # initialize

  def init_port(self):
    ''' Create an empty dictionary where keys are all available port 
    class aliases and values are empty directionaries. '''
    for x in self.PCLS_ALIAS.keys():
      setattr(self, x, {})

  def add_port(self, name, pcls, description, constraint):
    ''' Create a port. It will overwirte if already exists '''
    port_cls = self.PCLS_ALIAS[pcls] # port class
    port = getattr(self, pcls) # get a port dictionary of a port class
    port[name] = port_cls(name, description, constraint) # instantiate a port class

  def del_port(self, name):
    ''' Delete a port if exists. '''
    has_port, port, port_cls, description = self.__has_port(name)
    if has_port == True: del port
    return has_port # True if it's successful

  def copy_port(self, src_name, dst_name, constraint=None):
    ''' Copy a port and update constraint if provided. 
    return True if successful.  '''
    has_port, port, pcls, description = self.__has_port(src_name)
    if has_port == True:
      self.add_port(dst_name, pcls, description, port.get_constraint())
      getattr(self, pcls)[dst_name].update_constraint(constraint)
    return has_port
  
  def add_dummy_digitalmode_port(self):
    ''' Creates a dummy digital mode port in case no digital mode port exists. '''
    if self.get_no_of_digitalmode() == 0: # if digital mode doesn't exist
      self.add_port('dummy_digitalmode', self.tenv.DigitalMode, 'Dummy digital mode',
                    {self.tenvtp.pinned : (True, 0), 
                     self.tenvtp.bit_width : 1,
                     self.tenvtp.encode: self.tenvtp.binary })
    else:
      self._logger.warn(mcode.WARN_023)

  def get_analog_input(self):
    ''' returns a list of analog & quantized_analog port object '''
    return self.get_pure_analog_input()+self.get_quantized_analog()

  def get_pure_analog_input(self):
    ''' returns a list of analog port object '''
    p = self.get_by_type(self.tenv.AnalogInput).values()
    return list(chain(*[p]))

  def get_quantized_analog(self):
    ''' returns a list of analog port object '''
    p = self.get_by_type(self.tenv.QuantizedAnalog).values()
    return list(chain(*[p]))

  def get_digital_input(self):
    ''' returns a list of digital mode object port '''
    return list(chain(*[self.get_by_type(self.tenv.DigitalMode).values()]))

  def get_analog(self):
    p = self.get_by_type(self.tenv.AnalogInput).values()
    v = self.get_by_type(self.tenv.AnalogOutput).values()
    return list(chain(*[p+v]))

  def get_digital(self):
    digital = self.PCLS_ALIAS.keys()
    digital = list(set(digital)-set([self.tenv.AnalogInput, self.tenv.AnalogOutput]))
    v = []
    for p in digital: v = v + self.get_by_type(p).values()
    return list(chain(*[v]))

  def get_by_type(self, pcls):
    ''' return dict {name:obj} of port object of which port type is port_cls '''
    try:
      return getattr(self, pcls)
    except AttributeError:
      self._logger.debug(mcode.DEBUG_018 % pcls)
      return {}
  
  def get_by_name(self, name):
    ''' return port object of which port name matches name '''
    for pa in self.PCLS_ALIAS.keys():
      for x in self.get_by_type(pa).values():
        if x.name == name:
          return x
    return None

  def get_pinned(self, ports=[]): # return a list of pinned port objects 
    lfn = lambda v: v.is_pinned
    return list(ifilter(lfn, ports))

  def get_unpinned(self, ports=[]): # return a list of unpinned port objects 
    lfn = lambda v: v.is_pinned
    return list(ifilterfalse(lfn, ports))

  def get_name_by_type(self, pcls):
    ''' return a list of port names of which port class alias matches 'pcls' '''
    port_obj = self.get_by_type(pcls)
    return [] if len(port_obj) == 0 else port_obj.keys()

  def get_quantized_port_name(self):
    ''' return a list of port names of which port class is quantized analog '''
    return self.get_name_by_type(self.tenv.QuantizedAnalog)

  def get_unpinned_quantized_port_name(self):
    return filter(lambda x: self.get_by_name(x).is_pinned == False, self.get_quantized_port_name())

  def get_output_port_name(self):
    ''' return a list of port names of which port class is analog output '''
    return self.get_name_by_type(self.tenv.AnalogOutput)

  def get_input_port_name(self):
    ''' return a list of port names of which port direction is input '''
    return self.get_name_by_type(self.tenv.AnalogInput) + \
           self.get_name_by_type(self.tenv.QuantizedAnalog) + \
           self.get_name_by_type(self.tenv.DigitalMode)

  def get_name_by_types(self,pcls=[]):
    ''' return a list of port names of which port class aliases are listed in "pcls" '''
    return list(chain(*[self.get_name_by_type(x) for x in pcls]))

  def get_name(self):
    ''' Returns a dict where { port_class_alias : list of port names } '''
    return dict([(x,self.get_name_by_type(x)) for x in self.PCLS_ALIAS.keys()])

  def get_no_of_digitalmode(self):
    ''' Returns the number of digital-mode ports in a test '''
    return len(self.get_name_by_type(self.tenv.DigitalMode))

  def get_info(self, name): # print port (named 'name') information to a logger 
    port = self.get_by_name(name)
    self._logger.debug(mcode.DEBUG_002 % port.name)
    self._logger.debug(mcode.DEBUG_003 % port.get_constraint())

  def get_info_all(self): # print information of all ports to a logger 
    for p in flatten_list(self.get_name().values()):
      self.get_info(p)

  def __has_port(self, name):
    ''' checks if there is a port, named "name" and returns a tuple of
        (True/False, port instance, port class alias, description) '''
    for x in self.PCLS_ALIAS.keys():
      palias = getattr(self, x)
      if name in palias.keys(): # if port name "name" exists 
        return True, palias[name], x, palias[name].description
    return False, None, None, None

#--------------------------------
#  some useful functions for port
#--------------------------------

def get_singlebit_name(name, nth_bit): # return a single bit expression in string of a vector 
  return '%s_%d' % (name, nth_bit)

