/****************************************************************

Copyright (c) 2018- Stanford University. All rights reserved.

The information and source code contained herein is the 
property of Stanford University, and may not be disclosed or
reproduced in whole or in part without explicit written 
authorization from Stanford University. Contact bclim@stanford.edu for details.

* Filename   : vsin_real.v
* Author     : Byongchan Lim (bclim@stanford.edu)
* Description: It outputs a sine wave in real (PWC).

* Note       :

* Revision   :
  - 7/26/2016: First release

****************************************************************/

`timescale `DAVE_TIMEUNIT / `DAVE_TIMEUNIT

///////////
`ifndef AMS // NOT AMS
///////////


module vsin_real #(
  parameter integer Ns = 50,  // oversampling rate to get pretty waveforms
  parameter real amplitude = 1.0, // amplitude of a signal
  parameter real dc = 0.5,        // dc offset
  parameter real freq = 1.0,      // signal frequency
  parameter real phase = 0        // in degree
  ) (`output_real vout, voutb);

localparam real ph_rad = `M_TWO_PI*phase/180.0;  // phase in radian

reg sclk=1'b0;
real t0;

always sclk = `delay(1.0/(Ns/freq) ~sclk;

always @(sclk) begin
  t0 = `get_time;
  vout = dc + amplitude*sin(`M_TWO_PI*freq*t0 + ph_rad);
  voutb = dc - amplitude*sin(`M_TWO_PI*freq*t0 + ph_rad);
end

endmodule


///////////
`else // AMS
///////////


`include "disciplines.vams"
`include "constants.vams"

`timescale 1fs/1fs
module vsin_real (vout, voutb);

output  vout, voutb;
voltage vout, voutb;

parameter integer Ns = 50; // oversampling rate to get pretty waveforms
parameter real amplitude = 1.0 from [0:inf); // amplitude of a signal
parameter real dc = 0.5;  // dc offset
parameter real freq = 1.0 from (0:inf); // signal frequency
parameter real phase = 0.0;  // in degree

real out, outb;
integer delay_qnt;
real delay_step, qnt_err;
real TU=1e-15;

parameter real ph_rad = `M_TWO_PI*phase/180.0; // phase in radian

initial begin
    qnt_err = ph_rad/(`M_TWO_PI*freq*TU);
end

always begin
    out = amplitude * sin(`M_TWO_PI*freq*$abstime + ph_rad) + dc;
    outb = -1.0 * amplitude * sin(`M_TWO_PI*freq*$abstime + ph_rad) + dc;

    delay_step = 1.0/(Ns*freq*TU);
    delay_qnt = delay_step + qnt_err;
    #(delay_qnt) qnt_err = delay_step - delay_qnt;
end

analog begin
    V(vout) <+ transition(out, 0, 1.0/(Ns*freq));
    V(voutb) <+ transition(outb, 0, 1.0/(Ns*freq));
end

endmodule


///////////
`endif
///////////
