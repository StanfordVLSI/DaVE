/****************************************************************

Copyright (c) 2018- Stanford University. All rights reserved.

The information and source code contained herein is the 
property of Stanford University, and may not be disclosed or
reproduced in whole or in part without explicit written 
authorization from Stanford University. Contact bclim@stanford.edu for details.

* Filename   : channel_aug.v
* Author     : Byongchan Lim (bclim@stanford.edu)
* Description: 

* Note       :

* Revision   :
  - 7/26/2016: First release

****************************************************************/


module channel_aug #(
  parameter real etol = 0.005 // error tolerance of PWL approximation
) (
  `input_pwl si, `output_pwl so
);

`get_timeunit // get timeunit in sec and assign it to the variable 'TU'
// Method for PWL signal processing
PWLMethod pm=new;

// PWL accuracy-related parameters

// poles
parameter real p00 = 2186098000.0;
parameter real p10 = 6611181000.0;
parameter real p11 = 4153337000.0;
parameter real p20 = 14995460000.0;
parameter real p21 = 4002132000.0;
parameter real p30 = 23824920000.0;
parameter real p31 = 2252149000.0;

// wires
event  wakeup;  // event signal
real t0;  // time offset
real t_cur;   // current time
real dTr;
time dT=1;  // time interval of PWL waveform
time dTm;
time t_prev;
reg event_in=1'b0;

pwl si_at_t0;  // 
real so_cur0, so_cur1, so_cur2, so_cur3; // current output signal value
real so_cur;
real so_nxt0, so_nxt1, so_nxt2, so_nxt3;  // so at (t_cur+dT) for pwl output data
real yo00, yo01, yo02, yo03;  // output signal value offset (so_cur at t0)
real yo10, yo11, yo12, yo13;  
real xi0;
real so_slope0, so_slope1, so_slope2, so_slope3; // so slope
real so_slope;

pwl so0, so1, so2, so3;
event dummy_evt;
initial -> dummy_evt;

// you may need some additional wire definition here
real A00, A10, A20, A30;
real B00, B10, B11, B20, B21, B30, B31;
real C00, C10, C20, C30;

// @si_sensitivity is just "si" if it is piecewise constant waveform
// otheriwse, it is "si.t0 or si.s0 or si.slope"

always @(`pwl_event(si) or dummy_evt ) begin
  t_cur = `get_time;
  so_cur0 = pm.eval(so0, t_cur);
  so_cur1 = pm.eval(so1, t_cur);
  so_cur2 = pm.eval(so2, t_cur);
  so_cur3 = pm.eval(so3, t_cur);
  yo00 = so_cur0;
  yo01 = so_cur1;
  yo02 = so_cur2;
  yo03 = so_cur3;
  yo10 = fn1_ch0(t_cur-t0);
  yo11 = fn1_ch1(t_cur-t0);
  yo12 = fn1_ch2(t_cur-t0);
  yo13 = fn1_ch3(t_cur-t0);
  t0 = t_cur;
  xi0 = si.a;
  A00 = 1.80240227107842*si.a - 8.2448374733357e-10*si.b;
  B00 = (-1.80240227107842*si.a + 8.2448374733357e-10*si.b + yo00);
  C00 = 1.80240227107842*si.b;
  
  A10 = -0.98148061852243*si.a + 1.29458495601034e-10*si.b ;
  B10 = 0.577068025772112*si.a + 6.7128075721769e-11*si.b + 0.0395267653389009*xi0 + 0.628229207459303*yo01 + 1.51258905178969e-10*yo11;
  B11 = 0.98148061852243*si.a - 1.29458495601034e-10*si.b + 1.0*yo01;
  C10 = - 0.98148061852243*si.b ;
  
  A20 = -0.0106396333710409*si.a - 1.40055182023175e-11*si.b ;
  B20 = -0.227818471911998*si.a + 4.4474504913566e-12*si.b + 0.230658079178631*xi0 + 0.266889578579117*yo02 + 6.66868505534342e-11*yo12;
  B21 =  0.0106396333710408*si.a + 1.40055182023175e-11*si.b + 1.0*yo02;
  C20 = -0.0106396333710409*si.b ;
  
  A30 = 0.0262504692394047*si.a + 4.71836767066347e-14*si.b ;
  B30 = 0.00361562649330802*si.a - 1.10626746741294e-12*si.b - 0.00609706055676158*xi0 + 0.094529131682289*yo03 + 4.19728586706692e-11*yo13;
  B31 = -0.0262504692394047*si.a - 4.71836767066348e-14*si.b + 1.0*yo03;
  C30 = 0.0262504692394047*si.b ;

  t_prev = $realtime;
  dT = 0;
  ->> wakeup;
end

real so_cur_exact;
real err1, err2;

always @(wakeup) begin
  dTm = $realtime - t_prev;
  if (dT==dTm) begin
    t_cur = `get_time;
    t_prev = $realtime;
    so_cur0 = pm.eval(so0, t_cur);
    so_cur1 = pm.eval(so1, t_cur);
    so_cur2 = pm.eval(so2, t_cur);
    so_cur3 = pm.eval(so3, t_cur);
    so_cur = so_cur0 + so_cur1 + so_cur2 + so_cur3;
  
    dTr = calculate_dT_ch0(etol, t_cur-t0);
    so_nxt0 = fn_ch0(t_cur-t0+dTr);
    so_nxt1 = fn_ch1(t_cur-t0+dTr);
    so_nxt2 = fn_ch2(t_cur-t0+dTr);
    so_nxt3 = fn_ch3(t_cur-t0+dTr);
    so_slope0 = (so_nxt0-so_cur0)/dTr;
    so_slope1 = (so_nxt1-so_cur1)/dTr;
    so_slope2 = (so_nxt2-so_cur2)/dTr;
    so_slope3 = (so_nxt3-so_cur3)/dTr;
    so0 = pm.write(so_cur0, so_slope0, t_cur);
    so1 = pm.write(so_cur1, so_slope1, t_cur);
    so2 = pm.write(so_cur2, so_slope2, t_cur);
    so3 = pm.write(so_cur3, so_slope3, t_cur);
    so_slope = so0.b+so1.b+so2.b+so3.b;
    err1 = abs(so.b*dTr - so_slope*dTr);
    if ((err1 >= etol/4.0))
      so = pm.write(so_cur, so_slope, t_cur);
    dT = time'(dTr/TU);

    ->> #(dT) wakeup;
  end
