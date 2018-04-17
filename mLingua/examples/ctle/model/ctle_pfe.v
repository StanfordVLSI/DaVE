/****************************************************************

Copyright (c) 2018- Stanford University. All rights reserved.

The information and source code contained herein is the 
property of Stanford University, and may not be disclosed or
reproduced in whole or in part without explicit written 
authorization from Stanford University. Contact bclim@stanford.edu for details.

* Filename   : ctle.v
* Author     : Byongchan Lim (bclim@stanford.edu)
* Description: Linear model for continuous-time linear equalizer.
  It comprises two filter models having a zero, two poles.

* Note       :
  - This expresses the output as a sum of two pwl_filter_pfe outputs.
  - This gives convervative residual errors than another example.

* Revision   :
  - 0/00/2017: First release

****************************************************************/


module ctle_pfe #(
  parameter real etol=0.001, // error tolerance of PWL approximation
  parameter real gdc=0.66,   // dc gain
  parameter real fz1=150e6,  // zero in Hz
  parameter real fp1=500e6,  // 1st pole in Hz
  parameter real fp2=1e9     // 2nd pole in Hz
) ( 
  `input_pwl in,
  `output_pwl out
);

`get_timeunit

localparam real wz1 = `M_TWO_PI*fz1;
localparam real wp1 = `M_TWO_PI*fp1;
localparam real wp2 = `M_TWO_PI*fp2;

localparam real K = wp1*wp2/wz1;
complex A1 = '{K*(fz1-fp1)/(fp2-fp1),0};
complex A2 = '{-K*(fz1-fp2)/(fp2-fp1),0};
complex B1 = '{wp1,0};
complex B2 = '{wp2,0};

pwl in_1;
pwl out_1, out_2;

real scale[2];
pwl in_add[2];
assign scale = '{1.0,1.0};
assign in_add = '{out_1, out_2};

pwl_vga xscale (.scale(gdc), .in(in), .out(in_1));
pwl_filter_pfe ipfe1 ( .A(A1), .B(B1), .in(in_1), .out(out_1) );
pwl_filter_pfe ipfe2 ( .A(A2), .B(B2), .in(in_1), .out(out_2) );
pwl_add #(.no_sig(2)) iadd ( .scale(scale), .in(in_add), .out(out) );
//pwl_add2 iadd ( .scale1(1.0), .scale2(1.0), .in1(out_1), .in2(out_2), .out(out) );

endmodule
