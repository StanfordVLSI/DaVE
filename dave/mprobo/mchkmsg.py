# messages for mProbo

"""
LOGO_001 = '''
mProbo - Analog/Mixed-Signal Equivalence Checker
                  Version 0.8.5
 Copyright (c) 2014-2016 by Stanford University
               ALL RIGHTS RESERVED

This version is only for evaluation purpose. 
Any redistribution, modification, or commercial 
use is prohibited without written permission.
For more information, contact bclim@stanford.edu
'''
LOGO_002 = '''
mProbo - Generation of Verilog testbench from Virtuoso 
      for Analog/Mixed-Signal Equivalence Checker
                   Version 0.8.5
 Copyright (c) 2014-2016 by Stanford University
               ALL RIGHTS RESERVED

This version is only for evaluation purpose. Any
redistribution, modification, or commercial use is 
prohibited without written permission.
For more information, contact bclim21@gmail.com

'''
LOGO_003 = '''
==================================================
             _____                       _       
            / ____|                     | |      
  _ __ ___ | (___  _ __   ___  ___ _   _| | ___  
 | '_ ` _ \ \___ \| '_ \ / _ \/ __| | | | |/ _ \ 
 | | | | | |____) | |_) |  __/ (__| |_| | | (_) |
 |_| |_| |_|_____/| .__/ \___|\___|\__,_|_|\___/ 
                  | |                            
                  |_|                            

==================================================

       Back annotate model parameters
                                     version 0.8.5
    Copyright (c) 2015-2016 by Stanford University
                               ALL RIGHTS RESERVED

This version is only for evaluation purpose. Any
redistribution, modification, or commercial use is 
prohibited without written permission.
For more information, contact bclim@stanford.edu
'''
"""

INFO_002 = 'Run AMS model equivalence checker.'
INFO_003 = 'Test configuration file. Default is "%s"'
INFO_004 = 'Simulation configuration file. Default is "%s"'
INFO_005 = 'Report file name in HTML format. Default is "%s"'
INFO_005_1 = 'Working directory. Default is the current directory'
INFO_006 = 'Number of processes. Default is 1'
INFO_007 = 'Use cached simulation data'
INFO_007_1 = 'No on-the-fly pin check'
INFO_008 = 'Start GUI application'
INFO_008_1 = 'Extraction mode: Characterize golden model.'
INFO_008_2 = 'Cross reference file of modules. Default is "%s"'
INFO_009 = 'Model checking is completed'
INFO_009_1 = 'Circuit characterization is completed'
INFO_010 = 'Start GUI application.'
INFO_011 = 'Terminate GUI application.'
INFO_012 = 'List of Tests'
INFO_013 = 'Report in %s'
INFO_014 = 'Running a test: %s'
INFO_015 = "\nTest directory '%s' is deleted"
INFO_016 = 'End of test (%s)'
INFO_017 = 'Test Error Summary %s'
INFO_018 = '(Suggested model)'
INFO_019 = "Because there exists %d subregions or you're using 'regions' keyword on analog ports, the original test configuration %s is subdvided into from %s_0 to %s_%d"
INFO_020 = 'AMS model equivalence checker'
INFO_021 = 'End of testing the mode (%s)'
INFO_022 = 'Running simulations with the generated test vectors'
INFO_023 = 'Retrieve cached simulation data (--use-cache enabled)'
INFO_024 = 'Test vector (%d/%d) = %s'
INFO_025 = '%s Measurement (%d/%d)= %s'
INFO_026 = 'List of vector/response of the %s model'
INFO_027 = 'Performing linear regression for checking model accuracy'
INFO_027_1 = 'Performing linear regression for detecting pin-level discrepancy'
INFO_028 = 'Generating suggested model with input sensitivity constraint for checking model accuracy'
INFO_028_1 = 'Generating suggested model for detecting pin-level discrepancy'
INFO_029 = '%s Linear regression summary' 
INFO_030 = '%s Extracted linear model equation' 
INFO_030_1 = '%s Extracted linear model equation for simple pin discrepancy check' 
INFO_031 = "Storing regression samples of the %s model to '%s'." 
INFO_032 = 'Labeling port'
INFO_033 = 'For port information, see the report file.'
INFO_034 = 'Check wires'

