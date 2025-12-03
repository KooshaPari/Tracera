.PHONY: help build test clean deploy docker-up docker-down k8s-deploy k8s-delete

# Variables
DOCKER_REGISTRY ?=
IMAGE_TAG ?= latest
NAMESPACE ?= tracertm
KUBE_CONTEXT ?=

# Colors for output
GREEN  := \033[0;32m
YELLOW := \033[1;33m
NC     := \033[0m

help: ## Show this help message
	@echo '$(GREEN)TraceRTM - Available targets:$(NC)'
	@echo ''
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-20s$(NC) %s\n", $$1, $$2}'
	@echo ''

# Development
dev: ## Start development environment with Docker Compose
	@echo '$(GREEN)Starting development environment...$(NC)'
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d
	@echo '$(GREEN)Services available at:$(NC)'
	@echo '  API:      http://localhost:8000'
	@echo '  Backend:  http://localhost:8080'
	@echo '  Adminer:  http://localhost:8081'
	@echo '  Redis UI: http://localhost:8082'
	@echo '  Grafana:  http://localhost:3000'

dev-logs: ## Follow development logs
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml logs -f

dev-stop: ## Stop development environment
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml down

dev-clean: ## Clean development environment (remove volumes)
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml down -v

# Docker
docker-build: ## Build Docker images
	@echo '$(GREEN)Building Docker images...$(NC)'
	docker build -t tracertm-api:$(IMAGE_TAG) .
	docker build -t tracertm-backend:$(IMAGE_TAG) backend/

docker-push: docker-build ## Build and push Docker images to registry
	@if [ -z "$(DOCKER_REGISTRY)" ]; then \
		echo '$(YELLOW)Warning: DOCKER_REGISTRY not set. Set it with: make docker-push DOCKER_REGISTRY=registry.example.com$(NC)'; \
		exit 1; \
	fi
	@echo '$(GREEN)Tagging and pushing images to $(DOCKER_REGISTRY)...$(NC)'
	docker tag tracertm-api:$(IMAGE_TAG) $(DOCKER_REGISTRY)/tracertm-api:$(IMAGE_TAG)
	docker tag tracertm-backend:$(IMAGE_TAG) $(DOCKER_REGISTRY)/tracertm-backend:$(IMAGE_TAG)
	docker push $(DOCKER_REGISTRY)/tracertm-api:$(IMAGE_TAG)
	docker push $(DOCKER_REGISTRY)/tracertm-backend:$(IMAGE_TAG)

docker-up: ## Start production-like Docker Compose stack
	@echo '$(GREEN)Starting Docker Compose stack...$(NC)'
	docker-compose up -d

docker-down: ## Stop Docker Compose stack
	docker-compose down

docker-logs: ## Follow Docker Compose logs
	docker-compose logs -f

docker-clean: ## Clean Docker Compose stack (remove volumes)
	docker-compose down -v

# Testing
test: ## Run all tests
	@echo '$(GREEN)Running Python tests...$(NC)'
	pytest tests/ -v
	@echo '$(GREEN)Running Go tests...$(NC)'
	cd backend && go test -v ./...

test-python: ## Run Python tests only
	pytest tests/ -v --cov=src/tracertm --cov-report=html

test-go: ## Run Go tests only
	cd backend && go test -v -race -coverprofile=coverage.out ./...

test-integration: ## Run integration tests
	pytest tests/ -v -m integration

test-unit: ## Run unit tests
	pytest tests/ -v -m unit

# Code Quality
lint: ## Run linters
	@echo '$(GREEN)Running Python linters...$(NC)'
	ruff check src/ tests/
	ruff format --check src/ tests/
	@echo '$(GREEN)Running Go linters...$(NC)'
	cd backend && go vet ./...
	cd backend && gofmt -s -l .

format: ## Format code
	@echo '$(GREEN)Formatting Python code...$(NC)'
	ruff format src/ tests/
	@echo '$(GREEN)Formatting Go code...$(NC)'
	cd backend && gofmt -s -w .

type-check: ## Run type checking
	@echo '$(GREEN)Running mypy...$(NC)'
	mypy src/

security-scan: ## Run security scans
	@echo '$(GREEN)Running security scans...$(NC)'
	semgrep --config=p/security-audit src/
	cd backend && go install golang.org/x/vuln/cmd/govulncheck@latest
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
	docker-compose exec postgres psql -U tracertm -d tracertm

# Kubernetes
k8s-deploy: ## Deploy to Kubernetes
	@echo '$(GREEN)Deploying to Kubernetes...$(NC)'
	NAMESPACE=$(NAMESPACE) IMAGE_TAG=$(IMAGE_TAG) DOCKER_REGISTRY=$(DOCKER_REGISTRY) KUBE_CONTEXT=$(KUBE_CONTEXT) ./scripts/deploy.sh all

k8s-deploy-infra: ## Deploy infrastructure only
	@echo '$(GREEN)Deploying infrastructure to Kubernetes...$(NC)'
	NAMESPACE=$(NAMESPACE) ./scripts/deploy.sh infra

k8s-deploy-app: ## Deploy application only
	@echo '$(GREEN)Deploying application to Kubernetes...$(NC)'
	NAMESPACE=$(NAMESPACE) IMAGE_TAG=$(IMAGE_TAG) DOCKER_REGISTRY=$(DOCKER_REGISTRY) ./scripts/deploy.sh app

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

# Build
build: docker-build ## Alias for docker-build

# Clean
clean: ## Clean build artifacts
	@echo '$(GREEN)Cleaning build artifacts...$(NC)'
	find . -type d -name '__pycache__' -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name '.pytest_cache' -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name '.mypy_cache' -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name 'htmlcov' -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name '*.pyc' -delete 2>/dev/null || true
	find . -type f -name '.coverage' -delete 2>/dev/null || true
	cd backend && go clean 2>/dev/null || true
	rm -rf backend/coverage.out backend/coverage.html 2>/dev/null || true

# CI/CD
ci-test: ## Run CI tests (mimics GitHub Actions)
	@echo '$(GREEN)Running CI tests...$(NC)'
	@echo 'Python tests...'
	pytest tests/ -v --cov=src/tracertm
	@echo 'Go tests...'
	cd backend && go test -v -race -coverprofile=coverage.out ./...

ci-build: ## Build for CI
	@echo '$(GREEN)Building for CI...$(NC)'
	docker build -t tracertm-api:ci .
	docker build -t tracertm-backend:ci backend/

# Documentation
docs: ## Generate documentation
	@echo '$(GREEN)Generating documentation...$(NC)'
	@echo 'Documentation generation not yet implemented'

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

# Quick commands
up: docker-up ## Alias for docker-up
down: docker-down ## Alias for docker-down
logs: docker-logs ## Alias for docker-logs
ps: ## Show running containers
	docker-compose ps

# Default target
.DEFAULT_GOAL := help
