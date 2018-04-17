/****************************************************************

Copyright (c) #YEAR# #LICENSOR#. All rights reserved.

The information and source code contained herein is the 
property of #LICENSOR#, and may not be disclosed or
reproduced in whole or in part without explicit written 
authorization from #LICENSOR#.

* Filename   : delay.template.sv
* Author     : Byongchan Lim (info@joey-eda-consulting.com)
* Description: SV template for a delay cell

* Note       :

* Todo       :
  - 

* Revision   :
  - 00/00/00 : 

****************************************************************/

module $$(Module.name()) #(
// parameters here
  $$(Module.parameters())
) (
  $$(Module.pins())
);

`get_timeunit
PWLMethod pm=new;

$$Pin.print_map() $$# map between user pin names and generic ones

//---SNIPPET ON
///////////////////
// CODE STARTS HERE
///////////////////

$$# //--- any messages during generation
$$# //--- ensure that in/out data types match
$${
in_datatype = Pin.datatype('in')
out_datatype = Pin.datatype('out')
if in_datatype != out_datatype:
  print_error_message('The data types of in/out do not match')
  sys.exit()
}$$
$$#------------------------------------------------------------------------
$$#  Terminology
$$#  
$$#  "generic pin"  : pins that exist in a template interface
$$#   - "essential pin" : generic and must present in the generated model 
$$#   - "optional pin"  : don't have to be present in the generated model
$$#                       either user pin or generic pin in a template with (is_optional=True)
$$#  "user pin"     : pins added by user in a user interface
$$#  
$$#  "control pin"  : pins that tune the functional parameters
$$#                   all user pins are control pin, some of the generic pins might be control pin
$$#  Rule:
$$#  1. It is suggested to use "real" for any control analog input
$$#  2. For pwl control analog input, it needs to be discretized with some finite resolution
$$#------------------------------------------------------------------------

//----- wires, assignment
real td;  // the amount of delay
$$PWL.declare_optional_analog_pins_in_real() $$# real datatype declaration for discretizing pwl inputs 

//----- body
`protect
//pragma protect 
//pragma protect begin

//-- system's parameter 

// discretization of control inputs
$$PWL.instantiate_pwl2real_optional_analog_pins()

// update parameters as control inputs/mode inputs change

$${
'''
// * Model parameter mapping for back-annotating regression models to Verilog
// : The back-annotation is done using an API function call, 'annotate_modelparam()'.
// : Regression models of functional parameters can be extracted using either mProbo or
//   other tools. Each regression model defines a mathematical relationship between
//   a system's property (functional parameter) and inputs to this system (predictor variables). 
// : Sometimes, the variable names in regression models are different from those of Verilog models.
//   Therefore, it is necessary to define a map between them.
// : Two dictionaries are arguments of 'annotate_modelparam()' API function call. The first defines
//   the name mapping of response variables and the second does that of predictor variables.
// 1. Response variable name mapping
//   - For each test, named testname below, multiple responses are mapped using a child dictionary.
//       {testname:{response1:verilog variable being mapped to,response2:verilog name2}, ... }
// 2. Predictor variable name mapping
//   - A dictionary defines the relationship between a predictor variable name and its corresponding
//     Verilog name as follows:
//       { var1 : Verilog_var1, var2 : Verilog_var2, ... }
//   - e.g. 
//       variable_map = dict([(p,p) for p in Pin.list_optional_analog() if Pin.datatype(p)=='real'])
//   - If the relationship is not defined, the generator will assume that the two variables match.
//   - The exception is when the data type of a signal is "PWL" and var is the same as its pin name.
//     In that case, Verilog_var will be assigned using PWL.get_real(var) in an API function call.
'''


# sensitivity list of always @ statement
sensitivity = get_sensitivity_list() # get a sensitivity list of always @() statement below

model_param_map = { 'test1': {'delay':'td'} } 

#################
}$$

always @($$print_sensitivity_list(sensitivity)) begin
  t0 = `get_time;
$$annotate_modelparam(model_param_map, {})
end

//-- functional behavior
// delay input signal by "td" in second

$$[if in_datatype == 'pwl']
pwl_delay_prim #( .scale(1.0) ) iDELAY ( .in(in), .out(out), .delay(td) );
$$[else if in_datatype in ['real', 'logic']]
always @(in) out <= `delay(td) in;
$$[end if]

//pragma protect end
`endprotect
//---SNIPPET OFF
endmodule
