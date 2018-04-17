/****************************************************************

Copyright (c) 2018- Stanford University. All rights reserved.

The information and source code contained herein is the 
property of Stanford University, and may not be disclosed or
reproduced in whole or in part without explicit written 
authorization from Stanford University. Contact bclim@stanford.edu for details.

* Filename   : nfet.v
* Author     : Byongchan Lim (bclim@stanford.edu)
* Description:
  - NMOSFET DC I-V model similar to EKV model. This is developed 
    to describe DC behavior (saturation, linear, cut-off) of 
    NMOSFET.
  - I-V equation:
    I_f = gm*(V(g)-V(s)) when V(g)-V(s) >= VTH
          0.0 when V(g)-V(s) < VTH
    I_r = gm*(V(g)-V(d)) when V(g)-V(d) >= VTH
          0.0 when V(g)-V(d) < VTH
    id = I_f - I_r

* Note       :

* Revision   :
  - 7/26/2016: First release
  
****************************************************************/




module nfet #(
  parameter real VTH = 0.4   // threshold voltage
) (
// I/Os here
  `input_real gm,     // transconductance when vgs(or vgd) > VTH
  `input_pwl d, g, s, // drain, gate, source terminals, respectively
  `output_pwl id      // drain-to-source current 
);

timeunit `DAVE_TIMEUNIT ;
timeprecision `DAVE_TIMEUNIT ;

`protect
//pragma protect 
//pragma protect begin

`get_timeunit
PWLMethod pm=new;

// write your code
parameter pwl vth = '{VTH,0,0};
localparam pwl one = '{1.0,0,0};
localparam pwl zero = '{0,0,0};

pwl i_f; // forward current
pwl i_r; // reverse current
pwl vgs, vgd, vgs0, vgd0; // terminal voltages


pwl_add3 uadd1 (.in1(g), .in2(s), .in3(vth), .scale1(1.0), .scale2(-1.0), .scale3(-1.0), .out(vgs));
pwl_add3 uadd2 (.in1(g), .in2(d), .in3(vth), .scale1(1.0), .scale2(-1.0), .scale3(-1.0), .out(vgd));
pwl_limiter #(.NO_MAX(1'b1)) ulim1 (.scale(one), .minout(zero), .in(vgs), .out(vgs0));
pwl_limiter #(.NO_MAX(1'b1)) ulim2 (.scale(one), .minout(zero), .in(vgd), .out(vgd0));

pwl_vga uvga1 (.in(vgs0), .out(i_r), .scale(gm));
pwl_vga uvga2 (.in(vgd0), .out(i_f), .scale(gm));
pwl_add2 uadd3 (.in1(i_r), .in2(i_f), .scale1(1.0), .scale2(-1.0), .out(id));

//pragma protect end
`endprotect

endmodule
