// test PWL modeling


`include "mLingua_pwl.vh"

module test;

`get_timeunit
PWLMethod pm=new;

parameter real etol=0.001;
parameter real fsw=1e6;
parameter real vin=2.5;
parameter real vout_target=1.0;
parameter real beta=3.0/4.0;
parameter real vref_val = vout_target*beta;

pwl vref = '{vref_val,0,0};
pwl vddh = '{vin,0,0};
pwl vgnd = '{0.0,0,0};
pwl vout;
pwl saw_in;
real vout_r;

buck #(.etol(etol), .rp(1), .L(530e-9), .RL(10), .CL(940e-6)) xbuck(.vref(vref), .saw_in(saw_in), .vddh(vddh), .vgnd(vgnd), .vout(vout));
pwl_saw #(.offset(1.5), .pk2pk(3), .freq(fsw), .phase(0)) xsaw (.out(saw_in));

//pwl2real #(.dv(1e-15)) pwl2real3 (.in(vout), .out(vout_r));
pwl_probe #(.Tstart(1e-15), .Tend(1), .filename("vout.txt")) xprobe1 (.in(vout));

`run_wave

endmodule
