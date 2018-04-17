# Makefile for running simulation

deck = sim

all:
	hspice $(deck).sp | tee $(deck).lis

clean:
	\rm *.??0 *.lis

cleanall: clean
	\rm -rf logfile out
