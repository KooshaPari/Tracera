.PHONY: lint-naming test-setup desktop-electrobun-dev desktop-electrobun-build desktop desktop-build

# Used by Comprehensive Test Validation workflow; secrets optional in CI.
test-setup:
	@echo "test-setup: no-op in CI (set WORKOS_API_KEY and DATABASE_URL locally to provision users)"

lint-naming:
	bash scripts/shell/check-naming-explosion-python.sh
	bash scripts/shell/check-naming-explosion-go.sh
	cd frontend && bash scripts/check-naming-explosion.sh

desktop-electrobun-dev:
	cd frontend/apps/desktop-electrobun && bun run dev

desktop-electrobun-build:
	cd frontend/apps/desktop-electrobun && bun run build:release

desktop: desktop-electrobun-dev

desktop-build: desktop-electrobun-build
