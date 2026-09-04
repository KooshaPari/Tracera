SHELL := /bin/bash
COMPOSE := docker compose -f docker-compose.dev.yml
SCRIPT := scripts/dev-stack-seed.sh

.PHONY: up down logs ps reset seed

up:
	$(COMPOSE) up -d

down:
	$(COMPOSE) down

logs:
	$(COMPOSE) logs -f --tail=100

ps:
	$(COMPOSE) ps

reset:
	$(COMPOSE) down -v --remove-orphans

seed:
	bash $(SCRIPT)
