/****************************************************************

Copyright (c) 2018- Stanford University. All rights reserved.

The information and source code contained herein is the 
property of Stanford University, and may not be disclosed or
reproduced in whole or in part without explicit written 
authorization from Stanford University. Contact bclim@stanford.edu for details.

* Filename   : vco.v
* Author     : Byongchan Lim (bclim@stanford.edu)
* Description: ringosc + vcobuf module

* Note       :

* Revision   :
  - 7/26/2016: First release

****************************************************************/

module vco(
  `input_pwl vreg,
  `input_real vdd_in,
  output hck);

wire lclk, lclkb;

parameter vh = 1.0;  // upper bound of vreg [V]
parameter vl = 0.0;  // lower bound of vreg [V]
parameter vco0 = 1.5e9; // freq offset [Hz]
parameter vco1 = 1e9;   // freq gain [Hz/V]
parameter jitter = 0.0; // rms jitter in (jitter/period)

ringosc #(.vh(vh), .vl(vl), .vco0(vco0), .vco1(vco1), .jitter(jitter)) ringosc(.vreg(vreg), .ck(lclk), .ckb(lclkb));
vcobuf vcobuf(.avdd(vdd_in), .hck(hck), .hckb(hckb), .lck(lclk), .lckb(lclkb));

endmodule
