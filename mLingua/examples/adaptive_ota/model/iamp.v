/****************************************************************

Copyright (c) 2018- Stanford University. All rights reserved.

The information and source code contained herein is the 
property of Stanford University, and may not be disclosed or
reproduced in whole or in part without explicit written 
authorization from Stanford University. Contact bclim@stanford.edu for details.

* Filename   : iamp.v
* Author     : Byongchan Lim (bclim@stanford.edu)
* Description: Top module of an adaptive OTA

* Note       :

* Revision   :
  - 7/26/2016: First release

****************************************************************/



module iamp (
  `input_pwl inp,
  `input_pwl inm,
  `input_pwl ib,
  `input_pwl vdda,
  `output_pwl out
);

parameter real etol=0.001;

`protect
//pragma protect 
//pragma protect begin


`get_timeunit
PWLMethod pm=new;
real t;
pwl vc;
real p1;
real gain;
real islew;

pwl vd, vd1;
pwl vd_tmp;
pwl id;
pwl ibias, ibias_fb, ibias_in;
pwl vdd = '{3,0,0};
pwl vss = '{0,0,0};

ota #(.etol(etol), .gain_error(1-50/51), .lambda(0.4), .beta(0.005), .Rout(5e6), .Cout(1.2e-12)) ota (.vdd(vdd), .vss(vss), .ibias(ibias_in), .inp(inp), .inn(inm), .out(out));

// get common-mode and differential input voltages
pwl_add2 xpvcm (.in1(inp), .in2(inm), .scale1(0.5), .scale2(0.5), .out(vc));
pwl_add2 xpvdf (.in1(inp), .in2(inm), .scale1(1.0), .scale2(-1.0), .out(vd));

pwl_add2 xiadd (.in1(ib), .in2(ibias_fb), .scale1(1.0), .scale2(1.0), .out(ibias_in));
dynamic_bias dbias (.iin(ibias_in), .vd(vd), .vc(vc), .iout(ibias));
//pwl_gatekeeper #(.etol(2e-6), .en_lcc(1'b1), .gain_error(0.001)) xibgp (.inp(inp), .in(ibias), .out(ibias_fb));
pwl_gatekeeper_simple #(.etol(2e-6)) xibgp (.in(ibias), .out(ibias_fb));
//assign ibias_fb = ibias;

//pragma protect end
`endprotect

endmodule

