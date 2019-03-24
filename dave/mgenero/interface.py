
__doc__ = """
  Define interface templates in mGenero

Interface is written in YAML, which interfaces between user configuration of model/test and their templates.

The below describes how it looks like
-------------------------------------
version: 1.0  # interface version
module_name:  # interface name (i.e. generic model name, user config can override)
model_template: # model template filename (user config can override)
test_template:  # test template filename  (user config can override)

pin:  # pin declaration section
  PIN1:     # generic pin name is "PIN1"
    name:              # name of a pin          (user configuration only)
    description:       # description
    direction:         # input/ output
    datatype:          # logic/real/...
    vectorsize:        # number of bitwidth , set to 0 if vector is not allowed, default is 1
    is_optional:       # is this pin optional ? (exists in circuit.cfg while doesn't in interface will be optional)
    is_pinonly:        # True if you want an optional pin doesn't need to be attached to a stimulus driver and create a port spec.
    constraint:        # pin specific constraints (user configuration only)
      constr1:         # constraint name
        value:         # constraint value (string, bool, numbers)
  PIN2:     # another generic pin name is "PIN2"
    name:
  ...

metric:  # optional metrics to be incorporated in a model
  name1:               # metric name named "name1"
    description:       # description
    value:             # list or a value (for interface), a value (for user config)
  name2:
    ...

modelparam: # parameters to be declared in a model
  name1:               # name of a parameter in a model template
    description:       # description
    datatype:          # data type such as integer/real/logic/...
    value:             # value
    is_optional:       # is this param optional ? (interface template only)
  name2:
    ...

testparam: # parameters to be used in a "mProbo" test
  name1:               # name of a parameter in a test template
    description:       # description
    value:             # value
  name2:

testspec: # define I/O port (in test) specification
  test1: # test name 1
    portname1:       
    type:
    range:
    ...
  test2: # test name 2
    portname1:       
    type:
    range:
    ...
"""

import yaml
from dave.common.misc import get_abspath, read_yaml
from collections import OrderedDict


#--------------------------------------------
class Interface(object):
  # Interface class 
  key_tname = 'template_name'
  key_mname = 'module_name'
  key_description = 'description'
  key_pins = 'pin'
  key_metrics = 'metric'
  key_tparams = 'testparam'
  key_mparams = 'modelparam'
  key_tspecs = 'testspec'
  def __init__(self, tname, mname, description, pins, metrics, modelparams, testparams, testspecs):
    self.tname = tname              # template name
    self.mname = mname              # module name (instance name)
    self.description = description  # description
    self.pins = pins                # pin section
    self.metrics = metrics          # metric section
    self.modelparams = modelparams  # model parameter section
    self.testparams = testparams    # test parameter section
    self.testspecs = testspecs    # test port specification section

    self.generic_pin_names = sorted([p.generic_name for p in self.pins])
    self.generic_pin_names_optional = sorted([p.generic_name for p in filter(lambda x: x.is_optional, self.pins)])


  @classmethod
  def load(cls, filename):
    # Load interface file in yaml
    # Build interface class instance
    defaults = OrderedDict()
    defaults.update( {cls.key_pins:None, 
                      cls.key_metrics:None, 
                      cls.key_tparams:None, 
                      cls.key_mparams:None,
                      cls.key_tspecs:None,
                     }
                   )
    prop = read_yaml(filename, defaults)

    def build_section(cls_name, dct): 
      return [cls_name.from_dict(name,val) for name, val in dct.items()] if dct != None else []

    return cls(
            prop[cls.key_tname], 
            prop[cls.key_mname], 
            prop[cls.key_description], 
            build_section(Pin, prop[cls.key_pins]),
            build_section(Metric, prop[cls.key_metrics]),
            build_section(ModelParam, prop[cls.key_mparams]),
            build_section(TestParam, prop[cls.key_tparams]),
            TestSpec.from_dict(prop[cls.key_tspecs])
            )

  def to_dict(self):
    # export interface data to a yaml
    return OrderedDict( {
              self.key_tname: self.tname,
              self.key_mname: self.mname,
              self.key_description: self.description,
              self.key_pins: self.pins_to_dict(),
              self.key_metrics: self.metrics_to_dict(),
              self.key_mparams: self.modelparams_to_dict(),
              self.key_tparams: self.testparams_to_dict(),
              self.key_tspecs: self.testspecs_to_dict(),
            } )

  def pins_to_dict(self):
    return OrderedDict([(p.get_generic_name(),p.get_properties()) for p in self.pins])

  def metrics_to_dict(self):
    return OrderedDict([(p.get_name(),p.get_properties()) for p in self.metrics])

  def modelparams_to_dict(self):
    return OrderedDict([(p.get_name(),p.get_properties()) for p in self.modelparams])

  def testparams_to_dict(self):
    return OrderedDict([(p.get_name(),p.get_properties()) for p in self.testparams])

  def testspecs_to_dict(self):
    return self.testspecs.value 

  def to_yaml(self):
    return yaml.dump(self.to_dict())

  def get_generic_pin_list(self):
    # return a list of pin names 
    return self.generic_pin_names

  def get_generic_pin_optional(self):
    ''' return a list of pin names which is optional '''
    return self.generic_pin_names_optional

  def get_template_name(self):
    return self.tname

  def get_module_name(self):
    return self.mname


