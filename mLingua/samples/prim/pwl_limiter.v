/****************************************************************

Copyright (c) 2018- Stanford University. All rights reserved.

The information and source code contained herein is the 
property of Stanford University, and may not be disclosed or
reproduced in whole or in part without explicit written 
authorization from Stanford University. Contact bclim@stanford.edu for details.

* Filename   : pwl_limiter.v
* Author     : Byongchan Lim (bclim@stanford.edu)
* Description: 
  This performs a limiter function on a pwl signal. The possible maximum
  value and minimum value are set by inputs, "maxout" and "minout", respectively.
  One of the applications is to incorporate a gain compression behavior of a
  differential amplifier.
  - If "NO_MAX" parameter is set to '1', there will be no upper limiter.
  - If "NO_MIN" parameter is set to '1', there will be no lower limiter.

* Note       :

* Revision   :
  - 7/26/2016: First release

****************************************************************/


module pwl_limiter #(
  parameter logic NO_MAX = 1'b0,  // ignore maxout if 1
  parameter logic NO_MIN = 1'b0   // ignore minout if 1
) (
  `input_pwl scale, // gain, be effective when other inputs are changed
  `input_pwl maxout, minout, // maximum and minimum values
  `input_pwl in,   // input
  `output_pwl out  // compressed output
);

timeunit `DAVE_TIMEUNIT ;
timeprecision `DAVE_TIMEUNIT ;

`protect
//pragma protect 
//pragma protect begin

`get_timeunit // get timeunit in sec and assign it to the variable 'TU'
PWLMethod pm=new;

event wakeup, dummy;
real t0;         // current time stamp
real ci;         // gain*input value at t0
real co, err;
real smax, smin; // maxout and minout at t0
real gain;       // scale at t0
real dTr;        // real time value to schedule an event
time dT, dTm, t_prev,t0m;
reg update=1'b0;    // need to active wakeup

initial begin
  -> dummy;
  out = in;
end

always @(dummy or `pwl_event(in) or `pwl_event(maxout) or `pwl_event(minout)) begin
  t0 = `get_time;
  smax = pm.eval(maxout,t0);
  smin = pm.eval(minout,t0);
  dT = 0;
  t_prev = $time;
  ->> wakeup;
end

always @(wakeup) begin
  t0m = $time;
  dTm = t0m - t_prev;
  if (dTm == dT) begin
    t0 = `get_time;       // get current time
    gain = pm.eval(scale,t0);
    ci = gain*pm.eval(in,t0); 
    co = pm.eval(out,t0); 
  
    // update out
    if (ci >= smax && ~NO_MAX) // hit max value
      out = pm.write(smax, 0, t0);
    else if (ci <= smin && ~NO_MIN) // hit min value
      out = pm.write(smin, 0, t0);
    else
      out = pm.write(ci, gain*in.b, t0);
    //$display($time, " %m XXX ", t0m, " ", t_prev, " ", in.a, " ", in.b, " ", in.t0, " ", out.a, " ", out.b, " ",out.t0);
  
    // project the moment when the input will hit either smax or smin
    if (in.b > 0) begin
      if (ci < smin && ~NO_MIN) begin
        dTr = (smin-ci)/in.b;
        update = 1'b1;
      end
      else if (ci < smax && ~NO_MAX) begin
        dTr = (smax-ci)/in.b;
        update = 1'b1;
      end
      else update = 1'b0;
    end
    else if (in.b < 0) begin
      if (ci > smax && ~NO_MAX) begin
        dTr = (ci-smax)/-1.0/in.b;
        update = 1'b1;
      end
      else if (ci > smin && ~NO_MIN) begin
        dTr = (ci-smin)/-1.0/in.b;
        update = 1'b1;
      end
      else update = 1'b0;
    end
    else update = 1'b0;
  
    if (dTr> 0 && update) begin //
      dTr = min(`DT_MAX,max(dTr,TU));
      dT = time'(dTr/TU);
      ->> #(dT) wakeup;
      t_prev = $time;
    end
  end
end

//pragma protect end
`endprotect

endmodule
