
module cteq #(
  parameter real etol_v_fz = 0.01, // error tolerance of a v_fz input
  parameter real etol_vdd = 0.01, // resolution of vdd
  parameter real etol_v_icm = 0.01, // resolution of common-mode voltage input
  parameter real v_os = 0.0, // input referred static offset voltage
  parameter real etol_f = 0.001 // error tolerance of a filter
) (
  output pwl voutp , // positive output
  input pwl vinn , // negative input
  input pwl vss , // ground
  input pwl vdd , // power supply
  input pwl vinp , // positive input
  input pwl v_fz , // analog input which controls degeneration resistor
  output pwl voutn  // negative output
);

timeunit 1fs;
timeprecision 1fs;

`protect
//pragma protect 
//pragma protect begin

`get_timeunit
PWLMethod pm=new;

// map pins between generic names and user names, if they are different
pwl outp;
pwl inn;
pwl inp;
pwl outn;
assign voutp=outp ;
assign inn=vinn ;
assign inp=vinp ;
assign voutn=outn ; 
//----- BODY STARTS HERE -----

//----- SIGNAL DECLARATION -----

pwl v_id_lim;   // limited v_id 
pwl v_oc; // output common-mode voltage
pwl v_od; // output differential voltage
pwl vid_max, vid_min; // max/min of v_id for slewing 
pwl vop, von;
pwl v_od_filtered;
pwl vop_lim, von_lim;
pwl v_id, v_icm; // differential and common-mode inputs

real t0;
real v_icm_r;
real vdd_r;
real vss_r, v_fz_r;

real fz1, fp1, fp2; // at most, two poles and a zero
real Av;    // voltage gain (gm*Rout)
real max_swing; // Max voltage swing of an output (Itail*Rout)
real vid_r; // vid<|vid_r| (max_swing/Av)
real v_oc_r;  // common-mode output voltage

event wakeup;

//----- FUNCTIONAL DESCRIPTION -----

initial ->> wakeup; // dummy event for ignition at t=0

//-- Compute differential and common-mode voltages 

// diff/cm sense considering input referred offset
pwl_add #(.no_sig(3)) xidiff (.in('{inp,inn,'{v_os,0,0}}), .scale('{1,-1,1}), .out(v_id));
pwl_add #(.no_sig(2)) xicm (.in('{inp,inn}), .scale('{0.5,0.5}), .out(v_icm));

//-- System's parameter calculation

// discretization of control inputs
pwl2real #(.dv(etol_v_icm)) xp2r_v_icm (.in(v_icm), .out(v_icm_r)); // pwl-to-real of v_icm
pwl2real #(.dv(etol_vdd)) xp2r_vdd (.in(vdd), .out(vdd_r)); // pwl-to-real of vdd
pwl2real #(.dv(etol_v_fz)) xp2r_v_fz (.in(v_fz), .out(v_fz_r)); // pwl-to-real of v_fz

// updating parameters as control inputs/mode inputs change

always @(v_icm_r or vdd_r or wakeup or vss_r or v_fz_r) begin
  t0 = `get_time;

  //Av  = 1.262799e+00  + -9.902002e-01*v_fz_r +  2.779062e-02*v_icm_r + 1.261019e-01*v_fz_r*v_icm_r;
  //fz1  = 8.085917e+07 + -7.908804e+07*v_fz_r +  2.768540e+06*v_icm_r + 1.092432e+07*v_fz_r*v_icm_r;
  //fp1  = 3.523630e+08 + -7.095187e+07*v_fz_r + -9.011234e+04*v_icm_r + 9.578688e+06*v_fz_r*v_icm_r;
  //fp2  = 2.584193e+09 + -1.876075e+07*v_fz_r + -2.556672e+07*v_icm_r + 1.191863e+07*v_fz_r*v_icm_r;
  //max_swing = 9.502665e-01 + 2.898901e-02*v_fz_r + 3.219313e-02*v_icm_r + -7.694456e-02*v_fz_r*v_icm_r;
  //v_oc_r = 1.412220e+00 + -2.673026e-06*v_fz_r + -8.614779e-02*v_icm_r + 1.850210e-06*v_fz_r*v_icm_r;
  Av   = 1.267920e+00 + -9.510441e-01*v_fz_r +  2.457286e-02*v_icm_r + 9.772884e-02*v_fz_r*v_icm_r;
  fz1  = 8.131948e+07 + -7.546499e+07*v_fz_r +  2.479833e+06*v_icm_r + 8.296641e+06*v_fz_r*v_icm_r;
  fp1  = 3.527850e+08 + -6.767255e+07*v_fz_r + -3.550818e+05*v_icm_r + 7.203102e+06*v_fz_r*v_icm_r;
  fp2  = 2.584015e+09 + -1.956209e+07*v_fz_r + -2.545196e+07*v_icm_r + 1.242784e+07*v_fz_r*v_icm_r;

  max_swing = 9.904721e-01 + -6.123619e-02*v_fz_r + 2.335911e-03*v_icm_r + 4.197413e-03*v_fz_r*v_icm_r;
  v_oc_r    = 1.412217e+00 + 2.764301e-05*v_fz_r + -8.614602e-02*v_icm_r + -1.796318e-05*v_fz_r*v_icm_r;

  vid_r = max_swing/Av;
  vid_max = '{vid_r,0,t0};       // max input 
  vid_min = '{-1.0*vid_r,0,t0};  // min input

end

//-- Model behaviors

pwl_limiter xi_lim (.scale('{1,0,0}), .maxout(vid_max), .minout(vid_min), .in(v_id), .out(v_id_lim)); // limiting input range for modeling gm compression 

pwl_vga xgain (.in(v_id_lim), .scale(Av), .out(v_od)); // differential-mode gain stage 

pwl_filter_real_w_reset #(.etol(etol_f), .en_filter(1'b1), .filter(2)) xfilter (.fz1(fz1), .fp1(fp1), .fp2(fp2), .fp_rst(0.0), .in(v_od), .in_rst('{0,0,0}), .out(v_od_filtered), .reset(1'b0)); // differential output filtering

real2pwl #(.tr(10e-12)) r2poc (.in(v_oc_r), .out(v_oc)); // output common-mode voltage

// combine differential and common-mode output
pwl_add #(.no_sig(2)) xoutp (.in('{v_oc,v_od_filtered}), .scale('{1,0.5}), .out(outp));
pwl_add #(.no_sig(2)) xoutn (.in('{v_oc,v_od_filtered}), .scale('{1,-0.5}), .out(outn));

//pragma protect end
`endprotect

endmodule
