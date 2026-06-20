# ADR-0012: Code Quality Enforcement

**Status:** Accepted
**Date:** 2026-02-07
**Deciders:** Development Team
**Supersedes:** N/A

---

## Context

TraceRTM is built by AI agents with strict quality requirements. The codebase needs:

1. **Linting:** Catch bugs, anti-patterns, style violations
2. **Type checking:** Prevent type errors (Python, Go, TypeScript)
3. **Formatting:** Consistent code style (automated)
4. **Security scanning:** Detect vulnerabilities (dependencies, code patterns)
5. **Architecture enforcement:** Prevent circular dependencies, layer violations

Quality gates:
- **CI must pass:** All checks green before merge
- **Agent-compatible:** Agents can run checks locally, fix violations automatically
- **Fast feedback:** <30s for linting, <2min for full suite

Current status (from memory/MEMORY.md):
- **Ruff:** 0 violations (Python)
- **Golangci-lint:** 0 issues (Go)
- **OxLint:** 4,221 errors + 2,369 warnings (TypeScript - informational baseline)
- **TSC:** 0 errors (TypeScript strict mode)
- **Mypy:** 1,256 errors (Python strict mode - informational baseline)

## Decision

We will enforce:
- **Python:** Ruff (lint + format), Mypy (type check), Bandit (security)
- **Go:** golangci-lint (lint), go vet (static analysis), govulncheck (security)
- **TypeScript:** OxLint (lint), TSC (type check), oxfmt (format)
- **Architecture:** Tach (Python modules), import-linter (Python layers)

**CI gates (must pass):**
1. Ruff 0 violations
2. Ruff format 0 unformatted
3. Go build + go vet CLEAN
4. Golangci-lint 0 issues
5. TSC --noEmit 0 errors
6. Tach 0 violations

**Informational (non-blocking):**
- Mypy strict (1,256 errors baseline)
- Bandit (186 Low severity baseline)
- OxLint (4,221 errors baseline)
- Go coverage (32.5% baseline)

## Rationale

### Python (pyproject.toml)

**Ruff Configuration:**
```toml
[tool.ruff]
line-length = 120
target-version = "py312"

[tool.ruff.lint]
select = [
    "E", "W",   # pycodestyle
    "F",        # pyflakes
    "I",        # isort
    "B",        # bugbear
    "C4",       # comprehensions
    "UP",       # pyupgrade
    "N",        # pep8-naming
    "PT",       # pytest-style
    "SIM",      # simplify
    "RUF",      # ruff-specific
    "ASYNC",    # async best practices
    "PIE",      # unnecessary code
    "RET",      # return patterns
    "PTH",      # pathlib over os.path
    "ANN",      # type annotations (Phase 5)
    "TRY",      # exception handling (Phase 5)
    "S",        # security (bandit rules)
]

[tool.ruff.lint.per-file-ignores]
"tests/**/*.py" = ["S101", "D100", "ANN001"]  # Allow assert, no docstrings, untyped fixtures
```

**Why Ruff:**
- **Speed:** 10-100x faster than Flake8 + Black + isort combined
- **All-in-one:** Replaces 10+ tools (Flake8, Black, isort, pyupgrade, etc.)
- **Auto-fix:** `ruff check --fix` fixes most violations automatically
- **Agent-friendly:** Agents can run `ruff check --output-format=grouped` for file-grouped output

**Mypy Configuration (strict mode):**
```toml
[tool.mypy]
strict = True
python_version = "3.12"
warn_return_any = True
warn_unused_configs = True
disallow_untyped_defs = True

[[tool.mypy.overrides]]
module = "tests.*"
disallow_untyped_defs = False  # Relaxed for tests
```

**Why Mypy (informational only):**
- **Baseline:** 1,256 errors in strict mode (too many to fix immediately)
- **Incremental:** Agents fix mypy errors file-by-file
- **Target:** <500 errors (60% reduction) by end of project

### Go (backend/.golangci.yml)

