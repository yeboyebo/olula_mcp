VENV := .venv
.DEFAULT_GOAL := run
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip
REQUIREMENTS := requirements.txt
STAMP := $(VENV)/.deps_installed

.PHONY: run install setup

setup:
	python3.12 -m venv $(VENV)

run: $(STAMP)
	$(PYTHON) main.py

$(STAMP): $(REQUIREMENTS)
	$(PIP) install -r $(REQUIREMENTS)
	touch $(STAMP)

install: setup $(STAMP)
