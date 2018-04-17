/****************************************************************

Copyright (c) 2018- Stanford University. All rights reserved.

The information and source code contained herein is the 
property of Stanford University, and may not be disclosed or
reproduced in whole or in part without explicit written 
authorization from Stanford University. Contact bclim@stanford.edu for details.

* Filename   : vcobuf.v
* Author     : Byongchan Lim (bclim@stanford.edu)
* Description: VCO output buffer. 

* Note       :

* Revision   :
  - 7/26/2016: First release

****************************************************************/

module vcobuf(
  `input_real avdd, 
  input lck,lckb,
  output hck,
  output hckb);

assign hckb = ~hck;
assign hck = lck;

endmodule
