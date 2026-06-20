# Quality Tools Quick Reference

**Complete audit:** See `/docs/reference/QUALITY_TOOLS_COMPLETE_AUDIT.md`

## All Tools by Category

### GO LINTING (6 tools)
| Tool | Purpose | Config | Run Command | Strictness |
|------|---------|--------|---|---|
| golangci-lint | Comprehensive linting | `.golangci-backend.yml` | `cd backend && golangci-lint run` | 30+ linters |
| gofumpt | Code formatting | None | `gofumpt -w .` | Basic |
| govulncheck | CVE scanning | None | `govulncheck ./...` | Critical |
| go build -race | Race detection | None | `go build -race ./...` | Safety |
| go test | Testing | None | `go test -v -race ./...` | Unit/Integration |
| go mod tidy | Dependency validation | None | `go mod tidy` | Strict |

### PYTHON LINTING (16 tools)
| Tool | Purpose | Config | Run Command | Strictness |
|------|---------|--------|---|---|
| **Ruff** | Multi-category linter + formatter | `pyproject.toml` | `ruff format src/ && ruff check src/` | 43 categories (Phase 5 max) |
| mypy | Type checking | `mypy.ini` | `mypy src/` | Basic |
| basedpyright | Alt. type checker | `pyrightconfig.json` | `basedpyright` | Basic |
| ty | Fast type checker | `pyproject.toml` | `ty check src/` | error-on-warning |
| pytest | Testing | `pyproject.toml` | `pytest tests/ -v` | Unit/Integration/E2E |
| **bandit** | Security linting | `pyproject.toml` | `bandit -r src/` | Medium severity |
| **semgrep** | Security patterns | `.semgrep.yml` | `semgrep --config=p/security-audit src/` | Community preset |
| **pip-audit** | Dependency CVE | None | `pip-audit --strict` | Critical |
| interrogate | Docstring coverage | `pyproject.toml` | `interrogate --fail-under 85 src/` | 85% minimum |
| radon | Complexity metrics | None | `radon cc src/ -a -s --min=B` | B grade+ |
| import-linter | Architecture | `pyproject.toml` | `lint-imports` | Contracts |
| **tach** | Module boundaries | `tach.toml` | `tach check` | DAG strict |
| pycln | Unused imports | None | `pycln --all` | Cleanup |
| pydocstyle | Doc style | `pyproject.toml` | Via Ruff D-rules | Google style |
| pylint | Linting | `pyproject.toml` | Via Ruff PLR rules | Complexity |
| mccabe | Cyclomatic | `pyproject.toml` | Via Ruff C90 rules | Max-6 |

### TYPESCRIPT/JAVASCRIPT LINTING (9 tools)
| Tool | Purpose | Config | Run Command | Strictness |
|------|---------|--------|---|---|
| **oxlint** | Rust-based linter | `.oxlintrc.json` + `biome.json` | `oxlint -c .oxlintrc.json --type-aware` | Type-aware strict |
| typescript | Type checking | `tsconfig.json` | `tsc --noEmit` | Strict |
| **knip** | Dead code | None | `knip --include files,exports,dependencies` | Files/exports/deps |
| **madge** | Circular deps | None | `madge --circular apps/web/src/` | Circular detection |
| stylelint | CSS linting | `package.json` config | `stylelint "apps/**/*.css"` | Tailwind aware |
| prettier | Formatting | None | Pre-commit auto | YAML/JSON/MD |
| biome | Toolchain | `biome.json` | Schema validation | Ignores |
| type-coverage | TS coverage | None | Metric (not in CI) | Coverage % |
| ESLint plugins | Module/naming | `.oxlintrc.json` | Via oxlint | Boundaries/check-file/filename |

### CUSTOM SCRIPTS (5 scripts)
| Script | Purpose | Config | Run Command | Check |
|--------|---------|--------|---|---|
| check_naming_explosion.py | Naming validation | `config/naming-guard.json` | `bash scripts/shell/check-naming-explosion-python.sh` | Forbidden words/length |
| check_file_loc.py | LOC enforcement | `config/loc-guard.json` | `bash scripts/shell/check-file-loc.sh` | Max 500 LOC/file |
| extract_test_constants.py | Test framework | None | Via test automation | Constants extraction |
| add_test_noqa.py | Linter directives | None | Via test automation | Auto # noqa |
| auto_update_loc.py | LOC allowlist | `config/loc-allowlist.txt` | Via automation | Update allowlist |

### PRE-COMMIT HOOKS (11 fast checks, <5s target)
- ruff (check + format)
- trailing-whitespace, end-of-file-fixer
- check-yaml, check-added-large-files (1MB max)
- check-merge-conflict, debug-statements
- mixed-line-ending (LF)
- pycln (unused imports)
- prettier (YAML/JSON/Markdown)
- gofmt (Go formatting)

