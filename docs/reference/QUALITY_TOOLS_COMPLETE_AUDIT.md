# Complete Quality/Linting/Checking Tools Audit
## Repository: `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace`

**Audit Date:** 2026-02-10
**Total Tools Found:** 32+
**Languages Covered:** Go, Python, TypeScript/JavaScript, YAML, JSON, Markdown

---

## QUALITY TOOLS BY LANGUAGE

### GO LINTING & ANALYSIS (6 tools)

#### 1. **golangci-lint**
- **Language:** Go
- **Config File:** `/.golangci-backend.yml`
- **How to Run:** `cd backend && golangci-lint run` (or via chunked: `scripts/lint-go-chunks.sh`)
- **Makefile Target:** `lint-go`, `quality`, `quality-external` → `quality-go-external`
- **Checks:** 
  - Defaults: errcheck, govet, ineffassign, staticcheck, unused
  - Style: revive, gocritic, gosec, bodyclose, rowserrcheck
  - Complexity: gocyclo, gocognit, mnd (magic numbers)
  - Naming: misspell, unconvert, nakedret
  - Exhaustiveness: exhaustive, nolintlint
  - Performance: prealloc, perfsprint, whitespace
  - AI Hardening: dupl, goconst, funlen, gochecknoglobals
- **Strictness:** Enabled 30+ linters across all categories
- **Memory Strategy:** Chunked linting by package (GOMAXPROCS=1 GOGC=5 GOMEMLIMIT=256MiB)

#### 2. **gofumpt**
- **Language:** Go
- **How to Run:** `cd backend && gofumpt -w .` OR `gofmt` (pre-commit hook)
- **Makefile Target:** Pre-commit hook (fast local linting)
- **Checks:** Code formatting (stricter than gofmt)
- **Strictness:** Basic format checking (pre-commit only, CI has golangci-lint)

#### 3. **govulncheck**
- **Language:** Go
- **Installed:** `/go/bin/govulncheck`
- **How to Run:** `cd backend && govulncheck ./...`
- **Makefile Target:** `quality-go-external`
- **Checks:** CVE scanning in dependencies (CRITICAL PATH)
- **Status:** Active (GO-2026-4337 CVE mitigated in go.mod→1.25.7)

#### 4. **go build -race**
- **Language:** Go
- **How to Run:** `cd backend && go build -race ./...`
- **Makefile Target:** `quality-go-external`
- **Checks:** Race condition detection (concurrency safety)
- **Strictness:** Fails on race condition detection

#### 5. **go test**
- **Language:** Go
- **How to Run:** `go test -v -race ./...` + route validation tests
- **Makefile Target:** `test`, `test-validate-backend-go`
- **Checks:** Unit + integration testing with race detection
- **Strictness:** -race flag enabled for safety

#### 6. **go mod tidy**
- **Language:** Go
- **How to Run:** `go mod tidy && git diff --exit-code go.mod go.sum`
- **Makefile Target:** `quality-go-external`
- **Checks:** Dependency validation (unused/missing deps)
- **Strictness:** Fails if go.mod/go.sum out of sync

---

### PYTHON LINTING & ANALYSIS (16 tools)

#### 1. **Ruff** (Multi-category linter & formatter)
- **Language:** Python
- **Config File:** `pyproject.toml` [tool.ruff] section
- **Installed:** `/miniforge3/bin/ruff`
- **How to Run:**
  - Format: `ruff format src/ tests/`
  - Lint: `ruff check src/ tests/ --output-format=grouped`
- **Makefile Targets:** `lint`, `lint-python`, `quality`, pre-commit hook
- **Selected Categories (Strict Profile):**
  - Core: E/W (errors/warnings), F (pyflakes), I (imports), B (flake8-bugbear), C4 (comprehensions)
  - Style/Best Practice: UP (pyupgrade), N (naming), PT (pytest), SIM (simplify), RUF (Ruff-specific)
  - Advanced: RSE/PERF/LOG/S (security), ASYNC/PIE/RET/PTH, DTZ/FA/Q
  - **Phase 5 Maximum Strictness (+9 categories):**
    - ANN (type annotations - strict: no *args: Any)
    - TRY (error handling)
    - ARG (unused arguments)
    - INT (integers)
    - PGH (Pygrep)
    - ISC (implicit string concatenation)
    - FURB (refurb)
    - G (logging)
    - TCH (type checking blocks)
