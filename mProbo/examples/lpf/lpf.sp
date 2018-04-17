$ lpf with a single pole

.subckt lpf in out vctl
gvcr in out vcr pwl(1) vctl gnd 0v,10k 1v,100k  $ VCR
cload out gnd 1p
.ends

