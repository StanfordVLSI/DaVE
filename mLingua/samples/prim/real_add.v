/****************************************************************

Copyright (c) 2018- Stanford University. All rights reserved.

The information and source code contained herein is the 
property of Stanford University, and may not be disclosed or
reproduced in whole or in part without explicit written 
authorization from Stanford University. Contact bclim@stanford.edu for details.

* Filename   : real_add.v
* Author     : Byongchan Lim (bclim@stanford.edu)
* Description: 
  It adds multiple real signals.

* Note       :
  - It only works for VCS simulator.

* Revision   :
  - 7/26/2016: First release

****************************************************************/


module real_add #(
  parameter integer no_sig = 2   // number of signal inputs
) (
  input enable,   // enable add op., if 'L': keep the output, pull-up when unconnected
  `input_real in[no_sig-1:0],    // real inputs
  `input_real scale[no_sig-1:0], // scale factor for each input
  `output_real out               // real output
);

timeunit `DAVE_TIMEUNIT ;
timeprecision `DAVE_TIMEUNIT ;
 
`protect
//pragma protect 
//pragma protect begin

pullup(enable);

`get_timeunit

real t, out_a;
event wakeup;
initial ->> wakeup;

genvar i;
generate
  for (i=0; i<no_sig; i++) begin: event_gen
     always @(in[i]) -> wakeup;
     always @(scale[i]) -> wakeup;
  end
endgenerate

always @(wakeup or enable) begin
  if (enable) begin
    t = `get_time;
    out_a = 0.0;
    for(int j=0; j<no_sig; j++) begin
      out_a += scale[j]*in[j];
    end
    out = out_a;
  end
end

//pragma protect end
`endprotect

endmodule
