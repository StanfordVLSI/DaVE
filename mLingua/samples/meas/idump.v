/****************************************************************

Copyright (c) 2018- Stanford University. All rights reserved.

The information and source code contained herein is the 
property of Stanford University, and may not be disclosed or
reproduced in whole or in part without explicit written 
authorization from Stanford University. Contact bclim@stanford.edu for details.

* Filename   : idump.v
* Author     : Byongchan Lim (bclim@stanford.edu)
* Description: It dumps (time, value) pair of a pwl signal to a file. 
  Two modes are provided: sample mode (window=0) and window mode (window=1). 
  In sample mode, the module samples/dumps an instant value of "in" to a file. 
  In window mode, the module samples/dumps time series for a given window 
  (ts <= time <= te) to a file.
  It differs from "dump.v" in that this module is dedicated to 
  sample current signal as it provides "vdrop" parameter to consider
  finite output impedance of current driver.

* Note       :

* Revision   :
  - 7/26/2016: First release

****************************************************************/

`timescale `DAVE_TIMEUNIT / `DAVE_TIMEUNIT

///////////
`ifndef AMS // NOT AMS
///////////


module idump #(
  parameter real is_n = 1,  // current source if 1, else current sink
                            // in other words, is n-terminal the outnode ?
  parameter real scale = 1.0, // scale output by
  parameter real ts = 0.0,      // start time (window=1), or sample time
  parameter real te = 0.0,      // end time (window=1 only)
  parameter real ti = 0.0,      // interval (window=1 only)
  parameter      window = 1'b0, // sample at ts if window = 1'b0
                              // sample [ts<=t<=te] with interval ti
                              // if window = 1'b1
  parameter      filename = "dump.dat",
  parameter real vdrop = 0.0   // voltage drop across (outnode,refnode)
) (
  `input_pwl refnode, outnode
);

`get_timeunit
PWLMethod pm=new;



integer fid;
reg flag_window;
reg wakeup0;
wire wakeup;
real iout;

assign wakeup = flag_window? wakeup0 : 1'b0;

initial begin
  fid = $fopen(filename,"w");
  flag_window = 1'b0;
  wakeup0 = 1'b0;
  `delay(ts) flag_window = 1'b1;
  if (window) begin
    forever `delay(ti) wakeup0 = ~wakeup0;
  end
end
initial begin
  if (window) `delay(te+TU) flag_window = 1'b0;
end

always @(wakeup or flag_window) 
  if (window && flag_window) begin
    iout = pm.eval(outnode,`get_time);
    if (is_n) iout = -1.0*iout;
    $fwrite(fid, "%.15e %.15e\n", `get_time, scale*iout);
  end

always @(posedge flag_window)
  if (~window) begin
    iout = pm.eval(outnode,`get_time);
    if (is_n) iout = -1.0*iout;
    $fwrite(fid, "%.15e\n", scale*iout);
  end

endmodule


///////////
`else // AMS
///////////


`include "disciplines.vams"

module idump #(
  parameter real is_n = 1,  // current source type if 1, else current sink
  parameter real scale = 1.0, // scale output by
  parameter real ts = 0.0,      // start time (window=1), or sample time
  parameter real te = 0.0,      // end time (window=1 only)
  parameter real ti = 0.0,      // interval (window=1 only)
  parameter integer window = 0, // sample at ts if window = 1'b0
                                // sample [ts<=t<=te] with interval ti
                                // if window = 1'b1
  parameter      filename = "dump.dat",
  parameter real vdrop = 0.0    // voltage drop across (outnode,refnode)

) ( input outnode, refnode );

electrical outnode, refnode;

`get_timeunit

real iout;

integer fid;
reg flag_window;
reg wakeup0;
wire wakeup;

assign wakeup = flag_window? wakeup0 : 1'b0;

initial begin
  fid = $fopen(filename,"w");
  flag_window = 1'b0;
  wakeup0 = 1'b0;
  #(ts/TU) flag_window = 1'b1;
  if (window) begin
    forever #(ti/TU) wakeup0 = ~wakeup0;
  end
end
initial begin
  if (window) #(te/TU+1) flag_window = 1'b0;
end

analog begin
  if (is_n) V(refnode,outnode) <+ vdrop;
  else V(outnode,refnode) <+ vdrop;
end

always @(wakeup or flag_window) 
  if (window && flag_window) begin
    if (is_n) iout = I(refnode,outnode);
    else iout = I(outnode,refnode);
    $fwrite(fid, "%.15e %.15e\n", $time*TU, scale*iout);
  end

always @(posedge flag_window)
  if (~window) begin
    if (is_n) iout = I(refnode,outnode);
    else iout = I(outnode,refnode);
    $fwrite(fid, "%.15e\n", scale*iout);
  end

endmodule


///////////
`endif
///////////
