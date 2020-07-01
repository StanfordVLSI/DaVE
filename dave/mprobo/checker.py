#

import numpy as np
import texttable

from dave.common.davelogger import DaVELogger
from dave.common.misc import get_absmax, to_engr
import dave.mprobo.htmlamschk as ht

__doc__ = '''
Checker for model comparison.
'''

# color code 
result_colors = {
  'success':'lime',
  'failure':'red',
  'warning':  'yellow',
  'normal' : 'white' }

def err_code(error):
  return '*error*' if error == 'failure' else '*warning*' if error == 'warning' else ''

def generate_check_summary_table(result):
  ''' generate table instance of checking summary '''
  idx = 0
  x = [[]]
  tab = texttable.Texttable(max_width=132)
  for res in result:
    for r in sorted(res[1][0][-1].keys()):
      for m in res[1]:
        x.append([idx, res[0], r, m[0], err_code(m[1][r]), err_code(m[2][r])])
        idx += 1
  tab.add_rows(x)
  tab.set_cols_align(['r', 'c', 'c', 'c', 'c', 'c'])
  tab.header(['Index', 'Test', 'Output', 'Digital mode', 'Simple pin consistency check', 'Model accuracy check'])
  return tab

class UnitChecker(object):
  ''' Micro checker for comparing linear models (golden vs. revised) '''

  def __init__(self, stol, logger_id=0):
    self._logger = DaVELogger.get_logger('%s.%s.%s' % (logger_id, __name__, self.__class__.__name__)) # logger

    self._stol = stol # input sensitivity tolerance

  @property
  def lrg(self): # golden model object
    return self._lrg

  @property
  def lrr(self): # revised model object
    return self._lrr

  @property
  def ph(self): # port handler object
    return self._ph

  @property
  def stol(self): # input sensitivity tolerance
    return self._stol

  @property
  def residue_g2g(self): # residue (predict(golden) - sim(golden))
    return self._residue_g2g

  @property
  def residue_r2r(self): # residue (predict(revised) - sim(revised))
    return self._residue_r2r

  @property
  def residue_g2r(self): # residue (predict(golden) - sim(revised))
    return self._residue_g2r

  @property
  def residue_r2g(self): # residue (predict(revised) - sim(golden))
    return self._residue_r2g

  def run(self, lrg, lrr, ph, is_pincheck=False): # load golden/revised models to be compared
    self._lrg = lrg # golden model object
    self._lrr = lrr # revised model object
    self._ph  = ph  # port handler object

    self._cross_validation()
    return self.compare(is_pincheck)

  def compare(self, is_pincheck): 
    ''' compare golden model with revised model '''
    result = dict()
    for dv in self.lrg.get_response_name(): # for each response variable
      # get port spec.
      abstol  = self.ph.get_by_name(dv).abstol # absolute tolerance
      gtol = self.ph.get_by_name(dv).gaintol # gain error tolerance

      predictors = self.lrg.get_predictors()[dv] # predictor variables for dv

      # gain error
      gain_g = [self.lrg.get_coef(dv, p) for p in predictors] 
      gain_r = [self.lrr.get_coef(dv, p) for p in predictors]
      gain_err = [self._get_rel_error(gain_g[i],gain_r[i]) for i in range(len(gain_g))] # gain error

      # normalized sensitivity of predictors
      s_g = list(map(self._format_s, self.lrg.get_normalized_sensitivity()[dv]))
      s_r = list(map(self._format_s, self.lrr.get_normalized_sensitivity()[dv]))

      # max and stdvar of residual errors
      max_res_g = get_absmax(self.residue_g2g[dv])
      std_res_g = np.std(self.residue_g2g[dv])
      max_res_r = get_absmax(self.residue_r2r[dv])
      std_res_r = np.std(self.residue_r2r[dv])
      max_res_g2r = get_absmax(self.residue_g2r[dv])
      std_res_g2r = np.std(self.residue_g2r[dv])
      max_res_r2g = get_absmax(self.residue_r2g[dv])
      std_res_r2g = np.std(self.residue_r2g[dv])

      # compare gain matrix (pin check mode only) and build the table
      errflag_pin, gain_tbl = self._compare_gain(gtol, self.stol, gain_g, gain_r, gain_err, s_g, s_r, is_pincheck)

      # compare residual errors (model accuracy mode) and build the table
      errflag_residue, res_tbl_max, res_tbl_std = self._build_residue_table(abstol, max_res_g, max_res_r, max_res_g2r, max_res_r2g, std_res_g, std_res_r, std_res_g2r, std_res_r2g)
      result[dv] = {
                    'predictors': predictors,
                    'err_flag_pin': errflag_pin,
                    'err_flag_residue': errflag_residue,
                    'gain_table': gain_tbl,
                    'residue_table_max': res_tbl_max,
                    'residue_table_std': res_tbl_std
                   }
    return result


  def _compare_gain(self, gtol, stol, gain_g, gain_r, gain_err, s_g, s_r, is_pincheck):
    ''' Compare gains (elementwise) and build gain matrix.
      Rules:
      - Flag errors in the gain matrix will be done only if this is pin check 
        mode("is_pincheck")
        a. Fill the cell with warn color if gain sensitivity (both golden 
           and revised) is smaller than input sensitivity threshold
        b. Fill the cell with error color if either the sign of gains 
           (golden, revised) are different or the gain error is larger 
           than gain tolerance ("gtol"). 
        c. Offset won't be checked (automatically filtered by rule a)
      - Only build gain table if (not "is_pincheck")
    '''
    # rules
    rule_a = lambda x: abs(float(x)) < stol
    rule_b = lambda gg, gr, ge: ((abs(float(gg)*float(gr))<=0.0) and (abs(float(gg))+abs(float(gr)))>0) or abs(ge) > gtol

    # compare
    gtbl = []
    gtbl.append(gain_g)
    gtbl.append(gain_r)
    gtbl.append(gain_err)
    gtbl.append(s_g)
    gtbl.append(s_r)

    err_flag_pin = 'success'
    n_term = len(gtbl[0]) # number of terms
    for i in range(n_term): # for each gain term
      if is_pincheck:
        try: # it is possible the value is 'N/A'
          if i > 0: # rule c
            # do (gain) elementwise comparison
            if all(map(rule_a, [gtbl[3][i],gtbl[4][i]])): # rule a
              col = 'warning' # both sensitivies are below stol
            elif rule_b(gtbl[0][i],gtbl[1][i],gtbl[2][i]): # rule b
              col = 'failure'
              err_flag_pin = 'failure'
            else:
              col = 'normal'
          else: 
            col = 'normal'
        except:
          col = 'warning'
          err_flag_pin = 'warning'
      else:
        col = 'normal'
      gtbl[0][i] = ht.TableCell(to_engr(gtbl[0][i]), bgcolor=result_colors[col]) # gain (golden)
      gtbl[1][i] = ht.TableCell(to_engr(gtbl[1][i]), bgcolor=result_colors[col]) # gain (revised)
      gtbl[2][i] = ht.TableCell('%.1f' % gtbl[2][i] if gtbl[2][i]<=100.0 else '> 100.0') 

    return err_flag_pin, gtbl

  def _build_residue_table(self, abstol, max_g, max_r, max_g2r, max_r2g, std_g, std_r, std_g2r, std_r2g):
    ''' build table of residual errors (cross-validation result) 
        Complain error if any of cells has an error.
    '''
    form = lambda x: to_engr(x) if abs(x) <= abstol else ht.TableCell(to_engr(x), bgcolor=result_colors['failure']) # cell format
    residue_max = [['', '', 'Extracted', 'Extracted'],
                   ['', '', 'Golden', 'Revised'],
                   ['Simulated', 'Golden', '', ''],
                   ['Simulated', 'Revised', '', '']] # max residuals
    residue_std = [['', '', 'Extracted', 'Extracted'],
                   ['', '', 'Golden', 'Revised'],
                   ['Simulated', 'Golden', '', ''],
                   ['Simulated', 'Revised', '', '']] # stdvar residuals
    try:
      # error summary
      err_flag = 'failure' if any([abs(x) > abstol for x in [max_g, max_r, std_g, std_r, max_r2g, max_g2r, std_r2g, std_g2r]]) else 'success'
      # fill cell
      residue_max[2][2] = form(max_g)
      residue_max[3][3] = form(max_r)
      residue_std[2][2] = form(std_g)
      residue_std[3][3] = form(std_r)

      residue_max[2][3] = form(max_r2g)
      residue_max[3][2] = form(max_g2r)
      residue_std[2][3] = form(std_r2g)
      residue_std[3][2] = form(std_g2r)

    except:
      err_flag = 'failure'
      for i in range(2,4):
        for j in range(2,4):
          residue_max[i][j] = ht.highlight('N/A', bgcolor=result_colors['failure'])
          residue_std[i][j] = ht.highlight('N/A', bgcolor=result_colors['failure'])

    return err_flag, residue_max, residue_std

  def _cross_validation(self):
    ''' cross validation of simulated responses with predicted models
          - simulated (golden) vs. predicted (revised), and vice versa
    '''
    try:
      est_g = self.lrg.get_predicted_response()
      sim_g = self.lrg.get_response() 
      est_r = self.lrr.get_predicted_response()
      sim_r = self.lrr.get_response() 

      # calculate residues
      residue_g2g = dict([(k,v-sim_g[k]) for k,v in list(est_g.items())])
      residue_r2r = dict([(k,v-sim_r[k]) for k,v in list(est_r.items())])
      residue_g2r = dict([(k,v-sim_r[k]) for k,v in list(est_g.items())])
      residue_r2g = dict([(k,v-sim_g[k]) for k,v in list(est_r.items())])

    except: # don't remember which creates an error
      residue_g2g = None
      residue_r2r = None
      residue_g2r = None
      residue_r2g = None

    self._residue_g2g = residue_g2g
    self._residue_r2r = residue_r2r
    self._residue_g2r = residue_g2r
    self._residue_r2g = residue_r2g


  def _get_rel_error(self, v1, v2): # calculate relative error of two values
    if v1*v2==0.0:
      return np.inf if (v1+v2) != 0.0 else 0.0
    else:
      return int(max(abs((v2-v1)/v1*100), abs((v2-v1)/v2*100))*10)/10.0

  def _format_s(self, val): # format sensitivity value
    try:
      return '%.1f' % float(val)
    except:
      return 'N/A'