#--------------------------------------------
class Pin(object):
  # Generic I/O pins 
  def __init__(self, generic_name, name, description, direction, datatype, vectorsize, is_optional, is_pinonly):
    self.generic_name = generic_name # generic pin name
    self.name = name                 # pin name in a circuit
    self.description = description   # description
    self.direction = direction       # pin direction
    self.datatype = datatype         # signal datatype on a pin
    self.vectorsize = vectorsize     # optional for digital pin. default is 1
    self.is_optional = is_optional   # this pin is optional if True. Default is False
    self.is_pinonly = is_pinonly     # If this is true, it won't create test specs, stimulus driver in a test bench
    
  @classmethod
  def from_dict(cls, name, prop):
    # create member variables from a dictionary 
    defaults = {'is_pinonly': False, 'is_optional': False, 'vectorsize': 0, 'name': name}
    defaults.update(prop)
    prop = defaults
    return cls(name, prop['name'], prop['description'],
               prop['direction'], prop['datatype'],
               prop['vectorsize'], prop['is_optional'], prop['is_pinonly'])

  def to_dict(self):
    # export member variables to dict
    return {self.generic_name: {
              'name': self.name, 'description': self.description,
              'direction': self.direction, 'datatype': self.datatype,
              'vectorsize': self.vectorsize, 
              'is_optional': self.is_optional, 'is_pinonly': self.is_pinonly } }

  def get_generic_name(self): # generic pin name
    return self.generic_name

  def get_properties(self): # properties 
    return self.to_dict().values()[0]
            

#--------------------------------------------
class Metric(object):
  # Optional Model behaviors being incorporated
  def __init__(self, name, description, value):
    self.name = name                # name of a metric
    self.description = description  # description of a metric
    self.value = value              # a value/list for interface, a value for user configuration

  @classmethod
  def from_dict(cls, name, prop):
    # create member variables from a dictionary 
    defaults = {'value': []}
    defaults.update(prop)
    prop = defaults
    return cls(name, prop['description'], prop['value'])

  def to_dict(self):
    # export member variables to dict
    return {self.name: {
              'description': self.description, 'value': self.value} }

  def get_name(self):
    return self.name

  def get_properties(self):
    return self.to_dict().values()[0]


#--------------------------------------------
class ModelParam(object):
  # Model parameters which will be declared as parameters in a model 
  def __init__(self, name, description, datatype, value, is_optional):
    self.name = name
    self.description = description 
    self.datatype = datatype 
    self.value = value 
    self.is_optional = is_optional   # this param is optional if True. Default is False

  @classmethod
  def from_dict(cls, name, prop):
    # create member variables from a dictionary 
    defaults = {'is_optional': False}
    defaults.update(prop)
    prop = defaults
    return cls(name, prop['description'],
               prop['datatype'], prop['value'], prop['is_optional'])

  def to_dict(self):
    # export member variables to dict
    return {self.name: {
              'description': self.description, 'datatype': self.datatype,
              'value': self.value,
              'is_optional': self.is_optional} }

  def get_name(self):
    return self.name

  def get_properties(self):
    return self.to_dict().values()[0]


#--------------------------------------------
class TestParam(object):
  # Test parameters which will be used in test configuration of mProbo 
  def __init__(self, name, description, value):
    self.name = name
    self.description = description 
    self.value = value 

  @classmethod
  def from_dict(cls, name, prop):
    # create member variables from a dictionary 
    return cls(name, prop['description'], prop['value'])

  def to_dict(self):
    # export member variables to dict
    return {self.name: {'description': self.description, 'value': self.value}}

  def get_name(self):
    return self.name

  def get_properties(self):
    return self.to_dict().values()[0]


#--------------------------------------------
class TestSpec(object):
  # Specify input/output ranges of each test in mProbe test.cfg 
  def __init__(self, value):
    self.value = value # dict that defines test port specifications

  @classmethod
  def from_dict(cls, prop):
    # create member variables from a dictionary 
    return cls(prop)

  def to_dict(self):
    # export member variables to dict
    return self.value 

#--------------------------------------------
def main():
  m =  Metric.from_dict({'name': 'max_swing', 'description': 'max voltage swing', 'minval': 0.1, 'maxval': 1.1, 'abstol': 0.001})
  x = Interface.load('/home/bclim/proj/DaVEnv/mGenero/samples/template/cteq/cteq.interface')
  print vars(x)
  print x.get_generic_pin_optional()

if __name__ == "__main__":
  main()
