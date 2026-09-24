.PHONY: setup pipeline build test docs answer time-travel all clean

PYTHON ?= python

setup:
	$(PYTHON) -m venv .venv
	.venv/bin/python -m pip install -r requirements.txt

pipeline:
	$(PYTHON) -m src.pipeline

build:
	dbt build

test:
	$(PYTHON) -m pytest
	ruff check src tests_python

docs:
	dbt docs generate

answer:
	$(PYTHON) -m src.answer

time-travel:
	$(PYTHON) -m src.time_travel

all: pipeline build test docs answer time-travel

clean:
	$(PYTHON) -m src.clean

