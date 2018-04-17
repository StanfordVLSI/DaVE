$ a simple sample-and-hold circuit 

.subckt tnh in out sclk 
msamp out sclk in gnd nmos l=0.06u w=5.04u
csamp out gnd 30f
.ends tnh 
