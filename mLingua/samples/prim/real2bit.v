/****************************************************************

Copyright (c) 2018- Stanford University. All rights reserved.

The information and source code contained herein is the 
property of Stanford University, and may not be disclosed or
reproduced in whole or in part without explicit written 
authorization from Stanford University. Contact bclim@stanford.edu for details.

* Filename   : real2bit.v
* Author     : Byongchan Lim (bclim@stanford.edu)
* Description:
  - real2bit converts a real signal to a logic signal. 

* Note       :

* Revision   :
  - 7/26/2016: First release
  
****************************************************************/


module real2bit #(
  parameter real vlth=0.5  // logic threshold 
) (
  `input_real in,
  output logic out, outb
);

timeunit `DAVE_TIMEUNIT ;
timeprecision `DAVE_TIMEUNIT ;

assign outb = ~out;
always @(in) out = (in>=vlth) ? 1'b1 : 1'b0;

endmodule
