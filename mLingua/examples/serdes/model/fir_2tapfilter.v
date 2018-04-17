/****************************************************************

Copyright (c) 2018- Stanford University. All rights reserved.

The information and source code contained herein is the 
property of Stanford University, and may not be disclosed or
reproduced in whole or in part without explicit written 
authorization from Stanford University. Contact bclim@stanford.edu for details.

* Filename   : fir_2tapfilter.v
* Author     : Byongchan Lim (bclim@stanford.edu)
* Description: two-tap FIR filter in TX driver

* Note       :

* Revision   :
  - 7/26/2016: First release

****************************************************************/


module fir_2tapfilter #(
  parameter real tr=10e-12, // transition time
  parameter real dc=0,  // output dc value
  parameter real amp=1.0,   // amplitude
  parameter real wtap0 = 1.0, // first tap coef
  parameter real wtap1 = 1.0
) (
  input in,       // TX data
  input clk,      // TX clock
  `output_pwl out  // TX output
);

`get_timeunit
PWLMethod pm=new;

reg [1:0] d = '0;
pwl fir_bit1, fir_bit0;
pwl fir_out;
pwl dc_val;

initial dc_val = pm.write(dc, 0, 0);

// FIR filter

always @(posedge clk) begin
  d[0] <= in;
  d[1] <= d[0];
end

// bit to pwl conversion 
bit2pwl #(.vh(0.5*amp*wtap0), .vl(-0.5*amp*wtap0), .tr(tr)) bit2pwl0(.in(d[0]), .out(fir_bit0));
bit2pwl #(.vh(0.5*amp*wtap1), .vl(-0.5*amp*wtap1), .tr(tr)) bit2pwl1(.in(d[1]), .out(fir_bit1));

// add weighted sum
pwl_add2 xaddwgt (.in1(fir_bit0), .in2(fir_bit1), .scale1(1.0), .scale2(1.0), .out(fir_out));
// add dc level
pwl_add2 xadd (.in1(fir_out), .in2(dc_val), .scale1(1.0), .scale2(1.0), .out(out));

endmodule
