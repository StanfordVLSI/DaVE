# Makefile for running VCS simulation
#
# default rule:
all: 
	@echo ""
	@echo Now running circuit simulation 
	@echo ==================================================
	hspice sim.sp |tee sim.lis

clean:
	\rm -rf *.??0* *.log *.lis
