# Python and TypeScript Tooling – Stack and Recommendations

Summary of the code quality and security tooling used across **Python**, **TypeScript/JS (frontend)**, and **Go** in this repo, with practical usage and CI integration.

---

## 1. Python

| Category | Tool | Role | Run |
|----------|------|------|-----|
| **Lint** | Ruff | Style, bugs, security (S), imports, naming, complexity | `ruff check src/ tests/` |
| **Format** | Ruff | Canonical formatting | `ruff format .` / `ruff format --check .` |
| **Type** | mypy | Static typing | `mypy src/` |
| **Type (strict)** | basedpyright | Stricter type checking | `basedpyright src/` |
| **Security (code)** | Bandit | Security anti-patterns | `bandit -r src/` |
| **Security (deps)** | pip-audit | Dependency vulnerabilities (PyPI advisory DB) | `pip-audit` |
| **Security (rules)** | Semgrep | Rule-based security audit | `semgrep --config=p/security-audit src/` |
| **Architecture** | tach | Module boundary enforcement | `tach check` |
| **Doc coverage** | interrogate | Docstring coverage | `interrogate -vv src/` |
| **Tests** | pytest | Unit/integration/e2e | `pytest tests/` |

**Config:** `pyproject.toml` ([tool.ruff], [tool.mypy], [tool.basedpyright], [tool.bandit], [tool.interrogate], [tool.poe.tasks]).

**Makefile:** `lint-python`, `lint-python-fix`, `py-format`, `type-check`, `type-check-basedpyright`, `security-scan` (semgrep, bandit, pip-audit), `test-python`.

**CI:** Ruff lint/format, mypy, bandit, pip-audit, pytest (fast then slow, coverage). Semgrep in security-scan job.

**Optional:** `ty` (fast type checker), `pre-commit` (ruff, pycln, prettier, gofmt, biome).

---

## 2. TypeScript / Frontend

| Category | Tool | Role | Run |
|----------|------|------|-----|
| **Lint** | oxlint | ESLint-compatible rules, fast | `bun run lint` / `oxlint .` |
| **Format** | oxfmt | Format JS/TS (Oxc) | `bun run format` / `oxfmt .` |
| **Type** | oxlint (type-aware) | TypeScript-aware lint | `bun run typecheck` / `oxlint --type-check --type-aware .` |
| **CSS** | stylelint | CSS lint | `bun run lint:stylelint` |
| **Optional** | Biome | Lint + format (alternative) | `bun run lint:biome` |
| **Tests** | Vitest | Unit tests | `bun run test` / `vitest run` |
| **E2E** | Playwright | E2E tests | `bun run test:e2e` (apps/web) |

**Config:** `frontend/.oxlintrc.json`, `frontend/.oxfmtrc.json`, `frontend/apps/web/package.json` (scripts, vitest).

**Makefile:** `lint-frontend`, `lint-frontend-fix`, `typecheck-frontend`, `quality-frontend` (lint + typecheck + build + test).

**CI:** Oxlint check, typecheck, lint:oxc, stylelint, **format:check** (oxfmt), **Vitest** (unit tests). Playwright E2E in frontend-e2e job. **bun audit** in security-scan (continue-on-error).

---

## 3. Go

| Category | Tool | Role | Run |
|----------|------|------|-----|
| **Format** | gofumpt | Stricter gofmt | `gofumpt -l .` (check) / `gofumpt -w .` |
| **Lint** | golangci-lint | Multi-linter (revive, errcheck, govet, staticcheck, gosec, etc.) | `golangci-lint run --timeout=5m` |
| **Vulns** | govulncheck | Go vulnerability check | `govulncheck ./...` |

**Config:** `backend/.golangci.yml` (revive, gocritic, gosec, gocyclo, and many others).

**Makefile:** `lint-go`, `go-format`, `install-tools` (gofumpt, golangci-lint), `security-scan` (govulncheck).

**CI:** golangci-lint (v1.61), go test (short then full, race, coverage). govulncheck in local `make security-scan`.

See also: [Revive vs Other Go Linters](revive-and-go-linters-comparison.md).

---

## 4. Cross-stack

- **Unified quality:** `make quality` runs parallel quality (Go, Python, frontend) and report.
- **Lint all:** `make lint` runs `lint-go`, `lint-python`, `lint-frontend`.
- **Security:** `make security-scan` runs semgrep, bandit, pip-audit (Python), govulncheck (Go). CI: Trivy, Semgrep, bun audit (frontend).
- **Package manager:** Use **bun** for frontend; **uv**/pip for Python; **go** modules for Go.

---

## 5. Recommendations

- **Python:** Use ruff for lint/format; mypy (and optionally basedpyright) for types; bandit + pip-audit + semgrep for security; tach for architecture. Run `make lint-python`, `make type-check`, `make security-scan` (or poe quality/all).
- **Frontend:** Use oxlint + oxfmt for lint/format/typecheck; stylelint for CSS; Vitest for units, Playwright for E2E. Run `make lint-frontend`, `make typecheck-frontend`, `make quality-frontend`.
- **Go:** Use gofumpt for format; golangci-lint (with revive) for lint. Run `make lint-go`, `make go-format`.
- **CI:** All of the above are wired in `.github/workflows/ci.yml` (python-tests, go-tests, frontend-checks, frontend-e2e, security-scan).
