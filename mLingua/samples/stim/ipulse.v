/****************************************************************

Copyright (c) 2018- Stanford University. All rights reserved.

The information and source code contained herein is the 
property of Stanford University, and may not be disclosed or
reproduced in whole or in part without explicit written 
authorization from Stanford University. Contact bclim@stanford.edu for details.

* Filename   : ipulse.v
* Author     : Byongchan Lim (bclim@stanford.edu)
* Description: It outputs a current (source or sink) pulse in PWL.

* Note       :

* Revision   :
  - 7/26/2016: First release

****************************************************************/

`timescale `DAVE_TIMEUNIT / `DAVE_TIMEUNIT

////////////
`ifndef AMS // NOT AMS
////////////

module ipulse #(
  parameter real is_n = 1,  // current source if 1, else current sink
                            // in other words, is n-terminal the outnode ?
  parameter real i0 = 0.0,  // initial value 0
  parameter real i1 = 0.0,  // initial value 1
  parameter real td=10e-12, // initial delay
  parameter real tr=10e-12, // rise transition time
  parameter real tf=10e-12, // fall transition time
  parameter real tw=0.5e-9, // pulse width
  parameter real tp=1e-9    // pulse period
) ( 
  `input_pwl refnode, // reference node, valid only for Verilog-A module
  `output_pwl outnode // current output
);

wire pout;

pulse #(.b0(1'b0), .b1(1'b1), .td(td), .tw(tw), .tp(tp)) pls (.out(pout));
bit2pwl #(.vh(i1), .vl(i0), .tr(tr), .tf(tf)) xb2p (.in(pout), .out(outnode));

endmodule

////////////
`else // AMS
////////////

`include "disciplines.vams"
`include "constants.vams"

module ipulse #(
  parameter real is_n = 1,   // current source if 1, else current sink
  parameter real i0 = 0.0,   // initial value 0
  parameter real i1 = 1.0,   // initial value 1
  parameter real td = 1n,    // initial delay
  parameter real tr = 10p,   // rise transition time
  parameter real tf = 10p,   // fall transition time
  parameter real tw = 0.49n, // pulse width
  parameter real tp = 1n     // period
) ( outnode, refnode );

output outnode; // current output node
output refnode; // reference node
electrical outnode, refnode;

wire pout;

pulse #(.b0(1'b0), .b1(1'b1), .td(td), .tw(tw), .tp(tp)) pls (.out(pout));

analog begin
  if (is_n) I(refnode,outnode) <+ transition(pout? i1:i0,0,tr,tf);
  else I(outnode,refnode) <+ transition(pout? i1:i0,0,tr,tf);
end

endmodule

////////////
`endif
////////////
