/****************************************************************

Copyright (c) 2018- Stanford University. All rights reserved.

The information and source code contained herein is the 
property of Stanford University, and may not be disclosed or
reproduced in whole or in part without explicit written 
authorization from Stanford University. Contact bclim@stanford.edu for details.

* Filename   : pwl_spf.v
* Author     : Byongchan Lim (bclim@stanford.edu)
* Description: 
  A low pass filter with a single pole. 

* Note       :

* Revision   :
  - 7/26/2016: First release

****************************************************************/


module pwl_spf #(
  parameter real etol = 0.005,       // error tolerance of PWL approximation
  parameter real gain = 1,           // dc gain
  parameter real w1 = 2*`M_PI*500e6, // pole location in radian for in to out path
  parameter real wrst = w1,          // pole location in radian for rst to out path
  parameter en_filter = 1'b1         // enable output filtering
) (
  `input_pwl in, // filter signal input
  `input_pwl reset_sig, // reset value
  input reset,         // reset "out" to 'reset_sig' value, 'L' when unconnected
  `output_pwl out // filter signal output
);

timeunit `DAVE_TIMEUNIT ;
timeprecision `DAVE_TIMEUNIT ;

`protect
//pragma protect 
//pragma protect begin

pwl_filter_real_w_reset #(.etol(etol), .filter(0), .en_filter(en_filter)) xinst (.in(in), .in_rst(reset_sig), .out(out), .fp1(w1/`M_TWO_PI), .reset(reset));

//pragma protect end
`endprotect

endmodule
