__doc__ = '''
Interface for Empy templating system.
'''

import em
import os
import re

class EmpyInterface(em.Interpreter):
  ''' 
  Empy interpreter for generating template-based files (e.g. analogcontrol.scs) 
    - src_file: source template
    - dst_file: destination filename
    - param: a dict contains variable/value pairs to put in
  If there are multiple empty lines, those will be replaced with a single empty line
  '''
  def __init__(self, dst_file=''): 
    self._dst_file = dst_file
    self._dst_fid = open(dst_file, 'w')
    em.Interpreter.__init__(self, self._dst_fid, None, em.DEFAULT_PREFIX, None, None, None, None)

  def __call__(self, src_file, param):
    try:
      self.updateGlobals(param)
      if type(src_file) == type(''):
        with open(src_file, 'r') as f:
          self.file(f)
      else:
        self.file(src_file)
    finally:
      self.shutdown()
      self._dst_fid.close()
    with open(self._dst_file, 'rt') as f:
      c = f.read()
    # replace multiple empty lines with a single empty line
    with open(self._dst_file, 'w') as f:
      f.write(re.sub(r'[\r\n][\r\n]{2,}', '\n\n', c)) 
    return os.path.abspath(self._dst_file)
