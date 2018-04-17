/****************************************************************

Copyright (c) 2018- Stanford University. All rights reserved.

The information and source code contained herein is the 
property of Stanford University, and may not be disclosed or
reproduced in whole or in part without explicit written 
authorization from Stanford University. Contact bclim@stanford.edu for details.

* Filename   : res_pwl.v
* Author     : Byongchan Lim (bclim@stanford.edu)
* Description: A resistor, valid for Verilog-AMS only.

* Note       :

* Revision   :
  - 7/26/2016: First release

****************************************************************/

// resistor

`ifndef AMS // NOT AMS


module res_pwl #(
  parameter real r=0,
  parameter real vmax=1.5
) (
  `input_pwl pn,
  `input_pwl nn
);

endmodule


`else // AMS


`include "discipline.h"

module res_pwl #(
  parameter real r=0 from [0:inf),
  parameter real vmax=0 from [0:inf)
) (pn, nn);
inout pn, nn;
electrical pn, nn;

real i, v;

analog begin
  i = I(pn,nn);
  v = r*i;
  if (v>vmax) v = vmax;
  V(pn, nn) <+ v;
end

endmodule


`endif
