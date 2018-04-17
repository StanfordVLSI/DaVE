/****************************************************************

Copyright (c) 2018- Stanford University. All rights reserved.

The information and source code contained herein is the 
property of Stanford University, and may not be disclosed or
reproduced in whole or in part without explicit written 
authorization from Stanford University. Contact bclim@stanford.edu for details.

* Filename   : real_probe.v
* Author     : Byongchan Lim (bclim@stanford.edu)
* Description: 
  It dumps (time, offset) of a real signal to a file when "in" changes.

* Note       :

* Revision   :
  - 7/26/2016: First release

****************************************************************/

module real_probe #(
  parameter real Tstart = 0, // start dumping from this moment
  parameter real Tend = 0,   // end dumping file to this moment
  parameter filename = "dump.dat" // filename to dump
) (
  `input_real in
);

timeunit `DAVE_TIMEUNIT ;
timeprecision `DAVE_TIMEUNIT ;

`protect
//pragma protect 
//pragma protect begin

`get_timeunit


integer handle;
reg dump_flag;
real t0;
event dummy_wakeup;

initial begin
  dump_flag = 1'b0;
  `delay(Tstart) dump_flag = 1'b1;
  `delay(Tend-Tstart) dump_flag = 1'b0;
end

initial handle = $fopen(filename,"w");
initial #1 -> dummy_wakeup;


//always @(`pwl_event(in) or dump_flag) 
always @(in or dump_flag or dummy_wakeup) 
begin
    t0 = `get_time;
    if(t0 >= max(Tstart,TU) && t0 <= Tend)
    $fwrite(handle,"%.15e %.15e\n",t0, in);
end

//pragma protect end
`endprotect

endmodule
