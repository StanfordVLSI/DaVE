import yaml
from dave.common.misc import merge_list, flatten_list
import dave.mprobo.mchkmsg as mcode

__doc__ = '''
  This primitive.py contains classes relevant to processing Verilog primitive modules
'''

#---------------------------
class WireCrossReference(object):
  '''
    WireCrossReference class will parse a port reference file. An example file is 
    ${DAVE_SAMPLES}/mProbo/port_xref.cfg which is written in yaml.
    
    It is intended to find out the data type of an implicitly-declared wire. 
      - to draw a testbench in Cadence's Virtuoso and export it to mProbo test configuration
      - to automatically delare wire type instead of having explicit wire section in mProbo
    
    User can define a port reference file which contains
      - a map between port and its wire type in each module
      - a default wire type

    In a port reference file, the signal type of ports are declared where its rule in YAML 
    is as follows.

    default_wiretype : logic
    module:
      modulename1:            # module name is "modulename1"
        portname1: pwl        # port name : signal discipline
        portname2: logic   
      modulename2:
        portname1: logic 
        portname2: real 
    
    In each module (e.g. modulename1, modulename2), the default signal type is declared in 'default_wiretype' field. For example, the default wire type is 'logic' in the above case.

    Note that 'default_wiretype' and its value should be declared in a port reference file; otherwise, it outputs an error.
  '''
  
  DEF_WIRE_KEY = 'default_wiretype'  # key for default wire type field
  MODULE_KEY   = 'module'            # key for Verilog module field

  def __init__(self, xref_filename=None):
    ''' xref_filename: wire type cross-reference filename in YAML '''
    if xref_filename:
      self.load(xref_filename)

  def load(self, filename):
    ''' load wire type cross-reference file '''
    with file(filename, 'r') as f:
      cfg = yaml.load(f)
    self._assert_default(cfg, filename)
    self._extract_info(cfg)

  def get_default_wiretype(self):
    ''' return a default wire type '''
    return self._default

  def get_all_wiretype(self):
    ''' return a list of available wire type '''
    return self._all

  def get_wiretype(self, cellname, portname):
    ''' get a wire type of a port in a cell '''
    try:
      return self._map[cellname][portname]
    except:
      return None

  def _assert_default(self, cfg, filename):
    ''' assert if default wire type exists '''
    assert self.DEF_WIRE_KEY in list(cfg.keys()), mcode.ERR_019 % (self.DEF_WIRE_KEY, filename)

  def _extract_info(self, cfg):
    ''' extract wire cross-reference info '''
    self._default = self._extract_default(cfg)
    self._map = self._extract_map(cfg)
    self._all = self._extract_all_wiretype(cfg)

  def _extract_default(self, cfg):
    ''' default wire info '''
    return cfg[self.DEF_WIRE_KEY]

  def _extract_map(self, cfg):
    ''' (port vs. wire type) cross-reference info '''
    return cfg[self.MODULE_KEY]

  def _extract_all_wiretype(self, cfg):
    ''' extract all wire types '''
    _wiretypes = list(set(flatten_list([list(v.values()) for k,v in list(self._map.items())])))
    return list(set(merge_list(_wiretypes, [self._default])))
#---------------------------
