
import datetime

def printToday():
  today = datetime.date.today()
  return datetime.date.today().strftime('%b-%d-%Y').lower()

LOGO_001 = '''
mProbo - Analog/Mixed-Signal Equivalence Checker
                  Version 0.5 - {today}
 Copyright (c) 2016-2018 by Stanford University
               ALL RIGHTS RESERVED


This version is only for evaluation purpose. 
Any redistribution, modification, or commercial 
use is prohibited without written permission.
For more information, contact bclim@stanford.edu

'''

LOGO_002 = '''
mProbo - Generation of Verilog testbench from Virtuoso 
      for Analog/Mixed-Signal Equivalence Checker
                   Version 0.5 - {today}
 Copyright (c) 2016-2018 by Stanford University
               ALL RIGHTS RESERVED


This version is only for evaluation purpose. 
Any redistribution, modification, or commercial 
use is prohibited without written permission.
For more information, contact bclim@stanford.edu

'''

LOGO_003 = '''
mGenero - Analog/Mixed-Signal model generator
                   Version 0.5 - {today}
 Copyright (c) 2016-2018 by Stanford University
               ALL RIGHTS RESERVED


This version is only for evaluation purpose. 
Any redistribution, modification, or commercial 
use is prohibited without written permission.
For more information, contact bclim@stanford.edu

'''
