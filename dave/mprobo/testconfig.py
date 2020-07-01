
import sys
from configobj import ConfigObj
from .configobjwrapper import ConfigObjWrapper
import copy
from dave.common.misc import from_engr, eval_str, flatten_list, generate_random_str, get_abspath, all_therm, all_bin, all_gray, all_onehot, featureinfo, interpolate_env, print_section
import os
import collections
from BitVector import BitVector
from collections import OrderedDict
from itertools import product
from .amschkschema import SchemaTestConfig 
from .environ import EnvPortName, EnvTestcfgPort, EnvTestcfgSection, EnvTestcfgOption, EnvTestcfgTestbench, EnvTestcfgSimTime, EnvSimcfg, EnvFileLoc
from dave.common.davelogger import DaVELogger
import dave.mprobo.mchkmsg as mcode
from dave.mprobo.wire import TestBenchWire



#-------------------------------------------------------------------------
class TestConfig(object):

  def __init__(self, cfg_filename, bypass=False, keep_raw=False, port_xref='', logger_id='logger_id', quite=False):
    ''' 
      set bypass to False if you don't want to create sub-regions of tests 
      set keep_raw to True if you keep the raw configuration
      set port_xref to a filename which contains port cross reference of modules
    '''

    assert os.path.exists(get_abspath(cfg_filename)), mcode.ERR_001 % cfg_filename
    assert os.path.exists(get_abspath(port_xref)), mcode.ERR_001_1 % port_xref

    self._pxref = port_xref

    self._tenvp = EnvPortName()
    self._tenvt = EnvTestcfgPort()
    self._tenvs = EnvTestcfgSection()
    self._logger = DaVELogger.get_logger('%s.%s.%s' % (logger_id, __name__, self.__class__.__name__))
    self._logger_id = logger_id
    if not quite:
      list(map(self._logger.info, print_section('Compile test configrations', 1)))

    if keep_raw:
      self.config = self._read_raw_config_file(cfg_filename)
    else:
      self._test_cfg = {} # list of UnitTestConfig class instances
      self._test_name_list = [] # list of the corresponding test names
      self.config = self._read_config_file(cfg_filename)

      # 1st pass to Validate and update
      schema_testcfg = SchemaTestConfig(self.config)
      schema_testcfg.raise_vdterror()
      self.config = schema_testcfg.get_cfg()

      self._build(bypass)

  def get_config(self):
    ''' return configobj '''
    return self.config

  def get_raw_test(self, testname):
    return self.config[testname]

  def get_all_testnames(self):
    return self._test_name_list

  def get_test(self, testname):
    return self._test_cfg[testname]

  def get_all_tests(self):
    return [self._test_cfg[t] for t in self.get_all_testnames()]

  def _build(self, bypass):
    # instantiate config class for each class
    if not bypass:
      self._create_subtest()
    for k,v in list(self.config.items()):
      self._test_name_list.append(k)
      self._test_cfg[k]=UnitTestConfig(k, v, self._pxref, self._logger_id)
  
  def _create_subtest(self):
    ''' generate subtests for piecewise linear testing of analog inputs '''
    for tn, tv in list(self.config.items()): # for each test
      _tmp_multi_region = dict([(pn, sorted(map(float,pc[self._tenvt.regions]))) 
                          for pn, pc in list(tv[self._tenvs.port].items()) 
                          if self._tenvt.regions in list(pc.keys()) and 
                             pc[self._tenvt.pinned]==False and 
                             pc[self._tenvt.port_type]==self._tenvp.AnalogInput]
                          )

      _tmp_multi_region = OrderedDict(sorted(list(_tmp_multi_region.items()),key=lambda t:t[0]))

      _tmp_uniq_region = dict([(pn,sorted(map(float,pc[self._tenvt.regions]))) 
                         for pn,pc in list(tv[self._tenvs.port].items())
                         if pn not in list(_tmp_multi_region.keys()) and
                            self._tenvt.regions in list(pc.keys()) ]
                         )

      _subdiv = list(product(*[list(range(len(x)-1)) for x in list(_tmp_multi_region.values())]))
      _subdiv_key = list(_tmp_multi_region.keys()) # port names to be subdivded
      no_subtest = len(_subdiv)
      if no_subtest > 0: # if there really exists sub regions
        if no_subtest > 1:
          self._logger.info(mcode.INFO_019 %(no_subtest, tn, tn, tn, no_subtest-1))
        for idx,x in enumerate(_subdiv): # generate subdivided regions
          _tmp_cfg = copy.deepcopy(self.config[tn])
          for y in range(len(x)):
            _tmp_cfg[self._tenvs.port][_subdiv_key[y]][self._tenvt.upper_bound] = _tmp_multi_region[_subdiv_key[y]][x[y]+1]
            _tmp_cfg[self._tenvs.port][_subdiv_key[y]][self._tenvt.lower_bound] = _tmp_multi_region[_subdiv_key[y]][x[y]]
            del _tmp_cfg[self._tenvs.port][_subdiv_key[y]][self._tenvt.regions]
          for k,v in list(_tmp_uniq_region.items()):
            _tmp_cfg[self._tenvs.port][k][self._tenvt.upper_bound] = v[1]
            _tmp_cfg[self._tenvs.port][k][self._tenvt.lower_bound] = v[0]
            del _tmp_cfg[self._tenvs.port][k][self._tenvt.regions]
          tname = tn+'_%d'%idx if no_subtest > 1 else tn
          self.config[tname] = copy.deepcopy(_tmp_cfg)

        if no_subtest > 1:
          del self.config[tn] # delete original, undivided test

    for tn, tv in list(self.config.items()): # check analog output port has region
      for pn, pc in list(tv[self._tenvs.port].items()):
        if self._tenvt.regions in list(pc.keys()) and pc[self._tenvt.port_type]==self._tenvp.AnalogOutput:
          val = sorted(map(float, pc[self._tenvt.regions]))
          pc[self._tenvt.upper_bound] = val[1]
          pc[self._tenvt.lower_bound] = val[0]

  def _read_config_file(self, cfg_filename):
    ''' read configuration file and merge each section 
        with default section if exists '''
    cfg_instance = ConfigObjWrapper(cfg_filename, self._tenvs.default) 
    return cfg_instance.get_cfg()

  def _read_raw_config_file(self, cfg_filename):
    ''' read configuration file as is '''
    return ConfigObj(cfg_filename)

