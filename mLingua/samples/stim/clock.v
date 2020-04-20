/****************************************************************

Copyright (c) 2018- Stanford University. All rights reserved.

The information and source code contained herein is the 
property of Stanford University, and may not be disclosed or
reproduced in whole or in part without explicit written 
authorization from Stanford University. Contact bclim@stanford.edu for details.

* Filename   : clock.v
* Author     : Byongchan Lim (bclim@stanford.edu)
* Description: It outputs a digital clock

* Note       :

* Revision   :
  - 7/26/2016: First release

****************************************************************/

module clock #(
    parameter real freq = 1e9,    // frequency
    parameter real duty = 0.5,    // duty cycle
    parameter real td = 0.0,      // initial delay in second
    parameter b0 = 1'b0           // initial value
) (
    output ckout,                 // clock output
    output ckoutb                 // inverted clock output
);

    timeunit `DAVE_TIMEUNIT ;
    timeprecision `DAVE_TIMEUNIT ;

    pulse #(
        .b0(b0),
        .td(td),
        .tw(duty/freq),
        .tp(1.0/freq)
    ) xpulse (
        .out(ckout),
        .outb(ckoutb)
    );

endmodule

