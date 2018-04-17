/****************************************************************

Copyright (c) 2018- Stanford University. All rights reserved.

The information and source code contained herein is the 
property of Stanford University, and may not be disclosed or
reproduced in whole or in part without explicit written 
authorization from Stanford University. Contact bclim@stanford.edu for details.

* Filename   : bit2real.v
* Author     : Byongchan Lim (bclim@stanford.edu)
* Description:
  - bit2real converts a logic signal to a real signal. 

* Note       :

* Revision   :
  - 7/26/2016: First release
  
****************************************************************/


module bit2real #(
  parameter real vh=1.0,  // value corresponds to logic 'H'
  parameter real vl=0.0   // value corresponds to logic 'L'
) (
  input in,
  `output_real out, outb
);

timeunit `DAVE_TIMEUNIT ;
timeprecision `DAVE_TIMEUNIT ;

assign out = in ? vh : vl;
assign outb = in ? vl : vh;

endmodule
