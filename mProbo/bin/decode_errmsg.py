#!/usr/bin/env python

import os
import traceback

msg = 'Model checking is completed'

edc = lambda ss,cc: ''.join(chr(ord(s)^ord(c)) for s,c in zip(ss,cc*1000))
with open('.mProbo_dump.log','r') as f:
  lines = f.readlines()

print edc(''.join(lines), msg)
