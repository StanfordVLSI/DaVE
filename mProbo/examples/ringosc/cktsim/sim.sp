$ VCO f vs vreg


.options post method=gear scale=0.045u

.lib "/home/bclim/proj/DaVE/examples/spice_lib/ptm090/models.lib" tt
.include "../ringosc.sp" 

xdut vdd vreg cko ckob ringosc

vdd vdd 0 dc 1.0
vreg vreg 0 dc 0

.tran 10p 20n sweep vreg 0.4 1.0 0.05
.ic v(xdut.vck) = 1.0 v(xdut.vckb) = 0.0

.measure tran period trig v(cko)=0.5 rise=10 targ v(cko)=0.5 rise=11
.measure tran frequency param='1/period'
.end
