/****************************************************************

Copyright (c) 2018- Stanford University. All rights reserved.

The information and source code contained herein is the 
property of Stanford University, and may not be disclosed or
reproduced in whole or in part without explicit written 
authorization from Stanford University. Contact bclim@stanford.edu for details.

* Filename   : pwl_slicer.v
* Author     : Byongchan Lim (bclim@stanford.edu)
* Description: 
  It slices an analog signal to logic 'H' or 'L'.

* Note       :
  It differs from "pwl_slicer_prim" in that its input offset 
  is a static value.

* Revision   :
  - 7/26/2016: First release

****************************************************************/


module pwl_slicer #(
  parameter real offset = 0.0  // input offset value
) (
  `input_pwl vin,  // analog input
  output reg out   // slicer output
);

timeunit `DAVE_TIMEUNIT ;
timeprecision `DAVE_TIMEUNIT ;

`protect
//pragma protect 
//pragma protect begin

`get_timeunit     // get time unit and assign it to TU

PWLMethod pm=new; // class contains method for PWL signal

// wires
real __vin;   // sampled value of vdiff
real dTr;        // time step
event wakeup;     // event signal
initial out = 1'b0;

initial ->> wakeup;

// predict the firing time and compare 
always @(`pwl_event(vin) or wakeup) begin
  // comparison
  __vin = pm.eval(vin, `get_time) - offset;
  if (__vin>=0) out <= 1'b1;
  else out <= 1'b0; 
  // if vin-offset is heading to 0, schedule an event at the expected time
  if ((out && vin.b<0) || (~out && vin.b>0)) begin
    dTr = min(`DT_MAX,max(TU,abs(__vin/vin.b)));
    if (dTr < 100) ->> #(dTr/TU) wakeup;
  end
end

//pragma protect end
`endprotect

endmodule
