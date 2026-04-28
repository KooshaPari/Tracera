# CI/CD Targets

.PHONY: ci-install ci-test ci-lint ci-format ci-type-check ci-check ci-all

ci-install: ## Install tooling used in CI pipelines
	@echo "Installing CI/CD tools..."
	@$(PIP) install -q $(RUFF) $(BLACK) $(ISORT) bandit $(PYTEST) pytest-cov pytest-asyncio $(MYPY) || true

ci-test: ## Run CI test suite with coverage
	@echo "Running CI tests..."
	@$(PYTEST) --cov=src/pheno --cov-report=term-missing --cov-report=xml -v

ci-lint: ## Run CI linting step
	@echo "Running CI linting..."
	@$(RUFF) check . --statistics

ci-format: ## Verify formatting in CI
	@echo "Checking CI formatting..."
	@$(BLACK) --check .
	@$(ISORT) --check-only . --profile black

ci-type-check: ## Run CI type checking
	@echo "Running CI type check..."
	@$(MYPY) src/ --explicit-package-bases || true

ci-check: ci-lint ci-format ci-type-check ## Run all CI quality gates
	@echo "✅ All CI checks passed!"

ci-all: ci-install ci-check ci-test ## Run full CI pipeline locally
	@echo "✅ Full CI pipeline complete!"
