/****************************************************************

Copyright (c) 2018- Stanford University. All rights reserved.

The information and source code contained herein is the 
property of Stanford University, and may not be disclosed or
reproduced in whole or in part without explicit written 
authorization from Stanford University. Contact bclim@stanford.edu for details.

* Filename   : sar_adc.v
* Author     : Byongchan Lim (bclim@stanford.edu)
* Description: SAR-ADC top

* Note       :

* Revision   :
  - 7/26/2016: First release

****************************************************************/


module sar_adc(
  `input_pwl vdd,             // supply
  `input_pwl vss,             // ground
  input clk,                  // system clock
  input rstb,                 // system reset
  `input_pwl vinp,            // (+) input signal
  `input_pwl vinn,            // (-) input signal
  `input_pwl vcm,             // common-mode voltage of DAC
  `input_pwl vrefp,           // (+) reference voltage
  `input_pwl vrefn,           // (-) reference voltage
  `input_pwl ibiasn,           // bias current for pre-amp in a comparator
  output [`ADC_BIT-1:0] dout, // carefule about bus order
  output ready
);

pwl vinp_to_dac, vinn_to_dac;
pwl v_dacoutp, v_dacoutn;

wire sample;
wire cmp_out;
wire [`ADC_BIT-1:0] data_to_dac;

// pseduo differential sample-hold circuit
adc_snh adcsnh_p (.vdd(vdd), .vss(vss), .sample(sample), .vi(vinp), .vo(vinp_to_dac));
adc_snh adcsnh_n (.vdd(vdd), .vss(vss), .sample(sample), .vi(vinn), .vo(vinn_to_dac));

// SAR DAC
sar_dac xdac( .vinp(vinp_to_dac), .vinn(vinn_to_dac), .vcm(vcm), .vrefp(vrefp), .vrefn(vrefn), .din(data_to_dac), .v_dacoutp(v_dacoutp), .v_dacoutn(v_dacoutn));

// clocked comparator
comparator xcomp (.vdd(vdd), .vss(vss), .vinp(v_dacoutp), .vinn(v_dacoutn), .ibias(ibiasn), .pwdn(~rstb), .clk(clk), .dout(cmp_out), .doutb());

// storing DAC switch status
sar_logic xsarlog (.clk(clk), .rstb(rstb), .din(cmp_out), .ready(ready), .sample(sample), .dac_out(data_to_dac), .dout(dout));

endmodule
