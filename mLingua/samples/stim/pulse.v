/****************************************************************

Copyright (c) 2018- Stanford University. All rights reserved.

The information and source code contained herein is the 
property of Stanford University, and may not be disclosed or
reproduced in whole or in part without explicit written 
authorization from Stanford University. Contact bclim@stanford.edu for details.

* Filename   : pulse.v
* Author     : Byongchan Lim (bclim@stanford.edu)
* Description: It outputs a digital pulse.

* Note       :

* Revision   :
  - 7/26/2016: First release

****************************************************************/

`timescale `DAVE_TIMEUNIT / `DAVE_TIMEUNIT

module pulse #(
    parameter b0 = 0,            // initial bit value
    parameter real td=10e-12,    // initial delay
    parameter real tw=0.5e-9,    // pulse width
    parameter real tp=1e-9       // pulse period
) (
    `ifdef AMS
        out,
        outb
    `else
        output reg out,
        output outb
    `endif
);

    `ifdef AMS
        output reg out;
        output outb;
    `endif

    assign outb = ~out;

    initial begin
        out = b0;
        #(td*1s);
        out = ~b0;
        forever begin
            #(tw*1s) out = b0;
            #((tp-tw)*1s) out = ~b0;
         end
    end

endmodule