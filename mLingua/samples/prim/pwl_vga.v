/****************************************************************

Copyright (c) 2018- Stanford University. All rights reserved.

The information and source code contained herein is the 
property of Stanford University, and may not be disclosed or
reproduced in whole or in part without explicit written 
authorization from Stanford University. Contact bclim@stanford.edu for details.

* Filename   : pwl_vga.v
* Author     : Byongchan Lim (bclim@stanford.edu)
* Description: 
  Variable gain amplifier.

* Note       :

* Revision   :
  - 7/26/2016: First release

****************************************************************/


module pwl_vga (
  `input_real scale,  // gain 
  `input_pwl in,      // signal input
  `output_pwl out     // signal output
);

timeunit `DAVE_TIMEUNIT ;
timeprecision `DAVE_TIMEUNIT ;
 
`protect
//pragma protect 
//pragma protect begin
`get_timeunit
PWLMethod pm=new;

event dummy;
initial -> dummy;

always @(dummy or `pwl_event(in) or scale) out = pm.scale(in, scale, `get_time);

//pragma protect end
`endprotect
endmodule
