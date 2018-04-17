/****************************************************************

Copyright (c) 2018- Stanford University. All rights reserved.

The information and source code contained herein is the 
property of Stanford University, and may not be disclosed or
reproduced in whole or in part without explicit written 
authorization from Stanford University. Contact bclim@stanford.edu for details.

* Filename   : real2pwl.v
* Author     : Byongchan Lim (bclim@stanford.edu)
* Description: 
  It converts a real (pwc) signal to a pwl signal.

* Note       :
  - The time interval between input changes should be longer than "tr".
  - If 0 < "tr" < TU, "tr" is automatically set to TU.
  - If "tr" == 0, the output slope is set to 0.

* Revision   :
  - 7/26/2016: First release

****************************************************************/


module real2pwl #(
  parameter real tr = 100e-12 // transition time
)
(
  input en, // enable op. (act. Hi), set output to '{0,0,0} if Lo
            // en=Hi when unconnected
  `input_real in,
  `output_pwl out
);

timeunit `DAVE_TIMEUNIT ;
timeprecision `DAVE_TIMEUNIT ;

pullup(en);

`protect
//pragma protect 
//pragma protect begin

`get_timeunit
PWLMethod pm=new;

real in_prev;
real v0, v1;
real t0;
real tr_val;
event wakeup;
initial ->> wakeup;

//always @(TU) begin
initial begin
  if (tr < TU) tr_val = TU;
  else tr_val = tr;
end
//end

always @(in or wakeup or en) begin
  if (!en) out = pm.write(0, 0, 0);
  else begin
    t0 = `get_time;
    if (tr == 0.0) out = pm.write(in, 0.0, t0);
    else begin
      if (in_prev != in) begin
        v0 = pm.eval(out,t0);
        v1 = in;
        if (tr_val < TU) tr_val = TU;
        out = pm.write(v0, (v1-v0)/tr_val, t0);
        in_prev = in;
        ->> `delay(tr_val) wakeup;
      end
      else out = pm.write(in, 0, t0);
    end
  end
end

//pragma protect end
`endprotect

endmodule
