/****************************************************************

Copyright (c) 2018- Stanford University. All rights reserved.

The information and source code contained herein is the 
property of Stanford University, and may not be disclosed or
reproduced in whole or in part without explicit written 
authorization from Stanford University. Contact bclim@stanford.edu for details.

* Filename   : pwl_abs.v
* Author     : Byongchan Lim (bclim@stanford.edu)
* Description: 
  This takes absolute value of a PWL input.

* Note       :

* Revision   :
  - 0/00/2018: First release

****************************************************************/


module pwl_abs #(
) (
  `input_real scale, // gain, must be positive
  `input_pwl in,   // input
  `output_pwl out, // abs(in)
  output logic is_positive  // flag indicates in is positive if 1
);

timeunit `DAVE_TIMEUNIT ;
timeprecision `DAVE_TIMEUNIT ;

`protect
//pragma protect 
//pragma protect begin

`get_timeunit // get timeunit in sec and assign it to the variable 'TU'
PWLMethod pm=new;

real gain;

pwl_slicer #( .offset(0.0) ) iSLICE ( .vin(in), .out(is_positive) );

always @(is_positive, `pwl_event(in), scale) begin
  if (is_positive) gain = scale;
  else gain = -1.0*scale;
  out = pm.scale(in, gain, `get_time);
end

//pragma protect end
`endprotect

endmodule
