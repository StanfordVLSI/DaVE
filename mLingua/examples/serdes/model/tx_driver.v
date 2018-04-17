/****************************************************************

Copyright (c) 2018- Stanford University. All rights reserved.

The information and source code contained herein is the 
property of Stanford University, and may not be disclosed or
reproduced in whole or in part without explicit written 
authorization from Stanford University. Contact bclim@stanford.edu for details.

* Filename   : tx_driver.v
* Author     : Byongchan Lim (bclim@stanford.edu)
* Description: Tx driver 

* Note       :

* Revision   :
  - 7/26/2016: First release

****************************************************************/


module tx_driver #(
  parameter real tr=0, // transition time
  parameter real dc=0,  // output dc value
  parameter real amp=1.0,   // amplitude
  parameter real wtap0 = 1.0,
  parameter real wtap1 = 1.0
) (
  input in,       // TX data
  input clk,      // TX clock
  `output_pwl out  // TX output
);

`get_timeunit
PWLMethod pm=new;

pwl eq_out;
pwl dc_val;
initial dc_val = pm.write(dc, 0, 0);

fir_2tapfilter #(.tr(tr), .wtap0(wtap0), .wtap1(wtap1), .amp(amp), .dc(0.0)) xpre_emphasis
           (.in(in), .clk(clk), .out(eq_out));
pwl_add2 xadd (.in1(eq_out), .in2(dc_val), .scale1(1.0), .scale2(1.0), .out(out));

endmodule
