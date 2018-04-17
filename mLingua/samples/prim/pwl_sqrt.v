/****************************************************************

Copyright (c) 2018- Stanford University. All rights reserved.

The information and source code contained herein is the 
property of Stanford University, and may not be disclosed or
reproduced in whole or in part without explicit written 
authorization from Stanford University. Contact bclim@stanford.edu for details.

* Filename   : pwl_sqrt.v
* Author     : Byongchan Lim (bclim@stanford.edu)
* Description: 
  It takes square-root of "in".

* Note       :

* Revision   :
  - 7/26/2016: First release

****************************************************************/


module pwl_sqrt #(
  parameter real etol = 0.005, // error tolerance of PWL approximation
  parameter real scale = 1,    // gain factor
  parameter en_filter = 1'b0   // enable output event filtering
) (
  `input_pwl in, 
  `output_pwl out
);

timeunit `DAVE_TIMEUNIT ;
timeprecision `DAVE_TIMEUNIT ;

`protect
//pragma protect 
//pragma protect begin
`get_timeunit // get timeunit in sec and assign it to the variable 'TU'
PWLMethod pm=new; // Method for PWL signal processing

// wires
event  wakeup;  // event signal
real t0;  // time offset
real t_cur;   // current time
real dTr;  // time interval of PWL waveform
time dT=1;
time dTm;
time t_prev;
time t0m;

real so_cur; // current output signal value
real so_nxt;  // so at (t_cur+dT) for pwl output data
real so_slope; // so slope
real yo0;  // output signal value offset (so_cur at t0)


real A, B;
real err1, err2;
real so_cur_exact;

// a new input comes in
always @(`pwl_event(in)) begin
  t0 = `get_time;
  so_cur = pm.eval(out, t_cur);
  A = in.a;
  B = in.b;
  t_prev = $time;
  dT = 0;
  ->> wakeup;
end

// schedule an event to update PWL segments
always @(wakeup) begin
  t0m = $time;
  dTm = t0m - t_prev;
  if (dT==dTm) begin  // without this, 2x events are generated
    t_prev = $time;
    t_cur = `get_time;
    so_cur = pm.eval(out, t_cur);
    
    dTr = calculate_Tintv_sqrt(etol, t_cur-t0);
    //dTr = max(TU,min(dTr,1));
    so_nxt = fn_sqrt(t_cur-t0+dTr);
    so_slope = (so_nxt-so_cur)/dTr;
    if (en_filter == 1'b1) begin
      so_cur_exact = fn_sqrt(t_cur-t0);
      err1 = abs(out.b*dTr - so_slope*dTr);
      if (err1 >= etol)
        out = pm.write(so_cur, so_slope, t_cur);
    end
    else
      out = pm.write(so_cur, so_slope, t_cur);
    dT = time'(dTr/TU);
    ->> #(dT) wakeup;
  end
end

/*******************************************
  Response function, its 1st/2nd derivatives
*******************************************/

function real fn_sqrt;
input real t; 
begin
  return sqrt(A+B*t);
end
endfunction

function real f2max_sqrt;
input real t; 
begin
  return abs(-0.25*B**2)/(A+B*t)**1.5;
end
endfunction

/*************************************
  Caluating Tintv
*************************************/

function real calculate_Tintv_sqrt;
input real etol, t; 
real abs_f2max;
real calcT;
begin
  abs_f2max = f2max_sqrt(t);
  calcT = sqrt(8.0*etol/abs_f2max);
  return min(`DT_MAX,max(TU,min(1.0,calcT)));
  /*
  if (abs_f2max != 0)
    return sqrt(8.0*etol/abs_f2max); 
  else
    return TU;
  */
end
endfunction
//pragma protect end
`endprotect

endmodule
