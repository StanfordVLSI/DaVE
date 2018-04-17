# Configuration for generating Verilog PWL model 
from sympy import *

# PWL approximation parameters
etol = 0.001   # absolute error tolerance
tmax = 1e-6    # regard this number as infinite time

########################
# Verilog module related
########################
module_name = 'buck' # Verilog module name
include_filename = [] # list of files for `include directive
timeunit = '1fs'  # Verilog time unit
timeprec = '1fs'  # Verilog time precision
dpi_function = [] # DPI-C function list if any. set it to None if nothing

############
# Filter I/O
############
''' Note
  input transition time of digital input is negligible compared to filter bandwidth, so the input signal datatype is a PWC, not PWL
'''
filter_input_datatype = 'real'  # datatype of signal input, real or pwl
filter_output_datatype = 'pwl' # datatype of signal output, real or pwl


###############################################################################
# Transfer function
###############################################################################
# Vo/Vi
s, L, rp, CL, RL = symbols("s L rp CL RL")
equation = s*s+(L+rp*CL*RL)*s/(L*CL*RL)+(rp+RL)/(L*CL*RL)
sol = [-1.0*s for s in roots(equation,s).keys()]

numerator= '1/L/CL/p1/p2'
denumerator= '(s/p1+1)*(s/p2+1)'

###############################################################################
# Other inputs
'''
other_input: list of other input ports. For example, e.g. you may want to 
             adjust the response function with these inputs. 
             Note that datatype is always real for now. 
'''
###############################################################################
other_input = {} 
#user_param = {'rp':0.4, 'RL': 100, 'L':1e-9, 'CL':1e-12, 'p1':'-1.0*('+sol[0]+')', 'p2':'-1.0*('+sol[1]+')'} # user defined parameter if any
user_param = {'rp':0.4, 'RL': 100, 'L':1e-9, 'CL':1e-12, 'p1':sol[0], 'p2':sol[1]} # user defined parameter if any
