/****************************************************************

Copyright (c) 2018- Stanford University. All rights reserved.

The information and source code contained herein is the 
property of Stanford University, and may not be disclosed or
reproduced in whole or in part without explicit written 
authorization from Stanford University. Contact bclim@stanford.edu for details.

* Filename   : pwl_add3.v
* Author     : Byongchan Lim (bclim@stanford.edu)
* Description: 
  - Add two pwl signals

* Note       :
  - pwl_add.v supports the addition of arbitrary N pwl signals.

* Revision   :
  - 7/26/2016: First release

****************************************************************/


module pwl_add3 
(
  `input_pwl in1, in2, in3,       // pwl inputs
  `input_real scale1, scale2, scale3, // scale factor for each input
  input enable,   // enable add op., if 'L': keep the output, pull-up when unconnected
  `output_pwl out             // pwl output
);

timeunit `DAVE_TIMEUNIT ;
timeprecision `DAVE_TIMEUNIT ;
 
`protect
//pragma protect 
//pragma protect begin

pullup(enable);

`get_timeunit
PWLMethod pm=new;

real t, out_a, out_b;
event event_in;

always @(`pwl_event(in1) or `pwl_event(in2) or `pwl_event(in3) or scale1 or scale2 or scale3) -> event_in;

always @(event_in or enable) 
  if(enable) begin
    t = `get_time;
    out_a = scale1*pm.eval(in1,t) + scale2*pm.eval(in2,t) + scale3*pm.eval(in3,t);
    out_b = scale1*in1.b + scale2*in2.b + scale3*in3.b;
    out = pm.write(out_a, out_b, t);
  end

//pragma protect end
`endprotect

endmodule
