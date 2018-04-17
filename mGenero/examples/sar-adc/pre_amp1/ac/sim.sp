$

.opt post scale=1
.global vdd vss
.temp 50          $$ 50 is defined in test.cfg


// spice models
.lib "/home/bclim/proj/DaVEnv/mProbo/examples/spice_lib/ptm180/models.lib" tt 


.inc "../pre_amp1.sp"
xbalun df cm inp inn balun
xdut avdd clk ibn inn inp outn outp pdn pre_amp1
vdd avdd 0 dc 1.8
vclk clk 0 dc 0.0
vpdn pdn 0 dc 1.8
ib avdd ibn 10e-6
vcm cm 0 dc 1.0
vd df 0 dc 0 ac 1

.ac dec 100 10k 10g
.pz v(outp,outn) vd
.probe v(outp,outn)

.end
