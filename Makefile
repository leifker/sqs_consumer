ifeq (, $(shell which python3))
	$(error "python3 was not found in $(PATH). For installation instructions go to https://www.python.org/downloads/.")
endif

# define the name of the virtual environment directory
PY = python3
VENV = python/venv
BIN=$(VENV)/bin

all: test lint

$(VENV): requirements.txt requirements-dev.txt
	$(PY) -m venv $(VENV)
	$(BIN)/pip install --upgrade -r requirements.txt
	$(BIN)/pip install --upgrade -r requirements-dev.txt
	touch $(VENV)

.PHONY: test
test: $(VENV)
	$(PY) -m pytest tests/unit/

.PHONY: awslocal_test
awslocal_test: $(VENV)
	$(PY) -m pytest tests/awslocal/

.PHONY: lint
lint: $(VENV)
	flake8 project

.PHONY: run
run: $(VENV)
	$(PY) project/app.py

clean:
	rm -rf $(VENV)
	find . -type f -name *.pyc -delete
	find . -type d -name __pycache__ -delete
