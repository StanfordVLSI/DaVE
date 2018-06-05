/****************************************************************

Copyright (c) 2016-2018 Stanford University. All rights reserved.

The information and source code contained herein is the 
property of Stanford University, and may not be disclosed or
reproduced in whole or in part without explicit written 
authorization from Stanford University.

* Filename   : oscillator.template.sv
* Author     : Byongchan Lim (bclim@stanford.edu)
* Description: Generic oscillator template

* Note       :
  - Gain compression is valid only if 'actl' generic pin exists

* Todo       :

* Revision   :
  - 00/00/00: Initial commit

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

//----- wires, assignment
pwl PWL1 = `PWL1;
pwl phase;  // [0, modulo*2.0)
pwl freq;   // instantaneous frequency
pwl actl_lmt; // limited range of actl

real t0;  // temp time var.
real vdd_r;
real vss_r;
$$PWL.declare_optional_analog_pins_in_real() $$# discretize extra control inputs

$$[if Pin.is_exist('actl')]
real kvco;
real freq_os;
real actl_ctr;
real freq_ctr;
$$[if Metric.is_exist('compression')]
real vi_min, vi_max;
pwl actl_min, actl_max;
real freq_max, freq_min;
$$[else]
real actl_ctr;
real freq_ctr;
$$[end if]
$$[else]
real freqout;
$$[end if]

$$[if Pin.is_exist('outn')]
assign outn = ~outp;
$$[end if]

//----- body
`protect
//pragma protect 
//pragma protect begin

//-- system's parameter 

localparam real etol_vdd = etol_v;
localparam real etol_vss = etol_v;

// discretization of control inputs
$$PWL.instantiate_pwl2real('vdd')
$$#PWL.instantiate_pwl2real('vss')
$$PWL.instantiate_pwl2real_optional_analog_pins(exclude=['actl'])
$$PWL.instantiate_pwl2real_optional_analog_pins(exclude=['actl', 'vss'] if Pin.is_exist('vss') else ['actl'])


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
sensitivity = ['vdd_r', 'vss_r'] + get_sensitivity_list() # get a sensitivity list of always @() statement below
# sensitivity list of always @ statement
#sensitivity = ['vdd_r', 'vss_r'] + PWL.list_real_optional_analog_pins(exclude=['actl']) + Pin.list_optional_digital()

# variable map for real inputs
iv_map = dict([(p,p) for p in Pin.list_optional_analog() if Pin.datatype(p)=='real'])

# model parameter mapping for back-annotation
# { testname : { test output : Verilog variable being mapped to } }
if Pin.is_exist('actl'):
  model_param_map = { 'test2': {'kvco':'kvco','actl_ctr': 'actl_ctr', 'freqout_ctr': 'freq_ctr'} }
  if Metric.is_exist('compression'):
    model_param_map['test2'].update({'actl_max':'vi_max', 'actl_min':'vi_min', 'freqout_max': 'freq_max', 'freqout_min': 'freq_min'})
else:
  model_param_map = { 'test1': {'freqout':'freqout'} }

#################
}$$

always @($$print_sensitivity_list(sensitivity)) begin
$$annotate_modelparam(model_param_map, iv_map)
$$[if Pin.is_exist('actl')]
  freq_os = freq_ctr - kvco*actl_ctr; // frequency at vi=0
$$[if Metric.is_exist('compression')]
  actl_min = '{vi_min,0,0};
  actl_max = '{vi_max,0,0};
$$[end if]
$$[end if]
end


// calculate frequency in pwl
$$[if Pin.is_exist('actl')]
$$[if Metric.is_exist('compression')]
pwl_limiter uLIM0 ( .scale(PWL1), .maxout(actl_max), .minout(actl_min), .in(actl), .out(actl_lmt) );
$$[else]
assign actl_lmt = actl;
$$[end if]
  pwl _freq[2]; real _k_freq[2];
  assign _freq = '{actl_lmt, PWL1};
  assign _k_freq = '{kvco, freq_os};
pwl_add #(.no_sig(2)) uFREQ ( .enable(), .in(_freq), .scale(_k_freq), .out(freq) );
$$[else]
pwl_vga uFREQ ( .scale(freqout), .in(PWL1), .out(freq) );
$$[end if]

// frequency-to-phase
pwl_integrator_w_reset #(.etol(etol_ph), .modulo(0.5), .noise(jitter), .en_filter(0)) uph2ck ( .gain(1.0), .si(freq), .so(phase), .trigger(outp), .reset(1'b0), .reset_sig() );

//pragma protect end
`endprotect
endmodule
