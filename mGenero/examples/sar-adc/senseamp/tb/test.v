// test PWL modeling
// Ramp response of CTLE model to check the error (etol) is actually bound

`include "mLingua_pwl.vh"

module test;

timeunit 1fs;
timeprecision 1fs;
`get_timeunit
PWLMethod pm=new;

parameter real ps=1.8;
parameter real vcm=1.1;
parameter real va=0.005;
parameter real freq=20e6;
parameter real infreq=1.394e6;

wire clk_preamp;
wire clk_latch;
wire pdn;
pwl vinp, vinn;
pwl i_voutp, i_voutn;
pwl voutp, voutn;
pwl vdd, vss;
pwl ibias1, ibias2;
pwl vout, i_vout;

vdc #(.dc(ps)) xvdd (.vout(vdd));
vdc #(.dc(0.0)) xvss (.vout(vss));
idc #(.is_n(1), .dc(10e-6)) xibias1 (.refnode(vdd), .outnode(ibias1));
idc #(.is_n(1), .dc(4.2e-6)) xibias2 (.refnode(vdd), .outnode(ibias2));

pwl_sin #(.etol(0.0001), .freq(infreq), .amp(va), .offset(vcm), .ph(0)) xsinp (.out(vinp));
pwl_sin #(.etol(0.0001), .freq(infreq), .amp(va), .offset(vcm), .ph(180)) xsinn (.out(vinn));
clock #(.freq(freq), .duty(0.5), .td(1e-12)) xclk1 (.ckout(clk_preamp));
clock #(.freq(freq), .duty(0.5), .td(0.4/freq+1e-12)) xclk2 (.ckout(clk_latch));
pulse #(.b0(1'b1), .td(20e-9), .tw(100e-9), .tp(1)) xpulse(.out(pdn));

// model
comparator_mdl comparator_mdl ( .vdd(vdd), .ibias1(ibias1), .ibias2(ibias2), .vinp(vinp), .vinn(vinn), .voutp(voutp), .voutn(voutn), .pdn(pdn), .clk_preamp(clk_preamp), .clk_latch(clk_latch), .out(out), .outb(outb));

/*****
// circuit
logic out_r, outb_r;
real vinp_r, vinn_r, voutp_r, voutn_r;
real vout_r;
pwl2real #(.dv(0.0001)) xp2r1 (.in(vinp), .out(vinp_r));
pwl2real #(.dv(0.0001)) xp2r2 (.in(vinn), .out(vinn_r));
comparator comparator ( .vinp(vinp_r), .vinn(vinn_r), .voutp(voutp_r), .voutn(voutn_r), .pdn(pdn), .clk_preamp(clk_preamp), .clk_latch(clk_latch), .out(out_r), .outb(outb_r)); // circuit
*****/



pwl_add #(.no_sig(2)) xvout (.in('{voutp,voutn}), .scale('{1,-1}), .out(vout));
pwl_add #(.no_sig(2)) xivout (.in('{comparator_mdl.i_voutp,comparator_mdl.i_voutn}), .scale('{1,-1}), .out(i_vout));
//real_add #(.no_sig(2)) xvout_r (.in('{voutp_r,voutn_r}), .scale('{1,-1}), .out(vout_r));

//pwl_probe #(.Tstart(1e-15), .Tend(1), .filename("voutp.txt")) xprobe1 (.in(voutp));
//pwl_probe #(.Tstart(1e-15), .Tend(1), .filename("voutn.txt")) xprobe2 (.in(voutn));
pwl_probe #(.Tstart(1e-15), .Tend(1), .filename("vout.txt")) xprobe3 (.in(vout));
//real_probe #(.Tstart(1e-15), .Tend(1), .filename("vout_r.txt")) xprobe4 (.in(vout_r));
pwl_probe #(.Tstart(1e-15), .Tend(1), .filename("i_vout.txt")) xprobe5 (.in(i_vout));
`run_wave

endmodule

module comparator_mdl(
  `input_pwl vdd,
  `input_pwl ibias1, ibias2,
  `input_pwl vinp, vinn,
  `output_pwl voutp, voutn,
  input logic pdn, clk_preamp, clk_latch,
  output logic out, outb
);

pwl i_voutp, i_voutn;
pre_amp1 pre_amp1 ( .outp(i_voutp), .outn(i_voutn), .pdn(pdn), .inp(vinp), .inn(vinn), .avdd(vdd), .ibn(ibias1), .clk(clk_preamp) );
pre_amp2 pre_amp2 ( .outp(voutp), .outn(voutn), .pdn(pdn), .inp(i_voutp), .inn(i_voutn), .avdd(vdd), .ibn(ibias2), .clk(clk_preamp) );
senseamp senseamp ( .avdd(vdd), .clk_latch(clk_latch), .outn(outb), .outp(out), .vin(voutn), .vip(voutp) );
endmodule
