/****************************************************************

Copyright (c) 2018- Stanford University. All rights reserved.

The information and source code contained herein is the 
property of Stanford University, and may not be disclosed or
reproduced in whole or in part without explicit written 
authorization from Stanford University. Contact bclim@stanford.edu for details.

* Filename   : sensor.v
* Author     : Byongchan Lim (bclim@stanford.edu)
* Description: Feedback network (analog PWM) of a buck converter.

* Note       :

* Revision   :
  - 7/26/2016: First release

****************************************************************/

module sensor #(
parameter real etol = 0.001,          // error tolerance
parameter real rdivider_gain = 3/4.01, // resistive divider gain
parameter real gmota = 10e-3,         // OTA gm
parameter real Rota = 40e3,           // OTA Rout
parameter real Gota = gmota*Rota,     // OTA gain
parameter real Rc = 7.15e3,           // Compensator R
parameter real Cc = 4.7e-9            // Compensator C
) (
  `input_pwl vin,    // output of a buck converter
  `input_pwl vref,   // voltage reference to error amplifier
  `input_pwl saw_in, // saw-tooth wave input
  output dout       // driving signal 
);

`get_timeunit

PWLMethod pm=new;

parameter real wzc = 1/Rc/Cc;
parameter real wpc = 1/Cc/Rota;

pwl vf; // after R divider
pwl vd; // error amplifier input
pwl ve; // error amplifier output
pwl vc; // slicer input

// resistive divider
pwl_vga xrdivider (.in(vin), .scale(rdivider_gain), .out(vf));

// error amplifier & compensation network 
pwl_add2 xvd (.in1(vf), .in2(vref), .scale1(Gota), .scale2(-1.0*Gota), .out(vd));
pwl_filter_real_prime #(.etol(etol)) xcompensator (.filter_type(3), .wz1(wzc), .wp1(wpc), .in(vd), .out(ve)); // 1-pole, 1-zero

// slicer
pwl_add2 xvc (.in1(ve), .in2(saw_in), .scale1(1.0), .scale2(-1.0), .out(vc));
pwl_slicer #(.offset(0.0)) xcomparator (.vin(vc), .out(dout));

endmodule
