* Test

.protect
.inc '../lib/cktlib.lib'
.unprotect

.param suph = 3.6
.param vcm = 2.5
.param vvd = 0.00
.param iib = 15u

.option accurate

.option post
.opt scale = 0.2u

.include '../classAB/ota_AB.net'
xdut ib inm inp out vdda dynamic_bias
xdiffdrv inp inm vd vc diffdrive
ib vdda ib dc 'iib'

vdda vdda gnd 'suph' 
mout out out 0 0 nmos L=4 W=4 M=2

vc vc gnd dc 'vcm' 
vd vd gnd dc 'vvd' 

.dc vd -1.0 1.0 0.01
.probe dc i(mout)

.end
