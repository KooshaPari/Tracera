# Makefile for TraceRTM Backend

.PHONY: test test-coverage test-verbose test-security test-security-only clean setup setup-db build run \
 	build-backend build-cli build-desktop build-frontend build-all \
 	build-macos build-linux build-windows \
 	package-macos package-linux package-windows package-all \
 	dist-macos dist-linux dist-windows dist-all \
 	atlas-diff-supabase atlas-apply-supabase atlas-status-supabase \
 	gen-docs gen-docs-validate gen-docs-deploy docs-install docs-serve \
 	test-unit test-integration test-api test-e2e test-all coverage-report verify-coverage \
 	load-test load-test-smoke load-test-stress load-test-report install-k6 \
 	validate-schema validate-schema-keep-db sqlc-generate test-schema-validation \
 	test-contracts test-contracts-provider test-contracts-consumer test-contracts-all test-contracts-coverage

# Run all tests
test:
	cd tests && go test -v ./...

# Run only security tests
test-security:
	cd tests && go test -v ./security/...

# Run security tests with coverage
test-security-coverage:
	cd tests && go test -v -coverprofile=security-coverage.out ./security/...
	cd tests && go tool cover -html=security-coverage.out -o security-coverage.html
	@echo "Security coverage report: tests/security-coverage.html"

# Run security tests only (fast check)
test-security-only:
	@echo "Running security tests..."
	cd tests && go test -v -run Test.*Security ./security/ 2>&1 | grep -E "(PASS|FAIL|===)"

# Run tests with coverage
test-coverage:
	cd tests && go test -v -coverprofile=coverage.out ./...
	cd tests && go tool cover -html=coverage.out -o coverage.html
	@echo "Coverage report generated: tests/coverage.html"

# Run tests with race detection
test-race:
	cd tests && go test -v -race ./...

# Run tests verbosely
test-verbose:
	cd tests && go test -v -count=1 ./...

# Run specific test
test-one:
	cd tests && go test -v -run $(TEST) ./...

# Clean test artifacts
clean:
	cd tests && rm -f coverage.out coverage.html
	find . -name "*.test" -delete

# Install test dependencies
deps:
	go get -u github.com/stretchr/testify
	go get -u gorm.io/gorm
	go get -u gorm.io/driver/sqlite

# Run tests in watch mode (requires gotestsum)
watch:
	cd tests && gotestsum --watch

# Generate coverage badge
coverage-badge: test-coverage
	@echo "Coverage: $$(cd tests && go tool cover -func=coverage.out | grep total | awk '{print $$3}')"

# Setup databases (PostgreSQL + Neo4j)
setup-db:
	@echo "Setting up databases..."
	go run cmd/setup/main.go

# --- Local MinIO (Homebrew, no Docker) ---
# Install MinIO via Homebrew
minio-install:
	brew install minio

# Start MinIO as service (brew services), create bucket via Go (no UI, no mc)
minio-setup:
	@chmod +x scripts/minio-setup.sh
	@./scripts/minio-setup.sh

# Create bucket only (MinIO must already be running; reads S3_* from .env)
minio-bucket:
	@go run ./cmd/create-minio-bucket/

# Stop MinIO service
minio-stop:
	@brew services stop minio 2>/dev/null && echo "MinIO stopped." || echo "MinIO service not running."

# Database migrations with Atlas (Supabase as managed Postgres)

# Create a new migration for Supabase. Usage:
#   make atlas-diff-supabase name=add_items_table
atlas-diff-supabase:
		@echo "Creating Atlas migration for Supabase (env=supabase)..."
		atlas migrate diff --env supabase --name "$(name)"

# Apply all pending migrations to the Supabase database.
atlas-apply-supabase:
		@echo "Applying Atlas migrations to Supabase (env=supabase)..."
		atlas migrate apply --env supabase

# Show migration status for Supabase.
atlas-status-supabase:
		@echo "Atlas migration status for Supabase (env=supabase):"
		atlas migrate status --env supabase

# Build backend binary
build:
	go build -o tracertm-backend .

# Run backend
run: build
	./tracertm-backend

