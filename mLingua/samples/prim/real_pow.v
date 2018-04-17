/****************************************************************

Copyright (c) 2018- Stanford University. All rights reserved.

The information and source code contained herein is the 
property of Stanford University, and may not be disclosed or
reproduced in whole or in part without explicit written 
authorization from Stanford University. Contact bclim@stanford.edu for details.

* Filename   : real_pow.v
* Author     : Byongchan Lim (bclim@stanford.edu)
* Description: 
  It outputs in**(powf).

* Note       :

* Revision   :
  - 7/26/2016: First release

****************************************************************/

module real_pow (
  `input_real in,
  `input_real powf,
  `output_real out
);

timeunit `DAVE_TIMEUNIT ;
timeprecision `DAVE_TIMEUNIT ;
 
assign out = in**powf;

endmodule