- **Checks:** Linting (600+ rules), formatting (auto-fixable), type annotations, complexity
- **Strictness:** Maximum (Phase 5: +25pp bug prevention, 75-85% coverage)
- **McCabe Complexity:** max=6 (down from 7)
- **Max Args:** 4 (down from 5), Max Branches: 10 (down from 12)
- **Output Format:** Grouped by file for agent processing

#### 2. **mypy**
- **Language:** Python
- **Config File:** `mypy.ini`
- **Installed:** `/miniforge3/bin/mypy`
- **How to Run:** `mypy src/` (via pre-commit in CI)
- **Makefile Target:** Pre-commit (type checking moved to CI for speed)
- **Checks:** Static type checking (basic mode)
- **Strictness:** Basic typeCheckingMode (reportMissingParameterType: error)

#### 3. **basedpyright**
- **Language:** Python
- **Installed:** `/miniforge3/bin/basedpyright`
- **Config File:** `pyrightconfig.json`
- **How to Run:** `basedpyright` (type checking alternative to mypy)
- **Makefile Target:** Not explicitly in primary targets (installed for tools)
- **Checks:** Static type checking (faster than mypy)
- **Strictness:** basic mode

#### 4. **ty (Fast Type Checker)**
- **Language:** Python
- **Config File:** `pyproject.toml` [tool.ty] section
- **Installed:** Available as venv tool
- **How to Run:** `ty check src/`
- **Makefile Target:** `type-check-ty` (optional faster alternative)
- **Checks:** Type validation with per-file overrides
- **Overrides:** 30+ per-file rule exceptions for legacy/complex code
- **Strictness:** error-on-warning enabled

#### 5. **pytest**
- **Language:** Python
- **Config File:** `pyproject.toml` [tool.pytest.ini_options]
- **Installed:** Venv-based
- **How to Run:** `PYTHONPATH=src pytest tests/ -v -m unit`
- **Makefile Target:** `test`, `test-python-parallel` (with pytest-xdist via PYTEST_EXTRA)
- **Checks:** Unit/integration/e2e testing
- **Parallelization:** Optional via pytest-xdist with `-n auto`
- **Markers:** unit, e2e (test selection)

#### 6. **bandit**
- **Language:** Python (Security)
- **Config File:** `pyproject.toml` [tool.bandit]
- **Installed:** `/miniforge3/bin/bandit`
- **How to Run:** `bandit -r src/ --severity medium -f json -o .quality/baselines/python-bandit-latest.json`
- **Makefile Target:** `quality-python-external`
- **Checks:** Security linting (B-rules: assert_used, SQL injection, crypto, etc.)
- **Skips:** B101 (assert_used allowed in tests)
- **Output:** JSON baseline tracking

#### 7. **semgrep**
- **Language:** Python (+ Go/JS/TS security patterns)
- **Installed:** `/miniforge3/bin/semgrep`
- **How to Run:** `semgrep --config=p/python --config=p/security-audit src/`
- **Makefile Target:** `quality-python-external`
- **Pre-commit:** `semgrep --config=p/security-audit` (community preset)
- **Checks:** Custom security patterns (OWASP, PCI-DSS, etc.)
- **Strictness:** Community security audit preset

#### 8. **pip-audit**
- **Language:** Python (Dependency Security)
- **Installed:** `/miniforge3/bin/pip-audit`
- **How to Run:** `pip-audit --strict`
- **Makefile Target:** `quality-python-external`
- **Checks:** CVE scanning in installed dependencies
- **Strictness:** --strict flag (fail on any vulnerability)

#### 9. **interrogate**
- **Language:** Python (Documentation Coverage)
- **How to Run:** `interrogate --fail-under 85 src/`
- **Makefile Target:** `quality-python-external`
- **Config:** `pyproject.toml` [tool.interrogate]
- **Checks:** Docstring coverage enforcement
- **Threshold:** 85% (fail-under)
- **Strictness:** Docstring quality requirement

#### 10. **radon**
- **Language:** Python (Code Complexity Metrics)
- **How to Run:** `radon cc src/ -a -s --min=B` (cyclomatic complexity)
- **Makefile Target:** `quality-python-external`
- **Checks:** Complexity metrics (McCabe cyclomatic, maintainability index)
- **Output:** Report minimum B grade (medium complexity)

