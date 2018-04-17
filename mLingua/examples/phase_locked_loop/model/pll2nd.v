/****************************************************************

Copyright (c) 2018- Stanford University. All rights reserved.

The information and source code contained herein is the 
property of Stanford University, and may not be disclosed or
reproduced in whole or in part without explicit written 
authorization from Stanford University. Contact bclim@stanford.edu for details.

* Filename   : pll2nd.v
* Author     : Byongchan Lim (bclim@stanford.edu)
* Description: Top module of a second-order PLL

* Note       :

* Revision   :
  - 7/26/2016: First release

****************************************************************/

module pll2nd (
  `input_real vdd_in,
  input refclk,
  input rstb,
  output outclk,
  `output_pwl vctrl);

parameter tos = 0.0;
parameter iup = 0.0;
parameter idn = 0.0;
parameter C1 = 0.0;
parameter C2 = 0.0;
parameter R = 0.0;
parameter vh = 1.0;  // upper bound of vreg [V]
parameter vl = 0.0;  // lower bound of vreg [V]
parameter vco0 = 1.5e9; // freq offset [Hz]
parameter vco1 = 1e9;   // freq gain [Hz/V]
parameter vinit = 0;    // initial value of vctrl
parameter jitter = 0.0; // rms jitter in (jitter/period)


real iin_lpf;
pwl vreg;
real iin; 
real t, t0;

wire divclk;


// instantiation of components

// smear out 0 sec pulse to ensure that the lpf block really works. 
// Otherwise, it's not clear whether the lpf works because of repeated input events or something else.
//always @(iin)
//   #2 iin_lpf = iin;
assign iin_lpf = iin;

pfd #(.tos(tos)) pfd (.vdd_in(vdd_in), .ckref(refclk), .fdbk(divclk), .ext_rstb(rstb), .up(up), .dn(dn));
chgpmp #(.iup0(iup), .idn0(idn)) cp ( .avdd(vdd_in), .up(up), .dn(dn), .vctrl(iin));
lpf #(.R(R), .C1(C1), .C2(C2), .vinit(vinit)) lpf (.si(iin_lpf), .vc(vctrl));
regulator regulator(.vdd_in(vdd_in), .vctrl(vctrl), .vreg(vreg));
vco #(.vh(vh), .vl(vl), .vco0(vco0), .vco1(vco1), .jitter(jitter)) vco(.vreg(vreg), .vdd_in(vdd_in), .hck(outclk));

`ifdef CKTCOMP  // if for circuit comparison
  div2 div2 (.vdd(vdd_in), .cki(outclk), .ckib(~outclk), .cko(divclk));  
`else
  assign divclk = outclk;

`endif

    
endmodule
