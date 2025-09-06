all: QA

.PHONY: req
req:
	poetry install --no-root

.PHONY: flake8
flake8: req
	poetry run flake8

.PHONY: QA
QA: flake8