# Test Infrastructure Makefile

.PHONY: help
help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

.PHONY: test-env-up
test-env-up: ## Start test environment (PostgreSQL, Redis, Neo4j, NATS)
	docker-compose -f ../docker-compose.test.yml up -d
	@echo "Waiting for services to be ready..."
	@sleep 5
	@echo "Test environment is ready!"
	@echo "PostgreSQL: localhost:5433"
	@echo "Redis: localhost:6380"
	@echo "Neo4j: localhost:7475 (HTTP), localhost:7688 (Bolt)"
	@echo "NATS: localhost:4223 (Client), localhost:8223 (Monitoring)"

.PHONY: test-env-down
test-env-down: ## Stop test environment
	docker-compose -f ../docker-compose.test.yml down

.PHONY: test-env-clean
test-env-clean: ## Stop test environment and remove volumes
	docker-compose -f ../docker-compose.test.yml down -v

.PHONY: test-env-logs
test-env-logs: ## Show logs from test environment
	docker-compose -f ../docker-compose.test.yml logs -f

.PHONY: test-unit
test-unit: ## Run unit tests
	go test -v -race -coverprofile=coverage.out ./testutil/...

.PHONY: test-integration
test-integration: ## Run integration tests with testcontainers
	go test -v -race -coverprofile=coverage-integration.out ./integration/...

.PHONY: test-integration-env
test-integration-env: test-env-up ## Run integration tests against docker-compose environment
	@export TEST_DATABASE_URL="postgres://testuser:testpass@localhost:5433/testdb?sslmode=disable" && \
	export TEST_REDIS_URL="localhost:6380" && \
	export TEST_NEO4J_URI="bolt://neo4j:testpassword@localhost:7688" && \
	export TEST_NATS_URL="nats://localhost:4223" && \
	go test -v -race ./integration/...

.PHONY: test-all
test-all: test-unit test-integration ## Run all tests

.PHONY: coverage
coverage: ## Generate coverage report
	go test -coverprofile=coverage.out ./...
	go tool cover -html=coverage.out -o coverage.html
	@echo "Coverage report generated: coverage.html"

.PHONY: coverage-integration
coverage-integration: test-integration ## Generate integration test coverage report
	go tool cover -html=coverage-integration.out -o coverage-integration.html
	@echo "Integration coverage report generated: coverage-integration.html"

.PHONY: benchmark
benchmark: ## Run benchmarks
	go test -bench=. -benchmem ./...

.PHONY: clean
clean: test-env-clean ## Clean up test artifacts and environment
	rm -f coverage.out coverage-integration.out coverage.html coverage-integration.html

.PHONY: deps
deps: ## Install test dependencies
	go get github.com/testcontainers/testcontainers-go
	go get github.com/jackc/pgx/v5/pgxpool
	go get github.com/nats-io/nats.go
	go get github.com/google/uuid
	go mod tidy

.PHONY: verify
verify: ## Verify test setup
	@echo "Checking Docker..."
	@docker --version || (echo "Docker not found. Please install Docker." && exit 1)
	@echo "Checking Go..."
	@go version || (echo "Go not found. Please install Go." && exit 1)
	@echo "Checking dependencies..."
	@go mod verify
	@echo "All checks passed!"

.PHONY: setup
setup: deps verify ## Initial setup for test infrastructure
	@echo "Test infrastructure setup complete!"
	@echo "Run 'make test-env-up' to start test services"
	@echo "Run 'make test-all' to run all tests"
