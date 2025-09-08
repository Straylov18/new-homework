all: QA

.PHONY: requirements
requirements:
	poetry install --no-root

.PHONY: flake8
flake8: requirements
	poetry run flake8

.PHONY: isort
isort: requirements
	poetry run isort

.PHONY: QA
QA: flake8 isort