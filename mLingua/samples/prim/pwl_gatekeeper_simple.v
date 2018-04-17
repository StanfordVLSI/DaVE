/****************************************************************

Copyright (c) 2018- Stanford University. All rights reserved.

The information and source code contained herein is the 
property of Stanford University, and may not be disclosed or
reproduced in whole or in part without explicit written 
authorization from Stanford University. Contact bclim@stanford.edu for details.

* Filename   : pwl_gatekeeper_simple.v
* Author     : Byongchan Lim (bclim@stanford.edu)
* Description: 
  - Gate keeper on a continuous feedback path in order to
    prevent infinite number of event generation. 
  - Unlike "pwl_gatekeeper" and "pwl_gatekeeper1" cell, this model
    doesn't correct limit-cycle oscillations.

* Note       :

* Revision   :
  - 7/26/2016: First release

****************************************************************/


module pwl_gatekeeper_simple #(
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

`get_timeunit // get timeunit in sec and assign it to the variable 'TU'
PWLMethod pm=new;

event wakeup;
real t0;        // current time stamp
real err;       // error between input & output at t0
real dt1, dt2;  // intermediate time vairable to schedule an event
real dTr;       // real time value to schedule an event
real ci, co;    // input and output value at t0
time dT;        // time values in Verilog timeunit


always @(`pwl_event(in) or wakeup) begin
  // either input changes or scheduled event wakes up
  t0 = `get_time;

  // evaluate error
  ci = pm.eval(in,t0);  // input value at this moment
  co = pm.eval(out,t0);
  err = abs(co-ci);

  // filtering out unnecessary output update
  //if (err >= etol && (out.t0 != in.t0)) // update since err is large
  if (err >= etol) // update since err is large
    out = pm.write(pm.eval(in,t0),in.b,t0); // passthrough 'in' to 'out'
  else begin // project the moment when the error >= etol
    dt1 = (etol-(co-ci))/(out.b-in.b);
    dt2 = (-etol-(co-ci))/(out.b-in.b);
    dTr = min(`DT_MAX,max(dt1,dt2));
    if (dTr>0 && dTr<1e3) begin // treat 1e3 sec as infinite time, because of casting problem(real to time) in ncverilog
      dTr = max(dTr,TU);
      dT = time'(dTr/TU);
      ->> #(dT) wakeup;
    end
  end
end

//pragma protect end
`endprotect

endmodule
