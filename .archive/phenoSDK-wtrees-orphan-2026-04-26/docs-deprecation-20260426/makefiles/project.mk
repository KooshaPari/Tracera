# Project-level utility targets shared by kits

.PHONY: install install-dev setup-dev clean clean-build build docs pre-commit format-fix

install: ## Install project in editable mode
	@echo "Installing project in editable mode..."
	@$(PIP) install -e .

install-dev: ## Install project with development extras
	@echo "Installing project with development extras..."
	@$(PIP) install -e ".[dev,test,docs]"
	@if command -v pre-commit >/dev/null 2>&1; then \
		pre-commit install; \
	fi

setup-dev: install-dev pre-commit ## Prepare full development environment
	@echo "Development environment ready."

clean: ## Remove build, coverage, and cache artifacts
	@echo "Cleaning build artifacts..."
	@rm -rf build/ dist/ *.egg-info/ htmlcov/ .coverage .pytest_cache/ .mypy_cache/ .ruff_cache/
	@find . -type d -name "__pycache__" -exec rm -rf {} +
	@find . -type f -name "*.pyc" -delete

clean-build: clean ## Alias for clean target

build: clean ## Build distribution artifacts
	@echo "Building distribution artifacts..."
	@$(PYTHON) -m build

docs: ## Build documentation if mkdocs.yml exists
	@if [ -f "mkdocs.yml" ]; then \
		echo "Building documentation..."; \
		mkdocs build; \
	else \
		echo "No mkdocs.yml found. Skipping documentation."; \
	fi

pre-commit: ## Run pre-commit on all files
	@echo "Running pre-commit hooks..."
	@pre-commit run --all-files

format-fix: format ## Alias to run formatting target
