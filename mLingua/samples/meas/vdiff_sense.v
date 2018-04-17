/****************************************************************

Copyright (c) 2018- Stanford University. All rights reserved.

The information and source code contained herein is the 
property of Stanford University, and may not be disclosed or
reproduced in whole or in part without explicit written 
authorization from Stanford University. Contact bclim@stanford.edu for details.

* Filename   : vdiff_sense.v
* Author     : Byongchan Lim (bclim@stanford.edu)
* Description: It senses two single-ended signals ("vinp", "vinn")
  and outputs their differential ("diff") and common-mode ("cm")
  signals.

* Note       :

* Revision   :
  - 7/26/2016: First release

****************************************************************/

`timescale `DAVE_TIMEUNIT / `DAVE_TIMEUNIT

///////////
`ifndef AMS // NOT AMS
///////////


module vdiff_sense #(
  parameter real scale=1.0  // scale the output by this number
) (
  `input_pwl vinp, 
  `input_pwl vinn,
  `output_pwl diff, // vinp-vinn
  `output_pwl cm    // (vinp+vinn)/2.0
);

pwl_add2 xp (.in1(vinp), .in2(vinn), .scale1(scale/2.0), .scale2(scale/2.0), .out(cm));
pwl_add2 xn (.in1(vinp), .in2(vinn), .scale1(scale), .scale2(-scale), .out(diff));

//pwl_add #(.no_sig(2)) xp (.in('{vinp,vinn}), .scale('{scale/2.0,scale/2.0}), .out(cm));
//pwl_add #(.no_sig(2)) xn (.in('{vinp,vinn}), .scale('{scale,-1.0*scale}), .out(diff));

endmodule


///////////
`else // AMS
///////////


`include "disciplines.vams"

module vdiff_sense #(
  parameter real scale = 1.0  // scale the output by this number
) (
  input vinp,
  input vinn,
  output diff,
  output cm
);

electrical vinp, vinn, diff, cm;

analog begin
  V(cm) <+ scale*(V(vinp)+V(vinn))/2.0;
  V(diff) <+ scale*(V(vinp)-V(vinn));
end

endmodule


///////////
`endif
///////////
