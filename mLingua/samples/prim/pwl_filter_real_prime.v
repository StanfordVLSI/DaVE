/****************************************************************

Copyright (c) 2018- Stanford University. All rights reserved.

The information and source code contained herein is the 
property of Stanford University, and may not be disclosed or
reproduced in whole or in part without explicit written 
authorization from Stanford University. Contact bclim@stanford.edu for details.

* Filename   : pwl_filter_real_prime.v
* Author     : Byongchan Lim (bclim@stanford.edu)
* Description: 
  - A linear filter primitive cell. It supports upto a (real) zero 
    and two (real) poles. If you need more complicated (i.e. higher-order) 
    filters, it might be good to  cascade many of this primitive, or build 
    a custom model. When cascading many filters, be aware that it is 
    possible to lose some signals because of the pwl approximation. So,
    you have to consider which poles/zeros comes first. 
  - For now, the type of filters can be set by the "filter_type" input where
    - 0: a pole
    - 1: two poles
    - 2: two poles and a zero
    - 3: a pole and a zero

* Note       :
  - If "in" is a "real" signal, a trick is to change it to a pwl
    signal with zero slope.

* Revision   :
  - 7/26/2016: First release

****************************************************************/

`include "mLingua_pwl.vh"

module pwl_filter_real_prime #(
  parameter etol = 0.005,     // error tolerance of PWL approximation
  parameter logic en_filter = 1'b1  // enable output event filtering
) (
  `input_real wz1,      // zero location in radian
  `input_real wp1,      // 1st pole location in radian
  `input_real wp2,      // 2nd pole location in radian
  `input_pwl in,        // filter signal input 
  `input_pwl reset_sig, // input when reset is asserted
  input reset,          // '1': out = reset_sig instantaneouly, '0': out = in with filtering op.
  input hold,           // '1': hold the output, '0': normal op (pull-down when unconnected)
  input integer filter_type,  // select filter type. see the note above
  input en_complex,     // two poles are conjugate if True, then wp1 is real part, wp2 is imaginary part, this port is pulled-down when floating

  `output_pwl out       // filter output
);

timeunit `DAVE_TIMEUNIT ;
timeprecision `DAVE_TIMEUNIT ;

`protect
//pragma protect 
//pragma protect begin
`get_timeunit // get timeunit in sec and assign it to the variable 'TU'
PWLMethod pm=new; // Method for PWL signal processing

pulldown(en_complex);
pulldown(reset);
pulldown(hold);

// wires
event  wakeup;  // event signal
real t0;  // time offset
real t_cur;   // current time
real dTr;  // time interval of PWL waveform
time dT=1;
time dTm=0;
time t_prev;
time t0m;

real out_cur; // current output signal value
real out_nxt;  // out at (t_cur+dT) for pwl output data
real yo0;  // output signal value offset (out_cur at t0)
real yo1;  // first derivative y'(0)
real xi0;  // initial state of input

real out_slope; // out slope

real A, B0, B1, C;
real p1, p2, z1;
real err;
wire i_reset;
event dummy_event;

initial ->> dummy_event;


initial p1 = 1;
initial p2 = 2;
initial z1 = 1;

assign i_reset = reset;

pwl reset_sig_d;

always @(`pwl_event(reset_sig) or i_reset) 
  if (i_reset) reset_sig_d = reset_sig;

