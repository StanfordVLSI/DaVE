/****************************************************************

Copyright (c) 2018- Stanford University. All rights reserved.

The information and source code contained herein is the 
property of Stanford University, and may not be disclosed or
reproduced in whole or in part without explicit written 
authorization from Stanford University. Contact bclim@stanford.edu for details.

* Filename   : channel.v
* Author     : Byongchan Lim (bclim@stanford.edu)
* Description: Channel model for high-speed link simulation.

* Note       :

* Revision   :
  - 7/26/2016: First release

****************************************************************/


module channel #(
  parameter real etol = 0.001 // error tolerance
) (
  `input_pwl in,
  `output_pwl out
);

`get_timeunit
PWLMethod pm=new;


channel_aug #(.etol(etol)) ch (.si(in), .so(out));

endmodule
