/****************************************************************

Copyright (c) 2018- Stanford University. All rights reserved.

The information and source code contained herein is the 
property of Stanford University, and may not be disclosed or
reproduced in whole or in part without explicit written 
authorization from Stanford University. Contact bclim@stanford.edu for details.

* Filename   : pfd.v
* Author     : Byongchan Lim (bclim@stanford.edu)
* Description: Phase-frequency detector

* Note       :

* Revision   :
  - 7/26/2016: First release

****************************************************************/


module pfd(
  `input_real vdd_in,
  input ext_rstb,
  input ckref, fdbk,
  output reg up,dn);

`get_timeunit

parameter tos = 0.0;

wire reset = (up & dn) | ~ext_rstb ;


// actual PFD operation
always @(posedge ckref or posedge reset)
  if (reset) `delay(30e-12) up <= 0;
  else up <= 1'b1;

always @(posedge fdbk or posedge reset)
  if (reset) `delay(30e-12) dn <= 0;
  else dn <= 1'b1;

endmodule
