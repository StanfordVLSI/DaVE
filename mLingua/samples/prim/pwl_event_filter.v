/****************************************************************

Copyright (c) 2018- Stanford University. All rights reserved.

The information and source code contained herein is the 
property of Stanford University, and may not be disclosed or
reproduced in whole or in part without explicit written 
authorization from Stanford University. Contact bclim@stanford.edu for details.

* Filename   : pwl_event_filter.v
* Author     : Byongchan Lim (bclim@stanford.edu)
* Description: 
  - Filtering output events for given error tolerance.

* Note       :

* Revision   :
  - 0/00/2018: First release

****************************************************************/


module pwl_event_filter #(
  parameter real etol=0.001     // absolute error tolerance
) (
  `input_pwl in,   // input
  `output_pwl out  // output
);

timeunit `DAVE_TIMEUNIT ;
timeprecision `DAVE_TIMEUNIT ;

`protect
//pragma protect 
//pragma protect begin

localparam real h_etol = etol/2.0;

`get_timeunit // get timeunit in sec and assign it to the variable 'TU'
PWLMethod pm=new;

event dummy;
event wakeup;
real t0;        // current time stamp
real err;       // error between input & output at t0
real dTr;       // real time value to schedule an event
real ci, co;    // input and output value at t0
time dT, t_prev, t0m, dTm;

initial ->> dummy;

always @(`pwl_event(in), dummy) begin
  t_prev = $time;
  dT = 0;
  ->> wakeup;
end

always @(wakeup) begin
  t0m = $time;
  dTm = t0m - t_prev;
  if (dT == dTm) begin
    t0 = `get_time;
  
    // evaluate error
    ci = pm.eval(in,t0);  // input value at this moment
    co = pm.eval(out,t0);
    err = abs(co-ci);
  
    // filtering out unnecessary output update
    if ( (t0m==0) || (err >= h_etol) || (out.b==in.b) ) // update since err is large
      out = pm.write(ci, in.b, t0);
    else begin // schedule a new event at the moment when the error >= h_etol
      dTr = abs((h_etol-err)/(out.b-in.b));
      dTr = min(dTr, `DT_MAX);
      dT = time'(dTr/TU);
      if (dT==0) dT = 1;
      ->> #(dT) wakeup;
      t_prev = t0m;
    end
  end
end

//pragma protect end
`endprotect

endmodule