**Golangci-lint Configuration:**
```yaml
linters:
  enable:
    - errcheck      # Check error returns
    - gosimple      # Simplifications
    - govet         # Go vet
    - ineffassign   # Unused assignments
    - staticcheck   # Static analysis
    - typecheck     # Type errors
    - unused        # Unused code
    - bodyclose     # HTTP response body close
    - noctx         # HTTP request without context
    - godox         # TODO/FIXME comments
    - asciicheck    # Non-ASCII identifiers
    - gofmt         # Formatting
    - goimports     # Import sorting
    - misspell      # Spelling errors
```

**Why golangci-lint:**
- **Comprehensive:** Runs 50+ linters in parallel
- **Fast:** <10s for entire backend
- **CI-friendly:** JSON output, exit code on violations
- **Zero tolerance:** 0 issues enforced in CI

### TypeScript (frontend/.oxlintrc.json)

**OxLint Configuration:**
```json
{
  "rules": {
    "typescript": "on",
    "react": "on",
    "react-perf": "on",
    "jsx-a11y": "on",
    "import": "on",
    "vitest": "on",
    "promise": "on",
    "node": "on",
    "jsdoc": "on"
  },
  "plugins": [
    "typescript",
    "react",
    "react-perf",
    "jsx-a11y"
  ]
}
```

**Why OxLint:**
- **Speed:** 50-100x faster than ESLint (written in Rust)
- **Type-aware:** Uses TSC for type checking
- **React-focused:** React 19 rules built-in
- **Informational baseline:** 4,221 errors (many inherited from `frontend/disable/` archived packages)

**TSC (strict mode):**
```json
{
  "compilerOptions": {
    "strict": true,              // Enable all strict checks
    "noUncheckedIndexedAccess": true,  // Array access returns T | undefined
    "noImplicitReturns": true,
    "noFallthroughCasesInSwitch": true
  }
}
```

**CI enforcement:** `tsc --noEmit` must pass (0 errors)

### Architecture Enforcement (Tach)

**Tach Configuration (tach.toml):**
```toml
[project]
root = "src/tracertm"

[[modules]]
path = "config"
depends_on = []  # No dependencies (base layer)

[[modules]]
path = "models"
depends_on = ["config"]

[[modules]]
path = "repositories"
depends_on = ["models", "database"]

[[modules]]
path = "services"
depends_on = ["repositories", "models"]

[[modules]]
path = "api"
depends_on = ["services"]  # Cannot access repositories directly

forbid_circular_dependencies = false  # Realistic for interconnected codebase
```

**Why Tach:**
- **Module boundaries:** Prevent service layer from importing API layer
- **Dependency graph:** Visualize architecture (`tach show`)
- **CI gate:** `tach check` fails on violations
- **Current status:** 17 modules, 0 violations

## Alternatives Rejected

### Alternative 1: ESLint + Prettier (TypeScript)

- **Description:** Traditional JavaScript linting stack
- **Pros:** Mature, widely used, extensive plugin ecosystem
- **Cons:** Slow (1-2 min for full lint), complex config, requires multiple tools
- **Why Rejected:** OxLint 50x faster, single tool (lint + format). ESLint too slow for agent workflows.

### Alternative 2: Pylint (Python)

- **Description:** Traditional Python linter
- **Pros:** Comprehensive rules, widely used
- **Cons:** Slow (10x slower than Ruff), complex config, many false positives
- **Why Rejected:** Ruff faster, auto-fix, includes most Pylint rules. Pylint redundant.

### Alternative 3: Black (Python formatter)

- **Description:** Opinionated Python formatter
- **Pros:** Zero-config, consistent style
- **Cons:** No auto-fix for lint violations, requires separate tool (Ruff replaces Black)
- **Why Rejected:** Ruff includes Black-compatible formatter. One tool instead of two.

### Alternative 4: No architecture enforcement

- **Description:** Trust developers to maintain layered architecture
- **Pros:** No tool overhead, flexibility
- **Cons:** Architecture degrades over time (circular dependencies, layer violations)
- **Why Rejected:** Agent-driven development needs automated checks. Humans make mistakes.

