$

.opt post scale=1
.global vdd vss
.temp 50          $$ 50 is defined in test.cfg

.param ps=1.8
+ vcm=1.1
+ freq=20e6
+ va = 0.005
+ infreq=1.394e6
$+ infreq=1.394e6

// spice models
.lib "/home/bclim/proj/DaVEnv/mProbo/examples/spice_lib/ptm180/models.lib" tt 


.include "/home/bclim/proj/imager/netlist/imager_dave.netlists.ckt"

xpre_amp1 vdd clk_preamp ibias1 vinn vinp i_voutn i_voutp pdn pre_amp1
xpre_amp2 vdd clk_preamp ibias2 i_voutn i_voutp voutn voutp pdn pre_amp2
xsenseamp vdd clk_latch outb out voutn voutp senseamp

vdd vdd 0 dc ps
ib1 vdd ibias1 dc 10u
ib2 vdd ibias2 dc 4.2u

vinp vinp 0 sin(vcm va infreq 0)
vinn vinn 0 sin(vcm va infreq 0 0 180)

vpdn pdn 0 pulse(ps 0 20n 100p 100p 100n 1)
vclk_preamp clk_preamp 0 pulse(0 ps 1p 60p 60p '0.5/freq-60p' '1/freq')
vclk_latch clk_latch 0 pulse(0 ps '1p+0.4/freq' 60p 60p '0.5/freq-60p' '1/freq')

.tran 1p 20u
.probe v(voutp,voutn) v(i_voutp,i_voutn)

.end
