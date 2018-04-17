// test PWL modeling


`include "mLingua_pwl.vh"

module test;

//timeunit 1ns;
//timeprecision 1ns;

`get_timeunit
PWLMethod pm=new;

parameter real Z0= 50.0;     // characteristic impedance
parameter real TD= 0.5e-9;     // propagation delay
parameter real RS = 35;  // driver termination resistor
parameter real RT = 1000;  // receiver termination resistor
parameter real IOUT = 10e-3; // amplitude of driving current
parameter real ETOL = 0.01; // error tolerance of TLine, channel

logic din;
real vin;
pwl vout, chout;
real id;

pulse #(.b0(0), .td(10e-9), .tw(0.5e-9), .tp(2)) xpulse (.out(din));
always @(din) begin
  id = din? IOUT : -IOUT;
  vin = id*RS;  // change norton to thevnin
end

txline #(.etol(ETOL), .Z0(Z0), .TD(TD)) dut (.rt(RT), .rs(RS), .vin(vin), .vout(vout));
channel #(.etol(ETOL)) xch (.in(vout), .out(chout));
pwl_probe #(.Tstart(1e-15), .Tend(1), .filename("vout.txt")) xprobe1 (.in(vout));
pwl_probe #(.Tstart(1e-15), .Tend(1), .filename("chout.txt")) xprobe2 (.in(chout));

`run_wave

endmodule
