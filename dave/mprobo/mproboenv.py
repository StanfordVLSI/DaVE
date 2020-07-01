__doc__ = '''
Schema for all the keywords used in mProbo
  - envcfg: environment setup
  - testcfg: schema setup for test.cfg 
  - simcfg: sim.cfg
'''

from io import StringIO
import copy
  
envcfg = StringIO("""
[runarg]
testcfg_filename = test.cfg
simcfg_filename = sim.cfg
rpt_filename = report.html
verif_mcrun_filename = verif.py
port_xref_filename = ${DAVE_SAMPLES}/mProbo/port_xref.cfg

[fileloc]
root_rundir = .mProbo
server_tempdir = /tmp/mproboserver
server_logfile = mProbo_server.log
client_logfile = mProbo_client.log
server_userfile = mProbo_users.dat # under DAVE_INST_DIR
client_runarg_file = runargs.txt
csv_vector_prefix = vector
csv_vector_meas_prefix = vector_meas
csv_regression_prefix = regression
prototype_dirname = prototype
debug_file = .mProbo_debug.log
dump_file  = .mProbo_dump.log
logfile = mProbo.log
simlogfile = mProbo_sim.log
gui_prog   = mProbo_gui
extracted_model_param_file = extracted_linear_model.yaml
def_lfname = dave.lic


[oatable]
max_oa_depth = 9
max_oa_var = 10

[portname]
AnalogInput = analoginput
AnalogOutput = analogoutput
QuantizedAnalog = quantizedanalog
DigitalMode = digitalmode
DigitalOutput = digitaloutput
AnalogInputLabel = analog input
AnalogOutputLabel = analog output
QuantizedAnalogLabel = quantized analog input
DigitalModeLabel = digital input
DigitalOutputLabel = digital output

[testcfg]
  [[section]]
  test_name = test_name
  dut_name = dut
  description = description
  option = option
  port = port
  testbench = testbench
  simulation = simulation
  response = response
  post_processor = post-processor
  instance = instance
  wire = wire
  pre_module_declaration = pre_module_declaration
  tb_code = tb_code
  tb_supplement = tb_supplement
  default = DEFAULT
  initial_condition = initial_condition
  ic_golden = golden
  ic_revised = revised
  temperature = temperature

  [[option]]
  max_sample = max_sample
  #analog_level = no_of_analog_grid
  min_analog_level = min_no_of_analog_grid
  regression_method = regression_method
  regression_pval_threshold = regression_pval_threshold
  regression_cint_threshold = regression_cint_threshold
  regression_basis = regression_basis
  regression_do_not_regress = regression_do_not_regress
  polynomial = polynomial
  regression_user_model = regression_user_model
  regression_order = regression_order
  regression_en_interact = regression_en_interact
  regression_sval_threshold = regression_sval_threshold

  [[simtime]]
  sim_timeunit = timeunit
  sim_time = trantime

  [[port]]
  port_type = port_type
  regions = regions
  upper_bound = upper_bound
  lower_bound = lower_bound
  pinned = pinned
  bit_width = bit_width
  encode = encode
  default_value = default_value
  prohibited = prohibited
  domain = domain
  description = description
  constraint = constraint
  thermometer = thermometer
  binary = binary
  gray = gray
  onehot = onehot
  constr_common = pinned, default_value
  constr_analog = upper_bound, lower_bound, domain, abstol, gaintol, input_sensitivity_threshold
  constr_digital = bit_width, encode, prohibited
  abstol = abstol
  gaintol = gaintol
  regression_order = regression_order
  regression_en_interact = regression_en_interact
  regression_sval_threshold = regression_sval_threshold

  [[testbench]]
  meas_filename = meas_filename
  model_ams = ams
  model_verilog = verilog
  cell_name = cellname
  para_map = parameter_map
  port_map = port_map
  sample_signal = signal
  sample_at = at
  meas_blk = meas_vlogstr
  pp_script = script_files
  pp_command = command
  pp_measfile = measfile


[simcfg]
default = DEFAULT
golden = golden
revised = revised
characterization = characterization
model = model
simulator = simulator
vcs = vcs
ncsim = ncsim
ams_control_file = ams_control_file
ams_connrules = default_ams_connrules
simulator_option = simulator_option
hdl_files = hdl_files
hdl_include_files = hdl_include_files
sweep_file = sweep_file
circuit = circuit
model_ams = ams
model_vlog = verilog
process_file = process_file
mc_samples = mc_samples
vlog_param_samples = vlog_param_samples
vlog_param_file = vlog_param_file
global_variation = global_variation
rsq_threshold = rsq_threshold
splib = spice_lib

[mcrun]
prototype_dir = prototype_dir
format = format
circuit = circuit
verilog = verilog
process_file = process_file
parameter_file = parameter_file
run_script = run_script
pre_script = pre_script
post_script = post_script
global_variation = global_variation
measurement = measurement
dut_name =dut
circuit_file = circuit_file
vlog_tb_file = vlog_tb_file
suppress = suppress
mc_ckt = mc_ckt
mc_vlog = mc_vlog
mc_ckt_para_filename = ckt_para.dat
mc_vlog_para_filename = vlog_para.dat
mc_char_filename = .mc_char.pkl
mc_verif_data_dir = .amsmc
mc_vlog_netlist_dir = verilog
mc_ckt_netlist_dir = spice

[simulator_cls_opt]
workdir = workdir
sweep_file = sweep_file
hdl_files = hdl_files
ic = ic
sim_time = sim_time
timescale = timescale
measfile_def = measfile_def

[misc]
logger_prefix = mProbo_logger
no_clients = 5
server_port = 5000
""")

