SHELL := /bin/bash

all: run

# --- install ---

.PHONY: requirements
requirements:
	poetry lock
	poetry install --no-root

# --- QA ---

.PHONY: flake8
flake8: requirements
	poetry run flake8 $(ARGS)

.PHONY: isort
isort: requirements
	poetry run isort . --skip-gitignore --check-only $(ARGS)

.PHONY: quality_assurance_full
quality_assurance_full: flake8 isort

# --- run ---

.PHONY: run
run: requirements
	poetry run python src/main.py
