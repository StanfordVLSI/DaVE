/****************************************************************

Copyright (c) 2018- Stanford University. All rights reserved.

The information and source code contained herein is the 
property of Stanford University, and may not be disclosed or
reproduced in whole or in part without explicit written 
authorization from Stanford University. Contact bclim@stanford.edu for details.

* Filename   : ota.v
* Author     : Byongchan Lim (bclim@stanford.edu)
* Description: Operational transconductance amplifier

* Note       :

* Revision   :
  - 7/26/2016: First release

****************************************************************/


module ota #(
  parameter logic en_lcc = 1'b1, // enable limit cycle correction
  parameter gain_error = 0.001,   // 1-A/(1+A*f) for limit cycle only
  parameter real etol = 0.001,  // error tolerance (output)
  parameter real etol_i = 1e-6, // error tolerance (bias current)
  parameter real vos = 0,       // input referred offset voltage
  parameter real beta = 0.005,   // beta of differential input transistor
  parameter real vic0 = 0.4,    // common-mode voltage input offset for Itail calculation
  parameter real lambda = 0.4,  // Itail = ibias + ibias*lambda*(vic-vic0)
  parameter real Rout = 5e6,    // output impendance
  parameter real Cout = 1e-12,  // dominant pole = rout*Cout
  parameter real dvo_hi = 0.3,  // max(V(out)) = vdd - dvo_hi
  parameter real dvo_low = 0.3   // max(V(out)) = vss + dvo_low

) (
  `input_pwl vdd, vss,   // 
  `input_pwl inp, inn,   // differential inputs
  `input_pwl ibias,     // ibias current input to nmos diode
  `output_pwl out       // output 
);

parameter real wp = 1/Rout/Cout; // pole frequency in radian

`protect
//pragma protect 
//pragma protect begin

`get_timeunit
PWLMethod pm=new;
real Av;
real ibias_r, itail_r;
real itail_sqrt;
real sqrt_beta;


initial sqrt_beta = sqrt(beta); 

pwl v_id, v_ic; // differential and common-mode inputs
pwl v_id_lim;   // limited v_id 
pwl vid_max, vid_min; // max/min of v_id for slewing 
pwl vo;
pwl vo_max, vo_min;
pwl itail;  // tail current
pwl ib_prop;
pwl vo_filtered;
pwl vo_lim;
wire freeze;

pwl unity_scale = '{1,0,0};
pwl dvoh = '{dvo_hi,0,0};
pwl dvol = '{dvo_low,0,0};
pwl vos_pwl = '{vos,0,0};
pwl vic0_pwl = '{vic0,0,0};

// diff/cm sense & count input referred offset
pwl_add3 xidiff (.in1(inp), .in2(inn), .in3(vos_pwl), .scale1(1.0), .scale2(-1.0), .scale3(1.0), .out(v_id));
pwl_add2 xicm (.in1(inp), .in2(inn), .scale1(0.5), .scale2(0.5), .out(v_ic));

// tail current on v_ic
pwl_add2 xicm0 (.in1(v_ic), .in2(vic0_pwl), .scale1(lambda), .scale2(-1.0*lambda), .out(ib_prop));
pwl2real #(.dv(etol_i)) xp2r1 (.in(ibias), .out(ibias_r));
always @(ibias_r or `pwl_event(ib_prop)) begin
  itail_r = ibias_r*(1+pm.eval(ib_prop,`get_time));
  itail_sqrt = sqrt(itail_r);
end

// calculating voltage gain an0
// 1. voltage gain Av
// 2. Vid,max(min): range of differential input voltage which doesn't cause compression 
always @(itail_sqrt) begin
  Av = itail_sqrt*sqrt_beta/2*Rout;
  vid_max = pm.write(itail_sqrt*1.414/sqrt_beta,0,`get_time);
  vid_min = pm.write(-itail_sqrt*1.414/sqrt_beta,0,`get_time);
end

// Vod,max(min) calculation
pwl_add2 xvomax (.in1(vdd), .in2(dvoh), .scale1(1.0), .scale2(-1.0), .out(vo_max));
pwl_add2 xvomin (.in1(vss), .in2(dvol), .scale1(1.0), .scale2(1.0), .out(vo_min));

// limiting input range for modeling slew 
pwl_limiter xi_lim (.scale(unity_scale), .maxout(vid_max), .minout(vid_min), .in(v_id), .out(v_id_lim));

// gain stage and output limiting
pwl_vga xgain (.in(v_id_lim), .scale(Av), .out(vo));

// filtering op.
pwl_spf #(.etol(etol), .w1(wp), .en_filter(1'b1)) xfilter (.in(vo), .out(vo_filtered), .reset(freeze), .reset_sig(out));
// limiting output dynamic range
pwl_limiter xo_lim (.scale(unity_scale), .maxout(vo_max), .minout(vo_min), .in(vo_filtered), .out(vo_lim));

// gate keeper used in continuous-time feedback configuration
pwl_gatekeeper1 #(.en_lcc(en_lcc), .etol(etol), .gain_error(gain_error)) xgk1 (.extin(inp), .in(vo_filtered), .out(out), .lock(freeze));

//pragma protect end
`endprotect

endmodule
