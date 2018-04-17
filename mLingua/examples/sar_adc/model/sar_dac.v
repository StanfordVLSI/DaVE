/****************************************************************

Copyright (c) 2018- Stanford University. All rights reserved.

The information and source code contained herein is the 
property of Stanford University, and may not be disclosed or
reproduced in whole or in part without explicit written 
authorization from Stanford University. Contact bclim@stanford.edu for details.

* Filename   : sar_dac.v
* Author     : Byongchan Lim (bclim@stanford.edu)
* Description: Capacitive D/A converter in a SAR-ADC

* Note       :

* Revision   :
  - 7/26/2016: First release

****************************************************************/


module sar_dac (
  `input_pwl vinp,    // ADC input 
  `input_pwl vinn,    // pseudo (-) ADC input for differential op.
  `input_pwl vcm,     // common-mode voltage input
  `input_pwl vrefp,   // (+) reference voltage
  `input_pwl vrefn,   // (-) reference voltage
  input [`ADC_BIT-1:0] din, // switch control input
  `output_pwl v_dacoutp, v_dacoutn  // output to comparator
);

`get_timeunit
PWLMethod pm=new;

parameter real c_bridge = `BRIDGE_CAP;

real cap_array[`ADC_BIT] = `CAP_ARRAY;
real ctot;      // total effective capacitance
real ctot_lsb;  // total lsb bank capacitance
real ctot_msb;  // total msb bank capacitance
real ceff_lsb;  // effective capacitance of lsb cap bank to msb bank
real c_wgt[`ADC_BIT]; // capacitance ratio of each bit to total capacitance
real v_dacout_a, v_dacout_b;  // temporary offset, slope of dac output voltage

pwl vin_d;  // difference between vinp and vinn
pwl vref_d; // difference between vrefp and vrefn
pwl v_dac_od;
real v_dacoutb_a, v_dacoutb_b;

// convert split-cap D/A to its effective binary capacitor array at t=0-
// This will provide a weight of each binary output
initial begin
  ctot_lsb = cap_array[0];
  for (int j=0;j<`LSB_CAP_BW;j++) begin
    ctot_lsb += cap_array[j];
  end
  for (int j=`LSB_CAP_BW;j<`ADC_BIT;j++) begin
    ctot_msb += cap_array[j];
  end
  ceff_lsb = (c_bridge*ctot_lsb)/(c_bridge+ctot_lsb);

  ctot = ctot_msb + ceff_lsb;

  for (int j=0;j<`LSB_CAP_BW;j++) begin
    c_wgt[j] = cap_array[j]/ctot_lsb*ceff_lsb/ctot/2.0;
  end
  for (int j=`LSB_CAP_BW;j<`ADC_BIT;j++) begin
    c_wgt[j] = cap_array[j]/ctot;
  end
end    

// take the differences (vinp-vinn), (vrefp-vrefn)
pwl_add2 xadd1 ( .in1(vinp), .in2(vinn), .scale1(1.0), .scale2(-1.0), .out(vin_d)); 
pwl_add2 xadd2 ( .in1(vrefp), .in2(vrefn), .scale1(1.0), .scale2(-1.0), .out(vref_d)); 

real tmp;
// calculate dac output voltage
always @(`pwl_event(vin_d) or `pwl_event(vref_d) or din) begin
  v_dacout_a = vin_d.a;
  v_dacout_b = vin_d.b;
  v_dacoutb_a = -vref_d.a/2;
  v_dacoutb_b = -vref_d.b/2;
  for (int j=0;j<`ADC_BIT;j++) begin
    tmp = din[j]? 1.0:0.0;
    v_dacoutb_a += vref_d.a*c_wgt[j]*tmp;
    v_dacoutb_b += vref_d.b*c_wgt[j]*tmp;
  end
  v_dac_od = pm.write(v_dacout_a-v_dacoutb_a, v_dacout_b-v_dacoutb_b, `get_time);
end

pwl_add2 xoutp (.in1(vcm), .in2(v_dac_od), .scale1(1.0), .scale2(0.5), .out(v_dacoutp));
pwl_add2 xoutn (.in1(vcm), .in2(v_dac_od), .scale1(1.0), .scale2(-0.5), .out(v_dacoutn));

endmodule 
