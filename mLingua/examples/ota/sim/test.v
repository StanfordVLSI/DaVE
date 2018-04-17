// test module

`include "mLingua_pwl.vh"

module test;

//timeunit 1fs;
//timeprecision 1fs;
`get_timeunit // TU = timeunit of this module

parameter period = 10.0e-6;
parameter tr = 0.001e-6;

PWLMethod pm=new;

pwl inp;
pwl inn;
pwl vout; 
pwl vdd, vss;
real vout_r, inn_r;
pwl ibias;

reg pulse;
initial begin
  vdd = '{2.0,0,0};
  vss = '{0,0,0};
  ibias = '{10e-6,1e-6/TU,0};
  #1 ibias = '{11e-6,0,`get_time};
  pulse = 1'b0;
  #(400e-9/TU);
  pulse = 1'b0;
  for (int i=0;i<100000000;i++) pulse = #(period/TU/2.0) ~pulse;
end

parameter real etol=0.001;
parameter en_lcc = 1'b1;

bit2pwl #(.vh(1.45), .vl(1.00), .tr(tr)) b2p (.in(pulse), .out(inp));
//pwl_saw #(.offset(0.1), .pk2pk(0.3), .freq(1/10e-6)) xin (.out(inp));
ota #(.etol(etol), .gain_error(1.0-70.0/71.0), .en_lcc(en_lcc)) dut (.vdd(vdd), .vss(vss), .ibias(ibias), .inp(inp), .inn(inn), .out(vout));
//pwl_vga xxx (.in(vout), .scale(0.25), .out(inn));
assign inn = vout;

// save waveforms to vpd if necessary
`run_wave

endmodule
