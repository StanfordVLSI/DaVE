/****************************************************************

Copyright (c) 2018 Stanford University. All rights reserved.

The information and source code contained herein is the 
property of Stanford University, and may not be disclosed or
reproduced in whole or in part without explicit written 
authorization from Stanford University.

* Filename   : pwl_filter_real_prime_w_gain.v
* Author     : Byongchan Lim (bclim@stanford.edu)
* Description: add 'gain' to "pwl_filter_real_prime" cell
  - For detail information on parameters and ports, refer to
    "pwl_filter_real_prime" cell

* Note       :

* Revision   :

****************************************************************/


module pwl_filter_real_prime_w_gain #(
// parameters here
  parameter etol = 0.005,     // error tolerance of PWL approximation
  parameter en_filter = 1'b1  // enable output event filtering
) (
// I/Os here
  `input_real gain,     // dc gain
  `input_real wz1,      // zero location in radian
  `input_real wp1,      // 1st pole location in radian
  `input_real wp2,      // 2nd pole location in radian
  `input_pwl in,        // filter signal input 
  `input_pwl reset_sig, // input when reset is asserted
  input reset,          // '1': out = reset_sig instantaneouly, '0': out = in with filtering op.
  input hold,           // '1': hold the output, '0': normal op (pull-down when unconnected)
  input integer filter_type,  // select filter type. see the note above
  input en_complex,     // two poles are conjugate if True, then wp1 is real part, wp2 is imaginary part, this port is pulled-down when floating

  `output_pwl out       // filter output
);

timeunit `DAVE_TIMEUNIT ;
timeprecision `DAVE_TIMEUNIT ;

pwl in_scaled;

pwl_vga uGAINSTG (.scale(gain), .in(in), .out(in_scaled));
pwl_filter_real_prime #(
  .etol(etol),
  .en_filter(en_filter)
) uFILTER (
  .wz1(wz1),
  .wp1(wp1),
  .wp2(wp2),
  .in(in_scaled),
  .reset_sig(reset_sig),
  .reset(reset),
  .hold(hold),
  .filter_type(filter_type),
  .en_complex(en_complex),
  .out(out)
);

endmodule

