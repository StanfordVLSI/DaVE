# Makefile for running Hspice

DECK := sim

# default rule:
all: run

# 
run:
	@echo ""
	@echo Running HSPICE simulation
	@echo ==================================================
	@for d in $(DECK); do \
		hspice $$d.sp |tee $$d.lis; \
	done


clean:
	@for d in $(DECK); do \
		\rm -rf $$d.??0 $$d.lis sxcmd.log; \
	done
