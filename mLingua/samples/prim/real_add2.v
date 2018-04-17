/****************************************************************

Copyright (c) 2018- Stanford University. All rights reserved.

The information and source code contained herein is the 
property of Stanford University, and may not be disclosed or
reproduced in whole or in part without explicit written 
authorization from Stanford University. Contact bclim@stanford.edu for details.

* Filename   : real_add2.v
* Author     : Byongchan Lim (bclim@stanford.edu)
* Description: 
  It adds two real signals.

* Note       :

* Revision   :
  - 7/26/2016: First release

****************************************************************/


module real_add2 (
  input enable,   // enable add op., if 'L': keep the output, pull-up when unconnected
  `input_real in1, in2,        // real inputs
  `input_real scale1, scale2,  // scale factor for each input
  `output_real out             // real output
);

timeunit `DAVE_TIMEUNIT ;
timeprecision `DAVE_TIMEUNIT ;
 
`protect
//pragma protect 
//pragma protect begin

pullup(enable);

`get_timeunit

real t;
real out1, out2;
event event_in;

always @(in1 or in2 or scale1 or scale2) -> event_in;

always @(event_in or enable) begin
  if (enable) begin
    t = `get_time;
    out = scale1*in1 + scale2*in2;
  end
end

//pragma protect end
`endprotect

endmodule
