SHELL := /bin/bash

API_DIR=api
WEB_DIR=web
DEV_TOOLS_DIR=dev-tools
ANSIBLE_DIR=ansible


all: compose_up_rebuild


# --- operations with docker compose ---


.PHONY: compose_stop
compose_stop:
	docker compose down --volumes
	docker compose stop $(ARGS)

.PHONY: compose_up
compose_up: compose_stop
	docker compose up -d $(ARGS)

.PHONY: compose_rebuild
compose_rebuild:
	cd api; make requirements; cd -
	docker compose build

.PHONY: compose_up_rebuild
compose_up_rebuild: compose_stop compose_rebuild
	docker compose up -d $(ARGS)


# --- ab ---


.PHONY: ab
ab:
	# успешные запросы на получение версии приложения
	ab -k -c 10 -n 1000 http://localhost:8000/api/v1/app-info/versions
	# успешные запросы на получение мемов
	ab -k -c 10 -n 2000 http://localhost:8000/api/v1/meme/1
	ab -k -c 10 -n 2000 http://localhost:8000/api/v1/meme/2
	ab -k -c 10 -n 2000 http://localhost:8000/api/v1/meme/0
	# запросы на получение мемов, которые приведут к 500-й ошибке
	ab -k -c 10 -n 2000 http://localhost:8000/api/v1/meme/100

	# успешные запросы на получение шуток
	ab -k -c 10 -n 2000 http://localhost:8000/api/v1/joke/2
	ab -k -c 10 -n 2000 http://localhost:8000/api/v1/joke/0
	ab -k -c 10 -n 2000 http://localhost:8000/api/v1/joke/1
	# запросы на получение шуток, которые приведут к 500-й ошибке
	ab -k -c 10 -n 2000 http://localhost:8000/api/v1/joke/100

	# запросы на логин, которые приведут к 422-й ошибке
	ab -k -c 10 -n 2000 http://localhost:8000/api/v1/user/login
