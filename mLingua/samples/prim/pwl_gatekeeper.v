/****************************************************************

Copyright (c) 2018- Stanford University. All rights reserved.

The information and source code contained herein is the 
property of Stanford University, and may not be disclosed or
reproduced in whole or in part without explicit written 
authorization from Stanford University. Contact bclim@stanford.edu for details.

* Filename   : pwl_gatekeeper.v
* Author     : Byongchan Lim (bclim@stanford.edu)
* Description: 
  - Gate keeper on a continuous feedback path in order to
    (i) prevent infinite number of event generation, and
    (ii) reduce the frequency of possible limit-cycle oscillations.
  - Suggested "gain_error" parameter value is 1 - A/(1+A*f) where
    A is open-loop gain and f is feedback factor.

* Note       :

* Revision   :
  - 7/26/2016: First release

****************************************************************/

module pwl_gatekeeper #(
  parameter real etol=0.001,  // absolute error tolerance
  parameter en_lcc = 1'b1,    // enable limit cycle correction
  parameter real gain_error = 0.001, // limit-cycle criterion,
                                     // suggested value 1-A/(1+A*f)
  parameter integer no_ext_sig=1     // number of external inputs to activate loop
) (
  input logic ext_trig, // external trigger 
  `input_pwl extin[no_ext_sig-1:0],  // external inputs to a feedback system
  `input_pwl in,    // output of a feedback system
  `output_pwl out,  // filtered output of in
  output reg lock   // lock LC
);

timeunit `DAVE_TIMEUNIT ;
timeprecision `DAVE_TIMEUNIT ;

pulldown(ext_trig);

`protect
//pragma protect 
//pragma protect begin
// TODO
// lc signal is not toggling in the waveform although it is indeed.

`get_timeunit // get timeunit in sec and assign it to the variable 'TU'
PWLMethod pm=new;

event wakeup;
event wakeup2;
event wakeup_ext;
real t0;        // current time stamp
real err;       // error between input & output at t0
real dt1, dt2;  // intermediate time vairable to schedule an event
real dTr;       // real time value to schedule an event
real ci, co;    // input and output value at t0
time dTm, dT;   // time values in Verilog timeunit
time t_prev;    // save the current time in Vlog unit when scheduled an event
time t0m;
real smax, smin, sdiff; // max/min and their difference in limit cycle oscillation region
real ss;      // product of in & out slope
real a, b;
real retol;
real cloopgain; // loop gain
real tp;
real period;
real duty;
pwl in0;
real smax_prev;

parameter integer LC_BUFFER_BW=2;
reg [LC_BUFFER_BW-1:0] lc=0;

time tt_prev;

initial retol=etol;
initial lock = 1'b0;

always @(`pwl_event(in)) begin
  // either input changes or scheduled event wakes up
  t_prev = $time;
  t0 = t_prev*TU;
  ss = sgn(in.b*out.b); // check if sign is different

  // evaluate error
  ci = pm.eval(in,t0);  // input value at this moment
  co = pm.eval(out,t0);
  err = abs(co-ci);

  // update smax/smin only when input (in) changes
  // assume that smax == smin never happen
  // calculate closed loop gain
  if (out.b != 0.0) cloopgain = in.b/out.b;

  if ((in.b<0) && (smin!=ci) ) begin
    smax = ci;
    a = in.b;
  end
  else if ((in.b>0) && (smax!=ci) ) begin
    smin = ci;
    b = in.b;
  end
  sdiff = abs(smax - smin);

  if (en_lcc) begin
    // limit cycle condition
    //lc[LC_BUFFER_BW-1:1] <= lc[LC_BUFFER_BW-2:0];
    if ( (ss<0) && (abs(cloopgain+1.0)<=gain_error)) lc[0] <= 1'b1;
    else lc[0] <= 1'b0;
    if ( (lc[0]==1'b1)) begin
    /*
    if ( ss<0 ) lc[0] <= 1'b1;
    else lc[0] <= 1'b0;
    if ( (lc[0]==1'b1) && (sdiff<etol) ) begin
    */
      //out = pm.write((smax*abs(b)+smin*abs(a))/(abs(a)+abs(b)),0.0,t0);
      lock = 1'b1;
      out = pm.write((smax+smin)/2.0, 0, t0);
      err = abs(out.a-ci);
    end
    //else lock = 1'b0;
  end
  dT = 0;
  ->> wakeup;
  /*
  if (tt_prev != $time) begin
    in0 = in;
    tt_prev = $time;
  end
  */
end

event forced_update;
always @(ext_trig) begin // force to update the output
  dT = 0;
  t_prev = $time;
  ->> forced_update;
end


//always @(wakeup or forced_update) begin
always @(wakeup) begin
//  if (forced_update) begin
//    t0 = `get_time;
//    out = pm.write(pm.eval(in,t0),in.b,t0); // passthrough 'in' to 'out'
//  end
//  else begin
    t0m = $time;
    dTm = t0m - t_prev;
    if(dTm==dT) begin
      // either input changes or scheduled event wakes up
      t_prev = $time;
      t0 = t_prev*TU;
      // evaluate error
      ci = pm.eval(in,t0);  // input value at this moment
      co = pm.eval(out,t0);
      err = abs(co-ci);
    
      // filtering out unnecessary output update
        if (err >= retol) begin // update since err is large
          out = pm.write(pm.eval(in,t0),in.b,t0); // passthrough 'in' to 'out'
        end
        else begin // project the moment when the error >= etol
          dt1 = (retol-(co-ci))/(out.b-in.b);
          dt2 = (-retol-(co-ci))/(out.b-in.b);
          dTr = min(`DT_MAX,max(dt1,dt2));
          if (dTr>0 && dTr<1) begin // treat 1e3 sec as infinite time, because of casting problem(real to time) in ncverilog
            dTr = max(dTr,TU);
            dT = time'(dTr/TU);
            ->> #(dT) wakeup;
          end
        end
    end
//  end
end

/*
*/

genvar i;
generate
for (i=0; i<no_ext_sig; i++) begin: event_gen
  always @(`pwl_event(extin[i])) -> wakeup_ext;
end
endgenerate

always @(wakeup_ext) begin
  lock <= 1'b0;
//  release out;
end
/*****************************************************************
 Module Description: gatekeeper on a continuous feedback path


Copyright (c) 2014-Present by Byong Chan Lim. All rights reserved.

The information and source code contained herein is the property
of Byong Chan Lim, and may not be disclosed or reproduced
in whole or in part without explicit written authorization from
Byong Chan Lim.
*****************************************************************/

//pragma protect end
`endprotect

endmodule
