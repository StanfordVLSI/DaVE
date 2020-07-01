#

__doc__ = """
Schema for test/simulator configuration file.

TODO:
  - Somehow, validation of test config doesn't work correctly. Only type conversion works.
"""


from configobj import ConfigObj, flatten_errors
from validate import Validator, ValidateError, VdtTypeError
import os
from io import StringIO
from . import mproboenv

from .environ import EnvFileLoc, EnvFileLoc, EnvTestcfgSection, EnvTestcfgOption, EnvTestcfgPort, EnvSimcfg, EnvPortName
from dave.common.misc import get_abspath, from_engr, force_list, str2num
from dave.common.davelogger import DaVELogger
import dave.mprobo.mchkmsg as mcode

class SchemaConfig(object):
  def __init__(self, configobj, configspecfile, config_type, logger_id='logger_id'):

    self._logger = DaVELogger.get_logger('%s.%s.%s' % (logger_id, __name__, self.__class__.__name__)) # logger
    self.cfgtype = config_type
    configspec = ConfigObj(infile=configspecfile, interpolation=False, list_values=False)
    vfile = StringIO()
    configobj.write(vfile)
    self.config = ConfigObj(vfile.getvalue().splitlines(), configspec=configspec)
    vfile.close()

  def _validate(self, custom_check = {}):
    self.vtor = Validator(custom_check)
    results = self.config.validate(self.vtor) # this will always not be True
    return flatten_errors(self.config, results)

  def _output_vdterror(self, error_key):
    for (section_list, key, _) in self.vdt_errors:
      if key is None:
        pass
        #print 'The following sections "%s" is(are) missing in the %s configuration' % ('.'.join(section_list), self.cfgtype)
      else:
        msg = mcode.ERR_011 % (key, ','.join(section_list))
        if key in error_key:
          raise ValidateError(msg)
        else:
          print('[Warning]' + msg)

  def get_cfg(self):
    ''' get validated ConfigObj '''
    return self.config
    
  

class SchemaSimulatorConfig(SchemaConfig):

  def __init__(self, configobj, is_goldenonly=False, logger_id='logger_id'):
    self._tenvf = EnvFileLoc()
    self._tenvsc = EnvSimcfg()
    self._schema_filename = mproboenv.get_simcfg()
    SchemaConfig.__init__(self, configobj, self._schema_filename, 'simulator', logger_id)
    self.vdt_errors = self._validate()
    self._run_custom_check(is_goldenonly)

  def raise_vdterror(self):
    self._output_vdterror([self._tenvsc.model, self._tenvsc.simulator])

  def _run_custom_check(self, is_goldenonly):
    models = [self._tenvsc.golden] + [] if is_goldenonly else [self._tenvsc.revised]
    for x in models:
      self.config[x] = self._chk_circuit_subsection(self.config[x])
      self.config[x] = self._chk_ams_control(self.config[x])
      self.config[x] = self._chk_hdl_files(self.config[x])

  def _chk_ams_control(self, section):
    if section[self._tenvsc.ams_control_file] == '':
      del section[self._tenvsc.ams_control_file]
      return section

    assert section[self._tenvsc.model] == self._tenvsc.model_ams, '"%s" is valid only for model="%s"' % (self._tenvsc.ams_control_file, self._tenvsc.model_ams)

    v = section[self._tenvsc.ams_control_file]
    assert type(v)==str, mcode.ERR_012 % (v, self._tenvsc.ams_control_file)
    fname = get_abspath(v, do_assert=False, logger=self._logger)
    #assert os.path.isfile(fname), mcode.ERR_013 % v 
    section[self._tenvsc.ams_control_file]=fname
    return section

  def _chk_circuit_subsection(self, section):
    ''' circuit subsection is not validated with schema. 
        Rather, it is separately validated because it depends on 'model' '''
  
    if section[self._tenvsc.circuit] == {}:
      del section[self._tenvsc.circuit]
      return section
  
    assert section[self._tenvsc.model] == self._tenvsc.model_ams, mcode.ERR_014  % self._tenvsc.model_ams
    for k,v in list(section[self._tenvsc.circuit].items()):
      assert type(v)==str, mcode.ERR_015 % (v,k)
      fname = get_abspath(v, do_assert=False, logger=self._logger)
      #assert os.path.isfile(fname), mcode.ERR_016  % v 
      section[self._tenvsc.circuit][k]=fname
    return section

  def _chk_hdl_files(self, section):
    ''' check hdl files exist and update path'''
    if section[self._tenvsc.hdl_files] == ['']:
      section[self._tenvsc.hdl_files] = []

    for idx, f in enumerate(section[self._tenvsc.hdl_files]):
      assert type(f)==str, mcode.ERR_017 % self._tenvsc.hdl_files
      fname = get_abspath(f, do_assert=False, logger=self._logger)
      #assert os.path.isfile(fname), mcode.ERR_018 % f
      section[self._tenvsc.hdl_files][idx] = fname

    return section

#--------------------------------------------------------------

def _chk_engrtime(value):
  ''' Check if value is time in engr notation like 11ns, 5fs, etc. '''
  time_suffix = 's'
  if not isinstance(value,str) or value[-1] != time_suffix or from_engr(value[:-1]) == None:
    raise VdtTypeError(value)
  return value

def _chk_verilogtime(value):
  ''' Check if value is Verilog timescale format like 1fs, 10fs, 100fs, ... '''
  check_engrtime(value)
  if value[0] == '1' and all(x is '0' for x in value[1:]):
    return value
  else:
    raise VdtValueError(value)

class SchemaTestConfig(SchemaConfig):

  #(_pkg_module_root_dir,dummy_filename) = os.path.split(os.path.abspath(__file__))

  def __init__(self, configobj, logger_id='logger_id'):
    self._tenvf = EnvFileLoc()
    self._tenvs = EnvTestcfgSection()
    self._tenvr = EnvTestcfgOption()
    self._tenvtp = EnvTestcfgPort()
    self._tenvp = EnvPortName()

    self._schema_filename = mproboenv.get_testcfg()
    SchemaConfig.__init__(self, configobj, self._schema_filename, 'test', logger_id)
    self.vdt_errors = self._validate({
                                    'time_engr' : _chk_engrtime,
                                    'time_verilg' : _chk_verilogtime
                                    })
    self._run_custom_check()

  def raise_vdterror(self):
    self._output_vdterror([])

  def _run_custom_check(self):
    for t in list(self.config.keys()):
      self.config[t][self._tenvs.option] = self._chk_regress(self.config[t][self._tenvs.option])
      self.config[t][self._tenvs.port] = self._chk_port(self.config[t][self._tenvs.port])

  def _chk_regress(self, section):
    ''' do_not_progress subsection under regression section 
        it takes/returns the whole regress section
    '''
    if self._tenvr.regression_do_not_regress not in list(section.keys()):
      return section
    
    section[self._tenvr.regression_do_not_regress] = dict([(k,force_list(v)) for k,v in list(section[self._tenvr.regression_do_not_regress].items())])
    return section 
  
  def _chk_port(self, section):
    ''' prohibited, default_value '''
    for k,v in list(section.items()):
      section[k][self._tenvtp.default_value] = self._chk_port_default(section[k])
      #TODO: validate prohibited 
      #try:
      #  section[k][self._tenvtp.prohibited] = self._chk_port_prohibited(section[k])
      #except:
      #  pass
    return section

  def _chk_port_default(self, port):
    ana_port = [self._tenvp.AnalogInput, self._tenvp.AnalogOutput]
    dtype = float if port[self._tenvtp.port_type] in ana_port else int
    return str2num(port[self._tenvtp.default_value], dtype)

