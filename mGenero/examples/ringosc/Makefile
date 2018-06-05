# Makefile for model/test generation

MODULE_NAME := lcvco_9GHz

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
	\rm -rf $(MODULE_NAME).v* $(MODULE_NAME).intermediate.v .mProbo* report*.html logfile .mGenero_modelgen_debug.log test.cfg* mProbo.log mGenero.log extracted_linear_model.yaml
