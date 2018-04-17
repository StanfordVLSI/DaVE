# Generate checking report in PDF

import numpy as np
import copy
import operator
from dave.common.misc import to_engr, add_column_list, get_absmax, get_letter_index
import linearregression as lr
import htmlamschk as ht
from dave.common.davelogger import DaVELogger
from environ import EnvTestcfgPort, EnvSimcfg, EnvPortName
from dave.mprobo.checker import UnitChecker

# color code 
result_colors = \
    {'success':'lime',
     'failure':'red',
     'warning':  'yellow',
     'normal' : 'white'}

class ReportGenerator(object):
  def __init__(self, filename='result.html', logger_id=0):
    self._logger = DaVELogger.get_logger('%s.%s.%s' % (logger_id, __name__, self.__class__.__name__)) # logger
    self._logger_id = logger_id

    # system reserved words
    self._tenvtp = EnvTestcfgPort()
    self._tenvsc = EnvSimcfg()
    self._tenvpn = EnvPortName()

    self.fid = open(filename,'w') # report output in html

  def render(self):
    pass


  ###############
  # Report header
  ###############
  def print_report_header(self, testnames, cwd, workdir, rundir, testcfg_filename, simcfg_filename, rpt_filename):
    ''' load/print report header information 
        - testnames: all the test names
        - cwd: current directory
        - workdir: working directory
        - rundir: workdir/.mProbo
        - testcfg_filename: test configuration filename
        - simcfg_filename: simulator configuration filename
        - rpt_filename: report filename
    '''
    self.heading('Model Checking Summary', 1)
    self.line_break()
    self.heading('List of Tests', 2)
    self.list( [self.link(t, t) for t in testnames] )
    self.heading('Test file information', 2)
    self.list( ['Current directory: %s' % cwd, 
                'Working directory: %s' % workdir, 
                'Simulation run directory: %s' % rundir, 
                'Test configuration file: %s' % testcfg_filename, 
                'Simulation configuration file: %s' % simcfg_filename, 
                'Report file: %s' % rpt_filename, 
               ] )


  ########################
  # Basic test information
  ########################
  def print_testname(self, testname):
    ''' print a test name '''
    self.line_break()
    self.heading(ht.highlight('Test name: "%s"' % testname, bgcolor='yellow'), 2, testname)

  def print_test_info(self, dut_name, test_description):
    ''' print test brief information '''
    self.heading('1. Test information', 3)
    self.heading(self.underline('Device-under-Test'), 4)
    self.write('  : ' + dut_name)
    self.line_break()
    self.heading(self.underline('Description'), 4)
    self.write('  : ' + '<br>'.join(test_description.lstrip('\n').splitlines()))
    self.line_break()
    self.line_break()

  def load_porthandler_obj(self, port_h_obj):
    ''' load PortHandler class instance which will be used
        - to print out port summary
        - retrieve tolerance information
    '''
    self._ph = port_h_obj

  def print_port_info(self):
    ''' report port information '''
    self.heading('2. Port information', 3)

    analog = self._ph.get_analog() # analog port obj
    digital = self._ph.get_digital() # digital port obj

    if len(analog) != 0: # if analog port exists
      self.heading(self.underline('Analog port'), 4)
      self._print_port_table(analog, 'analog')
    if len(digital) != 0: # if digital port exists
      self.heading(self.underline('Digital port'), 4)
      self._print_port_table(digital, 'digital')
      self.text("Note: the auomatically generated prohibited codes due to encoding style are not shown in this report")
    self.line_break()
    self.line_break()

  def _print_port_table(self, port, signaltype = 'analog'):
    ''' build port information table of either analog or digital ports '''
    common_header = ['Name', 'Port type', 'Description']
    analog_header = common_header + ['Absolute Tolerance', 'Gain tolerance [%]', 'Upper bound', 'Lower bound', 'Pinned to']
    digital_header = common_header + ['Bit width', 'Prohibited code', 'Encode', 'Pinned to']
    
    header = analog_header if signaltype=='analog' else digital_header

    tbl = []
    for p in port:
      ptype = getattr(self._tenvpn, p.__class__.__name__.replace('Port','Label'))
      pinned_value = str(p.pinned_value) if p.is_pinned else '-'
      _tmp_tbl = [ p.name, ptype, p.description ]
      if signaltype == 'analog':
        try:
          abstol = '%g' % float(p.abstol)
          gaintol = '%g' % float(p.gaintol)
        except:
          abstol = '-'
          gaintol = '-'
        _tmp_tbl += [abstol , gaintol, p.ub, p.lb, pinned_value]
      else:
        _tmp_tbl += [p.bit_width, str(p.prohibited).replace('[','').replace(']',''), p.encode, pinned_value]
      tbl.append([str(t) for k, t in enumerate(_tmp_tbl)])

    tbl.sort(key=operator.itemgetter(0)) # sort with port name in alphabetical order

    # write a table about port information
    self.table(tbl, header, ['center']*len(header))



  #####################################
  # Regression results of all the modes
  #####################################
  def print_testmode_title(self, testname, modes, modetexts):
    ''' print section title, create hyperlink for each mode '''
    modelist = [self.link(modetexts[i], self.make_testmode_link(testname, m)) for i, m in enumerate(modes)]
    self.heading('3. Checking results for each mode configured by digital input port(s)', 3)
    self.heading(self.underline('List of configuration modes'), 4)
    self.list(modelist)

  @classmethod
  def make_testmode_link(cls, testname, mode):
    ''' make a hyperlink of a configuration mode '''
    _mode = sorted(mode.items())
    return '_'.join([testname]+['%s%s' % (k,str(v)) for k,v in _mode])

  def print_testmode(self, index, testmode, linkid):
    ''' Print header of each configuration mode '''
    self.heading(ht.highlight(self.underline('Configuration mode: %s' % testmode), color='blue', bgcolor='yellow'), 4, linkid)

  def build(self, expand_qanalog, suggest):
    return self._print_regression_result(expand_qanalog, suggest)

  def load_regression_result(self, lrg_simple, lrr_simple, lrg, lrr, lrg_sgt_simple, lrr_sgt_simple, lrg_sgt, lrr_sgt):
    self._lrg_simple = lrg_simple
    self._lrr_simple = lrr_simple
    self._lrg = lrg
    self._lrr = lrr
    self._lrg_sgt_simple = lrg_sgt_simple
    self._lrr_sgt_simple = lrr_sgt_simple
    self._lrg_sgt = lrg_sgt
    self._lrr_sgt = lrr_sgt

    chkr = UnitChecker(self._sensetol, self._logger_id)
    
    self._result_simple = chkr.run(lrg_simple, lrr_simple, self._ph, True)
    self._result_simple_suggested = chkr.run(lrg_sgt_simple, lrr_sgt_simple, self._ph, True)
    self._result_accurate_init   = chkr.run(lrg, lrr, self._ph, False)
    self._result_accurate_suggested = chkr.run(lrg_sgt, lrr_sgt, self._ph, True)

    self._err_flag_pin = dict([ (k, v['err_flag_pin']) for k,v in self._result_simple_suggested.items() ])
    self._err_flag_residual = dict([ (k, v['err_flag_residue']) for k,v in self._result_accurate_suggested.items() ])

  def is_pin_error(self):
    return self._err_flag_pin

  def is_residual_error(self):
    return self._err_flag_residual

  def print_regression_result(self):
    for idx, dv in enumerate(self._result_simple.keys()): # for each response variable
      self.heading('%s. Output response: %s' % (get_letter_index(idx+1, upper=True), dv), 4)

      # pin consistency report
      self.heading('%s. Pin consistency check: ' % get_letter_index(1, upper=False) + ht.highlight(self._err_flag_pin[dv],bgcolor=result_colors[self._err_flag_pin[dv]]), 4)
      self.heading(self.underline('Gain matrix'), 5)
      self._print_gain_matrix( self._result_simple[dv]['gain_table'], self._result_simple[dv]['predictors'], self._lrg_sgt_simple.get_summary()[dv], self._lrr_sgt_simple.get_summary()[dv])

      # model accuracy report
      self.heading('%s. Pin consistency & Model accuracy check: ' % get_letter_index(2, upper=False) + ht.highlight(self.is_residual_error()[dv],bgcolor=result_colors[self.is_residual_error()[dv]]), 4)
      self.heading(self.underline('Cross model validation'), 5)
      self._print_cross_model_validation(self._result_accurate_suggested[dv]['residue_table_max'], self._result_accurate_suggested[dv]['residue_table_std'])
      self.heading(self.underline('Gain matrix'), 5)
      self._print_gain_matrix( self._result_accurate_suggested[dv]['gain_table'], self._result_accurate_suggested[dv]['predictors'], self._lrg_sgt.get_summary()[dv], self._lrr_sgt.get_summary()[dv])

      # model accuracy report (full expansion for debugging purpose)
      self.heading('%s. Full regression for debugging purpose' % get_letter_index(3, upper=False), 4)
      self.heading(self.underline('Cross model validation'), 5)
      self._print_cross_model_validation(self._result_accurate_init[dv]['residue_table_max'], self._result_accurate_init[dv]['residue_table_std'])
      self.heading(self.underline('Gain matrix'), 5)
      self._print_gain_matrix( self._result_accurate_init[dv]['gain_table'], self._result_accurate_init[dv]['predictors'], self._lrg.get_summary()[dv], self._lrr.get_summary()[dv])
      self.hline(width=60)

  def load_sensitivity_threshold(self, val):
    ''' load input sensitivity threshold '''
    self._sensetol = val

  def _print_gain_matrix(self, table_data, predictors, lrg_summary, lrr_summary):
    self.table(
               add_column_list(['gain (%s)' % self._tenvsc.golden, 'gain (%s)' % self._tenvsc.revised, 'error [%]', 'normalized input sensitivity [%%] (%s)' % self._tenvsc.golden, 'normed input sensitivity [%%] (%s)' % self._tenvsc.revised ], table_data),
               [' ']+predictors,
               ['center']*(len(predictors)+1)
              )
    for p in [self._tenvsc.golden,self._tenvsc.revised]:
      lr_summary = lrg_summary if p == self._tenvsc.golden else lrr_summary
      spanid, spantext = self.span_button('+/-')
      self.heading(self.underline('Linear regression summary of %s model' % p + spantext), 5)
      quote = '''
<div id="{1}" style="display:block;">
{0}
</div>
'''.format(
        lr_summary,
        spanid
        )
      self.block_quote(quote)

  def _print_cross_model_validation(self, res_tbl_max, res_tbl_std):
    ''' print out cross model validation result (both maximum and standard deviation errors)
                           Extracted   Extracted
                            Golden      Revised
        Simulated Golden       1           2
        Simulated Revised      3           4
    '''
    self.write('- Maximum residual error')
    self.table(res_tbl_max, None, ['center']*4)
    self.line_break()
    self.write('- Standard deviation of residual errors')
    self.table(res_tbl_std, None, ['center']*4)


  # Belows are basis functions for writing raw HTML code
  def write(self,value):
    self.fid.write(value)

  def close(self):
    self.fid.close()

  def text(self,text):
    self.write(ht.text(text))
  
  def heading(self, text, level, linkid=''):
    self.write(ht.heading(text, level, linkid))

  def line_break(self):
    self.write('<br>')

  def hline(self, width=100, align='left'):
    self.write(ht.hline(width,align))

  def block_quote(self, text):
    self.write(ht.block_quote(text))

  def list(self,*args, **kwargs):
    self.write(ht.list(*args, **kwargs))

  def paragraph(self):
    self.write(ht.paragraph())

  def table(self, data, header, col_align):
    htmlcode = ht.table(data, header_row=header, col_align=col_align)
    self.write(htmlcode)
  
  # generating raw html code without write
  def link(self, text, linkid):
    return ht.link(text, linkid)

  def underline(self, text):
    return ht.underline(text)

  def span_button(self, text):
    return ht.span_button(text)
