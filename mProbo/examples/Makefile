# Makefile for running/cleaning all the examples


DIRS := $(sort $(shell find -mindepth 1 -maxdepth 1 -type d))

run:
	@echo ""
	@echo Running all the examples of model checking
	@echo ==========================================
	@for d in $(DIRS); do \
	  pushd ${PWD} > /dev/null; \
	  cd $$d; \
	  make; \
	  popd > /dev/null; \
  done

clean:
	@for d in $(DIRS); do \
	  pushd ${PWD} > /dev/null; \
	  cd $$d; \
	  make clean; \
	  popd > /dev/null; \
  done