# Full setup: databases + build + run
setup: setup-db build
	@echo "✅ Setup complete! Run 'make run' to start the server"

# ═══════════════════════════════════════════════════════════════════════════
# MULTI-PLATFORM BUILD TARGETS
# ═══════════════════════════════════════════════════════════════════════════

# Build individual components
build-backend:
	@echo "🔨 Building backend..."
	go build -o tracertm-backend .

build-cli:
	@echo "🔨 Building CLI..."
	cd ../cli && pip install -e .

build-desktop:
	@echo "🔨 Building desktop app..."
	cd ../desktop && npm run tauri:build

build-frontend:
	@echo "🔨 Building frontend..."
	cd ../frontend && npm run build

# Build all components
build-all: build-backend build-cli build-desktop build-frontend
	@echo "✅ All components built successfully"

# Platform-specific builds
build-macos: build-backend build-cli build-desktop
	@echo "✅ macOS build complete"

build-linux: build-backend build-cli
	@echo "✅ Linux build complete"

build-windows: build-backend build-cli
	@echo "✅ Windows build complete"

# ═══════════════════════════════════════════════════════════════════════════
# PACKAGING TARGETS
# ═══════════════════════════════════════════════════════════════════════════

package-macos: build-macos
	@echo "📦 Packaging for macOS..."
	go run cmd/package/main.go macos

package-linux: build-linux
	@echo "📦 Packaging for Linux..."
	go run cmd/package/main.go linux

package-windows: build-windows
	@echo "📦 Packaging for Windows..."
	go run cmd/package/main.go windows

package-all: build-all
	@echo "📦 Packaging for all platforms..."
	go run cmd/package/main.go all

# ═══════════════════════════════════════════════════════════════════════════
# DISTRIBUTION TARGETS (build + package)
# ═══════════════════════════════════════════════════════════════════════════

dist-macos: package-macos
	@echo "✅ macOS distribution ready"

dist-linux: package-linux
	@echo "✅ Linux distribution ready"

dist-windows: package-windows
	@echo "✅ Windows distribution ready"

dist-all: package-all
	@echo "✅ All distributions ready"

# ═══════════════════════════════════════════════════════════════════════════
# OPENAPI DOCUMENTATION GENERATION
# ═══════════════════════════════════════════════════════════════════════════

# Install swag documentation tool
docs-install:
	@echo "📚 Installing swag..."
	go install github.com/swaggo/swag/cmd/swag@latest
	@echo "✅ swag installed: $$(swag --version)"

# Generate OpenAPI documentation from Go annotations
gen-docs:
	@echo "📚 Generating OpenAPI documentation..."
	@./scripts/generate-openapi.sh
	@echo "✅ OpenAPI documentation generated"

# Generate and validate OpenAPI documentation
gen-docs-validate:
	@echo "📚 Generating and validating OpenAPI documentation..."
	@./scripts/generate-openapi.sh --validate
	@echo "✅ OpenAPI documentation generated and validated"

# Generate and deploy OpenAPI documentation to docs-site
gen-docs-deploy:
	@echo "📚 Generating and deploying OpenAPI documentation..."
	@./scripts/generate-openapi.sh --validate --deploy
	@echo "✅ OpenAPI documentation generated and deployed"

# Serve OpenAPI documentation locally (requires swagger-ui)
docs-serve:
	@echo "📚 Serving OpenAPI documentation..."
	@if command -v swagger-ui &> /dev/null; then \
		swagger-ui serve -F swagger --no-open --port 8081 docs/swagger.yaml; \
	else \
		echo "⚠️  swagger-ui not found. Install with: npm install -g swagger-ui-watcher"; \
		echo "Or view at: https://editor.swagger.io/"; \
		echo "Load file: docs/swagger.json"; \
	fi

# ═══════════════════════════════════════════════════════════════════════════
# ENHANCED TEST TARGETS
# ═══════════════════════════════════════════════════════════════════════════

# Run unit tests with coverage (no external dependencies)
test-unit:
	@echo "🧪 Running unit tests..."
	@./test-commands.sh unit

# Run integration tests with docker-compose (requires PostgreSQL, Redis, NATS)
test-integration:
	@echo "🧪 Running integration tests..."
	@./test-commands.sh integration

