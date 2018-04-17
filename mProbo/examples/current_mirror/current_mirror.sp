************************************************************************ 
* library name: pet 
* cell name: current_mirror 
* view name: schematic 
************************************************************************ 

.subckt current_mirror vdd vss cfg_mirr<1> cfg_mirr<0> iref out0 out1 
*.pininfo cfg_mirr<1>:i cfg_mirr<0>:i vdd:b vss:b iref:b out0:b out1:b 
mm1 out0 bref vss vss nmos w=0.8u l=0.3u 
mm2 out1 bref vss vss nmos w=0.8u l=0.3u 
mmrn bref bref vss vss nmos w=0.8u l=0.3u 
mm1d out0 vss vss vss nmos w=0.8u l=0.3u 
mm2d out1 vss vss vss nmos w=0.8u l=0.3u 
mmrnd bref vss vss vss nmos w=0.8u l=0.3u 
mmrefd vdd vdd vdd vdd pmos w=0.64u l=0.3u m=1 
mm0sw bref cfg_mirr<0> n0 vdd pmos w=0.32u l=0.06u 
mm0p n0 iref vdd vdd pmos w=0.64u l=0.3u m=1 
mmp n iref vdd vdd pmos w=0.64u l=0.3u m=1 
mmsw bref vss n vdd pmos w=0.32u l=0.06u 
mm0d n0 vdd vdd vdd pmos w=0.64u l=0.3u m=1 
mmd n vdd vdd vdd pmos w=0.64u l=0.3u m=1 
mm1p n1 iref vdd vdd pmos w=0.64u l=0.3u m=2 
mm1sw bref cfg_mirr<1> n1 vdd pmos w=0.32u l=0.06u 
mmref iref iref vdd vdd pmos w=0.64u l=0.3u m=4 
.ends 
