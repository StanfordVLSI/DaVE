# Note that 'mLINGUA_DIR' is already set up in setup.cshrc
mLINGUA_INC_DIR := $(mLINGUA_DIR)/samples_vcs
mLINGUA_VLOG_LIB_DIR := -y $(mLINGUA_DIR)/samples_vcs/prim -y $(mLINGUA_DIR)/samples_vcs/stim -y $(mLINGUA_DIR)/samples_vcs/meas -y $(mLINGUA_DIR)/samples_vcs/misc
mLINGUA_PLI_DIR := $(mLINGUA_DIR)/samples_vcs/pli

mLINGUA_VCS_FLAGS := -y . $(mLINGUA_VLOG_LIB_DIR) +incdir+$(mLINGUA_INC_DIR) -sverilog +cli +lint=PCWM +libext+.v+.vp +libext+.sv -notice +v2k -debug_pp +define+VCS+VCS_MSG_QUIET -full64 -P $(mLINGUA_PLI_DIR)/pli_get_timeunit.tab $(mLINGUA_PLI_DIR)/pli_get_timeunit.so -CFLAGS "-g -I$VCS_HOME/`vcs -platform`/lib" +acc+3 
