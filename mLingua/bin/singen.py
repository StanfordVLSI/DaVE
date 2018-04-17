#!/usr/bin/env python
# Generate LUT based sine wave output module
import os
import argparse
import sys
import numpy as np
from pwlgen.pwlgenerator import PWLWaveLUTGenerator

def pass_args():
  ''' args '''
  parser = argparse.ArgumentParser(description='Generate a sine wave stimulus module using a Lookup Table.')
  parser.add_argument('-e', '--etol', help='Error tolerance.', type=float)
  parser.add_argument('-f', '--freq', help='Frequency.', type=float)
  parser.add_argument('-p', '--phase', help='Initial phase in degree.', type=float)
  parser.add_argument('-o', '--offset', help='DC offset.', type=float)
  parser.add_argument('-a', '--amp', help='Amplitude.', type=float)
  parser.add_argument('-m', '--module', help='Module name.', type=str)
  return parser.parse_args()

def main():
  args = pass_args()
  fn = [('const', args.offset), ('sin', args.amp, 2.0*np.pi*args.freq, args.phase/180.*np.pi)]
  pwlgen = PWLWaveLUTGenerator(args.etol, wv_suffix='_%s' % args.module)
  pwlgen.load_fn(fn, 0, 1./args.freq, 1./args.freq/1000)
  pwlgen.generate()
  pwlgen.generate_verilog(args.module)

if __name__=="__main__":
  main()
