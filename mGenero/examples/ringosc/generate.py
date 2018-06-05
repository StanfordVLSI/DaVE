#!/usr/bin/env python

import os
from dave.mgenero.mgenero import ModelCreator
#from mgenero import ModelCreator

generic_module_name = 'oscillator'
dut = 'ringosc'

cfg_f = "circuit.cfg" # user configuration of interface template
ifc_f = os.path.join(os.environ['DAVE_SAMPLES'],'mGenero/template/{0}/{0}.ifc.yaml'.format(generic_module_name)) # interface template
mdl_template = os.path.join(os.environ['DAVE_SAMPLES'],'mGenero/template/{0}/{1}'.format(generic_module_name,'%s.template.sv' % generic_module_name)) # model template
test_template = os.path.join(os.environ['DAVE_SAMPLES'],'mGenero/template/{0}/{1}'.format(generic_module_name,'%s.test.template.cfg' % generic_module_name)) # test template
mdl_i_dst_file = '%s.intermediate.v' % dut  # intermediate verilog model (before back-annotation)
mdl_dst_file = '%s.v' % dut  # intermediate verilog model (before back-annotation)
test_dst_file = 'test.cfg'
user_test_file = 'user.cfg'

param_from_circuit = True

#-------------------------- CODE STARTS HERE
# Instantiation of Model generator class
m = ModelCreator(cfg_f, ifc_f) 
# Generate a model from a template
m.generate_model(mdl_template, mdl_i_dst_file) 
if param_from_circuit:
  # Model parameter calibration
  m.generate_test(test_template, test_dst_file+'.char', user_test_file+'.char', calibration=True) # Generate the corresponding test from a template
  m.run_characterization(no_processes=11, test_cfg='test.cfg.char', sim_cfg='sim.cfg', report='report_char.html') # Run circuit characterization using mProbo

# Back-annotate model parameters to the generated model
if param_from_circuit:
  m.backannotate_model(mdl_i_dst_file, mdl_dst_file, '.mProbo/extracted_linear_model.yaml')
else:
  m.backannotate_model(mdl_i_dst_file, mdl_dst_file, './sample_param.yaml')

# Run equivalence checking using mProbo
m.generate_test(test_template, test_dst_file, user_test_file, calibration=False)
m.run_equivalence(no_processes=11, test_cfg='test.cfg', sim_cfg='sim.cfg', report='report_check.html')
