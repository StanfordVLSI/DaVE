/****************************************************************

Copyright (c) 2018- Stanford University. All rights reserved.

The information and source code contained herein is the 
property of Stanford University, and may not be disclosed or
reproduced in whole or in part without explicit written 
authorization from Stanford University. Contact bclim@stanford.edu for details.

* Filename   : pwl_saw.v
* Author     : Byongchan Lim (bclim@stanford.edu)
* Description: 
  It generates a saw-tooth wave.

* Note       :

* Revision   :
  - 7/26/2016 : First release
  - 12/11/2016: 
    : Bug fix) DT_MAX was set to 2.0**31*TU which could
      be small when timeunit is small. So, it is increased to 2**61
      in mLingua_pwl.vh
    : initial statement is rewritten to understand it easier

****************************************************************/


module pwl_saw #(
  parameter real offset = 0.0, // dc offset value
  parameter real pk2pk  = 1.0, // peak-to-peak value
  parameter real freq   = 1e3, // frequency
  parameter real phase  = 0.0  // initial phase in degree [0, 360)
) (
  `output_pwl out  // saw-tooth output
);

timeunit `DAVE_TIMEUNIT ;
timeprecision `DAVE_TIMEUNIT ;

`protect
//pragma protect 
//pragma protect begin

`get_timeunit // get timeunit in sec and assign it to the variable 'TU'
PWLMethod pm=new;

real dTr;
real abs_slope; // absolute value of the signal slope
real toffset;   // initial time offset due to phase parameter
real voffset;   // initial output offset due to phase parameter
real out0;
reg flag_slope;  // slope flag ('0' for positive and '1' for negative)

event wakeup;
real t0;

initial begin
  assert (phase >=0 && phase <360) else $error("phase parameter should be greater than/equal to 0, and less than 360 [deg]");

  abs_slope = pk2pk*freq/0.5;
  if (phase>=0.0 && phase<90.0) begin
    flag_slope = 1'b0;
    out0 = 0.5*pk2pk*phase/90.0 + offset;
    toffset = 0.25/freq*phase/90.0;
    dTr = 0.25/freq-toffset;
  end
  else if (phase>=90.0 && phase<270.0) begin
    flag_slope = 1'b1;
    out0 = 0.5*pk2pk - pk2pk*(phase-90.0)/180.0 + offset;
    toffset = 0.25/freq + 0.5/freq*(phase-90.0)/180.0;
    dTr = 0.75/freq-toffset;
  end
  else if (phase>=270.0 && phase<360.0) begin
    flag_slope = 1'b0;
    out0 = -0.5*pk2pk + 0.5*pk2pk*(phase-270.0)/90.0 + offset;
    toffset = 0.75/freq + 0.25/freq*(phase-270.0)/90.0;
    dTr = 1.25/freq-toffset;
  end
  out = pm.write(out0, flag_slope? abs_slope*-1.0 : abs_slope, 0.0);
  dTr = min(`DT_MAX,dTr);
  ->> `delay(dTr) wakeup;
end

always @(wakeup) begin
  t0 = `get_time;
  out0 = pm.eval(out,t0);
  flag_slope = ~flag_slope;
  out = pm.write(out0, flag_slope? abs_slope*-1:abs_slope, t0);
  dTr = 0.5/freq;
  ->> `delay(dTr) wakeup;
end

//pragma protect end
`endprotect

endmodule
