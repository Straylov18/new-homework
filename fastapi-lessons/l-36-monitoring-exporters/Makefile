SHELL := /bin/bash

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
	docker compose build

.PHONY: compose_up_rebuild
compose_up_rebuild: compose_stop compose_rebuild
	docker compose up -d $(ARGS)

