/****************************************************************

Copyright (c) 2018- Stanford University. All rights reserved.

The information and source code contained herein is the 
property of Stanford University, and may not be disclosed or
reproduced in whole or in part without explicit written 
authorization from Stanford University. Contact bclim@stanford.edu for details.

* Filename   : linear_ota_cloop.v
* Author     : Byongchan Lim (bclim@stanford.edu)
* Description: Closed-loop linear OTA with single-ended output

* Note       :
  - "inn" should be connected to "feed" externally to avoid assertion
    message
  - Neither gain compression nor slew is incorporated
  - Dominant pole approximation for dynamic behavior
  - power supply noise is not yet incorporated

* Revision   :
  - 7/26/2016: First release

****************************************************************/

module linear_ota_cloop #(
  parameter real etol = 0.001,  // error tolerance of a filter operation
  parameter pwrnoise = 1'b0     // enable power supply noise
) (
  `input_pwl vdd,   // power supply for power noise simulation
  `input_real av,   // open-loop dc gain
  `input_real fp,   // open-loop pole in Hz
  `input_real vos,  // input referred static offset voltage
  `input_real ff,   // feedback factor
  input pd,         // enable power down (act. Hi), pulled Lo when unconnected
  `input_pwl pd_val,// output value when pd is Hi
  `input_pwl in,    // input
  `input_pwl inn,   // negative input to ota for checking connection
  `output_pwl out,  // output
  `output_pwl feed  // virtual feedback node to (-) input of an error amp.
);

timeunit `DAVE_TIMEUNIT ;
timeprecision `DAVE_TIMEUNIT ;

`get_timeunit
PWLMethod pm=new;

pulldown(pd); // pull-down of pd signal
//----- BODY STARTS HERE -----

//----- SIGNAL DECLARATION -----

pwl v_od; // differential inputs
pwl out1; // process pd
pwl PWL1 = `PWL1; // '{1.0,0,0}
logic reset=1;  // for initialization

//----- FUNCTIONAL DESCRIPTION -----

initial #5 reset = 0;


// diff sense considering input referred offset
pwl_add2 uIDIFF (.in1(in), .in2(PWL1), .scale1(av/(1.0+av*ff)), .scale2(vos*av/(1.0+av*ff)), .out(v_od)); // take static offset

pwl_filter_real_w_reset #(.etol(etol), .en_filter(1'b1), .filter(0)) uFILTER (.fp1(fp*(1.0+av*ff)), .in(v_od), .out(out1), .reset(reset), .fp_rst(100e12), .in_rst(v_od) ); // 1st order LPF 

assign out = pd? pd_val : out1;

pwl_vga uVGA (.in(out), .scale(ff), .out(feed)); // virtual feedback node

// assertion: check if "inn" is externally connected to "feed" 
string msg;
always @(`pwl_event(feed)) begin
  $sformat(msg, "[%m] At t=%.3e [sec], Check connection between inn and feed terminals (inn(%e)!=feed(%e)", $time*TU, pm.eval(inn,`get_time), pm.eval(feed,`get_time));
  #1;
  assert (inn == feed) else $warning(msg);
end

endmodule
