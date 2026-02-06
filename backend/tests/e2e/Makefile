# E2E Test Makefile

.PHONY: test test-all test-auth test-project test-search test-graph test-agent test-realtime test-linking test-verbose test-short clean help

# Default target
help:
	@echo "E2E Test Commands:"
	@echo "  make test            - Run all E2E tests"
	@echo "  make test-verbose    - Run all E2E tests with verbose output"
	@echo "  make test-short      - Run E2E tests, skip slow tests"
	@echo "  make test-auth       - Run authentication flow tests"
	@echo "  make test-project    - Run project lifecycle tests"
	@echo "  make test-search     - Run search flow tests"
	@echo "  make test-graph      - Run graph traversal tests"
	@echo "  make test-agent      - Run agent coordination tests"
	@echo "  make test-realtime   - Run real-time update tests"
	@echo "  make test-linking    - Run item linking tests"
	@echo "  make test-coverage   - Run tests with coverage report"
	@echo "  make test-race       - Run tests with race detector"
	@echo "  make clean           - Clean up test artifacts"

# Run all E2E tests
test:
	@echo "Running all E2E tests..."
	go test -tags=e2e -timeout=30m ./...

# Run all E2E tests with verbose output
test-verbose:
	@echo "Running all E2E tests (verbose)..."
	go test -v -tags=e2e -timeout=30m ./...

# Run E2E tests, skip slow tests
test-short:
	@echo "Running E2E tests (skipping slow tests)..."
	go test -v -tags=e2e -short -timeout=15m ./...

# Run authentication flow tests
test-auth:
	@echo "Running authentication flow tests..."
	go test -v -tags=e2e -timeout=10m -run "TestE2E_.*Auth|TestE2E_.*Login|TestE2E_.*Unauthorized" ./...

# Run project lifecycle tests
test-project:
	@echo "Running project lifecycle tests..."
	go test -v -tags=e2e -timeout=10m -run "TestE2E_.*Project" ./...

# Run search flow tests
test-search:
	@echo "Running search flow tests..."
	go test -v -tags=e2e -timeout=10m -run "TestE2E_.*Search" ./...

# Run graph traversal tests
test-graph:
	@echo "Running graph traversal tests..."
	go test -v -tags=e2e -timeout=10m -run "TestE2E_.*Graph|TestE2E_.*Impact|TestE2E_.*Dependency|TestE2E_.*Critical" ./...

# Run agent coordination tests
test-agent:
	@echo "Running agent coordination tests..."
	go test -v -tags=e2e -timeout=10m -run "TestE2E_.*Agent" ./...

# Run real-time update tests
test-realtime:
	@echo "Running real-time update tests..."
	go test -v -tags=e2e -timeout=10m -run "TestE2E_.*Realtime|TestE2E_.*WebSocket|TestE2E_.*Broadcast" ./...

# Run item linking tests
test-linking:
	@echo "Running item linking tests..."
	go test -v -tags=e2e -timeout=10m -run "TestE2E_.*Link|TestE2E_.*Chain|TestE2E_.*Tree|TestE2E_.*Cycle" ./...

# Run tests with coverage
test-coverage:
	@echo "Running E2E tests with coverage..."
	go test -v -tags=e2e -timeout=30m -coverprofile=coverage.out ./...
	go tool cover -html=coverage.out -o coverage.html
	@echo "Coverage report generated: coverage.html"

# Run tests with race detector
test-race:
	@echo "Running E2E tests with race detector..."
	go test -v -tags=e2e -race -timeout=45m ./...

# Run specific test by name
test-run:
	@echo "Running specific test: $(TEST)"
	go test -v -tags=e2e -timeout=10m -run "$(TEST)" ./...

# Clean up test artifacts
clean:
	@echo "Cleaning up test artifacts..."
	rm -f coverage.out coverage.html
	docker system prune -f
	@echo "Cleanup complete"

# Check if Docker is running
check-docker:
	@echo "Checking Docker status..."
	@docker version > /dev/null 2>&1 || (echo "Error: Docker is not running" && exit 1)
	@echo "Docker is running"

# Run tests with Docker check
test-with-docker-check: check-docker test

# Run all tests in parallel (faster but uses more resources)
test-parallel:
	@echo "Running E2E tests in parallel..."
	go test -v -tags=e2e -timeout=30m -parallel=4 ./...

# Run tests with JSON output for CI/CD
test-json:
	@echo "Running E2E tests with JSON output..."
	go test -tags=e2e -timeout=30m -json ./... > test-results.json

# List all available tests
list-tests:
	@echo "Available E2E tests:"
	@go test -tags=e2e -list . ./... 2>/dev/null | grep "^Test"
