#

__doc__ = '''
This module is for generating models/tests from templates.

Note:
  $$: Instead of @, we use $$ for empy template implementation 
      since @ is a reserved symbol in Verilog. These $$ and @ will 
      be internally replaced with @ and @@ for empy, respectively.
  $!: There are two-step model generation process if parameter 
      calibration and back-annotation is needed.  If the first phase 
      of model generation, this $! will be replaced with $$.
'''

import sys
import os
import StringIO
import re
import yaml
from time import strftime, localtime
from dave.common.davelogger import DaVELogger
from dave.mprobo.modelparameter import LinearModelParameter
from model_header import MODEL_HEADER, BACKANNOTATION_PRIMITIVE_FUNCTIONS
from dave.common.empyinterface import EmpyInterface
from dave.common.misc import flatten_list, get_abspath

#---------------------------------
class TemplateInterpreter(object):
  '''
    Generate model/test from a template
    METADATA_DELIMITER : Reserved for future implementation 
    METACHAR : Meta character instead of using the '@' prefix in EmPy
    METACHAR2 : Model generation including back-annotating regression models 
                is a two-step process (i.e. model generation followed by parameter 
                back annotation). Therefore, if there is something needed to be 
                compiled to '$$' in the first phase, use this meta character. 
  '''
  METADATA_DELIMITER = '---\r?\n'
  METACHAR  = '$$' 
  METACHAR2 = '$!' 
  def __init__(self, api_file=None, logger=None):
    '''
      api_file: Python File name that contains API functions used in a model/test template
    '''
    self.logger = logger
    self._embedded_api_text = self._embed_api(api_file)

  def generate_model(self, src_file, dst_file, param):
    ''' generate model without parameter calibration '''
    self.generate(src_file, dst_file, param, 'model', calibration=False)

  def generate_test(self, src_file, dst_file, param, calibration=False):
    ''' generate mProbo test 
        Generating a test has two purposes: 
          - extract circuit properties and check circuit/model equivalence
        Depending on the goal, calibration argument is set
    '''
    self.generate(src_file, dst_file, param, 'test', calibration)

  def backannotate_model(self, src_file, dst_file, param, lm_file):
    ''' back annotate regression models to Verilog '''
    self.generate(src_file, dst_file, param, 'model', calibration=False, ba_opt={'do_backannotate': True, 'lm_file': lm_file})

  def generate(self, src_file, dst_file, param, section, calibration=False, ba_opt={'do_backannotate':False, 'lm_file':''}):
    ''' This generates either Verilog model or mProbo test from a template 
        by binding the 'param' dictionary to the empy template.
        - src_file: template file name
        - dst_file: output file name
        - param   : a dictionary that defines values in a template
        - section : 'model' for Verilog, 'test' for mProbo test
        - calibration : Valid only for test generation.
          - True for circuit property characterization 
          - False for model/circuit equivalence checking
        - ba_opt   : back annotation option in dictionary 
          - do_backannotate : Perform back annotation if True
          - lm_file  : a ymal file that defines linear regression models 
                       for back-annotation
    '''
    param.update({'is_calibration': calibration}) 

    # if a pin is not allowed to be a vector, tweak user configuration properly processed by APIs
    #for p in param['pin'].keys(): # replace vectorsize of a pin if it is 0
    #  if param['pin'][p]['vectorsize'] == 0:
    #    param['pin'][p]['vectorsize'] = 1

    # create an intermediate template
    template = self._embedded_api_text
    if ba_opt['do_backannotate']:
      template += self._embed_ba_prim_func(ba_opt['lm_file'])
    else:
      template += self._print_model_header(section)
    with open(src_file,'r') as f: # adds model or test template
      template_body = f.read().replace('@','@@').replace(self.METACHAR,'@').replace(self.METACHAR2,self.METACHAR) 
    template += template_body

    # TODO: Better error reporting capability
    #       Get info from Empy and report it for better error tracking
    #EmpyInterface(dst_file)(StringIO.StringIO(template), param)
    try:
      EmpyInterface(dst_file)(StringIO.StringIO(template), param)
    except:
      err_fname = dst_file+'.err'
      with open(err_fname, 'w') as f:
        f.writelines(template_body)
      self.logger.error('[ERROR] The system is terminated due to error(s) in a template. Please check out the intermediate code, %s' % err_fname)
      sys.exit()
      
  def _embed_api(self, api_file):
    ''' create an intermediate template that embeds API function calls '''
    # read and embed API function calls to a template
    try: # user-defined API function calls
      api_fullpath = get_abspath(api_file, True, self.logger) 
    except: # default API function calls
      def_file = os.path.join(os.environ['DAVE_INST_DIR'], 'dave/mgenero/api_mgenero.py')
      api_fullpath = get_abspath(def_file, True, self.logger)
      self.logger.info("[INFO] Use default API calls in '%s'" % def_file)
    with open(api_fullpath,'r') as f:
      return '\n@{\n' + f.read() + '}@\n'

  def _print_model_header(self, section):
    ''' print out model header to a generated model '''
    t = strftime("%a, %d %b %Y %H:%M:%S", localtime())
    start = '/*' if section=='model' else '##'
    duplicate = '*'*63 if section=='model' else '#'*63
    ll = '*' if section=='model' else '#'
    end = '*/' if section=='model' else '##'
    return MODEL_HEADER.format(software='mGenero', timestamp=t, start=start, duplicate=duplicate,end=end, ll=ll)

  def _embed_ba_prim_func(self, lm_file):
    ''' add back-annotatation related API calls to a model template '''
    mp = LinearModelParameter()
    mp.load_model_parameters(lm_file)
    param = mp.get_param()
    return BACKANNOTATION_PRIMITIVE_FUNCTIONS.format(lm_param=param)

