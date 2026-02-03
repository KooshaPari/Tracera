.PHONY: help dev dev-tui dev-down dev-logs dev-restart dev-status install-native \
	quality quality-backend quality-frontend quality-pc quality-report quality-report-watch quality-watch quality-last quality-rerun check lint type-check format test \
	type-check-ty type-check-basedpyright type-check-pyright test-python-parallel test-python-uv \
	load-test-smoke load-test-load load-test-stress load-test-spike load-test-soak load-test-websocket load-test-database load-test-all load-test-compare load-test-report

# Platform detection
PLATFORM := $(shell uname -s | tr '[:upper:]' '[:lower:]')
ARCH := $(shell uname -m)

# Process Compose config selection (all under config/)
ifeq ($(PLATFORM),linux)
    PC_CONFIG := -f config/process-compose.linux.yaml
else ifeq ($(findstring mingw,$(PLATFORM)),mingw)
    PC_CONFIG := -f config/process-compose.windows.yaml
else
    PC_CONFIG := -f config/process-compose.yaml
endif

# Variables
NAMESPACE ?= tracertm
# Prefer venv tools so "make quality" / "make quality-python" work without them on PATH (pip install -e ".[dev]" or uv sync)
RUFF  := $(if $(wildcard .venv/bin/ruff),.venv/bin/ruff,ruff)
MYPY  := $(if $(wildcard .venv/bin/mypy),.venv/bin/mypy,mypy)
PYTEST := $(if $(wildcard .venv/bin/pytest),.venv/bin/pytest,pytest)
# Optional faster/alternative type checkers (venv-first)
TY           := $(if $(wildcard .venv/bin/ty),.venv/bin/ty,ty)
BASEDPYRIGHT := $(if $(wildcard .venv/bin/basedpyright),.venv/bin/basedpyright,basedpyright)
PYRIGHT      := $(if $(wildcard .venv/bin/pyright),.venv/bin/pyright,pyright)
# PYTHONPATH for mypy/pytest so src/ is importable; set in Python targets
export PYTHONPATH ?= $(shell pwd)/src
# Optional: PYTEST_EXTRA="-n auto" for parallel tests (pytest-xdist)
PYTEST_EXTRA ?=