# Run API tests (requires database)
test-api:
	@echo "🧪 Running API tests..."
	@./test-commands.sh api

# Run E2E tests with full docker-compose setup
test-e2e:
	@echo "🧪 Running E2E tests..."
	@./test-commands.sh e2e

# Run all tests with coverage
test-all:
	@echo "🧪 Running all tests..."
	@./test-commands.sh all

# Generate merged HTML coverage report
coverage-report:
	@echo "📊 Generating coverage report..."
	@./test-commands.sh coverage-report

# Verify coverage meets targets
verify-coverage:
	@echo "✓ Verifying coverage targets..."
	@./verify-coverage.sh

# ═══════════════════════════════════════════════════════════════════════════
# LOAD TESTING TARGETS
# ═══════════════════════════════════════════════════════════════════════════

# Install k6 load testing tool
install-k6:
	@echo "📦 Installing k6..."
	@if command -v k6 &> /dev/null; then \
		echo "✅ k6 already installed: $$(k6 version)"; \
	elif [[ "$$(uname)" == "Darwin" ]]; then \
		brew install k6; \
	elif [[ "$$(uname)" == "Linux" ]]; then \
		sudo snap install k6 || echo "Install k6 manually: https://k6.io/docs/get-started/installation/"; \
	else \
		echo "Install k6 manually: https://k6.io/docs/get-started/installation/"; \
	fi

# Run normal load test (100 req/s for 5 minutes)
load-test-normal:
	@echo "🔥 Running normal load test (100 req/s)..."
	@mkdir -p tests/load/results
	@cd tests/load && k6 run --env SCENARIO=normal service_load_test.js

# Run peak load test (1000 req/s for 3 minutes)
load-test-peak:
	@echo "⚡ Running peak load test (1000 req/s)..."
	@mkdir -p tests/load/results
	@cd tests/load && k6 run --env SCENARIO=peak service_load_test.js

# Run stress test (5000 req/s for 2 minutes)
load-test-stress:
	@echo "💪 Running stress test (5000 req/s)..."
	@mkdir -p tests/load/results
	@cd tests/load && k6 run --env SCENARIO=stress service_load_test.js

# Run spike test (sudden traffic increase)
load-test-spike:
	@echo "📈 Running spike test..."
	@mkdir -p tests/load/results
	@cd tests/load && k6 run --env SCENARIO=spike service_load_test.js

# Run soak test (sustained load for 30 minutes)
load-test-soak:
	@echo "⏱️  Running soak test (30 minutes)..."
	@mkdir -p tests/load/results
	@cd tests/load && k6 run --env SCENARIO=soak service_load_test.js

# Run ramp-up test (gradual load increase)
load-test-rampup:
	@echo "📊 Running ramp-up test..."
	@mkdir -p tests/load/results
	@cd tests/load && k6 run --env SCENARIO=rampup service_load_test.js

# Run quick smoke test (default scenario)
load-test-smoke:
	@echo "🔍 Running smoke test..."
	@mkdir -p tests/load/results
	@cd tests/load && k6 run service_load_test.js

# Run all load test scenarios
load-test-all:
	@echo "🚀 Running all load test scenarios..."
	@mkdir -p tests/load/results
	@$(MAKE) load-test-normal
	@$(MAKE) load-test-peak
	@$(MAKE) load-test-stress
	@$(MAKE) load-test-spike
	@echo "✅ All load tests completed!"
	@echo "📊 Results in: tests/load/results/"

# Run full load test suite (recommended scenarios)
load-test:
	@echo "🔥 Running recommended load test suite..."
	@mkdir -p tests/load/results
	@$(MAKE) load-test-normal
	@$(MAKE) load-test-peak
	@echo "✅ Load testing suite completed!"
	@echo "📊 Results in: tests/load/results/"

# View load test results
load-test-results:
	@echo "📊 Load test results:"
	@ls -lh tests/load/results/ 2>/dev/null || echo "No results found. Run 'make load-test' first."

