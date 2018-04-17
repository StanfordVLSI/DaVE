# Makefile for running VCS simulation
#
include $(mLINGUA_DIR)/etc/vcs_flag.mk
include $(mLINGUA_DIR)/etc/ncvlog_flag.mk

TOP_MODULE := test
TIME_SCALE := 1ns/1ns

VERILOG_FILES := test.v
TRAN_TIME := 500ns


# default rule:
all: vcs run

# vcs rule:
#
vcs:
	@echo ""
	@echo Now Compiling 
	@echo ==================================================
	vcs -top $(TOP_MODULE) $(VERILOG_FILES) $(mLINGUA_VCS_FLAGS) -y . -y .. -y /home/bclim/proj/DaVE/samples/library/model/meas/sv +incdir+../model -timescale=$(TIME_SCALE) +prof

# run rule:
run: vcs
	@echo ""
	@echo Now Running ./simv
	@echo ==================================================
	./simv +wave +vcs+finish+$(TRAN_TIME) -l simv.log

ncvlog:
	@echo ""
	@echo Now Compiling in NCVerilog
	@echo ==================================================
	@echo 'database -open waves.shm -into waves.shm -default' > hdl.tcl
	@echo 'run $(TRAN_TIME)' >> hdl.tcl
	@echo 'exit' >> hdl.tcl

	ncverilog -top $(TOP_MODULE) $(VERILOG_FILES) $(PWLGEN_NCVLOG_FLAGS) -f verilog.f +incdir+../model +nctimescale+$(TIME_SCALE) -input hdl.tcl +ncaccess+r -profile
	python plot_abserr.py

ncvlog_wave:
	@echo ""
	@echo Now Compiling in NCVerilog
	@echo ==================================================
	@echo 'database -open waves.shm -into waves.shm -default' > hdl.tcl
	@echo 'probe -creat -shm -all -depth all' >> hdl.tcl
	@echo 'run $(TRAN_TIME)' >> hdl.tcl
	@echo 'exit' >> hdl.tcl

	ncverilog -top $(TOP_MODULE) $(VERILOG_FILES) $(PWLGEN_NCVLOG_FLAGS) -f verilog.f +incdir+../model +nctimescale+$(TIME_SCALE) -input hdl.tcl +ncaccess+r -profile
	python plot_abserr.py


clean:
	\rm -rf simv* csrc ucli.key vc_hdrs.h simv.log DVEfiles *vpd vcs.prof *.txt INCA_libs waves.shm ncverilog.log hdl.tcl ncprof.out shm.prof *.norm *.log

cleanall: clean
	\rm -rf *.eps 
