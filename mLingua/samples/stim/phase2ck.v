/****************************************************************

Copyright (c) 2018- Stanford University. All rights reserved.

The information and source code contained herein is the 
property of Stanford University, and may not be disclosed or
reproduced in whole or in part without explicit written 
authorization from Stanford University. Contact bclim@stanford.edu for details.

* Filename   : phase2ck.v
* Author     : Byongchan Lim (bclim@stanford.edu)
* Description: It converts a phase to a digital clock with 50% duty cycle.

* Note       :

* Revision   :
  - 7/26/2016: First release

****************************************************************/

`timescale `DAVE_TIMEUNIT / `DAVE_TIMEUNIT

////////////
`ifndef AMS // NOT AMS
////////////

module phase2ck #(
  parameter real freq = 1.0 // frequency
) (
  `input_real phin, // phase input
  output reg ckout  // digital clock output
);

`get_timeunit

real phin_by_M_PI; // phin normalized by 2*pi
real ph0; // accumultaed phase
real t0, t1;  // time stamps
real ph_transition; // constant to define when ckout flips
real half_delay;  // half delay for timer
real phin_prev;
event evt;

// some initialization
initial begin
  ph0 = 0.0;
  phin_prev = 0.0;
  ph_transition = 0.5;
  ckout = 1'b0;
  #1 -> evt;
end

// this code is adopted from ringosc.v for PLL monte-carlo simulation
always @(phin or evt) begin
  phin_by_M_PI = phin/`M_PI; // normalize phin by pi
  t1 = `get_time;
  ph0 = ph0 + freq*(t1-t0) - (phin_by_M_PI - phin_prev)*ph_transition ; // accumulate phase
  if (ph0 > ph_transition) begin  // flip clock if phase exceed some degree (e.g., 180 if ph_transition=0.5)
    ckout = ~ckout;
    ph0 = ph0 - ph_transition ;
  end
  half_delay = (ph_transition-ph0)/(freq/ph_transition);
  half_delay = max(half_delay, TU);
  ->> `delay(half_delay) evt;
  t0 = t1;
  phin_prev = phin_by_M_PI;
end

endmodule


////////////
`else // AMS
////////////


module phase2ck #(
  parameter freq = 1.0 // clock frequency
) (
  input wreal phin, // phase input
  output reg ckout  // digital clock output
);

`get_timeunit

reg timer_clk;  // timer for detecting phase exceed first or ckout transition first
real phin_by_M_PI; // phin normalized by 2*pi
real ph0; // accumultaed phase
real t0, t1;  // time stamps
real ph_transition; // constant to define when ckout flips
real half_delay;  // half delay for timer
real phin_prev;

// some initialization
initial begin
  ph0 = 0.0;
  phin_prev = 0.0;
  ph_transition = 0.5;
  ckout = 1'b0;
  timer_clk = 1'b0;
  #1 timer_clk = 1'b0;
end

// normalize phin by pi
always @(phin) phin_by_M_PI = phin/`M_PI;

// this code is adopted from ringosc.v for PLL monte-carlo simulation
always @(phin_by_M_PI or timer_clk) begin
  t1 = `get_time;
  ph0 = ph0 + freq*(t1-t0) - (phin_by_M_PI - phin_prev)*ph_transition ; // accumulate phase
  if (ph0 > ph_transition) begin  // flip clock if phase exceed some degree (e.g., 180 if ph_transition=0.5)
    ckout = ~ckout;
    ph0 = ph0 - ph_transition ;
  end
  half_delay = $rtoi((ph_transition-ph0)/(freq/ph_transition)/TU);
  if (half_delay < 1.0) // in case half_delay goes negative at the initial start-up
    half_delay = 1.0;
  timer_clk <= #(half_delay) ~timer_clk;  // schedule a timer_clk flip
  t0 = t1;
  phin_prev = phin_by_M_PI;
end

endmodule


////////////
`endif
////////////
