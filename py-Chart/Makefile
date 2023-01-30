PYTHON = $(HOME)/Envs/respira/bin/python3

##########################################################################
#
#                   SETUP:  INSTALL PYTHON REQUIREMENTS
#					
#
##########################################################################

.PHONY: setup
setup:
	#make $(VENV)
	make deps

.PHONY: deps
deps: 
	@$(PYTHON) -m pip install -r requirements.txt > /dev/null


#$(VENV)/bin/activate: requirements.txt
#	$(BIN)/python3 -m venv $(VENV)
#	$(BIN)/pip install -r requirements.txt

.PHONY: clean
clean:
	#rm -rf $(VENV)
	rm -rf ./__pycache__

