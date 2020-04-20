/****************************************************************

Copyright (c) 2018 Stanford University. All rights reserved.

The information and source code contained herein is the 
property of Stanford University, and may not be disclosed or
reproduced in whole or in part without explicit written 
authorization from Stanford University. Contact #EMAIL# for details.

* Filename   : pwl_delay_prim.v
* Author     : Byongchan Lim (bclim@stanford.edu)
* Description: 
  - It delays a pwl signal.
  - delay is an input (c.f. pwl_delay.v)

* Note       :

* Revision   :
  - 7/26/2016: First release

****************************************************************/

`include "mLingua_pwl.vh"

module pwl_delay_prim #(
    parameter real scale = 1.0    // scale factor of input,
) (
    `input_real delay,            // delay in sec.
    `input_pwl in,                // pwl inputs
    `output_pwl out               // pwl output
);

    timeunit `DAVE_TIMEUNIT ;
    timeprecision `DAVE_TIMEUNIT ;

    PWLMethod pm = new;

    always @(`pwl_event(in)) begin
        if ($realtime==0) begin
            out = in;
        end else begin
            out <= #(delay*1s) pm.write(scale*in.a, scale*in.b, delay+in.t0);
        end
    end

endmodule