## Execution Commands

### Local Development (Fast)
```bash
make lint           # Naming + all linters (Go/Python/Frontend)
make type-check     # Type checking (mypy + tsc)
make test           # Unit tests
make quality        # Full parallel pipeline (12 steps)
```

### Comprehensive (CI/External Tools)
```bash
make quality-external           # All external tools
make quality-go-external        # govulncheck, race, mod tidy
make quality-python-external    # bandit, pip-audit, semgrep, interrogate, radon, tach, lint-imports
make quality-frontend-external  # tsc, knip, madge
```

### Reporting
```bash
make quality-report        # Parse and display results
make quality-report-watch  # Live reporting
```

## Configuration Files

**Centralized Configs:**
- `pyproject.toml` - Ruff (18 sections), pytest, mypy, ty (30+ overrides), bandit, interrogate, import-linter, coverage
- `.golangci-backend.yml` - golangci-lint (30+ linters)
- `tach.toml` - Module boundaries (7 modules, strict DAG)
- `mypy.ini` - mypy basic settings
- `pyrightconfig.json` - pyright basic mode
- `biome.json` - oxlint infrastructure (ignores)
- `frontend/.oxlintrc.json` - oxlint plugins/rules (per-app variations)
- `.pre-commit-config.yaml` - Local pre-commit hooks
- `.semgrep.yml` - semgrep project rules (empty, uses presets)
- `config/naming-guard.json` - Naming rules (cross-language)
- `config/loc-guard.json` - LOC enforcement + allowlist reference
- `config/loc-allowlist.txt` - LOC exceptions (22,609 lines)

## Tool Strictness Tiers

### Tier 1: Maximum Strictness (Phase 5)
**Bug Prevention: 75-85% | 138 total checks**
- Ruff: 43 categories including ANN (type annotations), TRY, ARG, INT, PGH, ISC, FURB, G, TCH
- golangci-lint: 30+ linters (dupl, goconst, funlen, gochecknoglobals critical)
- tach: exact=true, forbid_circular_dependencies=true
- bandit: B101 skip (tests allowed)
- interrogate: 85% threshold
- oxlint: type-aware with all plugins

### Tier 2: Strong (External)
**Catch security + architecture**
- govulncheck: CVE scanning
- pip-audit: --strict dependency CVE
- semgrep: OWASP/PCI-DSS patterns
- knip: Dead code detection
- madge: Circular dependency detection

### Tier 3: Basic (Pre-commit)
**Fast local checks (<5s)**
- ruff format + check
- gofmt
- prettier
- pycln

## Performance Notes

**Parallel Execution:**
- `make quality`: 12 steps concurrent (naming, go-lint, go-proto, go-build, go-test, py-lint, py-type, py-test, fe-lint, fe-type, fe-build, fe-test)
- Results in `.quality/logs/<step>.{log,exit}`

**Memory Optimization (Go):**
- Chunked linting by package (prevents OOM)
- Settings: GOMAXPROCS=1 GOGC=5 GOMEMLIMIT=256MiB
- Limits: --max-issues-per-linter=1 --max-same-issues=1

**Pre-commit Speed:**
- Target <5s with fast checks only
- Slow checks (ty, semgrep, interrogate, pytest) in CI

## Key Metrics

**Auto-Fixed (Phase 5):**
- 1,022 files auto-fixed
- ~23,000 violations corrected
- 3-agent swarm: ~2,700-3,500 violations/session

**Critical CVE:**
- GO-2026-4337 mitigated (go.mod → 1.25.7)

**Coverage:**
- 4 languages: Go, Python, TypeScript, CSS
- 32+ tools coordinated
- 15+ config files (single sources of truth)

## Architecture Enforcement (tach)

**Modules:**
- `tracertm.config` → `tracertm.core`
- `tracertm.models` → `tracertm.core`
- `tracertm.services` → config, models, database, core
- `tracertm.cli` → config, models, services, core, database
- `tracertm.database` → config, models, core
- `tracertm.core` → models (base)

**Rules:**
- exact=true: fail on unused deps
- forbid_circular_dependencies=true
- unused_ignore_directives=error

## Installed Tools Location

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

Frontend tools installed via bun: oxlint, knip, madge, stylelint, type-coverage

## Next Steps

1. Review Phase 5 strictness settings in `pyproject.toml` [tool.ruff]
2. Check `config/naming-guard.json` for naming policies
3. Review `tach.toml` for module boundary constraints
4. Run `make quality` for full pipeline with 12 parallel steps
5. Check `.quality/logs/` for detailed per-step results
