from .amschkschema import SchemaSimulatorConfig
from .environ import EnvSimcfg
from .environ import EnvTestcfgOption, EnvTestcfgSection
from dave.common.davelogger import DaVELogger
from dave.common.checkeval import ehdnsxmgor
from .configobjwrapper import ConfigObjWrapper
import os
import sys
from dave.common.misc import get_abspath, interpolate_env, featureinfo
import dave.mprobo.mchkmsg as mcode

#-------------------------------------------------------------------------
class SimulatorConfig(object):
  ''' Read simulator configuration from a file(cfg_filename) 
      Configuration set-up is the same across all the tests
  '''
  def __init__(self, cfg_filename, is_goldenonly=False, logger_id='logger_id'):
    assert os.path.isfile(get_abspath(cfg_filename)), mcode.ERR_002 %cfg_filename
    self._tenv = EnvSimcfg()
    self.config = self._read_config_file(cfg_filename)

    self._inv = not ehdnsxmgor(featureinfo())


    # Validate and update
    schema_simcfg = SchemaSimulatorConfig(self.config, is_goldenonly)
    schema_simcfg.raise_vdterror()
    self.config = schema_simcfg.get_cfg()

    self._golden_sim_config = SimulatorConfigModel(self.config[self._tenv.golden], True, logger_id=logger_id)
    self._revised_sim_config = SimulatorConfigModel(self.config[self._tenv.revised], False, logger_id=logger_id)
    self._characterization = SimulatorConfigCharacterization(self.config[self._tenv.characterization], logger_id=logger_id)

    if self._inv: dlrtmvkdldjem()

  def get_golden(self):
    return self._golden_sim_config

  def get_revised(self):
    return self._revised_sim_config

  def get_sweep(self):
    return self.get_golden().get_sweep() and self.get_revised().get_sweep()

  def get_characterization(self):
    return self._characterization

  def _read_config_file(self,cfg_filename):
    ''' read configuration file and process default section if exists '''
    cfg_instance = ConfigObjWrapper(cfg_filename, self._tenv.default)
    return cfg_instance.get_cfg()

#-------------------------------------------------------------------------
class SimulatorConfigCharacterization(object):
  def __init__(self, sim_cfg, logger_id='logger_id'):
    self._tenv = EnvSimcfg()
    self._tenvr = EnvTestcfgOption()
    self._tenvs = EnvTestcfgSection()
    self._cfg = sim_cfg 

  def get_process_file(self):
    return self._cfg[self._tenv.process_file]

  def get_mc_samples(self):
    return self._cfg[self._tenv.mc_samples]

  def get_vlog_param_samples(self):
    return self._cfg[self._tenv.vlog_param_samples]

  def get_vlog_param_file(self):
    return self._cfg[self._tenv.vlog_param_file]

  def get_global_variation(self):
    return self._cfg[self._tenv.global_variation]

  def get_regression(self):
    return self._cfg[self._tenvs.regression]

  def get_regression_min_sample(self):
    return self.get_regression()[self._tenvr.min_sample]

  def get_regression_oa_depth(self):
    return self.get_regression()[self._tenvr.analog_level]

  def get_regression_method(self):
    return self.get_regression()[self._tenvr.regression_method]

  def get_regression_pval_threshold(self):
    return self.get_regression()[self._tenvr.pval_threshold]

  def get_rsq_threshold(self):
    return self._cfg[self._tenv.rsq_threshold]

#-------------------------------------------------------------------------
class SimulatorConfigModel(object):
  '''
    class defining simulator options for both golden and revised models
  '''
  def __init__(self, sim_cfg, is_golden,logger_id='logger_id'):
    self._logger = DaVELogger.get_logger('%s.%s.%s' % (logger_id, __name__, self.__class__.__name__)) # logger
    self._tenv = EnvSimcfg()
    self.cfg_model = sim_cfg # get the corresponding section from the sim configuration
    self._is_golden = is_golden
  
  def get(self):
    return self.cfg_model

  def is_golden(self):
    ''' is this config golden ? '''
    return self._is_golden

  def get_config_name(self):
    return self._tenv.golden if self.is_golden() else self._tenv.revised

  def get_simulator_name(self):
    return self.cfg_model[self._tenv.simulator]

  def get_model(self):
    return self.cfg_model[self._tenv.model]

  def get_simulator_option(self):
    ''' return HDL simulator option '''
    return interpolate_env(self.cfg_model[self._tenv.simulator_option], self._logger)
  
  def get_ncams_connrules(self):
    ''' return ams connrules '''
    return interpolate_env(self.cfg_model[self._tenv.ams_connrules], self._logger)

  def get_hdl_files(self):
    ''' return a list of Verilog files '''
    return [interpolate_env(s, self._logger) for s in self.cfg_model[self._tenv.hdl_files]]

  def get_hdl_include_files(self):
    ''' return a list of files being included using `include directive '''
    return [interpolate_env(s, self._logger) for s in self.cfg_model[self._tenv.hdl_include_files]]

  def get_circuits(self):
    ''' return dictionary {circuit name:filename} for circuit netlist '''
    try:
      return dict([(k, interpolate_env(v, self._logger)) for k, v in list(self.cfg_model[self._tenv.circuit].items())]) 
    except:
      return None

  def get_spice_lib(self):
    ''' return spice lib definition '''
    try:
      return interpolate_env(self.cfg_model[self._tenv.splib], self._logger)
    except:
      return None

  def change_circuit(self, cktname, filename):
    ''' change circuit info 
        This is for fault simulator
    '''
    try:
      self.cfg_model[self._tenv.circuit][cktname]=filename
    except:
      pass

  def get_ams_control_filename(self):
    try:
      return interpolate_env(self.cfg_model[self._tenv.ams_control_file], self._logger)
    except:
      return None

  def get_sweep(self):
    ''' return sweep_file field, default is True '''
    return self.cfg_model[self._tenv.sweep_file]

def dlrtmvkdldjem():
  sys.exit()
