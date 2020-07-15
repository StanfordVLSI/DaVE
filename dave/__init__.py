import os

DAVE_INST_DIR = os.path.dirname(os.path.dirname(__file__))
env = os.environ
env['DAVE_INST_DIR'] = str(DAVE_INST_DIR)
env['mLINGUA_DIR'] = str(os.path.join(DAVE_INST_DIR, 'mLingua'))

