/****************************************************************

Copyright (c) 2018- Stanford University. All rights reserved.

The information and source code contained herein is the 
property of Stanford University, and may not be disclosed or
reproduced in whole or in part without explicit written 
authorization from Stanford University. Contact bclim@stanford.edu for details.

* Filename   : gated_osc.v
* Author     : Byongchan Lim (bclim@stanford.edu)
* Description:
  - An oscillator with a gated input

* Note       :

* Revision   :
  - 7/26/2016: First release

****************************************************************/


module gated_osc #(
  parameter real period = 2.1e-9, // period
  parameter logic init = 0        // cko value when enb = 'H'
) (
  input enb,  // enable clock output (active low)
  output cko  // clock output 
);

timeunit `DAVE_TIMEUNIT ;
timeprecision `DAVE_TIMEUNIT ;

`protect
//pragma protect 
//pragma protect begin

`get_timeunit

reg cko;
event wakeup;  // dummy for initial startup

initial begin
  cko = '0;
  -> wakeup;
end
  
always @(enb or cko or wakeup)
  if (!enb) cko <= `delay(period/2) ~cko;
  else cko <= init;

//pragma protect end
`endprotect

endmodule
