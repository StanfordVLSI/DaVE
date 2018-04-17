/****************************************************************

Copyright (c) 2018- Stanford University. All rights reserved.

The information and source code contained herein is the 
property of Stanford University, and may not be disclosed or
reproduced in whole or in part without explicit written 
authorization from Stanford University. Contact bclim@stanford.edu for details.

* Filename   : i_term.v
* Author     : Byongchan Lim (bclim@stanford.edu)
* Description: It terminates a current input to a reference voltage node
               with a resistor and outputs the corresponding voltage output.
  - This is a I-V converter which is useful for measuring  a current value.

* Note       :

* Revision   :
  - 12/18/2016: First release

****************************************************************/

`timescale `DAVE_TIMEUNIT / `DAVE_TIMEUNIT

///////////
`ifndef AMS // NOT AMS
///////////


module i_term #(
  parameter real res = 1.0  // termination resistance 
) (
  `input_pwl i_in,
  `input_pwl refnode,
  `output_pwl vout
);

`get_timeunit
PWLMethod pm=new;

pwl_add2 uvout (.in1(i_in), .in2(refnode), .scale1(1.0*res), .scale2(1.0), .out(vout));

endmodule


///////////
`else // AMS
///////////


`include "disciplines.vams"

module i_term #(
  parameter real res = 1.0  // termination resistance 

) ( input i_in, refnode,
  output vout
);

electrical i_in, refnode, vout;

`get_timeunit

analog begin
  V(i_in,refnode) <+ I(i_in,refnode)*res;
  V(vout) <+ V(i_in);
end

endmodule


///////////
`endif
///////////
