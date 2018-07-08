/****************************************************************

Copyright (c) 2018 Stanford University. All rights reserved.

The information and source code contained herein is the 
property of Stanford University, and may not be disclosed or
reproduced in whole or in part without explicit written 
authorization from Stanford University. Contact #EMAIL# for details.

* Filename   : pwl_delay.v
* Author     : Byongchan Lim (bclim@stanford.edu)
* Description: 
  - It delays a pwl signal.

* Note       :

* Revision   :
  - 7/26/2016: First release

****************************************************************/


module pwl_delay #(
  parameter real delay = 1.0,   // dealy in sec.
  parameter real scale = 1.0   // scale factor of input,
) (
  `input_pwl in,      // pwl inputs
  `output_pwl out     // pwl output
);

timeunit `DAVE_TIMEUNIT ;
timeprecision `DAVE_TIMEUNIT ;
 
`protect
//pragma protect 
//pragma protect begin

always @(`pwl_event(in)) 
  if ($realtime==0) out = in;
  else out <= #(delay*1s) pm.write(scale*in.a, scale*in.b, delay+in.t0);

//pragma protect end
`endprotect

endmodule
