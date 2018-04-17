/****************************************************************

Copyright (c) 2018- Stanford University. All rights reserved.

The information and source code contained herein is the 
property of Stanford University, and may not be disclosed or
reproduced in whole or in part without explicit written 
authorization from Stanford University. Contact bclim@stanford.edu for details.

* Filename   : sar_logic.v
* Author     : Byongchan Lim (bclim@stanford.edu)
* Description: SAR-ADC controller

* Note       :

* Revision   :
  - 7/26/2016: First release

****************************************************************/


module sar_logic ( 
  input clk, // clock input
  input rstb, // rstb=1 to perform conversion
  input din, // from comparator
  output reg ready, // ready=1 when conversion data is ready
  output sample, // to S&H circuit
  output [`ADC_BIT-1:0] dac_out, // to DAC switches
  output reg [`ADC_BIT-1:0] dout // ADC output
);

reg [1:0] state; // current state in state machine
reg [`ADC_BIT-1:0] mask; // bit to test in binary search
reg [`ADC_BIT-1:0] pout; // hold partially converted result

// state assignment
parameter sWait=0, sSample=1, sConv=2, sDone=3;

always @(posedge clk or negedge rstb) begin
  if (!rstb) begin
    state <= sWait; // reset 
    pout <= '0;
    mask <= '0;
  end
  else 
    case (state) // choose next state in state machine
      sWait : state <= sSample;
      sSample :
      begin // start new conversion so
        state <= sConv; // enter convert state next
        mask <= {1'b1,{(`ADC_BIT-1){1'b0}}}; // reset mask to MSB only
        pout <= '0; // clear result
      end
      sConv :
      begin
        // set bit if comparitor indicates input larger than
        // value currently under consideration, else leave bit clear
        if (din) pout <= pout | mask;
          // shift mask to try next bit next time
        mask <= mask>>1;
        // finished once LSB has been done
        if (mask[0]) state <= sDone;
      end
      sDone : state <= sSample;
    endcase
end

assign sample = state==sSample; // drive sample and hold
assign dac_out = pout | mask; // (result so far) OR (bit to try)

always @(posedge clk or negedge rstb) begin
  if (!rstb) begin
    dout <= '0;
    ready <= 1'b0;
  end
  else 
    if (state==sDone) begin
      dout <= pout;  
      ready <= 1'b1;
    end
    else
      ready <= 1'b0;
end

endmodule
