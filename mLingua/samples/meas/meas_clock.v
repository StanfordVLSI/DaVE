/****************************************************************

Copyright (c) 2018- Stanford University. All rights reserved.

The information and source code contained herein is the 
property of Stanford University, and may not be disclosed or
reproduced in whole or in part without explicit written 
authorization from Stanford University. Contact bclim@stanford.edu for details.

* Filename   : meas_clock.v
* Author     : Byongchan Lim (bclim@stanford.edu)
* Description: It measures properties of a clock signal such as
  frequency, duty-cycle, etc.

* Note       :

* Revision   :
  - 7/26/2016: First release

****************************************************************/

`timescale `DAVE_TIMEUNIT / `DAVE_TIMEUNIT

///////////
`ifndef AMS // NOT AMS
///////////


module meas_clock #(
  parameter dir = 1'b1, // invert clk if dir = 1'b0
  parameter real vlth = 0.5, // logic threshold in proportion to vdd, 
                             // valid only for Verilog-AMS
  parameter real tstart=0.0  // measurement starts after time "tstart"
) (
  input clk, `input_pwl vdd,
  `output_pwl frequency, period, dutycycle );

`get_timeunit
PWLMethod pm=new;

real t_pos, t_pos0, t_neg;
wire clk_int;

assign clk_int = dir? clk : ~clk;

always @(posedge clk_int) begin
	t_pos = `get_time;
	if ((t_pos0 > 0.0) && (t_pos >= tstart) && (t_pos != t_pos0))
		frequency = pm.write(1.0/(t_pos - t_pos0),0.0,0.0);
	period = pm.write(1.0/frequency.a,0.0,0.0);
	dutycycle = pm.write((t_neg-t_pos0)/period.a,0.0,0.0);
	t_pos0 = t_pos;
end

always @(negedge clk_int) t_neg = `get_time;

endmodule


///////////
`else // AMS
///////////


`include "disciplines.vams"

module meas_clock #(
  parameter dir = 1'b1, // invert clk if dir = 1'b0
  parameter real vlth = 0.5, // logic threshold in proportion to vdd
  parameter real tstart=0.0 // measurement starts after this
) (
  input clk,
  input vdd,
  output frequency, period, dutycycle);

electrical clk;
electrical vdd;
electrical frequency, period, dutycycle;

real t_pos0, t_pos, t_neg, rfreq, rperiod, rdutycycle;
reg clk_int;

analog begin
  V(frequency) <+ rfreq;
  V(period) <+ rperiod;
  V(dutycycle) <+ rdutycycle;
end

//initial rfreq = 1000e9;
initial rfreq = 1;

always @(cross(V(clk)-V(vdd)*vlth,+1)) clk_int = dir? 1'b1:1'b0;
always @(cross(V(clk)-V(vdd)*vlth,-1)) clk_int = dir? 1'b0:1'b1;

always @(posedge clk_int) begin
	t_pos = $abstime;
	if (t_pos0 > 0.0 && t_pos >= tstart) rfreq = 1.0/(t_pos - t_pos0);
	rperiod = 1.0/rfreq;
	rdutycycle = (t_neg-t_pos0)/rperiod;
	t_pos0 = t_pos;
end

always @(negedge clk_int) t_neg = $abstime;

endmodule


///////////
`endif
///////////
