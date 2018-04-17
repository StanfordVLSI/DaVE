/****************************************************************

Copyright (c) 2018- Stanford University. All rights reserved.

The information and source code contained herein is the 
property of Stanford University, and may not be disclosed or
reproduced in whole or in part without explicit written 
authorization from Stanford University. Contact bclim@stanford.edu for details.

* Filename   : prbs16.v
* Author     : Byongchan Lim (bclim@stanford.edu)
* Description:
  - Pseudo random bit sequence (run length of 16) generator.

* Note       :

* Revision   :
  - 7/26/2016: First release
  
****************************************************************/

module prbs16 (
  input clk,  // clock
  input rst,  // reset (act. high)
  output out  // output stream
);

timeunit `DAVE_TIMEUNIT ;
timeprecision `DAVE_TIMEUNIT ;

reg [15:0] sr='1;

always @(posedge clk or posedge rst) begin
  if(rst) sr = '1;
  else begin
    sr[15:1] <= sr[14:0];
    sr[0] <= sr[15] ^ sr[14] ^ sr[12] ^ sr[3];
  end
end

assign out = sr[6];

endmodule
