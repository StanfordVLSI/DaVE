/****************************************************************

Copyright (c) 2018- Stanford University. All rights reserved.

The information and source code contained herein is the 
property of Stanford University, and may not be disclosed or
reproduced in whole or in part without explicit written 
authorization from Stanford University. Contact bclim@stanford.edu for details.

* Filename   : bb_cdr.v
* Author     : Byongchan Lim (bclim@stanford.edu)
* Description: Top module of a band-band CDR

* Note       :

* Revision   :
  - 7/26/2016: First release

****************************************************************/


module bb_cdr #(
  parameter real vth=0.0,
  parameter dco_Nbit = 20,
  parameter [dco_Nbit-1:0] init_dctrl = {1'b1,{(dco_Nbit-1){1'b0}}},
  parameter real Kp = 256,
  parameter real Ki = 1,
  parameter real freq_min = 1.5e9,
  parameter real freq_max = 2.5e9
)(
  `input_pwl in,
  output data, clk
);

`get_timeunit

wire up, dn;
wire [dco_Nbit-1:0] dctrl;

alexander_pd #(.vth(vth)) xpd (.in(in), .clk(clk), .data(data), .up(up), .dn(dn));
digital_lf #(.Nbit(dco_Nbit),.offset(init_dctrl),.Kp(Kp),.Ki(Ki)) dlf
           (.clk(clk), .up(up), .dn(dn), .out(dctrl));
dco #(.Nbit(dco_Nbit), .freq_min(freq_min), .freq_max(freq_max)) xdco(.in(dctrl), .clk(clk));

endmodule
