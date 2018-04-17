Phase-Locked Loop
=================

Description
-----------
A second-order charge-pump phase-locked loop (PLL) example is here. 

Simulation
----------
1. go to ./sim directory
2. run Makefile, if you don't need to probe signals
   $ make

3. If you want to probe signals, do the following.
   $ make wave

   This will dump waveforms to vcdplus.vpd which can be opened with VCS's "dve" tool. Note that dumping the waveforms will slow down the simulation speed. 
