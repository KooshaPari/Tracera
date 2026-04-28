# PhenoSDK Unified Makefile
# Modular design with includes

.DEFAULT_GOAL := help

# Colors for output
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[0;33m
RED := \033[0;31m
NC := \033[0m

# Include modular makefiles
include makefiles/quality.mk
include makefiles/testing.mk
include makefiles/ci.mk
include makefiles/deps.mk

# ============================================================================
# Setup & Installation
# ============================================================================

.PHONY: install install-dev setup clean

install:
	@echo "$(BLUE)Installing phenoSDK...$(NC)"
	@pip install -e .
	@echo "$(GREEN)✓ Installation complete$(NC)"

install-dev:
	@echo "$(BLUE)Installing development dependencies...$(NC)"
	@pip install -e ".[dev,test]"
	@echo "$(GREEN)✓ Development installation complete$(NC)"

setup: install-dev
	@echo "$(BLUE)Setting up development environment...$(NC)"
	@pre-commit install || true
	@echo "$(GREEN)✓ Development environment ready!$(NC)"

clean:
	@echo "$(BLUE)Cleaning up...$(NC)"
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name ".coverage" -delete 2>/dev/null || true
	@find . -type f -name "coverage.xml" -delete 2>/dev/null || true
	@echo "$(GREEN)✓ Cleanup complete$(NC)"

# ============================================================================
# Development Workflow
# ============================================================================

.PHONY: dev pre-commit watch

dev: format lint test
	@echo "$(GREEN)✓ Development checks passed!$(NC)"

pre-commit:
	@echo "$(BLUE)Running pre-commit hooks...$(NC)"
	@pre-commit run --all-files || true

watch:
	@echo "$(BLUE)Watching for changes...$(NC)"
	@pytest-watch

# ============================================================================
# Documentation
# ============================================================================

.PHONY: docs docs-serve docs-build

docs:
	@echo "$(BLUE)Building documentation...$(NC)"
	@cd docs && make html || echo "$(YELLOW)⚠ Docs not configured$(NC)"

docs-serve:
	@echo "$(BLUE)Serving documentation...$(NC)"
	@cd docs && make serve || python -m http.server -d docs/_build/html

docs-build:
	@echo "$(BLUE)Building documentation for production...$(NC)"
	@cd docs && make clean html

# ============================================================================
# Release
# ============================================================================

.PHONY: build publish release

build:
	@echo "$(BLUE)Building distribution...$(NC)"
	@python -m build
	@echo "$(GREEN)✓ Build complete$(NC)"

publish:
	@echo "$(BLUE)Publishing to PyPI...$(NC)"
	@python -m twine upload dist/*

release: clean test build
	@echo "$(GREEN)✓ Ready for release!$(NC)"
	@echo "$(YELLOW)Run 'make publish' to upload to PyPI$(NC)"

# ============================================================================
# Utilities
# ============================================================================

.PHONY: loc count-lines version

loc:
	@echo "$(BLUE)Counting lines of code...$(NC)"
	@cloc src/ tests/ --exclude-dir=__pycache__,.pytest_cache || \
		echo "$(YELLOW)⚠ cloc not installed. Install with: brew install cloc$(NC)"

count-lines:
	@echo "$(BLUE)Line counts:$(NC)"
	@find src/ -name "*.py" | xargs wc -l | tail -1

version:
	@echo "$(BLUE)Current version:$(NC)"
	@python -c "import pheno; print(pheno.__version__)" 2>/dev/null || echo "Not installed"

# ============================================================================
# Help
# ============================================================================

.PHONY: help

help:
	@echo "$(BLUE)PhenoSDK Makefile Commands$(NC)"
	@echo ""
	@echo "$(GREEN)Setup & Installation:$(NC)"
	@echo "  make install       - Install phenoSDK"
	@echo "  make install-dev   - Install with development dependencies"
	@echo "  make setup         - Full development environment setup"
	@echo "  make clean         - Clean up generated files"
	@echo ""
	@echo "$(GREEN)Development:$(NC)"
	@echo "  make dev           - Run format, lint, and test"
	@echo "  make format        - Format code with ruff, black, isort"
	@echo "  make lint          - Run linting checks"
	@echo "  make type-check    - Run type checking"
	@echo "  make test          - Run tests"
	@echo "  make test-cov      - Run tests with coverage"
	@echo ""
	@echo "$(GREEN)Quality:$(NC)"
	@echo "  make check         - Run all quality checks"
	@echo "  make security      - Run security checks"
	@echo "  make complexity    - Analyze code complexity"
	@echo "  make dead-code     - Detect dead code"
	@echo ""
	@echo "$(GREEN)CI/CD:$(NC)"
	@echo "  make ci-all        - Run full CI pipeline"
	@echo "  make ci-test       - Run CI tests"
	@echo "  make ci-check      - Run CI checks"
	@echo ""
	@echo "$(GREEN)Dependencies:$(NC)"
	@echo "  make deps-tree     - Show dependency tree"
