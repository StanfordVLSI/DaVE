/****************************************************************

Copyright (c) 2018- Stanford University. All rights reserved.

The information and source code contained herein is the 
property of Stanford University, and may not be disclosed or
reproduced in whole or in part without explicit written 
authorization from Stanford University. Contact bclim@stanford.edu for details.

* Filename   : pwl_feedthrough.v
* Author     : Byongchan Lim (bclim@stanford.edu)
* Description: A signal feedthrough module.

* Note       :

* Revision   :
  - 7/26/2016: First release

****************************************************************/

`timescale `DAVE_TIMEUNIT / `DAVE_TIMEUNIT

///////////
`ifndef AMS // NOT AMS
///////////


module pwl_feedthrough (
  `input_pwl in,
  `output_pwl out
);
 

`protect
//pragma protect 
//pragma protect begin
`get_timeunit
PWLMethod pm=new;

assign out = in;
//pragma protect end
`endprotect
endmodule


///////////
`else // AMS
///////////


`include "disciplines.vams"

module pwl_feedthrough (
  input in,
  output out
);

electrical in, out;

analog begin
  V(out) <+ V(in);
end

endmodule


///////////
`endif
///////////
