/****************************************************************

Copyright (c) 2018- Stanford University. All rights reserved.

The information and source code contained herein is the 
property of Stanford University, and may not be disclosed or
reproduced in whole or in part without explicit written 
authorization from Stanford University. Contact bclim@stanford.edu for details.

* Filename   : sar_adc_def.vh
* Author     : Byongchan Lim (bclim@stanford.edu)
* Description: Parameter definition of a SAR-ADC

* Note       :

* Revision   :
  - 7/26/2016: First release

****************************************************************/


////////////////////
// ADC configuration
////////////////////
`define ADC_BIT 11    // ADC resolution

//////
// S&H 
//////
`define ETOL_SNH 0.001 // error tolerance
`define R_SNH 500      // adc snh on-resistance
`define EPSPED 0.0     // signal-dependent pedestal error
`define VOSPED 0.0     // signal-independent pedestal error
`define TDPED  1e-15   // pedestal delay

////////////////////
// DAC configuration
////////////////////
// split-capacitor dac (Normalized)
`define BRIDGE_CAP 2
`define CAP_ARRAY  {1, 2, 4, 8, 16, 1, 2, 4, 8, 16, 30}
`define LSB_CAP_BW 5 
`define MSB_CAP_BW (`ADC_BIT-`LSB_CAP_BW)

`define C_DAC 1.44e-12 // DAC capacitance as ADC snh loading

/////////////////////////////////////
// SA Preamplifier
/////////////////////////////////////
`define PA_VOS 0.0     // input referred offset voltage
`define PA_ETOL_V 0.001   // resolution of voltage
`define PA_ETOL_I 1e-6   // resolution of current

/////////////////////////////////////
// Sense amplifier
/////////////////////////////////////
`define SA_TA  100e-12 // sampling aperture 
`define SA_VOS 0.0     // input referred offset voltage
`define SA_TAU 40e-12  // time constant of regeneration
`define SA_VTH 0.01    // threshold of quantizer

/////////////////////////////////////
// Parasitics & Electrical parameters
/////////////////////////////////////