simcfg = StringIO("""
######################################
# Schema for simulator configuration #
# Don't comment at the end of line   #
######################################

[characterization] 
process_file = string(default='')  
mc_samples = integer(min=1,default=1) 
vlog_param_samples = integer(min=1,default=1) 
vlog_param_file = string(default='') 
global_variation = boolean(default=True)
rsq_threshold = float(min=-0.1, max=1.0, default=0.5)
  [[option]]
  max_sample = integer(min=8, default=8)
  OA_depth = integer(min=2, default=2)
  regression_order = integer(min=1,max=10, default=1)
  regression_en_interact = boolean(default=True)
  regression_method = option("basic","filtered", default="basic")
  regression_pval_threshold = float(min=0.0, max=1.0, default=0.05)
  regression_cint_threshold = float(min=0.0, max=1.0, default=0.95)
  regression_basis = option("polynomial", default="polynomial")

[golden]
model = option("ams", "verilog")
simulator = option("ncsim", "vcs")
default_ams_connrules = string(default='')
ams_control_file = string(default='') 
simulator_option = string() 
hdl_files = force_list(default='')
hdl_include_files = force_list(default='')
sweep_file = boolean(default=True) 
spice_lib = string(default='')
[[circuit]]

[revised]
model = option("ams", "verilog")
simulator = option("ncsim", "vcs")
default_ams_connrules = string(default='')
ams_control_file = string(default='') 
simulator_option = string() 
hdl_files = force_list(default='')
hdl_include_files = force_list(default='')
sweep_file = boolean(default=True) 
spice_lib = string(default='')
[[circuit]]
""")

testcfg = StringIO("""
####################################
# Schema for test configuration    #
# Don't comment at the end of line #
####################################

[__many__] 
testname = string()
dut = string(default='')
description = string(default='')

[[option]]
min_no_of_analog_grid = integer(min=1, max=1, default=1)
max_sample = integer(min=8, default=8)
#no_of_analog_grid = integer(min=2, default=2)
regression_method = option("basic","filtered", default="basic")
regression_pval_threshold = float(min=0.0, max=1.0, default=0.05)
regression_cint_threshold = float(min=0.0, max=1.0, default=0.95)
regression_basis = option("polynomial", default="polynomial")
regression_order = integer(min=1,max=10, default=1)
regression_en_interact = boolean(default=True)
regression_sval_threshold = float(min=0.0, max=100.0, default=5.0) # in %

[[[regression_do_not_regress]]]

[[[regression_user_model]]]

[[simulation]]
timeunit = time_verilog()
trantime = time_engr()

[[port]]
[[[__many__]]]
port_type = option("analoginput", "analogoutput", "quantizedanalog", "digitalmode") 
description = string(default='')
regions = force_list()
upper_bound = float()
lower_bound = float()
pinned = boolean(default=False)
bit_width = integer(min=1)
encode = option("thermometer", "binary", "gray", "onehot", default='binary')
default_value = string(default=0)
prohibited = force_list(default='')
abstol = float(default=1.0)
gaintol = integer(min=0, max=100, default=25)
regression_order = integer(min=1,max=10,default=None)
regression_en_interact = boolean(default=None)
regression_sval_threshold = float(min=0.0,max=100.0,default=5.0)

[[testbench]]
pre_module_declaration = string(default='')
tb_code = string(default='')
tb_supplement = string(default='')
temperature = integer(default='27')

[[[initial_condition]]]
  [[[[golden]]]]
  [[[[revised]]]]

[[[wire]]]
ams_electrical = force_list(default='')
ams_wreal = force_list(default='')
ams_ground = force_list(default='')
logic = force_list(default='')

[[[instance]]]
[[[[__many__]]]]
cellname = string()
parameter_map = force_list(default='')
port_map = force_list()

[[[response]]]
[[[[__many__]]]]
signal = string()
at = time_engr()

[[[post-processor]]]
script_files = force_list(default='')
command = string(default='')
""")

def get_envcfg():
  return copy.deepcopy(envcfg)

def get_simcfg():
  return copy.deepcopy(simcfg)

def get_testcfg():
  return copy.deepcopy(testcfg)
