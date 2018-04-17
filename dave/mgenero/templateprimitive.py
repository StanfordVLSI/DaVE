#
__doc__ = '''
Primitive functions to be embeded in model/test templates
'''

MODEL_PRIMITIVE_FUNCTIONS = """@{
# Available classes
# Module()
# Pin()
# Metric()
# Param()

import sys
import os
from dave.common.misc import dec2bin

##############################
# primitive functions
##############################

def put_warning_message(msg):
  return '###--- WARNING: '+ msg.upper()

def put_error_message(msg):
  return '###--- ERROR: '+ msg

def print_bus(n):
  ''' 
  print out bus representation for given bus width (n) 
  if n==1, return a space
  '''
  return '[%d:0]' % int(n-1) if n > 1 else ''

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

##############################
# MODULE declaration section
##############################
class Module(object):
  @classmethod
  def name(cls): 
    ''' 
    Prints out a module name. Mainly used for two purposes: 
      a. module name declaration in Verilog model, and
      b. device-under-test (dut) name declaration in mProbo test
    '''
    try:
      return module_name
    except:
      return None
    
  @classmethod
  def pin(cls, p, comma=False): 
    '''
    print a pin in module declaration. A comma will follow if comma==True
    '''
    if Pin.is_exist(p):
      if Pin.datatype(p) == 'pwl':
        return PWL.declare_pin(p, comma)
      elif Pin.datatype(p) == 'real':
        return REAL.declare_pin(p, comma)
      elif Pin.datatype(p) == 'logic':
        return LOGIC.declare_pin(p, comma)
    
  @classmethod
  def pins(cls): # print all pins in module declaration
    pl = Pin.list()
    return '\\n  '.join([ cls.pin(p, True) for p in pl[:-1] ] + [ cls.pin(pl[-1], False) ])
  
  @classmethod
  def parameter(cls, p, comma=False, semicolon=False): 
    ''' 
    Print a parameter in module declaration. A comma will follow if comma==True
    '''
    if Param.is_exist(p):
      return 'parameter %s %s = %s%s%s // %s' % (Param.datatype(p), Param.name(p), Param.value(p), ',' if comma else '', ';' if semicolon else '', Param.description(p))
  
  @classmethod
  def parameters(cls): # print all parameters in module declaration
    pl = Param.list()
    if pl != []:
      return '\\n  '.join([ cls.parameter(p, True) for p in pl[:-1] ] + [ cls.parameter(pl[-1], False) ])

##############################
# PIN section
##############################

class Pin(object):
  @classmethod
  def get(cls): # get the "pin" section in the interface
    return pin

  @classmethod
  def list(cls): # return a list of pins
    return cls.get().keys()

  @classmethod
  def list_property(cls, p): # return a list of properties for given pin name
    return cls.get()[p].keys()

  @classmethod
  def get_namemap(cls): # return a dict of pin map (generic -> user)
    return dict([(p, cls.name(p)) for p in cls.list()])
  
  @classmethod
  def get_reversed_namemap(cls): # return a dict of reversed pin map (user -> generic)
    return dict([(cls.name(p),p) for p in cls.list()])
  
  @classmethod
  def is_exist(cls, p): # check if a pin named 'p' exists
    return p in cls.list()
  
  @classmethod
  def property(cls, p, c): # retreive property 'c' of a pin 'p'
    try:
      return cls.get()[p][c]
    except:
      return None
  
  @classmethod
  def is_mode(cls, p): # retreive property 'is_mode' of a pin 'p'
    return cls.property(p, 'is_mode') 
  
  @classmethod
  def constraint(cls, p, c): # retreive the value of constraint 'c' of a pin 'p'
    constraint = cls.property(p, 'constraint') 
    return constraint[c]['value']
  
  @classmethod
  def is_or(cls, p1, p2): # at least one of pins ('p1' and 'p2') should exist
    return True if cls.is_exist(p1) or cls.is_exist(p2) else False
  
  @classmethod
  def is_and(cls, p1, p2): # both pins ('p1' and 'p2') should exist
    return True if cls.is_exist(p1) and cls.is_exist(p2) else False
  
  @classmethod
  def is_xor(cls, p1, p2): # only one of pins ('p1' and 'p2') should exist
    return True if cls.is_exist(p1) ^ cls.is_exist(p2) else False
  
  @classmethod
  def name(cls, p):
    return cls.property(p,'name')
  
  @classmethod
  def generic_name(cls, name):
    return cls.get_reversed_namemap()[name]
  
  @classmethod
  def direction(cls, p):
    return cls.property(p, 'direction')
  
  @classmethod
  def datatype(cls, p):
    dt = cls.property(p, 'datatype') 
    if dt=='': dt='logic'
    return dt
  
  @classmethod
  def description(cls, p):
    return cls.property(p, 'description')
  
  @classmethod
  def vectorsize(cls, p):
    if 'vectorsize' in cls.list_property(p):
      return cls.property(p, 'vectorsize')
    else:
      return 0
  
  @classmethod
  def list_constraint(cls, p):
    c = cls.property(p, 'constraint')
    if c != None:
      return c.keys()
    else:
      return []

  @classmethod
  def check_pin_chain(cls): # sometimes, other pins should exist when a pin exists
    err_list = []
    for p in cls.list():
      if 'pin_chain' in cls.list_constraint(p):
        violated = list(set(cls.constraint(p, 'pin_chain'))-set(cls.list()))
        if (violated != []):
          err_list.append('Pin chain validation failed. Missing pin(s) "'+','.join(violated)+'" for the pin "%s"' % p)

    if len(err_list) > 0:
      print '\\n'.join(map(put_error_message, err_list))
      sys.exit()

  @classmethod
  def is_current(cls, p):  # check if this pin is current signal
    return 'current' in cls.list_constraint(p)

  @classmethod
  def current_direction(cls, p):  # return current direction ('p' or 'n')
    return Pin.constraint(p, 'current')
      
  @classmethod
  def list_optional(cls): # return list of generic pin names which are optional
    return [p for p,v in cls.get().items() if v['is_optional']]
  
  @classmethod
  def list_optional_digital(cls):  # return generic pin names of (digital)
    return [p for p in cls.list_optional() if cls.datatype(p) in ['logic', ''] and cls.direction(p) == 'input']
  
  @classmethod
  def list_optional_analog(cls, exclude=[]):  # return generic pin names of (NOT digital) except pins listed in exclude
    plist = [p for p in cls.list_optional() if cls.datatype(p) != 'logic' and cls.direction(p) == 'input']
    return list(set(plist)-set(exclude))
  
  @classmethod
  def list_optional_analog_current(cls, exclude=[]):  # return generic pin names of (NOT digital) except pins listed in exclude (constraint doesn't have 'current' key)
    plist = [p for p in cls.list_optional() if cls.datatype(p) != 'logic']
    pins  = list(set(plist)-set(exclude))
    return filter(cls.is_current, pins)
  
  @classmethod
  def list_optional_analog_voltage(cls, exclude=[]):  # return generic pin names of (NOT digital) except pins listed in exclude (constraint doesn't have 'current' key)
    pins = cls.list_optional_analog(exclude)
    return list(set(pins)-set(cls.list_optional_analog_current(exclude)))

  @classmethod
  def list_pinonly(cls, exclude=[]): # return optional pin names with 'is_pinonly'==True
    return [p for p,v in cls.get().items() if v['is_pinonly']]

  @classmethod
  def declare_signal(cls, p):
    if Pin.datatype(p) == 'pwl':
      return PWL.declare_signal(p)
    elif Pin.datatype(p) == 'real':
      return REAL.declare_signal(p)
    elif Pin.datatype(p) == 'logic':
      return LOGIC.declare_signal(p)
    
  @classmethod
  def print_map(cls): 
    '''
    Print out vlog statements to map generic pins in the template to user pins, if the names are different.
    Since all the body statements in the model template will look up generic pin names instead of user pin names, there should be statements for the mapping.  
    NOTE: THIS FUNCTION MUST BE PRESENT IN VERILOG TEMPLATE
    '''
    vlogstatement = [cls.declare_signal(p) for p in cls.list() if p != cls.name(p)]
    vlogstatement += ['assign %s=%s ;' %(cls.name(p),p) if cls.direction(p)=='output' else 'assign %s=%s ;' %(p,cls.name(p)) for p in cls.list() if p != cls.name(p)]
    return '// map pins between generic names and user names, if they are different\\n'+'\\n'.join(vlogstatement)

  @classmethod
  def print_if_exists(cls, statement, p): 
    ''' 
    Print a Verilog statement if pin p exists.
    Note that @@ is replaced with @ in this function.
    Therefore do not use this function if the statement has @ for Verilog such as 'always @'
    '''
    return statement.replace('@@','@') if Pin.is_exist(p) else ''

##############################
# PARAMETER section
##############################
class Param(object):

  @classmethod
  def get(cls): # return modelparams section
    return modelparam

  @classmethod
  def prefix(cls): # return parameter prefix when calibration is disabled
    return 'rep_'

  @classmethod
  def list(cls): # return a list of model parameters
    return cls.get().keys()
  
  @classmethod
  def is_exist(cls, p): # check if a parameter named 'p' exists
    try:
      return p in cls.list()
    except:
      return None
  
  @classmethod
  def property(cls, p,c): # retreive property 'c' of a parameter 'p'
    return cls.get()[p][c]
  
  @classmethod
  def name(cls, p): # return parameter name p, if it exists
    return p if p in cls.list() else None
  
  @classmethod
  def description(cls, p): # retreive description of a parameter 'p'
    return cls.property(p, 'description')
  
  @classmethod
  def value(cls, p): # retreive value of a parameter 'p'
    return cls.property(p, 'value')
  
  @classmethod
  def datatype(cls, p): # retreive data type of a parameter 'p'
    return cls.property(p, 'datatype')


##############################
# METRIC section
##############################
class Metric(object):
  @classmethod
  def get(cls): # return metrics section
    return metric

  @classmethod
  def list(cls): # return a list of metrics
    return cls.get().keys()

  @classmethod
  def is_exist(cls, m): # check if a metric named 'm' exist
    try:
      return m in cls.list()
    except:
      return None

  @classmethod
  def property(cls, m, c): # retreive property 'c' of a metric 'm'
    return cls.get()[m][c]
  
  @classmethod
  def description(cls, m): # retreive description of a metric 'm'
    try:
      return cls.property(m, 'description')
    except:
      return ''

  @classmethod
  def value(cls, m): # retreive description of a metric 'm'
    return cls.property(m, 'value')
  
  @classmethod
  def print_if_exists(cls, statement, m): 
    ''' 
    Print a Verilog statement if metric m exists.
    Note that @@ is replaced with @ in this function.
    Therefore do not use this function if the statement has @ for Verilog such as 'always @'
    '''
    return statement.replace('@@','@') if cls.is_exist(m) else ''
  

##############################
# Miscellaneous functions
##############################

def get_sensitivity_list():
  '''
  return default sensitivity list
  '''
  return REAL.list_optional_pins() + PWL.list_optional_pins_in_real() + LOGIC.list_optional_pins()

  
def print_sensitivity_list(list_val):
  ''' 
  print out sensitivity list in Verilog format
  '''
  if list_val == []:
    return '*'
  else:
    return ' or '.join(list_val)

def annotate_modelparam(param_map, variable_map={}):
  '''
  Create verilog statements to back annotate the extracted parameters to variables
  param_map = { testname : { testresponse : verilog variable being mapped to }, ... }
  variable_map is a dictionary that maps predictor variable in a test to a Verilog variable.
  variable_map = { var1 : Verilog_var1, var2 : Verilog_var2, ... }
  This will take into account for digital modes as well
  '''
  #if 'variable_map' not in globals():
  #  variable_map = {}
  digital_modes = ["get_lm_equation_modes('%s', '%s')" % (k, v.keys()[0]) for k,v in param_map.items()]
  digital_cases = ['digital_modes[%d][0].keys()' % i for i in range(len(digital_modes))]
  vlog_1 = 'digital_modes = [%s]\\n' % ', '.join(digital_modes)
  vlog_2 = 'digital_cases = [%s]\\n' % ', '.join(digital_cases)
  vlog_3 = 'variable_map = {v_map}\\n'.format(v_map = variable_map)
  vlog = '$${\\n' + vlog_1 + vlog_2 + vlog_3 + '}$$\\n'
  for i, t in enumerate(param_map.keys()):
    vlog += _annotate_verilog_statement(t, param_map[t], i)
  return vlog

def _annotate_verilog_statement(testname, param_map_value, case_index):
  vlog_statement_template = '''
$$[if not mode_exists('{testname}')]
{vlog_statement1}
$$[else]
  case({{$$(','.join({casenumber}))}})
$$[for m in {modenumber}]
  {{$$(','.join(["%d'b%s" % (Pin.vectorsize(d), dec2bin('%d'%m[d], Pin.vectorsize(d))) for d in {casenumber}]))}}: begin
{vlog_statement2}
  end
$$[end for]
  default: begin
{vlog_statement3}
  end
  endcase
$$[end if]
'''
  vlog = ''
  template_base = "{variable} = $$get_lm_equation('{testname}', '{response}'"
  casenumber = 'digital_cases[%d]' % case_index
  modenumber = 'digital_modes[%d]' % case_index
  template = template_base + ');'
  vlog_statement1 = '  '+'\\n  '.join([template.format(variable=v, testname=testname, response=k) for k,v in param_map_value.items()])
  template = template_base + ', m);'
  vlog_statement2 = '    '+'\\n    '.join([template.format(variable=v, testname=testname, response=k) for k,v in param_map_value.items()])
  template = template_base + ', %s[0]);' % modenumber
  vlog_statement3 = '    '+'\\n    '.join([template.format(variable=v, testname=testname, response=k) for k,v in param_map_value.items()])
  vlog += vlog_statement_template.format(testname=testname, casenumber=casenumber, modenumber=modenumber, vlog_statement1 = vlog_statement1, vlog_statement2 = vlog_statement2, vlog_statement3 = vlog_statement3)
  return vlog

################
# LOGIC-specific
################
class LOGIC(object):
  @classmethod
  def declare_pin(cls, p, comma=False): 
    ''' print a pin in module declaration. A comma will follow if comma==True '''
    return '%s %s %s %s%s // %s' % (Pin.direction(p), Pin.datatype(p), print_bus(Pin.vectorsize(p)), Pin.name(p), ',' if comma else '', Pin.description(p))
  @classmethod
  def declare_signal(cls, p): 
    return '%s %s %s;' %(Pin.datatype(p), print_bus(Pin.vectorsize(p)), p)

  @classmethod
  def list_optional_pins(cls, exclude=[]):  # return generic pin names of (digital)
    return [p for p in list(set(Pin.list_optional())-set(exclude)) if Pin.datatype(p) in ['logic', '']]

################
# REAL-specific
################
class REAL(object):
  @classmethod
  def declare_pin(cls, p, comma=False): 
    ''' print a pin in module declaration. A comma will follow if comma==True '''
    return '%s %s %s %s%s // %s' % (Pin.direction(p), Pin.datatype(p), print_bus(Pin.vectorsize(p)), Pin.name(p), ',' if comma else '', Pin.description(p))

  @classmethod
  def declare_signal(cls, p): 
    return '%s %s %s;' %(Pin.datatype(p), p, print_bus(Pin.vectorsize(p)))

  @classmethod
  def list_optional_pins(cls, exclude=[]):
    '''
    Get a list of real signal expressions for optional real analog pins
    '''
    return  [p for p in list(set(Pin.list_optional_analog())-set(exclude)) if Pin.datatype(p)=="real"]

##############
# PWL-specific
##############
class PWL(object):
  @classmethod
  def declare_pin(cls, p, comma=False): 
    ''' print a pin in module declaration. A comma will follow if comma==True '''
    return '%s %s %s %s%s // %s' % (Pin.direction(p), Pin.datatype(p), Pin.name(p), print_bus(Pin.vectorsize(p)), ',' if comma else '', Pin.description(p))

  @classmethod
  def declare_signal(cls, p): 
    return '%s %s %s;' %(Pin.datatype(p), p, print_bus(Pin.vectorsize(p)))

  @classmethod
  def get_real(cls, signame):
    '''
    Get a real signal expression for given pwl signal name (signame)
    '''
    return '%s_r' % signame

  @classmethod
  def list_optional_pins(cls, exclude=[]):
    '''
    Get a list of real signal expressions for optional pwl analog pins
    '''
    pl = [p for p in list(set(Pin.list_optional_analog())-set(exclude)) if Pin.datatype(p)=="pwl"]
    return map(cls.get_real, pl)

  @classmethod
  def list_optional_pins_in_real(cls, exclude=[]):
    '''
    Get a list of real signal expressions for optional pwl analog pins with real suffix
    '''
    return map(cls.get_real, cls.list_optional_pins())


  @classmethod
  def instantiate_pwl2real(cls, signame):
    '''
    Convert PWL waveform to PWC waveform for a given signal name, using pwl2real primitive.
    Output "real" signal has the same signal name as its PWL signal, but it will be followed by a suffix "_r" 
    '''
    return 'pwl2real #(.dv(etol_{signal})) xp2r_{signal} (.in({signal}), .out({signal}_r)); // pwl-to-real of {signal}'.format(signal=signame)

  @classmethod
  def declare_real(cls, sig_list):
    ''' 
    Declare the corresponding "real" signal (wire) of a PWL signal
    The "real" signal will have the same signal 
    '''
    if len(sig_list) > 0:
      return 'real %s;' % ', '.join(sig_list)
    else:
      return ''

  @classmethod
  def declare_optional_analog_pins_in_real(cls, exclude=[]):
    ''' 
    declare optional analog pins with real datatype suffix
    '''
    pl_real = list(set(cls.list_optional_pins())-set(exclude))
    return cls.declare_real(pl_real)

  @classmethod
  def instantiate_pwl2real_optional_analog_pins(cls, exclude=[]):
    ''' 
    do instantiate_pwl2real for all optional analog pins
    '''
    pl = [p for p in list(set(Pin.list_optional_analog())-set(exclude)) if Pin.datatype(p)=="pwl"]
    _statements = map(cls.instantiate_pwl2real, pl)
    return '\\n'.join(_statements)
  
}@
"""

