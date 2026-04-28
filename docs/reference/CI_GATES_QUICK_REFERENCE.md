# CI Quality Gates Quick Reference

**PRODUCTION-GRADE ENFORCEMENT** | All gates required, hard failures, zero bypasses

---

## Coverage Thresholds (Hard Enforced)

| Language | Threshold | Enforcer | Enforcement |
|----------|-----------|----------|-------------|
| **Python** | 90% | pytest `--cov-fail-under=90` | Blocks merge |
| **Go** | Tracked | golangci-lint | Reports generated |
| **TypeScript** | 90% | vitest thresholds | Blocks merge |

---

## Complexity Limits (Hard Enforced)

| Language | Metric | Limit | Enforcer | Tool |
|----------|--------|-------|----------|------|
| **Python** | McCabe | ≤7 | ruff C90 | Ruff |
| **Python** | Function length | ≤80 lines | funlen | Ruff |
| **Python** | Max args | ≤5 | PLR0913 | Ruff |
| **Python** | Max branches | ≤12 | PLR0912 | Ruff |
| **Python** | Max statements | ≤50 | PLR0915 | Ruff |
| **Go** | McCabe | ≤10 | gocyclo | golangci-lint |
| **Go** | Cognitive | ≤12 | gocognit | golangci-lint |
| **Go** | Function length | ≤80 lines | funlen | golangci-lint |

---

## Linter Suites

### Python (ci.yml:88-121)
```
✅ ruff check (format + lint + complexity)
✅ ty check --error-on-warning (strict types)
✅ bandit -r src/ (security)
✅ semgrep (SAST)
✅ pip-audit (dependencies)
✅ interrogate --fail-under=85 (docstrings)
✅ pytest --cov-fail-under=90 (coverage)
```

### Go (go-tests.yml:20-30)
```
✅ golangci-lint run (15+ linters)
  - errcheck, govet, staticcheck, gosec
  - gocyclo, gocognit, funlen, mnd
  - dupl, goconst, depguard, revive
✅ go test -v -race (unit + integration)
✅ coverage reports
```

### TypeScript (test.yml:93-103)
```
✅ vitest thresholds (90% all 4 metrics)
✅ vitest coverage reporters
✅ Global setup.ts (MSW, ResizeObserver, mocks)
```

---

## Required Status Checks (Branch Protection)

1. ✅ **ci.yml** - Python + security + docstrings
2. ✅ **quality.yml** - Multi-version Python
3. ✅ **test.yml** - All three ecosystems
4. ✅ **go-tests.yml** - Go linting + coverage
5. ✅ **pre-commit.yml** - Hook enforcement

---

## Bypass Prevention

| Vector | Status |
|--------|--------|
| `|| true` on quality gates | ❌ Not allowed |
| `continue-on-error: true` on critical gates | ❌ Not allowed |
| `--tb=no` (hide tracebacks) | ❌ Not allowed |
| Coverage exceptions | ❌ Hard threshold (90%) |
| Test skip allowance | ❌ All tests must run |
| Optional linters | ❌ All required |

---

## Security Scanning

| Scanner | Scope | Enforced |
|---------|-------|----------|
| **Bandit** | Python security | ✅ YES |
| **Semgrep** | Multi-language SAST | ✅ YES |
| **Gosec** | Go security | ✅ YES |
| **pip-audit** | Dependency vulns | ✅ YES |

---

## Architecture Enforcement

| Tool | Scope | Enforced |
|------|-------|----------|
| **tach** | Python layering | ✅ YES |
| **depguard** | Go boundaries | ✅ YES |
| **import-linter** | Python imports | ✅ YES |

---

## Key Files

| File | Purpose |
|------|---------|
| `pyproject.toml` | Python quality config (coverage, ruff, ty, docstrings) |
| `backend/.golangci.yml` | Go linting (15+ linters, 269 lines) |
| `frontend/apps/web/vitest.config.ts` | TypeScript coverage thresholds |
| `.github/workflows/ci.yml` | Main pipeline (1537 lines) |
| `.github/workflows/quality.yml` | Python multi-version checks |

---

## Coverage Commands

```bash
# Python: Run with coverage enforcement
pytest tests/ --cov=src/tracertm --cov-fail-under=90

# Go: Run with coverage reporting
go test -v -race -coverprofile=coverage.out ./...
go tool cover -html=coverage.out

# TypeScript: Run with vitest threshold enforcement
npm run test  # vitest checks 90% on branches/functions/lines/statements
```

---

## Configuration Locations

```
Python:
  - pyproject.toml (coverage, ruff, ty, interrogate, tach, import-linter)

Go:
  - backend/.golangci.yml (golangci-lint config, 15+ linters)

TypeScript:
  - frontend/apps/web/vitest.config.ts (coverage thresholds)
  - frontend/apps/web/src/__tests__/setup.ts (global mocks)

CI/CD:
  - .github/workflows/ci.yml (main pipeline)
  - .github/workflows/quality.yml (Python)
  - .github/workflows/test.yml (all ecosystems)
  - .github/workflows/go-tests.yml (Go)
```

---

## Enforcement Philosophy

**REQUIRED + FAIL-HARD + ZERO BYPASSES**

All quality gates are:
- ✅ **Required:** Must pass before merge
- ✅ **Fail-Hard:** No `continue-on-error` exceptions
- ✅ **Transparent:** Full logs + actionable messages
- ✅ **Multi-Layer:** Pre-commit + CI + architecture checks

---

## Quick Troubleshooting

| Issue | Solution | Config |
|-------|----------|--------|
| Coverage <90% | Add tests | `--cov-fail-under=90` |
| McCabe too high | Refactor | `max-complexity = 7` (Python), `min-complexity: 10` (Go) |
| Type error | Fix type | `ty check --error-on-warning` |
| Security issue | Review/fix | bandit/semgrep/gosec output |
| Linter violation | Auto-fix or justify | ruff/golangci-lint reports |

---

## Audit Summary

| Category | Status | Details |
|----------|--------|---------|
| **Coverage** | ✅ ENFORCED | 90% minimum, hard fail |
| **Complexity** | ✅ ENFORCED | McCabe ≤7 (Py), ≤10 (Go) |
| **Type Safety** | ✅ ENFORCED | Strict mode on Py + TS |
| **Security** | ✅ ENFORCED | 3+ scanners, medium+ severity |
| **Architecture** | ✅ ENFORCED | tach + depguard boundaries |
| **Documentation** | ✅ ENFORCED | 85% docstring coverage |
| **Bypasses** | ✅ NONE FOUND | Zero silent fallbacks |

---

**Last Updated:** 2026-02-06
**Compliance:** PRODUCTION-READY