#### 11. **import-linter (lint-imports)**
- **Language:** Python (Architecture)
- **How to Run:** `lint-imports`
- **Makefile Target:** `quality-python-external`
- **Config File:** `pyproject.toml` [tool.importlinter]
- **Checks:** Module import contract enforcement
- **Strictness:** Validates declared dependencies and contracts

#### 12. **tach**
- **Language:** Python (Module Boundaries)
- **Installed:** `/miniforge3/bin/tach`
- **Config File:** `tach.toml`
- **How to Run:** `tach check`
- **Makefile Target:** `quality-python-external`
- **Checks:** Strict module boundary enforcement (DAG validation)
- **Strictness:** 
  - exact = true (fail on unused deps)
  - forbid_circular_dependencies = true
  - unused_ignore_directives = error
- **Architecture:** Enforces tracertm.config → tracertm.core → tracertm.models hierarchy

#### 13. **pycln (Unused Import Removal)**
- **Language:** Python (Cleanup)
- **How to Run:** `pycln --all` (pre-commit hook)
- **Pre-commit:** Automatic cleanup of unused imports
- **Checks:** Removes unused imports + relative imports cleanup

#### 14. **pydocstyle (via Ruff)**
- **Language:** Python (Documentation Style)
- **Config:** `pyproject.toml` [tool.ruff.lint.pydocstyle]`
- **Convention:** Google-style (FastAPI standard)
- **Checks:** Docstring style validation (D-rules in Ruff)

#### 15. **pylint (via Ruff)**
- **Language:** Python (Linting)
- **Config:** `pyproject.toml` [tool.ruff.lint.pylint]`
- **Checks:** Function complexity (max-args, max-branches, max-returns)
- **Strictness:** 
  - max-args: 4
  - max-branches: 10
  - max-returns: 6

