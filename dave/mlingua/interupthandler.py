# keyboard interrupt handler

import signal
import time

def handler(signum, frame):
  print 'Here you go'

#signal.signal(signal.SIGINT, handler)
#time.sleep(10) # Press Ctrl+c here
