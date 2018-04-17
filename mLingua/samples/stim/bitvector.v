/****************************************************************

Copyright (c) 2018- Stanford University. All rights reserved.

The information and source code contained herein is the 
property of Stanford University, and may not be disclosed or
reproduced in whole or in part without explicit written 
authorization from Stanford University. Contact bclim@stanford.edu for details.

* Filename   : bitvector.v
* Author     : Byongchan Lim (bclim@stanford.edu)
* Description: It outputs a static bit vector 

* Note       :

* Revision   :
  - 7/26/2016: First release

****************************************************************/

`timescale `DAVE_TIMEUNIT / `DAVE_TIMEUNIT

module bitvector #(
  parameter integer bit_width = 1,  // bit width
  parameter integer value = 0       // value to output
  ) (
  output [bit_width-1:0] out,
  output [bit_width-1:0] outb // inverse of out
);

assign out = value;
assign outb = ~value;

endmodule
