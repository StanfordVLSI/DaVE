/****************************************************************

Copyright (c) 2018- Stanford University. All rights reserved.

The information and source code contained herein is the 
property of Stanford University, and may not be disclosed or
reproduced in whole or in part without explicit written 
authorization from Stanford University. Contact bclim@stanford.edu for details.

* Filename   : dfe.v
* Author     : Byongchan Lim (bclim@stanford.edu)
* Description: Two tap decision feedback equalizer

* Note       :

* Revision   :
  - 7/26/2016: First release

****************************************************************/


`protect
//pragma protect 
//pragma protect begin
module dfe #(
  parameter real tr=10e-12, // transition time
  parameter real dc=0,  // output dc value
  parameter real amp=1.0,   // amplitude
  parameter real wtap0 = 1.0,
  parameter real wtap1 = 1.0

) (
  `input_pwl in,       // TX data
  input data,     // feedback data
  input clk,      // TX clock
  `output_pwl out  // TX output
);

`get_timeunit

pwl fback;

fir_2tapfilter #(.tr(tr), .wtap0(wtap0), .wtap1(wtap1), .amp(1.0), .dc(0.0)) xfir
           (.in(data), .clk(clk), .out(fback));
pwl_add2 xadd (.in1(in), .in2(fback), .scale1(1.0), .scale2(1.0), .out(out));

endmodule
//pragma protect end
`endprotect
