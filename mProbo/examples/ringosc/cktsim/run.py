#!/usr/bin/env python

from readmeas import readmeas
import subprocess
import pylab as plt

def read_sim():
  res  = readmeas('sim.mt0')
  vreg   = res.get_array('vreg')
  freq   = res.get_array('frequency')
  plt.plot(vreg,freq,'x-')
  plt.savefig('f_vs_vreg.png')
  plt.close()

def main():
  
  cached = False
  # Run circuit simulation 
  if not cached:
    p=subprocess.Popen('make', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err  = p.communicate()
    sim_msg = out + '\n' + err
  if cached or 'hspice job concluded' in sim_msg:
    print 'Circuit simulation is done !!!'
    read_sim()
  else:
    print sim_msg 
    print 'Circuit simulation is unsuccessful !!!'

if __name__=="__main__":
  main()
