# Common definitions for pheno-sdk Makefiles

ifndef PHENO_COMMON_INCLUDED
PHENO_COMMON_INCLUDED := 1

SHELL := /bin/bash

BLUE  := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[0;33m
RED   := \033[0;31m
NC    := \033[0m

PYTHON ?= python3
PIP ?= pip
PYTEST ?= pytest
RUFF ?= ruff
BLACK ?= black
ISORT ?= isort
MYPY ?= mypy
PIP_AUDIT ?= pip-audit
PIP_LICENSES ?= pip-licenses
PIPDEPTREE ?= pipdeptree

HELP_TITLE ?= Pheno-SDK Commands

.DEFAULT_GOAL ?= help

.PHONY: help print-var

help: ## Show available make targets
	@echo "$(BLUE)$(HELP_TITLE)$(NC)"
	@echo "$(BLUE)=====================$(NC)"
	@grep -h -E '^[a-zA-Z0-9_.-]+:.*##' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*## "}; {printf "  $(GREEN)%-24s$(NC) %s\n", $$1, $$2}'

print-var: ## Print value of VAR, usage: make print-var VAR=NAME
	@echo "$${VAR} = $${$${VAR}}"

endif
