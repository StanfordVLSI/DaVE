__doc__ = '''
Linear regression of sampled analog responses
'''

import numpy as np 
import os
import copy
import re
import statsmodels.formula.api as sm
import pandas as pd
from itertools import product, combinations, groupby
from operator import itemgetter

from dave.common.davelogger import DaVELogger
from environ import EnvTestcfgOption
from dave.common.misc import flatten_list
import dave.mprobo.mchkmsg as mcode

#------------------------------------------------------------------------
class LinearRegression(object):
  '''Parent class of linear regression in this module''' 

  def __init__(self, logger_id='logger_id'):
    ''' 
    '''
    self._logger = DaVELogger.get_logger('%s.%s.%s' % (logger_id, __name__, self.__class__.__name__))
    self._tenv = EnvTestcfgOption()
    self._option = {self._tenv.regression_do_not_regress : {}, 
                     self._tenv.regression_basis : self._tenv.polynomial,
                     self._tenv.regression_order : 1, 
                     self._tenv.regression_pval_threshold : 0.05, 
                     self._tenv.regression_cint_threshold : 0.95, 
                     self._tenv.regression_en_interact : False,
                     self._tenv.regression_sval_threshold : 0.01
                    }

  def update_option(self, option):
    ''' update option & do_not_regress dict '''
    self._option.update(option)
    if self._tenv.regression_do_not_regress in option.keys():
      self.regression_do_not_regress.update(option[self._tenv.regression_do_not_regress])

  def load_data(self, dv, iv, option={}):
    ''' 
      load dependent & independent variables and their data as well as linear regression option
        - dv: a dict of dependent variables
        - iv: a dict of independent variables
        - option: same dict as self._option
    '''
    self.dv = dv
    self.iv = iv
    self.quantizedport_name = option['qaport_name']
    self.regression_do_not_regress = dict([(x,[x]) for x in self.dv.keys()]) # one could not be a predictor variable of oneself.
    self.update_option( {self._tenv.regression_do_not_regress : self.regression_do_not_regress} )
    self.update_option(option)
    self.dv_iv_map = self._make_dv_iv_map(self.dv.keys(), self.iv.keys(), self.regression_do_not_regress)
    self.binary_iv = self._get_binary_predictors(self.iv) 
    #self.iv = dict(self.iv.items() + self.dv.items()) # output could be a predictor of another output


  def _get_binary_predictors(self, iv):
    ''' Get iv with binary data type ''' 
    return [k for k,v in iv.items() if filter(lambda x: float(x) not in [1.0,0.0], v)==[]]

  def _make_dv_iv_map(self, dv_item, iv_item, do_not_regress):
    ''' Create a mapping between dep. var and indep. var 
        Return a dict where 
        { dep.var : list of indep. vars for linear regression }
        do_not_regress : a dict defines list of indep. vars for each dep. var
                         to exclude for linear regression
    '''
    dv_item = sorted(dv_item)
    iv_item = sorted(iv_item)
    return dict([ (p,filter(lambda v: v not in do_not_regress[p], iv_item)) for p in dv_item ])


  def _make_formula(self, dv_iv_map, basis, order, en_interact, user_model):
    ''' Make a R formula without the output variable and '~'
          - e.g.) If the R model is y~x1 + x2 + x3 + I(x1^2) + I(x2^2) + ...,
                  this returns 'x1 + x2 + x3 + I(x1^2) + I(x2^2) + ...'
        For now, only 'polynomial' as basis is allowed
        This will use user-provided model if exists. 
          - Otherwise, all polynomial terms up to the 'order' arg 
            and  the first order interaction terms between iv's
    '''
    formula = {}
    for dv in dv_iv_map.keys(): # for each output
      if dv in user_model.keys(): # user-provided model if exists
        formula[dv] = user_model[dv] 
        if formula[dv] == '': # if user model is NULL
          formula[dv] = '1'
        continue
      elif not dv_iv_map[dv]: # list is empty; it's possible only to have an offset term
        formula[dv] = '1'
      else: # generate full terms
        formula[dv] = self._gen_full_terms(dv_iv_map[dv], order, en_interact)
    return formula
  

  def _gen_full_terms(self, dv_iv, order, en_interact):
    ''' generate all terms of an equation '''
    for p in range(order):
      if p == 0: # 1st order term
        term = ['%s' % v for v in dv_iv]
        if len(dv_iv) > 1 and en_interact == True: # add interact terms between predictors
          interact = filter(lambda x: x[0] != x[1], list(product(dv_iv, dv_iv)))
          term = term+[ self._interact_R(x[0], x[1]) for x in interact 
                        if re.sub(r'_\d+$','',x[0]) != re.sub(r'_\d+$','',x[1]) ]
      else: # higher order term
        bin_exclude = list(set(dv_iv)-set(self.binary_iv)) # no poly for binary variable
        term = term + [ self._polynomial_R(v, p+1) for v in bin_exclude ]
    return '+'.join( term )


  def _interact_R(self, x0, x1):
    ''' interact term expression in R '''
    return '%s:%s' % (x0, x1)


  def _polynomial_R(self, x, n):
    ''' polynomial expression  in R '''
    return 'I(%s**%s)' % (x, n)


