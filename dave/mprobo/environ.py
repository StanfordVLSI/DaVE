__doc__ = '''
Read-only meta class to retrieve keywords of mProbo
'''

import os
from configobj import ConfigObj
from . import mproboenv
import copy

def get_checkerconfig():
  ''' get configuration file for the checker keywords '''
  return ConfigObj(infile = copy.deepcopy(mproboenv.envcfg))

''' getmethod() and ROmetaClass() are to make read-only attribute '''
def getmethod(attrname):
  def _getmethod(self):
    return self.__readonly__[attrname]
  
  return _getmethod

class ROmetaClass(type):
  def __new__(cls, classname, bases, classdict):
    readonly = classdict.get('__readonly__',{})
    for name, default in list(readonly.items()):
      classdict[name] = property(getmethod(name))
    return type.__new__(cls, classname, bases, classdict)

class EnvRunArg(object, metaclass=ROmetaClass):
  ''' keywords for argument default value of amschk.py ''' 
  __cfg = get_checkerconfig()
  __readonly__ = __cfg['runarg']

class EnvFileLoc(object, metaclass=ROmetaClass):
  __cfg = get_checkerconfig()
  __readonly__ = __cfg['fileloc']

class EnvFileLoc(object, metaclass=ROmetaClass):
  __cfg = get_checkerconfig()
  __readonly__ = __cfg['fileloc']

class EnvOaTable(object, metaclass=ROmetaClass):
  __cfg = get_checkerconfig()
  __readonly__ = __cfg['oatable']

class EnvTestcfgOption(object, metaclass=ROmetaClass):
  __cfg = get_checkerconfig()
  __readonly__ = __cfg['testcfg']['option']

class EnvTestcfgSection(object, metaclass=ROmetaClass):
  __cfg = get_checkerconfig()
  __readonly__ = __cfg['testcfg']['section']

class EnvTestcfgPort(object, metaclass=ROmetaClass):
  __cfg = get_checkerconfig()
  __readonly__ = __cfg['testcfg']['port']

class EnvTestcfgSimTime(object, metaclass=ROmetaClass):
  __cfg = get_checkerconfig()
  __readonly__ = __cfg['testcfg']['simtime']

class EnvTestcfgTestbench(object, metaclass=ROmetaClass):
  __cfg = get_checkerconfig()
  __readonly__ = __cfg['testcfg']['testbench']

class EnvPortName(object, metaclass=ROmetaClass):
  __cfg = get_checkerconfig()
  __readonly__ = __cfg['portname']

class EnvSimcfg(object, metaclass=ROmetaClass):
  __cfg = get_checkerconfig()
  __readonly__ = __cfg['simcfg']

class EnvSimulatorClassOpt(object, metaclass=ROmetaClass):
  __cfg = get_checkerconfig()
  __readonly__ = __cfg['simulator_cls_opt']

class EnvMisc(object, metaclass=ROmetaClass):
  __cfg = get_checkerconfig()
  __readonly__ = __cfg['misc']
