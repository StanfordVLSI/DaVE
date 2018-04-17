/****************************************************************

Copyright (c) 2018- Stanford University. All rights reserved.

The information and source code contained herein is the 
property of Stanford University, and may not be disclosed or
reproduced in whole or in part without explicit written 
authorization from Stanford University. Contact bclim@stanford.edu for details.

* Filename   : detect_ss.v
* Author     : Byongchan Lim (bclim@stanford.edu)
* Description: It detects if "in" signal is in steady-state. If
  it is, it asserts "detect" signal to 'H'.

* Note       :

* Revision   :
  - 7/26/2016: First release
  - 12/18/2016: Bug fix) Once a steady-state is detected, in0 should
      remain the same as a reference level for the filtering. But, 
      the old code continued to sample "in1" to "in0".

****************************************************************/

`timescale `DAVE_TIMEUNIT / `DAVE_TIMEUNIT

///////////
`ifndef AMS // NOT AMS
///////////


module detect_ss #(
  parameter real ts = 0.0,      // start time 
  parameter real ti = 0.0,      // time interval to check
  parameter real tol= 0.001,     // tolerance
  parameter integer no_buff = 4 // number of buffer for filtering
) ( `input_pwl in, output detect );

`get_timeunit
PWLMethod pm=new;

event wakeup;
real in0, in1;

reg [no_buff-1:0] buffer='0;

assign detect = &buffer;

initial begin
  `delay(ts);
  forever begin
    `delay(ti);
    -> wakeup;
  end
end

/*
always @(`pwl_event(in)) begin
  in1 = pm.eval(in, `get_time);
  if (!is_steady(in1,in0)) buffer=2'b0;
  in0 = in1;
end
*/
initial in0 = pm.eval(in, `get_time);

always @(wakeup) begin
  in1 = pm.eval(in, `get_time);
  buffer[no_buff-1:1] = buffer[no_buff-2:0];
  buffer[0] = is_steady(in1,in0);
  if (~buffer[0]) in0 = in1;  // if not steady-state, update reference value
  //in0 = in1;
end

function real is_steady;
input real in_new;
input real in_old;
begin
  return abs(in_new-in_old)>tol? 1'b0: 1'b1;
end
endfunction

endmodule


///////////
`else // AMS
///////////


`include "disciplines.vams"

module detect_ss ( input in, output detect );

electrical in;

parameter is_pwl=1'b1;  // dummy for va(ms)
parameter real ts = 0.0;      // start time 
parameter real ti = 0.0;      // interval to check
parameter real tol= 0.001;     // tolerance
parameter integer no_buff = 4; // number of buffer for filtering

`get_timeunit
event sample;
real in0, in1;

reg [no_buff-1:0] buffer=0;
assign detect = &buffer;

initial begin
  #(ts/TU);
  forever begin
    #(ti/TU);
    -> sample;
  end
end

initial in0 = V(in);

always @(sample) begin
  in1 = V(in);
  buffer[no_buff-1:1] = buffer[no_buff-2:0];
  buffer[0] = is_steady(in1,in0);
  if (~buffer[0]) in0 = in1;  // if not steady-state, update reference value
  //in0 = in1;
end

function real is_steady;
input real in_new;
input real in_old;
begin
  if (abs(in_new-in_old)>tol) is_steady=1'b0;
  else is_steady=1'b1;
end
endfunction

endmodule


///////////
`endif
///////////