end

/*******************************************
  Response function, its 1st/2nd derivatives
*******************************************/

function real fn_ch0;
input real t; 
begin
  return A00 + C00*t + B00*exp(-p00*t) ;
end
endfunction

function real fn_ch1;
input real t; 
begin
  return A10 + C10*t + (B10*sin(p10*t) + B11*cos(p10*t))*exp(-p11*t) ;
end
endfunction

function real fn_ch2;
input real t; 
begin
  return A20 + C20*t + (B20*sin(p20*t) + B21*cos(p20*t))*exp(-p21*t) ;
end
endfunction

function real fn_ch3;
input real t; 
begin
  return A30 + C30*t + (B30*sin(p30*t) + B31*cos(p30*t))*exp(-p31*t);
end
endfunction

function real fn1_ch0;
input real t; 
begin
  return C00 + B00*(-p00)*exp(-p00*t) ;
end
endfunction

function real fn1_ch1;
input real t; 
begin
  return C10 + ((-p10*B11-p11*B10)*sin(p10*t)+ (p10*B10-p11*B11)*cos(p10*t))*exp(-p11*t) ;
end
endfunction

function real fn1_ch2;
input real t; 
begin
  return C20 + ((-p20*B21-p21*B20)*sin(p20*t)+ (p20*B20-p21*B21)*cos(p20*t))*exp(-p21*t) ;
end
endfunction

function real fn1_ch3;
input real t; 
begin
  return C30 + ((-p30*B31-p31*B30)*sin(p30*t)+ (p30*B30-p31*B31)*cos(p30*t))*exp(-p31*t) ;
end
endfunction


function real f2max_ch0;
input real t; 
begin
  return abs(B00)*(p00)**2*exp(-p00*t);
end
endfunction

function real f2max_ch1;
input real t; 
begin
  return sqrt(abs(B10)**2 + abs(B11)**2)*(p10**2 + 2*p10*p11 + p11**2)*exp(-p11*t);
end
endfunction

function real f2max_ch2;
input real t; 
begin
  return sqrt(abs(B20)**2 + abs(B21)**2)*(p20**2 + 2*p20*p21 + p21**2)*exp(-p21*t);
end
endfunction

function real f2max_ch3;
input real t; 
begin
  return sqrt(abs(B30)**2 + abs(B31)**2)*(p30**2 + 2*p30*p31 + p31**2)*exp(-p31*t);
end
endfunction

function real calculate_dT_ch0;
input real etol; 
input real t;
real abs_f2max;
real calcT;
begin
  abs_f2max = max(max(f2max_ch0(t),f2max_ch1(t)),max(f2max_ch2(t),f2max_ch3(t)));
  calcT = sqrt(8.0*etol/abs_f2max);
  return max(TU,min(1.0,calcT));
end
endfunction

endmodule
