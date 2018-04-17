/****************************************************************

Copyright (c) #YEAR# #LICENSOR#. All rights reserved.

The information and source code contained herein is the 
property of #LICENSOR#, and may not be disclosed or
reproduced in whole or in part without explicit written 
authorization from #LICENSOR#.

* Filename   : test.v
* Author     : Byongchan Lim(bclim@stanford.edu)
* Description:

* Note       :
  - virtual test clock name: "virclk"
  - list of basic tasks
    a. repeat_virclk(N);  // repeat N cycles of "virclk"
    b. finish_sim;        // finish simulation
  - `INFO(""); // display information
  - $sformat(string_var, formatted string); // assign formatted string to a variable

* Revision   :

****************************************************************/

`include "mLingua_pwl.vh"
// `include "YOUR_OWN_PARAM_HEADER.v"

module test;

//timeunit 1fs;
//timeprecision 1fs;

`get_timeunit     // assign timeunit to "TU"
PWLMethod pm=new; // instantiation of pwl class 

///////////////////////////
// parameters if any
///////////////////////////
parameter real PERIOD_VIRCLK = 10e-9; // period of virtual clock ("virclk")

///////////////////////////
// wires, assignment
///////////////////////////
wire virclk;  // virtual clock for test


///////////////////////////
// user instances
///////////////////////////


///////////////////////////
// user tasks
///////////////////////////


///////////////////////////
// utility instances & tasks
///////////////////////////

clock #(.freq(1/PERIOD_VIRCLK)) uVIRCLK (.ckout(virclk)); // virtual clock generation

task repeat_virclk; // wait for N virclk clock cycles
input integer N;
begin
  repeat (N) @(posedge virclk);
end
endtask

task finish_sim;  // finish simulation
  $finish(2);
endtask

`run_wave  // macro for dumping signal waveforms

endmodule

