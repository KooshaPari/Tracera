# Go and Python developer experience – research, audit, and plan

**Sources:** `../atoms-mcp-prod` (Python CLI), `../../clean/deploy/atomsAgent` (Python API), `../../clean/deploy/atomsbot` (TS/Node scripts), `../../clean/deploy/atoms.tech` (package.json).  
**Target:** Trace Go + Python DX (Makefile and root package.json).

---

## 1. Research – atoms-mcp-prod (Python CLI)

### 1.1 Atoms CLI (`python cli.py` / `atoms`)

Typer app with npm-like command names. **CLAUDE.md:** "ALWAYS use atoms CLI (`python cli.py`) for project operations."

| Command | Purpose |
|--------|---------|
| **Server** | |
| `atoms run` | Start MCP server |
| `atoms dev` | Dev mode (Vercel dev or uvicorn --reload) |
| `atoms health` | Check server health |
| **Test** | |
| `atoms test` | Full suite (--scope unit/integration/e2e) |
| `atoms test:unit` | Unit only (pytest -m unit, parallel) |
| `atoms test:int` | Integration (pytest -m integration) |
| `atoms test:e2e` | E2E (pytest -m e2e) |
| `atoms test:cov` | Unit + coverage (html + term) |
| `atoms test:rls` | RLS/security tests |
| `atoms test:story` | By user story / epic |
| `atoms test:comprehensive` | Integration + e2e (mock/live) |
| `atoms test:live` | Live service tests with credentials |
| **Quality** | |
| `atoms lint` | ruff check |
| `atoms format` | black + isort |
| `atoms type-check` | mypy |
| `atoms check` | format + lint + type-check |
| **Build / deps** | |
| `atoms build` | checks + tests + python -m build |
| `atoms clean` | __pycache__, .pytest_cache, .mypy_cache, build, dist, htmlcov |
| `atoms update` | Dependency update (interactive) |
| `atoms deps` | Dependency summary |
| **DB / docs / debug** | |
| `atoms db:regen-types` | Regenerate Supabase types |
| `atoms docs` / `atoms wiki:*` | MkDocs serve/build/deploy |
| `atoms debug:token` | Get JWT for scripts |
| `atoms debug:test-connection` | Test MCP connection |
| `atoms logs` | Tail server log |

**Patterns:** test:unit / test:int / test:e2e / test:cov; lint, format, type-check, check; db:regen-types; debug:*.

### 1.2 Config (pyproject_quality.toml)

- **black** (line-length 100), **ruff** (E, W, F, I, C, B, UP), **mypy** (relaxed), **pytest** (markers: unit, integration, e2e, slow, asyncio; --cov, html report), **coverage**.

### 1.3 package.json (atoms-mcp-prod)

Minimal: `dev` (sst dev), `deploy`, `test:rls`, `typecheck`. Most DX is in the Python CLI.

---

## 2. Research – atomsbot (TypeScript)

### 2.1 package.json scripts (Go-relevant naming patterns)

| Category | Scripts |
|----------|--------|
| **Lint** | `lint` (oxlint), `lint:fix` |
| **Test** | `test`, `test:watch`, `test:ui`, `test:coverage`, `test:unit`, `test:integration`, `test:e2e`, `test:workflows`, `test:all` |
| **DB** | `db:init`, `db:migrate`, `db:generate`, `db:push`, `db:studio`, `db:reset` |
| **Other** | `format`, `clean`, `build`, `validate` |

Patterns: **test:unit**, **test:integration**, **test:e2e**, **test:coverage**; **db:***; **lint:fix**.

---

## 3. Research – atoms.tech (already used in PACKAGE_JSON_DX_PLAN)

- Root scripts: dev, build, lint, lint:strict, lint:fix, type-check, format, format:check, test, test:run, test:unit, test:e2e, test:api, test:ci, db:migrate, clean, coverage:*, security:*, etc.

---

## 4. Audit – Trace Go/Py today

### 4.1 Makefile (existing)

| Area | Targets |
|------|--------|
| **Lint** | `lint` (lint-go + lint-python), `lint-go`, `lint-python` |
| **Format** | `format` (ruff + gofmt) |
| **Type-check** | `type-check`, `type-check-ty`, `type-check-basedpyright`, `type-check-pyright` |
| **Test** | `test`, `test-python`, `test-python-parallel`, `test-go`, `test-unit`, `test-e2e`, `test-integration` |
| **DB** | `db-migrate`, `db-rollback`, `db-reset`, `db-shell` |
| **Quality** | `quality`, `quality-go`, `quality-python` |
| **Security** | `security-scan` |

