/****************************************************************

Copyright (c) 2018- Stanford University. All rights reserved.

The information and source code contained herein is the 
property of Stanford University, and may not be disclosed or
reproduced in whole or in part without explicit written 
authorization from Stanford University. Contact bclim@stanford.edu for details.

* Filename   : ck2phase.v
* Author     : Byongchan Lim (bclim@stanford.edu)
* Description: Convert a digital clock signal to a phase.

* Note       :

* Revision   :
  - 7/26/2016: First release

****************************************************************/

`timescale `DAVE_TIMEUNIT / `DAVE_TIMEUNIT

///////////
`ifndef AMS // NOT AMS
///////////


module ck2phase (
  input ckin,
  `input_pwl vdd,
  `output_pwl phout);

`get_timeunit
PWLMethod pm=new;

parameter freq = 1.0; // clock frequency
parameter dir = 1'b1;  // '1': check posedge of ckin, '0': check negedge of ckin
parameter vth = 0;  // dummy for sverilog

real UI_abs, UI_diff, UI_out;
wire ckin_int;

integer i;  // check this is the first rising edge
initial i = 0;

assign ckin_int = dir? ckin : ~ckin; 


always @(posedge ckin_int) begin
  if (i == 0) begin // initialize UI_out with the first rising edge of ckin_int
    i = 1;
    UI_out = freq*`get_time;
  end
  else begin
    UI_abs = freq*`get_time - UI_out;
    UI_diff = UI_abs - $rtoi(UI_abs + 0.5) ; // $rtoi does floor function
    UI_out = UI_out + UI_diff;
    phout = pm.write(`M_TWO_PI*UI_out, 0.0, `get_time);
  end
end

endmodule


///////////
`else // AMS
///////////


`include "disciplines.vams"

module ck2phase (input ckin,
       input vdd,
       output phout);

electrical ckin;
electrical vdd;
electrical phout;

// module parameters
parameter freq = 1.0; // clock frequency
parameter dir = 1'b1;  // posedge of ckin if dir ==1'b1, else negedge
parameter vth = 0.5; // logic threshold

// code starts here
reg ckin_int;

real phout_real;
real UI_abs, UI_diff, UI_out;
integer i;  // check this is the first rising edge
initial UI_out = 0.0;
initial i = 0;
initial ckin_int = 1'b0;

always @(cross(V(ckin)-V(vdd)*vth,+1)) ckin_int = dir? 1'b1:1'b0;
always @(cross(V(ckin)-V(vdd)*vth,-1)) ckin_int = dir? 1'b0:1'b1;

always @(posedge ckin_int) begin
  if (i == 0) begin // initialize UI_out with the first rising edge of ckin
    i = 1;
    UI_out = $abstime*freq;
  end
  else begin
    UI_abs = $abstime*freq - UI_out;
    UI_diff = UI_abs - $rtoi(UI_abs + 0.5) ; // $rtoi does floor function
    UI_out = UI_out + UI_diff;
    phout_real = `M_TWO_PI*UI_out;
  end
end

analog begin
  V(phout) <+ phout_real;
end

endmodule


///////////
`endif
///////////
