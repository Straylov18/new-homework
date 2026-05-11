SHELL := /bin/bash


all: run_uvicorn


# --- init project ---

.PHONY: requirements
requirements: pyproject.toml
	uv lock
	uv sync
	uv sync --group test

# --- QA ---

.PHONY: flake8
flake8: requirements
	uv run flake8 $(ARGS)

.PHONY: isort
isort: requirements
	uv run isort . --skip-gitignore --skip .uv-cache --check-only $(ARGS)

.PHONY: mypy
mypy: requirements
	uv run mypy . $(ARGS)

.PHONY: quality_assurance_isolated
quality_assurance_isolated: flake8 isort mypy

.PHONY: quality_assurance_full
quality_assurance_full: flake8 isort mypy

# --- QA fix ---

.PHONY: isort_fix
isort_fix: requirements
	uv run isort . --skip-gitignore --skip .uv-cache $(ARGS)

# --- uv add package ---

.PHONY: add_package
add_package: requirements
	uv add $(ARGS)

.PHONY: add_package_test
add_package_test: requirements
	uv add --group test $(ARGS)

.PHONY: add_package_deploy
add_package_deploy: requirements
	uv add --group deploy $(ARGS)

# --- run app ---

.PHONY: run_uvicorn
run_uvicorn: requirements
	uv run uvicorn src.main:app --reload --port 8000 $(ARGS)
