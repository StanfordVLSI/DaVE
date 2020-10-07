/****************************************************************

Copyright (c) 2018- Stanford University. All rights reserved.

The information and source code contained herein is the 
property of Stanford University, and may not be disclosed or
reproduced in whole or in part without explicit written 
authorization from Stanford University. Contact bclim@stanford.edu for details.

* Filename   : pwl_filter_real_p1.v
* Author     : Byongchan Lim (bclim@stanford.edu)
* Description: 
  - A low pass filter with a single pole.

* Note       :

* Revision   :
  - 7/26/2016: First release

****************************************************************/

`include "mLingua_pwl.vh"

module pwl_filter_real_p1 #(
  parameter etol = 0.005,     // error tolerance of PWL approximation
  parameter en_filter = 1'b1  // enable output event filtering
) (
  `input_real fp,  // pole location in Hz
  `input_pwl in,   // filter input 
  `output_pwl out  // filter output 
);

timeunit `DAVE_TIMEUNIT ;
timeprecision `DAVE_TIMEUNIT ;

//`protect
//pragma protect 
//pragma protect begin

pwl_filter_real_w_reset #(.etol(etol), .filter(0), .en_filter(en_filter)) xinst (.in(in), .out(out), .fp1(fp));

//pragma protect end
//`endprotect

endmodule
