/****************************************************************

Copyright (c) 2018- Stanford University. All rights reserved.

The information and source code contained herein is the 
property of Stanford University, and may not be disclosed or
reproduced in whole or in part without explicit written 
authorization from Stanford University. Contact bclim@stanford.edu for details.

* Filename   : pwl_add.v
* Author     : Byongchan Lim (bclim@stanford.edu)
* Description: 
  - Add arbitrary number of pwl signals

* Note       :

* Revision   :
  - 7/26/2016: First release

****************************************************************/


module pwl_add #(
  parameter integer no_sig = 2    // number of signal inputs
) (
  `input_pwl in[no_sig-1:0],      // pwl inputs
  `input_real scale[no_sig-1:0],  // scale factor for each input
  input enable,   // enable add op., if 'L': keep the output, pull-up when unconnected
  `output_pwl out                 // pwl output
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

genvar i;
generate
  for (i=0; i<no_sig; i++) begin: event_gen
     always @(`pwl_event(in[i])) -> event_in;
     always @(scale[i]) -> event_in;
  end
endgenerate

always @(event_in or enable) 
  if(enable) begin
    t = `get_time;
    out_a = 0.0;
    out_b = 0.0;
    for(int j=0; j<no_sig; j++) begin
      out_a += scale[j]*(in[j].a + in[j].b*(t-in[j].t0));
      out_b += scale[j]*in[j].b;
    end
    out = pm.write(out_a, out_b, t);
  end

//pragma protect end
`endprotect

endmodule
