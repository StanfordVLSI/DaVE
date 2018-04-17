// test PWL modeling
// Ramp response of CTLE model to check the error (etol) is actually bound

`include "mLingua_pwl.vh"

module test;

timeunit 1fs;
timeprecision 1fs;
`get_timeunit
PWLMethod pm=new;

reg in;
wire inb = ~in;

pwl inp, inn;
pwl outp, outn;
pwl ibias;
pwl vctl1, vctl2;
pwl vdd, vss;


initial begin
  vdd = pm.write(1.8, 0, 0);
  vss = pm.write(0,0,0);
  ibias = pm.write(550e-6,0,0);
  vctl1 = pm.write(1.0,0,0);
  #1;
  $display("wz=%e", dut.wz1);
  $display("wp1=%e", dut.wp1);
  $display("wp2=%e", dut.wp2);
  $display("Av=%e", dut.Av);
  /*
  */
end

pwl v_od, v_id;

pulse #(.td(10e-9), .tw(1e-9), .tp(100e-9)) xpulse (.out(in), .outb(inb));
bit2pwl #(.vh(1.2+0.15), .vl(1.2-0.15), .tr(10e-12), .tf(10e-12) ) b2pp ( .in(in), .out(inp));
bit2pwl #(.vh(1.2+0.15), .vl(1.2-0.15), .tr(10e-12), .tf(10e-12) ) b2pn ( .in(inb), .out(inn));
cteq dut (.vdd(vdd), .vss(vss), .inp(inp), .inn(inn), .ibiasn(ibias), .eq_z(vctl1), .outp(outp), .outn(outn));

pwl_add #(.no_sig(2)) xvdi (.in('{inp,inn}), .scale('{1.0,-1.0}), .out(v_id));
pwl_add #(.no_sig(2)) xvdo (.in('{outp,outn}), .scale('{1.0,-1.0}), .out(v_od));

dump_pwl #(.filename("input.txt"),.ts(0), .te(900E-9),.ti(10e-12),.window(1)) dumpi (.in(v_id));
dump_pwl #(.filename("output.txt"),.ts(0), .te(900E-9),.ti(10e-12),.window(1)) dumpo (.in(v_od));
dump_pwl #(.filename("outp.txt"),.ts(0), .te(900E-9),.ti(10e-12),.window(1)) dumpoutp (.in(outp));
dump_pwl #(.filename("outn.txt"),.ts(0), .te(900E-9),.ti(10e-12),.window(1)) dumpoutn (.in(outn));


`run_wave

endmodule