#------------------------------------------------------------------------
class LinearRegressionSM(LinearRegression):
  ''' Linear regression using "statsmodels" package '''
  
  def __init__(self, port_handler, logger_id='logger_id'):
    ''' 
      TODO: How to extract covariance
    '''
    LinearRegression.__init__(self, logger_id)
    self._ph = port_handler

    # dict of functions for getting some linear model properties
    self.stat_func = {
      'residuals'     : lambda x: getattr(x, 'resid').values,
      'std_residuals' : lambda x: np.std(getattr(x, 'resid').values),
      'r_sq'          : lambda x: getattr(x, 'rsquared'),
      'adjusted_r_sq' : lambda x: getattr(x, 'rsquared_adj'),
      'confidence_interval'      : lambda x: getattr(x, 'conf_int')(1.0-self._option[self._tenv.regression_cint_threshold]).values.reshape(-1,2),
      'coefficient'   : lambda x: np.column_stack(( 
                                  getattr(x,'params').values,
                                  getattr(x,'bse').values,
                                  getattr(x,'tvalues').values,
                                  getattr(x,'pvalues').values
                                  ))
    }

    # dict of functions for getting properties related to gain cocefficent
    self.stat_coef_func = { 
      'coef_gain'       : lambda coefficients: coefficients[:,0], 
      'coef_std_err'    : lambda coefficients: coefficients[:,1], 
      'coef_t_statistic': lambda coefficients: coefficients[:,2], 
      'coef_p_value'    : lambda coefficients: coefficients[:,3] 
                                           }
  def run(self):
    ''' Run OLS linear regression '''
    self._create_model(ignore_usermodel=False)

  def suggest_model_using_sensitivity(self):
    '''
      After doing linear regression (run()), one may want to call this function to see which terms are significant
      Select terms from a full expansion list by observing the Normalized Input Sensitivity (NIS) in [%]
      NIS >= threhold in [%]
    '''
    threshold = self._option[self._tenv.regression_sval_threshold]
    norm_s = self.get_normalized_sensitivity()
    dv = self.get_response()
    predictors = self.get_predictors()
    self.dv_iv_map = dict( [(d, [p for i, p in enumerate(predictors[d]) if i != 0 and abs(norm_s[d][i]) >= threshold]) for d in dv] ) # don't check offset
    return self._make_suggested_formula(self.dv_iv_map)

  def suggest_model_using_abstol(self, is_simple=False):
    '''
      After doing linear regression using cls.suggest_model_using_sensitivity()
      filter out terms where gain*input_range is less than abstol.
      THIS CURRENTLY WORKS ONLY FOR A SINGLE PREDICTOR RESPONSE if is_simple is False
      THIS CAN'T HANDLE POLYNOMIAL and MULTIPLICATION !!!!
    '''
    predictors = self.get_predictors()
    self.dv_iv_map = {}
    for d in self.get_response():
      self.dv_iv_map[d] = []
      abstol = self._ph.get_by_name(d).abstol
      if len(predictors[d]) < 3 or is_simple:
        for i,p in enumerate(predictors[d]):
          if i!= 0:
            port = self._ph.get_by_name(p)
            _scale = port.scale if port else 1.0
            if abs(self.get_coef(d,p)*_scale) >= abstol:
              self.dv_iv_map[d].append(p)
      else:
        self.dv_iv_map[d] = predictors[d][1:]
        
    return self._make_suggested_formula(self.dv_iv_map)

  def suggest_model_using_confidence_interval(self):
    ''' Like suggest_model_using_sensitivity() function, this will filter out predictores with the user provided confidence intervals that the extracted gain terms embraces 0.0 which means that the term is insiginificant for given confidence interval
    '''
    self.dv_iv_map = self._filterout_insignificant_predictors_by_confidence_interval()
    return self._make_suggested_formula(self.dv_iv_map)


  def _make_suggested_formula(self, dv_iv_map):
    ''' make formula from given terms '''
    return dict( [(d, '+'.join(dv_iv_map[d])) for d in dv_iv_map.keys()] )

  def _create_model(self, ignore_usermodel=False):
    # write formula of regression model
    if ignore_usermodel: # ignore user model
      opt_formula = ('polynomial', 1, True, {})
    else:
      opt_formula = self._get_model_build_option()

    formula = self._make_formula(self.dv_iv_map, *opt_formula)
    self._logger.debug(mcode.WARN_017 % formula)

    # run regression
    self.iv_ols, self.model_ols, self.df_ols, self.exog, self.endog, self.xnames = self._run_regression(formula) 
    self._formula = formula

    # build/get statistics from the linear regression model, and calculate normalized input sensitivity
    self.ols_stat = self._build_statistics(self.model_ols) 
    self._normalized_sensitivity = dict( [(k, calculate_normalized_sensitivity(self.get_predictors()[k], self, self.ols_stat, k)) for k in self.dv_iv_map.keys()] )

  def get_normalized_sensitivity(self):
    return self._normalized_sensitivity

  def get_formula(self):
    return self._formula


  def get_statistics(self):
    try:
      return getattr(self,'ols_stat')
    except:
      return None

  def get_predictors(self):
    ''' return a list of predictors of linear regression models '''
    try: 
      return getattr(self,'iv_ols')
    except:
      return None

  def get_coefs(self):
    ''' return coefficents of linear regression models '''
    try: 
      return self.get_statistics()['coef_gain']
    except:
      return None

  def get_residuals(self, response):
    try:
      return self.get_statistics()['residuals'][response]
    except:
      return None

  def is_confidence_interval_embrace_zero(self, response, predictor):
    ''' check if confidence interval of the predictor variable for the response embrace 0.0 '''
    _dv_iv = self.get_predictors()
    idx = _dv_iv[response].index(predictor)
    _confint = self.get_statistics()['confidence_interval'][response][idx]
    if _confint[0]*_confint[1] <= 0.0:
      return True
    else:
      return False

  def get_coef(self, response, predictor):
    idx = self.get_predictors()[response].index(predictor)
    return self.get_coefs()[response][idx]

  def get_max_residuals(self):
    ''' return max residuals '''
    try: 
      _residue = self.get_statistics()['residuals']
      return dict([(r,max(abs(_residue[r]))) for r in _residue.keys()])
    except:
      return None

  def get_adjusted_r_sqs(self):
    try:
      return self.get_statistics()['adjusted_r_sq']
    except:
      return None

  def get_std_residuals(self):
    ''' return rms residuals '''
    try: 
      _residue = self.get_statistics()['residuals']
      return dict([(r,np.std(_residue[r])) for r in _residue.keys()])
    except:
      return None

  def get_intercept_name(self):
    return 'Intercept'

  def get_intercept(self, response):
    try:
      return self.get_coef(response, self.get_intercept_name())
    except:
      return None

  def _filterout_insignificant_predictors_by_confidence_interval(self):
    ''' 
      Check confidence intervals and remove any predictor embraces 0.0 in the interval because it is insignificant contributor
    '''
    _dv_iv = self.get_predictors()
    for k in _dv_iv.keys():
      _confint = self.get_statistics()['confidence_interval'][k]
      remove_items = []
      for idx,p in enumerate(_dv_iv[k]):
        if _confint[idx][0]*_confint[idx][1] <= 0.0 or p==self.get_intercept_name():
          remove_items.append(p)
          self._logger.debug(mcode.DEBUG_017 % (p, k))
      _dv_iv[k] = [ p for p in _dv_iv[k] if p not in remove_items ]
    return _dv_iv

  def export_data(self, csvfile):
    ''' export samples of linear regression models to a csv file '''
    getattr(self, 'df_ols').to_csv(csvfile)

  def get_response(self):
    ''' return a dict of { dependepnt variable : data samples } '''
    return self.dv

  def get_response_name(self):
    ''' return the names of responses in alphabetical order'''
    return sorted(self.get_response().keys())

  def get_summary(self):
    ''' get model summary of statsmodels OLS '''
    return dict([(k,self.short_summary(v.summary())) for k,v in getattr(self,'model_ols').items()])

  def short_summary(self, summary, short=True):
    ''' rip off unnecessary report '''
    text = summary.as_text()
    text_splitted = text.split('\n')
    for idx, t in enumerate(text_splitted):
      if t.startswith('Omni'): 
        break
    text_splitted = text_splitted[:idx]
    text_splitted[-1] = '='*len(text_splitted[-2])
    return '\n'.join(text_splitted)

  def get_predicted_response(self):
    ''' get predicted response from the extracted models '''
    mdl = getattr(self, 'model_ols')
    return dict([ (k, v.predict()) for k,v in mdl.items() ])

  def print_model_summary(self):
    ''' I made this function because printing model_summary is too verbose '''
    model=getattr(self,'model_ols')
    try:
      for mdl in model.values():
        self._logger.info('\n')
        self._logger.info(self.short_summary(mdl.summary()))
    except:
      self._logger.warn(mcode.WARN_018)

  def print_formula(self, quite=False):
    ''' print formula from linear regression '''
    model=getattr(self,'model_ols')
    try:
      for mdl in model.values():
        if not quite:
          self._logger.info(self._build_formula_from_lr(mdl))
        else:
          self._logger.debug(self._build_formula_from_lr(mdl))
    except:
      if not quite:
        self._logger.warn(mcode.WARN_018)
      else:
        self._logger.debug(mcode.WARN_018)

  def get_lr_formulas(self):
    try:
      model=getattr(self,'model_ols')
      return [self._build_formula_from_lr(mdl) for mdl in model.values()]
    except:
      return None

  def _build_formula_from_lr(self, model):
    ''' build a linear equation from linear regression result '''
    dv = model.model.formula.split('~')[0]
    pv = model.params.keys()
    pv_expanded = list(set(flatten_list([s.split(':') for s in pv]))) # list of expanded predictors
    qa_expanded = [s for k in self.quantizedport_name for s in pv_expanded if re.match(k+'_\d$', s)] # find terms quantized analog
    coef = model.params.values
    terms = ['%e*%s' %(coef[i], self._change_R_power_to_Vlog_power(pv[i]).replace(':','*')) for i in range(len(pv))]
    terms[0] = terms[0].split('*')[0]
    expr = dv+' = '+' + '.join(terms) #+';'
    for q in qa_expanded: # change _\d$ with [\d]
      k = q.rfind('_')
      if self._ph.get_by_name(q[:k]).bit_width == 1: # if bit-width ==1, replace x[0] with x
        expr = expr.replace(q,q[:k])
      else:
        expr = expr.replace(q, q[:k]+'['+q[k+1:]+']')
    return expr
        
  @classmethod
  def extract_coef_from_lr_formula(cls, expr):
    ''' For model calibration, 
        This function will extract 1) response name, 2) each predictor terms and coefficients, from a linear regression expression generated by self.__build_formula_from_lr()
    '''
    formula = expr.split('=')
    dv = formula[0].strip()
    terms = formula[1].split(' + ')
    predictors = {}
    
    for t in terms:
      f = t.strip().split('*', 1) # split with the first occurence of '*'
      coef = float(f[0])
      try:
        pv = f[1]
      except:
        pv = 'offset'
      predictors[pv] = coef
    return dict([(dv, predictors)])

  def _change_R_power_to_Vlog_power(self, pv):
    ''' replace power term expr in R to expr in Verilog '''
    return pv.replace('I(','').replace(')','').replace(' ** ','**')

  def _get_model_build_option(self):
    ''' Return options needed for building a linear model expression'''
    opt = self._option[self._tenv.regression_basis], self._option[self._tenv.regression_order], self._option[self._tenv.regression_en_interact]
    try:
      user_model = self._option[self._tenv.regression_user_model]
      return opt + (user_model,)
    except:
      return opt + ({},)

  def _run_regression(self, formula):
    ''' Run linear regressions for each dependent variable 
        model = {} # key: dep. var, value : regression model instance
        predictors = {} # key: dep. var, value: list of variables in the formula
    '''
    df = pd.DataFrame(dict(self.iv.items()+self.dv.items())) # data frame in pandas
    model = dict([ (dv, sm.ols(formula='%s ~ %s' %(dv, formula[dv]), data=df).fit()) for dv in self.dv_iv_map.keys() ])
    predictors = dict([ (dv, list(model[dv].params.keys())) for dv in self.dv_iv_map.keys() ])
    exog  = dict([ (dv, model[dv].model.data.orig_exog) for dv in self.dv_iv_map.keys() ])
    endog = dict([ (dv, model[dv].model.data.orig_endog) for dv in self.dv_iv_map.keys() ])
    xnames = dict([ (dv, model[dv].model.data.xnames) for dv in self.dv_iv_map.keys() ])
    return predictors, model, df, exog, endog, xnames

  def _build_statistics(self, model):
    ''' returns statistical inference of regression models '''
    stat = dict([ (p, dict([ (x, fn(y)) for x, y in model.items() ])) for p, fn in self.stat_func.items() ])
    stat.update( dict([ (i, dict([(x, fn(stat['coefficient'][x])) for x in model.keys()])) for i, fn in self.stat_coef_func.items() ]) )
    return stat

  def get_combinations(self, predictors, iv_key):
    '''
      predictors: {} where a key is an output response
                           value is a list of predictor variables including 'Intercept'
                           it contains all higher polynomial terms & interaction terms while iv_key is a list that only contains the input variables.
      * Assumption
        - all the output responses should have a full term expansion, which means that the predictor variables are the same
        - if a bit of quantized port is included, the corresponding bits of the port should also be included
    '''
    comb = []
    intercept = [self.get_intercept_name()]
    _pvar = predictors[predictors.keys()[0]]
    for i in range(len(iv_key)-1):
      for subset in combinations(iv_key, i):
        qa_in_subset = [k for s in subset for k in self.quantizedport_name if re.match(k+'_\d$', s)]
        subset = list(subset) + [k for k in iv_key for q in qa_in_subset if re.match(q+'_\d$', k)]
        subset = list(set(subset))
        if len(subset)>0:
            full_subset = [p for s in subset for p in _pvar if re.search(s,p) != None]
            fs = sorted(subset + full_subset)
            fs = [fs[i] for i in range(len(fs)) if i==0 or fs[i] != fs[i-1]] # remove duplicates
            comb.append(sorted(fs))
    comb.append(list(set(_pvar)-set(intercept)))
    comb.sort()
    comb = sorted(comb, key=lambda x: len(x), reverse=True) # sort by no of items
    comb = [comb[i] for i in range(len(comb)) if i==0 or comb[i] != comb[i-1]] # remove duplicates
    return comb

