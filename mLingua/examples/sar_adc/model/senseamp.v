/****************************************************************

Copyright (c) 2018- Stanford University. All rights reserved.

The information and source code contained herein is the 
property of Stanford University, and may not be disclosed or
reproduced in whole or in part without explicit written 
authorization from Stanford University. Contact bclim@stanford.edu for details.

* Filename   : senseamp.v
* Author     : Byongchan Lim (bclim@stanford.edu)
* Description: Clocked sense amplifier in a comparator. It consists of
  regenerative amplifier latch and R-S latch.

* Note       :
  - Sampling aperture: Here we use a simple model. For given ta 
  (sampling aperature time), we sample the analog input with a 
  delayed clock where the delay is ta/2.0

  - regeneration time calculation: We use the following formula 
  for regenerative process V(t) = v0*exp(t/tau) where tau = Cl/Gm
  The latch output will flip when V(t) researches Vth.

  - Hysteresis effect (reset transient) is not modeled yet.

* Revision   :
  - 7/26/2016: First release

****************************************************************/


module senseamp #(
  parameter real ta   = `SA_TA,   // sampling aperture 
  parameter real vos0  = `SA_VOS,  // input referred offset voltage
  parameter real tau = `SA_TAU,   // time constant of regeneration
  parameter real Vth = `SA_VTH    // threshold of quantizer

) (
  `input_pwl vdd,        // power supply, does nothing here yet
  `input_pwl vss,        // ground, does nothing here yet
  `input_pwl vinp, vinn, // two analog inputs to be compared
  input clk,             // sampling clock (rising edge)
  output dout, doutb     // output of this comparator
);

`get_timeunit
PWLMethod pm=new;

reg cout=1'b1, coutb=1'b1;  // R-S latch input
//reg clke_latch=1'b0;        // delayed clock of clk to model sampling aperature
reg [1:0] state = '0;  // '00': reset, '01': regeneration, '10': decision made
pwl vin;
real t0;
real v0;
real dTr;
real tdiff;
event wakeup;

pwl vos = '{vos0,0,0};

/////////////////////
// Input offset 
/////////////////////
pwl_add3 xiadd (.in1(vinp), .in2(vinn), .in3(vos), .scale1(1.0), .scale2(-1.0), .scale3(1.0), .out(vin));

/////////////////////
// regenerative latch
/////////////////////

// reset phase
always @(negedge clk) begin
  state <= 2'b0;
  cout <= 1'b0;
  coutb <= 1'b0;
end

// sampling phase
always @(posedge clk) begin
  state <= 2'b01;
  t0 = `get_time;
  v0 = pm.eval(vin, t0+ta); // initial voltage at regeneration
  dTr = get_comp_delay(v0); // regeneration delay
  ->> `delay(dTr) wakeup;
end

// decision or reschedule phase
always @(wakeup) 
  if (state == 2'b01) begin
    tdiff = `get_time - (t0+dTr);
    if (tdiff >= 0.0) begin // voltage is large enough to flip states
      state = 2'b10;
      cout  <= (v0 >= 0)? 1'b1:1'b0;
      coutb <= (v0 >= 0)? 1'b0:1'b1;
    end
    else
      ->> `delay(max(TU,-1.0*tdiff)) wakeup;
  end

/////////////////////
// R-S latch
/////////////////////
rslatch_nor xlat (.setb(coutb), .resetb(cout), .q(dout), .qb(doutb));

///////////////////////////////////////////////////
// calculate expected delay of regeneration process
///////////////////////////////////////////////////
function real get_comp_delay;
`input_real v0;
real calcT;
begin
  calcT = tau*log(Vth/abs(v0));
  return min(max(TU,calcT),1.0);
end
endfunction

endmodule
