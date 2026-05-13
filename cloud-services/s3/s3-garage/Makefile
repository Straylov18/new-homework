SHELL := /bin/bash

all: start_s3_garage



.PHONY: generate_user
generate_user:
	./user_generator.sh $(ARGS)



.PHONY: start_s3_garage
start_s3_garage:
	docker compose up -d $(ARGS)

.PHONY: setup_s3_garage
setup_s3_garage:
	./s3_setup.sh $(ARGS)

.PHONY: start_and_setup_s3_garage
start_and_setup_s3_garage: start_s3_garage setup_s3_garage
