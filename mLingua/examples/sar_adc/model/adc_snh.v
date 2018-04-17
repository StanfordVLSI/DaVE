/****************************************************************

Copyright (c) 2018- Stanford University. All rights reserved.

The information and source code contained herein is the 
property of Stanford University, and may not be disclosed or
reproduced in whole or in part without explicit written 
authorization from Stanford University. Contact bclim@stanford.edu for details.

* Filename   : adc_snh.v
* Author     : Byongchan Lim (bclim@stanford.edu)
* Description: ADC sample-and-hold input stage

* Note       :

* Revision   :
  - 7/26/2016: First release

****************************************************************/


module adc_snh #(
  parameter real Rsnh = `R_SNH,
  parameter real Cdac = `C_DAC,
  parameter real etol = `ETOL_SNH,    // error tolerance of PWL approximation
  parameter real epsPed = `EPSPED,  // signal-dependent pedestal error
  parameter real VosPed = `VOSPED, // signal-independent pedestal error
  parameter real tdPed  = `TDPED  // pedestal delay
) (
  input sample, // adc snh sampling clock
  input cs_trigger, // charge sharing trigger signal
  input rst,        // reset output
  `input_pwl vdd,     // power supply voltage
  `input_pwl vss,     // ground
  `input_pwl vi,      // input voltage
  `input_pwl vrst,     // reset voltage
  `output_pwl vo   // sampled voltage
);

`get_timeunit // get timeunit in sec and assign it to the variable 'TU'
PWLMethod pm=new; // Method for PWL signal processing

pulldown (cs_trigger);
pulldown (rst);

// wires
real vo0, vo1;  
real pole;  // pole frequency depending on mode
event wakeup;  // event signal
event pedwakeup;  // event signal for pedestal error update
real t0;  // time offset
real t_cur;   // current time
real dTr;  // time interval of PWL waveform
time dT=1;
time dTm;
time t_prev;

pwl si;  // 
real so_cur; // current output signal value
real so_prev; // previous output signal value
real so_nxt;  // so at (t_cur+dT) for pwl output data
real yo0;  // output signal value offset (so_cur at t0)

real so_slope; // so slope
real A, B, C;

wire cs_trigger_d;
assign pole = 1/Rsnh/Cdac;
assign #1 cs_trigger_d = cs_trigger;   // for charge sharing 

// update target reset value
always @(sample or `pwl_event(vi)) begin
  if (sample & ~rst) begin
    si = vi;
    dT = 0;
    t_prev = $realtime;
    ->> wakeup;
  end
end

// update target reset value
always @(rst or `pwl_event(vrst)) begin
  if (rst & ~sample) begin
    si = vrst;
    dT = 0;
    t_prev = $realtime;
    ->> wakeup;
  end
end

always @(`pwl_event(si)) begin
  t_cur = `get_time;
  so_cur = pm.eval(vo, t_cur);
  yo0 = so_cur;
  t0 = t_cur;
  A = si.a - si.b/pole;
  B = -si.a + si.b/pole + yo0;
  C = si.b;
  dT = 0;
  t_prev = $realtime;
  ->> wakeup;
end

// hold mode with pedestal error
always @(negedge sample or negedge rst) begin 
  vo0 = pm.eval(vo, `get_time);
  vo1 = vo0*(1+epsPed) + VosPed;
  vo = pm.write(vo0, (vo1-vo0)/tdPed, `get_time);
  ->> `delay(tdPed) pedwakeup;
end
always @(pedwakeup) // settle in hold mode after pedestal error transition
  vo = pm.write(vo1, 0.0, `get_time+tdPed);

always @(posedge cs_trigger_d) begin
  yo0 = pm.eval(vi, `get_time);
  vo  = pm.write(yo0, 0, `get_time);
end

// event control and update signal in reset mode & transmission mode
always @(wakeup) begin
  if (sample || rst) begin // track mode
    dTm = $realtime - t_prev;
    if (dT==dTm) begin
      t_prev = $realtime;
      t_cur = `get_time;
      so_cur = pm.eval(vo, t_cur);
      
      dTr = calculate_Tintv_spf(etol, t_cur-t0);
      so_nxt = fn_spf(t_cur-t0+dTr);
      so_slope = (so_nxt-so_cur)/dTr;
      vo = pm.write(so_cur, so_slope, t_cur);
      if (so_slope != 0) begin
        dT = time'(dTr/TU);
        ->> #(dT) wakeup;
      end
    end
  end
end

/*******************************************
  Response function, its 1st/2nd derivatives
*******************************************/

function real fn_spf;
input real t; 
begin
  return A + B*exp(-pole*t) + C*t;
end
endfunction

function real f2max_spf;
input real t; 
begin
  return abs(B)*pole**2*exp(-pole*t);
end
endfunction

/*************************************
  Caluating Tintv
*************************************/

function real calculate_Tintv_spf;
input real etol, t; 
real abs_f2max;
real calcT;
begin
  abs_f2max = f2max_spf(t);
  calcT = sqrt(8.0*etol/abs_f2max);
  return max(TU,min(1.0,calcT));

end
endfunction

endmodule
