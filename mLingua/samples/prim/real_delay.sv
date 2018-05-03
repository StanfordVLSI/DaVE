/****************************************************************

Copyright (c) #YEAR# #LICENSOR#. All rights reserved.

The information and source code contained herein is the 
property of #LICENSOR#, and may not be disclosed or
reproduced in whole or in part without explicit written 
authorization from #LICENSOR#. Contact #EMAIL# for details.

* Filename   : real_delay.sv
* Author     : Byongchan Lim (bclim@stanford.edu)
* Description: 
  - It delays a real signal.

* Note       :

* Revision   :
  - 00/00/2018: First release

****************************************************************/


module real_delay #(
  parameter real delay = 1.0,   // dealy in sec.
  parameter real scale = 1.0   // scale factor of input,
) (
  `input_real in,      // pwl inputs
  `output_real out     // pwl output
);

timeunit `DAVE_TIMEUNIT ;
timeprecision `DAVE_TIMEUNIT ;
 
`protect
//pragma protect 
//pragma protect begin

always @(in)
  if ($realtime==0) out = in;
  else out <= #(delay*1s) in;

//pragma protect end
`endprotect

endmodule
