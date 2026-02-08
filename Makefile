.PHONY: help dev dev-tui dev-down dev-logs dev-restart dev-status install-native \
	quality quality-backend quality-frontend quality-pc quality-report quality-report-watch quality-watch quality-last quality-rerun \
	quality-external quality-go-external quality-python-external quality-frontend-external \
	check lint type-check format test \
	type-check-ty test-python-parallel test-python-uv \
	test-setup validate test-validate-frontend test-validate-backend test-validate-backend-go test-validate-backend-python test-validate-report test-pyramid \
	load-test load-test-smoke load-test-load load-test-stress load-test-spike load-test-soak load-test-report \
	generate-contracts check-contracts clean-locks

# Platform detection
PLATFORM := $(shell uname -s | tr '[:upper:]' '[:lower:]')
ARCH := $(shell uname -m)

# Process Compose config selection (all under config/)
ifeq ($(PLATFORM),linux)
    PC_CONFIG := -f config/process-compose.yaml -f config/process-compose.linux.yaml
else ifeq ($(findstring mingw,$(PLATFORM)),mingw)
    PC_CONFIG := -f config/process-compose.yaml -f config/process-compose.windows.yaml
else
    PC_CONFIG := -f config/process-compose.yaml
endif

# Variables
NAMESPACE ?= tracertm
# Prefer venv tools so "make quality" / "make quality-python" work without them on PATH (pip install -e ".[dev]" or uv sync)
RUFF  := $(if $(wildcard .venv/bin/ruff),.venv/bin/ruff,ruff)
PYTEST := $(if $(wildcard .venv/bin/pytest),.venv/bin/pytest,pytest)

SMART_CMD := bash scripts/shell/smart-command.sh
FORMATTER := python3 $(shell pwd)/scripts/python/test-summary-formatter.py

# Optional faster/alternative type checkers (venv-first)
TY           := $(if $(wildcard .venv/bin/ty),.venv/bin/ty,ty)
# PYTHONPATH for ty/pytest so src/ is importable; set in Python targets
export PYTHONPATH ?= $(shell pwd)/src
# Optional: PYTEST_EXTRA="-n auto" for parallel tests (pytest-xdist)
PYTEST_EXTRA ?=

