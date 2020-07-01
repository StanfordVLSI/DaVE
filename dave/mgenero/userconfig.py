
__doc__ = '''
process user configuration 
'''

import sys
import copy
from dave.mgenero.interface import Interface
from dave.common.misc import read_yaml, generate_random_str
from collections import OrderedDict
from configobj import ConfigObj



#-------------------------------------------------------------
class UserConfiguration(object):
  ''' This will read a user configuration file and validate the configuration against its interface file.
      terminology:
        - user interface : leaf cell interface customized by a user
  '''
  def __init__(self, cfg_filename, ifc_filename, template_rootdir, logger=None):
    self.logger = logger
    # read template interface
    self.ifc = Interface.load(ifc_filename) 
    # read user interface file and override the existing template configuration
    self.cfg = read_yaml(cfg_filename, 
                          { Interface.key_pins:OrderedDict(), 
                            Interface.key_metrics:OrderedDict(), 
                            Interface.key_tparams:OrderedDict(), 
                            Interface.key_mparams:OrderedDict(),
                            Interface.key_tspecs:OrderedDict(),
                        }) 

    # run validation
    self.cfg_validated = {'template_rootdir': template_rootdir}
    self.cfg_validated.update({self.ifc.key_tname: self._validate_template_name()})
    self.cfg_validated.update({self.ifc.key_mname: self._validate_module_name()})
    self.cfg_validated.update({self.ifc.key_pins: self._validate_pins()})
    self.cfg_validated.update({self.ifc.key_metrics: self._validate_metrics()})
    self.cfg_validated.update({self.ifc.key_mparams: self._validate_modelparams()})
    self.cfg_validated.update({self.ifc.key_tparams: self._validate_testparams()})
    self.testcfg_filename, testspec = self._generate_test_cfg()
    self.cfg_validated.update({self.ifc.key_tspecs: testspec})

  def get_config(self):
    ''' return a user validated configuration to model creation class '''
    return self.cfg_validated
  
  def get_testcfg_filename(self):
    # test configuration filename that describes test port specifications
    return self.testcfg_filename

  def _validate_template_name(self):
    key = self.ifc.key_tname
    tname = self.ifc.get_template_name()
    self.logger.info('[INFO] Template name is %s.' % tname)
    return tname

  def _validate_module_name(self):
    key = self.ifc.key_mname
    mname = self.cfg[key] if key in self.cfg else self.ifc.get_module_name()
    self.logger.info('[INFO] Module name is set to %s.' % mname)
    return mname

  def _validate_pins(self):
    p_ifc = self.ifc.pins_to_dict()
    p_usr = self.cfg[self.ifc.key_pins]
    # temperary fix
    for k,v in list(p_usr.items()):
      if 'is_pinonly' not in list(v.keys()):
        p_usr[k]['is_pinonly'] = False
    # categorize the types of pins
    essential_pins = sorted([p for p in list(p_ifc.keys()) if not p_ifc[p]['is_optional']])
    optional_pins = sorted(list(set(p_ifc.keys()) - set(essential_pins)))
    user_pins = sorted([p for p in list(p_usr.keys()) if p not in list(p_ifc.keys())])
    missing_ess_pins_usr = sorted([p for p in essential_pins if p not in list(p_usr.keys())])
    missing_opt_pins_usr = sorted([p for p in optional_pins if p not in list(p_usr.keys())])
    valid_optional_pins = sorted(list(set(optional_pins) - set(missing_opt_pins_usr)))
    pinonly_user_pins = sorted([p for p in user_pins if p_usr[p]['is_pinonly']])

    self.logger.info("[INFO-PIN] Essential pins are %s." % essential_pins)
    self.logger.info("[INFO-PIN] Valid optional pins are %s." % valid_optional_pins)
    self.logger.info("[INFO-PIN] User-defined pins are %s." % user_pins)
    self.logger.info("[INFO-PIN] User-defined pins with 'is_pinonly'==True are %s." % pinonly_user_pins)
    if len(missing_ess_pins_usr)>0:
      self.logger.info("[WARN-PIN] Essential pins not listed in the user configuration are %s. Their informations are retrieved from the interface." % missing_ess_pins_usr)
    if len(missing_opt_pins_usr)>0:
      self.logger.info("[WARN-PIN] Optional pins in an interface which are not listed in a user configuration are %s. These are automatically set to invalid pins" % missing_opt_pins_usr)

    #pins = {}
    p_ifc1 = copy.deepcopy(p_ifc) # temp copy that p_ifc changes after updating pins
    pins = OrderedDict()
    for p in essential_pins:
      pins.update({p:p_ifc1[p]})
      if p in list(p_usr.keys()): pins[p].update(p_usr[p])
    for p in valid_optional_pins:
      pins.update({p:p_ifc1[p]})
      pins[p].update(p_usr[p])
      if 'is_pinonly' not in list(pins[p].keys()):
        pins[p].update({'is_pinonly':False})
    for p in user_pins:
      pins.update({p:p_usr[p]}) # A user pin is also an optional pin
      pins[p].update({'is_optional': True}) # A user pin is also an optional pin
      if 'vectorsize' not in list(pins[p].keys()):
        pins[p].update({'vectorsize':1})
    valid_pins = sorted(pins.keys())
    self.logger.info("[INFO-PIN] Valid pins are %s." % valid_pins)
    self.logger.debug('Validated pins:' + str(pins))

    # check essential pins that vectorization is not allowed
    #invalid_vector_pins = [p for p in essential_pins if p_ifc[p]['datatype'] != 'logic' and p_ifc[p]['vectorsize'] == 0 and pins[p]['vectorsize'] > 1]
    invalid_vector_pins = [p for p in essential_pins if p_ifc[p]['vectorsize'] < 1 and pins[p]['vectorsize'] > 1]
    if len(invalid_vector_pins) != 0:
      self.logger.error("[ERROR-PIN] Invalid vectorization of essential pins (%s) is detected. The program will be terminated" % invalid_vector_pins)
      sys.exit()

    return pins

  def _validate_metrics(self):
    m_ifc = self.ifc.metrics_to_dict()
    m_usr = self.cfg[self.ifc.key_metrics] 

    available_metrics = list(m_ifc.keys())
    defined_metrics = list(m_usr.keys())
    undefined_metrics = list(set(available_metrics)-set(defined_metrics))
    invalid_metrics = list(set(defined_metrics)-set(available_metrics))
    valid_metrics = list(set(defined_metrics)-set(invalid_metrics))
    self.logger.info("[INFO-METRIC] Valid metrics are %s." % valid_metrics)
    self.logger.info("[WARN-METRIC] Invalid metrics are %s. These will be ignored" % invalid_metrics)
    self.logger.info("[WARN-METRIC] Undefined metrics in the user configuration are %s. These will not be incorporated in the model" % undefined_metrics)

    metrics = {}
    for m in valid_metrics:
      metrics.update({m:m_ifc[m]})
      metrics.update({m:m_usr[m]})
      if len(m_ifc[m]['value'])>0 and m_usr[m]['value'] not in m_ifc[m]['value']:
        self.logger.info("[WARN-METRIC] Value in the metric '%s' (%s) is not valid value. Check out both the user configuration and its interface !" % (m, m_usr[m]['value']))
    self.logger.debug('Validated metrics:' + str(metrics))
      
    return metrics

  def _validate_modelparams(self):
    p_ifc = self.ifc.modelparams_to_dict()
    p_usr = self.cfg[self.ifc.key_mparams]
    params = copy.deepcopy(p_ifc)
    params = OrderedDict(list(params.items()))
    p_usr_only = list(set(p_usr.keys())-set(p_ifc.keys()))
    params.update(OrderedDict([(p, p_usr[p]) for p in p_usr]))

    self.logger.info("[INFO-MODELPARAM] Model parameters from the interface are %s." % list(p_ifc.keys())) 
    self.logger.info("[INFO-MODELPARAM] User-defined model parameters are %s." % p_usr_only) 
    return params

  def _validate_testparams(self):
    p_ifc = self.ifc.testparams_to_dict()
    p_usr = self.cfg[self.ifc.key_tparams]
    params = copy.deepcopy(p_ifc)
    p_usr_only = list(set(p_usr.keys())-set(p_ifc.keys()))
    params.update(dict([(p, p_usr[p]) for p in p_usr]))

    self.logger.info("[INFO-TESTPARAM] Test parameters from the interface are %s." % list(p_ifc.keys())) 
    self.logger.info("[INFO-TESTPARAM] User-defined test parameters are %s." % p_usr_only) 
    return params

  def _generate_test_cfg(self):
    # it doesn't do validation
    # it just spit out what's in the user configuration
    # it's validation is done after test generation is done in ModelCreator.generate_test
    p_usr = self.cfg[self.ifc.key_tspecs]
    filename = generate_random_str('mgenero_', 5) + '.cfg'
    cfg = ConfigObj()
    cfg.filename = filename
    params = copy.deepcopy(p_usr)
    for k,v in list(params.items()):
      cfg[k] = {'port': v}
    cfg.write()
    return filename, params
