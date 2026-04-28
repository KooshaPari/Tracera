# Code Quality Targets

.PHONY: lint lint-fix format format-check type-check security check complexity dead-code duplication doc-coverage docstyle docs-lint docs-quality quality-report

lint: ## Run ruff lint checks
	@echo "Running ruff linter..."
	@$(RUFF) check . --statistics

lint-fix: ## Run ruff with auto-fix enabled
	@echo "Running ruff with auto-fix..."
	@$(RUFF) check . --fix

format: ## Apply formatters (ruff, black, isort)
	@echo "Formatting code..."
	@$(RUFF) format .
	@$(BLACK) .
	@$(ISORT) . --profile black
	@docformatter --in-place --recursive src/

format-check: ## Check formatting without modifying files
	@echo "Checking code formatting..."
	@$(BLACK) --check .
	@$(ISORT) --check-only . --profile black
	@docformatter --check --recursive src/

type-check: ## Run mypy type checking
	@echo "Running type checker..."
	@$(MYPY) src/ --explicit-package-bases || true

security: ## Run bandit security scan
	@echo "Running security checks..."
	@bandit -r src/ -f json -o bandit-report.json || true
	@bandit -r src/

check: lint type-check security ## Run lint, type-check, and security scans
	@echo "✅ All quality checks passed!"

complexity: ## Report cyclomatic complexity and maintainability
	@echo "Analyzing code complexity..."
	@radon cc src/ -a -s || true
	@radon mi src/ -s || true

dead-code: ## Detect dead code with vulture
	@echo "Detecting dead code..."
	@vulture src/ --min-confidence 80 || true

duplication: ## Check for duplicated code blocks with pylint
	@echo "Checking for duplicated code..."
	@pylint --disable=all --enable=duplicate-code src/ || true

doc-coverage: ## Measure documentation coverage with interrogate
	@echo "Measuring documentation coverage..."
	@interrogate -v --fail-under 80 src/ || true

docstyle: ## Enforce docstring style guidelines
	@echo "Checking docstring style..."
	@pydocstyle src/ || true

docs-lint: ## Validate Markdown formatting and links
	@echo "Linting Markdown content..."
	@npx --yes markdownlint-cli2 "**/*.md" "#node_modules"
	@echo "Checking Markdown links..."
	@bash scripts/checks/run_markdown_link_check.sh

docs-quality: docstyle doc-coverage docs-lint ## Run all documentation quality checks
	@echo "✅ Documentation quality checks complete."

quality-report: ## Generate comprehensive quality report via prospector
	@echo "Generating quality report (prospector)..."
	@prospector --profile prospector.yaml || true
