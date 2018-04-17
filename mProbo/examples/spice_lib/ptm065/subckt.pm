.subckt nfet d g s b w=0 l=0 nf=1
mn d g s b nmos w=w l=l mult=nf
.ends

.subckt pfet d g s b w=0 l=0 nf=1
mp d g s b pmos w=w l=l mult=nf
.ends

.subckt xcap in out ref w=1u l=1u
.param cu=0.75e-3
c0 in out 'cu*w*l'
.ends
.subckt pres pn nn ref w=0 l=0
.param rsh = 400
r0 pn nn 'rsh*l/w'
.ends