#### 16. **mccabe (via Ruff)**
- **Language:** Python (Complexity)
- **Config:** `pyproject.toml` [tool.ruff.lint.mccabe]`
- **Checks:** McCabe cyclomatic complexity
- **Threshold:** max-complexity = 6

---

### TYPESCRIPT/JAVASCRIPT/FRONTEND LINTING (9 tools)

#### 1. **oxlint** (Rust-based, ultra-fast linter)
- **Language:** TypeScript/JavaScript/JSX
- **Config Files:**
  - Root: `biome.json` (basic ignores)
  - Per-app: `frontend/.oxlintrc.json`, `frontend/apps/web/.oxlintrc.json`, etc.
- **How to Run:** 
  - Main: `cd frontend && bun run format && bun run lint`
  - Explicit: `oxlint -c .oxlintrc.json -f unix --type-check --type-aware`
  - Web-specific: `oxlint -c .oxlintrc.json -f unix --threads 1 --type-check --type-aware --tsconfig apps/web/tsconfig.oxlint.json apps/web/src`
- **Makefile Targets:** `lint`, `lint-frontend`, `fe-lint`, `quality`
- **Frontend package.json Scripts:**
  - `lint`: oxfmt (format)
  - `lint:web`: oxlint with type checking
  - `format`: oxfmt
  - `check`: lint + format:check + typecheck
- **Plugins Enabled:**
  - ESLint compat, TypeScript, Unicorn, Oxc, React, React-Perf, Import, JSX-a11y
  - Promise, Vitest, React-hooks
  - JS Plugins: eslint-plugin-check-file, eslint-plugin-boundaries, eslint-plugin-filename-export
- **Pre-commit:** Fast local linting (oxlint not in pre-commit; gofmt + Ruff only)
- **Checks:** Linting (ESLint rules), formatting, type awareness
- **Strictness:** Type-aware analysis with multi-plugin system

#### 2. **typescript (tsc)**
- **Language:** TypeScript
- **How to Run:** 
  - `tsc --noEmit` (type checking only, no emit)
  - Via oxlint: type-aware checking
- **Makefile Target:** `quality-frontend-external`, `fe-type`, `typecheck`
- **Checks:** TypeScript compilation errors (strict mode)
- **Strictness:** Standalone type checking

#### 3. **knip** (Dead Code Detection)
- **Language:** TypeScript/JavaScript
- **Installed:** bun dependency (in frontend/package.json)
- **How to Run:** `cd frontend && knip --include files,exports,dependencies`
- **Makefile Target:** `quality-frontend-external`
- **Checks:** Unused files, exports, dependencies, types
- **Strictness:** Fails on dead code detection

#### 4. **madge** (Circular Dependency Detection)
- **Language:** TypeScript/JavaScript (graph analysis)
- **Installed:** bun dependency
- **How to Run:** `cd frontend && madge --circular apps/web/src/`
- **Makefile Target:** `quality-frontend-external`
- **Checks:** Circular dependency detection
- **Strictness:** Fails on circular dependencies

#### 5. **stylelint** (CSS/SCSS Linting)
- **Language:** CSS/SCSS
- **Installed:** bun dependency with stylelint-config-recommended + stylelint-config-tailwindcss
- **How to Run:** `bun run lint:stylelint` (auto-fix) + `stylelint "apps/**/*.css" "packages/**/*.css"`
- **Makefile Target:** `lint-frontend` invokes this
- **Checks:** CSS best practices, Tailwind consistency
- **Configs:** Recommended + Tailwind CSS plugin

#### 6. **prettier** (Code Formatter)
- **Language:** YAML, JSON, Markdown
- **Pre-commit Hook:** `v3.1.0` via mirrors-prettier
- **How to Run:** Auto via pre-commit
- **Checks:** Code formatting (YAML/JSON/Markdown only)
- **Strictness:** Fast formatter for config files

#### 7. **biome** (All-in-one toolchain)
- **Config File:** `biome.json` (minimal config with ignorePatterns)
- **Role:** Infrastructure for oxlint/formatting
- **Checks:** Schema validation for project structure

#### 8. **type-coverage** (Type Coverage Metrics)
- **Language:** TypeScript
- **Installed:** bun dependency
- **How to Run:** Not explicitly in Makefile (metric tool)
- **Checks:** Type coverage percentage across codebase

#### 9. **ESLint Plugins (TS specific)**
- **Language:** TypeScript/JavaScript
- **Installed Plugins:**
  - eslint-plugin-boundaries: Module boundary enforcement
  - eslint-plugin-check-file: File naming rules
  - eslint-plugin-filenames: Filename conventions
  - @typescript-eslint/eslint-plugin: TS-specific rules
- **Config:** Integrated via oxlint plugins section
- **Checks:** Module structure, naming, conventions

---

## SUPPORTING TOOLS & SCRIPTS

### Custom Python Scripts (Quality Automation)

#### 1. **check_naming_explosion.py** (Cross-Language)
- **Location:** `scripts/quality/check_naming_explosion.py`
- **Config:** `config/naming-guard.json`
- **How to Run:** `bash scripts/shell/check-naming-explosion-python.sh` + Go/Frontend variants
- **Languages:** Go, Python, TypeScript/JavaScript
- **Checks:**
  - Forbidden words in filenames/directories (new, improved, enhanced, temp, draft, etc.)
  - Forbidden identifier words in code (subset of above)
  - Filename length (max 120 chars)
  - Directory name length (max 80 chars)
  - Identifier length (max 48 chars)
  - Path depth (max 12 levels)
- **Strictness:** Hard fail on naming violations with domain exceptions

#### 2. **check_file_loc.py** (Lines of Code Guard)
- **Location:** `scripts/quality/check_file_loc.py`
- **Config:** `config/loc-guard.json`
- **How to Run:** `bash scripts/shell/check-file-loc.sh`
- **Checks:**
  - Max file size: 500 LOC (per file)
  - Tracked via allowlist: `config/loc-allowlist.txt` (22,609 lines of exceptions)
- **Strictness:** Enforces file complexity limit with override mechanism

#### 3. **extract_test_constants.py** (Test Automation)
- **Location:** `scripts/quality/extract_test_constants.py`
- **Purpose:** Extract test constants for Phase 5 testing framework

#### 4. **add_test_noqa.py** (Linter Directive Management)
- **Location:** `scripts/quality/add_test_noqa.py`
- **Purpose:** Auto-add `# noqa` directives to suppress linter false positives

#### 5. **auto_update_loc.py** (LOC Allowlist Update)
- **Location:** `scripts/quality/auto_update_loc.py`
- **Purpose:** Automatic update mechanism for LOC allowlist

---

