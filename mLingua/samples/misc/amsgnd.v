/****************************************************************

Copyright (c) 2018- Stanford University. All rights reserved.

The information and source code contained herein is the 
property of Stanford University, and may not be disclosed or
reproduced in whole or in part without explicit written 
authorization from Stanford University. Contact bclim@stanford.edu for details.

* Filename   : amsgnd.v
* Author     : Byongchan Lim (bclim@stanford.edu)
* Description: AMS ground valid only for Verilog-AMS simulation.

* Note       :

* Revision   :
  - 7/26/2016: First release

****************************************************************/

`timescale `DAVE_TIMEUNIT / `DAVE_TIMEUNIT

///////////
`ifndef AMS // NOT AMS
///////////


module amsgnd (
  `input_pwl gnd
);
 
endmodule


///////////
`else // AMS
///////////


module amsgnd (
  input gnd
);

electrical gnd;
ground gnd;
 
endmodule


///////////
`endif
///////////
