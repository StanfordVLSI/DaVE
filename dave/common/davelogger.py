__doc__ = '''
DaVE logger
'''

import logging

class DaVELogger(object):
  @classmethod
  def get_logger(kls, name):
    logger = logging.getLogger(name)
    return logger
