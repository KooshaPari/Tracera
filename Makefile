SHELL := /bin/bash
COMPOSE := docker compose -f docker-compose.dev.yml
SCRIPT := scripts/dev-stack-seed.sh

# =============================================================================
# Tracera development + production entrypoints.
#
# GLOBAL RULE (Sep-2026): the build entrypoint is `task` (not `make`).
#   `make` is the historic GNU alias; all new scripts + lefthook hooks +
#   docs reference `task <target>`. Both work today; `make` is kept as a
#   one-line forwarder so any tooling that still calls `make stack`
#   continues to work. New code should call `task`.
#
# Per the Sep-2026 architecture decision:
#   * `task stack` brings up the full 25-service local dev compose
#   * `task run-server` runs tracera-server natively (port 8080) against
#     the stack
#   * `task tunnel` exposes localhost to `tracera.pheno.studio/api/*`
#     with a hybrid preference: Tailnet (MagicDNS / 100.x) first,
#     Cloudflare Quick Tunnel fallback when Tailnet is not reachable.
#   * `task prod` is the one-shot: stack + run + tunnel
#     (the canonical "go live locally" combo)
#   * `task deploy` triggers the Render fallback (used only when the
#     local box is offline for an extended period)
#
# URI mapping (canonical):
#   API:        https://tracera.pheno.studio/api/*
#   MCP:        https://mcp.tracera.pheno.studio
#   Edge:       https://tracera-edge.pheno.studio (worker)
#   Web app:    https://app.tracera.pheno.studio (Vercel)
#   Landing:    https://phenotype.space (separate repo, NOT aliased)
# =============================================================================

.PHONY: help task stack stack-down stack-logs stack-ps stack-reset stack-seed \
        task-run-server task-mcp-server task-tunnel task-tunnel-bg task-tunnel-stop \
        task-prod task-deploy \
        build test check fmt clippy \
        up down logs ps reset seed \
        make-stack make-run-server make-tunnel make-prod make-deploy

# --- help ----------------------------------------------------------------
help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-22s\033[0m %s\n", $$1, $$2}'

# =============================================================================
# Primary entrypoint: `task` (canonical alias of `make`)
# =============================================================================
task: ## Canonical alias of `make` — pass target as arg (e.g. `task stack`)
	@$(MAKE) $(filter-out $@,$(MAKECMDGOALS))

# =============================================================================
# Stack: 25-service local dev compose (postgres, redis, neo4j, nats, etc.)
# =============================================================================
stack: ## Bring up the full local dev compose
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

# =============================================================================
# Server: native Rust binaries against the local stack
# =============================================================================
task-run-server: ## Run tracera-server natively on :8080 against the local stack
	@if [ -f .cloudflared/tunnel.pid ]; then \
	  echo "[run-server] tunnel active on PID $$(cat .cloudflared/tunnel.pid)"; \
	else \
	  echo "[run-server] (no tunnel running) — start with 'task tunnel-bg'"; \
	fi
	set -a && . crates/tracera-server/.env.local && set +a && \
	  cargo run -p tracera-server

task-mcp-server: ## Run tracera-mcp natively on :8081 (streamable-HTTP wrapper around stdio)
	set -a && . crates/tracera-server/.env.local && set +a && \
	  cargo run -p tracera-mcp --bin mcp-server

# =============================================================================
# Tunnel: hybrid Tailnet + Cloudflare fallback to tracera.pheno.studio/api
# =============================================================================
task-tunnel: ## Expose local tracera-server to tracera.pheno.studio/api/* via Tailnet or CF tunnel
	@mkdir -p .cloudflared
	@bash scripts/start-tunnel.sh

task-tunnel-bg: ## Run the tunnel in the background (writes PID to .cloudflared/tunnel.pid)
	@mkdir -p .cloudflared
	@bash scripts/start-tunnel.sh >.cloudflared/tunnel.log 2>&1 & \
	  echo $$ >.cloudflared/tunnel.pid && \
	  echo "[tunnel-bg] started (PID $$(cat .cloudflared/tunnel.pid)). Log: .cloudflared/tunnel.log"

task-tunnel-stop: ## Stop the background tunnel
	@if [ -f .cloudflared/tunnel.pid ]; then \
	  kill $$(cat .cloudflared/tunnel.pid) 2>/dev/null && \
	  rm .cloudflared/tunnel.pid && \
	  echo "[tunnel-stop] stopped"; \
	else \
	  echo "[tunnel-stop] no PID file"; \
	fi

# =============================================================================
# Prod: stack + run + tunnel (one-shot "go live locally")
# =============================================================================
task-prod: stack task-run-server task-tunnel ## Canonical "go live locally" combo
	@echo "[prod] stack + tracera-server + tunnel are all up."
	@echo "[prod] Local services on http://localhost:8080"
	@echo "[prod] Exposed at  https://tracera.pheno.studio/api  (CF tunnel)"
	@echo "[prod] Tailnet     http://100.x.y.z:8080  (if Tailnet up)"
	@echo "[prod] Worker edge https://tracera-edge.pheno.studio"
	@echo "[prod] Vercel      https://app.tracera.pheno.studio"

# =============================================================================
# Deploy: Render fallback only (used when local box is offline)
# =============================================================================
task-deploy: ## Trigger the Render fallback deploy via OIDC
	@echo "[deploy] Triggering Render fallback via OIDC..."
	gh workflow run build-push-image.yml --repo KooshaPari/Tracera --ref main || \
	  echo "[deploy] gh CLI not authed; trigger manually in the GitHub UI"

# =============================================================================
# Build / test / lint / format
# =============================================================================
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

# =============================================================================
# Backward-compat aliases (do NOT use in new code — prefer `task <target>`)
# =============================================================================
up: stack ## deprecated alias
down: stack-down ## deprecated alias
logs: stack-logs ## deprecated alias
ps: stack-ps ## deprecated alias
reset: stack-reset ## deprecated alias
seed: stack-seed ## deprecated alias

make-stack: stack ## explicit `make` alias
make-run-server: task-run-server
make-tunnel: task-tunnel
make-prod: task-prod
make-deploy: task-deploy
