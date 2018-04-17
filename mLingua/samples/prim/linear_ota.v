/****************************************************************

Copyright (c) 2018- Stanford University. All rights reserved.

The information and source code contained herein is the 
property of Stanford University, and may not be disclosed or
reproduced in whole or in part without explicit written 
authorization from Stanford University. Contact bclim@stanford.edu for details.

* Filename   : linear_ota_cloop.v
* Author     : Byongchan Lim (bclim@stanford.edu)
* Description: Open-loop linear OTA with single-ended output

* Note       :
  - No gain compression, slew is incorporated
  - Dominant pole approximation for dynamic behavior

* Revision   :
  - 7/26/2016: First release

****************************************************************/

module linear_ota #(
  parameter real av = 1e6,  // open-loop DC gain
  parameter real fp = 10e6,  // pole location in Hz
  parameter real vos = 0.0, // input referred static offset voltage
  parameter real etol = 0.001  // error tolerance of a filter 
) (
  `input_pwl inp, // positive input
  `input_pwl inm, // negative input
  `output_pwl out // output
);

timeunit `DAVE_TIMEUNIT ;
timeprecision `DAVE_TIMEUNIT ;

`protect
//pragma protect 
//pragma protect begin

`get_timeunit
PWLMethod pm=new;

//----- BODY STARTS HERE -----

//----- SIGNAL DECLARATION -----

pwl v_id; // differential inputs
pwl offset = '{vos,0,0};

//----- FUNCTIONAL DESCRIPTION -----

// diff sense considering input referred offset
pwl_add #(.no_sig(3)) uIDIFF (.in('{inp,inm,offset}), .scale('{av,-av,av}), .out(v_id));
pwl_filter_real_w_reset #(.etol(etol), .en_filter(1'b1), .filter(0)) uFILTER (.fp1(fp), .in(v_id), .out(out) ); // output filtering

//pragma protect end
`endprotect

endmodule
