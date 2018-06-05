/****************************************************************

Copyright (c) #YEAR# #LICENSOR#. All rights reserved.

The information and source code contained herein is the 
property of #LICENSOR#, and may not be disclosed or
reproduced in whole or in part without explicit written 
authorization from #LICENSOR#.

* Filename   : amplifier.template.sv
* Author     : Byongchan Lim (info@joey-eda-consulting.com)
* Description: SV template for an amplifier cell

* Note       :

* Todo       :
  - 

* Revision   :
  - 00/00/00 : 

****************************************************************/
/*******************************************************
* An amplifier with possible output equalization
* - Input referred voltage offset as a static parameter
* - Gain Compression
* - Dynamic behavior (a pole or two-poles with a zero)
* - 

* Calibrating metrics:
* 1. Av = gm*Rout 
* 2. Max output swing = Itail*Rout 
* 3. fp1, fp2, fz1
*******************************************************/

module $$(Module.name()) #(
  $$(Module.parameters())
) (
  $$(Module.pins())
);


`protect
//pragma protect 
//pragma protect begin

`get_timeunit
PWLMethod pm=new;

$$Pin.print_map() $$# map between user pin names and generic ones

//----- BODY STARTS HERE -----

//----- SIGNAL DECLARATION -----
pwl ONE = `PWL1;
pwl ZERO = `PWL0;

pwl v_id_lim;   // limited v_id 
pwl v_oc; // output common-mode voltage
pwl v_od; // output differential voltage
pwl vid_max, vid_min; // max/min of v_id for slewing 
pwl vop, von;
pwl v_od_filtered;
pwl vop_lim, von_lim;
pwl v_id, v_icm; // differential and common-mode inputs

real t0;
real v_icm_r;
real vdd_r;
$$PWL.declare_optional_analog_pins_in_real()

real fz1, fp1, fp2; // at most, two poles and a zero
real Av;    // voltage gain (gm*Rout)
real max_swing; // Max voltage swing of an output (Itail*Rout)
real vid_r; // vid<|vid_r| (max_swing/Av)
real v_oc_r;  // common-mode output voltage

event wakeup;

//----- FUNCTIONAL DESCRIPTION -----

initial ->> wakeup; // dummy event for ignition at t=0

//-- Compute differential and common-mode voltages 

  pwl _v_id[3]; pwl _v_icm[2]; real _k_v_id[3]; real _k_v_icm[2];
  assign _k_v_id = '{1.0, -1.0, v_os};
  assign _k_v_icm = '{0.5, 0.5};
  assign _v_id = '{inp, inn, ONE};
  assign _v_icm = '{inp, inn};
// diff/cm sense considering input referred offset
pwl_add #(.no_sig(3)) xidiff (.in(_v_id), .scale(_k_v_id), .out(v_id));
pwl_add #(.no_sig(2)) xicm (.in(_v_icm), .scale(_k_v_icm), .out(v_icm));


//-- System's parameter calculation

// discretization of control inputs
$$PWL.instantiate_pwl2real('v_icm')
$$PWL.instantiate_pwl2real('vdd')
$$PWL.instantiate_pwl2real_optional_analog_pins(['vss'] if Pin.is_exist('vss') else [])

// updating parameters as control inputs/mode inputs change

$${
# sensitivity list of always @ statement
sensitivity = ['v_icm_r', 'vdd_r', 'wakeup'] + get_sensitivity_list() 

# model parameter mapping for back-annotation
# { testname : { test output : Verilog variable being mapped to } }
model_param_map = { 'test1': {'dcgain': 'Av'}, 'test3': {'v_oc': 'v_oc_r'} }
if Metric.is_exist('filter'):
  ftype = Metric.value('filter')
  if ftype == 'p1':
    model_param_map['test1'].update({'fp1': 'fp1'})
    filter_type = 0
  elif ftype == 'p2':
    model_param_map['test1'].update({'fp1': 'fp1', 'fp2': 'fp2'})
    filter_type = 1
  elif ftype == 'p2z1':
    model_param_map['test1'].update({'fp1': 'fp1', 'fp2': 'fp2', 'fz1': 'fz1'})
    filter_type = 2
  
if Metric.is_exist('compression'):
  model_param_map['test2']={'max_swing': 'max_swing'}

iv_map = {'v_icm': 'v_icm_r'}
}$$

always @($$print_sensitivity_list(sensitivity)) begin
  t0 = `get_time;

$$annotate_modelparam(model_param_map, iv_map)

$$[if Metric.is_exist('compression')]
  vid_r = max_swing/Av;
  vid_max = '{vid_r,0,t0};       // max input 
  vid_min = '{-1.0*vid_r,0,t0};  // min input
$$[end if]
end

//-- Model behaviors

$$[if Metric.is_exist("compression")]
pwl_limiter xi_lim (.scale(ONE), .maxout(vid_max), .minout(vid_min), .in(v_id), .out(v_id_lim)); // limiting input range for modeling gm compression 
$$[else]
assign v_id_lim = v_id; // gain compression is not implemented
$$[end if]

pwl_vga xgain (.in(v_id_lim), .scale(Av), .out(v_od)); // differential-mode gain stage 

$$[if Metric.is_exist('filter')]
pwl_filter_real_w_reset #(.etol(etol_f), .en_filter(1'b1), .filter($$filter_type)) xfilter (.fz1(fz1), .fp1(fp1), .fp2(fp2), .fp_rst(0.0), .in(v_od), .in_rst(ZERO), .out(v_od_filtered), .reset(1'b0)); // differential output filtering
$$[else]
assign v_od_filtered = v_od;  // filtering behavior is not implemented
$$[end if]

real2pwl #(.tr(10e-12)) r2poc (.in(v_oc_r), .out(v_oc)); // output common-mode voltage

// combine differential and common-mode output
  pwl _v_od[2]; real _k_v_od_1[2]; real _k_v_od_2[2];
  assign _v_od = '{v_oc, v_od_filtered};
$$[if Pin.is_exist('outn')]
  assign _k_v_od_1 = '{1.0, 0.5};
  assign _k_v_od_2 = '{1.0, -0.5};
pwl_add #(.no_sig(2)) xoutp (.in(_v_od), .scale(_k_v_od_1), .out(outp));
pwl_add #(.no_sig(2)) xoutn (.in(_v_od), .scale(_k_v_od_2), .out(outn));
$$[else]
  assign _k_v_od_1 = '{1.0, 1.0};
pwl_add #(.no_sig(2)) xoutp (.in(_v_od), .scale(_k_v_od_1), .out(outp));
$$[end if]

//pragma protect end
`endprotect

endmodule
