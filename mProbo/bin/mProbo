#!/usr/bin/env python

import logging
import sys
from dave.mprobo.launcher import launch, pass_args
from dave.mprobo.environ import EnvFileLoc, EnvMisc

__doc__ = ''' mProbo launcher in stand-alone mode [c.f. mProbo_server(client).py] '''

# logger
logging.basicConfig(filename=EnvFileLoc().debug_file,
                  filemode='w',
                  level=logging.DEBUG)
logger = logging.getLogger(EnvMisc().logger_prefix)
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.INFO)
logger.addHandler(ch)

def main():
  args = pass_args().parse_args() # get command-line arguments
  launch(args, csocket=None) # launch application

if __name__ == "__main__":
  main()
