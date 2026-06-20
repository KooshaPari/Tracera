# Warp Guide for trace

Warp is the default terminal UX for this repo. Keep sessions fast, reproducible, and aligned with the FastMCP contract and `llms-full.txt` (authoritative).

## Environment & Tooling
- Activate venv first: `source .venv/bin/activate`
- Prefer uv for everything: `uv run ...`, `uv pip install -e .[dev]`
- Primary CLI: `uv run rtm ...` (Typer app in `tracertm.cli`)
- Use `poe` shortcuts (via uv): `uv run poe format | lint | type-check | type-check-strict | arch-check | security | test | test-cov | test-parallel | test-unit | test-integration | all`

## File Size & Modularity (Hard Limit)
- Max 500 lines per module, target ≤350; decompose before crossing 350.
- Split by concern: services/<domain>/, infrastructure/, cli/, db/, utils/, tests/ mirroring code.
- No backward-compat shims or dual code paths; update all callers in one cut.

## Core Loops (Warp Snippets)
- Quick status: `git status` → `uv run poe test -q` (or targeted) → `uv run poe lint`
- Fast checks: `uv run poe format && uv run poe lint && uv run poe type-check`
- Ultra strict: `uv run poe type-check-strict && uv run poe arch-check && uv run poe security`
- Tests: `uv run poe test-unit`, `uv run poe test-integration`, `uv run poe test-cov`, `uv run poe test-parallel`
- Coverage rule: keep changed files at 100% (pyproject enforces strict markers/warnings-as-errors)

## Database & Migrations
- Default store: SQLite (aiosqlite). For Postgres/Neo4j experiments, parameterize via env/config; never hard-code secrets.
- Run Alembic via uv when migrations exist; no raw reset scripts. Keep migrations one-shot and idempotent.

## CLI Operations
- Inspect views/links: `uv run rtm view <name>`, `uv run rtm links <id>`, `uv run rtm drill <id> --depth N`
- CRUD automation: `uv run rtm create story --title "…" --auto-generate`, `uv run rtm extend <id> --with "…"`, `uv run rtm collapse <id> --cascade`
- Chaos utilities live in CLI; ensure commands are deterministic and respect config/state isolation.

## Testing Discipline
- Markers: unit/integration/e2e/slow/agent/asyncio (pytest.ini). Use markers, not file-name suffixes.
- Async tests use asyncio_mode=auto; avoid blocking calls.
- Always run relevant suite after changes; broaden to `uv run poe all` before release-grade work.

## Security & Secrets
- Never commit keys or connection strings. Config via env + pydantic-settings; validate with `uv run poe security` and `rg -i "api[_-]?key|secret|token"` before commits.

## Docs Hygiene
- Keep canonical docs in `docs/` (session folders OK). Do not create root-level markdown sprawl; update existing session docs instead of duplicating.

## Git Hygiene
- Review `git diff` + `git status` before any commit. No commits with failing checks. Ensure line-count constraints respected on touched files.


## Opinionated Quality Enforcement
- We want opinionated rules that enforce opinionated styling to a strict degree.
- This is an exclusively agent/vibecoded project; programmatic enforcement must guard against bad quality and antipatterns.
- Rather than disables or ignores, fix code properly.
