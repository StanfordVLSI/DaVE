# Makefile for running VCS simulation
#
include $(mLINGUA_DIR)/etc/vcs_flag.mk
include $(mLINGUA_DIR)/etc/ncvlog_flag.mk

TOP_MODULE := test
TIME_SCALE := 1ns/1ns

VERILOG_FILES := test.v
TRAN_TIME := 20us


# default rule:
all: vcs run

# vcs rule:
#
vcs:
	@echo ""
	@echo Now Compiling in VCS
	@echo ==================================================
	vcs -top $(TOP_MODULE) $(VERILOG_FILES) $(mLINGUA_VCS_FLAGS) -f verilog.f -timescale=$(TIME_SCALE) +prof #-ad=vcsAD.init

# run rule:
run: vcs
	@echo ""
	@echo Now Running ./simv
	@echo ==================================================
	./simv +wave +vcs+finish+$(TRAN_TIME) -l simv.log

clean:
	\rm -rf simv* csrc ucli.key vc_hdrs.h simv.log DVEfiles *vpd vcs.prof *.txt INCA_libs waves.shm ncverilog.log hdl.tcl ncprof.out shm.prof *.tr0 *.fsdb xa.log genie.log sxcmd.log

cleanall: clean
	\rm -rf *.txt *.eps 
