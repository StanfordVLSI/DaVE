/****************************************************************

Copyright (c) 2016-2017 Stanford University. All rights reserved.

The information and source code contained herein is the 
property of Stanford University, and may not be disclosed or
reproduced in whole or in part without explicit written 
authorization from Stanford University. Contact bclim@stanford.edu for details.

* Filename   : dump_diff.v
* Author     : Byongchan Lim (bclim@stanford.edu)
* Description: It dumps (time, value) pair of a differential pwl signal 
  ("inp"-"inn") to a file. Two modes are provided: sample mode (window=0)
  and window mode (window=1). In sample mode, the module samples/dumps 
  an instant value of ("inp"-"inn") to a file. In window mode, the module
  samples/dumps time series for a given window (ts <= time <= te) to a 
  file.

* Note       :

* Revision   :
  - 7/26/2016: First release

****************************************************************/

`timescale `DAVE_TIMEUNIT / `DAVE_TIMEUNIT

///////////
`ifndef AMS // NOT AMS
///////////


module dump_diff #(
  parameter real scale=1.0,     // scale input by 
  parameter real ts = 0.0,      // start time (window=1), or sample time
  parameter real te = 0.0,      // end time (window=1 only)
  parameter real ti = 0.0,      // interval (window=1 only)
  parameter      window = 1'b0, // sample at ts if window = 1'b0
                                // sample [ts<=t<=te] with interval ti
                                // if window = 1'b1
  parameter      filename = "dump.dat"
) ( `input_pwl inp, inn );


`get_timeunit
PWLMethod pm=new;

integer fid;
event sample;
logic flag_window;

initial begin
  fid = $fopen(filename,"w");
  `delay(ts);
  -> sample;
  if (window) begin
    forever begin
      `delay(ti);
      -> sample;
    end
  end
end

initial begin
  flag_window = 1'b1;
  if (window) #(te/TU+1) flag_window = 1'b0;
end


always @(sample) begin
  // (time,value) vectors or a single value
  if (window && flag_window)  $fwrite(fid, "%.15e %.15e\n", $time*TU, scale*(pm.eval(inp,`get_time)-pm.eval(inn,`get_time)));
  else $fwrite(fid, "%.15e\n", scale*(pm.eval(inp,`get_time)-pm.eval(inn,`get_time)));
end

endmodule


///////////
`else // AMS
///////////


`include "disciplines.vams"

module dump_diff ( input inp, inn );

electrical inp, inn;

parameter real scale=1.0;     // scale input by 
parameter real ts = 0.0;      // start time (window=1), or sample time
parameter real te = 0.0;      // end time (window=1 only)
parameter real ti = 0.0;      // interval (window=1 only)
parameter integer window = 0; // sample at ts if window = 1'b0
                              // sample [ts<=t<=te] with interval ti
                              // if window = 1'b1
parameter      filename = "dump.dat";

`get_timeunit


integer fid;
reg flag_window;

event sample;

initial begin
  fid = $fopen(filename,"w");
  #(ts/TU);
  -> sample;
  if (window) begin
    forever begin
      #(ti/TU);
      -> sample;
    end
  end
end

initial begin
  flag_window = 1'b1;
  if (window) #(te/TU+1) flag_window = 1'b0;
end


always @(sample) begin
  // (time,value) vectors or a single value
  if (window && flag_window)  $fwrite(fid, "%.15e %.15e\n", $time*TU, scale*V(inp,inn));
  else $fwrite(fid, "%.15e\n", scale*V(inp,inn));

end

endmodule

///////////
`endif
///////////
