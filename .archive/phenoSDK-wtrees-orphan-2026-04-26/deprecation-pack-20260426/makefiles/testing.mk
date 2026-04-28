# Testing Targets

.PHONY: test test-verbose test-quick test-cov test-cov-xml test-unit test-integration \
	test-docs performance test-container test-config test-mcp test-all-custom

test: ## Run default pytest suite
	@echo "Running tests..."
	@$(PYTEST) -q

test-verbose: ## Run pytest with verbose output
	@echo "Running tests (verbose)..."
	@$(PYTEST) -v

test-quick: ## Run fast failing-forward test selection
	@echo "Running quick tests..."
	@$(PYTEST) -x --ff

test-cov: ## Run tests with coverage summary and HTML report
	@echo "Running tests with coverage..."
	@$(PYTEST) --cov=src/pheno --cov-report=term-missing --cov-report=html
	@echo "Coverage report generated in htmlcov/"

test-cov-xml: ## Run tests with XML coverage output
	@echo "Running tests with XML coverage..."
	@$(PYTEST) --cov=src/pheno --cov-report=xml

test-unit: ## Run unit tests
	@echo "Running unit tests..."
	@$(PYTEST) -m unit

test-integration: ## Run integration tests
	@echo "Running integration tests..."
	@$(PYTEST) -m integration

test-docs: ## Run doctests discovered in documentation
	@echo "Running documentation doctests..."
	@$(PYTEST) --doctest-modules --doctest-glob="*.md" docs src

performance: ## Run performance benchmark suite
	@echo "Running performance benchmarks..."
	@mkdir -p reports/performance
	@$(PYTEST) tests/performance --benchmark-only --benchmark-json=reports/performance/benchmark.json --benchmark-storage=file://reports/performance/benchmarks.sqlite

test-container: ## Run container smoke tests
	@echo "Running container tests..."
	@$(PYTHON) tests/run_container_tests.py

test-config: ## Run configuration smoke tests
	@echo "Running config tests..."
	@$(PYTHON) tests/run_config_tests.py

test-mcp: ## Run MCP integration tests
	@echo "Running MCP tests..."
	@$(PYTHON) tests/run_mcp_tests.py

test-all-custom: ## Run all custom scripted test harnesses
	@echo "Running all custom tests..."
	@$(PYTHON) tests/run_container_tests.py
	@$(PYTHON) tests/run_config_tests.py
	@$(PYTHON) tests/run_mcp_tests.py
