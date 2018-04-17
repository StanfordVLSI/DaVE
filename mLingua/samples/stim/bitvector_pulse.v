/****************************************************************

Copyright (c) 2018- Stanford University. All rights reserved.

The information and source code contained herein is the 
property of Stanford University, and may not be disclosed or
reproduced in whole or in part without explicit written 
authorization from Stanford University. Contact bclim@stanford.edu for details.

* Filename   : bitvector_pulse.v
* Author     : Byongchan Lim (bclim@stanford.edu)
* Description: It outputs multiple-bits, digital pulses.

* Note       :

* Revision   :
  - 1/ 4/2017: First release

****************************************************************/

`timescale `DAVE_TIMEUNIT / `DAVE_TIMEUNIT

module bitvector_pulse #(
  parameter bit_width = 1,  // number of bits
  parameter b0 = 0,         // initial bit value
  parameter b1 = 1,         // another bit value
  parameter real td=10e-12, // initial delay
  parameter real tw=0.5e-9, // pulse width
  parameter real tp=1e-9    // pulse period
) ( 
  output reg [bit_width-1:0] out, 
  output reg [bit_width-1:0] outb 
);

`get_timeunit

initial begin
  out = b0; outb = b1;
  #(td/TU) ;
  out = b1; outb = b0;
  forever begin
    #(tw/TU) out = b0; outb = b1;
  
    #((tp-tw)/TU) out = b1; outb = b0;
  end
end

endmodule
