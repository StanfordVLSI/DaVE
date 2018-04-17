# make tool logos

with open('../VERSION','r') as f:
  __version__ = f.read().strip()
with open('../LICENSOR','r') as f:
  __licenser__ = f.read().strip()
with open('../CONTACT','r') as f:
  __contact__   = f.read().strip()
with open('../YEAR','r') as f:
  __year__ = f.read().strip()

evalcopy_msg = '''
This version is only for evaluation purpose. 
Any redistribution, modification, or commercial 
use is prohibited without written permission.
For more information, contact {contact}
'''.format(contact=__contact__)

code = """
import datetime

def printToday():
  today = datetime.date.today()
  return datetime.date.today().strftime('%b-%d-%Y').lower()

LOGO_001 = '''
mProbo - Analog/Mixed-Signal Equivalence Checker
                  Version {version} - {{today}}
 Copyright (c) {year} by {licenser}
               ALL RIGHTS RESERVED

{copymsg}
'''

LOGO_002 = '''
mProbo - Generation of Verilog testbench from Virtuoso 
      for Analog/Mixed-Signal Equivalence Checker
                   Version {version} - {{today}}
 Copyright (c) {year} by {licenser}
               ALL RIGHTS RESERVED

{copymsg}
'''

LOGO_003 = '''
mGenero - Analog/Mixed-Signal model generator
                   Version {version} - {{today}}
 Copyright (c) {year} by {licenser}
               ALL RIGHTS RESERVED

{copymsg}
'''
""".format(copymsg=evalcopy_msg, version=__version__, licenser=__licenser__, year=__year__)

with open('../dave/common/davemsg.py','w') as f:
  f.write(code)
