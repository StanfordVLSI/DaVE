/****************************************************************

Copyright (c) 2018- Stanford University. All rights reserved.

The information and source code contained herein is the 
property of Stanford University, and may not be disclosed or
reproduced in whole or in part without explicit written 
authorization from Stanford University. Contact bclim@stanford.edu for details.

* Filename   : vdiff_drive.v
* Author     : Byongchan Lim (bclim@stanford.edu)
* Description: It takes a differential and common-mode voltage, and
  convert them to two single-ended voltage signals.

* Note       :

* Revision   :
  - 7/26/2016: First release

****************************************************************/

`timescale `DAVE_TIMEUNIT / `DAVE_TIMEUNIT

///////////
`ifndef AMS // NOT AMS
///////////


module vdiff_drive #(
  parameter real scale_d=1.0, // scale differential input by "scale_d"
  parameter real scale_c=1.0  // scale common-mode input by "scale_c"
) (
  `input_pwl diff,  // (vinp-vinn)
  `input_pwl cm,    // (vinp+vinn)/2.0
  `output_pwl vinp, 
  `output_pwl vinn
);

pwl_add2 xp (.in1(cm), .in2(diff), .scale1(scale_c), .scale2(scale_d/2.0), .out(vinp));
pwl_add2 xn (.in1(cm), .in2(diff), .scale1(scale_c), .scale2(-1.0*scale_d/2.0), .out(vinn));

endmodule


///////////
`else // AMS
///////////


`include "discipline.h"
`include "constants.h"

module vdiff_drive #(
  parameter real scale_d=1.0, // scale differential input by "scale_d"
  parameter real scale_c=1.0  // scale common-mode input by "scale_c"
) (
  diff, cm, vinp, vinn
);

input diff, cm; // (vinp-vinn), (vinp+vinn)/2.0
output vinp, vinn;

electrical diff, cm, vinp, vinn;

analog begin
  V(vinp) <+ scale_c*V(cm) + scale_d*V(diff)/2.0;
  V(vinn) <+ scale_c*V(cm) - scale_d*V(diff)/2.0;
end

endmodule


///////////
`endif
///////////
