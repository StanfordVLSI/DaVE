/****************************************************************

Copyright (c) 2018- Stanford University. All rights reserved.

The information and source code contained herein is the 
property of Stanford University, and may not be disclosed or
reproduced in whole or in part without explicit written 
authorization from Stanford University. Contact bclim@stanford.edu for details.

* Filename   : div2.v
* Author     : Byongchan Lim (bclim@stanford.edu)
* Description: Feedback divider (/2)

* Note       :

* Revision   :
  - 7/26/2016: First release

****************************************************************/


module div2(
  `input_real vdd, 
  input cki, ckib,
  output reg cko);

`get_timeunit

parameter div2_a0 = 1.531439e-10;
parameter div2_a1 = -7.148846e-11;

reg div_ff;
real propagation_delay;  // propagation delay of cki-to-clkout

initial div_ff = 1'b0;

// propagation delay calculation
always @(div_ff) begin
  cko = `delay(div2_a0+div2_a1*vdd) div_ff;
end
always @(posedge cki) div_ff <= ~div_ff;

endmodule
