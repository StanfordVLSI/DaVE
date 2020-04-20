/****************************************************************

Copyright (c) 2018- Stanford University. All rights reserved.

The information and source code contained herein is the 
property of Stanford University, and may not be disclosed or
reproduced in whole or in part without explicit written 
authorization from Stanford University. Contact bclim@stanford.edu for details.

* Filename   : pwl_filter_real_w_reset.v
* Author     : Byongchan Lim (bclim@stanford.edu)
* Description: 
  - A linear filter primitive cell. It is almost the same as 
    "pwl_filter_real_prime" cell. The difference is that
    (i) one can assign the pole frequency of reset path, and
    (ii) assigning filter type is done statically.

* Note       :

* Revision   :
  - 7/26/2016: First release

****************************************************************/

`include "mLingua_pwl.vh"

module pwl_filter_real_w_reset #(
  parameter real gain = 1.0,    // dc gain
  parameter real etol = 0.005,   // error tolerance of PWL approximation
  parameter integer filter = 0,  // filter type of main I/O path (in-to-out), 
                                 // 0: a pole, 1: two-poles, 2: two-poles and a zero
  parameter en_filter = 1'b1     // enable output event filtering
) (
  // filter I/Os
  `input_pwl in,     // filter signal input
  `input_pwl in_rst, // reset input
  `output_pwl out,   // filter signal output
  // parameters
  `input_real fp1, fp2, fz1, // poles and zero in Hz from in to out
  `input_real fp_rst,        // pole in Hz from in_rst to out
  // mode
  input en_complex,  // poles are complex conjugates
  input reset // reset the output state to 'in_rst' value, set to 'L' when unconnected
);

timeunit `DAVE_TIMEUNIT ;
timeprecision `DAVE_TIMEUNIT ;

`get_timeunit // get timeunit in sec and assign it to the variable 'TU'
PWLMethod pm=new; // Method for PWL signal processing

// wires
integer filter_type=0;
pwl si; // muxed input
real wp1;

pulldown (reset);

always @(reset or `pwl_event(in_rst) or `pwl_event(in)) 
  if (reset) begin
    si = pm.scale(in_rst, gain, `get_time); 
    if (fp_rst == 0.0) wp1 = 1.0/TU;
    else wp1 = fp_rst*`M_TWO_PI; 
    filter_type = 1'b0;
  end
  else begin
    si = pm.scale(in, gain, `get_time); wp1 = fp1*`M_TWO_PI; filter_type = filter;
  end

pwl_filter_real_prime #(
    .etol(etol),
    .en_filter(en_filter)
) xfilter (
    .in(si),
    .out(out),
    .wp1(wp1),
    .wp2(`M_TWO_PI*fp2),
    .wz1(`M_TWO_PI*fz1),
    .filter_type(filter_type),
    .en_complex(en_complex)
);

endmodule
