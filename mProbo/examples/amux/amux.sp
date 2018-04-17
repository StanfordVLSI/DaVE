* subckt: amux
.subckt amux avdd avss i0 i1 out sel0
xi0 avdd avss sel0b sel0 i1 out tg
xi3 avdd avss sel0 sel0b i0 out tg
xi5 sel0 avdd avss sel0b inv
.ends amux

* subckt: tg
.subckt tg avdd avss c cb d s
xtp0 d cb s avdd pfet l=180e-9 w=500e-9 nf=1 m=1 
xtn1 s c d avss nfet l=180e-9 w=500e-9 nf=1 m=1 
.ends tg

* subckt: inv
.subckt inv a vdd vss z
xtpa z a vdd vdd pfet l=180e-9 w=400e-9 nf=1 m=1 
xtna z a vss vss nfet l=180e-9 w=400e-9 nf=1 m=1 
.ends inv