#-------------------------------------------------------------------------
class UnitTestConfig(object):
  ''' 
    Read/Parse/Store test configuration from a file(cfg_filename) 
    wire conversion rule: In testbench.py
      ams_electrical = gnd:clkout:clkout_b,clkin # (AMS,SV) = (electrical,real)
      ams_wreal = duty                           # (AMS,SV) = (wreal,real) 
      ams_ground = gnd                           # (AMS,SV) = (ground,real)
      logic =                                    # (AMS,SV) = (wire,wire)
  '''

  __wire_map = {'ams':{'ams_electrical':'electrical','ams_wreal':'wreal', 'logic':'wire'}, \
               'verilog':{'ams_electrical':'real ','ams_wreal':'real  ', 'logic':'wire'}}
  __gnd_map = {'ams':{'ams_ground': 'ground'},'verilog':{'ams_ground':''}}

  #_test_cfg = {}

  def __init__(self, test_name, unit_test_cfg, port_xref='', logger_id='logger_id'):
    self._logger = DaVELogger.get_logger('%s.%s.%s' % (logger_id, __name__, self.__class__.__name__))
    self._tenvs = EnvTestcfgSection()
    self._tenvtp = EnvTestcfgPort()
    self._tenvr = EnvTestcfgOption()
    self._tenvts = EnvTestcfgSimTime()
    self._tenvtb = EnvTestcfgTestbench()
    self._tenvp = EnvPortName()
    self._tenvsim = EnvSimcfg()
    self._portref_filename = interpolate_env(port_xref)

    self._logger.info(mcode.INFO_055 % test_name)

    _tmpcfg = dict([(test_name,dict([(self._tenvs.test_name, test_name)]+list(dict(unit_test_cfg).items())))])
    cfg = ConfigObj(_tmpcfg)
    schema_testcfg = SchemaTestConfig(cfg)
    schema_testcfg.raise_vdterror()
    self._test_cfg = schema_testcfg.get_cfg()[test_name]

    self._test_cfg.update(self._compile_test(unit_test_cfg))
    
  def get_test_name(self):
    ''' return testname '''
    return self._test_cfg[self._tenvs.test_name]

  def get_dut_name(self):
    ''' return testname '''
    return self._test_cfg[self._tenvs.dut_name]
  
  def get_description(self):
    desc = self._test_cfg[self._tenvs.description]
    return desc if desc != '' else 'N/A'

  def get_test(self):
    ''' return a dict of test configuration '''
    return self._test_cfg
  
  def get_port(self):
    return self.get_test()[self._tenvs.port]

  def get_port_constraint(self, port):
    return port[self._tenvtp.constraint]

  def get_port_type(self, port):
    return port[self._tenvtp.port_type]
  
  def get_port_description(self, port):
    return port[self._tenvtp.description]
  
  def get_testbench(self):
    return self.get_test()[self._tenvs.testbench]

  def get_wires(self):
    ''' return list of wires declared in wire section '''
    return list(set(flatten_list(list(self.get_testbench()[self._tenvs.wire][self._tenvtb.model_ams].values()))))

  def get_temperature(self):
    return self.get_testbench()[self._tenvs.temperature]

  def get_ic(self, model):
    if model == self._tenvsim.golden:
      return self.get_ic_golden()
    elif model == self._tenvsim.revised:
      return self.get_ic_revised()

  def get_ic_golden(self):
    return self.get_testbench()[self._tenvs.initial_condition][self._tenvs.ic_golden]

  def get_ic_revised(self):
    return self.get_testbench()[self._tenvs.initial_condition][self._tenvs.ic_revised]

  def get_postprocessor(self):
    return self.get_testbench()[self._tenvs.post_processor]

  def get_option(self):
    return self.get_test()[self._tenvs.option]

  def get_option_regression_min_sample(self):
    return self.get_option()[self._tenvr.min_sample]

  def get_option_regression_max_sample(self):
    return max(8, int(self.get_option()[self._tenvr.max_sample]))

  def get_option_regression_oa_depth(self):
    return self.get_option()[self._tenvr.analog_level]

  def get_option_regression_min_oa_depth(self):
    return self.get_option()[self._tenvr.min_analog_level]

  def get_option_regression_en_interact(self):
    return self.get_option()[self._tenvr.regression_en_interact]

  def get_option_regression_order(self):
    return self.get_option()[self._tenvr.regression_order]

  def get_option_regression_method(self):
    return self.get_option()[self._tenvr.regression_method]

  def get_option_regression_pval_threshold(self):
    return self.get_option()[self._tenvr.regression_pval_threshold]

  def get_option_regression_input_sensitivity_threshold(self):
    return self.get_option()[self._tenvr.regression_sval_threshold]

  def get_simulation_time(self):
    ''' return simulation time '''
    return self._test_cfg[self._tenvs.simulation][self._tenvts.sim_time] 

  def get_simulation_timeunit(self):
    ''' return simulation time unit '''
    return self._test_cfg[self._tenvs.simulation][self._tenvts.sim_timeunit]

  def get_timescale(self):
    ''' return a string of Verilog timescale '''
    return self.get_simulation_timeunit() + '/' + self.get_simulation_timeunit()

  def get_meas_files(self):
    return self._test_cfg[self._tenvs.testbench][self._tenvs.response][self._tenvtb.meas_filename]


  # compile test configuration
  def _compile_test(self, test):
    return {
            self._tenvs.dut_name : test[self._tenvs.dut_name], 
            self._tenvs.option : test[self._tenvs.option],
            self._tenvs.port : self._compile_port(test),
            self._tenvs.testbench : self._compile_testbench(test), 
            self._tenvs.simulation : test[self._tenvs.simulation]}

  # port section
  def _compile_port(self,test):
    ''' return a dict {portname:{port info}}'''
    p = test[self._tenvs.port]
    return dict([ (k, self._elab_port(v)) for k,v in list(p.items())])

  def _elab_port(self, port_param):
    ''' elaborate port to make a constraint '''
    ptype = port_param[self._tenvtp.port_type]

    # processing pinned constraints
    if ptype == self._tenvp.QuantizedAnalog or ptype == self._tenvp.DigitalMode:
      pinned_cfg = (port_param[self._tenvtp.pinned], eval_str(port_param[self._tenvtp.default_value],int))
    else:
      pinned_cfg = (port_param[self._tenvtp.pinned], port_param[self._tenvtp.default_value])
    pinned_dict = {self._tenvtp.pinned : pinned_cfg}

    # processing port constraints other than pinned ones

    if ptype in [self._tenvp.AnalogInput, self._tenvp.AnalogOutput]:
      _eff_constr = self._tenvtp.constr_analog
    else:
      _eff_constr = self._tenvtp.constr_digital
    constraint_in_cfg = list(filter(lambda x, opt=_eff_constr: 
                                         x in opt, list(port_param.keys()) ))

    constraint = dict(dict([(p,port_param[p]) for p in constraint_in_cfg]),**pinned_dict) 
    if ptype == self._tenvp.AnalogInput:  # only analog output has abstol 
      constraint.update({self._tenvtp.abstol: 'N/A'})
      constraint.update({self._tenvtp.gaintol: 'N/A'})
      constraint.update({self._tenvtp.regression_en_interact: 'N/A'})
      constraint.update({self._tenvtp.regression_order: 'N/A'})
      constraint.update({self._tenvtp.regression_sval_threshold: 'N/A'})

    # 'prohibited' field is either integer or binary, and could be a list
    _p = self._tenvtp.prohibited
    _e = self._tenvtp.encode
    prohibited = [x for x in port_param[_p] if x not in ['']]
    constraint[_p] = list(map(eval_str,prohibited)) # convert to an integer
    # if port is a digital input, automatically adds other prohibited codes due to encode
    if port_param[self._tenvtp.port_type] == self._tenvp.QuantizedAnalog or port_param[self._tenvtp.port_type] == self._tenvp.DigitalMode:
      bitw = port_param[self._tenvtp.bit_width]
      constraint[_p] = list(set(constraint[_p]+self._autoinsert_prohibited_code(bitw, port_param[_e])))

    return { self._tenvtp.port_type : port_param[self._tenvtp.port_type],
             self._tenvtp.description : port_param[self._tenvtp.description],
             self._tenvtp.constraint : constraint
           }

  def _autoinsert_prohibited_code(self, bitw, encode):
    if encode == self._tenvtp.thermometer:
      return list(set(all_bin(bitw))-set(all_therm(bitw)))
    elif encode == self._tenvtp.gray:
      return list(set(all_bin(bitw))-set(all_gray(bitw)))
    elif encode == self._tenvtp.onehot:
      return list(set(all_bin(bitw))-set(all_onehot(bitw)))
    else:
      return []

  def _compile_testbench(self, test):
    tb = test[self._tenvs.testbench]
    port = test[self._tenvs.port]
    tb_code = self._compile_tb_code(tb)
    tbw = TestBenchWire(self._portref_filename)
    tbw.load_testbench(tb_code)
    tb_wires, tb_wires_unresolved = tbw.get_wires()
    return {self._tenvs.instance : self._compile_instance(tb),
            self._tenvs.response : self._compile_response(test, tb),
            self._tenvs.wire     : self._compile_wire(tb, tb_wires, tb_wires_unresolved),
            self._tenvs.tb_code : tb_code,
            self._tenvs.pre_module_declaration : self._compile_pre_module_declaration(tb),
            self._tenvs.temperature : self._compile_temperature(tb),
            self._tenvs.post_processor : self._compile_postprocessor(tb, port),
            self._tenvs.initial_condition : self._compile_ic(tb)
           }

  def _compile_ic(self, testbench):
    ''' set initial condition section under testbench '''
    ic_golden = testbench[self._tenvs.initial_condition][self._tenvs.ic_golden]
    ic_revised = testbench[self._tenvs.initial_condition][self._tenvs.ic_revised]
    ic_common = dict([(k,v) for k,v in list(testbench[self._tenvs.initial_condition].items()) if k not in [self._tenvs.ic_golden, self._tenvs.ic_revised]])
    ic_golden.update(ic_common)
    ic_revised.update(ic_common)
    return { self._tenvs.ic_golden  : ic_golden, self._tenvs.ic_revised : ic_revised }

  def _compile_temperature(self, testbench):
    ''' return temperature setting'''
    return testbench[self._tenvs.temperature] 

  def _compile_pre_module_declaration(self, testbench):
    ''' return a (multi-line) string of pre_module_declaration code'''
    return testbench[self._tenvs.pre_module_declaration] 

  def _compile_tb_code(self, testbench):
    ''' return a (multi-line) string of custom code'''
    return testbench[self._tenvs.tb_supplement] + testbench[self._tenvs.tb_code]

  def _compile_wire(self, testbench, tb_wires, tb_wires_unresolved):
    ''' prepare two set of wire definition: 1) for ams and 2) for verilog '''
    wire = testbench[self._tenvs.wire]
    wire = self._update_wire(wire, tb_wires, tb_wires_unresolved)
    wire_opt = dict([ (k,v) for k, v in list(wire.items()) if v !=[''] ])
    return {
            self._tenvtb.model_ams : self._elab_wire(wire_opt, self._tenvtb.model_ams),
            self._tenvtb.model_verilog : self._elab_wire(wire_opt, self._tenvtb.model_verilog)
           }

  def _update_wire(self, wire, tb_wires, tb_wires_unresolved):
    ''' update wire information extracted from tb_code by user-provided [wire] section '''

    updated_wires = dict(tb_wires)
    unresolved_nets_displiine = list(tb_wires_unresolved.keys())[0]
    unresolved_nets = list(tb_wires_unresolved.values())[0]
    resolved_nets = []
    _un_flag = True
    if len(unresolved_nets) > 0:
      self._logger.warning(mcode.WARN_020 % (unresolved_nets, unresolved_nets_displiine))
    else:
      _un_flag = False
      self._logger.info(mcode.INFO_056)

    # overwrites [wire] info to tb_wires dict.
    for k,v in list(wire.items()):
      for w in v:
        for kk, vv in list(tb_wires.items()):
          if w in vv:
            self._logger.warning(mcode.WARN_021 %(k, w, kk, w))
            updated_wires[kk].remove(w)
            if k in list(tb_wires.keys()):
              updated_wires[k].append(w)
            else:
              updated_wires[k] = [w]
      for n in unresolved_nets:
        if n in v:
          self._logger.warning(mcode.WARN_021 %(k, n, unresolved_nets_displiine, n))
          resolved_nets.append(n)
          if k in list(tb_wires.keys()):
            updated_wires[k].append(n)
          else:
            updated_wires[k] = [n]

    unresolved_nets = list(set(unresolved_nets)-set(resolved_nets))
    if len(unresolved_nets)>0:
      self._logger.error(mcode.ERR_021 %(unresolved_nets, self._portref_filename))
    elif _un_flag:
      self._logger.info(mcode.INFO_056)

    return updated_wires
      
    

  def _elab_wire(self, wire, model_type):
    ''' make either ams or verilog version of wire information 
        if the keys are not in the wire_map, those keys are treated as user_defined wires such that it will start with '`' in Verilog
    '''
    default_wire = dict([(self.__wire_map[model_type][p],list(set(v))) for p,v in list(wire.items()) if p in list(self.__wire_map[model_type].keys())])
    gnd_wire = dict([(self.__gnd_map[model_type][p],list(set(v))) for p,v in list(wire.items()) if (p in list(self.__gnd_map[model_type].keys()) and model_type == self._tenvtb.model_ams)])
    cwire = dict([(p,list(set(v))) for p,v in list(wire.items()) if p not in (list(self.__wire_map[model_type].keys())+list(self.__gnd_map[model_type].keys()))])
    custom_wire = dict([('`'+p,list(set(v))) if type(v)==type([]) else ('`'+p,[v]) for p,v in list(cwire.items())])
    return dict(list(default_wire.items()) + list(gnd_wire.items()) + list(custom_wire.items()))

  def _compile_instance(self,testbench):
    ''' return a list of verilog instantiation strings '''
    instance = testbench[self._tenvs.instance]
    return [ self._elab_instance(p, instance[p]) for p in list(instance.keys())]

  def _elab_instance(self, instname, instance):
    ''' get a string to be instantiated in the verilog testbench'''
    cellname = instance[self._tenvtb.cell_name] 
    para = instance[self._tenvtb.para_map] 
    para = '#(' + ', '.join(para) + ')' if para[0] !='' else ''
    port = '(' + ', '.join(instance[self._tenvtb.port_map]) + ')' 
    return cellname + ' '.join(['']+[para] + [instname] + [port]) +';\n'

  def _compile_response(self, test, testbench):
    ''' return a list of response statement and options '''
    response = testbench[self._tenvs.response]
    simulation = test[self._tenvs.simulation]
    return self._map_response_variable(
             dict([(k, self._elab_response(k, response[k])) for k in list(response.keys())]),
             simulation
             )

  def _elab_response(self, respname, response):
    ''' return a verilog code to get a response from some output '''
    response_opt = {}
    if self._tenvtb.sample_at in list(response.keys()) and response[self._tenvtb.sample_at] != '': 
      vlog_str = '''
      integer @fileid;
      initial begin
      @fileid = $fopen("@filename");
      #@{at} ;
      $fstrobe(@fileid,"%e", {signal});
      #1;
      $fclose(@fileid);
      end
      '''.format(at=self._tenvtb.sample_at, signal = response[self._tenvtb.sample_signal])
      return { self._tenvtb.sample_at : response[self._tenvtb.sample_at],
               self._tenvtb.meas_blk : vlog_str
             }

  def _map_response_variable(self, response, simulation):
    ''' map variable related to time information in response dump statement '''
    measfile = {}
    tname = self.get_test_name()
    for p, v in list(response.items()):
      fileid = generate_random_str('f', 5)
      filename = '_'.join(['meas', p + '.txt']) 
      time_opt = list(filter(lambda x,opt=[self._tenvtb.sample_at]:x in opt, list(v.keys())))
      for x in time_opt:
        v[x] = int(round(from_engr(v[x].rstrip('s'))/from_engr(simulation[self._tenvts.sim_timeunit].rstrip('s'))))
        v[self._tenvtb.meas_blk] = v[self._tenvtb.meas_blk].replace('@'+x, str(v[x]))
      v[self._tenvtb.meas_blk] = v[self._tenvtb.meas_blk].replace('@filename', filename)
      v[self._tenvtb.meas_blk] = v[self._tenvtb.meas_blk].replace('@fileid', fileid)
      measfile[p] = filename
    response[self._tenvtb.meas_filename] = measfile
    return response
  
  def _compile_postprocessor(self, testbench, port):
    ''' return a list of post process script files
    '''
    pp = testbench[self._tenvs.post_processor]
    pp_script = pp[self._tenvtb.pp_script]
    pp_cmd = pp[self._tenvtb.pp_command]
    if pp_script != [''] and pp_cmd != '':
      #pp_scr = [get_abspath(v, False) for v in pp_script]
      pp_scr = [interpolate_env(v, self._logger) for v in pp_script]
    else:
      pp_scr =  [None]
    return [_f for _f in pp_scr if _f], pp_cmd
