* Test

.protect
.inc '../lib/cktlib.lib'
.unprotect

.param suph = 3.6
.param vh = 2.5
.param vl = 1.40
.param period = 10e-6
.param trf = 0.01e-6
.param iib = 15e-6

.option accurate 

.option post
.opt scale = 0.2u

.include './ota_AB.net'
xdut inp inm ib vdda out ota_AB

vdda vdda gnd 'suph' 
ib vdda ib 'iib'

vinp inp gnd pulse(vh vl 400e-9 trf trf 'period/2-trf' 'period')

cload out gnd 1.2p
vfb out inm dc 0

.tran 1p 1000us
.probe i(xdut.xiamp.msrc) i(xdut.xiamp.mdiff) i(xdut.xiamp.madd)
+ i(xdut.xiamp.mfb) + i(xdut.xibias.mbias)


.end
