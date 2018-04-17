/****************************************************************

Copyright (c) 2018- Stanford University. All rights reserved.

The information and source code contained herein is the 
property of Stanford University, and may not be disclosed or
reproduced in whole or in part without explicit written 
authorization from Stanford University. Contact bclim@stanford.edu for details.

* Filename   : txline.v
* Author     : Byongchan Lim (bclim@stanford.edu)
* Description: 
  It models a lossless transmission line with resistive termination.

    vin----^^rs^^----|-----Z0,TD----|----|
                                         rt
                                         |
                                        gnd 

* Note       :

* Revision   :
  - 7/26/2016: First release

****************************************************************/

module txline #(
// parameters here
  parameter real Z0= 50.0,     // characteristic impedance
  parameter real TD= 0.1e-9,   // propagation delay 
  parameter real etol= 0.001,  // error tolerance to stop creating events
  parameter real tr= 1e-15,    // transition time (real to pwl), debugging purpose
  parameter integer NREFLECT=100000 // number of reflections to care about, use this param if you want to limit the reflection than using etol param
) (
// I/Os here
  `input_real rs,   // termination resistor @ transmitter
  `input_real rt,   // termination resistor @ receiver
  `input_real vin,  // driving voltage @ transmitter
  `output_pwl vout // voltage @ receiver
);

timeunit `DAVE_TIMEUNIT ;
timeprecision `DAVE_TIMEUNIT ;

`protect
//pragma protect 
//pragma protect begin

`get_timeunit
PWLMethod pm=new;

// write your code
localparam integer NBUF=1;    // number of internal buffer

real rho_s, rho_t;  // reflection coefficient at Tx and Rx
real vin_prev;  
real d_vin;
real vo[0:NBUF-1];
real vout_r;
real tmpval;
int idx_vo=0;

// reflection coefficient
initial begin
  rho_s = get_rho(rs,Z0);
  rho_t = get_rho(rt,Z0);
end

always @(rs) rho_s = get_rho(rs,Z0);
always @(rt) rho_t = get_rho(rt,Z0);

// calculate reflected voltages and schedule events
always @(vin) begin
  if ($time==0) begin
    tmpval = 0;
    for (int j=0;j<NREFLECT;j++) tmpval += rho_t**j*rho_s**j;  
    vout_r = vin*rs/(rs+Z0)*(1+rho_s)*tmpval;
    vin_prev = vin;
  end
  else begin
    d_vin = (vin - vin_prev)*rs/(rs+Z0)*(1+rho_s);
    if (idx_vo==NBUF) idx_vo = 0;
    for (int j=0;j<NREFLECT;j++) begin
      tmpval = d_vin*rho_t**j*rho_s**j/(1-rho_t*rho_s);
      if (abs(tmpval) > etol) // sum of remaining terms > etol
        vo[idx_vo] <= `delay(TD*(2*j+1)) d_vin*rho_t**j*rho_s**j;
      else begin // sum of remaining terms < etol
        vo[idx_vo] <= `delay(TD*(2*j+1)) tmpval;
        break;
      end
    end
    vin_prev = vin;
    idx_vo++;
  end
end

/// create output waveform
genvar i;
generate
  for(i=0;i<NBUF;i++)
    always @(vo[i]) vout_r += vo[i];
endgenerate

real2pwl #(.tr(tr)) xr2p (.in(vout_r), .out(vout));

// function to calculate reflection coefficient
function real get_rho(input real rterm, input real z0);
begin
  return (rterm-z0)/(rterm+z0);
end
endfunction

//pragma protect end
`endprotect

endmodule

