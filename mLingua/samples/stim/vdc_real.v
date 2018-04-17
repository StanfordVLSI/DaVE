/****************************************************************

Copyright (c) 2018- Stanford University. All rights reserved.

The information and source code contained herein is the 
property of Stanford University, and may not be disclosed or
reproduced in whole or in part without explicit written 
authorization from Stanford University. Contact bclim@stanford.edu for details.

* Filename   : vdc_real.v
* Author     : Byongchan Lim (bclim@stanford.edu)
* Description: It outputs a DC voltage in real (PWC).

* Note       :

* Revision   :
  - 7/26/2016: First release

****************************************************************/

`timescale `DAVE_TIMEUNIT / `DAVE_TIMEUNIT

////////////
`ifndef AMS // NOT AMS
////////////

module vdc_real #(
  parameter real dc=0.3  // voltage value
) (
  `output_real vout
);

initial vout = dc ;

endmodule


////////////
`else // AMS
////////////

`include "discipline.h"
`include "constants.h"

module vdc #(
  parameter real dc=0.3 // dc value
) (output vout);

electrical vout;

analog V(vout) <+ dc;

endmodule


////////////
`endif
////////////
