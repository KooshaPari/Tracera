# Pheno-SDK Standardized Makefile
# This Makefile provides consistent development tasks across all pheno-sdk projects
# Usage: Copy this file to your project root and customize if needed

.PHONY: help install install-dev test test-verbose lint format type-check security clean build docs pre-commit setup-dev atlas-health atlas-status atlas-monitor atlas-report monitor-atlas monitor-comprehensive health-dashboard

# Default target
help:
	@echo "Available targets:"
	@echo "  setup-dev     - Set up development environment"
	@echo "  install       - Install package in development mode"
	@echo "  install-dev   - Install with development dependencies"
	@echo "  test          - Run tests"
	@echo "  test-verbose  - Run tests with verbose output"
	@echo "  lint          - Run all linting and formatting checks"
	@echo "  format        - Format code with black and isort"
	@echo "  type-check    - Run type checking with mypy"
	@echo "  security      - Run security checks"
	@echo "  clean         - Clean build artifacts"
	@echo "  build         - Build package"
	@echo "  docs          - Generate documentation"
	@echo "  pre-commit    - Run pre-commit hooks on all files"
	@echo "  legacy-imports  - Run legacy import guard (and import-linter if available)"
	@echo "  unit-fastmcp  - Run FastMCP unit/integration tests with safe env"
	@echo "  atlas-health  - Generate atlas health report"
	@echo "  atlas-status  - Show atlas status"
	@echo "  atlas-monitor - Monitor atlas health continuously"
	@echo "  atlas-report  - Generate comprehensive atlas report"
	@echo "  monitor-atlas - Monitor atlas health"
	@echo "  monitor-comprehensive - Run comprehensive monitoring"
	@echo "  health-dashboard - Show health dashboard"

# Runtime shortcuts
serve:
	./zen serve http

dev:
	./zen dev

cli-help:
	python zen --help


# Development setup
setup-dev: install-dev pre-commit
	@echo "✅ Development environment ready!"

# Installation targets
install:
	pip install -e .

install-dev:
	pip install -e ".[dev,test,docs]"
	pre-commit install

# Testing targets
test:
	pytest --cov --cov-report=term-missing

test-verbose:
	pytest -v --cov --cov-report=term-missing --cov-report=html

test-integration:
	pytest -m integration

# Code quality targets
lint: format type-check security
	ruff check .
	@echo "✅ All linting checks passed!"

format:
	black .
	isort .
	@echo "✅ Code formatted!"

type-check:
	mypy .
	@echo "✅ Type checking complete!"

security:
	bandit -r . -f json -o bandit-report.json || true
	bandit -r .
	@echo "✅ Security check complete!"

# Pre-commit
pre-commit:
	pre-commit run --all-files

# Build and distribution
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf .ruff_cache/
	find . -type d -name __pycache__ -delete
	find . -type f -name "*.pyc" -delete

build: clean
	python -m build

# Documentation
docs:
	@echo "📚 Generating documentation..."
	@if [ -f "mkdocs.yml" ]; then \
		mkdocs build; \
	else \
		echo "No mkdocs.yml found. Skipping documentation generation."; \
	fi

# Development workflow shortcuts
dev-check: format lint test
	@echo "✅ All development checks passed!"

# Quick development cycle
quick-test:
	pytest --maxfail=1 -x

# Coverage report
coverage-report:
	pytest --cov --cov-report=html
	@echo "📊 Coverage report generated in htmlcov/"

# Performance profiling
profile:
	@echo "🔍 Running performance profiling..."
	python -m pytest --profile-svg

# Dependency management
update-deps:
	pip-compile --upgrade requirements.in
	pip-compile --upgrade requirements-dev.in

# Release helpers (semantic-release integration)
release-dry-run:
	semantic-release version --noop

release:
	semantic-release version

# Docker helpers (if Dockerfile exists)
docker-build:
	@if [ -f "Dockerfile" ]; then \
		docker build -t zen-mcp-server:latest .; \
	else \
		echo "No Dockerfile found."; \
	fi

docker-run:
	docker run --rm -it zen-mcp-server:latest

# Performance and benchmarking
benchmark:
	@test -d benchmarks && python -m pytest benchmarks/ --benchmark-only || echo "No benchmarks directory found."

atlas-health:
	@echo "Generating atlas health report..."
	python ../scripts/atlas_health.py --report

atlas-status:
	python ../scripts/atlas_health.py --status

atlas-report:
	@echo "Generating comprehensive atlas report..."
	python ../scripts/atlas_health.py --report --full-report --output docs/atlas_reports/atlas_health.json

monitor-atlas:
	@echo "Running atlas monitoring sequence..."
	python ../scripts/atlas_health.py --monitor

monitor-comprehensive:
	@echo "Running comprehensive monitoring workflow..."
	$(MAKE) test
	$(MAKE) lint
	$(MAKE) atlas-health
	$(MAKE) security

health-dashboard:
	@echo "Launching health dashboard..."
	python ../pheno-sdk/tools/dashboards/performance.py --live

# Legacy imports guard
.PHONY: legacy-imports
legacy-imports:
	@echo "🔎 Checking for legacy imports..."
	python scripts/ci_check_legacy_imports.py
	@echo "ℹ️  Running import-linter if available..."
	@command -v import-linter >/dev/null 2>&1 && import-linter || echo "(import-linter not installed; skipping)"
	@echo "✅ Legacy import check complete"



# FastMCP safe test runner
.PHONY: unit-fastmcp
unit-fastmcp:
	PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONPATH=../pheno-sdk/src:$(PYTHONPATH) MCP_TEST_TYPE=dry ZEN_TEST_PASSWORD=dummy ENABLED_PROVIDERS=OPENROUTER,GEMINI,OPENAI,XAI,CUSTOM,AEGIS,GOOSE,AIDER,CRUSH,MCP_AGENT,DIAL,CURSOR \
		uv run pytest -q \
		tests/unit/test_fastmcp_agent_client_streaming.py::test_fastmcp_agent_client_streams_and_finishes \
		tests/unit/test_fastmcp_agent_client_failure_stderr.py::test_fastmcp_agent_client_stderr_failure \
		tests/unit/test_fastmcp_agent_client_long_stream.py::test_fastmcp_agent_client_long_running_stream \
		tests/unit/test_fastmcp_agent_client_token_count.py::test_fastmcp_agent_client_token_count \
		tests/unit/test_fastmcp_agent_client_partial_crash.py::test_fastmcp_agent_client_partial_output_on_crash \
		tests/unit/test_fastmcp_agent_client_multiple_types.py::test_fastmcp_agent_client_works_for_multiple_agent_types \
		tests/integration/test_agent_manager_fastmcp_e2e.py::test_agent_manager_execute_agent_with_fastmcp_custom_bin

# Atlas Health Monitoring
