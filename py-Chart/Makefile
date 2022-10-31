VENV 		  = vpyChart
BIN			  = $(VENV)/bin
SYSTEM_PYTHON = $(or $(shell which python3), $(shell which python))
PYTHON 		  = $(or $(wildcard $(VENV)/bin/python), $(SYSTEM_PYTHON))
##########################################################################
#
#                   SETUP:  INSTALL PYTHON REQUIREMENTS
#					
#
##########################################################################

.PHONY: setup
setup:
	make $(VENV)
	make deps

$(VENV):
	$(SYSTEM_PYTHON) -m venv $(VENV)
	touch $(VENV)

.PHONY: deps
deps: 
	$(BIN)/pip install -r requirements.txt >/dev/null


$(VENV)/bin/activate: requirements.txt
	$(BIN)/python3 -m venv $(VENV)
	$(BIN)/pip install -r requirements.txt

clean:
	rm -rf $(VENV)
	rm -rf ./__pycache__

.PHONY: clean
