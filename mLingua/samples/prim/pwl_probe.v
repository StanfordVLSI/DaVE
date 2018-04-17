/****************************************************************

Copyright (c) 2018- Stanford University. All rights reserved.

The information and source code contained herein is the 
property of Stanford University, and may not be disclosed or
reproduced in whole or in part without explicit written 
authorization from Stanford University. Contact bclim@stanford.edu for details.

* Filename   : pwl_probe.v
* Author     : Byongchan Lim (bclim@stanford.edu)
* Description: 
  It dumps (time, offset) of a pwl signal to a file when "in" changes.

* Note       :

* Revision   :
  - 7/26/2016: First release

****************************************************************/


module pwl_probe #(
  parameter real Tstart = 0,    // time start of signal dump
  parameter real Tend = Tstart, // time end of signal dump
  parameter filename = "dump.dat" // filename to dump 
) (
  `input_pwl in // pwl signal to dump
);

timeunit `DAVE_TIMEUNIT ;
timeprecision `DAVE_TIMEUNIT ;

`protect
//pragma protect 
//pragma protect begin

`get_timeunit
PWLMethod pm=new;


integer fid;
event sample;
real t0;
real t_prev = -1;

initial begin
  fid = $fopen(filename,"w");
  #(Tstart/TU);
  -> sample;
  #((Tend-Tstart)/TU);
  -> sample;
end

always @(`pwl_event(in)) begin
  t0 = `get_time;
  if (t0 > Tstart && t0 < Tend) -> sample;
end

always @(sample) begin
  t0 = `get_time;
  if (t0!=t_prev) $fwrite(fid, "%.15e %.15e\n", t0, pm.eval(in,t0));
  t_prev = t0;
end

//pragma protect end
`endprotect

endmodule
