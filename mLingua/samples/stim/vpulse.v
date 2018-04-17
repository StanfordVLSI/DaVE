/****************************************************************

Copyright (c) 2018- Stanford University. All rights reserved.

The information and source code contained herein is the 
property of Stanford University, and may not be disclosed or
reproduced in whole or in part without explicit written 
authorization from Stanford University. Contact bclim@stanford.edu for details.

* Filename   : vpulse.v
* Author     : Byongchan Lim (bclim@stanford.edu)
* Description: It outputs a voltage pulse in PWL.

* Note       :

* Revision   :
  - 7/26/2016: First release

****************************************************************/

`timescale `DAVE_TIMEUNIT / `DAVE_TIMEUNIT

///////////
`ifndef AMS // NOT AMS
///////////


module vpulse #(
  parameter real v0 = 0.0,  // low value
  parameter real v1 = 0.0,  // high value
  parameter real td=10e-12, // initial delay
  parameter real tr=10e-12, // rise transition time
  parameter real tf=10e-12, // fall transition time
  parameter real tw=0.5e-9, // pulse width
  parameter real tp=1e-9    // pulse period
) ( 
  `output_pwl vout, voutb
);

wire out, outb;

pulse #(.b0(1'b0), .td(td), .tw(tw), .tp(tp)) pls (.out(out), .outb(outb));
bit2pwl #(.vh(v1), .vl(v0), .tr(tr), .tf(tf)) xb2p1 (.in(out), .out(vout));
bit2pwl #(.vh(v1), .vl(v0), .tr(tr), .tf(tf)) xb2p2 (.in(outb), .out(voutb));

endmodule


///////////
`else // AMS
///////////


`include "disciplines.vams"
`include "constants.vams"

module vpulse #(
parameter real v0 = 0.0,   // low value
parameter real v1 = 1.0,   // high value
parameter real td = 1n,    // initial delay
parameter real tr = 10p,   // rise transition time
parameter real tf = 10p,   // fall transition time
parameter real tw = 0.49n, // pulse width
parameter real tp = 1n     // period
) ( vout, voutb );

output  vout, voutb;
electrical vout, voutb;

wire out;

pulse #(.b0(1'b0), .td(td), .tw(tw), .tp(tp)) pls (.out(out));

analog begin
  V(vout) <+ transition(out? v1:v0,0,tr,tf);
  V(voutb) <+ transition(out? v0:v1,0,tr,tf);
end

endmodule


///////////
`endif
///////////