always @(`pwl_event(in) or `pwl_event(reset_sig_d) or i_reset or hold or wp1 or wp2 or wz1 or dummy_event or filter_type or en_complex) begin
  if (hold) begin
    t_cur = `get_time;
    t0 = t_cur;
    yo0 = pm.eval(out, t_cur);
    out = pm.write(yo0, 0, t_cur);
  end
  else if (i_reset) begin
    t_cur = `get_time;
    t0 = t_cur;
    yo0 = pm.eval(reset_sig_d, t_cur);
    yo1 = reset_sig_d.b;
    out = pm.write(yo0,yo1, t_cur);
  end
  else begin
    if ($time == 0) out = in; // dc initialization
    t_cur = `get_time;
    out_cur = pm.eval(out, t_cur);
    yo0 = out_cur;
    if (filter_type != 0) yo1 = fn1_filter_prime(t_cur-t0);
    else yo1 = out.b; // somehow this approx. doesn't work for CTLE example.
    xi0 = in.a;
    t0 = t_cur;
    if (!en_complex)
      if (wp1 > 0) p1 = wp1; else p1=1;
    else
      p1 = wp1;
    if (wp2 > 0) p2 = wp2; else p2=2;
    if (wz1 > 0) z1 = wz1; else z1=1;
    if (p1 == p2) p2 = p1+1;
    if (filter_type==2) begin // p2z1
      A = in.a + in.b/z1 - in.b*(1/p2+1/p1);
      B0 = -(p1*p2*in.a/z1 - p1*p2*xi0/z1 - p2*in.a - p2*in.b/z1 + p2*yo0 + yo1 + p2*in.b/p1)/(p1 - p2);
      B1 = (p1*p2*in.a/z1 - p1*p2*xi0/z1 - p1*in.a - p1*in.b/z1 + p1*yo0 + yo1 + p1*in.b/p2)/(p1 - p2);
      C = in.b;
    end
    else if (filter_type==1) begin // p2
      A = in.a - in.b*(1/p2+1/p1);
      B0 = -(-p1*p2*in.a + p1*p2*yo0 + p1*yo1 + p2*in.b)/p1/(p1 - p2);
      B1 = (-p1*p2*in.a + p1*p2*yo0 + p2*yo1 + p1*in.b)/p2/(p1 - p2);
      C = in.b;
    end
    else if (filter_type==0) begin // p1
      A = in.a - in.b/p1;
      B0 = -in.a + in.b/p1 + yo0;
      B1 = 0;
      C = in.b;
    end
    else if (filter_type==3) begin // p1z1
      A = in.a + in.b/z1 - in.b/p1;
      B0 = -in.a + in.b/p1 + yo0 - in.b/z1;
      B1 = 0;
      C = in.b;
    end
    t_prev = $time;
    dT = 0;
    if ($time != 0) ->> wakeup;
  end
end

always @(wakeup) begin
  t0m = $time;
  dTm = t0m - t_prev;
  if (dT==dTm && ~hold && ~reset) begin
    t_prev = $time;
    t_cur = `get_time;
    out_cur = pm.eval(out, t_cur);
    
    dTr = calculate_Tintv_filter_prime(etol, t_cur-t0);
    dT = time'(dTr/TU);

    out_nxt = fn_filter_prime(t_cur-t0+dTr);
    out_slope = (out_nxt-out_cur)/dTr;
    err = abs(out.b*dTr - out_slope*dTr);
    if (en_filter == 1'b1) 
      if (err >= etol) out = pm.write(out_cur, out_slope, t_cur);
      else out = out;
    else
      out = pm.write(out_cur, out_slope, t_cur);
    ->> #(dT) wakeup;
  end
end

/*******************************************
  Response function, its 1st/2nd derivatives
*******************************************/

function real fn_filter_prime;
input real t; 
begin
  if (!en_complex) 
    return A + B0*exp(-p1*t) + B1*exp(-p2*t) + C*t;
  else
    if (filter_type==1) // p2
      return in.a - 2*in.b*p1/(p1**2 + p2**2) + in.b*t + p1*(-in.a*p1**2*sin(p2*t) - in.a*p2**2*sin(p2*t) + in.b*p1*sin(p2*t) + in.b*p2*cos(p2*t) + p1**2*yo0*sin(p2*t) + p1*yo1*sin(p2*t) + p2**2*yo0*sin(p2*t) - p2*yo1*cos(p2*t))*exp(-p1*t)/(p2*(p1**2 + p2**2)) + (-in.a*p1**2*cos(p2*t) - in.a*p2**2*cos(p2*t) + in.b*p1*cos(p2*t) - in.b*p2*sin(p2*t) + p1**2*yo0*cos(p2*t) + p1*yo1*cos(p2*t) + p2**2*yo0*cos(p2*t) + p2*yo1*sin(p2*t))*exp(-p1*t)/(2*(p1**2 + p2**2)) - (in.a*p1**2*cos(p2*t) + in.a*p2**2*cos(p2*t) - in.b*p1*cos(p2*t) + in.b*p2*sin(p2*t) - p1**2*yo0*cos(p2*t) - p1*yo1*cos(p2*t) - p2**2*yo0*cos(p2*t) - p2*yo1*sin(p2*t))*exp(-p1*t)/(2*(p1**2 + p2**2));
    else if (filter_type==2) // p2z1
      return in.a - 2*in.b*p1/(p1**2 + p2**2) + in.b*t + in.b/z1 + (in.a*p1**2*sin(p2*t)/z1 - in.a*p1*sin(p2*t) + in.a*p2**2*sin(p2*t)/z1 - in.a*p2*cos(p2*t) + in.b*p1**2*sin(p2*t)/(p1**2 + p2**2) + 2*in.b*p1*p2*cos(p2*t)/(p1**2 + p2**2) - in.b*p1*sin(p2*t)/z1 - in.b*p2**2*sin(p2*t)/(p1**2 + p2**2) - in.b*p2*cos(p2*t)/z1 - p1**2*xi0*sin(p2*t)/z1 + p1*yo0*sin(p2*t) - p2**2*xi0*sin(p2*t)/z1 + p2*yo0*cos(p2*t) + yo1*sin(p2*t))*exp(-p1*t)/p2;
    else
      return 0;
end
endfunction

function real fn1_filter_prime;
input real t; 
begin
  if (!en_complex) 
    return (-p1)*B0*exp(-p1*t) + (-p2)*B1*exp(-p2*t) + C;
  else
    if (filter_type==1) // p2
      return in.b - p1**2*(-in.a*p1**2*sin(p2*t) - in.a*p2**2*sin(p2*t) + in.b*p1*sin(p2*t) + in.b*p2*cos(p2*t) + p1**2*yo0*sin(p2*t) + p1*yo1*sin(p2*t) + p2**2*yo0*sin(p2*t) - p2*yo1*cos(p2*t))*exp(-p1*t)/(p2*(p1**2 + p2**2)) - p1*(-in.a*p1**2*cos(p2*t) - in.a*p2**2*cos(p2*t) + in.b*p1*cos(p2*t) - in.b*p2*sin(p2*t) + p1**2*yo0*cos(p2*t) + p1*yo1*cos(p2*t) + p2**2*yo0*cos(p2*t) + p2*yo1*sin(p2*t))*exp(-p1*t)/(2*(p1**2 + p2**2)) + p1*(in.a*p1**2*cos(p2*t) + in.a*p2**2*cos(p2*t) - in.b*p1*cos(p2*t) + in.b*p2*sin(p2*t) - p1**2*yo0*cos(p2*t) - p1*yo1*cos(p2*t) - p2**2*yo0*cos(p2*t) - p2*yo1*sin(p2*t))*exp(-p1*t)/(2*(p1**2 + p2**2)) + p1*(-in.a*p1**2*p2*cos(p2*t) - in.a*p2**3*cos(p2*t) + in.b*p1*p2*cos(p2*t) - in.b*p2**2*sin(p2*t) + p1**2*p2*yo0*cos(p2*t) + p1*p2*yo1*cos(p2*t) + p2**3*yo0*cos(p2*t) + p2**2*yo1*sin(p2*t))*exp(-p1*t)/(p2*(p1**2 + p2**2)) - (-in.a*p1**2*p2*sin(p2*t) - in.a*p2**3*sin(p2*t) + in.b*p1*p2*sin(p2*t) + in.b*p2**2*cos(p2*t) + p1**2*p2*yo0*sin(p2*t) + p1*p2*yo1*sin(p2*t) + p2**3*yo0*sin(p2*t) - p2**2*yo1*cos(p2*t))*exp(-p1*t)/(2*(p1**2 + p2**2)) + (in.a*p1**2*p2*sin(p2*t) + in.a*p2**3*sin(p2*t) - in.b*p1*p2*sin(p2*t) - in.b*p2**2*cos(p2*t) - p1**2*p2*yo0*sin(p2*t) - p1*p2*yo1*sin(p2*t) - p2**3*yo0*sin(p2*t) + p2**2*yo1*cos(p2*t))*exp(-p1*t)/(2*(p1**2 + p2**2));
    else if (filter_type==2) // p2z1
      return in.b - p1*(in.a*p1**2*sin(p2*t)/z1 - in.a*p1*sin(p2*t) + in.a*p2**2*sin(p2*t)/z1 - in.a*p2*cos(p2*t) + in.b*p1**2*sin(p2*t)/(p1**2 + p2**2) + 2*in.b*p1*p2*cos(p2*t)/(p1**2 + p2**2) - in.b*p1*sin(p2*t)/z1 - in.b*p2**2*sin(p2*t)/(p1**2 + p2**2) - in.b*p2*cos(p2*t)/z1 - p1**2*xi0*sin(p2*t)/z1 + p1*yo0*sin(p2*t) - p2**2*xi0*sin(p2*t)/z1 + p2*yo0*cos(p2*t) + yo1*sin(p2*t))*exp(-p1*t)/p2 + (in.a*p1**2*p2*cos(p2*t)/z1 - in.a*p1*p2*cos(p2*t) + in.a*p2**3*cos(p2*t)/z1 + in.a*p2**2*sin(p2*t) + in.b*p1**2*p2*cos(p2*t)/(p1**2 + p2**2) - 2*in.b*p1*p2**2*sin(p2*t)/(p1**2 + p2**2) - in.b*p1*p2*cos(p2*t)/z1 - in.b*p2**3*cos(p2*t)/(p1**2 + p2**2) + in.b*p2**2*sin(p2*t)/z1 - p1**2*p2*xi0*cos(p2*t)/z1 + p1*p2*yo0*cos(p2*t) - p2**3*xi0*cos(p2*t)/z1 - p2**2*yo0*sin(p2*t) + p2*yo1*cos(p2*t))*exp(-p1*t)/p2;
    else
      return 0;
end
endfunction


function real f2max_filter_prime;
input real t; 
begin
  if (!en_complex) 
    //return abs(B0)*p1**2*exp(-p1*t) + abs(B1)*p2**2*exp(-p2*t);
    return max(abs(B0*p1**2*exp(-p1*t)),abs(B1*p2**2*exp(-p2*t)));
  else
    if (filter_type==1) // p2
      //return abs(-(-2*p1**3*(-in.a*p1**2*sin(p2*t) - in.a*p2**2*sin(p2*t) + in.b*p1*sin(p2*t) + in.b*p2*cos(p2*t) + p1**2*yo0*sin(p2*t) + p1*yo1*sin(p2*t) + p2**2*yo0*sin(p2*t) - p2*yo1*cos(p2*t))/(p2*(p1**2 + p2**2)) + p1**2*(-in.a*p1**2*cos(p2*t) - in.a*p2**2*cos(p2*t) + in.b*p1*cos(p2*t) - in.b*p2*sin(p2*t) + p1**2*yo0*cos(p2*t) + p1*yo1*cos(p2*t) + p2**2*yo0*cos(p2*t) + p2*yo1*sin(p2*t))/(p1**2 + p2**2) - p1**2*(in.a*p1**2*cos(p2*t) + in.a*p2**2*cos(p2*t) - in.b*p1*cos(p2*t) + in.b*p2*sin(p2*t) - p1**2*yo0*cos(p2*t) - p1*yo1*cos(p2*t) - p2**2*yo0*cos(p2*t) - p2*yo1*sin(p2*t))/(p1**2 + p2**2) - 2*p1*p2*(-in.a*p1**2*sin(p2*t) - in.a*p2**2*sin(p2*t) + in.b*p1*sin(p2*t) + in.b*p2*cos(p2*t) + p1**2*yo0*sin(p2*t) + p1*yo1*sin(p2*t) + p2**2*yo0*sin(p2*t) - p2*yo1*cos(p2*t))/(p1**2 + p2**2) + p2**2*(-in.a*p1**2*cos(p2*t) - in.a*p2**2*cos(p2*t) + in.b*p1*cos(p2*t) - in.b*p2*sin(p2*t) + p1**2*yo0*cos(p2*t) + p1*yo1*cos(p2*t) + p2**2*yo0*cos(p2*t) + p2*yo1*sin(p2*t))/(p1**2 + p2**2) - p2**2*(in.a*p1**2*cos(p2*t) + in.a*p2**2*cos(p2*t) - in.b*p1*cos(p2*t) + in.b*p2*sin(p2*t) - p1**2*yo0*cos(p2*t) - p1*yo1*cos(p2*t) - p2**2*yo0*cos(p2*t) - p2*yo1*sin(p2*t))/(p1**2 + p2**2))*exp(-p1*t)/2);
      return abs((2*p1**3*(abs(-in.a*p1**2) + abs(in.a*p2**2) + abs(in.b*p1) + abs(in.b*p2) + abs(p1**2*yo0) + abs(p1*yo1) + abs(p2**2*yo0) + abs(p2*yo1))/(p2*(p1**2 + p2**2)) + p1**2*(abs(-in.a*p1**2) + abs(in.a*p2**2) + abs(in.b*p1) + abs(in.b*p2) + abs(p1**2*yo0) + abs(p1*yo1) + abs(p2**2*yo0) + abs(p2*yo1))/(p1**2 + p2**2) + p1**2*(abs(in.a*p1**2) + abs(in.a*p2**2) + abs(in.b*p1) + abs(in.b*p2) + abs(p1**2*yo0) + abs(p1*yo1) + abs(p2**2*yo0) + abs(p2*yo1))/(p1**2 + p2**2) + 2*p1*p2*(abs(in.a*p1**2) + abs(in.a*p2**2) + abs(in.b*p1) + abs(in.b*p2) + abs(p1**2*yo0) + abs(p1*yo1) + abs(p2**2*yo0) + abs(p2*yo1))/(p1**2 + p2**2) + p2**2*(abs(in.a*p1**2) + abs(in.a*p2**2) + abs(in.b*p1) + abs(in.b*p2) + abs(p1**2*yo0) + abs(p1*yo1) + abs(p2**2*yo0) + abs(p2*yo1))/(p1**2 + p2**2) + p2**2*(abs(in.a*p1**2) + abs(in.a*p2**2) + abs(in.b*p1) + abs(in.b*p2) + abs(p1**2*yo0) + abs(p1*yo1) + abs(p2**2*yo0) + abs(p2*yo1))/(p1**2 + p2**2))*exp(-p1*t)/2);
    else if (filter_type==2) // p2z1
      return abs(-(-2*p1**2*(in.a*p1**2*sin(p2*t)/z1 - in.a*p1*sin(p2*t) + in.a*p2**2*sin(p2*t)/z1 - in.a*p2*cos(p2*t) + in.b*p1**2*sin(p2*t)/(p1**2 + p2**2) + 2*in.b*p1*p2*cos(p2*t)/(p1**2 + p2**2) - in.b*p1*sin(p2*t)/z1 - in.b*p2**2*sin(p2*t)/(p1**2 + p2**2) - in.b*p2*cos(p2*t)/z1 - p1**2*xi0*sin(p2*t)/z1 + p1*yo0*sin(p2*t) - p2**2*xi0*sin(p2*t)/z1 + p2*yo0*cos(p2*t) + yo1*sin(p2*t))/p2 - 2*p1*(-in.a*p1**2*cos(p2*t)/z1 + in.a*p1*cos(p2*t) - in.a*p2**2*cos(p2*t)/z1 - in.a*p2*sin(p2*t) - in.b*p1**2*cos(p2*t)/(p1**2 + p2**2) + 2*in.b*p1*p2*sin(p2*t)/(p1**2 + p2**2) + in.b*p1*cos(p2*t)/z1 + in.b*p2**2*cos(p2*t)/(p1**2 + p2**2) - in.b*p2*sin(p2*t)/z1 + p1**2*xi0*cos(p2*t)/z1 - p1*yo0*cos(p2*t) + p2**2*xi0*cos(p2*t)/z1 + p2*yo0*sin(p2*t) - yo1*cos(p2*t)) + 2*p1*(in.a*p1**2*cos(p2*t)/z1 - in.a*p1*cos(p2*t) + in.a*p2**2*cos(p2*t)/z1 + in.a*p2*sin(p2*t) + in.b*p1**2*cos(p2*t)/(p1**2 + p2**2) - 2*in.b*p1*p2*sin(p2*t)/(p1**2 + p2**2) - in.b*p1*cos(p2*t)/z1 - in.b*p2**2*cos(p2*t)/(p1**2 + p2**2) + in.b*p2*sin(p2*t)/z1 - p1**2*xi0*cos(p2*t)/z1 + p1*yo0*cos(p2*t) - p2**2*xi0*cos(p2*t)/z1 - p2*yo0*sin(p2*t) + yo1*cos(p2*t)) + 2*p2*(in.a*p1**2*sin(p2*t)/z1 - in.a*p1*sin(p2*t) + in.a*p2**2*sin(p2*t)/z1 - in.a*p2*cos(p2*t) + in.b*p1**2*sin(p2*t)/(p1**2 + p2**2) + 2*in.b*p1*p2*cos(p2*t)/(p1**2 + p2**2) - in.b*p1*sin(p2*t)/z1 - in.b*p2**2*sin(p2*t)/(p1**2 + p2**2) - in.b*p2*cos(p2*t)/z1 - p1**2*xi0*sin(p2*t)/z1 + p1*yo0*sin(p2*t) - p2**2*xi0*sin(p2*t)/z1 + p2*yo0*cos(p2*t) + yo1*sin(p2*t)))*exp(-p1*t)/2);
    else
      return 0;
end
endfunction

/*************************************
  Caluating Tintv
*************************************/

function real calculate_Tintv_filter_prime;
input real etol, t; 
real abs_f2max;
real calcT;
begin
  abs_f2max = f2max_filter_prime(t);
  calcT = sqrt(8.0*etol/abs_f2max);
  return min(`DT_MAX,max(TU,min(1.0,calcT)));
end
endfunction

//pragma protect end
`endprotect

endmodule
