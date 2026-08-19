SHELL := /bin/bash

# --- init project ---

.PHONY: requirements
requirements: pyproject.toml
	poetry lock
	poetry install --no-root

# --- docker ---

.PHONY: compose-build
compose-build:
	docker compose build

.PHONY: compose-up
compose-up:
	docker compose up -d

.PHONY: compose-up-build
compose-up-build:
	docker compose up -d --build

.PHONY: compose-down
compose-down:
	docker compose down

.PHONY: compose-logs
compose-logs:
	docker compose logs -f

.PHONY: worker-logs
worker-logs:
	docker compose logs -f worker

.PHONY: api-logs
api-logs:
	docker compose logs -f api

# --- local run (без docker) ---

.PHONY: run_api
run_api: requirements
	poetry run uvicorn src.main:app --reload $(ARGS)

.PHONY: run_worker
run_worker: requirements
	poetry run arq src.arq_app.WorkerSettings $(ARGS)

# --- QA ---

.PHONY: flake8
flake8: requirements
	poetry run flake8 $(ARGS)

.PHONY: isort
isort: requirements
	poetry run isort . --skip-gitignore --check-only $(ARGS)

.PHONY: isort_fix
isort_fix: requirements
	poetry run isort . --skip-gitignore $(ARGS)

.PHONY: full_qa
full_qa: flake8 isort
