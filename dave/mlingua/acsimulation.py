#!/usr/bin/env python
import numpy as np
import os
import subprocess
import matplotlib.pylab as plt
from empyinterface import EmpyInterface

class RunACSimulation(object):
  _tb_filename = 'test.v'
  _ac_template = os.path.abspath(os.path.join(os.environ['mLINGUA_INST_DIR'], 'pwlgen/resource', 'ac_template.empy'))
  _dc_template = os.path.abspath(os.path.join(os.environ['mLINGUA_INST_DIR'], 'pwlgen/resource', 'dc_template.empy'))

  def __init__(self, param):
    self._param = param

  def get_param(self):
    return self._param

  def run(self):
    param = self._param
    if 'start_time' not in param.keys():
      param['start_time'] = 0.0
    param.update({'out_op': self.__run_dc(param)})
    freq  = param['frequency_span']
    out = []
    for f in freq:
      param.update({'ac_frequency': f})
      meas = self.__runsim(param)
      print 'Frequency, %s = %e, %e' %(param['signal_out'], f, meas)
      out.append(meas)
    return freq, np.array(out)
  
  def __run_dc(self, param):
    op = self.__runsim(param, ac=False)
    print 'DC operating point of %s=%e' %(param['signal_out'], op)
    return op

  def __runsim(self, param, ac=True):
    template = self._ac_template if ac else self._dc_template
    EmpyInterface(self._tb_filename)(template, param)
    p = subprocess.Popen('make', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    meas = np.loadtxt('meas_ac.txt') if ac else np.loadtxt('meas_dc.txt')
    return meas

  @classmethod
  def postprocess(cls, freq, meas, param):
    gain = np.abs(meas/param['sine_amp'])
    gaindB = 20*np.log10(gain)
    np.savetxt("acsim_data.txt", (freq, gain)) # save measurement data
    return gaindB

  @classmethod
  def plot(cls, freq, gaindB, param):
    plt.semilogx(freq, gaindB, 'o-')
    plt.xlabel('Frequency [Hz]')
    plt.ylabel('Gain [dB]')
    plt.title(param['plot_title'])
    plt.savefig(param['plot_filename'])
    if param['show_figure']:
      plt.show()
