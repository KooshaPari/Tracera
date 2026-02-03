# Quality checks – quick reference

Unified quality (lint, typecheck, build, tests) for Go, Python, and frontend, with **auto re-run**, **last check**, and **caching**.

## Commands

| Target | Description |
|--------|-------------|
| `make quality` | Run Go, Python, frontend in parallel; print action plan by file; write last-run state |
| `make quality-pc` | Run quality via process-compose TUI (port 18080); failed suites auto-rerun (on_failure, max 5); stop with ^C |
| `make quality-pc LOOP=1` | Same TUI; all suites rerun after every completion (live feed). Same as `quality-pc-loop` / `quality-pc-watch`. |
| `make quality-pc-loop` | Alias: TUI with continuous rerun (restart always). Port 18080. Stop with ^C. |
| `make quality-pc-watch` | Alias for `quality-pc-loop` (“watch” = continuous loop, not file watch; process-compose has no `--watch` flag). |
| `make quality-watch` | Auto re-run quality on **file change** (watchexec or poll fallback); no TUI. |
| `make quality-last` | Show last run state (timestamp, exit codes, failed_suites) |
| `make quality-rerun` | Re-run quality (same as `make quality`) |
| `make quality-report` | Action plan by file and/or by log; color by project (Go/Python/Frontend) |
| `make quality-report-watch` | **File-watched report:** re-run report when .quality/logs or source changes (watchexec). Stop with ^C. |
| `make quality-go` | Go-only suite (no Python) |
| `make quality-python` | Python-only suite (no Go) |
| `make quality-frontend` | Frontend-only suite |

## Auto re-run (quality-watch)

