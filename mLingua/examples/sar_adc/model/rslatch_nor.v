/****************************************************************

Copyright (c) 2018- Stanford University. All rights reserved.

The information and source code contained herein is the 
property of Stanford University, and may not be disclosed or
reproduced in whole or in part without explicit written 
authorization from Stanford University. Contact bclim@stanford.edu for details.

* Filename   : rslatch_nor.v
* Author     : Byongchan Lim (bclim@stanford.edu)
* Description: NOR-type RS latch.

* Note       :

* Revision   :
  - 7/26/2016: First release

****************************************************************/


module rslatch_nor(
  input setb, resetb,
  output reg q, qb
);

always @(setb or resetb) begin
  case({setb,resetb})
    2'b01: begin
            q  <= 1'b1;
            qb <= 1'b0;
           end
    2'b10: begin
            q  <= 1'b0;
            qb <= 1'b1;
           end
    2'b11: begin
            $display("%t, Forbidden input ('11') for a NOR RS latch", $realtime);
            q  <= 1'b1;
            qb <= 1'b1;
           end
  endcase
end

endmodule