### CI/Orchestration Scripts

#### 1. **run-quality-split.sh** (Parallel Pipeline)
- **Location:** `scripts/shell/run-quality-split.sh`
- **Purpose:** Run 12 quality steps in parallel (naming, go-lint, go-proto, go-build, go-test, py-lint, py-type, py-test, fe-lint, fe-type, fe-build, fe-test)
- **Log Storage:** `.quality/logs/<step>.log` + `.quality/logs/<step>.exit`
- **Refresh:** Optional live report updates (REFRESH_INTERVAL env var)
- **Parallelization:** All steps concurrent with final report

#### 2. **quality-report.sh** (Result Aggregation)
- **Location:** `scripts/shell/quality-report.sh`
- **Purpose:** Parse `.quality/logs/` and generate action plan
- **Makefile Target:** `quality-report`, `quality-report-watch`

#### 3. **lint-go-chunks.sh** (Memory-Efficient Go Linting)
- **Location:** `scripts/lint-go-chunks.sh`
- **Purpose:** Run golangci-lint per-package to avoid OOM
- **Memory Settings:** GOMAXPROCS=1 GOGC=5 GOMEMLIMIT=256MiB
- **Linter Limits:** --max-issues-per-linter=1 --max-same-issues=1

#### 4. **check-naming-explosion-*.sh** (Language-Specific)
- **Location:** `scripts/shell/check-naming-explosion-{python,go}.sh`
- **Location:** `frontend/scripts/check-naming-explosion.sh`
- **Purpose:** Invoke custom naming guard script per language

#### 5. **check-file-loc.sh**
- **Location:** `scripts/shell/check-file-loc.sh`
- **Purpose:** Invoke LOC guard script

---

## QUALITY EXECUTION HIERARCHY

### Make Targets (from Makefile)

**Primary Quality Targets:**
```
make quality                  # Full parallel pipeline (12 steps)
make quality-report          # View action plan from last run
make quality-watch           # Watch mode with live reporting
make quality-external        # Run external security/architecture tools
  ├─ quality-go-external     # govulncheck, race detection, mod tidy
  ├─ quality-python-external # bandit, pip-audit, semgrep, interrogate, radon, tach, lint-imports
  └─ quality-frontend-external # tsc, knip, madge

make lint                    # Naming + linters (Go/Python/Frontend)
  ├─ lint-naming             # Naming explosion + LOC guards
  ├─ lint-go                 # golangci-lint + gofumpt
  ├─ lint-python             # Ruff format + Ruff check
  └─ lint-frontend           # oxlint + stylelint

make type-check              # Type checking (mypy + tsc + oxlint --type-aware)
make format                  # Code formatting (Ruff + oxfmt)
make test                    # Unit/integration tests (pytest + Go + frontend)
```

**Per-Language Targets:**
```
make type-check-ty           # Fast type checker (ty) alternative
make test-python-parallel    # pytest with -n auto (xdist)
make test-python-uv          # pytest via uv
make test-validate-*         # Route/health validation tests
```

---

## PRE-COMMIT HOOKS (Local Development)

**File:** `.pre-commit-config.yaml`

**Fast Checks (target <5s):**
- ruff (check + format)
- trailing-whitespace
- end-of-file-fixer
- check-yaml
- check-added-large-files (1000 KB max)
- check-merge-conflict
- debug-statements
- mixed-line-ending
- pycln (unused imports)
- prettier (YAML/JSON/Markdown)
- gofmt (Go formatting only)

**Slow Checks Moved to CI:**
- ty (type checking)
- semgrep (security patterns)
- interrogate (docstring coverage)
- pytest (unit tests)

---

## CONFIGURATION FILES SUMMARY

| Tool | Config File | Type |
|------|---|---|
| Ruff | `pyproject.toml` [tool.ruff*] | TOML (18 sections) |
| mypy | `mypy.ini` | INI |
| Pyright | `pyrightconfig.json` | JSON |
| ty | `pyproject.toml` [tool.ty] | TOML (30+ per-file overrides) |
| pytest | `pyproject.toml` [tool.pytest.ini_options] | TOML |
| Bandit | `pyproject.toml` [tool.bandit] | TOML |
| interrogate | `pyproject.toml` [tool.interrogate] | TOML |
| tach | `tach.toml` | TOML (7 modules defined) |
| import-linter | `pyproject.toml` [tool.importlinter] | TOML |
| golangci-lint | `.golangci-backend.yml` | YAML (30+ linters) |
| oxlint | `biome.json` + `.oxlintrc.json` (per-app) | JSON |
| stylelint | Via bun package.json | JSON deps |
| Pre-commit | `.pre-commit-config.yaml` | YAML |
| Naming Guard | `config/naming-guard.json` | JSON |
| LOC Guard | `config/loc-guard.json` | JSON |

