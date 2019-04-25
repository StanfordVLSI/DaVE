# assumes that mLINGUA_DIR has already been set

mLINGUA_INC_DIR := $(mLINGUA_DIR)/samples
mLINGUA_VLOG_LIB_DIR := -y $(mLINGUA_DIR)/samples/prim -y $(mLINGUA_DIR)/samples/stim -y $(mLINGUA_DIR)/samples/meas -y $(mLINGUA_DIR)/samples/misc
mLINGUA_PLI_DIR := $(mLINGUA_DIR)/samples/pli

# generate main flags for ncvlog

mLINGUA_NCVLOG_FLAGS := -y . $(mLINGUA_VLOG_LIB_DIR) +incdir+$(mLINGUA_INC_DIR) -sv +libext+.v+.vp +libext+.sv +define+NCVLOG -loadpli1 ${mLINGUA_PLI_DIR}/libpli.so:dave_boot -sem2009 -seed random +nc64bit

# append extra arguments as desired

ifneq ($(strip $(TOP_MODULE)),)
	mLINGUA_NCVLOG_FLAGS += -top $(TOP_MODULE)
endif

ifneq ($(strip $(TIME_SCALE)),)
	mLINGUA_NCVLOG_FLAGS += +nctimescale+$(TIME_SCALE)
endif

ifneq ("$(wildcard ncvlog.f)","")
	mLINGUA_NCVLOG_FLAGS += -f ncvlog.f
endif

