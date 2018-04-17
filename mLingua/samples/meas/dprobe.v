/****************************************************************

Copyright (c) 2018- Stanford University. All rights reserved.

The information and source code contained herein is the 
property of Stanford University, and may not be disclosed or
reproduced in whole or in part without explicit written 
authorization from Stanford University. Contact bclim@stanford.edu for details.

* Filename   : dprobe.v
* Author     : Byongchan Lim (bclim@stanford.edu)
* Description: 
  It dumps an input digital signal to a file.

* Note       :

* Revision   :
  - 7/26/2016: First release

****************************************************************/


module dprobe #(
  parameter integer BITW = 1, // bit width of a digital signal
  parameter logic SYNC = 1'b0,  // '1': sample "in" with a clock and dump the sampled data
                                // '0': dump "in" data
  parameter real Tstart = 0,    // time start of signal dump
  parameter real Tend = Tstart, // time end of signal dump
  parameter filename = "dump.dat" // filename to dump 
) (
  input clk,  // sampling clock when SYNC = 1
  input [BITW-1:0] in // input digital signal to dump
);

timeunit `DAVE_TIMEUNIT ;
timeprecision `DAVE_TIMEUNIT ;

`protect
//pragma protect 
//pragma protect begin

`get_timeunit
PWLMethod pm=new;


reg [BITW-1:0] in_s;
integer fid;
event sample;
real t0;
real t_prev = -1;

initial begin
  fid = $fopen(filename,"w");
  #(Tstart/TU);
  if (!SYNC) -> sample;
  #((Tend-Tstart)/TU);
  if (!SYNC) -> sample;
end

always @(posedge clk) in_s <= in;

always @(in) begin
  t0 = `get_time;
  if (!SYNC & t0 > Tstart & t0 < Tend) -> sample;
end

always @(in_s) begin
  t0 = `get_time;
  if (SYNC & t0 > Tstart & t0 < Tend) -> sample;
end

always @(sample) begin
  t0 = `get_time;
  if (t0!=t_prev) $fwrite(fid, "%.15e %d\n", t0, SYNC ? in_s : in);
  t_prev = t0;
end

//pragma protect end
`endprotect

endmodule