---

## INSTALLED TOOLS VERIFICATION

**Installed:** ✅ All 8 critical tools present on system
```
/Users/kooshapari/miniforge3/bin/mypy
/Users/kooshapari/miniforge3/bin/ruff
/Users/kooshapari/miniforge3/bin/bandit
/Users/kooshapari/miniforge3/bin/semgrep
/Users/kooshapari/go/bin/govulncheck
/Users/kooshapari/miniforge3/bin/pip-audit
/Users/kooshapari/miniforge3/bin/tach
/Users/kooshapari/miniforge3/bin/basedpyright
```

**Frontend Tools:** Installed via bun (knip, madge, oxlint, stylelint, type-coverage)

---

## QUALITY METRICS & BASELINES

**Storage Location:** `.quality/` directory

**Baseline Files:**
- `.quality/baselines/python-bandit-latest.json` - Security findings
- `.quality/baselines/*.json` - External tool outputs
- `.quality/logs/` - Per-step execution logs

**Coverage Tracking:**
- `[tool.coverage.run]` in pyproject.toml
- HTML reports: `htmlcov/`

---

## STRICTNESS ASSESSMENT

### Phase 5 Maximum Strictness (2026-02-07)

**Bug Prevention Rate:** 75-85% (up from 50-60%)
**Total Checks:** 138 (up from 102)
**Categories:** 
- **Go:** 30+ linters across 6 categories
- **Python:** 16 tools, 43+ Ruff categories (9 new: ANN, TRY, ARG, INT, PGH, ISC, FURB, G, TCH)
- **TypeScript:** 9 tools (oxlint ultra-strict, type-aware checking)

**Auto-Fixed:** 1,022 files, ~23,000 violations
**Agent Swarm:** 3 parallel agents fixing ~2,700-3,500 violations/session

**Critical CVE Mitigated:** GO-2026-4337 (govulncheck integration)

---

## ANTI-PATTERNS & LESSONS LEARNED

1. **Parallel Linting:** All steps concurrent in `run-quality-split.sh` (12 parallel processes)
2. **Memory Efficiency:** Chunked Go linting (per-package) to prevent OOM
3. **Pre-commit Speed:** <5s target via fast checks only (slow checks in CI)
4. **Module Boundaries:** Tach enforces strict DAG (no cycles, unused deps fail)
5. **Naming Consistency:** Single source of truth in `config/naming-guard.json` (shared across languages)
6. **Type Safety:** Multi-tier (ruff ANN strict, mypy, pyright, ty, tsc, oxlint type-aware)

---

## EXECUTION QUICK REFERENCE

**Local Development:**
```bash
make lint           # Fast naming + linting (pre-commit style)
make type-check     # Type checking (mypy + tsc)
make test           # Unit tests
make quality        # Full parallel pipeline (lint + type + build + test)
```

**CI/Comprehensive:**
```bash
make quality-external       # Security + architecture validation
make quality-report         # Parse results and generate action plan
make validate               # E2E route/health validation
```

**Specific Tool Invocation:**
```bash
ruff check src/ --output-format=grouped
bandit -r src/
govulncheck ./...
tach check
cd frontend && knip --include files,exports,dependencies
```

---

## CONFIGURATION DRIFT PREVENTION

**Centralized Config Rules:**
- Ruff all rules in `pyproject.toml` (single source)
- ty overrides per-file in `pyproject.toml` (no separate files)
- tach modules in `tach.toml` (architecture as code)
- Naming rules in `config/naming-guard.json` (cross-language)
- LOC rules in `config/loc-guard.json` (single allowlist)

**Version Pinning:**
- Pre-commit: All tools pinned to specific versions
- Bun/npm: `bun.lock` (lockfile)
- Go: `go.mod` (module versioning)
- Python: `uv.lock` or virtual environment

