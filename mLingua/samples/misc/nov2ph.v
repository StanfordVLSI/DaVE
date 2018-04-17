/****************************************************************

Copyright (c) 2018- Stanford University. All rights reserved.

The information and source code contained herein is the 
property of Stanford University, and may not be disclosed or
reproduced in whole or in part without explicit written 
authorization from Stanford University. Contact bclim@stanford.edu for details.

* Filename   : nov2ph.v
* Author     : Byongchan Lim (bclim@stanford.edu)
* Description: 
  - Non-overlap two-phase clock generator.

* Note       :
  - There is an assertion that tphi >= 0.5*novtime .

* Revision   :
  - 7/26/2016: First release

****************************************************************/


module nov2ph #(
  parameter real novtime = 100e-12, // nonoverlap time
  parameter real tphi = 80e-12      // intrinsic propagation delay
) (
  input clk,      // clock input
  output reg ph1, // phase1 clock output
  output ph1b,    // ~ph1
  output reg ph2, // phase2 clock output
  output ph2b     // ~ph2
);

timeunit `DAVE_TIMEUNIT ;
timeprecision `DAVE_TIMEUNIT ;

// assertion
initial begin
  assert (tphi > novtime/2.0) else $error("[non2ph] Intrinsic propagation delay (tphi) cannot be smaller than half of Non-overlap time (novtime)");
  ph1 = 1'b0;
  ph2 = 1'b0;
end

`protect
//pragma protect 
//pragma protect begin

`get_timeunit
real t0;

assign ph1b = ~ph1; 
assign ph2b = ~ph2; 

always @(posedge clk) begin
  t0 = `get_time;
  if ($time == 0) begin
    ph1 <= 0;
    ph2 <= 0;
  end
  else begin
    ph1 <= `delay(tphi+novtime/2.0) 1'b1;
    ph2 <= `delay(tphi-novtime/2.0) 1'b0;
  end
end

always @(negedge clk) begin
  if ($time == 0) begin
    ph1 <= 0;
    ph2 <= 0;
  end
  else if ((`get_time-t0)<novtime) begin
    $display("Pulse width is smaller than non-overlap time %.3f [nsec]", novtime*1e9);
    ph1 <= `delay(tphi+novtime/2.0) 1'b0;
    ph2 <= `delay(tphi+novtime/2.0) 1'b1;
  end
  else begin
    ph1 <= `delay(tphi-novtime/2.0) 1'b0; 
    ph2 <= `delay(tphi+novtime/2.0) 1'b1;
  end
end

//pragma protect end
`endprotect

endmodule
