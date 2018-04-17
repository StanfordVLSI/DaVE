/************************************************
  Module: phase frequency detector
  Model discrepancy: two clock inputs are swapped
************************************************/

module pfd (
  `input_pwl vdd, vss,  // modeling for propagation delay
  input rstb,           // reset, active low
  input ckref, ckfb,    // two clock inputs
  output reg up, dn     // up and down signal pulses
);

timeunit 1fs;
timeprecision 1fs;
`get_timeunit
PWLMethod pm=new;

real tpd; // average propagation delay of input clocks
real tos; // static phase offset
real rst_pw; // self-reset pulse width

real lut_tpd[1:0];   // coef of delay vs vdd
real lut_tos;  // static phase offset
real lut_pw[1:0];   // reset pulse width vs vdd

reg i_ckref, i_ckfb; // delayed input clocks for modeling propagation delay
wire reset = (up & dn);

// LUT
initial begin
  lut_tpd[0] = 29.0e-12 ;
  lut_tpd[1] = -14.8e-12 ;
  lut_tos = 0.0 ;
  lut_pw[0] = 141.0e-12 ;
  lut_pw[1] = -78.0e-12 ;
end

initial up = 0;
initial dn = 0;

// parameter calculation
event wakeup;
real vdd_r;
initial -> wakeup;
always @(`pwl_event(vdd) or wakeup) begin
  vdd_r = pm.eval(vdd,`get_time);
  tpd = lut_tpd[0] + lut_tpd[1]*vdd_r ;
  tos = lut_tos; 
  rst_pw = lut_pw[0] + lut_pw[1]*vdd_r ;
end

// delay inputs
always @(ckref) i_ckref = #((tpd+tos)/TU) ckref;
always @(ckfb) i_ckfb = #((tpd)/TU) ckfb;


// actual PFD operation
always @(posedge i_ckfb or posedge reset or negedge rstb)
  if (reset || !rstb) #(rst_pw/TU) up <= 0;
  else up <= 1'b1;

always @(posedge i_ckref or posedge reset or negedge rstb)
  if (reset || !rstb) #(rst_pw/TU) dn <= 0;
  else dn <= 1'b1;

endmodule
