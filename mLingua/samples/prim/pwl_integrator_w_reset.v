/****************************************************************

Copyright (c) 2018- Stanford University. All rights reserved.

The information and source code contained herein is the 
property of Stanford University, and may not be disclosed or
reproduced in whole or in part without explicit written 
authorization from Stanford University. Contact bclim@stanford.edu for details.

* Filename   : pwl_integrator_w_reset.v
* Author     : Byongchan Lim (bclim@stanford.edu)
* Description: 
  - integrates a pwl signal. It does have a reset input unlike
    "pwl_integrator" cell
  - If 'modulo' > 0, a modulo operation is performed on the output, 
    which is a useful feature to realize an oscillator model in phase
    domain.
  - If one wants to use this for an oscillator model in phase domain,
    the output "trigger" will flip its value when the internal output
    exceeds "modulo" number (i.e. modulo operation)

* Note       :

* Revision   :
  - 7/26/2016: First release

****************************************************************/


module pwl_integrator_w_reset #(
  parameter real etol = 0.001, // error tolerance of PWL approximation
  parameter real vinit = 0,    // initial state value of the output
  parameter real modulo = 0,   // output % modulo for phase integrator application
  parameter en_filter = 1'b0,  // enable output filtering
  parameter real noise= 0      // modulo noise stddev
) (
  `input_real gain,     // scale the output by this amount
  `input_pwl  si,       // input to integrate
  `input_pwl reset_sig, // set the output to this value when reset is asserted
  input reset,          // reset the output with "reset_sig" value, active high.
                        // 'L' when unconnected.
  `output_pwl so,       // integrator output
  output reg trigger,   // flip this signal if output > modulo, then reset the output to output % modulo
  `output_real i_modulo
);

timeunit `DAVE_TIMEUNIT ;
timeprecision `DAVE_TIMEUNIT ;

`protect
//pragma protect 
//pragma protect begin
`get_timeunit // get timeunit in sec and assign it to the variable 'TU'
PWLMethod pm=new; // Method for PWL signal processing

pulldown(reset);

// wires
event  wakeup;  // event signal
pwl out;
//real i_modulo;
real t0;  // time offset
real t_cur;   // current time
real dTr1, dTr2;
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

real A, B, C;
real err;

int seed;
event dummy_event;
initial ->> dummy_event;
pwl reset_sig_d;

initial begin
  yo0 = vinit;
  out = pm.write(vinit,0,0);
  trigger = 1'b0;
  i_modulo = modulo;
end

assign so = out;

always @(`pwl_event(reset_sig) or reset) 
  if (reset) reset_sig_d = reset_sig;

always @(dummy_event or `pwl_event(si) or reset or `pwl_event(reset_sig_d)) begin 
  if (reset) begin
    yo0 = pm.eval(reset_sig_d, `get_time);
    out = reset_sig_d;
  end
  else begin
    t_cur = `get_time;
    out_cur = pm.eval(out, t_cur);
    yo0 = out_cur;
    t0 = t_cur;
    A = yo0;
    B = gain*si.a;
    C = gain*0.5*si.b;
    t_prev = $time;
    dT = 0;
    ->> wakeup;
  end
end

always @(wakeup) begin
  t0m = $time;
  dTm = t0m - t_prev;
  if (dT==dTm && ~reset) begin
    t_prev = $time;
    t_cur = `get_time; 
    out_cur = pm.eval(out, t_cur);
    if (((modulo>0.0) || (noise>0.0)) && (out_cur > i_modulo)) begin
      out_cur = out_cur - i_modulo;
      t0 = t_cur;
      yo0 = out_cur; A = yo0;
      B = gain*pm.eval(si, t_cur);
      C = gain*0.5*si.b;
      trigger = ~trigger;
      if (noise >0.0 && ~trigger)
        i_modulo = modulo + noise*`rdist_normal(seed, 10000);
      else
        i_modulo = modulo;
    end
    dTr1 = calculate_Tintv_filter_prime(etol, t_cur-t0);
    if (i_modulo > 0.0) begin
      if (out.b != 0.0) dTr2 = max(TU, (i_modulo-out_cur)/out.b);
      else dTr2 = TU;
      dTr = min(dTr1, dTr2);
    end
    else dTr = dTr1;

    dTr = min(`DT_MAX, dTr);

    dT = time'(dTr/TU);
    out_nxt = fn_pwl_integrator(t_cur-t0+dTr);
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
  Response function, its abs of 2nd derivatives
*******************************************/

function real fn_pwl_integrator;
input real t;
begin
  return A + B*t + C*t**2;
end
endfunction

function real f2max_pwl_integrator;
input real t; 
begin
  return abs(2.0*C);
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
  abs_f2max = f2max_pwl_integrator(t);
  calcT = sqrt(8.0*etol/abs_f2max);
  return max(TU,min(`DT_MAX,calcT));
end
endfunction

//pragma protect end
`endprotect

endmodule
