/***********************************************************

Copyright (c) 2018- Stanford University. All rights reserved.

The information and source code contained herein is the 
property of Stanford University, and may not be disclosed or
reproduced in whole or in part without explicit written 
authorization from Stanford University. Contact bclim@stanford.edu for details.

* Filename   : dac.v
* Author     : Byongchan Lim (bclim@stanford.edu)
* Date       : 00/00/2016
* Description: Ideal synchronous DAC

* Note       :

* Todo       :

* Revision   :
  - 7/26/2016: First release

***********************************************************/

`timescale `DAVE_TIMEUNIT / `DAVE_TIMEUNIT

module dac #(
// parameters here
  parameter integer BITW=8,  // bit width of a dac
  parameter real TR=1e-12,   // transition time of "out"
  parameter SYNC=1'b1        // 1'b1 if it is synchronous
) (
// I/Os here
  `input_real out_min,  // min value of output
  `input_real out_max,  // max value of output
  input clk,            // clock
  input [BITW-1:0] din, // digital input
  `output_pwl out,      // analog output
  `output_real lsb      // lsb number
);

`get_timeunit
PWLMethod pm=new;

`protect
//pragma protect 
//pragma protect begin

///////////////////
// CODE STARTS HERE
///////////////////

// wires, assignment
real fscale;  // full scale
real out_r;
real out_r_async; // real of out
real out_r_sync; // real of out in case of ASYNC = 1'b1
pwl out_min_pwl;  // pwl of out_min input
event wakeup;

// body

initial #1 -> wakeup;  // for ncsim

always @(out_min or out_max or wakeup) begin
  fscale = out_max - out_min;
  lsb = fscale/(2.0**BITW);
end

always @(din or lsb) out_r_async = out_min + lsb*din;

always @(posedge clk)
  if (SYNC) out_r_sync = out_r_async;

assign out_r = SYNC ? out_r_sync : out_r_async;

real2pwl #(.tr(TR)) uR2P (.in(out_r), .out(out));

//pragma protect end
`endprotect
endmodule

