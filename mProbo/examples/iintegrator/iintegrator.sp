* subckt: iintegrator
.subckt iintegrator avdd avss iin pwdnb rst rstb vbn vout vref vrefi
xi13 avdd avss vref xvref vref vbn amp_unity
xi9 avdd avss rst rstb xvref vrefi tg
xi7 avdd avss rst rstb avss vout tg
xc6 xvref avss avss xcap w=2.4e-6 l=10e-6
xc7 xvref avdd avss xcap w=2.4e-6 l=10e-6
xc4 vout avss avss xcap w=7.84e-6 l=13e-6
xc1 vout avdd avss xcap w=7.84e-6 l=13e-6
xi10 avdd avss pwdnb vrefi vrefgen
r0 iin vout 1e-3
.ends iintegrator

* subckt: amp_unity
.subckt amp_unity avdd avss inm inp out vbn
xtn1 out inm net10 avss nfet l=400e-9 w=1.5e-6 nf=4 m=1
xtn0 net17 inp net10 avss nfet l=400e-9 w=1.5e-6 nf=4 m=1
xtn2 net10 vbn avss avss nfet l=400e-9 w=1e-6 nf=2 m=1
xtp1 out net17 avdd avdd pfet l=400e-9 w=1.5e-6 nf=4 m=1
xtp0 net17 net17 avdd avdd pfet l=400e-9 w=1.5e-6 nf=4 m=1
.ends amp_unity

* subckt: tg
.subckt tg avdd avss c cb d s
xtp0 d cb s avdd pfet l=180e-9 w=500e-9 nf=1 m=1
xtn1 s c d avss nfet l=180e-9 w=500e-9 nf=1 m=1
.ends tg

* subckt: vrefgen
.subckt vrefgen avdd avss pwndb vref
xtn0 net4 pwndb avss avss nfet l=180e-9 w=4e-6 nf=2 m=1
xrpc6 avdd avdd avss pres w=1e-6 l=6e-6 m=1
xrpc4 avdd vref avss pres w=1e-6 l=6e-6 m=1
xrpc3 vref net07 avss pres w=1e-6 l=6e-6 m=1
xrpc0 net07 net4 avss pres w=1e-6 l=6e-6 m=1
xrpc5 avdd avdd avss pres w=1e-6 l=6e-6 m=1
.ends vrefgen

* subckt: biasgen
.subckt biasgen avdd avss pwdn vbn
xtp6 vbn vbn net11 avdd pfet l=400e-9 w=1e-6 nf=1 m=1
xtp11 net11 pwdn avdd avdd pfet l=180e-9 w=1e-6 nf=1 m=1
xtn3 vbn vbn avss avss nfet l=400e-9 w=2e-6 nf=2 m=1
.ends biasgen
