/****************************************************************

Copyright (c) 2018- Stanford University. All rights reserved.

The information and source code contained herein is the 
property of Stanford University, and may not be disclosed or
reproduced in whole or in part without explicit written 
authorization from Stanford University. Contact bclim@stanford.edu for details.

* Filename   : pwl_filter_pfe.v
* Author     : Byongchan Lim (bclim@stanford.edu)
* Description: 
  - A linear filter primitive cell. 
    Wehn A and/or B are complex numbers, the transfer function is 
    TF(s) = A/(s+B) + (A*)/(s+B*) where  A* = conj(A), B* = conj(B)
  - When both A and B are real, the computed TF(s) = A/(s+B).

* Note       :
  - If "in" should be a "real" signal, a trick is to change it to a pwl
    signal with zero slope.

* Revision   :
  - 00/00/00 : First release

****************************************************************/


module pwl_filter_pfe #(
  parameter real etol = 0.001,      // error tolerance of PWL approximation
  parameter logic en_filter = 1'b0  // enable output event filtering
) (
  input complex A,  // coef A
  input complex B,  // coef B
  `input_pwl in,    // filter signal input 
  `output_pwl out   // filter output
);

timeunit `DAVE_TIMEUNIT ;
timeprecision `DAVE_TIMEUNIT ;


`protect
//pragma protect 
//pragma protect begin
`get_timeunit // get timeunit in sec and assign it to the variable 'TU'
PWLMethod pm=new; // Method for PWL signal processing
CMath cm=new; // Method for complex numbers

// wires
event  wakeup;  // event signal
real t0;  // time offset
real t_cur;   // current time
real dTr;  // time interval of PWL waveform
time dT=1;
time dTm=0;
time t_prev;
time t0m;

pwl yo1_r, yo2_r;
pwl yo1_i, yo2_i;
complex yo10, yo20;

complex out_cur1; // current output signal value
complex out_cur2; // current output signal value
complex out_nxt1;  // out at (t_cur+dT) for pwl output data
complex out_nxt2;  // out at (t_cur+dT) for pwl output data
complex out_slope1, out_slope2;
complex _tmp1, _tmp2;
real out_slope; // out slope
real out_cur;
real err;
event dummy_event;
logic en_complex=0;

complex Ac, Bc;
complex inb_c, ina_c, y0_c;

initial -> dummy_event;

always @(A.r or A.i or B.r or B.i or dummy_event) begin
  if (A.i != 0 || B.i !=0) en_complex = 1'b1;
  else en_complex = 1'b0;
end

