.PHONY: lint-naming

lint-naming:
	bash scripts/shell/check-naming-explosion-python.sh
	bash scripts/shell/check-naming-explosion-go.sh
	cd frontend && bash scripts/check-naming-explosion.sh
