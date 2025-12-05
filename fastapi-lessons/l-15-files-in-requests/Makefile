SHELL := /bin/bash


all: run_uvcorn


# --- init project ---

.PHONY: requirements
requirements: pyproject.toml
	poetry lock
	poetry install --no-root

# --- poetry add package ---

.PHONY: add_package
add_package: requirements
	poetry add $(ARGS)

.PHONY: add_package_test
add_package_test: requirements
	poetry add --group test $(ARGS)

.PHONY: add_package_deploy
add_package_deploy: requirements
	poetry add --group deploy $(ARGS)

# --- run app ---

.PHONY: run_uvcorn
run_uvcorn: requirements
	poetry run uvicorn src.main:app --reload $(ARGS)
