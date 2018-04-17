/****************************************************************

Copyright (c) 2018- Stanford University. All rights reserved.

The information and source code contained herein is the 
property of Stanford University, and may not be disclosed or
reproduced in whole or in part without explicit written 
authorization from Stanford University. Contact bclim@stanford.edu for details.

* Filename   : check_a2d.v
* Author     : Byongchan Lim (bclim@stanford.edu)
* Description: A wrapper for checking a slicer (comparator) in
  mProbo.
  - Ensure that "virclk" has a cycle delay for correct operation.

* Note       :

* Revision   :
  - 7/26/2016: First release

****************************************************************/

`timescale `DAVE_TIMEUNIT / `DAVE_TIMEUNIT

///////////
`ifndef AMS // NOT AMS
///////////


module check_a2d #(
  parameter integer invert = 0,  // 0 if a comparator is non-inverting
  parameter real voffset_max = 0.2, // abs of possible offset of a comparator
  parameter real vlth = 0.5  // logic threshold of digital signal (nothing for SV)
) (
  `input_pwl vdd,  // supply
  `input_pwl vinp,  // + input
  `input_pwl vinn,  // - input
  input comp_out,    // comparator's digital output 
  input virclk,  // clock input for running recursive 1-bit DAC
  `output_pwl inp_comp, // comparator's actual + input
  `output_pwl inn_comp, // comparator's actual - input
  `output_pwl d2a_out, // transformed analog output (diff) of an comparator, (vinp-vinn), for non-inverting
  `output_pwl d2a_offset // transformed analog output (offset) of an comparator
);
`get_timeunit

PWLMethod pm=new;

localparam real dv_sign = invert ? 1.0 : -1.0 ; 

real t0;
pwl vin_diff, vin_cm;  // diff & common mode voltages of vinp & vinn
pwl vcomp_diff; 
real dv, abs_dv_prev;  // delta V and its previous state for voltage step(dv) of vcomp_diff 
logic skip=1;


pwl_add2 xadd1 (.in1(vinp), .in2(vinn), .scale1(1.0), .scale2(-1.0), .out(vin_diff));
pwl_add2 xadd2 (.in1(vinp), .in2(vinn), .scale1(0.5), .scale2(0.5), .out(vin_cm));
pwl_add3 xadd3 (.in1(vin_cm), .in2(vcomp_diff), .in3(vin_diff), .scale1(1.0), .scale2(0.5), .scale3(0.5), .out(inp_comp));
pwl_add3 xadd4 (.in1(vin_cm), .in2(vcomp_diff), .in3(vin_diff), .scale1(1.0), .scale2(-0.5), .scale3(-0.5), .out(inn_comp));
pwl_add2 xadd5 (.in1(vcomp_diff), .in2(vin_diff), .scale1(1.0), .scale2(1.0), .out(d2a_offset));

pwl_vga xvga1 (.in(vcomp_diff), .scale(-1.0), .out(d2a_out));

initial abs_dv_prev = fabs(voffset_max)*2.0;

// do binary search
always @(posedge virclk) begin
  if (skip) skip = 1'b0;
  else begin
    t0 = `get_time;
    dv = dv_sign*abs_dv_prev/2.0; dv = comp_out ? dv : -1.0*dv;
    vcomp_diff = pm.write(vcomp_diff.a + dv, 0.0,t0);
    abs_dv_prev = fabs(dv);
  end
end

// take absolute value
function real fabs(input real x);
  if (x < 0.0) fabs = -1.0*x; else fabs = x;
endfunction

endmodule


///////////
`else // AMS
///////////


`include "disciplines.vams"
//`timescale 1fs/1fs
module check_a2d #(
  parameter integer invert = 0,  // 0 if a comparator is non-inverting
  parameter real voffset_max = 0.2, // allowable max vin_diff to comparator
  parameter real vlth = 0.5  // logic threshold of digital signal
) (
  vdd, // supply
  vinp, // + input
  vinn, // - input
  comp_out,    // comparator's digital output 
  virclk,  // clock input for running recursive 1-bit DAC
  inp_comp, // comparator's actual + input
  inn_comp, // comparator's actual - input
  d2a_offset, // transformed analog output (offset) of an comparator
  d2a_out // extacted analog output (differential), (vinp-vinn), for non-inverting
);

input vdd;
input vinp; 
input vinn; 
input comp_out; 
input virclk;
output inp_comp;
output inn_comp;
output d2a_out;
output d2a_offset;  

electrical vdd;
electrical vinp, vinn;
electrical comp_out;
electrical inp_comp, inn_comp;
electrical d2a_out, d2a_offset;


parameter vtol = 0.00001;
parameter ttol = 1e-12;

localparam real dv_sign = invert ? 1.0 : -1.0 ;

reg comp_out_dig;
real vin_diff, vin_cm;
real vcomp_diff; // actual differential input for comparator
real dv, abs_dv_prev;  // delta V and its previous state for voltage step(dv) of vcomp_diff 
real d2a_r, d2a_offset_r;
reg skip=1;

// no initialization for comp_out_dig ???

always @(above(V(comp_out)-vlth*V(vdd), ttol, vtol)) comp_out_dig = 1'b1;
always @(above(vlth*V(vdd)-V(comp_out), ttol, vtol)) comp_out_dig = 1'b0;

initial abs_dv_prev = fabs(voffset_max)*2.0;
initial vcomp_diff = 0.0;

analog begin
  //@(initial_step) 
  //  if (V(comp_out)-vlth*V(vdd)) comp_out_dig = 1'b1;
  //  else comp_out_dig = 1'b0;
  //@(above(V(comp_out)-vlth*V(vdd), ttol, vtol)) comp_out_dig = 1'b1;
  //@(above(vlth*V(vdd)-V(comp_out), ttol, vtol)) comp_out_dig = 1'b0;
  vin_diff = V(vinp)-V(vinn);
  vin_cm = (V(vinp)+V(vinn))/2.0;
  V(inp_comp) <+ vin_cm + vcomp_diff/2.0 + vin_diff/2.0;
  V(inn_comp) <+ vin_cm - vcomp_diff/2.0 - vin_diff/2.0;
  V(d2a_out) <+ d2a_r;
  V(d2a_offset) <+ d2a_offset_r;
end

// do binary search
always @(posedge virclk) begin
  if (skip) skip = 1'b0;
  else begin
    dv = dv_sign*abs_dv_prev/2.0; dv = comp_out_dig ? dv : -1.0*dv;
    vcomp_diff = vcomp_diff + dv;
    abs_dv_prev = fabs(dv);
    d2a_offset_r = vcomp_diff + vin_diff;
    d2a_r = -1.0*vcomp_diff;
  end
end

function real fabs(input real x);
  if (x < 0.0) fabs = -1.0*x; else fabs = x;
endfunction

endmodule


///////////
`endif
///////////
