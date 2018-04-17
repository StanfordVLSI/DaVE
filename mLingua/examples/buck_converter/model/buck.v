/****************************************************************

Copyright (c) 2018- Stanford University. All rights reserved.

The information and source code contained herein is the 
property of Stanford University, and may not be disclosed or
reproduced in whole or in part without explicit written 
authorization from Stanford University. Contact bclim@stanford.edu for details.

* Filename   : buck.v
* Author     : Byongchan Lim (bclim@stanford.edu)
* Description: Top module of a buck converter

* Note       :
  - References from microsemi.com :
    a. AN-9: Modulated Constant Off-Time Control Mechanism
    b. AN-10: Design Procedure for Microprocessor Buck Regulators

* Revision   :
  - 7/26/2016: First release

****************************************************************/


module buck (
  `input_pwl vref,
  `input_pwl saw_in,
  `input_pwl vddh, vgnd,
  `output_pwl vout
);

`get_timeunit
PWLMethod pm=new;

parameter real etol = 0.001;
parameter real rp = 0.2;
parameter real L = 18e-9;
parameter real RL = 100;
parameter real CL = 150e-9;

wire pulse;

// Analog PWM controller
sensor #(.etol(etol)) xsensor (.vin(vout), .vref(vref), .saw_in(saw_in), .dout(pulse));

// driving circuit of a buck converter
buck_core #(.etol(etol), .rp(rp), .L(L), .RL(RL), .CL(CL)) xbuck(.din(pulse), .vddh(vddh), .vgnd(vgnd), .so(vout));

endmodule