INFO_035 = ''

INFO_036 = 'Generating test vectors'
INFO_037 = 'Minimum required test vectors by linearity assumption: %d'
INFO_038 = 'Minimum test vectors set by user: %d' 
INFO_039 = 'Number of analog grid is adjusted to %d (1 + maximum bit width of quantized analog inputs)' 
INFO_036_1 = 'Maximum number of samples set by user: %d'
INFO_036_1_1 = 'Maximum number of samples is adjusted to: %d'
INFO_036_2= 'Maximum number of samples (with possible adjustment): %d'
INFO_036_3= 'Calculated number of analog grid: %d'
INFO_036_4= 'OA vector size with the number of analog grid (%d): %d'
INFO_040 = 'List of true digital mode vectors'
INFO_041 = 'List of (quantized) analog vectors'
INFO_042 = 'Loading cached test vectors (--use-cache enabled)'
INFO_043 = 'Creating a testbench from Cadence is %s'
INFO_044 = 'unsuccessful. Check out the error message below.'
INFO_045 = '\nNumber of generated test vectors in each digital mode: %d'
INFO_046 = "Generation of mProbo testbench from Cadence's Virtuoso schematic."
INFO_047 = 'CDS cell to extract in libname:cellname:viewname format, required'
INFO_048 = 'Directory where cds.lib file is located at. Default is current directory'
INFO_049 = 'Port map file of stimulus/measurement modules. Default is %s'
INFO_050 = 'Generated Testbench'
INFO_051 = 'List of variable port'
INFO_052 = 'Generating testbench is completed.'
INFO_053 = '''# INSTALLING AND USING THE SOFTWARE ACCOMPANYING THIS LICENSE FILE INDICATES
# YOUR ACCEPTANCE AND AGREEMENT THAT SUCH INSTALLATION AND USE IS SUBJECT TO
# THE TERMS AND CONDITIONS OF THE CURRENT LICENSE AGREEMENT BETWEEN BYONG 
# CHAN LIM AND YOU/YOUR COMPANY. IF YOU DO NOT AGREE, DELETE THIS
# CORRESPONDENCE AND DO NOT USE THE LICENSE FILE.
'''
INFO_054 = 'Back annotation is completed.'
INFO_055 = '\nCompiling a test configuration for the test, %s.' 
INFO_056 = 'There is no unresolved net.' 
INFO_057 = 'The number of analog grid is set to %d and thus "max_sample" is set to %d.'
INFO_058 = 'Checking summary of a mode (%s)'


WARN_001 = 'The program is interrupted by user. Terminate the program abnormally.'
WARN_002 = "Test directory '%s' is created."
WARN_003 = "Test directory '%s' already exists."
WARN_004 = "The existing test directory is renamed to '%s'."
WARN_005 = "There is no true digital port. A dummy true digital port, 'dummy_digitalmode', is created and set to 'b0'."
WARN_006 = 'The extracted wires mapped in instances are %s.' 
WARN_007 = "The wires declared in 'wire' section of the test configuration file are %s." 
WARN_008 = 'The wires between them are %s.' 
WARN_009 = 'The unmatched wire name%s %s.' 
WARN_010 = "This doesn't necessarily mean that wires are really unmatched; this check does not account for the wire declaration in tb_code section. Please make sure you listed all the wires."
WARN_011 = 'No Orthogonal array table exists for # of variables=%d, depth=%d. Switching to full Latin Hypercube Sampling mode.'
#WARN_012 = 'Random vectors are generated instead of Orthogonal Array.'
WARN_013 = 'Random vectors (%d) are added to the generated Orthogonal Array vectors.'
WARN_014 = '\n\n'+"="*50+'\n'+ 'Reading simulation results failed. See the details below.' +'\n'+"="*50
WARN_015 = "*"*50+'\n'+'Simulation message\n'+"*"*50
WARN_016 = "*"*50+'\n'+'Post-Process routine message\n'+"*"*50
WARN_017 = 'Model formula: %s'
WARN_018 = 'No model exists'
WARN_019 = 'Unknown error is occured. For e.g., check out Virtuoso license and its environment setting'
WARN_020 = 'There are unresolved nets by automatic net extraction: %s, which will be intially assigned to a default nettype (%s).'
WARN_021 = 'Wire (%s,%s) defined in [[[wire]]] section overwrites the wire (%s,%s) extracted from tb_code section.'
WARN_022 = 'Wire (%s,%s) defined in [[[wire]]] section overwrites the unresolved wire (%s,%s).'
WARN_023 = 'There already exists digital mode port(s). Adding dummy digital mode port is ignored.'
WARN_024 = 'For given "max_sample" (%d) and number of analog+quantized analog input ports (%d), the number of analog grid (%d) is smaller than the minimum number of analog grid (%d).'
WARN_025 = "The option, '--use-cache', is enabled, but the simulation directory, %s, doesn't exist. Thus, a simulation will be performed."





