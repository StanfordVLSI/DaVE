# Makefile for running simulation
#
# available make target
# 1. make run  : run simulation w/o dumping waveforms
# 2. make wave : run simulation w/ dumping waveforms


TRAN_TIME := 200ns # transient simulation time (change the value as you wish)
TIME_SCALE := 1ps/1ps # time scale (change the value as you wish)
PP_CMD := python plot_abserr.py # post-processing script
SIMULATOR := $(mLINGUA_SIMULATOR) # vcs or ncsim

####################################
include $(mLINGUA_DIR)/etc/Makefile_mLINGUA.template

TOP_MODULE := test
VERILOG_FILES := $(TOP_MODULE).v
NCVLOG_CMD := ncverilog -top $(TOP_MODULE) $(VERILOG_FILES) $(mLINGUA_NCVLOG_FLAGS) -y ../model +incdir+../model +nctimescale+$(TIME_SCALE) -input hdl.tcl +ncaccess+r -profile -sem2009 -svseed random
VCS_CMD := vcs -top $(TOP_MODULE) $(VERILOG_FILES) $(mLINGUA_VCS_FLAGS) -y ../model -timescale=$(TIME_SCALE) +prof

