$ lpf with a single pole

$ wrong model, vctl polarity inversion

.subckt lpf in out vctl
gvcr in out vcr pwl(1) vctl gnd 0v,100k 1v,90k  $ VCR
cload out gnd 1p
.ends

