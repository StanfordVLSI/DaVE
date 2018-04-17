# Miscellaneous routines
import os
import argparse
import sys

def pass_args(description, cfgfile_default):
  ''' args for a configuration file '''
  parser = argparse.ArgumentParser(description=description)
  parser.add_argument('--ghktdjvn', action='store_true', help=argparse.SUPPRESS)
  parser.add_argument('config', nargs='?', default=cfgfile_default, help='Configuration file. Default is "%s"' % cfgfile_default)
  return parser.parse_args()

def read_cfg(cfg_file):
  ''' read a configuration file and return variables as dict '''
  dirname, basename = os.path.split(cfg_file)
  if dirname == '':
    sys.path.append(os.getcwd()) 
  else:
    sys.path.append(dirname)
  cfg = os.path.splitext(basename)[0] # get verification scirpt file name w/o ext
  try:
    __import__(cfg) # import the cfg file 
  except:
    print '[Error] Check out the configuration file %s.py' %cfg
    sys.exit()
  __cfg = sys.modules[cfg] # get cfg module handle
  return dict([(k,getattr(__cfg, k)) for k in dir(__cfg) if not k.startswith('__')])
