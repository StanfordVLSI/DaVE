/****************************************************************

Copyright (c) 2018- Stanford University. All rights reserved.

The information and source code contained herein is the 
property of Stanford University, and may not be disclosed or
reproduced in whole or in part without explicit written 
authorization from Stanford University. Contact bclim@stanford.edu for details.

* Filename   : fir_2tapfilter_real.v
* Author     : Byongchan Lim (bclim@stanford.edu)
* Description: two-tap FIR filter in TX driver

* Note       :

* Revision   :
  - 7/26/2016: First release

****************************************************************/


module fir_2tapfilter_real #(
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

reg [1:0] d = '0;
real fir_bit1, fir_bit0;
real fir_out;
real dc_val;

initial dc_val = dc;

// FIR filter

// shift register
always @(posedge clk) begin
  d[0] <= in;
  d[1] <= d[0];
end

bit2real #(.vh(0.5*amp*wtap0), .vl(-0.5*amp*wtap0)) bit2real0(.in(d[0]), .out(fir_bit0));
bit2real #(.vh(0.5*amp*wtap1), .vl(-0.5*amp*wtap1)) bit2real1(.in(d[1]), .out(fir_bit1));

// add weighted sum
real_add2 xaddwgt (.in1(fir_bit0), .in2(fir_bit1), .scale1(1.0), .scale2(1.0), .out(fir_out));
// add dc level
real_add2 xadd (.in1(fir_out), .in2(dc_val), .scale1(1.0), .scale2(1.0), .out(out));

endmodule
