/****************************************************************

Copyright (c) 2018- Stanford University. All rights reserved.

The information and source code contained herein is the 
property of Stanford University, and may not be disclosed or
reproduced in whole or in part without explicit written 
authorization from Stanford University. Contact bclim@stanford.edu for details.

* Filename   : meas_slicer.v
* Author     : Byongchan Lim (bclim@stanford.edu)
* Description: A slicer to generate strobe signal for "strobe.v"

* Note       :

* Revision   :
  - 1/ 3/2017: First release

****************************************************************/

`timescale `DAVE_TIMEUNIT / `DAVE_TIMEUNIT

///////////
`ifndef AMS // NOT AMS
///////////


module meas_slicer #(
  parameter real offset = 0.0 // input offset
) ( `input_pwl in, output out );


`get_timeunit
PWLMethod pm=new;


// slicer
pwl_slicer #(.offset(offset)) uSLICER (.vin(in), .out(out));

endmodule


///////////
`else // AMS
///////////


module meas_slicer #(
  parameter real offset = 0.0 // input offset
) ( input in, output out );

electrical in;
reg out;

// slicer
always @(cross(V(in)-offset,+1)) out = 1;
always @(cross(V(in)-offset,-1)) out = 0;

endmodule


///////////
`endif
///////////
