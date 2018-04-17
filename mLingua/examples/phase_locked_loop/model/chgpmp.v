/****************************************************************

Copyright (c) 2018- Stanford University. All rights reserved.

The information and source code contained herein is the 
property of Stanford University, and may not be disclosed or
reproduced in whole or in part without explicit written 
authorization from Stanford University. Contact bclim@stanford.edu for details.

* Filename   : chgpmp.v
* Author     : Byongchan Lim (bclim@stanford.edu)
* Description: Charge-pump circuit.

* Note       :
  - The output is current, not voltage here.

* Revision   :
  - 7/26/2016: First release

****************************************************************/


module chgpmp (
  `input_real avdd,
  input up, dn,
  `output_real vctrl
  );

`get_timeunit

parameter idn0 = 20e-6;
parameter iup0 = 20e-6;

assign vctrl = up*iup0 - dn*idn0;

endmodule
