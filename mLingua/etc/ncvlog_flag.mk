# Note that 'mLINGUA_DIR' is already set up in setup.cshrc
mLINGUA_INC_DIR := $(mLINGUA_DIR)/samples_ncsim
mLINGUA_VLOG_LIB_DIR := -y $(mLINGUA_DIR)/samples_ncsim/prim -y $(mLINGUA_DIR)/samples_ncsim/stim -y $(mLINGUA_DIR)/samples_ncsim/meas -y $(mLINGUA_DIR)/samples_ncsim/misc
mLINGUA_PLI_DIR := $(mLINGUA_DIR)/samples_ncsim/pli

mLINGUA_NCVLOG_FLAGS := -y . $(mLINGUA_VLOG_LIB_DIR) +incdir+$(mLINGUA_INC_DIR) -sv +libext+.v+.vp +libext+.sv +define+NCVLOG -loadpli1 ${mLINGUA_PLI_DIR}/libpli.so:dave_boot -sem2009 -seed random +nc64bit
