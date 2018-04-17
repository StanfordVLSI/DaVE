/****************************************************************

Copyright (c) 2018- Stanford University. All rights reserved.

The information and source code contained herein is the 
property of Stanford University, and may not be disclosed or
reproduced in whole or in part without explicit written 
authorization from Stanford University. Contact bclim@stanford.edu for details.

* Filename   : mProbo_macro.vh
* Author     : Byong Chan Lim (bclim@stanford.edu)
* Description: Include header for mProbo application

* Note       :

* Revision   :
  - 7/26/2016: First release

****************************************************************/


`ifdef AMS
  // get timeunit and assign it to TU
  `define get_timeunit real TU; initial $get_timeunit(TU);
  // get the current time in [second]
  `define get_time  $realtime*TU
  // get delay in Verilog timeunit
  `define delay(t) #((t)/TU)
  // import "DPI-C" pure function real sin(input real x);
`endif
//`define M_PI             3.14159265358979323846
//`define M_TWO_PI         6.28318530717958647652

// signal discipline
`ifndef AMS
  `define real real
  `define pwl pwl
  `define wreal real
  `define logic wire
  `define real_array(name,bw) real name[bw-1:0];
  `define pwl_array(name,bw) pwl name[bw-1:0];
`else
  `define real electrical
  `define pwl electrical
  `define wreal wreal
  `define logic wire
  `define real_array(name,bw) electrical [bw-1:0] name;
  `define pwl_array(name,bw) electrical [bw-1:0] name;
`endif

// real port
`ifdef VCS
  `define input_real input real
  `define output_real output real
`elsif NCVLOG
  `define input_real input var real
  `define output_real output var real
`elsif AMS
  `define input_real input 
  `define output_real output 
`endif

// ground in AMS

`define amsgnd(a) \
  `ifdef AMS \
    ground a; \
  `endif

