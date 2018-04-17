/****************************************************************

Copyright (c) 2018- Stanford University. All rights reserved.

The information and source code contained herein is the 
property of Stanford University, and may not be disclosed or
reproduced in whole or in part without explicit written 
authorization from Stanford University. Contact bclim@stanford.edu for details.

* Filename   : alexander_pd.v
* Author     : Byongchan Lim (bclim@stanford.edu)
* Description: Bang-band phase detector

* Note       :

* Revision   :
  - 7/26/2016: First release

****************************************************************/

`protect
//pragma protect 
//pragma protect begin
module alexander_pd #(
  parameter real vth = 0.0
) (
  `input_pwl in,
  input clk,
  output reg data,
  output up,
  output dn
);

`get_timeunit
PWLMethod pm=new;

reg a, b;
reg t;
wire clkb = ~clk;
initial begin
  data = 1'b0;
  a = 1'b0;
  b = 1'b0;
end

assign up = a ^ b;
assign dn = data ^ b;

always @(posedge clk) 
  if (pm.eval(in,`get_time)>=vth) data <= 1'b1;
  else data <= 1'b0;

always @(posedge clkb) 
  if (pm.eval(in,`get_time)>=vth) t <= 1'b1;
  else t <= 1'b0;

always @(posedge clk) begin
  a <= data;
  b <= t;
end
  
endmodule
//pragma protect end
`endprotect
