__doc__ = '''
Read-only meta class to retrieve keywords of mProbo
'''

import os
from configobj import ConfigObj
import mproboenv
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
    for name, default in readonly.items():
      classdict[name] = property(getmethod(name))
    return type.__new__(cls, classname, bases, classdict)

class EnvRunArg(object):
  ''' keywords for argument default value of amschk.py ''' 
  __metaclass__ = ROmetaClass
  __cfg = get_checkerconfig()
  __readonly__ = __cfg['runarg']

class EnvFileLoc(object):
  __metaclass__ = ROmetaClass
  __cfg = get_checkerconfig()
  __readonly__ = __cfg['fileloc']

class EnvFileLoc(object):
  __metaclass__ = ROmetaClass
  __cfg = get_checkerconfig()
  __readonly__ = __cfg['fileloc']

class EnvOaTable(object):
  __metaclass__ = ROmetaClass
  __cfg = get_checkerconfig()
  __readonly__ = __cfg['oatable']

class EnvTestcfgOption(object):
  __metaclass__ = ROmetaClass
  __cfg = get_checkerconfig()
  __readonly__ = __cfg['testcfg']['option']

class EnvTestcfgSection(object):
  __metaclass__ = ROmetaClass
  __cfg = get_checkerconfig()
  __readonly__ = __cfg['testcfg']['section']

class EnvTestcfgPort(object):
  __metaclass__ = ROmetaClass
  __cfg = get_checkerconfig()
  __readonly__ = __cfg['testcfg']['port']

class EnvTestcfgSimTime(object):
  __metaclass__ = ROmetaClass
  __cfg = get_checkerconfig()
  __readonly__ = __cfg['testcfg']['simtime']

class EnvTestcfgTestbench(object):
  __metaclass__ = ROmetaClass
  __cfg = get_checkerconfig()
  __readonly__ = __cfg['testcfg']['testbench']

class EnvPortName(object):
  __metaclass__ = ROmetaClass
  __cfg = get_checkerconfig()
  __readonly__ = __cfg['portname']

class EnvSimcfg(object):
  __metaclass__ = ROmetaClass
  __cfg = get_checkerconfig()
  __readonly__ = __cfg['simcfg']

class EnvSimulatorClassOpt(object):
  __metaclass__ = ROmetaClass
  __cfg = get_checkerconfig()
  __readonly__ = __cfg['simulator_cls_opt']

class EnvMisc(object):
  __metaclass__ = ROmetaClass
  __cfg = get_checkerconfig()
  __readonly__ = __cfg['misc']