# Clean load test results
load-test-clean:
	@echo "🧹 Cleaning load test results..."
	@rm -rf tests/load/results/*
	@echo "✅ Load test results cleaned"

# Load testing help
load-test-help:
	@echo "Load Testing Commands:"
	@echo "  make install-k6         - Install k6 load testing tool"
	@echo "  make load-test-smoke    - Quick smoke test"
	@echo "  make load-test-normal   - Normal load (100 req/s, 5min)"
	@echo "  make load-test-peak     - Peak load (1000 req/s, 3min)"
	@echo "  make load-test-stress   - Stress test (5000 req/s, 2min)"
	@echo "  make load-test-spike    - Spike test (sudden traffic)"
	@echo "  make load-test-soak     - Soak test (sustained, 30min)"
	@echo "  make load-test-rampup   - Ramp-up test (gradual increase)"
	@echo "  make load-test          - Run recommended suite (normal + peak)"
	@echo "  make load-test-all      - Run all scenarios"
	@echo "  make load-test-results  - View test results"
	@echo "  make load-test-clean    - Clean test results"
	@echo ""
	@echo "Custom configuration:"
	@echo "  cd tests/load && k6 run --env BASE_URL=https://api.example.com service_load_test.js"
	@echo "  cd tests/load && k6 run --env AUTH_TOKEN=xxx service_load_test.js"
	@echo ""
	@echo "See docs/guides/LOAD_TESTING_GUIDE.md for detailed documentation"

# ═══════════════════════════════════════════════════════════════════════════
# SCHEMA VALIDATION TARGETS
# ═══════════════════════════════════════════════════════════════════════════

# Validate schema alignment between migrations, GORM models, and sqlc models
validate-schema:
	@echo "🔍 Validating schema alignment..."
	@chmod +x scripts/validate_schema_alignment.sh
	@./scripts/validate_schema_alignment.sh

# Validate schema and keep test database for inspection
validate-schema-keep-db:
	@echo "🔍 Validating schema alignment (keeping test DB)..."
	@chmod +x scripts/validate_schema_alignment.sh
	@KEEP_TEST_DB=true ./scripts/validate_schema_alignment.sh

# Regenerate sqlc models
sqlc-generate:
	@echo "🔧 Regenerating sqlc models..."
	@sqlc generate
	@echo "✅ sqlc models generated"

# Full schema workflow: regenerate sqlc and validate
schema-check: sqlc-generate validate-schema
	@echo "✅ Schema check complete"

# Schema validation help
# Run schema validation tests (22 model tests)
test-schema-validation:
	@echo "Running schema validation tests..."
	TEST_DATABASE_URL="postgres://tracertm:tracertm_password@localhost:5432/tracertm?sslmode=disable" \
	go test -v ./internal/models -run "^Test"

# Run schema validation with coverage
test-schema-validation-coverage:
	@echo "Running schema validation tests with coverage..."
	@if [ -z "$$TEST_DATABASE_URL" ]; then \
		TEST_DATABASE_URL="postgres://tracertm:tracertm_password@localhost:5432/tracertm?sslmode=disable" \
		go test -v -coverprofile=schema-validation-coverage.out ./internal/models -run "^Test"; \
	else \
		go test -v -coverprofile=schema-validation-coverage.out ./internal/models -run "^Test"; \
	fi
	@go tool cover -html=schema-validation-coverage.out -o schema-validation-coverage.html
	@echo "Coverage report: schema-validation-coverage.html"

schema-help:
	@echo "Schema Validation Commands:"
	@echo "  make test-schema-validation          - Run 22 model schema validation tests"
	@echo "  make test-schema-validation-coverage - Run with coverage report"
	@echo "  make validate-schema                 - Validate schema alignment (migrations/GORM/sqlc)"
	@echo "  make validate-schema-keep-db         - Validate and keep test database for inspection"
	@echo "  make sqlc-generate                   - Regenerate sqlc models from queries"
	@echo "  make schema-check                    - Full workflow (generate + validate)"
	@echo ""
	@echo "Environment variables:"
	@echo "  TEST_DATABASE_URL - Test PostgreSQL connection string (default: tracertm credentials)"
	@echo "  DATABASE_URL      - PostgreSQL connection string for schema validation"
	@echo "  DB_HOST           - PostgreSQL host (default: localhost)"
	@echo "  DB_PORT           - PostgreSQL port (default: 5432)"
	@echo "  DB_USER           - PostgreSQL user (default: tracertm)"
	@echo "  DB_PASSWORD       - PostgreSQL password (default: tracertm_password)"
	@echo "  KEEP_TEST_DB      - Keep test database after validation (default: false)"
	@echo ""
	@echo "Examples:"
	@echo "  make test-schema-validation"
	@echo "  TEST_DATABASE_URL=postgres://user:pass@host:5432/db make test-schema-validation"
	@echo "  make validate-schema"
	@echo "  DB_HOST=myhost make validate-schema"
	@echo "  KEEP_TEST_DB=true make validate-schema"
	@echo ""
	@echo "Prerequisites:"
	@echo "  1. PostgreSQL must be running"
	@echo "  2. Database 'tracertm' must exist with schema 'tracertm'"
	@echo "  3. Migrations must be applied (alembic upgrade head)"

# Viewport API targets
viewport-validate:
	@echo "🔍 Validating viewport migration..."
	@./scripts/validate_viewport_migration.sh

viewport-test:
	@echo "🧪 Testing viewport API endpoints..."
	@./scripts/test_viewport_api.sh

viewport-verify-indexes:
	@echo "📊 Verifying spatial indexes..."
	@if [ -z "$$DATABASE_URL" ]; then \
		psql "postgres://tracertm:tracertm_password@localhost:5432/tracertm?sslmode=disable" \
			-c "SELECT indexname, indexdef FROM pg_indexes WHERE tablename = 'items' AND indexname LIKE '%position%';"; \
	else \
		psql "$$DATABASE_URL" -c "SELECT indexname, indexdef FROM pg_indexes WHERE tablename = 'items' AND indexname LIKE '%position%';"; \
	fi

viewport-explain:
	@echo "🔬 EXPLAIN viewport query..."
	@if [ -z "$$DATABASE_URL" ]; then \
		psql "postgres://tracertm:tracertm_password@localhost:5432/tracertm?sslmode=disable" \
			-c "EXPLAIN ANALYZE SELECT * FROM items WHERE project_id = 'test' AND position_x BETWEEN 0 AND 1000 AND position_y BETWEEN 0 AND 1000;"; \
	else \
		psql "$$DATABASE_URL" -c "EXPLAIN ANALYZE SELECT * FROM items WHERE project_id = 'test' AND position_x BETWEEN 0 AND 1000 AND position_y BETWEEN 0 AND 1000;"; \
	fi

viewport-help:
	@echo "Viewport API Commands:"
	@echo "  make viewport-validate       - Validate migration SQL syntax"
	@echo "  make viewport-test           - Test API endpoints with curl"
	@echo "  make viewport-verify-indexes - Verify spatial indexes are created"
	@echo "  make viewport-explain        - Show query plan for viewport query"
	@echo ""
	@echo "Environment variables:"
	@echo "  DATABASE_URL  - PostgreSQL connection string"
	@echo "  API_BASE      - API base URL (default: http://localhost:8080/api/v1)"
	@echo "  PROJECT_ID    - Test project ID (default: test-project-id)"
	@echo ""
	@echo "Full workflow:"
	@echo "  1. make migrate                - Run migrations"
	@echo "  2. make viewport-verify-indexes - Verify indexes"
	@echo "  3. make run                    - Start server"
	@echo "  4. make viewport-test          - Test API"

# Contract Testing
test-contracts-consumer:
	@echo "Running consumer contract tests..."
	cd ../tests/contracts && ./scripts/run-consumer-tests.sh

test-contracts-provider:
	@echo "Running provider contract verification..."
	cd ../tests/contracts && ./scripts/run-provider-tests.sh

test-contracts: test-contracts-consumer test-contracts-provider

test-contracts-all: test-contracts
	@echo "Running contract coverage report..."
	cd ../tests/contracts && ./scripts/generate-coverage-report.sh

test-contracts-coverage:
	@echo "Generating contract coverage report..."
	cd ../tests/contracts && ./scripts/generate-coverage-report.sh
