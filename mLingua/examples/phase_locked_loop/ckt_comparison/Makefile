# Makefile for running VCS simulation
#
include $(mLINGUA_DIR)/etc/vcs_flag.mk

TOP_MODULE := test
TIME_SCALE := 1ns/1ns
VERILOG_FILES := ../model/tb_pll2nd.v

TRAN_TIME := 20us


# default rule:
all: vcs run

# vcs rule:
#
vcs:
	@echo ""
	@echo Now Compiling 
	@echo ==================================================
	vcs -top $(TOP_MODULE) $(VERILOG_FILES) $(mLINGUA_VCS_FLAGS) -f verilog.f +incdir+../model -timescale=$(TIME_SCALE) +prof +define+CKTCOMP

# run rule:
run: vcs
	@echo ""
	@echo Now Running ./simv
	@echo ==================================================
	./simv +vcs+finish+$(TRAN_TIME) -l simv.log

run_wave: vcs
	@echo ""
	@echo Now Running ./simv +wave
	@echo ==================================================
	./simv +vcs+finish+$(TRAN_TIME) -l simv.log +wave +vpdbufsize+200 +vpdfileswitchsize+200

clean:
	\rm -rf simv* csrc ucli.key vc_hdrs.h simv.log *.vpd DVEfiles

