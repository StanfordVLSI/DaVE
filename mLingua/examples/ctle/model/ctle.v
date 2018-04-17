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

* Revision   :
  - 7/26/2016: First release

****************************************************************/


module ctle #(
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

pwl in_1;

pwl_vga xscale (.scale(gdc), .in(in), .out(in_1));
pwl_filter_real_w_reset #(.etol(etol), .filter(2), .en_filter(1'b1)) xinst (.in(in_1), .out(out), .fp1(fp1), .fp2(fp2), .fz1(fz1));

endmodule
