SHELL := /usr/bin/env bash

.PHONY: bootstrap
bootstrap: 
	./.bootstrap.sh
	init_db

.PHONY: develop
develop:
	./bin/flask run

.PHONY: init_db
init_db:
	./bin/flask init-db

.PHONY: clean_db
clean_db:
	./bin/flask clean-db

.PHONY: fetch_tickets
fetch_tickets:
	./bin/flask fetch-tickets

