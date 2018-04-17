#!/usr/bin/env python
# Take LTI system transfer function in terms of poles and zeros
# Show the corresponding symbolic expression in time domain

import os
import sys
import argparse
from pwlgen.pwlmisc import pass_args, read_cfg
from pwlgen.txf2tran import Txf2Tran

"""
Configuration example

# Take LTI system transfer function in terms of poles and zeros
# Show the corresponding symbolic expression in time domain

# configuration file example for tf2tr.py

#####################################
# Determine the input is ramp or step
#####################################
in_type = 'pwl' # 'real' or 'pwl'


#########################################################################
# RESERVED SYMBOLs
#########################################################################
# Pre-define symbols in symbolic expression
# 'si' is reserved for signal step input.
# 'si_a' and 'si_b' are reserved for signal offset/slope of a ramp input.
# 't' and 's' are variables in time and s-domain, respectively.

###############################
# Define Transfer function (TF)
# TF = numerator/denumerator
###############################
numerator= 's'
denumerator= '(s+p1)'
"""

def main():
  args = pass_args('Print out an analytic equation of a transient response for given s-domain transfer function expression.', 'cfg_tf.py')
  cfg = read_cfg(args.config)
  equation = Txf2Tran(cfg['numerator'], cfg['denumerator'], cfg['in_type'])

if __name__ == "__main__":
  main()
