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

.PHONY: migration-generate
migration-generate: requirements
	# generate new revision based on current difference with db
	poetry run alembic revision --autogenerate -m "$(ARGS)"

.PHONY: migration-upgrade
migration-upgrade: requirements
	poetry run alembic upgrade head

.PHONY: migration-downgrade
migration-downgrade: requirements
	poetry run alembic downgrade -1

# --- run app ---

.PHONY: start_postgres
start_postgres:
	./start_postgres_in_docker.sh

.PHONY: start_redis
start_redis:
	./start_redis_in_docker.sh

.PHONY: run_uvcorn
run_uvcorn: requirements migration-upgrade
	poetry run uvicorn src.main:app --reload $(ARGS)

.PHONY: run_uvcorn_4_workers
run_uvcorn_4_workers: requirements migration-upgrade
	poetry run uvicorn src.main:app --workers 4 $(ARGS)
