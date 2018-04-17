* Test

.protect
.inc '/home/bclim/proj/DaVEnv/mProbo/examples/spice_lib/ptm180/models.lib' TT
.unprotect

.param sup = 1.8
.param vh = 1.3
.param vl = 1.0
.param period = 100e-9
.param tw = 1e-9
.param trf = 0.01e-9
.param iib = 500e-6

.option accurate post 


.include '../cteq.sp'
xdut inp inn outp outn ibias eq_z vdd vss cteq
xdrv inp inn vd vc diffdrive

vdd vdd vss 'sup' 
vss vss gnd dc 0
veq_z eq_z vss dc '1.0'
ib vdd ibias 'iib'

vc vc vss dc 1.2
vd vd vss pulse(-0.6 0.6 10e-9 trf trf 'tw-trf' 'period')

.tran 1p 500n
.op 8e-9
.probe i(xdut.m_1) i(xdut.m_2) i(xdut.m_3) i(xdut.m_4)
.probe gm(xdut.m_1) gm(xdut.m_2)

.dc vd -2.5 2.5 0.05
.probe i(xdut.m_1) i(xdut.m_2) i(xdut.m_3) i(xdut.m_4)
.probe gm(xdut.m_1) gm(xdut.m_2)

.end
