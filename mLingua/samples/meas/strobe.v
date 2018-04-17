/****************************************************************

Copyright (c) 2018- Stanford University. All rights reserved.

The information and source code contained herein is the 
property of Stanford University, and may not be disclosed or
reproduced in whole or in part without explicit written 
authorization from Stanford University. Contact bclim@stanford.edu for details.

* Filename   : strobe.v
* Author     : Byongchan Lim (bclim@stanford.edu)
* Description: It strobes a signal (@posedge of "strobe") and dump 
  it to a file.

* Note       :

* Revision   :
  - 7/26/2016: First release

****************************************************************/

`timescale `DAVE_TIMEUNIT / `DAVE_TIMEUNIT

///////////
`ifndef AMS // NOT AMS
///////////


module strobe #(
  parameter      filename = "dump.dat"
) ( input strobe, `input_pwl in, `output_pwl out );


`get_timeunit
PWLMethod pm=new;

integer fid;
initial fid = $fopen(filename,"w");

// strobe a signal
always @(posedge strobe) begin
  $fwrite(fid, "%.15e\n", pm.eval(in,`get_time));
  out = '{pm.eval(in,`get_time),0,0};
end

endmodule


///////////
`else // AMS
///////////


module strobe #(
  parameter is_pwl=1'b1,  // dummy for va(ms)
  parameter filename = "dump.dat"
) ( input strobe, input in, output out );

electrical in, out;

integer fid;
real out_r;
initial fid = $fopen(filename,"w");

// strobe a signal
always @(posedge strobe) begin
  $fwrite(fid, "%.15e\n", V(in));
  out_r = V(in);
end

analog begin
  V(out) <+ out_r;
end

endmodule


///////////
`endif
///////////
