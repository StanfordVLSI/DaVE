/****************************************************************

Copyright (c) 2018- Stanford University. All rights reserved.

The information and source code contained herein is the 
property of Stanford University, and may not be disclosed or
reproduced in whole or in part without explicit written 
authorization from Stanford University. Contact bclim@stanford.edu for details.

* Filename   : pwl_cos.v
* Author     : Byongchan Lim (bclim@stanford.edu)
* Description: 
  - This outputs a cosine waveform in pwl.

* Note       :

* Revision   :
  - 7/26/2016: First release

****************************************************************/


module pwl_cos #(
  parameter real etol = 0.0001, // error tolerance of PWL approximation
  parameter real freq = 100e6,  // frequency
  parameter real amp  = 0.01,   // amplitude
  parameter real offset = 0.01, // DC offset
  parameter real ph   = 0.0     // initial phase in degree
) (
  `output_pwl out    // cosine output in pwl
);

timeunit `DAVE_TIMEUNIT ;
timeprecision `DAVE_TIMEUNIT ;

`protect
//pragma protect 
//pragma protect begin

`get_timeunit // get timeunit in sec and assign it to the variable 'TU'
PWLMethod pm=new;

// DPI-C function if needed (only takes an input and produces a real output)
import "DPI-C" pure function real cos(input real x);

// wires
event  wakeup;  // event signal
real phase;
real dPhase;
real dTr;  // time interval of PWL waveform
real t_cur;   // current time
real out_cur; // current output signal value
real out_nxt;  // out at (t_cur+dT) for pwl output data
time dT;


real out_slope; // out slope

// you may need outme additional wire definition here
initial begin
  phase = ph/180*`M_PI;
  dPhase = 0.0;
  ->> wakeup;
end

always @(wakeup) begin
  t_cur = `get_time;
  phase = phase + dPhase;
  if (phase >= 2*`M_PI) phase = phase - 2*`M_PI;
  out_cur = fn_pwl_cos(phase);
  dTr = calculate_Tintv_pwl_cos(etol, phase);
  dPhase = 2*`M_PI*freq*dTr;
  out_nxt = fn_pwl_cos(phase+dPhase);
  out_slope = (out_nxt-out_cur)/dTr;
  out = pm.write(out_cur, out_slope, t_cur);
  dT = time'(dTr/TU);
  ->> #(dT) wakeup;
end

/*******************************************
  Response function, its 1st/2nd derivatives
*******************************************/

function real fn_pwl_cos;
input real phase;
begin
  return offset + amp*cos(phase);
end
endfunction

function real f2max_pwl_cos;
input real phase;
begin
  return abs(amp*(2*`M_PI*freq)**2);
end
endfunction

/*************************************
  Caluating Tintv
*************************************/

function real calculate_Tintv_pwl_cos;
input real etol, phase; 
real abs_f2max;
real calcT;
begin
  abs_f2max = f2max_pwl_cos(phase);
  calcT = sqrt(8.0*etol/abs_f2max); 
  return min(`DT_MAX,max(TU,min(1.0,calcT)));
end
endfunction

//pragma protect end
`endprotect

endmodule
