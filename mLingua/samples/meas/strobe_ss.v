/****************************************************************

Copyright (c) 2018- Stanford University. All rights reserved.

The information and source code contained herein is the 
property of Stanford University, and may not be disclosed or
reproduced in whole or in part without explicit written 
authorization from Stanford University. Contact bclim@stanford.edu for details.

* Filename   : strobe_ss.v
* Author     : Byongchan Lim (bclim@stanford.edu)
* Description: It strobes a signal and dump it to a file after
  detecting steady-state condition (using "detect_ss" cell).

* Note       :

* Revision   :
  - 7/26/2016: First release

****************************************************************/

`timescale `DAVE_TIMEUNIT / `DAVE_TIMEUNIT

///////////
`ifndef AMS // NOT AMS
///////////


module strobe_ss #(
  parameter real ts = 0.0,      // start time to check
  parameter real ti = 0.0,      // interval to check
  parameter real tol= 0.001,     // tolerance
  parameter integer no_buff = 4, // number of buffer for filtering
  parameter      filename = "dump.dat" // filename to dump
) ( `input_pwl in, output detect );


`get_timeunit
PWLMethod pm=new;

// detect steady-state condition
detect_ss #(.ts(ts), .ti(ti), .tol(tol), .no_buff(no_buff)) xdetect (.in(in), .detect(detect));

// strobe a signal
strobe #(.filename(filename)) xstrobe (.strobe(detect), .in(in));

endmodule


///////////
`else // AMS
///////////


module strobe_ss #(
  parameter  is_pwl=1'b1,  // 1 if "in" is pwl, 0 if "in" is real
  parameter real ts = 0.0,      // start time 
  parameter real ti = 0.0,      // interval to check
  parameter real tol= 0.001,     // tolerance
  parameter integer no_buff = 4, // number of buffer for filtering
  parameter      filename = "dump.dat"
) ( input in, output detect );

electrical in;

// detect steady-state condition
detect_ss #(.is_pwl(is_pwl), .ts(ts), .ti(ti), .tol(tol), .no_buff(no_buff)) xdetect (.in(in), .detect(detect));

// strobe a signal
strobe #(.is_pwl(is_pwl), .filename(filename)) xstrobe (.strobe(detect), .in(in));

endmodule


///////////
`endif
///////////
