__doc__ = '''
Class and functions for model calibration

TODO:
  - Support PWL-segmented test
'''

import yaml
import os
import re
from .environ import EnvFileLoc
from .linearregression import LinearRegressionSM
from dave.common.misc import flatten_list



class LinearModelParameter(object):
  '''
    mProbo extracts linear models so as to back-annotate the coefficients of the models
    into analog functional models.
    This LinearModelParameter class provides an interface to 
      - save the extracted linear models using mProbo
      - allow other script to read the saved file
      - provide a function to read out a coefficient of the extracted models
  '''
  _default_filename = EnvFileLoc().extracted_model_param_file
  def __init__(self):
    self._param = {}

  def save_model_parameters(self, workdir):
    ''' save model parameters to a file in YAML 
        - workdir: working directory to save model parameters
    '''
    with open(self._get_model_param_filename(workdir), 'w') as f:
      f.write(yaml.dump(self._param, default_flow_style=False))

  def load_model_parameters(self, lm_file):
    ''' load model parameters in YAML '''
    with open(os.path.abspath(lm_file), 'r') as f:
      self._param = yaml.load(f)

  def get_param(self):
    return self._param

  def formulate_model_parameters(self, testname, res):
    ''' reformulate extracted linear model coefficients in mProbo 
        Not support PWL segmented tests yet
    '''
    if testname not in list(self._param.keys()):
      self._param[testname] = {}
    for r in res:
      for e in r[2]['lr_formula_suggested']:
        for k,v in list(LinearRegressionSM.extract_coef_from_lr_formula(e).items()):
          if k in list(self._param[testname].keys()):
            self._param[testname][k].append({'mode':dict(list(r[0].items())), 'coef':v})
          else:
            self._param[testname][k]=[{'mode':dict(list(r[0].items())), 'coef':v}]

  @classmethod
  def get_default_filename(cls):
    ''' return a default filename that holds extracted model parameters '''
    return cls._default_filename

  def _get_model_param_filename(self, workdir):
    return os.path.join(workdir, self.get_default_filename())

  def show_param_in_yaml(self):
    return yaml.dump(self._param)

  def get_lm_coef(self, testname, dv, iv, mode={'dummy_digitalmode':0}):
    if dv in list(self._param[testname].keys()):
      for v in self._param[testname][dv]:
        if v['mode']==mode:
          if iv in list(v['coef'].keys()):
            return v['coef'][iv]
          else:
            return None
      return None
    else:
      return None

  def get_terms(self, testname, dv, mode={'dummy_digitalmode':0}):
    ''' return a list of terms for dependent variable dv '''
    if dv in list(self._param[testname].keys()):
      for v in self._param[testname][dv]:
        if v['mode']==mode:
          return list(v['coef'].keys())
      return None
    else:
      return None

  def get_lm_equation(self, testname, dv, iv_list, mode={'dummy_digitalmode':0}):
    _port = [iv[0] for iv in iv_list]
    _varl = [iv[1] for iv in iv_list]
    _terms = self.get_terms(testname, dv, mode)
    _coefs = [self.get_lm_coef(testname, dv, iv, mode) for iv in _terms]
    def get_unit_terms(term):
      ''' extact variables. For example, ctl1*ctl2 will produce [ctl1,ctl2] '''
      return [f for f in term.split('*') if len(f) >0 and f[0].isalpha()]
    all_terms = sorted(list(set(flatten_list([get_unit_terms(t) for t in _terms]))-set(['offset'])))
    assert list(set(all_terms)-set(_port))==[], 'Lack of terms in get_lm_equation'
    equation = ' + '.join(['%s*%s' %(str(_coefs[i]),t) if t!='offset' else str(_coefs[i]) for i,t in enumerate(_terms)]).replace('+-','-')+';'
    for i,v in enumerate(_port):
      equation = re.sub(r'\b%s\b' % v, _varl[i], equation)
    return equation
    

def main():
  metric = 'zero'
  mode = {'dummy_digitalmode':0}
  ifile = '/home/bclim/proj/DaVE/mssmodel/sandbox/cteq/.mProbo/extracted_linear_model.yaml'
  mp = LinearModelParameter()
  mp.load_model_parameters(ifile)
  print(mp.show_param_in_yaml())
  print(mp.get_lm_equation('test1', metric,[('ibias','ibias_r'),('ctl1','ctl1_r'),('vcm','vcm_r')],mode))

if __name__ == "__main__":
  main()
  
