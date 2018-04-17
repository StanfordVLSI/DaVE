/****************************************************************

Copyright (c) 2018- Stanford University. All rights reserved.

The information and source code contained herein is the 
property of Stanford University, and may not be disclosed or
reproduced in whole or in part without explicit written 
authorization from Stanford University. Contact bclim@stanford.edu for details.

* Filename   : lpf.v
* Author     : Byongchan Lim (bclim@stanford.edu)
* Description: 2nd-order passive low-pass filter for a pll

* Note       :

* Revision   :
  - 7/26/2016: First release

****************************************************************/

module lpf #(
  parameter real etol = 1e-9, // error tolerance of PWL approximation
  parameter real C1 = 5e-13,
  parameter real C2 = 5e-14,
  parameter real R = 20000.0,
  parameter real vinit = 0    // initial voltage
) (
  `input_real si, `output_pwl vc
);

`get_timeunit
PWLMethod pm=new;

parameter real p1 = (C1+C2)/R/C1/C2;

// wires
event wakeup;  // wake-up signal
real t0;  // time offset
real t_cur;   // current time
time t_prev;
time dT=1;
time dTm;  // time interval of PWL waveform
real dTr;
reg event_in=1'b0;

real si_at_t0;  // 
real so_cur; // current output signal value
real yo0;  // output signal value offset (so_cur at t0)


real so_nxt;  // so at (t_cur+dT) for pwl output data
real so_slope; // so slope
real so_prev;

real vc1, vc1_nxt;
real vc0, vc10;
real A, B;
real expt;
int index;

pwl so;
pwl vc1_pwl;

initial begin
  vc1 = vinit;
  vc1_pwl = pm.write(vinit,0,0);
end
//pragma protect end
`endprotect

`include "lut_exp_pll.v"

`protect
//pragma protect
//pragma protect begin
pwl_add2 lpwladd( .in1(vc1_pwl), .in2(so), .scale1(1.0), .scale2(R), .out(vc) );

// @si_sensitivity is just "si" if it is piecewise constant waveform
// otheriwse, it is "si.t0 or si.s0 or si.slope"
always @(si or wakeup) begin
  dTm = $realtime - t_prev;
  event_in = si != si_at_t0;
  if (dT==dTm || event_in) begin
    t_prev = $realtime;
    t_cur = `get_time;
    so_cur = pm.eval(so, t_cur);
    vc1 = vc1 + (so.a+so_cur)/2.0*(t_cur-so.t0)/C1;
    if (event_in) begin 
      t0 = t_cur;
      yo0 = so_cur;
      si_at_t0 = si;
      vc0 = pm.eval(vc, t_cur);
      vc10 = pm.eval(vc1_pwl, t_cur);
      A = si*C1/(C2+C1);
      B = (vc0-vc10)/R;
      index = 0;
      expt = lut_exp.get_y(index);
    end

    if (index < (lut_exp.get_size()-1)) begin
      if (p1>0) dTr = lut_exp.get_dx(index)/p1;
      else dTr = TU;
      dT = time'(dTr/TU);
      dTr = dT*TU;
      expt = lut_exp.get_y(index+1);
      so_nxt = fn_lpf_pwl(t_cur-t0+dTr, si_at_t0, yo0 , vc10, vc0);
      so_slope = (so_nxt-so_cur)/dTr;
      so = pm.write(so_cur, so_slope, t_cur);
      index +=1;
    end
    vc1_nxt = vc1 + (2*so.a+so.b*dTr)/2.0*dTr/C1;
    vc1_pwl = pm.write(vc1, (vc1_nxt-vc1)/dTr, t_cur);

    ->> #(dT) wakeup;
  end
end

/*******************************************
  Response function, its 1st/2nd derivatives
*******************************************/

function real fn_lpf_pwl;
input real t; 
input real si; 
input real yo0  , vc1, vc;
begin
  //return A+(-A+B)*exp(-p1*t);
  return A+(-A+B)*expt;
end
endfunction

function real f2max_lpf_pwl;
input real t; 
input real si; 
input real yo0  , vc1, vc;
begin
  //return abs(-A+B)*(p1)**2*exp(-p1*t);
  return abs(-A+B)*(p1)**2*expt;
end
endfunction

/*************************************
  Caluating Tintv
*************************************/

function real calculate_Tintv_lpf_pwl;
input real etol, t; 
input real si; 
input real yo0  , vc1, vc;
real abs_f2max;
real calcT;
begin
  abs_f2max = f2max_lpf_pwl(t, si, yo0  , vc1, vc);
  calcT = sqrt(8.0*etol/abs_f2max);
  return max(TU,min(1.0,calcT));
  //return sqrt(8.0*etol/abs_f2max); 
end
endfunction

endmodule
