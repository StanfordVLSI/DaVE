/****************************************************************

Copyright (c) 2018- Stanford University. All rights reserved.

The information and source code contained herein is the 
property of Stanford University, and may not be disclosed or
reproduced in whole or in part without explicit written 
authorization from Stanford University. Contact bclim@stanford.edu for details.

* Filename   : dynamic_bias.v
* Author     : Byongchan Lim (bclim@stanford.edu)
* Description: Dynamic bias of an OTA.

* Note       :

* Revision   :
  - 7/26/2016: First release

****************************************************************/


module dynamic_bias (
  `input_pwl iin, vd, vc,
  `output_pwl iout
);

`protect
//pragma protect 
//pragma protect begin

`get_timeunit
PWLMethod pm=new;

pwl  i_0, i_1, i_2;
pwl max_current = '{160e-6,0,0};
pwl min_current = '{0,0,0};
pwl unity_scale = '{1,0,0};
real scalef;
real igain;
real vd_r;

pwl2real #(.dv(0.01)) p2r (.in(vd), .out(vd_r));
always @(vd_r) igain = vd_r*1.8;
pwl_vga igainx (.in(iin), .scale(igain), .out(i_0));
pwl_limiter ilim (.maxout(max_current), .minout(min_current), .scale(unity_scale), .in(i_0), .out(i_1));
pwl_delay #(.delay(3e-9)) xdly (.in(i_1), .out(i_2));
pwl_spf #(.etol(2e-6), .w1(`M_TWO_PI*10e6), .en_filter(1'b1)) xi1 (.in(i_2), .out(iout));

//pragma protect end
`endprotect

endmodule
