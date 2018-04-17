/****************************************************************

Copyright (c) 2018- Stanford University. All rights reserved.

The information and source code contained herein is the 
property of Stanford University, and may not be disclosed or
reproduced in whole or in part without explicit written 
authorization from Stanford University. Contact bclim@stanford.edu for details.

* Filename   : ringosc.v
* Author     : Byongchan Lim (bclim@stanford.edu)
* Description: Simple phase domain model of a ring oscillator

* Note       :

* Revision   :
  - 7/26/2016: First release

****************************************************************/

module ringosc (
  `input_pwl vreg, // PWL sig
  output ck,
  output ckb
);


`get_timeunit

parameter vh = 1.0;  // upper bound of vreg [V]
parameter vl = 0.0;  // lower bound of vreg [V]
parameter vco0 = 1.5e9; // freq offset [Hz]
parameter vco1 = 1e9;   // freq gain [Hz/V]
//parameter jitter = 0.005; // rms jitter in (jitter/period)
parameter jitter = 0.0; // rms jitter in (jitter/period)

pwl freq, phase;

assign ckb = ~ck;

txf_vco #(.vh(vh), .vl(vl), .vco0(vco0), .vco1(vco1)) xdc (.in(vreg), .out(freq));
pwl_integrator #(.etol(0.01), .modulo(0.5), .noise(jitter)) xph2clk(.gain(1.0), .si(freq), .so(phase), .trigger(ck));

endmodule
