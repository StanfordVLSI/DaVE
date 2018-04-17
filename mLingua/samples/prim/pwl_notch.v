/****************************************************************

Copyright (c) 2018- Stanford University. All rights reserved.

The information and source code contained herein is the 
property of Stanford University, and may not be disclosed or
reproduced in whole or in part without explicit written 
authorization from Stanford University. Contact bclim@stanford.edu for details.

* Filename   : pwl_notch.v
* Author     : Byongchan Lim (bclim@stanford.edu)
* Description: 
  This is a notch filter where its transfer function in s-domain 
  is given by 
    - TF(s) = (s^2+w0^2)/(s^2+w0/q*s+w0^2)

* Note       :

* Revision   :
  - 7/26/2016: First release

****************************************************************/

module pwl_notch #(
  parameter real etol=0.001;  // error tolerance of PWL approximation
)(
  `input_pwl q,  // Q-factor
  `input_pwl w0, // resonant frequency in radian
  `input_pwl si, // filter signal input 
  `output_pwl so // filter signal output
);

timeunit `DAVE_TIMEUNIT ;
timeprecision `DAVE_TIMEUNIT ;

`protect
//pragma protect 
//pragma protect begin


// DPI-C function if needed (only takes an input and produces a real output)


`get_timeunit // get timeunit in sec and assign it to the variable 'TU'

// Method for PWL signal processing
PWLMethod pm=new;

// User parameters

real a;
real b;


// wires
event wakeup;  // event signal
real t0;  // time offset
real t_cur;   // current time
real dT;  // time interval of PWL waveform

pwl si_at_t0;  // 
real so_cur; // current output signal value
real so_prev; // previous output signal value
real so_nxt;  // so at (t_cur+dT) for pwl output data
real yo0;  // output signal value offset (so_cur at t0)
real yo1;  // first derivative y'(0)
real xi0;  // initial state of input
real xi1;  // initial state of first derivative of input

real so_slope; // so slope

real q_s; // sampled version of q when input si changes
real w0_s; // sampled version of w0 when input si changes


// @si_sensitivity is just "si" if it is piecewise constant waveform
// otheriwse, it is "si.t0 or si.s0 or si.slope"

always @(`pwl_event(si) or wakeup) begin
  t_cur = `get_time;
  q_s = pm.eval(q, t_cur); // sampled version of q
  w0_s = pm.eval(w0, t_cur); // sampled version of w0
  a = -w0_s*(sqrt(-4*q_s**2 + 1) - 1)/(2*q_s);
  b = +w0_s*(sqrt(-4*q_s**2 + 1) + 1)/(2*q_s);

  if (t_cur == 0) begin // DC initialization
    so_cur = fn_filter_notch(1e-06, si, si.a, si.b, yo0, yo1  , q_s, w0_s);
    if (isnan(so_cur)) so_cur = 0.0;
    so = pm.write(so_cur, 0.0, t_cur);
    yo0 = so_cur;
    si_at_t0 = si;
  end
  else begin  // After DC initialization
    so_cur = fn_filter_notch(t_cur-t0, si_at_t0, xi0, xi1, yo0, yo1  , q_s, w0_s);
    // so_cur = so.a + so.b*(t_cur-so.t0);
    // you may need some additional code here
  
    
    if (`pwl_check_diff(si, si_at_t0)) begin 
  
      t0 = t_cur;
      yo0 = so_cur;
      yo1 = so.b;
    
      xi0 = si.a;
      xi1 = si.b;
  
      //yo1 = fn_1_derivative_filter_notch(t_cur-t0, si_at_t0, xi0, xi1, yo0, yo1 , q_s, w0_s); 
      si_at_t0 = si;
  
      // you may need some additional code here
    end
  
    dT = calculate_Tintv_filter_notch(etol, t_cur-t0, si_at_t0, xi0, xi1, yo0, yo1  , q_s, w0_s);
    // don't update signal/event if dT > 1e-06
    if (dT <= 1e-06) begin
      so_nxt = fn_filter_notch(t_cur-t0+dT, si_at_t0, xi0, xi1, yo0, yo1  , q_s, w0_s);
      so_slope = (so_nxt-so_cur)/dT;
      so = pm.write(so_cur, so_slope, t_cur);
      ->> #(dT/TU) wakeup;
    end
    else begin
      so = pm.write(so_cur, 0.0, t_cur);
    end
  
    // you may need some additional code here 
  end

end

/*******************************************
  Response function, its 1st/2nd derivatives
*******************************************/

function real fn_filter_notch;
input real t; 
input pwl si; 
input real xi0, xi1, yo0, yo1  , q, w0;
begin
  return (a*b**2*yo0 - b**3*si.a + b**3*xi0 + b**2*si.b - b**2*xi1 + b**2*yo1 - b*si.a*w0**2 + si.b*w0**2)*exp(-b*t)/(b**2*(a - b)) + si.b*t*w0**2/(a*b) + (a**3*si.a - a**3*xi0 - a**2*b*yo0 - a**2*si.b + a**2*xi1 - a**2*yo1 + a*si.a*w0**2 - si.b*w0**2)*exp(-a*t)/(a**2*(a - b)) + w0**2*(a*b*si.a - a*si.b - b*si.b)/(a**2*b**2);
end
endfunction


function real fn_1_derivative_filter_notch;
input real t; 
input pwl si; 
input real xi0, yo0, yo1  , q, w0;
begin
  return -(a*b**2*yo0 - b**3*si.a + b**3*xi0 + b**2*si.b - b**2*xi1 + b**2*yo1 - b*si.a*w0**2 + si.b*w0**2)*exp(-b*t)/(b*(a - b)) - (a**3*si.a - a**3*xi0 - a**2*b*yo0 - a**2*si.b + a**2*xi1 - a**2*yo1 + a*si.a*w0**2 - si.b*w0**2)*exp(-a*t)/(a*(a - b)) + si.b*w0**2/(a*b);
end
endfunction
    

function real f2max_filter_notch;
input real t; 
input pwl si; 
input real xi0, xi1, yo0, yo1  , q, w0;
begin
  return abs(-(-a**3*si.a + a**3*xi0 + a**2*b*yo0 + a**2*si.b - a**2*xi1 + a**2*yo1 - a*si.a*w0**2 + si.b*w0**2)*exp(-a*t)/(a-b)) + abs((a*b**2*yo0 - b**3*si.a + b**3*xi0 + b**2*si.b - b**2*xi1 + b**2*yo1 - b*si.a*w0**2 + si.b*w0**2)*exp(-b*t)/(a-b));
end
endfunction

/*************************************
  Caluating Tintv
*************************************/

function real calculate_Tintv_filter_notch;
input real etol, t; 
input pwl si; 
input real xi0, xi1, yo0, yo1  , q, w0;
real abs_f2max;
real calcT;
begin
  abs_f2max = f2max_filter_notch(t, si, xi0, xi1, yo0, yo1  , q, w0);
  calcT = sqrt(8.0*etol/abs_f2max);
  return max(TU,min(1.0,calcT));
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