def calculate_normalized_sensitivity(predictors, lr, stat, response):
  ''' calculate normalized sensitivity of each predictor to the response '''
  exog = get_exog(lr, response)
  norm_sensitivity=[]
  gain = get_gain(stat, response)
  xnames = get_xnames(lr, response)
  norm_sensitivity = np.array([ gain[i]*np.std(exog[x]) for i, x in enumerate(predictors) if i != 0])
  norm_sensitivity = 100.0*norm_sensitivity/np.sum(norm_sensitivity)
  return [None] + [ n for n in norm_sensitivity ]


def get_xnames(lr, response):
  try:
    return lr.xnames[response]
  except:
    return None

def get_endog(lr, response):
  try:
    return lr.endog[response]
  except:
    return None

def get_exog(lr, response):
  try:
    return lr.exog[response]
  except:
    return None

def get_gain(stat, response):
  try:
    return stat['coef_gain'][response]
  except:
    return None

def get_intercept(stat, response):
  try:
    return stat['coef_gain'][response]
  except:
    return None

def get_all_gain(stat):
  try:
    return stat['coef_gain']
  except:
    return None

def get_gain_p_value(stat, response):
  try:
    return stat['coef_p_value'][response]
  except:
    return None

def get_r_sq(stat, response):
  try:
    return stat['r_sq'][response]
  except:
    return None

def get_all_r_sq(stat):
  try:
    return stat['r_sq']
  except:
    return None

def get_adjusted_r_sq(stat, response):
  try:
    return stat['adjusted_r_sq'][response]
  except:
    return None

def get_all_adjusted_r_sq(stat):
  try:
    return stat['adjusted_r_sq']
  except:
    return None

def get_confidence_interval(stat):
  try:
    return stat['confidence_interval']
  except:
    return None

def get_all_coef_p_value(stat):
  try:
    return stat['coef_p_value']
  except:
    return None

def get_residuals(stat, response):
  try:
    return stat['residuals'][response]
  except:
    return None

def get_all_residuals(stat):
  try:
    return stat['residuals']
  except:
    return None

def get_sigma_residuals(stat, response):
  try:
    return stat['std_residuals'][response]
  except:
    return None
