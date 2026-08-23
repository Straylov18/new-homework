SHELL := /bin/bash


# Запустить только сервер (терминал 1).
.PHONY: server
server:
	$(MAKE) -C server run

# Запустить клиент (терминал 2, 3, …).
.PHONY: client
client:
	$(MAKE) -C client run
