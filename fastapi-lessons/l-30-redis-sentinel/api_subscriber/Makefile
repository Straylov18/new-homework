SHELL := /bin/bash


all: run_app


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

# --- QA ---

.PHONY: flake8
flake8: requirements
	poetry run flake8 $(ARGS)

.PHONY: isort
isort: requirements
	poetry run isort . --skip-gitignore --check-only $(ARGS)

.PHONY: full_qa
full_qa: flake8 isort

# --- QA fix ---

.PHONY: isort_fix
isort_fix: requirements
	poetry run isort . --skip-gitignore $(ARGS)

# --- run app ---

.PHONY: run_app
run_app: requirements
	poetry run python3 src/main.py $(ARGS)
