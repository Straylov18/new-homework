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
