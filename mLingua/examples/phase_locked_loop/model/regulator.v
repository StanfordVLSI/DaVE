/****************************************************************

Copyright (c) 2018- Stanford University. All rights reserved.

The information and source code contained herein is the 
property of Stanford University, and may not be disclosed or
reproduced in whole or in part without explicit written 
authorization from Stanford University. Contact bclim@stanford.edu for details.

* Filename   : regulator.v
* Author     : Byongchan Lim (bclim@stanford.edu)
* Description: voltage regulator.

* Note       :
  - Do nothing yet.

* Revision   :
  - 7/26/2016: First release

****************************************************************/

module regulator (
  `input_real vdd_in,
  `input_pwl vctrl,
  `output_pwl vreg);

assign vreg = vctrl;

endmodule
