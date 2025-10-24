
all: run_uvicorn

# самая простая команда hi
# .PHONY нужен чтобы make не ассоциировал hi с файлом
.PHONY: hi
# описание команды
hi:
	echo "Hi"


# --- init project ---

.PHONY: requirements
# команда requirements будет вызываться при изменении pyproject.toml файла
requirements: pyproject.toml
	poetry lock  # генерация poetry.lock файла
	poetry install --no-root  # установка всех необходимых пакетов

# --- QA ---

.PHONY: flake8
# тут на вход получается переменная ARGS
# команда будет требовать перед собой успешного выполнения команды requirements
flake8: requirements
	poetry run flake8 $(ARGS)

# --- poetry add package ---

.PHONY: add_package
# тут на вход получается переменная ARGS
# чтобы передать ее при вызове можно написать:
# make add_package ARGS="--group test flake8"
# команда будет требовать перед собой успешного выполнения команды requirements
add_package: requirements
	poetry add $(ARGS)


# --- run app ---

.PHONY: run_uvicorn
# команда будет требовать перед собой успешного выполнения команды requirements
run_uvicorn: requirements
	poetry run uvicorn src.main:app --reload $(ARGS)
