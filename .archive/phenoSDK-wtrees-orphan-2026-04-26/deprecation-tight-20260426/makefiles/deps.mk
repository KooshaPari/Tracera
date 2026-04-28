# Dependency Management Targets

.PHONY: deps-tree deps-audit deps-update deps-licenses show-outdated deps-check

deps-tree: ## Show dependency tree (installs pipdeptree if needed)
	@echo "Dependency tree:"
	@$(PIPDEPTREE) || $(PIP) install $(PIPDEPTREE) && $(PIPDEPTREE)

deps-audit: ## Audit dependencies for vulnerabilities
	@echo "Auditing dependencies..."
	@$(PIP_AUDIT) || $(PIP) install $(PIP_AUDIT) && $(PIP_AUDIT)

deps-update: ## List outdated dependencies
	@echo "Updating dependencies..."
	@$(PIP) list --outdated

deps-licenses: ## Show dependency licenses
	@echo "Dependency licenses:"
	@$(PIP_LICENSES) --format=markdown || $(PIP) install $(PIP_LICENSES) && $(PIP_LICENSES) --format=markdown

show-outdated: ## Alias for deps-update
	@echo "Checking for outdated packages..."
	@$(PIP) list --outdated

deps-check: deps-audit deps-licenses ## Run dependency audit and license report
	@echo "✅ Dependency health checks complete."
