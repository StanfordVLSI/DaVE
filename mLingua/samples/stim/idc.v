/****************************************************************

Copyright (c) 2018- Stanford University. All rights reserved.

The information and source code contained herein is the 
property of Stanford University, and may not be disclosed or
reproduced in whole or in part without explicit written 
authorization from Stanford University. Contact bclim@stanford.edu for details.

* Filename   : idc.v
* Author     : Byongchan Lim (bclim@stanford.edu)
* Description: It outputs a DC current (source or sink).
    - is_n = 1
    
        ---- refnode
          |
          v
        ---- outnode

    - is_n = 0
    
        ---- outnode
          |
          v
        ---- refnode

* Note       :

* Revision   :
  - 7/26/2016: First release

****************************************************************/

`timescale `DAVE_TIMEUNIT / `DAVE_TIMEUNIT

////////////
`ifndef AMS // NOT AMS
////////////


module idc #(
  parameter real is_n = 1,  // current source if 1, else current sink
                            // in other words, is n-terminal the outnode ?
  parameter real dc=1e-6    // current value
) ( 
  `input_pwl refnode,   // reference node, valid only for Verilog-A module
  `output_pwl outnode   // current output
);

PWLMethod pm=new;

real i_scale;

initial begin
  i_scale = is_n ? 1.0 : -1.0;
  outnode=pm.write(i_scale*dc,0,0);
end

endmodule

////////////
`else // AMS
////////////


`include "discipline.h"

module idc #(
  parameter real is_n = 1,  // current source if 1, else current sink
  parameter real dc=1e-6 // current value
) ( outnode, refnode );

output outnode;   // current output node
output refnode;   // reference node
electrical outnode, refnode;

analog begin
  if (is_n) I(refnode,outnode) <+ dc;
  else I(outnode,refnode) <+ dc;
end

endmodule


////////////
`endif
////////////
