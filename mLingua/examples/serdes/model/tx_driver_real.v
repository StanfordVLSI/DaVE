/****************************************************************

Copyright (c) 2018- Stanford University. All rights reserved.

The information and source code contained herein is the 
property of Stanford University, and may not be disclosed or
reproduced in whole or in part without explicit written 
authorization from Stanford University. Contact bclim@stanford.edu for details.

* Filename   : tx_driver_real.v
* Author     : Byongchan Lim (bclim@stanford.edu)
* Description: Tx driver 

* Note       :

* Revision   :
  - 7/26/2016: First release

****************************************************************/

module tx_driver_real #(
  parameter real dc=0,  // output dc value
  parameter real amp=1.0,   // amplitude
  parameter real wtap0 = 1.0,
  parameter real wtap1 = 1.0
) (
  input in,       // TX data
  input clk,      // TX clock
  `output_real out  // TX output
);

`get_timeunit
PWLMethod pm=new;

real eq_out;
real dc_val;
initial dc_val = dc;

fir_2tapfilter_real #(.wtap0(wtap0), .wtap1(wtap1), .amp(amp), .dc(0.0)) xpre_emphasis (.in(in), .clk(clk), .out(eq_out));
real_add2 xadd (.in1(eq_out), .in2(dc_val), .scale1(1.0), .scale2(1.0), .out(out));

endmodule
