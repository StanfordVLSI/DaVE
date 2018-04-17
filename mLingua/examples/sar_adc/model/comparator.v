/****************************************************************

Copyright (c) 2018- Stanford University. All rights reserved.

The information and source code contained herein is the 
property of Stanford University, and may not be disclosed or
reproduced in whole or in part without explicit written 
authorization from Stanford University. Contact bclim@stanford.edu for details.

* Filename   : comparator.v
* Author     : Byongchan Lim (bclim@stanford.edu)
* Description: Top module of a comparator

* Note       :

* Revision   :
  - 7/26/2016: First release

****************************************************************/

module comparator #(
) (
  `input_pwl vdd,   // power supply, does nothing here yet
  `input_pwl vss,   // ground, does nothing here yet
  `input_pwl vinp, vinn, // ground for pre-amp 1 & 2, does nothing
  `input_pwl ibias,     // bias current
  input pwdn,           // power down pre-amp
  input clk,
  output dout, doutb  // output of the latch
);

`get_timeunit

PWLMethod pm=new;
pwl voutp, voutn;

clk_preamp xpreamp (.vdd(vdd), .vss(vss), .vinp(vinp), .vinn(vinn), .ibias(ibias), .pwdn(pwdn), .eq(~clk), .voutp(voutp), .voutn(voutn));
senseamp xsenseamp (.vdd(vdd), .vss(vss), .vinp(voutp), .vinn(voutn), .clk(~clk), .dout(dout), .doutb(doutb));

endmodule
