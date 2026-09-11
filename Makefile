SHELL := /bin/bash
COMPOSE := docker compose -f docker-compose.dev.yml
SCRIPT := scripts/dev-stack-seed.sh

# =============================================================================
# Tracera development + production entrypoints.
# Per the Sep-2026 architecture decision:
#   - `make stack` brings up the full 25-service local dev compose
#   - `make run` runs tracera-server natively (port 8080) against the stack
#   - `make tunnel` starts the Cloudflare Tunnel that exposes localhost
#     to `tracera.pheno.studio/api/*` on the public internet
#   - `make prod` is the one-shot: stack + run + tunnel (the canonical
#     "go live locally" combo)
#   - `make deploy` triggers the Render fallback (used only when the
#     local box is offline for an extended period)
# =============================================================================

.PHONY: up down logs ps reset seed \
        run build test check fmt clippy \
        stack run-server mcp-server tunnel prod deploy

stack: ## Bring up the full local dev compose (postgres, redis, neo4j, nats, etc.)
	$(COMPOSE) up -d

stack-down: ## Tear down the local dev stack
	$(COMPOSE) down

stack-logs: ## Tail logs from the local dev stack
	$(COMPOSE) logs -f --tail=100

stack-ps: ## Show running services
	$(COMPOSE) ps

stack-reset: ## Drop volumes and orphan containers (DESTRUCTIVE)
	$(COMPOSE) down -v --remove-orphans

stack-seed: ## Seed sample data into the local dev stack
	bash $(SCRIPT)

run: run-server ## alias for `make run-server`

run-server: ## Run tracera-server natively on :8080 against the local stack
	@if [ ! -f .cloudflared/tunnel.pid ]; then \
	  echo "[run] Local stack should already be up — run 'make stack' first."; \
	else \
	  echo "[run] Tunnel running on PID $$(cat .cloudflared/tunnel.pid)"; \
	fi
	set -a && . crates/tracera-server/.env.local && set +a && \
	  cargo run -p tracera-server

mcp-server: ## Run tracera-mcp natively on :8081 (streamable-HTTP wrapper around stdio)
	set -a && . crates/tracera-server/.env.local && set +a && \
	  cargo run -p tracera-mcp --bin mcp-server

build: ## Compile the entire workspace
	cargo build --workspace

test: ## Run the full test suite
	cargo test --workspace

check: ## cargo check across the workspace
	cargo check --workspace

fmt: ## Format the entire Rust workspace
	cargo fmt --all

clippy: ## Lint the entire Rust workspace
	cargo clippy --workspace --all-targets -- -D warnings

tunnel: ## Start the Cloudflare Tunnel exposing local tracera-server to `tracera.pheno.studio/api/*`
	@mkdir -p .cloudflared
	@bash scripts/start-tunnel.sh

tunnel-bg: ## Start the tunnel in the background (writes PID to .cloudflared/tunnel.pid)
	@mkdir -p .cloudflared
	@bash scripts/start-tunnel.sh >.cloudflared/tunnel.log 2>&1 & \
	  echo $$ >.cloudflared/tunnel.pid && \
	  echo "[tunnel] started (PID $$(cat .cloudflared/tunnel.pid)). Log: .cloudflared/tunnel.log"

tunnel-stop: ## Stop the background tunnel (PID in .cloudflared/tunnel.pid)
	@if [ -f .cloudflared/tunnel.pid ]; then \
	  kill $$(cat .cloudflared/tunnel.pid) 2>/dev/null && \
	  rm .cloudflared/tunnel.pid && \
	  echo "[tunnel] stopped"; \
	else \
	  echo "[tunnel] no PID file"; \
	fi

prod: stack run-server tunnel ## The canonical "go live locally" combo: stack + run + tunnel
	@echo "[prod] stack + tracera-server + tunnel are all up."
	@echo "[prod] Local services on http://localhost:8080, exposed at https://tracera.pheno.studio/api"
	@echo "[prod] Vercel frontend (separate) at https://tracera-kappa.vercel.app"
	@echo "[prod] Cloudflare Worker edge at https://tracera-edge.kooshapari.workers.dev"

deploy: ## Trigger the Render fallback deploy (use when local box is offline)
	@echo "[deploy] Triggering Render fallback via OIDC..."
	gh workflow run build-push-image.yml --repo KooshaPari/Tracera --ref main || \
	  echo "[deploy] gh CLI not authed; trigger manually in the GitHub UI"

up: stack ## backward-compat alias
down: stack-down ## backward-compat alias
logs: stack-logs ## backward-compat alias
ps: stack-ps ## backward-compat alias
reset: stack-reset ## backward-compat alias
seed: stack-seed ## backward-compat alias

.PHONY: help
help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'
