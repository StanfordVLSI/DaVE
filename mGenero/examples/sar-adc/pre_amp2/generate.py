#!/usr/bin/env python

import os
from dave.mgenero.circuit import ModelCreator

generic_module_name = 'amplifier'
dut = 'pre_amp2'

cfg_f = "circuit.cfg" # user configuration of interface template
ifc_f = os.path.join(os.environ['DAVE_SAMPLES'],'mGenero/template/{0}/{0}.interface'.format(generic_module_name)) # interface template
mdl_template = os.path.join(os.environ['DAVE_SAMPLES'],'mGenero/template/{0}/{1}'.format(generic_module_name,'%s.empy.v' % generic_module_name)) # model template
test_template = os.path.join(os.environ['DAVE_SAMPLES'],'mGenero/template/{0}/{1}'.format(generic_module_name,'%s.test.empy.cfg' % generic_module_name)) # test template
mdl_i_dst_file = '%s.intermediate.v' % dut  # intermediate verilog model (before back-annotation)
mdl_dst_file = '%s.v' % dut  # intermediate verilog model (before back-annotation)
test_dst_file = 'test.cfg'
user_test_file = 'user.cfg'
#user_test_file = '' # customization of test template


#-------------------------- CODE STARTS HERE
# Instantiation of Model generator class
m = ModelCreator(cfg_f, ifc_f) 

# Generate a model from a template
m.generate_model(mdl_template, mdl_i_dst_file) 

# Model parameter calibration
m.generate_test(test_template, test_dst_file, user_test_file) # Generate the corresponding test from a template
m.run_characterization(no_processes=4, test_cfg='test.cfg', sim_cfg='sim.cfg') # Run circuit characterization using mProbo

# Back-annotate model parameters to the generated model
m.backannotate_model(mdl_i_dst_file, mdl_dst_file, './.mProbo/extracted_linear_model.yaml')

# Run equivalence checking using mProbo
m.run_equivalence(no_processes=4, test_cfg='test.cfg', sim_cfg='sim.cfg')
