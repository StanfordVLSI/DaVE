# Wrapper of ConfigObj

___doc__ = """
A wrapper of ConfigObj module to support "DEFAULT" section feature. 
Somehow, ConfigObj doesn't recognize "default". So make sure that the default section name is all upper case."
"""

from configobj import ConfigObj
import copy
from dave.common.misc import assert_file

class ConfigObjWrapper(object):
  ''' 
    This is a wrapper of ConfigObj to provide [DEFAULT] section; ConfigObj doesn't support it.
    It reads a configuration file in ConfigObj format, merge each section with [DEFAULT] section if exists, and then [DEFAULT] section is removed.
    Note that the section name, DEFAULT, is case sensitive for unknown reason.
  '''
  def __init__(self, cfg_filename, default_name):
    '''
      This merges each section with DEFAULT section
      - cfg_filename: CfgObj filename
      - default_name: default section name
    '''
    assert_file(cfg_filename, strict=False)
    self._cfg = ConfigObj(cfg_filename)
    section = self._get_section_list(self._cfg)
    section1 = self._get_section_list_exclude_default(section, default_name)
    try: # merge each section with [DEFAULT] section
      for p in section1:
        _tmp_cfg = copy.deepcopy(self._get_section(default_name))
        _tmp_cfg.merge(self._get_section(p))
        self._cfg[p] = copy.deepcopy(_tmp_cfg)
      del self._cfg[default_name]
    except:
      pass

  def _get_section_list(self, cfgobj):
    ''' return a list of section names '''
    return cfgobj.keys()

  def _get_section_list_exclude_default(self, section, default_name):
    ''' return a list of section names except 'default_name' '''
    return filter(lambda x:x.lower() not in [default_name], section)

  def _get_section(self, name):
    ''' return a section's contents by name '''
    return self._cfg[name]

  def get_cfg(self):
    ''' return CfgObj object '''
    return self._cfg
