# Tooling Audit and Strict Setup Plan

Audit of all lint, format, type-check, test, and build tooling with configs and rulesets; plan to bring each to **full strict depth** (configs, rulesets, and other needed items). Includes research-backed modern options and "upgraded from" context.

---

## 0. Research & modern context (2024–2025)

### 0.1 Python

- **Ruff:** 800+ lint rules; 10–100× faster than Flake8/Black in practice; drop-in for Flake8 (+ plugins), Black, isort, pydocstyle, pyupgrade, autoflake. Config: `pyproject.toml` / `ruff.toml` / `.ruff.toml`; **`extend`** to inherit from another config (enables strict base + override); `select` / `ignore` / `extend-select`; **per-file-ignores** and **extend-per-file-ignores**; **`--preview`** for unstable rules and fixes. Rule categories: E/W (pycodestyle), F (Pyflakes), B (bugbear), C4, UP, N, PT, SIM, RUF, **RSE** (raise), **PERF**, **LOG**, **S** (security), PYI (stubs), AIR, ERA, FAST, etc. Respects `.gitignore` by default; **`include`** / **`extend-exclude`** for narrow discovery. Monorepo-friendly; first-party VS Code integration. [Ruff](https://docs.astral.sh/ruff/), [rules](https://docs.astral.sh/ruff/rules/).
- **uv:** Astral’s Python package/resolution runner; `uv sync`, `uv run`, `uv pip`; lockfile and workspace support. Use `uv run tach check`, `uv run ruff`, etc. in CI and scripts for consistent env. [uv](https://github.com/astral-sh/uv).
- **Tach:** Python dependency and interface enforcement (modular monolith). **`tach.toml`**: `source_roots` (required), **`exact`** (default false; fail if declared deps unused), **`forbid_circular_dependencies`** (default false), **`[rules]`** (`unused_ignore_directives`, `require_ignore_directive_reasons`, `unused_external_dependencies`), **`root_module`** (`ignore` | `allow` | `dependenciesonly` | **`forbid`** for strictest), optional **`layers`** and **`[[interfaces]]`**. **`tach.domain.toml`** for per-domain config; `tach check` / `tach check-external`; pre-commit via `tach install`. [Tach](https://github.com/tach-org/tach), [docs](https://docs.gauge.sh/usage/configuration).
- **ty (Astral):** Optional fast type checker; alternative to mypy/pyright for CI when speed matters. Not required for strict depth but useful for large codebases.

### 0.2 Frontend (JS/TS)

- **Oxlint:** 655+ rules; correctness-first defaults. **Type-aware linting** (alpha) via tsgo (TypeScript 7); **multi-file analysis** (e.g. `import/no-cycle`). 50–100× faster than ESLint in benchmarks; adoption by Preact, date-fns, PostHog, Actual, Outline. **Pedantic** rule set available (stricter). Migrate via `@oxlint/migrate` or run alongside ESLint with `eslint-plugin-oxlint`. [Oxlint](https://oxc-project.github.io/docs/guide/usage/linter.html).
- **Biome:** Linter + formatter; **rule groups**: a11y, complexity, correctness, nursery, performance, security, style, suspicious; severity per group (`on` | `off` | `warn` | `error`); **`overrides`** for per-path config; **`files.includes`** (glob, negations, **force-ignore `!!`** for scanner); **`vcs.useIgnoreFile`**; **`formatter.useEditorconfig`**. Biome 2 uses own type inference (coverage improving). [Biome](https://biomejs.dev/reference/configuration/#linter).
- **Turbo:** Vercel’s monorepo task runner; cache, dependencies, `turbo.json` tasks; `"ui": "tui"` for TUI. Use for `lint`, `typecheck`, `build`, `test` with consistent inputs/outputs.
- **Knip:** Optional; finds unused files, dependencies, and exports in TS/JS monorepos. Complements Oxlint/Biome for dead-code and dependency strictness.

### 0.3 Go

- **golangci-lint:** **Enabled by default:** errcheck, govet, ineffassign, staticcheck, unused. **Disabled by default (strict):** revive, gocritic, gocyclo, gosec, exhaustruct, wrapcheck, funlen, gocognit, bodyclose, noctx, prealloc, misspell, godot, etc. Config: `.golangci.yml`; **`linters.enable`** / **`linters.disable`**; **`linters-settings`** per linter (e.g. **gocyclo.min-complexity**, **gocritic.enabled-checks** / **disabled-checks**, **revive.rules**, **gosec.excludes**); **`issues.exclude-rules`**, **`max-issues-per-linter`**. For full strict: enable revive, gocritic, gocyclo, gosec; tune complexity thresholds and exclude only generated/tests. [golangci-lint linters](https://golangci-lint.run/usage/linters/).

### 0.4 Upgraded from (this repo)

- **Package manager:** npm → **Bun** (frontend). Use `bun install`, `bun run`, `bun add` (see CLAUDE.md).
- **Python lint/format:** flake8 / pylint → **Ruff** (lint + format). Black → **Ruff format**. isort → **Ruff I** (import sorting).
- **Frontend lint:** ESLint → **Oxlint** (primary lint); **Biome** for format and optional lint.
- **Architecture:** **Tach** added for Python module boundaries (`tach.toml`, `tach check` in pre-commit and quality-python).
- **Run commands:** Prefer **`uv run`** for Python tools in CI/scripts when using uv; **`bun run`** for frontend.
- **Security:** Standalone Bandit retained; Semgrep uses community preset `p/security-audit` plus project `.semgrep.yml`. Ruff **S** (flake8-bandit) can complement Bandit for inline security rules.

---

## 1. Audit: Inventory and Current Strictness

### 1.1 Orchestration and quality harness

| Tool / System | Config / Entry | Current strictness | Notes |
|---------------|----------------|--------------------|--------|
| **Pre-commit** | `.pre-commit-config.yaml` | Medium | Runs Ruff, mypy, basedpyright, bandit, semgrep, hooks, interrogate, pycln, prettier, gofmt, golangci-lint, biome. `fail_fast: false`. Revs pinned; Semgrep uses `p/security-audit` + `.semgrep.yml`. |
| **Turbo (TUI)** | `frontend/turbo.json` | N/A | `"ui": "tui"`; tasks for build, test, typecheck, lint. No strictness; orchestrates only. |
| **Make quality** | `Makefile`, `scripts/run-quality-parallel.sh`, `scripts/quality-report.py` | N/A | Runs quality-go, quality-python, quality-frontend in parallel; report parses logs and `.quality/last-run.json`. |
| **Process-compose quality** | `process-compose.quality.yaml`, `process-compose.quality-watch.yaml` | N/A | TUI on 18080; runs same suites. |

### 1.2 Python

| Tool | Config | Current strictness | Gaps / strict options |
|------|--------|--------------------|------------------------|
| **Tach** | `tach.toml` (root) | **Strict** | Already has `exact = true`, `forbid_circular_dependencies = true`, `[rules]` with `unused_ignore_directives = "error"`, `require_ignore_directive_reasons = "error"`; pre-commit hook present. Optional: `root_module = "forbid"` or `"dependenciesonly"` if all code in modules; `[[interfaces]]` for public API; `layers` for layering. |
| **Ruff** | `pyproject.toml` `[tool.ruff]` | Medium | **Strict:** Add RSE, PERF, LOG, S; reduce per-file-ignores; use `extend` for strict base; enable `--preview` in CI if desired. Current: E, W, F, I, B, C4, UP, N, PT, SIM, RUF; ignore E501, B008, SIM105; per-file for `__init__.py`, tests, conftest. |
| **Ruff format** | `pyproject.toml` `[tool.ruff.format]` | Standard | line-length 120, quote-style double, skip-magic-trailing-comma false. Optional: docstring-code-format. |
| **Mypy** | `pyproject.toml` `[tool.mypy]` | Strict in principle | **Strict:** Remove or narrow `ignore_errors = true` overrides (api.main, services.*, repositories.*); fix types incrementally. |
| **Basedpyright** | `pyproject.toml` `[tool.basedpyright]` | Strict | typeCheckingMode strict; many report* = error. Align pre-commit paths with mypy; avoid new overrides that weaken. |
| **Bandit** | `.bandit` | Medium | **Strict:** severity/confidence HIGH; document inline skip policy (`# nosec`). |
| **Interrogate** | `pyproject.toml` `[tool.interrogate]` + pre-commit | 80% docstring | Config in pyproject (fail-under 80, path src/). Optional: raise fail-under (e.g. 85). |
| **Pycln** | pre-commit only | Default | `--all`. No config file. |
| **Pytest** | `pyproject.toml` (addopts, etc.) | Standard | addopts: -ra, -vv, --strict-markers, --tb=short; coverage in Makefile. |
| **Semgrep** | `.semgrep.yml` + pre-commit | Preset + project | Pre-commit: `p/security-audit` + `.semgrep.yml`. Add project rules in `.semgrep.yml` as needed. |

### 1.3 Go

| Tool | Config | Current strictness | Gaps / strict options |
|------|--------|--------------------|------------------------|
| **gofmt** | N/A | Standard | `-s -l` in Makefile; `-s -w` in pre-commit. |
| **go vet** | N/A | Standard | In Makefile. |
| **golangci-lint** | `backend/.golangci.yml` | High | 18 linters enabled; max-issues-per-linter: 0; test and generated code excluded. No linters disabled for strictness; **Strict:** Enable revive, gocritic, gocyclo, gosec (and optionally funlen, exhaustruct, wrapcheck); set gocyclo.min-complexity, gocritic enabled-checks; keep max-issues-per-linter: 0; limit exclude-rules to generated/tests. Current: 18 linters; test/generated excluded. (Previously: could add more linters  |
| **Buf** | `buf.yaml` | Medium | DEFAULT lint; except FIELD_NO_DEPRECATED, SYNTAX_PROTO3; breaking FILE. **Strict:** Optional tighter breaking rules; document proto conventions. |

### 1.4 Frontend (TypeScript/React)

| Tool | Config | Current strictness | Gaps / strict options |
|------|--------|--------------------|------------------------|
| **Oxlint** | `frontend/.oxlintrc.json`, `frontend/apps/web/.oxlintrc.json` | Low–medium | **Strict:** Set **pedantic: "error"** (or "warn"); add explicit rules (no-explicit-any, no-unsafe-*); unify ignorePatterns. Current: correctness error, suspicious warn, pedantic off; react-in-jsx-scope off. |
| **Biome** | `frontend/biome.json` | Low | **Strict:** Turn on a11y, suspicious, correctness, style, security (per group or recommended); use overrides only where justified. Current: recommended true but many groups off; formatter on. |
| **TypeScript** | `frontend/tsconfig.json`, apps/packages tsconfig | Varies | **Strict:** Ensure **strict: true**, strictNullChecks, noImplicitAny in all tsconfigs; single base (e.g. tsconfig.packages.json) for inheritance. |
| **Turbo** | `frontend/turbo.json` | N/A | Task inputs/outputs defined. Align lint/typecheck tasks to strict configs. |
| **Vitest** | app-level configs | Standard | No central strict config. |
| **ESLint** | Referenced in turbo | Not present | turbo may reference `.eslintrc*`; oxlint used instead—remove stale turbo inputs or document. |

### 1.5 Other

| Tool | Config | Current strictness | Gaps |
|------|--------|--------------------|------|
| **Prettier** | `.prettierrc.json` (root) | Default | Used by pre-commit for yaml, json, markdown. Align with Biome/formatter if needed. |
| **pre-commit-hooks** | `.pre-commit-config.yaml` | Standard | trailing-whitespace, end-of-file-fixer, check-yaml, check-added-large-files, check-merge-conflict, debug-statements, mixed-line-ending. |

---

## 2. Gaps Summary (for full strict depth)

1. **Python**
   - **Tach**: Already at strict depth (exact, forbid_circular_dependencies, rules, pre-commit). Optional: `root_module = "forbid"` or `"dependenciesonly"`; `[[interfaces]]`; `layers`.
   - Ruff: add stricter rule sets (e.g. RSE, PERF, LOG); reduce per-file ignores; consider fail-fast or CI strict profile.
   - Mypy: remove or narrow `ignore_errors = true` overrides so more of codebase is strictly checked.
   - Bandit: raise to HIGH severity / HIGH confidence; add config file for inline skips policy.
   - Interrogate: add `interrogate` section in pyproject or config file; optionally raise fail-under.
   - Semgrep: add project-specific rules file and reference in pre-commit.

2. **Go**
   - golangci-lint: enable additional linters (e.g. revive, gocritic, gocyclo); consider max-issues-per-linter and exclusions review.
   - Buf: consider stricter breaking rules; document proto conventions.

3. **Frontend**
   - Oxlint: set **pedantic: "error"** (or "warn"); add explicit rule set for strict correctness/suspicious; align ignorePatterns across root and apps/web.
   - Biome: turn on and tighten rules (a11y, suspicious, correctness, style, security) incrementally; add strict preset or explicit rule list.
   - TypeScript: ensure **strict: true** and key strict options (strictNullChecks, noImplicitAny, etc.) in all tsconfigs; single source of strict options where possible.
   - Add/align ESLint if keeping (or remove from turbo inputs and rely on oxlint + biome).

4. **Orchestration**
   - Pre-commit: pin versions; consider separate “strict” env or config path for CI.
   - Turbo: add `lint` task that runs oxlint + biome (or single strict lint); ensure typecheck uses strict TS.
   - Quality report: already parses logs; optional: add exit-code awareness per suite for strict mode.

5. **Config and docs**
   - Single “strict” profile: document which commands/flags to use for “full strict” (e.g. `make quality` with all strict configs).
   - Version pins: pre-commit revs, pyproject dev deps, frontend devDependencies.
   - Root-level rulesets: consider `.editorconfig`, shared ignore files, and one-page “strict checklist” in docs.

---

## 3. Plan: Full Strict Depth (Phased)

### Phase 1: Config and ruleset files (no behavior change)

- **1.1** Add missing config files:
  - `.editorconfig` at repo root (indent, line endings, trim).
  - `frontend/.prettierrc` or root if frontend Prettier should extend (for pre-commit YAML/JSON/MD).
  - Semgrep: `.semgrep.yml` or `semgrep/rules` and reference in pre-commit.
  - Interrogate: add `[tool.interrogate]` in pyproject.toml with fail-under and paths.
- **1.2** Align ignore patterns:
  - Single or layered `.ignore` / `.lintignore` for Ruff, oxlint, biome where applicable.
  - Document in QUALITY_QUICK_REFERENCE or this doc.
- **1.3** Version pins:
  - Pre-commit: revs pinned; document in README or CONTRIBUTING.
  - pyproject.toml: keep version lower bounds; optional upper bounds for dev.
  - frontend: lockfile present; document “use bun install” and minimal node version.

**Deliverables:** All config files present; ignore patterns documented; pins documented.

**Phase 1 implementation (done):** `.editorconfig` already present; added `.prettierrc.json` (root) for pre-commit YAML/JSON/MD; added `.semgrep.yml` (project rules) and pre-commit now runs `--config=p/security-audit --config=.semgrep.yml`; added `[tool.interrogate]` in pyproject.toml (fail-under=80, paths=src/). Ignore patterns and version pins documented in `docs/reference/QUALITY_QUICK_REFERENCE.md`.

### Phase 2: Python to strict depth

- **2.1** Ruff:
  - Add RSE, PERF, LOG to select; add explicit ignore list with comments.
  - Reduce per-file-ignores to minimum (only where necessary); add `[tool.ruff.lint.extend-per-file-ignores]` if needed.
  - Option: add `ruff.toml` or profile in pyproject for “strict” with more rules.
- **2.2** Mypy:
  - Remove or narrow one override at a time (e.g. one module from ignore_errors); fix types; repeat.
  - Target: no `ignore_errors = true` for application code; keep only for third-party or generated.
- **2.3** Bandit:
  - Set severity and confidence to HIGH in `.bandit`; add inline skip policy (e.g. `# nosec` and document).
- **2.4** Basedpyright:
  - Ensure pre-commit runs it over same paths as mypy; no new overrides that weaken.
- **2.5** Interrogate:
  - Add `[tool.interrogate]` in pyproject; set fail-under (e.g. 85); exclude only generated/tests.

**Deliverables:** Ruff strict profile; mypy overrides reduced; bandit strict; interrogate config in pyproject.

### Phase 3: Go to strict depth

- **3.1** golangci-lint:
  - Enable extra linters: e.g. revive, gocritic, gocyclo, dupl, gosec (if desired).
  - Set options for revive (config) and gocritic (severity) in `.golangci.yml`.
  - Review exclude-rules; keep only for generated/tests; no broad “all” unless generated.
- **3.2** Buf:
  - Tighten breaking rules if needed; add custom lint rules if any; document in buf.yaml comments.

**Deliverables:** `.golangci.yml` with full strict linter set; buf rules documented.

### Phase 4: Frontend to strict depth

- **4.1** TypeScript:
  - Audit all `tsconfig.json` (root, apps, packages); set `strict: true`, `noImplicitAny`, `strictNullChecks`, etc.
  - Use `frontend/tsconfig.packages.json` or base to inherit strict options; apps extend and only override when necessary.
- **4.2** Oxlint:
  - Set `pedantic: "error"` (or "warn" first); add explicit rules for no-explicit-any, no-unsafe-*, etc. in root and apps/web.
  - Unify ignorePatterns; document in frontend README or this doc.
- **4.3** Biome:
  - Turn on one group at a time (e.g. correctness, then suspicious, then a11y); fix; then enable next.
  - Target: recommended + explicit strict list; only off where justified with comment.
- **4.4** Turbo:
  - Ensure `lint` and `typecheck` tasks use the strict configs; add task `lint:strict` if needed (e.g. oxlint + biome both).

**Deliverables:** All tsconfigs strict; oxlint pedantic on and rules documented; biome rule set strict and documented.

### Phase 5: Harness and CI

- **5.1** Pre-commit:
  - Add or reference “strict” Ruff/Bandit configs if different from default; document how to run “pre-commit run --all-files” as strict gate.
- **5.2** Make / scripts:
  - `make quality` already runs all suites; ensure it uses the strict configs (no extra flags needed if configs are strict by default).
  - Optional: `make quality-strict` that sets env (e.g. STRICT=1) and scripts use stricter options where implemented.
- **5.3** CI:
  - `.github/workflows/ci.yml`: ensure Go job uses same `.golangci.yml`; add Python job that runs ruff + mypy + bandit with strict configs; add frontend job that runs typecheck + lint (oxlint + biome) with strict configs.
- **5.4** Docs:
  - Update QUALITY_QUICK_REFERENCE and this doc with “Strict mode” section: list commands and expected zero errors.
  - Add `docs/checklists/STRICT_LINT_CHECKLIST.md`: one-pager with tool, config path, and “strict” expectation.

**Deliverables:** Pre-commit and CI run strict configs; docs updated; optional make quality-strict.

---

## 4. Checklist: Items Needed for Full Strict Depth

- [x] **.editorconfig** (root)
- [x] **Prettier** config (root or frontend) for pre-commit
- [x] **Semgrep** custom rules and pre-commit path
- [x] **Interrogate** `[tool.interrogate]` in pyproject.toml
- [ ] **Ruff** strict profile (more rules; fewer ignores)
- [ ] **Mypy** overrides reduced (no ignore_errors for app code)
- [ ] **Bandit** severity/confidence HIGH; inline skip policy
- [ ] **golangci-lint** extra linters (revive, gocritic, etc.)
- [ ] **Buf** breaking/lint rules documented and tightened if needed
- [ ] **TypeScript** strict in all tsconfigs
- [ ] **Oxlint** pedantic on; strict rule set
- [ ] **Biome** strict rule set (all groups on or explicitly set)
- [ ] **Turbo** lint/typecheck aligned to strict configs
- [ ] **Pre-commit** pins and optional strict hook set
- [ ] **CI** jobs for Python and frontend strict lint/typecheck
- [ ] **STRICT_LINT_CHECKLIST.md** and QUALITY_QUICK_REFERENCE update
- [x] **Tach** exact + forbid_circular_dependencies + rules; pre-commit hook; full module coverage (optional: root_module forbid, interfaces, layers)

---

## 5. Reference: Config File Locations

| Tool | Primary config | Secondary / overrides |
|------|----------------|------------------------|
| Pre-commit | `.pre-commit-config.yaml` | — |
| Tach | `tach.toml` (root) | [docs](https://docs.gauge.sh), [GitHub](https://github.com/tach-org/tach) |
| Ruff | `pyproject.toml` [tool.ruff] | — |
| Mypy | `pyproject.toml` [tool.mypy] | — |
| Basedpyright | `pyproject.toml` [tool.basedpyright] | — |
| Bandit | `.bandit` | — |
| Interrogate | `pyproject.toml` [tool.interrogate] | pre-commit args |
| Semgrep | pre-commit: `p/security-audit` + `.semgrep.yml` | — |
| golangci-lint | `backend/.golangci.yml` | — |
| Buf | `buf.yaml` | — |
| Oxlint | `frontend/.oxlintrc.json`, `frontend/apps/web/.oxlintrc.json` | — |
| Biome | `frontend/biome.json` | — |
| TypeScript | `frontend/tsconfig.json`, apps/packages tsconfig.json | — |
| Turbo | `frontend/turbo.json` | — |

---

*Document generated for audit + plan first; implementation to follow in phases.*
