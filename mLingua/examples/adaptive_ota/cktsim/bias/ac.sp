* Test

.protect
.inc '../lib/cktlib.lib'
.unprotect

.param suph = 3.6
.param vcm = 2.5
.param vvd = 0.4
.param iib = 15u

.option accurate

.option post
.opt scale = 0.2u

.include '../classAB/ota_AB.net'
xdut ib inm inp out vdda dynamic_bias
xdiffdrv inp inm vd vc diffdrive
ib vdda ib dc 'iib' ac 1

vdda vdda gnd 'suph' 
mout out out 0 0 nmos L=4 W=4 M=2

vc vc gnd dc 'vcm' 
vd vd gnd dc 'vvd' $ac 1

.ac dec 50 10 5g sweep vd -0.5 0.5 0.05
$.pz i(mout) ib
.pz i(mout) vd
.probe ac im(mout) ip(mout)
.measure ac fp1 when ip(mout)=-45
.measure ac fp2 when ip(mout)=-135

.end
