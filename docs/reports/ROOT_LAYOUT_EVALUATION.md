# Root Layout Evaluation and Consolidation

**Date:** 2026-02-02  
**Goal:** Reduce top-level clutter so the root is smaller and easier to scan.

## Changes Made

### 1. `config/` directory

All process-compose and Caddy config files were moved under **`config/`**:

| Moved to `config/` | Purpose |
|--------------------|--------|
| `process-compose.yaml` | Main orchestration (macOS default) |
| `process-compose.linux.yaml` | Linux overrides |
| `process-compose.windows.yaml` | Windows overrides |
| `process-compose.quality.yaml` | Quality TUI (make quality-pc) |
| `process-compose.quality-watch.yaml` | Quality watch config |
| `Caddyfile` | Production-style gateway (standalone Caddy) |
| `Caddyfile.dev` | Dev gateway (used by process-compose) |

**Updated references:**

- **Makefile:** `PC_CONFIG` now uses `-f config/process-compose.yaml` (and platform variants under `config/`). Default case explicitly passes `-f config/process-compose.yaml`.
- **scripts/python/dev-start-with-preflight.py:** Checks `config/process-compose.yaml`; passes `-f config/process-compose.yaml` when `PC_CONFIG` is unset.
- **scripts/shell/run-caddy.sh:** Uses `--config config/Caddyfile`.
- **config/process-compose.yaml:** Caddy command uses `--config config/Caddyfile.dev`.
- **scripts/shell/verify-apm-integration.sh**, **scripts/shell/verify-native-setup.sh:** Paths updated to `config/process-compose.yaml`, `config/Caddyfile.dev`.
- **scripts/shell/run-quality-watch.sh**, **scripts/shell/run-quality-report-watch.sh:** Watch `config/process-compose.quality.yaml`.
- **Makefile (quality-pc):** `-f config/process-compose.quality.yaml`.
- **README.md:** Validate command updated to `process-compose -f config/process-compose.yaml validate`.

### 2. Test script relocated

- **`test-auth-routes.sh`** → **`scripts/shell/test-auth-routes.sh`** (no references found; safe move).

## Root After Consolidation

**Still at root (by design):**

- **Docs (allowed):** `README.md`, `CHANGELOG.md`, `AGENTS.md`, `claude.md`, `00_START_HERE.md`
- **Build / runtime:** `Makefile`, `Makefile.gateway`, `package.json`, `bun.lock`, `bunfig.toml`, `pyproject.toml`, `uv.lock`, `alembic.ini`, `buf.yaml`, `buf.gen.yaml`, `biome.json`, `tach.toml`, `conftest.py`
- **Tooling:** `.pre-commit-config.yaml`, `.semgrep.yml`, `Brewfile.dev`
- **Deploy / Docker:** `Procfile`, `docker-compose.yml`, `docker-compose.chaos.yml`, `redis.conf` (could be moved to `config/` in a follow-up)
- **Dirs:** `backend`, `frontend`, `src`, `tests`, `scripts`, `docs`, `infrastructure`, `k8s`, `monitoring`, `openapi`, `proto`, `alembic`, `cli`, `examples`, `load-tests`, `DEMO_PROJECT`, `ARCHIVE`, `config`, etc.

**Removed from root (moved):**

- 5× `process-compose*.yaml` → `config/`
- 2× `Caddyfile*` → `config/`
- 1× `test-auth-routes.sh` → `scripts/`

## Optional Next Steps

- **Move more into `config/`:** `docker-compose.yml`, `docker-compose.chaos.yml`, `redis.conf` (would require updating `Makefile.gateway` and any scripts that reference them).
- **Stray items:** If present, `1`, `default`, `__pycache__` can be removed or gitignored; `exports`, `backup`, `tmp` are often build/output and can stay gitignored.
- **DEMO_PROJECT:** Left at root because many scripts reference `DEMO_PROJECT` or `./DEMO_PROJECT`; moving would require a coordinated path update.