**Gaps vs atoms/atomsbot:**

1. No **lint-python-fix** (ruff check --fix); only `format` changes formatting, not lint fixes.
2. No short **py:*** / **go:*** aliases (e.g. py:lint, go:test) for discoverability.
3. Root package.json has no **test:coverage**, **test:python:parallel**, **lint:go**, **lint:python**, **format:python**, **format:go**, or **type-check:ty**.

---

## 5. Plan – Enhancements for Trace

### 5.1 Makefile

| Target | Command | Rationale |
|--------|---------|-----------|
| `lint-python-fix` | ruff check --fix src/ tests/ | Match atoms lint + fix; fix auto-fixable lint only. |
| `py-lint` | $(MAKE) lint-python | Alias for Python-only lint. |
| `py-lint-fix` | $(MAKE) lint-python-fix | Alias. |
| `py-format` | ruff format src/ tests/ | Python-only format. |
| `py-type-check` | $(MAKE) type-check | Alias. |
| `py-test` | $(MAKE) test-python | Alias. |
| `py-test-parallel` | $(MAKE) test-python-parallel | Alias. |
| `go-lint` | $(MAKE) lint-go | Alias. |
| `go-format` | cd backend && gofmt -s -w . | Go-only format. |
| `go-test` | $(MAKE) test-go | Alias. |

*(Make uses hyphens, not colons, to avoid pattern rules.)*

Optional: `test-python-coverage` as explicit name for “pytest with coverage” (current `test-python` already has --cov). We can keep `test-python` as the single target and use it for coverage.

### 5.2 Root package.json

Add scripts that delegate to make (and match atoms/atomsbot naming):

| Script | Delegation |
|--------|-------------|
| `test:coverage` | make test-python (already has --cov) |
| `test:python:parallel` | make test-python-parallel |
| `lint:go` | make lint-go |
| `lint:python` | make lint-python |
| `lint:python:fix` | make lint-python-fix |
| `format:python` | make py:format (or make format; py-only if we add py:format) |
| `format:go` | make go:format |
| `type-check:ty` | make type-check-ty |
| `type-check:basedpyright` | make type-check-basedpyright |
| `type-check:pyright` | make type-check-pyright |

### 5.3 Out of scope (this pass)

- Adding a full Python CLI (like atoms) for Trace; we keep make + package.json as the single entry point.
- atomsAgent-specific API routes (monitoring, sandbox, streaming); not applicable to Trace structure.
- wiki:*, debug:token, db:regen-types (Supabase-specific); skip unless Trace adopts same stack.

---

## 6. Implementation status

**Done.** Makefile and root `package.json` updated. Make uses **hyphens** for Py/Go aliases (`py-format`, `go-format`) to avoid Make pattern rules.

### 6.1 Makefile

| Target | Delegation |
|--------|------------|
| `lint-python-fix` | ruff check src/ tests/ --fix |
| `py-lint`, `py-lint-fix`, `py-format`, `py-type-check`, `py-test`, `py-test-parallel` | lint-python, lint-python-fix, ruff format, type-check, test-python, test-python-parallel |
| `go-lint`, `go-format`, `go-test` | lint-go, gofmt, test-go |

### 6.2 Root package.json

| Script | Delegation |
|--------|------------|
| `test:coverage`, `test:python:parallel` | make test-python, make test-python-parallel |
| `lint:go`, `lint:python`, `lint:python:fix` | make lint-go, make lint-python, make lint-python-fix |
| `format:python`, `format:go` | make py-format, make go-format |
| `type-check:ty`, `type-check:basedpyright`, `type-check:pyright` | make type-check-ty, type-check-basedpyright, type-check-pyright |

**Quick reference (from repo root):**

- **Python:** `bun run lint:python`, `bun run lint:python:fix`, `bun run format:python`, `bun run test:python`, `bun run test:python:parallel`, `bun run test:coverage`, `bun run type-check:ty`
- **Go:** `bun run lint:go`, `bun run format:go`, `bun run test:go`
- **Make:** `make py-lint`, `make py-format`, `make go-test`, etc.

See also **Package.json DX plan:** `docs/reports/PACKAGE_JSON_DX_PLAN.md` (dev, build, lint, format, test, db, clean).

---

## 7. References

- `../atoms-mcp-prod/cli.py`, `../atoms-mcp-prod/pyproject_quality.toml`
- `../../clean/deploy/atomsbot/package.json`
- Trace `Makefile`, `package.json`
