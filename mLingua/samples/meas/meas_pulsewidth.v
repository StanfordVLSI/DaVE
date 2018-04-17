/****************************************************************

Copyright (c) 2018- Stanford University. All rights reserved.

The information and source code contained herein is the 
property of Stanford University, and may not be disclosed or
reproduced in whole or in part without explicit written 
authorization from Stanford University. Contact bclim@stanford.edu for details.

* Filename   : meas_pulsewidth.v
* Author     : Byongchan Lim (bclim@stanford.edu)
* Description: It measures a pulse width.

* Note       :
  - "vdd" input and "vlth" parameter are valid only for Verilog-AMS.

* Revision   :
  - 7/26/2016: First release

****************************************************************/

`timescale `DAVE_TIMEUNIT / `DAVE_TIMEUNIT

///////////
`ifndef AMS // NOT AMS
///////////


module meas_pulsewidth #(
  parameter dir = 1,  // '1' if measuring high pulse width, '0'  for measureing  low pulse width
  parameter real vlth = 0.5, // logic threshold in proportion to vdd
                             // valid only for Verilog-AMS
  parameter real tstart=0.0 // measurement starts after time "tstart"
) (
  input in, 
  `input_pwl vdd, 
  `output_pwl pw
);

`get_timeunit
PWLMethod pm=new;

wire i_in;
real ts=0.0;
real t0;
reg triggered=1'b0;

assign i_in = dir? in : ~in;

always @(posedge i_in) begin
  triggered <= 1'b1;
  t0 = `get_time;
  if(t0 >= tstart) ts = t0;
end
always @(negedge i_in) begin
  t0 = `get_time;
  if(t0 >= tstart && triggered) pw = pm.write(t0-ts,0.0,0.0);
end

endmodule


///////////
`else // AMS
///////////


`include "disciplines.vams"

module meas_pulsewidth #(
  parameter dir = 1'b1, // '1' if measuring highpulse width, '0'  for measureing  lowpulse width
  parameter real vlth = 0.5, // logic threshold in proportion to vdd
  parameter real tstart=0.0 // measurement starts after this
) (in, vdd, pw);

input in;
input vdd;
output pw;
electrical in, vdd, pw;

reg i_in;
reg d_in;
real ts = 0.0;
real r_pw = 0.0;
reg triggered=1'b0;

always @(cross(V(in)-V(vdd)*vlth, +1)) d_in = dir? 1'b1 : 1'b0;
always @(cross(V(in)-V(vdd)*vlth, -1)) d_in = dir? 1'b0 : 1'b1;

always @(posedge d_in) begin
  triggered <= 1'b1;
  if ($abstime >= tstart) ts = $abstime;
end
always @(negedge d_in) begin
  if ($abstime >= tstart && triggered) r_pw = $abstime - ts;
end

analog begin
  V(pw) <+ r_pw;
end

endmodule


///////////
`endif
///////////