# Colors
GREEN  := \033[0;32m
YELLOW := \033[1;33m
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
	@process-compose $(PC_CONFIG) down

dev-logs: ## Show logs for all services
	@process-compose $(PC_CONFIG) logs

dev-logs-follow: ## Follow logs (optionally for specific service)
	@if [ -z "$(SERVICE)" ]; then \
		process-compose $(PC_CONFIG) logs -f; \
	else \
		process-compose $(PC_CONFIG) logs -f $(SERVICE); \
	fi

dev-restart: ## Restart specific service (make dev-restart SERVICE=postgres)
	@if [ -z "$(SERVICE)" ]; then \
		echo "Usage: make dev-restart SERVICE=<service-name>"; \
		exit 1; \
	fi
	@process-compose $(PC_CONFIG) restart $(SERVICE)

dev-status: ## Show service status
	@process-compose $(PC_CONFIG) process list

dev-scale: ## Scale a service (make dev-scale SERVICE=worker REPLICAS=3)
	@if [ -z "$(SERVICE)" ] || [ -z "$(REPLICAS)" ]; then \
		echo "Usage: make dev-scale SERVICE=<name> REPLICAS=<count>"; \
		exit 1; \
	fi
	@process-compose $(PC_CONFIG) scale $(SERVICE)=$(REPLICAS)

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

dev-generate: ## Generate test data (make dev-generate USERS=10 PROJECTS=5 ITEMS=50)
	@./scripts/dev generate $(if $(USERS),--users $(USERS)) $(if $(PROJECTS),--projects $(PROJECTS)) $(if $(ITEMS),--items $(ITEMS))

dev-init: ## Initialize development environment
	@./scripts/dev init

dev-cli: ## Show dev CLI help
	@./scripts/dev --help

#############################################################################
# Unified quality (lint, typecheck, build, tests) by codebase
# quality = per-step parallel run + report (run-quality-split.sh). REFRESH_INTERVAL=2 refreshes report as logs arrive.
# quality-pc = TUI (port 18080, fail reruns). quality-watch = file watcher re-runs quality (watchexec).
#############################################################################

quality: ## Per-step parallel quality (lint/type/build/test) + report. REFRESH_INTERVAL=2 to refresh report as logs arrive.
	@bash scripts/shell/run-quality-split.sh

quality-pc: ## Run quality in process-compose TUI (port 18080). Failed suites auto-rerun. Stop with ^C.
	@process-compose -f config/process-compose.quality.yaml -p 18080 up

quality-report: ## Parse .quality/logs and print action plan (run after quality or on demand)
	@bash scripts/shell/quality-report.sh

quality-report-watch: ## File-watched report: re-run report when .quality/logs or source changes (watchexec). Stop with ^C.
	@bash scripts/shell/run-quality-report-watch.sh

quality-watch: ## Real-time: re-run quality on file change (watchexec). Fallback: poll every QUALITY_WATCH_INTERVAL s. Stop with ^C.
	@bash scripts/shell/run-quality-watch.sh

quality-last: ## Show last quality run state (timestamp, steps or suites, failed)
	@if [ -f .quality/last-run.json ]; then jq -r 'if .steps then "Last run: \(.timestamp)\n  steps: \(.steps | keys | join(", "))\n  ok: \(.ok)\n  failed_steps: \(.failed_steps)" else "Last run: \(.timestamp)\n  go=\(.exit_go) python=\(.exit_python) frontend=\(.exit_frontend)\n  ok=\(.ok)\n  failed_suites: \(.failed_suites)" end' .quality/last-run.json 2>/dev/null || cat .quality/last-run.json; else echo "No last run (run make quality first)"; fi

quality-rerun: ## Re-run last quality (same as make quality; use after quality-last to re-check)
	@bash scripts/shell/run-quality-split.sh

check: quality ## Alias for quality

quality-backend: quality-go quality-python ## Backend: full Go suite + full Python suite (needs both toolchains)

quality-go: ## Go only: lint, proto-lint (if buf), build, test (no Python/ruff required)
	@echo '$(GREEN)[Go] Lint (vet + gofmt)...$(NC)'
	@$(MAKE) lint-go
	@echo '$(GREEN)[Go] Proto lint (if buf installed)...$(NC)'
	@$(MAKE) proto-lint
	@echo '$(GREEN)[Go] Build...$(NC)'
	@$(MAKE) -C backend build
	@echo '$(GREEN)[Go] Tests...$(NC)'
	@$(MAKE) test-go

quality-python: ## Python only: lint (ruff), architecture (tach), type-check (mypy), test (pytest) (no Go required)
	@echo '$(GREEN)[Python] Lint (ruff)...$(NC)'
	@$(MAKE) lint-python
	@echo '$(GREEN)[Python] Architecture (tach)...$(NC)'
	@$(MAKE) tach-check
	@echo '$(GREEN)[Python] Type-check (mypy)...$(NC)'
	@$(MAKE) type-check
	@echo '$(GREEN)[Python] Tests (pytest)...$(NC)'
	@$(MAKE) test-python

quality-frontend: ## Frontend only: lint (oxlint), typecheck (oxlint --type-aware), build, test. See docs/checklists/OXC_IMPLEMENTATION_CHECKLIST.md
	@echo '$(GREEN)[frontend] Quality (oxlint lint + typecheck, build, test)...$(NC)'
	@cd frontend && bun run quality

# Per-step targets for parallel quality (make quality-split)
quality-go-lint:   ; @$(MAKE) lint-go
quality-go-proto:  ; @$(MAKE) proto-lint
quality-go-build:  ; @$(MAKE) -C backend build
quality-go-test:   ; @$(MAKE) test-go
quality-py-lint:   ; @$(MAKE) lint-python
quality-py-type:   ; @$(MAKE) type-check
quality-py-test:   ; @$(MAKE) test-python
quality-fe-lint:   ; @(cd frontend && bun run lint)
quality-fe-type:   ; @(cd frontend && bun run typecheck)
quality-fe-build:  ; @(cd frontend && bun run build)
quality-fe-test:   ; @(cd frontend && bun run test)

#############################################################################
# Testing
#############################################################################

test: ## Run all backend tests (Python + Go)
	@echo '$(GREEN)Running Python tests...$(NC)'
	PYTHONPATH="$(shell pwd)/src" $(PYTEST) tests/ -v
	@echo '$(GREEN)Running Go tests...$(NC)'
	cd backend && go test -v ./...

test-python: ## Run Python tests only (pytest; use PYTEST_EXTRA="-n auto" for parallel)
	PYTHONPATH="$(shell pwd)/src" $(PYTEST) tests/ -v --cov=src/tracertm --cov-report=html $(PYTEST_EXTRA)

test-python-parallel: ## Run Python tests in parallel (pytest-xdist -n auto). Requires: pip install pytest-xdist
	PYTHONPATH="$(shell pwd)/src" $(PYTEST) tests/ -v --cov=src/tracertm --cov-report=html -n auto

test-python-uv: ## Run Python tests with uv (faster env). Requires: uv installed
	uv run pytest tests/ -v --cov=src/tracertm --cov-report=html

test-go: ## Run Go tests only
	cd backend && go test -v -race -coverprofile=coverage.out ./...

test-integration: ## Run integration tests
	PYTHONPATH="$(shell pwd)/src" $(PYTEST) tests/ -v -m integration

test-unit: ## Run unit tests (fast, then slow)
	PYTHONPATH="$(shell pwd)/src" $(PYTEST) tests/ -v -m "unit and not slow" --cov=src/tracertm --cov-report=html
	PYTHONPATH="$(shell pwd)/src" $(PYTEST) tests/ -v -m "unit and slow" --cov=src/tracertm --cov-append --cov-report=html

test-e2e: ## Run end-to-end tests
	PYTHONPATH="$(shell pwd)/src" $(PYTEST) tests/ -v -m e2e

#############################################################################
# Load Testing
#############################################################################

load-test-smoke: ## Run smoke test (1-5 users, 1 minute)
	@echo '$(GREEN)Running smoke test...$(NC)'
	k6 run tests/load/k6/scenarios/smoke.js

load-test-load: ## Run load test (100 users, 18 minutes)
	@echo '$(GREEN)Running load test...$(NC)'
	k6 run tests/load/k6/scenarios/load.js

load-test-stress: ## Run stress test (1000 users, 25 minutes)
	@echo '$(GREEN)Running stress test...$(NC)'
	k6 run tests/load/k6/scenarios/stress.js

load-test-spike: ## Run spike test (10→500 users, 7.5 minutes)
	@echo '$(GREEN)Running spike test...$(NC)'
	k6 run tests/load/k6/scenarios/spike.js

load-test-soak: ## Run soak test (50 users, 2+ hours)
	@echo '$(GREEN)Running soak test (endurance)...$(NC)'
	@echo '$(YELLOW)⚠️  This test takes 2+ hours to complete$(NC)'
	k6 run tests/load/k6/scenarios/soak.js

load-test-websocket: ## Run WebSocket load test (5000+ connections)
	@echo '$(GREEN)Running WebSocket load test...$(NC)'
	k6 run tests/load/websocket/ws-load-test.js

load-test-database: ## Run database connection pool stress test
	@echo '$(GREEN)Running database stress test...$(NC)'
	@echo '$(YELLOW)⚠️  Requires PostgreSQL running$(NC)'
	pgbench -c 1000 -j 100 -T 600 \
		-f tests/load/database/connection-pool-test.sql \
		-U tracertm tracertm

load-test-all: ## Run all load tests (sequential)
	@echo '$(GREEN)Running all load tests...$(NC)'
	@$(MAKE) load-test-smoke
	@$(MAKE) load-test-load
	@$(MAKE) load-test-stress
	@$(MAKE) load-test-spike
	@$(MAKE) load-test-websocket

load-test-compare: ## Compare current results with baseline
	@echo '$(GREEN)Comparing performance with baseline...$(NC)'
	python tests/load/scripts/compare-performance.py \
		--baseline tests/load/.baseline/load-baseline.json \
		--current load-test-summary.json \
		--threshold 10

load-test-report: ## Generate HTML performance report
	@echo '$(GREEN)Generating performance report...$(NC)'
	python tests/load/scripts/generate-report.py \
		--results-dir results \
		--output performance-report.html
	@echo '$(GREEN)Report saved to: performance-report.html$(NC)'

#############################################################################
# Chaos Engineering
#############################################################################

chaos-setup: ## Install and start Toxiproxy for chaos testing
	@bash scripts/shell/toxiproxy-setup.sh install
	@bash scripts/shell/toxiproxy-setup.sh start

chaos-start: ## Start Toxiproxy server
	@bash scripts/shell/toxiproxy-setup.sh start

chaos-stop: ## Stop Toxiproxy server
	@bash scripts/shell/toxiproxy-setup.sh stop

chaos-status: ## Check Toxiproxy status
	@bash scripts/shell/toxiproxy-setup.sh status

chaos-test: ## Run all chaos engineering tests
	@bash scripts/shell/run-chaos-tests.sh

chaos-test-latency: ## Run network latency chaos tests
	PYTHONPATH="$(shell pwd)/src" $(PYTEST) tests/chaos/test_network_latency.py -v

chaos-test-failures: ## Run connection failure chaos tests
	PYTHONPATH="$(shell pwd)/src" $(PYTEST) tests/chaos/test_connection_failures.py -v

chaos-test-resources: ## Run resource exhaustion chaos tests
	PYTHONPATH="$(shell pwd)/src" $(PYTEST) tests/chaos/test_resource_exhaustion.py -v

chaos-test-e2e: ## Run end-to-end resilience chaos tests
	PYTHONPATH="$(shell pwd)/src" $(PYTEST) tests/chaos/test_end_to_end_resilience.py -v

chaos-report: ## Open chaos test HTML report
	@open chaos-reports/chaos-report.html || xdg-open chaos-reports/chaos-report.html

#############################################################################
# Code Quality (see also: quality, quality-go, quality-python, quality-frontend)
#############################################################################

lint: lint-go lint-python lint-frontend ## Run Go, Python, and frontend linters

lint-frontend: ## Frontend linters only (oxlint via bun). See docs/checklists/OXC_IMPLEMENTATION_CHECKLIST.md
	@echo '$(GREEN)Running frontend linters (oxlint)...$(NC)'
	@cd frontend && bun run lint

lint-frontend-fix: ## Frontend lint auto-fix (oxlint --fix)
	@echo '$(GREEN)Fixing frontend lint (oxlint --fix)...$(NC)'
	@cd frontend && bun run lint:fix

typecheck-frontend: ## Frontend typecheck (oxlint --type-check --type-aware)
	@echo '$(GREEN)Running frontend typecheck (oxlint --type-aware)...$(NC)'
	@cd frontend && bun run typecheck

lint-go: ## Go linters only (gofumpt check + vet + golangci-lint)
	@echo '$(GREEN)Running Go linters...$(NC)'
	@cd backend && OUT=$$(gofumpt -l .); \
	if [ -n "$$OUT" ]; then echo '$(YELLOW)Go format: run make go-format$(NC)'; echo "$$OUT"; exit 1; fi; \
	go vet ./... && golangci-lint run --timeout=5m

lint-python: ## Python linters only (ruff check + format check)
	@echo '$(GREEN)Running Python linters...$(NC)'
	$(RUFF) check src/ tests/
	$(RUFF) format --check src/ tests/

lint-python-fix: ## Python lint auto-fix (ruff check --fix; does not format)
	@echo '$(GREEN)Fixing Python lint (ruff check --fix)...$(NC)'
	$(RUFF) check src/ tests/ --fix

tach-check: ## Python module boundaries (tach); requires tach.toml and tach installed
	@command -v tach >/dev/null 2>&1 || (echo 'tach not found (pip install tach or uv sync)' >&2; exit 1)
	tach check

format: ## Format code
	@echo '$(GREEN)Formatting Python code...$(NC)'
	$(RUFF) format src/ tests/
	@echo '$(GREEN)Formatting Go code...$(NC)'
	cd backend && gofumpt -w .

# Py/Go DX aliases (atoms-mcp-prod / atomsbot style; use - not : to avoid Make pattern rules)
py-lint: ; @$(MAKE) lint-python
py-lint-fix: ; @$(MAKE) lint-python-fix
py-format: ## Python format only
	@echo '$(GREEN)Formatting Python...$(NC)'
	$(RUFF) format src/ tests/
py-type-check: ; @$(MAKE) type-check
py-test: ; @$(MAKE) test-python
py-test-parallel: ; @$(MAKE) test-python-parallel
go-lint: ; @$(MAKE) lint-go
go-format: ## Go format only (gofumpt)
	@echo '$(GREEN)Formatting Go...$(NC)'
	cd backend && gofumpt -w .
go-test: ; @$(MAKE) test-go

type-check: ## Run type checking (mypy; default for quality)
	@echo '$(GREEN)Running mypy...$(NC)'
	PYTHONPATH="$(shell pwd)/src" $(MYPY) src/

type-check-ty: ## Run type checking with ty (Astral; fast, beta). Requires: uv/pip install ty
	@echo '$(GREEN)Running ty...$(NC)'
	PYTHONPATH="$(shell pwd)/src" $(TY) check src/

type-check-basedpyright: ## Run type checking with basedpyright. Requires: pip install basedpyright
	@echo '$(GREEN)Running basedpyright...$(NC)'
	PYTHONPATH="$(shell pwd)/src" $(BASEDPYRIGHT) src/

type-check-pyright: ## Run type checking with pyright. Requires: pip install pyright
	@echo '$(GREEN)Running pyright...$(NC)'
	PYTHONPATH="$(shell pwd)/src" $(PYRIGHT) src/

security-scan: ## Run security scans (semgrep, bandit, pip-audit, govulncheck)
	@echo '$(GREEN)Running security scans...$(NC)'
	@echo '$(GREEN)[Python] Semgrep...$(NC)'
	semgrep --config=p/security-audit src/
	@echo '$(GREEN)[Python] Bandit...$(NC)'
	$(if $(wildcard .venv/bin/bandit),.venv/bin/bandit,bandit) -r src/
	@echo '$(GREEN)[Python] pip-audit (dependency vulns)...$(NC)'
	$(if $(wildcard .venv/bin/pip-audit),.venv/bin/pip-audit,pip-audit)
	@echo '$(GREEN)[Go] govulncheck...$(NC)'
	cd backend && go install golang.org/x/vuln/cmd/govulncheck@latest 2>/dev/null || true
	cd backend && govulncheck ./...

# Database
db-migrate: ## Run database migrations
	@echo '$(GREEN)Running database migrations...$(NC)'
	alembic upgrade head

db-rollback: ## Rollback last migration
	@echo '$(GREEN)Rolling back last migration...$(NC)'
	alembic downgrade -1

db-reset: ## Reset database (drop all tables and re-migrate)
	@echo '$(GREEN)Resetting database...$(NC)'
	alembic downgrade base
	alembic upgrade head

db-shell: ## Open database shell
	@psql -h localhost -U tracertm -d tracertm

#############################################################################
# Monitoring
#############################################################################

grafana-dashboard: ## Open Grafana in browser
	@open http://localhost:3000 || xdg-open http://localhost:3000 || echo "Open http://localhost:3000"

prometheus-ui: ## Open Prometheus in browser
	@open http://localhost:9090 || xdg-open http://localhost:9090 || echo "Open http://localhost:9090"

metrics: ## Show quick metrics summary
	@echo '$(GREEN)Service Metrics:$(NC)'
	@curl -s http://localhost:9090/api/v1/query?query=up | jq -r '.data.result[] | "\(.metric.job): \(.value[1])"' 2>/dev/null || echo "Prometheus not available"

# Kubernetes
k8s-deploy: ## Deploy to Kubernetes
	@echo '$(GREEN)Deploying to Kubernetes...$(NC)'
	NAMESPACE=$(NAMESPACE) IMAGE_TAG=$(IMAGE_TAG) DOCKER_REGISTRY=$(DOCKER_REGISTRY) KUBE_CONTEXT=$(KUBE_CONTEXT) ./scripts/shell/deploy.sh all

k8s-deploy-infra: ## Deploy infrastructure only
	@echo '$(GREEN)Deploying infrastructure to Kubernetes...$(NC)'
	NAMESPACE=$(NAMESPACE) ./scripts/shell/deploy.sh infra

k8s-deploy-app: ## Deploy application only
	@echo '$(GREEN)Deploying application to Kubernetes...$(NC)'
	NAMESPACE=$(NAMESPACE) IMAGE_TAG=$(IMAGE_TAG) DOCKER_REGISTRY=$(DOCKER_REGISTRY) ./scripts/shell/deploy.sh app

k8s-status: ## Show Kubernetes deployment status
	@echo '$(GREEN)Kubernetes deployment status:$(NC)'
	kubectl get all -n $(NAMESPACE)

k8s-logs: ## Show Kubernetes logs
	@echo '$(GREEN)API logs:$(NC)'
	kubectl logs -l app=tracertm-api -n $(NAMESPACE) --tail=50
	@echo ''
	@echo '$(GREEN)Backend logs:$(NC)'
	kubectl logs -l app=tracertm-backend -n $(NAMESPACE) --tail=50

k8s-delete: ## Delete Kubernetes deployment
	@echo '$(YELLOW)Deleting Kubernetes deployment...$(NC)'
	kubectl delete namespace $(NAMESPACE)

k8s-port-forward: ## Port forward to API service
	@echo '$(GREEN)Port forwarding API to localhost:8000...$(NC)'
	kubectl port-forward -n $(NAMESPACE) svc/tracertm-api 8000:80

# CI/CD
ci-test: ## Run CI tests (mimics GitHub Actions)
	@echo '$(GREEN)Running CI tests...$(NC)'
	@echo 'Python tests...'
	PYTHONPATH="$(shell pwd)/src" $(PYTEST) tests/ -v --cov=src/tracertm
	@echo 'Go tests...'
	cd backend && go test -v -race -coverprofile=coverage.out ./...

# Documentation
docs: ## Generate documentation
	@echo '$(GREEN)Generating documentation...$(NC)'
	@echo 'Documentation generation not yet implemented'

# gRPC Code Generation
proto-gen: ## Generate gRPC code from protobuf definitions
	@echo '$(GREEN)Generating gRPC code...$(NC)'
	@bash scripts/shell/generate-grpc.sh

proto-gen-ts: ## Generate gRPC code including TypeScript
	@echo '$(GREEN)Generating gRPC code with TypeScript...$(NC)'
	@bash scripts/shell/generate-grpc.sh --typescript

proto-watch: ## Watch proto files and regenerate on changes
	@echo '$(GREEN)Watching proto files...$(NC)'
	@bash scripts/shell/generate-grpc.sh --watch

proto-test: ## Test gRPC connection and services
	@echo '$(GREEN)Testing gRPC services...$(NC)'
	@python scripts/python/test_grpc.py

proto-lint: ## Lint proto files (requires buf)
	@if command -v buf &> /dev/null; then \
		echo '$(GREEN)Linting proto files...$(NC)'; \
		buf lint; \
	else \
		echo '$(YELLOW)buf not installed. Install with: brew install bufbuild/buf/buf$(NC)'; \
	fi

proto-breaking: ## Check for breaking changes in proto files (requires buf)
	@if command -v buf &> /dev/null; then \
		echo '$(GREEN)Checking for breaking changes...$(NC)'; \
		buf breaking --against '.git#branch=main'; \
	else \
		echo '$(YELLOW)buf not installed. Install with: brew install bufbuild/buf/buf$(NC)'; \
	fi

# Installation
install: ## Install dependencies
	@echo '$(GREEN)Installing Python dependencies...$(NC)'
	uv pip install -e ".[dev]"
	@echo '$(GREEN)Installing Go dependencies...$(NC)'
	cd backend && go mod download

install-tools: ## Install development tools
	@echo '$(GREEN)Installing development tools...$(NC)'
	go install github.com/cosmtrek/air@latest
	go install honnef.co/go/tools/cmd/staticcheck@latest
	go install golang.org/x/vuln/cmd/govulncheck@latest
	go install google.golang.org/protobuf/cmd/protoc-gen-go@latest
	go install google.golang.org/grpc/cmd/protoc-gen-go-grpc@latest
	go install mvdan.cc/gofumpt@latest
	go install github.com/golangci/golangci-lint/cmd/golangci-lint@latest
	@echo '$(GREEN)gRPC tools installed. For buf: brew install bufbuild/buf/buf$(NC)'

#############################################################################
# Utilities
#############################################################################

clean: ## Clean build artifacts and logs
	@echo '$(GREEN)Cleaning build artifacts...$(NC)'
	@find . -type d -name '__pycache__' -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name '.pytest_cache' -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name '.mypy_cache' -exec rm -rf {} + 2>/dev/null || true
	@rm -rf .process-compose/logs/* 2>/dev/null || true
	@rm -rf htmlcov/
	@cd backend && go clean

logs-clean: ## Clean all service logs
	@rm -rf .process-compose/logs/*

data-clean: ## Clean all data directories (destructive!)
	@echo '$(YELLOW)⚠️  This will delete all local data!$(NC)'
	@read -p "Continue? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		rm -rf .prometheus/* .grafana/* .temporal/*; \
	fi

# Default target
.DEFAULT_GOAL := help