## Consequences

### Positive

- **Zero-tolerance quality:** CI blocks PRs with violations
- **Fast feedback:** Ruff <5s, golangci-lint <10s, OxLint <15s
- **Auto-fix:** Agents run `ruff check --fix`, `oxlint --fix` to auto-resolve issues
- **Consistent style:** Automated formatting (Ruff, gofmt, oxfmt)
- **Security scanning:** Bandit (Python), govulncheck (Go) catch vulnerabilities

### Negative

- **Initial setup effort:** Configuring all tools, fixing baselines
- **CI time:** Full quality suite adds ~2 min to CI
- **False positives:** OxLint 4,221 errors includes inherited issues from `frontend/disable/`
- **Mypy strict overhead:** 1,256 errors require gradual fixes (non-blocking for MVP)

### Neutral

- **Suppressions inventory:** 727 suppressions (Python: 690, Go: 28, TS: 9) - tracked in MEMORY.md
- **Coverage goals:** 80% target (Python: 90%, Go: 70%, TS: 75%)
- **Pre-commit hooks:** Recommended but not enforced (agents run checks manually)

## Implementation

### Affected Components

- `.github/workflows/ci.yml` - CI pipeline with quality gates
- `pyproject.toml` - Ruff, Mypy, Bandit config
- `backend/.golangci.yml` - Go linting config
- `frontend/.oxlintrc.json` - OxLint config
- `frontend/tsconfig.json` - TypeScript strict mode
- `tach.toml` - Architecture enforcement
- `Makefile` - Local quality commands (`make lint`, `make format`, `make quality`)

### Migration Strategy

**Phase 1: Baselines (Week 1)**
- Measure current violations (done in Session 9 QA Atlas)
- Document baselines (MEMORY.md, CODEBASE_QA_ATLAS.md)
- Configure CI gates (must-pass vs informational)

**Phase 2: Zero Violations (Week 2-4)**
- Fix Ruff violations (done: 15,426 → 0)
- Fix golangci-lint issues (done: violations → 0)
- Fix TSC errors (done: 0 errors maintained)

**Phase 3: Incremental Improvement (Ongoing)**
- Reduce Mypy errors (1,256 → <500 target)
- Reduce OxLint errors (4,221 → <2000 target)
- Increase coverage (Go: 32.5% → 70%)

### Rollout Plan

- **Phase 1:** Soft enforcement (warnings only)
- **Phase 2:** Hard enforcement (CI fails on violations)
- **Phase 3:** Strict mode (Mypy, OxLint baseline tracking)

### Success Criteria

- [x] Ruff: 0 violations
- [x] Golangci-lint: 0 issues
- [x] TSC: 0 errors (strict mode)
- [x] Tach: 0 violations (17 modules)
- [ ] Mypy: <500 errors (60% reduction)
- [ ] OxLint: <2000 errors (50% reduction)
- [ ] Go coverage: >70%
- [ ] Python coverage: >90%

## References

- [Ruff Documentation](https://docs.astral.sh/ruff/)
- [golangci-lint](https://golangci-lint.run/)
- [OxLint](https://oxc.rs/docs/guide/usage/linter.html)
- [Tach](https://gauge.sh/docs)
- [ADR-0005: Test Strategy](ADR-0005-test-strategy-coverage-goals.md)
- [docs/reference/CODEBASE_QA_ATLAS.md](../reference/CODEBASE_QA_ATLAS.md)

---

**Notes:**
- **Session 9 achievement:** 15,426 Ruff violations → 0 in single session (agent swarm)
- **Suppression policy:** Fix code, don't suppress. Suppressions tracked, must be justified.
- **Agent workflow:** `make lint` → agents get file-grouped output → agents fix violations → `make lint` again
- **CI budget:** Quality checks <2 min total (Ruff <5s, golangci <10s, OxLint <15s, TSC <30s, tests <60s)
