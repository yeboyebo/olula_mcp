VENV := .venv
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip
REQUIREMENTS := requirements.txt
STAMP := $(VENV)/.deps_installed

.PHONY: run install

run: $(STAMP)
	$(PYTHON) main.py

$(STAMP): $(REQUIREMENTS)
	$(PIP) install -r $(REQUIREMENTS)
	touch $(STAMP)

install:
	$(PIP) install -r $(REQUIREMENTS)
	touch $(STAMP)
