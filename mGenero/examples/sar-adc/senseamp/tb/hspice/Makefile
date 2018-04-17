# Makefile for running Hspice
#

DECK := sim

# default rule:
all: run

# 
run:
	@echo ""
	@echo Running HSPICE simulation
	@echo ==================================================
	hspice $(DECK).sp |tee $(DECK).lis

clean:
	\rm -rf $(DECK).??0 $(DECK).lis sxcmd.log 