TEST_PRIMITIVE_FUNCTIONS = """@{
##############################
# test primitive functions
##############################

class Test(object):

  @classmethod
  def dut(cls): # print dut name
    return Module.name()

class TestPort(object):

  @classmethod
  def declare_optional_pins_prime(cls, port_name, is_digital):
    '''
    Declare port specifiction in test for given port
    '''
    if is_digital:
      spec = {'port_type': 'digitalmode', 'encode':'binary', 'prohibited': '', 'pinned': 'False', 'default_value': 'b0'}
      template = '''    [[[{port_name}]]]
      port_type = {port_type}
      bit_width = {bit_width}
      encode = {encode}
      prohibited = {prohibited}
      pinned = {pinned}
      default_value = {default_value}
      description = {description}
'''
    else:
      spec = {'port_type': 'analoginput', 'regions': '0.0, 1.0', 'pinned': 'False', 'default_value': '0.5'}
      template = '''    [[[{port_name}]]]
      port_type = {port_type}
      regions = {regions}
      pinned = {pinned}
      default_value = {default_value}
      description = {description}
'''
    testcfg = ''
    spec.update({'port_name': port_name, 'description': Pin.description(port_name)})
    if is_digital:
      spec.update({'bit_width': Pin.vectorsize(port_name)})
    testcfg += template.format(**spec)
    return testcfg

  @classmethod
  def declare_optional_analog_pins(cls, exclude=[]):
    '''
    Do class.declare_optional_pins_prime for optional analog pins
    '''
    testcfg = ''
    for p in list(set(Pin.list_optional_analog())-set(exclude)):
      testcfg += cls.declare_optional_pins_prime(p, False)
    return testcfg

  @classmethod
  def declare_optional_digital_pins(cls, exclude=[]):
    '''
    Do class.declare_optional_pins_prime for optional digital pins
    '''
    testcfg = ''
    for p in list(set(Pin.list_optional_digital())-set(exclude)):
      testcfg += cls.declare_optional_pins_prime(p, True)
    return testcfg

  @classmethod
  def declare_optional_pins(cls, exclude=[]):
    '''
    Do class.declare_optional_pins_prime for optional analog and digital pins
    '''
    testcfg = cls.declare_optional_analog_pins(exclude)
    testcfg += cls.declare_optional_digital_pins(exclude)
    return testcfg
    
class Testbench(object):      

  @classmethod
  def instantiate_bitvector(cls, signame, bitwidth, value=''):
    ''' 
    Instantiate bitvector
    bitvector #(.bit_width({bitwidth}), .value(@{signame})) xbv_{signame} (.out({signame}));
    '''
    if value == '':
      value = '@(%s)' % signame
    return 'bitvector #(.bit_width({bitwidth}), .value({value})) xbv_{signame} (.out({signame}{bus}));'.format(signame=signame, bitwidth=bitwidth, value=value, bus='[%d:0]' % (Pin.vectorsize(signame)-1) if Pin.vectorsize(signame)>1 else '')

  @classmethod
  def instantiate_bitvector_optional_pins(cls, exclude=[]):
    '''
    Do cls._instantiate_bitvector() for all optional digital pins
    '''
    return '\\n'.join([cls.instantiate_bitvector(p, Pin.vectorsize(p)) for p in Pin.list_optional_digital() if p not in exclude])

  @classmethod
  def instantiate_vdc(cls, signame, value=''):
    ''' 
    Instantiate vdc 
    For e.g., instantiate_vdc('vin') will produce
    vdc #(.dc(@vin)) xvdc_vin (.vout(vin));
    '''
    if value == '':
      value = '@(%s)' % signame
    return 'vdc #(.dc({value})) xvdc_{signame} (.vout({signame}));'.format(signame=signame, value=value)

  @classmethod
  def instantiate_vdc_optional_pins(cls, exclude=[]):
    '''
    Do cls._instantiate_vdc() for all optional analog voltage pins
    '''
    return '\\n'.join([cls.instantiate_vdc(p) for p in list(set(Pin.list_optional_analog_voltage()) - set(exclude))])

  @classmethod
  def instantiate_idc(cls, signame, pnode, nnode, value=''):
    ''' 
    Instantiate idc which produces signame 
    For e.g., instantiate_idc('iin', 'vdd', 'iin') will produce
    idc #(.is_n(1), .dc(@iin)) xidc_iin (.outnode(iin), .refnode(vdd));
    '''
    if value == '':
      value = '@(%s)' % signame
    return 'idc #(.is_n({direction}), .dc({value})) xidc_{signame} (.outnode({outnode}), .refnode({refnode}));'.format(signame=signame, outnode=signame, refnode=pnode if signame==nnode else nnode if signame==pnode else 'ERROR', direction = '0' if signame==pnode else '1' if signame==nnode else 'ERROR', value=value)

  @classmethod
  def instantiate_idc_optional_pins(cls, prefnode='vdd', nrefnode='gnd', exclude=[]):
    '''
    Do cls._instantiate_idc() for all optional analog current pins
    '''
    return '\\n'.join([cls.instantiate_idc(p, p if Pin.current_direction(p)=='n' else prefnode, p if Pin.current_direction(p)=='p' else nrefnode  ) for p in Pin.list_optional_analog_current() if p not in exclude])

  @classmethod
  def instantiate_idc_on_pin(cls, signame, prefnode='vdd', nrefnode='gnd'):
    '''
    Do cls._instantiate_idc() for all optional analog current pins
    '''
    p = signame
    return cls.instantiate_idc(p, p if Pin.current_direction(p)=='n' else prefnode, p if Pin.current_direction(p)=='p' else nrefnode)

  @classmethod
  def dut(cls): # device-under-test
    return Test.dut()

  @classmethod
  def map_by_name(cls, p): # map a pin by name in Verilog
    if Pin.vectorsize(p) > 1:
      return '.%s(%s%s)' % (Pin.name(p),p,print_bus(Pin.vectorsize(p)))
    else:
      return '.%s(%s)' % (Pin.name(p),p)
  
  @classmethod
  def dut_map_by_name(cls): # print dut pin mapping by name in Verilog
    return ' %s ' % (', '.join([cls.map_by_name(p) for p in Pin.list()]))
  
class TestParam(object):
  @classmethod
  def get(cls): # return testparams section
    return testparam

  @classmethod
  def list(cls): # return a list of parameter names
    return cls.get().keys()

  @classmethod
  def is_exist(cls, p): # check if p param exists
    return p in cls.list()
  
  @classmethod
  def value(cls, p, dtype=float): # retrieve parameter value in test
    return dtype(cls.property(p, 'value'))
    
  @classmethod
  def property(cls, p, c): # retrieve parameter property in test
    return cls.get()[p][c]
  
class TestWire(object):
  @classmethod
  def declare_analog(cls, list_pin, datatype=''):
    if datatype=='':
      list_val = list_pin
    else:
      list_val = filter(lambda x: Pin.datatype(x)==datatype, list_pin)
    return ','.join(list_val)

  @classmethod
  def declare_logic(cls, list_pin):
    return ','.join(['%s %s' %(print_bus(Pin.vectorsize(p)),p) for p in list_pin])

##############################
# Template section
##############################
class Template(object):
  @classmethod
  def module_name(cls):
    ''' return generic module name '''
    return generic_module_name

  @classmethod
  def is_calibration(cls):
    ''' check if a test is for calibration or for model checking '''
    return is_calibration

  @classmethod
  def include_snippet(cls, filename, id=''):
    ''' include snippets from the specified file.
        The full filename will be os.path.join(template_rootdir, filename)
        This is useful if you want to reuse parts of codes from other template
        Snippets between ('//---SNIPPET ON' and '//---SNIPPET OFF') 
        will be snipped off and included in the current template
        'id' is an identifier if you want to have many snippet sections
        e.g.) see cml and cml_mux
    '''
    code = []
    snippet_on = False
    snippet_filename = os.path.join(template_rootdir, filename)
    if not os.path.exists(snippet_filename):
      print put_error_message('No %s file exists' % snippet_filename)
      sys.exit()
    else:
      with open(os.path.join(template_rootdir, filename), 'r') as f:
        for l in f.readlines():
          l = l.strip()
          if l.startswith('//---SNIPPET ON'):
            if id == '' or id == l.split('//---SNIPPET ON')[1].rstrip().lstrip():
              snippet_on = True
          elif l.startswith('//---SNIPPET OFF'):
            snippet_on = False
          elif snippet_on:
            code.append(l)
    return '\\n'.join(code)

# check pin chain (a pin need other pin. for e.g. differential inputs)
Pin.check_pin_chain()
}@
"""

