/****************************************************************

Copyright (c) 2018- Stanford University. All rights reserved.

The information and source code contained herein is the 
property of Stanford University, and may not be disclosed or
reproduced in whole or in part without explicit written 
authorization from Stanford University. Contact bclim@stanford.edu for details.

* Filename   : pfet.v
* Author     : Byongchan Lim (bclim@stanford.edu)
* Description:
  - PMOSFET DC I-V model similar to EKV model. This is developed 
    to describe DC behavior (saturation, linear, cut-off) of 
    PMOSFET.
  - I-V equation:
    I_f = gm*(V(s)-V(g)) when V(s)-V(g) >= |VTH|
          0.0 when V(s)-V(g) < |VTH|
    I_r = gm*(V(d)-V(g)) when V(g)-V(d) >= |VTH|
          0.0 when V(d)-V(g) < |VTH|
    id = I_f - I_r

* Note       :

* Revision   :
  - 7/26/2016: First release
  
****************************************************************/

module pfet #(
  parameter real VTH = 0.4   // threshold voltage (positive number)
) (
// I/Os here
  `input_real gm,     // transconductance when vsg (or vdg) > |VTH|
  `input_pwl d, g, s, // drain, gate, source terminals, respectively
  `output_pwl id      // source-to-drain current
);

timeunit `DAVE_TIMEUNIT ;
timeprecision `DAVE_TIMEUNIT ;

`protect
//pragma protect 
//pragma protect begin

`get_timeunit
PWLMethod pm=new;

// write your code
parameter pwl vth = '{abs(VTH),0,0};
localparam pwl one = '{1.0,0,0};
localparam pwl zero = '{0,0,0};

pwl i_f; // forward current
pwl i_r; // reverse current
pwl vsg, vdg, vsg0, vdg0;

pwl_add3 uadd1 (.in1(s), .in2(g), .in3(vth), .scale1(1.0), .scale2(-1.0), .scale3(-1.0), .out(vsg));
pwl_add3 uadd2 (.in1(d), .in2(g), .in3(vth), .scale1(1.0), .scale2(-1.0), .scale3(-1.0), .out(vdg));
pwl_limiter #(.NO_MAX(1'b1)) ulim1 (.scale(one), .minout(zero), .in(vsg), .out(vsg0));
pwl_limiter #(.NO_MAX(1'b1)) ulim2 (.scale(one), .minout(zero), .in(vdg), .out(vdg0));

pwl_vga uvga1 (.in(vsg0), .out(i_r), .scale(gm));
pwl_vga uvga2 (.in(vdg0), .out(i_f), .scale(gm));
pwl_add2 uadd3 (.in1(i_r), .in2(i_f), .scale1(1.0), .scale2(-1.0), .out(id));

//pragma protect end
`endprotect

endmodule
