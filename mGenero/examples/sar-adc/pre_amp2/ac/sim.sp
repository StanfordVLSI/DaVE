$

.opt post scale=1
.global vdd vss
.temp 50          $$ 50 is defined in test.cfg


// spice models
.lib "/home/bclim/proj/DaVEnv/mProbo/examples/spice_lib/ptm180/models.lib" tt 


.inc "../pre_amp2.sp"
xbalun df cm inp inn balun
xdut avdd clk ibn inn inp outn outp pdn pre_amp2
vdd avdd 0 dc 1.8
$vclk clk 0 dc 1.8
vclk clk 0 dc 0
vpdn pdn 0 dc 1.8
ib avdd ibn 4.625e-6
vcm cm 0 dc 1.1
vd df 0 dc 0 ac 1

.ac dec 100 10k 100g
.pz v(outp,outn) vd
.probe v(outp,outn)

.end
