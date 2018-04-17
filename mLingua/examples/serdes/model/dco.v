/****************************************************************

Copyright (c) 2018- Stanford University. All rights reserved.

The information and source code contained herein is the 
property of Stanford University, and may not be disclosed or
reproduced in whole or in part without explicit written 
authorization from Stanford University. Contact bclim@stanford.edu for details.

* Filename   : dco.v
* Author     : Byongchan Lim (bclim@stanford.edu)
* Description: Digitally controlled oscillator in Rx

* Note       :

* Revision   :
  - 7/26/2016: First release

****************************************************************/

module dco #(
  parameter Nbit= 14,
  parameter real freq_min = 1.5e9,
  parameter real freq_max = 2.5e9
)(
  input [Nbit-1:0] in,
  output clk
);

`get_timeunit
PWLMethod pm=new;

pwl freq, phase;
real Kdco;

initial Kdco = (freq_max-freq_min)/2**Nbit;
always @(in) freq = pm.write(Kdco*in + freq_min, 0, `get_time);

pwl_integrator #(.etol(0.001), .modulo(0.5)) xph2clk(.gain(1.0), .si(freq), .so(phase), .trigger(clk));

endmodule
