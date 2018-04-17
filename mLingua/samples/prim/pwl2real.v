/****************************************************************

Copyright (c) 2018- Stanford University. All rights reserved.

The information and source code contained herein is the 
property of Stanford University, and may not be disclosed or
reproduced in whole or in part without explicit written 
authorization from Stanford University. Contact bclim@stanford.edu for details.

* Filename   : pwl2real.v
* Author     : Byongchan Lim (bclim@stanford.edu)
* Description: 
  - pwl2real converts a pwl signal to a pwc (real) signal. The output
    will be updated when the projected input value differs from its current
    output by dv parameter value.

* Note       :

* Revision   :
  - 7/26/2016: First release

****************************************************************/

module pwl2real #(
  parameter real dv = 0.0  // delta value of input signal that needs to update out
) (
  `input_pwl in,
  `output_real out
);

timeunit `DAVE_TIMEUNIT ;
timeprecision `DAVE_TIMEUNIT ;

`protect
//pragma protect 
//pragma protect begin

`get_timeunit
PWLMethod pm=new;

event wakeup;
time dT=0;
time dTm, t_prev, t0m;
real dTr;
real slope;


initial ->> wakeup;

always @(`pwl_event(in)) begin
  t_prev = $time;
  dT = 0;
  ->> wakeup;
end

always @(wakeup) begin
  t0m = $time;
  dTm = t0m - t_prev;
  if (dT==dTm) begin  // without this, 2x events are generated
    t_prev = $time;
    out = pm.eval(in,`get_time);
    slope = abs(in.b);
    if (slope != 0) begin
      dTr = min(`DT_MAX,max(TU, dv/slope));
      dT = time'(dTr/TU);
      ->> #(dT) wakeup;
    end
  end
end

//pragma protect end
`endprotect

endmodule
