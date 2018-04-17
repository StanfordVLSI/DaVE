# Makefile for model/test generation

MODULE_NAME := senseamp

# default rule:
all: gen

# vcs rule:
#
gen:
	@echo ""
	@echo "Model generation/calibration/validation"
	@echo Now Compiling 
	@echo ==================================================
	python generate.py

clean:
	\rm -rf $(MODULE_NAME).v* .mProbo* report.html report_char.html logfile .mGenero_modelgen_debug.log test.cfg* *.v.intermediate mProbo.log mGenero.log
