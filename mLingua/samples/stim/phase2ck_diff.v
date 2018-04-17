/****************************************************************

Copyright (c) 2018- Stanford University. All rights reserved.

The information and source code contained herein is the 
property of Stanford University, and may not be disclosed or
reproduced in whole or in part without explicit written 
authorization from Stanford University. Contact bclim@stanford.edu for details.

* Filename   : phase2ck_diff.v
* Author     : Byongchan Lim (bclim@stanford.edu)
* Description: It outputs two digital clocks with different phases.

* Note       :

* Revision   :
  - 7/26/2016: First release

****************************************************************/

`timescale `DAVE_TIMEUNIT / `DAVE_TIMEUNIT

module phase2ck_diff #(
  parameter real ph_diff = 0.0, // diff-mode phase in rad/s
  parameter real ph_cm   = 0.0, // common-mode phase in rad/s
  parameter real freq    = 1.0, // frequency
  parameter real duty    = 0.5  // duty cycle
) (
  output cko_lead, ckob_lead, // lead clock output
  output cko_lag , ckob_lag   // lag clock output
);

assign ckob_lead = ~cko_lead;
assign ckob_lag = ~cko_lag;

clock #(.b0(1'b0), .freq(freq), .duty(duty), .td(1.0/freq+(ph_cm-ph_diff/2.0)*0.5/freq/`M_PI)) xlead (.ckout(cko_lead));
clock #(.b0(1'b0), .freq(freq), .duty(duty), .td(1.0/freq+(ph_cm+ph_diff/2.0)*0.5/freq/`M_PI)) xlag (.ckout(cko_lag));

endmodule