DEBUG_001 = "Storing vector/response of the %s model to '%s'."
DEBUG_002 = 'Port Name: %s' 
DEBUG_003 = ' - Constraint %s' 
DEBUG_004 = "Storing digital mode vectors to '%s'." 
DEBUG_005 = "Storing analog vectors to '%s'."
DEBUG_006 = 'base vector for quantized analog: %s'
DEBUG_007 = "Running simulation in '%s' is failed: %s" 
DEBUG_008 = "Running '%s' is successful."
DEBUG_009 = 'List of post processing scripts: %s'
DEBUG_010 = 'Post processing command: %s'
DEBUG_011 = 'workdir: %s'
DEBUG_012 = "Changing directory to '%s' for running post-processing script"
DEBUG_013 = 'Going back to tool running directory'
DEBUG_014 = 'Using cached resuts for post-processing routine.'
DEBUG_015 = 'Run suggested linear regression with confidence interval'
DEBUG_016 = 'Run suggested linear regression with normlized sensitivity'
DEBUG_017 = 'Predictor %s is removed from linear regression of the response, %s, because the predictor is intercept or its confidence interval embraces 0.0'
DEBUG_018 = 'Port class alias named %s does not exist.'
DEBUG_019 = 'Number of available orthogonal vectors with analog discretization levels of %d: %d' 


ERR_001 = 'No test configuration file, %s, exists'
ERR_001_1 = 'No port cross reference file, %s, exists'
ERR_002 = 'No simulation configuration file, %s, exists'
ERR_003 = "You cannot claim both 'goldensim_only' and 'revisedsim_only' parameters to be True"
ERR_004 = 'Direction for %s port is invalid. The allowed I/O type is either input or output'
#ERR_005 = 'bit_width should be a positive integer'
ERR_006 = 'Pinned value for %s port is invalid' 
ERR_007 = 'Trying to get a out-of-index vector' 
ERR_008 = '%s simulator is not supported for %s mode' 
ERR_009 = 'Cannot find closing comment delimiter in '
ERR_010 = 'Error occurred while reading %s.'
ERR_011 = 'The "%s" key in the section "%s" failed validation'
ERR_012 = 'The filename field %s of "%s" should be a string'
ERR_013 = 'The circuit control file %s does not exist'
ERR_014 = 'circuit subsection can only be defined with "%s" model'
ERR_015 = 'The filename field %s for %s subcircuit should be a string'
ERR_016 = 'The circuit netlist file %s does not exist'
ERR_017 = 'Each value in %s field should be a string'
ERR_018 = 'The hdl file %s does not exist' 
ERR_019 = '%s is not defined in %s'
ERR_020 = 'No raw testbench file %s exists'
ERR_021 = 'There are still unresolved nets: %s. Check out port reference file %s and/or [[[wire]]] section.'
ERR_022 = 'Bit width of a quantized analog port cannot be larger than %d.'






MISC_001 = 'Some measurement result(s) is/are out of specification: '
MISC_002 = 'Failed. See the log file'

