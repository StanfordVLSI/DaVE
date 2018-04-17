/****************************************************************

Copyright (c) 2018- Stanford University. All rights reserved.

The information and source code contained herein is the 
property of Stanford University, and may not be disclosed or
reproduced in whole or in part without explicit written 
authorization from Stanford University. Contact bclim@stanford.edu for details.

* Filename   : txf_vco.v
* Author     : Byongchan Lim (bclim@stanford.edu)
* Description: Transfer curve (f_VCO vs. control voltage input) of
  a ring oscillator.

* Note       :

* Revision   :
  - 7/26/2016: First release

****************************************************************/

module txf_vco #(
  parameter real vh = 1.0,  // upper bound of vreg [V]
  parameter real vl = 0.0,  // lower bound of vreg [V]
  parameter real vco0 = 1.5e9, // freq offset [Hz]
  parameter real vco1 = 1e9    // freq gain [Hz/V]
) (
  `input_pwl in,
  `output_pwl out
);

`get_timeunit
PWLMethod pm=new;
pwl in_prev;
event wakeup;
//reg wakeup=1'b0;
integer index;
real t;
real in_value;
real slope;
real scale;
real dTr;
real out_cur;
time dT=1;
time dTm, t_prev;
reg event_in=1'b0;
//pragma protect end
`endprotect

///////////////////////////////////////
// LUT of DC Transfer Curve
///////////////////////////////////////
parameter integer LUTSize=3;
real lutx[LUTSize-1:0]; // x-axis
real luty[LUTSize-1:0]; // gain 
real ly[LUTSize-1:0];   // offset to handle when luty[j]==0
initial begin

lutx[0] = vl-0.1; luty[0] = 0.0; ly[0] = vco0; 
lutx[1] = vl; luty[1] = vco1; ly[1] = vco0; 
lutx[2] = vh; luty[2] = 0.0; ly[2] = vco0+vco1*(vh-vl);
end
///////////////////////////////////////


`protect
//pragma protect
//pragma protect begin

always @(`pwl_event(in) or wakeup) begin
  dTm = $realtime - t_prev;
  event_in = `pwl_check_diff(in, in_prev);
  if (dT==dTm || event_in) begin
    if (event_in) in_prev = in;
    t = `get_time;              // current time
    in_value = pm.eval(in, t);  // current value
    slope = in.b;               // slope of the input
  
    // input changes and the current index is NOT valid
    index = find_region_txf_vco(in_value);  // update index
    // evaluate the output at current time
    scale = luty[index];            // get scale(gain) from the LUT
    out_cur = ly[index]+scale*(in_value-lutx[index]);
    out = pm.write(out_cur, scale*in.b, t); 
    // schedule next event if necessary
    // calculate when the input will hit the inflection point.
    dTr = calculate_dx_txf_vco(in_value, slope, index); 
    if (dTr > TU && dTr < 10e-9) begin
      dT = time'(dTr/TU);
      ->> #(dT) wakeup; // schedule an event after dT
    end
    t_prev = $realtime;
  end
end


// for given value, find the index of LUT (region)
function integer find_region_txf_vco (real value);
int idx[$];
int i;
begin
  if (value < lutx[1]) return 0;
  else if (value >= lutx[LUTSize-1]) return LUTSize-1;
  else begin
    `ifdef VCS
      idx = lutx.find_index with (item > value);
      return idx[0]-1;
    `elsif NCVLOG
      for(i=0;i<LUTSize;i++) if (lutx[i] > value) return i-1;
    `endif
  end
end
endfunction

// calculate the next event where inflection of transfer curve 
// for given input (value, slope)
function real calculate_dx_txf_vco(real value, real slope, integer index);
real nxt_value;
real sgn_sl;
real dx;
begin
  sgn_sl = sgn(slope);
  if (sgn_sl == 0) return 0.0;
  if (value >= lutx[LUTSize-1] && sgn_sl > 0) return 0.0;
  if (value <= lutx[0] && sgn_sl < 0) return 0.0;
  // the first two if handle boundary condition
  if (value > lutx[LUTSize-1]) begin
    dx = (lutx[LUTSize-1]-value)/slope;
    if (dx < TU) return TU;
    else return dx;
  end
  else if (value < lutx[0]) begin
    dx = (lutx[0]-value)/slope;
    if (dx < TU) return TU;
    else return dx;
  end
  if (sgn_sl > 0) nxt_value = lutx[index+1];
  else nxt_value = lutx[index];
  dx = (nxt_value-value)/slope;
  if (dx < TU) return TU;
  else return dx;
end
endfunction

endmodule
