/****************************************************************

Copyright (c) 2016-2017 Stanford University. All rights reserved.

The information and source code contained herein is the 
property of Stanford University, and may not be disclosed or
reproduced in whole or in part without explicit written 
authorization from Stanford University. Contact bclim@stanford.edu for details.

* Filename   : dump.v
* Author     : Byongchan Lim (bclim@stanford.edu)
* Description: It dumps (time, value) pair of a pwl signal to a file. 
  Two modes are provided: sample mode (window=0) and window mode (window=1). 
  In sample mode, the module samples/dumps an instant value of "in" to a file. 
  In window mode, the module samples/dumps time series for a given window 
  (ts <= time <= te) to a file.

* Note       :

* Revision   :
  - 7/26/2016: First release

****************************************************************/

`timescale `DAVE_TIMEUNIT / `DAVE_TIMEUNIT

///////////
`ifndef AMS // NOT AMS
///////////


module dump #(
  parameter real scale=1.0,     // scale input by 
  parameter real ts = 0.0,      // start time (window=1), or sample time
  parameter real te = 0.0,      // end time (window=1 only)
  parameter real ti = 0.0,      // interval (window=1 only)
  parameter      window = 1'b0, // sample at ts if window = 1'b0
                                // sample [ts<=t<=te] with interval ti
                                // if window = 1'b1
  parameter      filename = "dump.dat"
) ( `input_pwl in );


pwl refnode = '{0,0,0};

dump_diff #(.scale(scale), .ts(ts), .te(te), .ti(ti), .window(window), .filename(filename)) xdumpdiff (.inp(in), .inn(refnode));

endmodule


///////////
`else // AMS
///////////


`include "disciplines.vams"

module dump ( input in );

electrical in;

parameter real scale=1.0;     // scale input by 
parameter real ts = 0.0;      // start time (window=1), or sample time
parameter real te = 0.0;      // end time (window=1 only)
parameter real ti = 0.0;      // interval (window=1 only)
parameter window = 1'b0; // sample at ts if window = 1'b0
                              // sample [ts<=t<=te] with interval ti
                              // if window = 1'b1
parameter filename = "dump.dat";

`get_timeunit

dump_diff #(.scale(scale), .ts(ts), .te(te), .ti(ti), .window(window), .filename(filename)) xdumpdiff (.inp(in), .inn(gnd));

endmodule


///////////
`endif
///////////
