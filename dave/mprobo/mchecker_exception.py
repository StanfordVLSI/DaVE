
import sys                  # sys
import warnings             # warnings
import traceback            # traceback

# exception classes

class MCheckerError(Exception):
  """ error exception """
  pass
class MCheckerWarning(Warning):
  """ warning exception """
  pass

def mchk_warning(msg):
  """ issue a warning message """

  (type, value, tb) = sys.exc_info()
  traceback.print_tb(tb, 3)
  warnings.warn(msg, category=MCheckerWarning, stacklevel=2)