MODEL_HEADER = """{start}{duplicate}
{ll} Module Name: @Module.name()
{ll} This code is automatically generated by "{software}"
{ll} at {timestamp}.
{ll} Note that this version of "{software}" and the generated code
{ll} are only for evaluation purpose. Any redistribution, modification, 
{ll} or commercial use is prohibited without permission.
{ll}
{ll} Copyright (c) 2014-Present by Byong Chan Lim. All rights reserved.
{ll}
{ll} The information and source code contained herein is the property
{ll} of Byong Chan Lim, and may not be disclosed or reproduced
{ll} in whole or in part without explicit written authorization from
{ll} Byong Chan Lim.
{ll} For more information, contact bclim at stanford.edu
{duplicate}{end}
"""

BACKANNOTATION_PRIMITIVE_FUNCTIONS = """
@{{
lm_param = {lm_param}

def mode_exists(testname): # return False if there is only 'dummy_digitalmode' in a test, testname
  param = globals()['lm_param']
  response = param[testname][param[testname].keys()[0]][0]
  if response['mode'].keys()==['dummy_digitalmode']:
    return False
  else:
    return True

def get_lm_coef(testname, dv, iv, mode={{'dummy_digitalmode':0}}):
  ''' 
      testname: test name
      dv: generic output response name (metric) 
      iv: generic analog control input in test.cfg
      mode: dict of true digital input vector in test.cfg
  '''
  param = globals()['lm_param']
  if dv in param[testname].keys():
    for v in param[testname][dv]:
      if v['mode']==mode:
        if iv in v['coef'].keys():
          return v['coef'][iv]
        else:
          return None
    return None
  else:
    return None

def get_terms(testname, dv, mode={{'dummy_digitalmode':0}}):
  ''' return a list of terms for dependent variable dv 
      Note that A, B, A:B are all different terms
  '''
  param = globals()['lm_param']
  if dv in param[testname].keys():
    for v in param[testname][dv]:
      if v['mode']==mode:
        return v['coef'].keys()
    return None
  else:
    return None

def get_lm_equation_modes(testname, dv):
  ''' return a list of a dictionary where the dictionary is a mode '''
  param = globals()['lm_param'][testname][dv]
  return [k['mode'] for k in param]

def replace_lm_variable_name(t):
  ''' replace variable name in linear equation by looking up variable_map if exists '''
  if t in variable_map.keys():
    return variable_map[t]
  elif Pin.is_exist(t):
    if Pin.datatype(t) == 'pwl':
      return PWL.get_real(t)
    else:
      return t
  else:
    return t

def get_lm_equation(testname, dv, mode={{'dummy_digitalmode':0}}, default='0.0'):
  ''' return a linear equation of dv as a function of inputs
      note that there is a suffix of '_r' for every independent variable in the resultant equation
      of which pin has a datatype of pwl
  '''
  try:
    import re
    from dave.common.misc import flatten_list
    param = globals()['lm_param']
    _terms = get_terms(testname, dv, mode) # terms from linear regression
    _coefs = [get_lm_coef(testname, dv, iv, mode) for iv in _terms]
  
    def get_unit_terms(term):
      ''' extact variables. For example, ctl1*ctl2 will produce [ctl1,ctl2] '''
      return [f for f in term.split('*') if len(f) >0 and f[0].isalpha()]
  
    _port = sorted(list(set(flatten_list([get_unit_terms(t) for t in _terms]))-set(['offset']))) # all the unit independent variables from linear regression results
    _varl = [replace_lm_variable_name(t) for t in _port]
  
    equation = '+'.join(['%s*%s' %(str(_coefs[i]),t) if t!='offset' else str(_coefs[i]) for i,t in enumerate(_terms)]).replace('+-','-')
    for i,v in enumerate(_port):
      equation = re.sub(r'\\b%s\\b' % v, _varl[i], equation)
    return equation
  except:
    return default


}}@
"""
