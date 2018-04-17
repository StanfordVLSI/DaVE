/****************************************************************

Copyright (c) 2018- Stanford University. All rights reserved.

The information and source code contained herein is the 
property of Stanford University, and may not be disclosed or
reproduced in whole or in part without explicit written 
authorization from Stanford University. Contact bclim@stanford.edu for details.

* Filename   : pwl_sin.v
* Author     : Byongchan Lim (bclim@stanford.edu)
* Description: 
  It generates a sine wave.

* Note       :

* Revision   :
  - 7/26/2016: First release

****************************************************************/


module pwl_sin #(
  parameter real etol = 0.001,  // error tolerance of PWL approximation
  parameter real freq = 100e6,  // frequency
  parameter real amp  = 0.01,   // amplitude
  parameter real offset = 0.01, // DC offset
  parameter real ph   = 0.0     // initial phase in degree
) (
  `output_pwl out // sine output in pwl
);

timeunit `DAVE_TIMEUNIT ;
timeprecision `DAVE_TIMEUNIT ;

pwl_cos #(.etol(etol), .freq(freq), .amp(amp), .offset(offset), .ph(ph-90)) pwlcos(.out(out));

endmodule
