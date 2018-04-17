# Makefile for model/test generation

MODULE_NAME := pfd1

# default rule:
all: gen

# vcs rule:
#
gen:
	@echo ""
	@echo "Model generation/calibration/validation"
	@echo Now Compiling 
	@echo ==================================================
	python generate.py |tee logfile

clean:
	\rm -rf $(MODULE_NAME).v* $(MODULE_NAME).intermediate.v .mProbo* report.html report_char.html logfile .mGenero_modelgen_debug.log test.cfg* mProbo.log mGenero.log
