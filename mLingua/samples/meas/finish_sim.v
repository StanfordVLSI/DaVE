/****************************************************************

Copyright (c) 2018- Stanford University. All rights reserved.

The information and source code contained herein is the 
property of Stanford University, and may not be disclosed or
reproduced in whole or in part without explicit written 
authorization from Stanford University. Contact bclim@stanford.edu for details.

* Filename   : finish_sim.v
* Author     : Byongchan Lim (bclim@stanford.edu)
* Description: It finishes a simulation if "in" are all 'H'.

* Note       :

* Revision   :
  - 7/26/2016: First release

****************************************************************/

`timescale `DAVE_TIMEUNIT / `DAVE_TIMEUNIT

///////////
`ifndef AMS // NOT AMS
///////////


module finish_sim #(
  parameter integer no_sig = 1, // number of inputs
  parameter real delay = 1e-9   // finish sim. after this delay
) ( input [no_sig-1:0] in  );


`get_timeunit

reg finish=0;
always @(in)
  finish <= #(delay/TU) &in;

always @(posedge finish) $finish;

endmodule


///////////
`else // AMS
///////////


module finish_sim #(
  parameter integer no_sig = 1, // number of inputs
  parameter real delay = 1e-9 // finish sim. after this delay
) ( input [no_sig-1:0] in  );

`get_timeunit

reg finish=0;
always @(in)
  finish <= #(delay/TU) &in;

always @(posedge finish) $finish;

endmodule


///////////
`endif
///////////
