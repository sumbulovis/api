SHELL := /bin/bash

# Load env from .env if present
# ifneq (,$(wildcard .env))
#     include .env
#     export $(shell sed -n 's/^[A-Za-z_][A-Za-z0-9_]*=.*/\0/p' .env)
# endif

POETRY := poetry
ALEMBIC := $(POETRY) run alembic
DC := docker-compose
APP_SVC := api
APP_CTR := api-app

.PHONY: migrate upgrade downgrade revision current history heads

## Show current revision
current:
	$(ALEMBIC) current

## Show history
history:
	$(ALEMBIC) history --verbose

## Upgrade to head
migrate upgrade:
	$(ALEMBIC) upgrade head

## Downgrade one step
downgrade:
	$(ALEMBIC) downgrade -1

## Create new revision: make revision msg="message"
revision:
	@if [ -z "$(msg)" ]; then echo "Usage: make revision msg=\"message\""; exit 1; fi
	$(ALEMBIC) revision -m "$(msg)"

.PHONY: dcu dcd dmigrate dcurrent dhistory ddowngrade drevision

## Docker compose up (detached)
dcu:
	$(DC) up -d
	
## Docker compose down (detached)
dcd:
	$(DC) down

## Dockerized: upgrade to head inside app container
dmigrate:
	$(DC) exec -e PYTHONPATH=/app $(APP_SVC) poetry run alembic upgrade head

## Dockerized: current revision
dcurrent:
	$(DC) exec -e PYTHONPATH=/app $(APP_SVC) poetry run alembic current

## Dockerized: history
dhistory:
	$(DC) exec -e PYTHONPATH=/app $(APP_SVC) poetry run alembic history --verbose

## Dockerized: downgrade one step
ddowngrade:
	$(DC) exec -e PYTHONPATH=/app $(APP_SVC) poetry run alembic downgrade -1

## Dockerized: create revision: make drevision msg="message"
drevision:
	@if [ -z "$(msg)" ]; then echo "Usage: make drevision msg=\"message\""; exit 1; fi
	$(DC) exec -e PYTHONPATH=/app $(APP_SVC) poetry run alembic revision -m "$(msg)"