always @(`pwl_event(in)) begin
  if (en_complex) Ac = cm.conj(A);
  if (en_complex) Bc = cm.conj(B);
  inb_c = cm.to_c(in.b);
  ina_c = cm.to_c(in.a);
  t_cur = `get_time;
  if ($time == 0) begin
    _tmp1 = fn_compute_out0(A,B);
    _tmp2 = fn_compute_out0(Ac,Bc);
    yo1_r = pm.write(_tmp1.r,0.0,t_cur); 
    yo1_i = pm.write(_tmp1.i,0.0,t_cur); 
    if (en_complex) yo2_r = pm.write(_tmp2.r,0.0,t_cur); 
    if (en_complex) yo2_i = pm.write(_tmp2.i,0.0,t_cur); 
    out = pm.write(yo1_r.a+yo2_r.a,0.0,t_cur);
  end
  yo10 = '{pm.eval(yo1_r,t_cur), pm.eval(yo1_i, t_cur)};
  if (en_complex) yo20 = '{pm.eval(yo2_r,t_cur), pm.eval(yo2_i, t_cur)};
  t0 = t_cur;
  t_prev = $time;
  dT = 0;
  if ($time != 0) ->> wakeup;
end

always @(wakeup) begin
  t0m = $time;
  dTm = t0m - t_prev;
  if (dT==dTm) begin
    t_prev = $time;
    t_cur = `get_time;
    out_cur1 = '{pm.eval(yo1_r, t_cur), pm.eval(yo1_i, t_cur)};
    out_cur2 = '{pm.eval(yo2_r, t_cur), pm.eval(yo2_i, t_cur)};
    dTr = compute_dt(etol, t_cur-t0, yo10, yo20); //dTr = TU;
    dT = max(1, time'(dTr/TU));
    dTr = dT*TU;
    out_nxt1 = compute_fn(t_cur-t0+dTr, A, B, yo10);
    if (en_complex) out_nxt2 = compute_fn(t_cur-t0+dTr, Ac, Bc, yo20);
    out_slope1 = '{(out_nxt1.r - out_cur1.r)/dTr, (out_nxt1.i-out_cur1.i)/dTr};
    if (en_complex) out_slope2 = '{(out_nxt2.r - out_cur2.r)/dTr, (out_nxt2.i-out_cur2.i)/dTr};
    out_slope = cm.re(cm.add(out_slope1,out_slope2));
    out_cur = cm.re(cm.add(out_cur1,out_cur2));
    yo1_r = pm.write(out_cur1.r,out_slope1.r,t_cur);
    yo1_i = pm.write(out_cur1.i,out_slope1.i,t_cur);
    if (en_complex) yo2_r = pm.write(out_cur2.r,out_slope2.r,t_cur);
    if (en_complex) yo2_i = pm.write(out_cur2.i,out_slope2.i,t_cur);
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

function complex fn_compute_out0;
input complex C, D;
begin
  return cm.sub(cm.mult(cm.div(C,D),ina_c),cm.div(cm.mult(C,inb_c),cm.mult(D,D))); // C*(D*ina - inb)/D**2
end
endfunction

function complex compute_fn;
input real t; 
input complex C, D, yo0;
complex te1, te2, te3;
complex _e1, _e2;
complex term;
complex t_c;
begin
  t_c = cm.to_c(t);
  _e1 = cm.cexp(cm.scale(cm.mult(D,t_c),-1));
  _e2 = cm.div(cm.sub(cm.add(cm.mult(cm.mult(D,D),yo0),cm.mult(C,inb_c)),cm.mult(cm.mult(C,D),ina_c)),cm.mult(D,D)); // (-C*D*ina + C*inb + D**2*y0)/D**2
  te1 = cm.mult(cm.div(C,D),cm.to_c(in.b*t)); // C*inb*t/D
  te2 = cm.sub(cm.mult(cm.div(C,D),ina_c),cm.div(cm.mult(C,inb_c),cm.mult(D,D))); // C*(D*ina - inb)/D**2
  te3 = cm.mult(_e1,_e2); // (-C*D*ina + C*inb + D**2*y0)*exp(-D*t)/D**2
  term = cm.add(cm.add(te1,te2),te3);
  return term;
end
endfunction

function real compute_f2max;
input real t; 
input complex y10, y20;
complex term1, term2, term;
real f21, f22;
complex t_c, _e1, _e2;
begin
  t_c = cm.to_c(t);
  _e1 = cm.cexp(cm.scale(cm.mult(B,t_c),-1));
  _e2 = cm.cexp(cm.scale(cm.mult(Bc,t_c),-1));
  //term1 = cm.mult(cm.sub(cm.add(cm.mult(cm.mult(B,B),y10),cm.mult(A,inb_c)),cm.mult(cm.mult(A,B),ina_c)),_e1); // (-A*B*ina + A*inb + B**2*y0)*exp(-B*t)
  //term2 = cm.mult(cm.sub(cm.add(cm.mult(cm.mult(Bc,Bc),y20),cm.mult(Ac,inb_c)),cm.mult(cm.mult(Ac,Bc),ina_c)),_e2); // (-Ac*Bc*ina + Ac*inb + Bc**2*y0)*exp(-Bc*t)
  // return (cm.abs(term1)+cm.abs(term2));
  //f21 = (cm.abs(cm.mult(cm.mult(B,B),y10))+cm.abs(cm.mult(A,inb_c))+cm.abs(cm.mult(cm.mult(A,B),ina_c)))*exp(-B.r*t);
  //f22 = (cm.abs(cm.mult(cm.mult(Bc,Bc),y20))+cm.abs(cm.mult(Ac,inb_c))+cm.abs(cm.mult(cm.mult(Ac,Bc),ina_c)))*exp(-Bc.r*t);
  if (en_complex) begin
    f21 = (abs(cm.abs(B)*cm.abs(B)*cm.abs(y10))+abs(cm.abs(A)*in.b)+abs(cm.abs(A)*cm.abs(B)*in.a))*exp(-B.r*t);
    f22 = (abs(cm.abs(Bc)*cm.abs(Bc)*cm.abs(y20))+abs(cm.abs(Ac)*in.b)+abs(cm.abs(Ac)*cm.abs(Bc)*in.a))*exp(-Bc.r*t);
  end
  else begin
    f21 = cm.abs(cm.sub(cm.add(cm.mult(cm.mult(B,B),y10),cm.mult(A,inb_c)),cm.mult(cm.mult(A,B),ina_c)))*exp(-B.r*t); // (-A*B*ina + A*inb + B**2*y0)*exp(-B*t)
    f22 = 0.0;
  end
  return abs(f21 + f22);
end
endfunction

/*************************************
  Caluating Tintv
*************************************/

function real compute_dt;
input real etol, t; 
input complex y10, y20;
real abs_f2max;
real calcT;
begin
  abs_f2max = compute_f2max(t,y10,y20);
  calcT = sqrt(8.0*etol/abs_f2max);
  return min(`DT_MAX,max(TU,min(1.0,calcT)));
end
endfunction

//pragma protect end
`endprotect

endmodule
