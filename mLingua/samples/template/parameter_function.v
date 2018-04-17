/****************************************************************

Copyright (c) 2018- Stanford University. All rights reserved.

The information and source code contained herein is the 
property of Stanford University, and may not be disclosed or
reproduced in whole or in part without explicit written 
authorization from Stanford University. Contact bclim@stanford.edu for details.

* Filename   : parameter_function.v
* Author     : Byongchan Lim(bclim@stanford.edu)
* Description: Template for PWL inputs to parameter mapping

* Note       :

* Revision   :
  - 7/26/2016: First release

****************************************************************/

module parameter_function #(
// parameters here
  parameter integer BW_MODE = 2,  // bit width of digital mode inputs
  parameter real RES_IN1 = 0.1,  // "in1" signal resolution to discretization
  parameter real RES_IN2 = 0.1   // "in2" signal resolution to discretization
// ... add more resolution parameter values if necessary
//  ...
) (
// I/Os here
  input [BW_MODE-1:0] mode, // digital mode inputs
  `input_pwl in1,  // input
  `input_pwl in2,  // input
//  `input_pwl in3, ...  // another inputs
  `output_real out_param // output parameter
);

`get_timeunit
PWLMethod pm=new;

///////////////////
// CODE STARTS HERE
///////////////////

// wires, assignment
real in1_r;  // discretized input "in1"
real in2_r;  // discretized input "in2"
// real in3_r, ... ;

// body
initial out_param = 0.0; // put initial value for valid start

pwl2real #(.dv(RES_IN1)) uP2R1 (.in(in1), .out(in1_r)); // discretize "in1"
pwl2real #(.dv(RES_IN2)) uP2R2 (.in(in2), .out(in2_r)); // discretize "in2"
//pwl2real #(.dv(RES_IN3)) uP2R3 (.in(in3), .out(in3_r)); // discretize "in3"

always @(in1_r, in2_r) // update output_param  (add more sensitivity list if necessary)
  case
    0: out_param = ; // out_param = f(in1_r, in2_r, ...);
    1: out_param = ; // out_param = f(in1_r, in2_r, ...);
    2: out_param = ; // out_param = f(in1_r, in2_r, ...);
    3: out_param = ; // out_param = f(in1_r, in2_r, ...);
    // add more mode if necessary
    default: out_param = ; // out_param = f(in1_r, in2_r, ...);
  endcase

endmodule

