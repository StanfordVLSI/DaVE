/****************************************************************

Copyright (c) 2018- Stanford University. All rights reserved.

The information and source code contained herein is the 
property of Stanford University, and may not be disclosed or
reproduced in whole or in part without explicit written 
authorization from Stanford University. Contact bclim@stanford.edu for details.

* Filename   : clk_preamp.v
* Author     : Byongchan Lim (bclim@stanford.edu)
* Description: Clocked pre-amplifier in a comparator

* Note       :

* Revision   :
  - 7/26/2016: First release

****************************************************************/


module clk_preamp #(
  parameter real vos0 = `PA_VOS, // input referred offset voltage
  parameter real etol_vic = `PA_ETOL_V, // resolution of common-mode voltage input for tail current calculation
  parameter real etol_f = `PA_ETOL_V, // error tolerance of a filter
  parameter real etol_ib = `PA_ETOL_I, // resolution of ibias current
  parameter real alpha = 2.0  // alpha factor of MOS transistor iv equation (id ~ B*Vgo^alpha)
  //parameter real dvo_low = 0.3, // min(V(out)) = vss+dvo_low*(vdd-vss)
  //parameter real dvo_hi = 0.0, // max(V(out)) = vdd-dvo_hi*(vdd-vss)
) (
  input pwl vdd,          // power supply
  input pwl vss,          // ground
  input pwl vinp, vinn,   // +/- input
  input pwl ibias,        // bias current input
  input pwdn,             // shut down bias current
  input eq,               // equalize two outputs
  output pwl voutp, voutn // +/- output
);



`get_timeunit
PWLMethod pm=new;

parameter real Ron_xtr = 200;
parameter real Rl_cm = 15e3;
parameter real Cl = 2e-15;

pwl v_id, v_icm; // differential and common-mode inputs
real v_icm_r;
real ibias_r; 
real t0;
real ibias_r_pow;

pwl v_id_lim;   // limited v_id 
pwl v_oc; // output common-mode voltage
pwl v_od; // output differential voltage
pwl vid_max, vid_min; // max/min of v_id for slewing 
//pwl vo_max, vo_min;
pwl vop, von;
pwl v_od_filtered;
pwl vop_lim, von_lim;
pwl half_swing;
pwl vos = '{vos0,0,0};
pwl unity_scale = '{1,0,0};

real wp;
real Av;    // voltage gain (gm*Rout)
real max_swing; // Max voltage swing of an output (Itail*Rout)
real vid_r; // vid<|vid_r| (max_swing/Av)
real Rl_diff;


event wakeup;
initial ->> wakeup;


/***********************************************
* Compute differential and common-mode voltages 
***********************************************/
// diff/cm sense & count input referred offset
pwl_add3 xidiff (.in1(vinp), .in2(vinn), .in3(vos), .scale1(1.0), .scale2(-1.0), .scale3(1.0), .out(v_id));
pwl_add2 xicm (.in1(vinp), .in2(vinn), .scale1(0.5), .scale2(0.5), .out(v_icm));


/***********************************************
* System's parameter calculation
***********************************************/
// discretization of control inputs
pwl2real #(.dv(etol_vic)) xp2r_vic (.in(v_icm), .out(v_icm_r));  // discretization of Vi_cm
pwl2real #(.dv(etol_ib)) xp2r_it (.in(ibias), .out(ibias_r));  // discretization of ibias


// calculating voltage gain, input range of tranconductance stage for slewing 
always @(ibias_r or v_icm_r or pwdn or eq or wakeup) begin
  t0 = `get_time;
  ibias_r_pow = ibias_r**((alpha-1.0)/alpha);
  Rl_diff = eq? Rl_cm*Ron_xtr/2.0/(Rl_cm+Ron_xtr/2.0) : Rl_cm;
  max_swing = pwdn? 0.0 : ibias_r*Rl_cm;
  Av = pwdn? 0.0 : ibias_r_pow*0.01*Rl_diff;
  vid_r = max_swing/Av;
  vid_max = '{vid_r,0,t0};       // max input 
  vid_min = '{-1.0*vid_r,0,t0};  // min input
  half_swing = pm.write(max_swing/2.0,0,t0);
end

// Rout, gm params, poles, and zero
always @(Rl_diff or wakeup) begin
  wp = 1/Rl_diff/Cl;
end

/***********************************************
* Circuit behaviors
***********************************************/

// limiting input range for modeling gm compression 
pwl_limiter xi_lim (.scale(unity_scale), .maxout(vid_max), .minout(vid_min), .in(v_id), .out(v_id_lim));

// differential-mode gain stage 
pwl_vga xgain (.in(v_id_lim), .scale(Av), .out(v_od));

pwl vin_filter;

always @(pwdn or `pwl_event(v_od) or `pwl_event(vdd)) begin
  if (pwdn) begin
    vin_filter = '{0,0,`get_time};
  end
  else begin
    vin_filter = v_od;
  end
end

// filtering with a pole
pwl_filter_real_p1 #(.etol(etol_f), .en_filter(1'b1)) xfilter (.fp(wp/`M_TWO_PI), .in(vin_filter), .out(v_od_filtered));

// output common-mode voltage
pwl_add2 xvoc (.in1(vdd), .in2(half_swing), .scale1(1.0), .scale2(-1.0), .out(v_oc));

// combine differential and common-mode output
pwl_add2 xvop (.in1(v_oc), .in2(v_od_filtered), .scale1(1.0), .scale2(0.5), .out(vop));
pwl_add2 xvon (.in1(v_oc), .in2(v_od_filtered), .scale1(1.0), .scale2(-0.5), .out(von));

assign voutp = vop;
assign voutn = von;

endmodule