# Colors
GREEN  := \033[0;32m
YELLOW := \033[1;33m
BLUE   := \033[0;34m
CYAN   := \033[0;36m
NC     := \033[0m

help: ## Show this help
	@echo '$(GREEN)TraceRTM - Native Development$(NC)'
	@echo ''
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-20s$(NC) %s\n", $$1, $$2}'

#############################################################################
# Installation
#############################################################################

install-native: ## Install all native dependencies (one-time setup)
	@echo '$(GREEN)Installing native development dependencies...$(NC)'
	@bash scripts/shell/setup-native-dev.sh

verify-install: ## Verify installation
	@echo '$(GREEN)Verifying installation...$(NC)'
	@command -v process-compose >/dev/null || { echo "❌ process-compose not found"; exit 1; }
	@command -v postgres >/dev/null || { echo "❌ postgres not found"; exit 1; }
	@command -v redis-server >/dev/null || { echo "❌ redis not found"; exit 1; }
	@command -v caddy >/dev/null || { echo "❌ caddy not found"; exit 1; }
	@command -v prometheus >/dev/null || { echo "❌ prometheus not found"; exit 1; }
	@echo '$(GREEN)✅ All tools installed$(NC)'

#############################################################################
# Development
#############################################################################

dev: ## Start all services (detached). Preflight auto-starts infra if needed; failures show details (no rtm dev check).
	@echo '$(GREEN)Starting TraceRTM development environment...$(NC)'
	@PYTHONPATH="$(shell pwd)/src" PC_CONFIG="$(PC_CONFIG)" $(if $(wildcard .venv/bin/python),.venv/bin/python,python3) scripts/python/dev-start-with-preflight.py up -d --logs-truncate
	@echo ''
	@echo '$(GREEN)Services available at:$(NC)'
	@echo '  Gateway:    http://localhost:4000'
	@echo '  Go API:     http://localhost:8080'
	@echo '  Python API: http://localhost:8000'
	@echo '  Doc site:   http://localhost:3001  (or http://localhost:4000/documentation)'
	@echo '  Storybook:  http://localhost:6006  (or http://localhost:4000/storybook)'
	@echo '  Grafana:    http://localhost:3000'
	@echo '  Prometheus: http://localhost:9090'
	@echo '  Neo4j:      http://localhost:7474'
	@echo ''
	@echo 'View dashboard: make dev-tui'
	@echo 'View logs:      make dev-logs'

dev-tui: ## Start with interactive TUI dashboard. Preflight auto-starts infra if needed; failures show details (no rtm dev check).
	@PYTHONPATH="$(shell pwd)/src" PC_CONFIG="$(PC_CONFIG)" $(if $(wildcard .venv/bin/python),.venv/bin/python,python3) scripts/python/dev-start-with-preflight.py up --logs-truncate

dev-down: ## Stop all services
	@echo '$(GREEN)Stopping all services...$(NC)'
	@process-compose down --port 18080

dev-logs: ## Show logs for all services
	@process-compose logs --port 18080

dev-logs-follow: ## Follow logs (optionally for specific service)
	@if [ -z "$(SERVICE)" ]; then \
		process-compose logs -f --port 18080; \
	else \
		process-compose process logs -f $(SERVICE) --port 18080; \
	fi

dev-restart: ## Restart specific service (make dev-restart SERVICE=postgres)
	@if [ -z "$(SERVICE)" ]; then \
		echo "Usage: make dev-restart SERVICE=<service-name>"; \
		exit 1; \
	fi
	@process-compose process restart $(SERVICE) --port 18080

dev-status: ## Show service status
	@process-compose process list --port 18080

#############################################################################
# Development CLI Tools
#############################################################################

dev-health: ## Check health of all services
	@./scripts/dev health

dev-seed: ## Seed database with test data
	@./scripts/dev seed

dev-seed-full: ## Seed database with comprehensive test data
	@./scripts/dev seed --comprehensive

dev-reset: ## Reset database (WARNING: destructive)
	@./scripts/dev reset

dev-clear: ## Clear all caches
	@./scripts/dev clear --all

dev-clear-redis: ## Clear Redis cache only
	@./scripts/dev clear --redis

dev-clear-neo4j: ## Clear Neo4j graph data only
	@./scripts/dev clear --neo4j

dev-init: ## Initialize development environment
	@./scripts/dev init

dev-cli: ## Show dev CLI help
	@./scripts/dev --help

#############################################################################
# Quality & Validation
#############################################################################

lint: ## Run naming/LOC guards, then Go, Python, and frontend linters
	@$(SMART_CMD) lint "$(MAKE) lint-naming lint-go lint-python lint-frontend"

lint-naming: ## Naming explosion + LOC guards
	@echo '$(GREEN)Running naming explosion guards and file LOC limits...$(NC)'
	@bash scripts/shell/check-file-loc.sh
	@bash scripts/shell/check-naming-explosion-python.sh
	@bash scripts/shell/check-naming-explosion-go.sh
	@cd frontend && bash scripts/check-naming-explosion.sh

lint-frontend: ## Frontend linters only (oxlint via bun)
	@echo '$(GREEN)Running frontend linters (oxlint)...$(NC)'
	@cd frontend && bun run format && bun run lint

lint-go: ## Go linters only (gofumpt check + vet + golangci-lint)
	@echo '$(GREEN)Running Go linters...$(NC)'
	@cd backend && gofumpt -w . && go vet ./...
	@GOMAXPROCS=1 GOGC=20 ./scripts/lint-go-chunks.sh

lint-python: ## Python linters only (ruff check + format check)
	@echo '$(GREEN)Running Python linters...$(NC)'
	@$(RUFF) format src/ tests/
	@$(RUFF) check src/ tests/ --output-format=grouped

quality: ## Per-step parallel quality (lint/type/build/test)
	@bash scripts/shell/run-quality-split.sh

quality-report: ## Parse .quality/logs and print action plan
	@bash scripts/shell/quality-report.sh

#############################################################################
# Quality - External Tools (Phase 5 Maximum Strictness)
#############################################################################

quality-external: quality-go-external quality-python-external quality-frontend-external ## Run all external quality tools (CVE, race, security, dead code)

quality-go-external: ## Go: CVE scanning, race detection, and advanced static analysis
	@echo '$(CYAN)[Go] Running external quality tools...$(NC)'
	@echo '$(YELLOW)  → govulncheck (CVE scanning)$(NC)'
	@cd backend && govulncheck ./... || { echo '$(YELLOW)⚠️  govulncheck not installed: go install golang.org/x/vuln/cmd/govulncheck@latest$(NC)'; }
	@echo '$(YELLOW)  → go build -race (race detection)$(NC)'
	@cd backend && go build -race ./... || { echo '$(YELLOW)⚠️  Race detection failed$(NC)'; exit 1; }
	@echo '$(YELLOW)  → go mod tidy (dependency validation)$(NC)'
	@cd backend && go mod tidy && git diff --exit-code go.mod go.sum || { echo '$(YELLOW)⚠️  go.mod/go.sum out of sync$(NC)'; exit 1; }
	@echo '$(GREEN)✅ Go external tools complete$(NC)'

quality-python-external: ## Python: Security scanning (bandit, semgrep, pip-audit), metrics (radon), architecture (import-linter, tach)
	@echo '$(CYAN)[Python] Running external quality tools...$(NC)'
	@echo '$(YELLOW)  → bandit (security linter)$(NC)'
	@bandit -r src/ --severity medium -f json -o .quality/baselines/python-bandit-latest.json || { echo '$(YELLOW)⚠️  bandit found security issues (review .quality/baselines/python-bandit-latest.json)$(NC)'; }
	@echo '$(YELLOW)  → pip-audit (CVE scanning)$(NC)'
	@pip-audit --strict || { echo '$(YELLOW)⚠️  pip-audit found vulnerabilities$(NC)'; }
	@echo '$(YELLOW)  → semgrep (security patterns)$(NC)'
	@semgrep --config=p/python --config=p/security-audit src/ || { echo '$(YELLOW)⚠️  semgrep not installed: brew install semgrep$(NC)'; }
	@echo '$(YELLOW)  → interrogate (docstring coverage)$(NC)'
	@interrogate --fail-under 85 src/ || { echo '$(YELLOW)⚠️  Docstring coverage below 85%$(NC)'; }
	@echo '$(YELLOW)  → radon (complexity metrics)$(NC)'
	@radon cc src/ -a -s --min=B || { echo '$(YELLOW)⚠️  High complexity detected$(NC)'; }
	@echo '$(YELLOW)  → import-linter (architecture validation)$(NC)'
	@lint-imports || { echo '$(YELLOW)⚠️  Architecture violations detected$(NC)'; }
	@echo '$(YELLOW)  → tach (module boundaries)$(NC)'
	@tach check || { echo '$(YELLOW)⚠️  Module boundary violations detected$(NC)'; }
	@echo '$(GREEN)✅ Python external tools complete$(NC)'

quality-frontend-external: ## TypeScript: Dead code detection (knip), circular deps (madge), type checking (tsc)
	@echo '$(CYAN)[TypeScript] Running external quality tools...$(NC)'
	@echo '$(YELLOW)  → tsc --noEmit (standalone type checking)$(NC)'
	@cd frontend && bun run tsc --noEmit || { echo '$(YELLOW)⚠️  TypeScript errors detected$(NC)'; exit 1; }
	@echo '$(YELLOW)  → knip (dead code detection)$(NC)'
	@cd frontend && knip --include files,exports,dependencies || { echo '$(YELLOW)⚠️  knip not installed: bun add -d knip$(NC)'; }
	@echo '$(YELLOW)  → madge (circular dependency detection)$(NC)'
	@cd frontend && madge --circular apps/web/src/ || { echo '$(YELLOW)⚠️  madge not installed: bun add -d madge$(NC)'; }
	@echo '$(GREEN)✅ TypeScript external tools complete$(NC)'

#############################################################################
# Quality - Validation
#############################################################################

validate: ## Comprehensive route & health validation (frontend + backend)
	@$(SMART_CMD) validate "$(MAKE) test-validate-frontend test-validate-backend"

test-validate-frontend: ## Frontend: Playwright E2E + Vitest API tests
	@echo '$(BLUE)[Frontend] Running comprehensive tests...$(NC)'
	@cd frontend/apps/web && \
		bun run test:e2e -- websocket-validation.spec.ts && \
		bun run test:e2e -- route-validation.spec.ts && \
		bun run test -- src/__tests__/api/routes-validation.comprehensive.test.ts

test-validate-backend: test-validate-backend-go test-validate-backend-python ## Backend: Go + Python tests

test-validate-backend-go: ## Go: route validation tests
	@echo '$(BLUE)[Backend] Running Go route validation tests...$(NC)'
	@cd backend && go test -v -race ./internal/handlers -run TestAllRoutes

test-validate-backend-python: ## Python: route validation tests
	@echo '$(BLUE)[Backend] Running Python route validation tests...$(NC)'
	@cd backend && PYTHONPATH="$(shell pwd)/src" $(PYTEST) tests/unit/api/test_routes_validation.py -v

test-pyramid: ## Verify test pyramid ratios (unit >> integration >> E2E)
	@bash backend/scripts/verify-test-pyramid.sh

#############################################################################
# Testing
#############################################################################

test: ## Run all tests (unit + integration)
	@$(SMART_CMD) test "$(MAKE) test-unit test-integration"

test-unit: ## Run unit tests (Go + Python + TS)
	@echo '$(CYAN)[Go] Unit tests...$(NC)'
	@cd backend && go test -v -short ./... | $(FORMATTER) go
	@echo '$(CYAN)[Python] Unit tests...$(NC)'
	@PYTHONPATH="$(shell pwd)/src" $(PYTEST) tests/ -v -m "unit" | $(FORMATTER) pytest
	@echo '$(CYAN)[TypeScript] Unit tests...$(NC)'
	@cd frontend/apps/web && bun run test --run | $(FORMATTER) vitest || true

test-integration: ## Run integration tests (Live-first: uses process-compose if available)
	@$(SMART_CMD) integration "$(MAKE) test-integration-live"

test-integration-live: ## Run integration tests against LIVE services (Postgres, Redis, NATS, Neo4j, Python)
	@echo '$(GREEN)═══════════════════════════════════════════════════════════════════════════$(NC)'
	@echo '$(GREEN)Running LIVE Integration Tests (Real Services)$(NC)'
	@echo '$(GREEN)═══════════════════════════════════════════════════════════════════════════$(NC)'
	@echo '$(CYAN)[Go] Live services tests...$(NC)'
	@cd backend/tests && go test -v -run TestLive_ ./integration/... | $(FORMATTER) go
	@echo ''
	@echo '$(CYAN)[Python] Live services tests...$(NC)'
	@PYTHONPATH="$(shell pwd)/src" $(PYTEST) backend/tests/integration/test_full_agent_lifecycle.py -v | $(FORMATTER) pytest
	@echo '$(GREEN)✅ Live integration tests complete$(NC)'

test-e2e: ## Run E2E tests only (Playwright for frontend, full backend)
	@echo '$(GREEN)═══════════════════════════════════════════════════════════════════════════$(NC)'
	@echo '$(GREEN)Running E2E Tests (Python + TypeScript/Playwright)$(NC)'
	@echo '$(GREEN)═══════════════════════════════════════════════════════════════════════════$(NC)'
	@echo '$(CYAN)[Python] E2E tests...$(NC)'
	@PYTHONPATH="$(shell pwd)/src" $(PYTEST) tests/ -v -m e2e 2>/dev/null || true
	@echo ''
	@echo '$(CYAN)[TypeScript] Playwright E2E tests...$(NC)'
	@cd frontend/apps/web && bun run test:e2e 2>/dev/null || true
	@echo '$(GREEN)✅ E2E tests complete$(NC)'

#############################################################################
# Load Testing
#############################################################################

load-test: ## Consolidated load testing (default: smoke)
	@mkdir -p .results/load
	@$(MAKE) load-test-$(if $(SCENARIO),$(SCENARIO),smoke)

load-test-smoke: ## Run smoke test (1-5 users, 1 minute)
	@echo '$(GREEN)Running smoke test...$(NC)'
	k6 run --summary-export=.results/load/smoke-summary.json tests/load/k6/scenarios/smoke.js

load-test-load: ## Run load test (100 users, 18 minutes)
	@echo '$(GREEN)Running load test...$(NC)'
	k6 run --summary-export=.results/load/load-summary.json tests/load/k6/scenarios/load.js

load-test-stress: ## Run stress test (1000 users, 25 minutes)
	@echo '$(GREEN)Running stress test...$(NC)'
	k6 run --summary-export=.results/load/stress-summary.json tests/load/k6/scenarios/stress.js

load-test-spike: ## Run spike test (10→500 users, 7.5 minutes)
	@echo '$(GREEN)Running spike test...$(NC)'
	k6 run --summary-export=.results/load/spike-summary.json tests/load/k6/scenarios/spike.js

load-test-soak: ## Run soak test (50 users, 2+ hours)
	@echo '$(GREEN)Running soak test (endurance)...$(NC)'
	@echo '$(YELLOW)⚠️  This test takes 2+ hours to complete$(NC)'
	k6 run --summary-export=.results/load/soak-summary.json tests/load/k6/scenarios/soak.js

load-test-report: ## Generate HTML performance report
	@python3 tests/load/scripts/generate-report.py --results-dir .results/load --output .results/load/performance-report.html
	@echo '$(GREEN)Report saved to: .results/load/performance-report.html$(NC)'

#############################################################################
# Utilities
#############################################################################

clean: ## Clean build artifacts and logs
	@echo '$(GREEN)Cleaning build artifacts...$(NC)'
	@find . -type d -name '__pycache__' -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name '.pytest_cache' -exec rm -rf {} + 2>/dev/null || true
	@rm -rf .quality/logs/* 2>/dev/null || true
	@cd backend && go clean

clean-locks: ## Remove all command lock files
	@rm -f .process-compose/locks/*.lock
	@echo '$(GREEN)All command locks cleared$(NC)'

generate-contracts: ## Generate OpenAPI specs + SDKs/types
	@bash scripts/shell/generate-contracts.sh

check-contracts: ## Verify generated contracts are up-to-date
	@bash scripts/shell/check-generated-contracts.sh

# Default target
.DEFAULT_GOAL := help
