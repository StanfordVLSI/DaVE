/****************************************************************

Copyright (c) 2018- Stanford University. All rights reserved.

The information and source code contained herein is the 
property of Stanford University, and may not be disclosed or
reproduced in whole or in part without explicit written 
authorization from Stanford University. Contact bclim@stanford.edu for details.

* Filename   : digital_lf.v
* Author     : Byongchan Lim (bclim@stanford.edu)
* Description: digital loop filter in Rx PLL

* Note       :
  - Behavioral model for simplicity. In a real implementation, 
    you will use a fixed-point opearations for this filter. 

* Revision   :
  - 7/26/2016: First release

****************************************************************/


`protect
//pragma protect 
//pragma protect begin
module digital_lf #(
    parameter integer Nbit = 14,   // width of out
    parameter integer Nl = 4,           // loop filter latency
    parameter [Nbit-1:0] offset=14'b10000000000000, // control offset
    parameter real Kp=256,              // proportional gain
    parameter real Ki=1                 // integral gain
)(
    input clk,                     // triggering clock
    input up,                      // up signal from pd/pfd
    input dn,                      // down signal from pd/pfd
    output reg[Nbit-1:0] out       // output signal
);

`get_timeunit

// variables
reg [Nl-1:0] up_d='0, dn_d='0;
real int_path=0, pro_path=0;

// initialize out
initial out = offset;
    
always @(posedge clk) begin
  up_d=up_d<<1; up_d[0]=up;
  dn_d=dn_d<<1; dn_d[0]=dn;
  pro_path=Kp*(1.0*up_d[Nl-1]-1.0*dn_d[Nl-1]);
  int_path=int_path+Ki*(1.0*up_d[Nl-1]-1.0*dn_d[Nl-1]);
  out=offset+pro_path+int_path;
end

endmodule
//pragma protect end
`endprotect
