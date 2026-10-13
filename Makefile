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
#   * Shared Cloudflare tunnel lifecycle is owned by shared infra IaC.
#     `task tunnel-status` is read-only; `task tunnel` / `task tunnel-bg`
#     are retired fail-closed compatibility entrypoints.
#   * `task prod` brings up the local stack/server and reports ingress status;
#     it does not create, restart, or replace shared public ingress.
#   * `task deploy` triggers the Render fallback (used only when the
#     local box is offline for an extended period)
#
# URI mapping (canonical):
#   Web/Auth:   https://tracera.pheno.studio
#   API:        https://t.tracera.pheno.studio
#   Edge:       https://tracera-edge.pheno.studio (worker)
#   Web app:    https://app.tracera.pheno.studio (Vercel)
#   Landing:    https://phenotype.space (separate repo, NOT aliased)
# =============================================================================

.PHONY: help task stack stack-down stack-logs stack-ps stack-reset stack-seed \
        task-run-server task-mcp-server task-tunnel-status task-tunnel task-tunnel-bg task-tunnel-stop \
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
	@echo "[run-server] shared public ingress is managed externally; use 'task tunnel-status' to inspect it"
	set -a && . crates/tracera-server/.env.local && set +a && \
	  cargo run -p tracera-server

task-mcp-server: ## Run tracera-mcp natively on :8081 (streamable-HTTP wrapper around stdio)
	set -a && . crates/tracera-server/.env.local && set +a && \
	  cargo run -p tracera-mcp --bin mcp-server

# =============================================================================
# Ingress: shared Cloudflare tunnel is externally managed
# =============================================================================
task-tunnel-status: ## Read-only Tailnet/shared-Cloudflare ingress status
	@bash scripts/start-tunnel.sh

task-tunnel: ## RETIRED: shared tunnel lifecycle belongs to shared infra IaC
	@echo "error: task tunnel is retired; use task tunnel-status for read-only status" >&2
	@exit 2

task-tunnel-bg: ## RETIRED: do not launch the shared Cloudflare tunnel from Tracera
	@echo "error: task tunnel-bg is retired; shared tunnel lifecycle is externally managed" >&2
	@exit 2

task-tunnel-stop: ## RETIRED: do not stop shared Cloudflare infrastructure from Tracera
	@echo "error: task tunnel-stop is retired; shared tunnel lifecycle is externally managed" >&2
	@exit 2

# =============================================================================
# Prod: local runtime only; shared public ingress is independently managed
# =============================================================================
task-prod: stack task-tunnel-status task-run-server ## Local go-live; does not mutate shared ingress
	@echo "[prod] local stack + tracera-server are up; shared public ingress is externally managed."

# =============================================================================
# Deploy: Render fallback only (used when local box is offline)
# =============================================================================
task-deploy: ## Trigger the Render fallback deploy via OIDC
	@echo "[deploy] Triggering Render fallback via OIDC..."
	gh workflow run build-push-image.yml --repo <REDACTED>/Tracera --ref main || \
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
