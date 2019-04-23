# assumes that mLINGUA_DIR is already defined
mLINGUA_INC_DIR := $(mLINGUA_DIR)/samples
mLINGUA_VLOG_LIB_DIR := -y $(mLINGUA_DIR)/samples/prim -y $(mLINGUA_DIR)/samples/stim -y $(mLINGUA_DIR)/samples/meas -y $(mLINGUA_DIR)/samples/misc
mLINGUA_PLI_DIR := $(mLINGUA_DIR)/samples/pli

# generate main flags for VCS
mLINGUA_VCS_FLAGS := -y . $(mLINGUA_VLOG_LIB_DIR) +incdir+$(mLINGUA_INC_DIR) -sverilog +cli +lint=PCWM +libext+.v+.vp +libext+.sv -notice +v2k -debug_pp +define+VCS+VCS_MSG_QUIET -full64 -P $(mLINGUA_PLI_DIR)/pli_get_timeunit.tab $(mLINGUA_PLI_DIR)/pli_get_timeunit.so -CFLAGS "-g -I$VCS_HOME/`vcs -platform`/lib" +acc+3 
# generate random seed used by VCS
VCS_RND_SEED := $(strip $(shell head -4 /dev/urandom |od -N 4 -D -A n| awk '{print $1}')) # random seed generation
