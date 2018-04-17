$

.opt post scale=1
.global vdd vss
.temp 50          $$ 50 is defined in test.cfg

.lib "/home/bclim/proj/DaVEnv/mProbo/examples/spice_lib/ptm180/models.lib" tt 


.inc "../../pre_amp1/pre_amp1.sp"
.inc "../../pre_amp2/pre_amp2.sp"
.inc "../senseamp.sp"

.subckt comparator vinp vinn voutp voutn pdn clk_preamp clk_latch out outb
.param ps = 1.8
vdd vdd 0 dc ps
ib1 vdd ibias1 dc 10u
ib2 vdd ibias2 dc 4.2u
xpre_amp1 vdd clk_preamp ibias1 vinn vinp i_voutn i_voutp pdn pre_amp1
xpre_amp2 vdd clk_preamp ibias2 i_voutn i_voutp voutn voutp pdn pre_amp2
xsenseamp vdd clk_latch outb out voutn voutp senseamp
.probe v(*)
.ends


.end
