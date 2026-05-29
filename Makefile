.PHONY: lint-naming test-setup

# Used by Comprehensive Test Validation workflow; secrets optional in CI.
test-setup:
	@echo "test-setup: no-op in CI (set WORKOS_API_KEY and DATABASE_URL locally to provision users)"

lint-naming:
	bash scripts/shell/check-naming-explosion-python.sh
	bash scripts/shell/check-naming-explosion-go.sh
	cd frontend && bash scripts/check-naming-explosion.sh
