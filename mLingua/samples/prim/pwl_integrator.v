/****************************************************************

Copyright (c) 2018- Stanford University. All rights reserved.

The information and source code contained herein is the 
property of Stanford University, and may not be disclosed or
reproduced in whole or in part without explicit written 
authorization from Stanford University. Contact bclim@stanford.edu for details.

* Filename   : pwl_integrator.v
* Author     : Byongchan Lim (bclim@stanford.edu)
* Description: 
  - integrates a pwl signal. It doesn't have a reset input unlike
    "pwl_integrator_w_reset" cell
  - If 'modulo' > 0, a modulo operation is performed on the output, 
    which is a useful feature to realize an oscillator model in phase
    domain.

* Note       :

* Revision   :
  - 7/26/2016: First release

****************************************************************/

module pwl_integrator #(
  parameter real etol = 0.001, // error tolerance of PWL approximation
  parameter real vinit = 0,    // initial state value of the output
  parameter real modulo = 0,   // output % modulo for phase integrator application
  parameter real noise= 0      // modulo noise stddev
) (
  `input_real gain,   // scale the output by this amount
  `input_pwl si, 
  `output_pwl so, 
  output reg trigger,
  `output_real i_modulo
);

timeunit `DAVE_TIMEUNIT ;
timeprecision `DAVE_TIMEUNIT ;

`protect
//pragma protect 
//pragma protect begin

`get_timeunit 
PWLMethod pm=new;

pwl reset_sig;
initial reset_sig = pm.write(0,0,0);

pwl_integrator_w_reset #( .etol(etol), .vinit(vinit), .modulo(modulo), .noise(noise) ) xinteg( .gain(gain), .si(si), .reset(1'b0), .reset_sig(reset_sig), .so(so), .trigger(trigger), .i_modulo(i_modulo) );

//pragma protect end
`endprotect

endmodule