- **With watchexec (recommended):** `make quality-watch` uses [watchexec](https://github.com/watchexec/watchexec-cli) to watch `backend/`, `src/`, `tests/`, `frontend/`, `Makefile`, and key configs; on change (debounce 2s) it re-runs `make quality`.
- **Install:** `brew install watchexec` (macOS) or `cargo install watchexec-cli`.
- **Fallback:** If watchexec is missing, the script polls every `QUALITY_WATCH_INTERVAL` seconds (default 30). Set `QUALITY_WATCH_INTERVAL=60` to poll less often.
- **One-shot:** `bash scripts/run-quality-watch.sh --once` runs quality once and exits (no watch).

Process-compose does **not** provide file-watch re-run for one-shot processes; it supports scheduled (cron/interval) processes for recurring runs. For **file-based** re-run we use watchexec (same pattern as `scripts/run-with-config-watch.sh` for Prometheus/Grafana).

## Last check and state

- After each `make quality` (or `scripts/run-quality-parallel.sh`), state is written to **`.quality/last-run.json`**:
  - `timestamp`, `exit_go`, `exit_python`, `exit_frontend`, `failed_suites`, `ok`
- **`make quality-last`** prints that state (uses `jq` if available, else raw JSON).
- **`make quality-rerun`** is an alias for running quality again (useful after inspecting `quality-last`).

## Caching

- **Logs as cache:** `.quality/logs/` holds the last run’s output (`quality-go.log`, `quality-python.log`, `quality-frontend.log`). `make quality-report` reads these to produce the action plan; no re-run is done.
- **Turbo:** Frontend already uses Turbo’s cache for build/test where applicable.
- **Optional hash-based skip (future):** You could add per-suite input hashes (e.g. of `backend/**`, `src/**`, `frontend/**`) under `.quality/cache/` and skip a suite if the hash is unchanged, reusing the last log. Not implemented here; logs + last-run state are the current “cache” for inspection and re-run.

## Process-compose quality (quality-pc)

- **quality-pc:** `make quality-pc` uses `process-compose.quality.yaml`. Each suite runs; **failed** suites auto-rerun (`restart: on_failure`, backoff 3s, max 5). TUI on port **18080**; logs in `.quality/logs`. Stop with ^C.
- **File-triggered:** Use `make quality-watch` for full quality on file change, or `make quality-report-watch` for report-only refresh when logs or source change.

## Action plan (by file and by log)

- **By file:** When the parser finds file:line issues, it prints **QUALITY ACTION PLAN (by file)** with file path and per-suite lines (Go, Python, Frontend).
- **By log:** When there are no parseable by-file issues but logs exist (or suites failed), it prints **ACTION PLAN (by log)** with each log path and an excerpt (error-like lines or last lines). So you always get an actionable view.
- **Colors:** In a TTY (and unless `NO_COLOR` is set), Go = cyan, Python = yellow, Frontend = blue; failed runs header = red. Disabled when stdout is not a TTY.
- **File-watched report:** `make quality-report-watch` uses watchexec to re-run the report when `.quality/logs` or source files change (e.g. after running quality or quality-pc in another terminal). Fallback: poll every `QUALITY_REPORT_INTERVAL` s (default 5).

## Config files and ignore patterns

- **Root:** `.editorconfig` (indent, line endings, trim); `.prettierrc.json` (YAML/JSON/MD for pre-commit); `.semgrep.yml` (project rules; pre-commit runs `p/security-audit` + `.semgrep.yml`).
- **Python:** Ruff, mypy, interrogate, bandit: config in `pyproject.toml` and `.bandit`. Ruff per-file ignores: `[tool.ruff.lint.per-file-ignores]`. Pre-commit global exclude: `.pre-commit-config.yaml` `exclude:` (e.g. `.venv/`, `__pycache__/`). **Bandit inline skip:** use `# nosec BXXX` with a brief reason when a finding is a false positive or accepted risk; document justification in code or here.
- **Go:** `backend/.golangci.yml`; paths and exclusions in that file.
- **Frontend:** Oxlint: `frontend/.oxlintrc.json`, `frontend/apps/web/.oxlintrc.json`; Biome: `frontend/biome.json`; ignore patterns in each.
- **Tach:** `tach.toml` at repo root; `exclude` for tests, build, dist, docs. See [TOOLING_AUDIT_AND_STRICT_SETUP_PLAN.md](../reports/TOOLING_AUDIT_AND_STRICT_SETUP_PLAN.md) for full config locations.

## Version pins

- **Pre-commit:** Hook revisions are pinned in `.pre-commit-config.yaml` (e.g. `ruff-pre-commit` rev, `pre-commit-hooks` rev). Update with `pre-commit autoupdate`; then run `pre-commit run --all-files` to verify.
- **Python:** `pyproject.toml` uses lower bounds for deps; dev deps (ruff, mypy, tach, etc.) have minimum versions. Lockfile: `uv.lock` (use `uv sync`).
- **Frontend:** Use `bun install`; lockfile in `frontend/`. See repo README for minimum Node/Bun versions.

## Optional Python type-check and test runners

`make quality` and `quality-py-type` / `quality-py-test` use **mypy** and **pytest** by default. For faster or alternative tools (ty, basedpyright, pyright, pytest-xdist, uv test), see [docs/research/PYTHON_TYPE_AND_TEST_TOOLS.md](../research/PYTHON_TYPE_AND_TEST_TOOLS.md).

| Target | Description |
|--------|-------------|
| `make type-check-ty` | Type-check with **ty** (Astral; very fast). Requires `ty` in venv. |
| `make type-check-basedpyright` | Type-check with **basedpyright**. Requires `basedpyright` in venv. |
| `make type-check-pyright` | Type-check with **pyright**. Requires `pyright` in venv. |
| `make test-python-parallel` | Run Python tests in parallel (**pytest-xdist** `-n auto`). Requires `pytest-xdist`. |
| `make test-python-uv` | Run Python tests with **uv test**. Requires `uv` installed. |
| `PYTEST_EXTRA="-n auto" make test-python` | Same as test-python but with extra pytest args (e.g. parallel). |
