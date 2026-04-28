# File Structure Linters - Research and Recommendations

## Executive Summary

This document researches and recommends file structure linting tools for a multi-language monorepo containing Go backend, TypeScript/Node frontend, and Python services.

**Current State:**
- **Go**: `gofumpt` (strict formatter) + `golangci-lint` with extensive linters
- **TypeScript**: `oxlint` with strict rules including `unicorn/filename-case`
- **Python**: `ruff` with format and lint rules
- **Monorepo**: Custom scripts for naming explosion and LOC guards

**Key Gaps:**
- Go import organization (no GCI configured)
- Python import organization (no isort configured)
- TypeScript architecture boundary enforcement (no import boundaries plugin)
- Monorepo-wide structure validation

---

## 1. Go File Structure Tools

### 1.1 gofumpt (Already Configured) ✓

**Status:** Already in use via `.golangci.yml`

**Description:** A stricter Go formatter that extends `gofmt` with additional rules.

**Features:**
- Requires Go 1.24+
- Drop-in replacement for `gofmt`
- Enforces additional formatting rules
- Integrated into golangci-lint formatters

**Current Configuration:**
```yaml
# backend/.golangci.yml
formatters:
  enable:
    - gofmt
    - gofumpt
```

**Documentation:** [mvdan/gofumpt](https://github.com/mvdan/gofumpt)

---

### 1.2 GCI (Go Control Imports) ⭐ Recommended

**Status:** NOT configured - **HIGH PRIORITY ADDITION**

**Description:** Controls Go package import order and makes it deterministic. Provides more control than `goimports`.

**Features:**
- Deterministic import ordering
- Highly customizable output formats
- AST-based analysis
- Custom grouping of imports (standard, local, third-party)
- Can skip generated files

**Why Add GCI:**
- The project already uses `goimports` (via golangci-lint), but GCI provides better customization
- GCI allows defining custom import groups matching project structure
- Helps maintain consistency across team members' IDEs

**Installation:**
```bash
go install github.com/daixiang0/gci@latest
```

**Configuration for golangci-lint:**
```yaml
# backend/.golangci.yml (add to formatters section)
formatters:
  enable:
    - gofmt
    - gofumpt
    - gci  # ADD THIS

linters-settings:
  gci:
    sections:
      - Standard   # Standard library
      - Default    # All imports not matching other sections
      - Prefix(github.com/yourorg/yourproject)  # Local imports
    skip-generated: true
```

**Documentation:** [daixiang0/gci](https://github.com/daixiang0/gci)

---

### 1.3 Other Go Structure Tools

| Tool | Description | Recommendation |
|------|-------------|----------------|
| **goimports** | Already used via golangci-lint; adds missing imports, removes unused | Keep - works well |
| **gomodguard** | Enforces Go module restrictions (replace/banned) | Optional for strict module control |
| **go-header** | Enforces license headers | Optional for corporate projects |

---

## 2. TypeScript/JavaScript Structure Tools

### 2.1 oxlint (Already Configured) ✓

**Status:** Already in use with `.oxlintrc.json`

**Description:** Fast Rust-based linter with TypeScript support.

**Current File Structure Rules:**
```json
{
  "unicorn/filename-case": [
    "error",
    {
      "cases": {
        "camelCase": true,
        "pascalCase": true,
        "kebabCase": true
      }
    }
  ]
}
```

**Gap:** Only enforces filename casing, not directory structure or architecture boundaries.

---

### 2.2 eslint-plugin-import (Already Partially Configured) ✓

**Status:** Import ordering rules configured in `.oxlintrc.json`

**Current Configuration:**
```json
{
  "import/order": ["error", {...}],
  "import/no-cycle": ["error", {...}],
  "import/no-self-import": "error",
  "import/no-duplicates": "error",
  "import/first": "error"
}
```

---

### 2.3 eslint-plugin-boundaries ⭐ Recommended for Architecture

**Status:** NOT configured - **HIGH PRIORITY FOR MONOREPO**

**Description:** Enforces architectural boundaries between different parts of an application using import path patterns.

**Features:**
- Define allowed/disallowed import paths between layers
- Enforce clean architecture principles
- TypeScript support
- Prevent circular dependencies
- Custom boundary definitions via glob patterns

**Use Cases for This Project:**
- Prevent `components/` from importing directly from `__tests__/`
- Enforce separation between `api/`, `stores/`, `views/`
- Validate cross-app imports in monorepo

**Installation:**
```bash
bun add -D eslint-plugin-boundaries
```

**Configuration Example:**
```json
{
  "plugins": ["boundaries"],
  "rules": {
    "boundaries/entry-point": ["error", {
      "disallow": ["*"],
      "allow": ["apps/web/src/index.tsx"]
    }],
    "boundaries/no-external-import": ["error", {
      "allow": ["react", "react-dom", "@tanstack/react-router"]
    }],
    "boundaries/no-private-import": ["error", {
      "allow": ["src/*"],
      "restrict": "**/internal/**"
    }]
  },
  "settings": {
    "boundaries/include": ["**/*.{js,jsx,ts,tsx}"],
    "boundaries/elements": [
      {
        "type": "components",
        "pattern": "components/**/*",
        "mode": "file"
      },
      {
        "type": "api",
        "pattern": "api/**/*",
        "mode": "file"
      },
      {
        "type": "views",
        "pattern": "views/**/*",
        "mode": "file"
      }
    ]
  }
}
```

**Documentation:** [@boundaries/eslint-plugin](https://www.npmjs.com/package/@boundaries/eslint-plugin)

---

### 2.4 eslint-plugin-check-file (Alternative for Naming)

**Description:** Enforces filename and folder naming conventions.

**Comparison with oxlint:**
- **oxlint** (current): `unicorn/filename-case` - simpler, built-in
- **eslint-plugin-check-file**: More granular control, supports directory-specific rules

**Recommendation:** Keep current oxlint configuration unless more granular control is needed.

**Documentation:** [dukeluo/eslint-plugin-check-file](https://github.com/DukeLuo/eslint-plugin-check-file)

---

## 3. Python File Structure Tools

### 3.1 ruff (Already Configured) ✓

**Status:** Primary Python linter with format and lint rules

**Current Configuration:**
- Fast format checking
- Complexity rules (C90, PLR)
- McCabe max-complexity: 7
- max-args: 5, max-branches: 12, max-returns: 6, max-statements: 50

**Gap:** No explicit import sorting configuration visible.

---

### 3.2 isort ⭐ Recommended for Import Organization

**Status:** NOT explicitly configured - **MEDIUM PRIORITY**

**Description:** Python utility for sorting imports alphabetically and separating them into sections (standard library, third-party, local).

**Why Add isort:**
- Complements ruff (ruff can run isort-compatible rules)
- Explicit import section separation
- Configurable via `pyproject.toml`
- Integrates with VSCode and other editors

**Installation:**
```bash
uv pip install isort
# or
pip install isort
```

**Configuration (pyproject.toml):**
```toml
[tool.isort]
profile = "black"
line_length = 100
multi_line_output = 3
include_trailing_comma = true
force_grid_wrap = 0
use_parentheses = true
ensure_newline_before_comments = true
sections = ["FUTURE", "STDLIB", "THIRDPARTY", "FIRSTPARTY", "LOCALFOLDER"]
known_first_party = ["tracertm"]
```

**Note:** Ruff's import sorting is isort-compatible. Consider using ruff's import sorting instead:
```toml
[tool.ruff]
line-length = 100

[tool.ruff.lint.isort]
known-first-party = ["tracertm"]
section-order = ["future", "standard-library", "third-party", "first-party", "local-folder"]
```

**Documentation:** [isort Documentation](https://pycqa.github.io/isort/)

---

### 3.3 import-linter ⭐ Recommended for Architecture

**Status:** NOT configured - **HIGH PRIORITY FOR PYTHON ARCHITECTURE**

**Description:** Command-line tool for imposing constraints on imports between Python modules. Enforces architectural rules by analyzing the dependency graph.

**Features:**
- Define and enforce layer boundaries (e.g., views, models, services)
- Prevent circular dependencies
- Ensure proper separation of concerns
- Integrates with CI/CD pipelines
- Supports multiple root packages configuration

**Use Cases for This Project:**
- Prevent `internal/services/` from importing from `internal/api/`
- Enforce unidirectional dependencies (e.g., API → Services → Models)
- Validate that test files don't import from production code in wrong direction

**Installation:**
```bash
uv pip install import-linter
# or
pip install import-linter
```

**Configuration Example:**
```toml
# pyproject.toml
[tool.importlinter]
root_packages = ["tracertm"]

[[tool.importlinter.contracts]]
name = "Domain Layer Independence"
type = "forbidden"
source_modules = ["tracertm.domain"]
forbidden_modules = ["tracertm.infrastructure", "tracertm.api"]

[[tool.importlinter.contracts]]
name = "API to Services Only"
type = "layers"
layers = ["tracertm.api", "tracertm.services", "tracertm.domain", "tracertm.models"]
```

**Documentation:**
- [GitHub: seddonym/import-linter](https://github.com/seddonym/import-linter)
- [import-linter.readthedocs.io](https://import-linter.readthedocs.io/)

---

### 3.4 tach (Already Mentioned in Makefile) ✓

**Status:** Referenced in `Makefile` via `tach-check` target

**Description:** Python module boundaries enforcement tool (similar to import-linter).

**Current Status:**
```makefile
tach-check: ## Python module boundaries (tach); requires tach.toml and tach installed
	@command -v tach >/dev/null 2>&1 || (echo 'tach not found' >&2; exit 1)
	tach check
```

**Note:** Verify if `tach.toml` exists and is configured. If not, consider choosing between import-linter and tach (similar functionality).

---

## 4. Monorepo Structure Validation Tools

### 4.1 monolint ⭐ Recommended for Directory Structure

**Status:** NOT configured - **MEDIUM PRIORITY**

**Description:** A linter specifically for monorepos that checks folder structure, module contents, file contents, and naming conventions.

**Features:**
- Identifies modules inside your repo
- Validates modules according to your rules
- Checks folder structure
- Validates file contents
- Naming convention enforcement

**Installation:**
```bash
npm install -g monolint
# or
bun add -g monolint
```

**Documentation:** [flaviostutz/monolint](https://github.com/flaviostutz/monolint)

---

### 4.2 Monorepolint

**Description:** Maintains homogeneity and predictability within monorepos.

**Features:**
- Comprehensive monorepo-wide rule enforcement
- Enforces consistent structure and conventions
- Dependency management

**Comparison with monolint:** More comprehensive but heavier. monolint is more focused on structure validation.

**Documentation:** [monorepolint.com](https://monorepolint.com/docs/)

---

### 4.3 file-structure-validator

**Description:** Simple npm package for validating directory structure.

**Features:**
- Validate base directory existence
- Check specified files/directories exist
- Simple, focused validation

**Use Case:** Basic structural checks (e.g., required config files present).

**Documentation:** [npmjs.com/package/file-structure-validator](https://www.npmjs.com/package/file-structure-validator)

---

### 4.4 Nx (Existing Tools May Suffice)

**Note:** The project uses Turborepo (mentioned in search results). Nx and Turborepo provide some built-in structure validation.

**Recommendation:** Leverage existing Turborepo configuration before adding new tools.

---

## 5. Recommendations Summary

### Priority 1: Implement Immediately

| Language | Tool | Purpose | Integration |
|----------|------|---------|-------------|
| **Go** | GCI | Import organization control | Add to `.golangci.yml` formatters |
| **Python** | Ruff import sorting | Use built-in isort-compatible rules | Add to `pyproject.toml` |
| **TypeScript** | eslint-plugin-boundaries | Architecture boundary enforcement | Add to oxlint config |
| **Python** | import-linter | Module dependency constraints | Add to pre-commit + CI |

### Priority 2: Evaluate for Specific Needs

| Tool | Use Case | When to Add |
|------|----------|-------------|
| **monolint** | Complex monorepo structure rules | If custom validation needed |
| **go-header** | License header enforcement | Corporate/compliance requirements |
| **gomodguard** | Module replacement/banning | Strict dependency control |

### Priority 3: Consider for Future

| Tool | Use Case |
|------|----------|
| **isort** | If ruff's import sorting insufficient |
| **Monorepolint** | If comprehensive monorepo rules needed |

---

## 6. Implementation Guide

### 6.1 Go - Add GCI

**Step 1: Install GCI**
```bash
go install github.com/daixiang0/gci@latest
```

**Step 2: Update `.golangci.yml`**
```yaml
formatters:
  enable:
    - gofmt
    - gofumpt
    - gci  # ADD

linters-settings:
  gci:
    sections:
      - Standard
      - Default
      - Prefix(github.com/kooshapari/trace)  # Update with actual org
    skip-generated: true
```

**Step 3: Run and Fix**
```bash
cd backend
golangci-lint run --fix
```

---

### 6.2 Python - Enable Ruff Import Sorting

**Step 1: Update `pyproject.toml`**
```toml
[tool.ruff.lint.isort]
known-first-party = ["tracertm"]
section-order = ["future", "standard-library", "third-party", "first-party", "local-folder"]
```

**Step 2: Apply**
```bash
make lint-python-fix
```

---

### 6.3 Python - Add import-linter

**Step 1: Install**
```bash
uv pip install import-linter
```

**Step 2: Add to `pyproject.toml`**
```toml
[tool.importlinter]
root_packages = ["tracertm"]

[[tool.importlinter.contracts]]
name = "Domain Layer Independence"
type = "forbidden"
source_modules = ["tracertm.domain"]
forbidden_modules = ["tracertm.infrastructure", "tracertm.api"]
```

**Step 3: Add to Makefile**
```makefile
lint-imports: ## Check Python import architecture
	uv run import-linter
```

**Step 4: Add to pre-commit**
```yaml
# .pre-commit-config.yaml
- repo: local
  hooks:
    - id: import-linter
      name: import-linter (Python architecture)
      entry: uv run import-linter
      language: system
      pass_filenames: false
```

---

### 6.4 TypeScript - Add eslint-plugin-boundaries

**Step 1: Install**
```bash
cd frontend
bun add -D eslint-plugin-boundaries
```

**Step 2: Update `.oxlintrc.json`**
```json
{
  "plugins": ["boundaries"],
  "rules": {
    "boundaries/entry-point": ["error", {
      "disallow": ["*"],
      "allow": ["apps/web/src/index.tsx"]
    }]
  },
  "settings": {
    "boundaries/elements": [
      {
        "type": "components",
        "pattern": "components/**/*",
        "mode": "file"
      },
      {
        "type": "api",
        "pattern": "api/**/*",
        "mode": "file"
      }
    ]
  }
}
```

**Step 3: Add to package.json scripts**
```json
{
  "scripts": {
    "lint:boundaries": "oxlint --rule boundaries/*"
  }
}
```

---

### 6.5 CI/CD Integration

**Update `.github/workflows/quality.yml`:**
```yaml
name: Quality

on: [push, pull_request]

jobs:
  structure:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Check Go imports (GCI)
        run: |
          cd backend && golangci-lint run --disable-all --enable=gci

      - name: Check Python imports (import-linter)
        run: |
          uv run import-linter

      - name: Check TS boundaries
        run: |
          cd frontend && bun run lint:boundaries
```

---

## 7. Sources

- [mvdan/gofumpt - A stricter gofmt](https://github.com/mvdan/gofumpt)
- [daixiang0/gci - Go Control Imports](https://github.com/daixiang0/gci)
- [golangci/golangci-lint - Fast linters runner for Go](https://github.com/golangci/golangci-lint)
- [GolangCI-Lint Documentation - Settings](https://golangci-lint.run/docs/formatters/configuration/)
- [isort - Python Import Sorter Documentation](https://pycqa.github.io/isort/)
- [isort Configuration Options](https://pycqa.github.io/isort/docs/configuration/options.html)
- [import-linter - Python Architecture Enforcement](https://github.com/seddonym/import-linter)
- [import-linter Documentation](https://import-linter.readthedocs.io/)
- [eslint-plugin-check-file - Filename Naming](https://github.com/DukeLuo/eslint-plugin-check-file)
- [@boundaries/eslint-plugin](https://www.npmjs.com/package/@boundaries/eslint-plugin)
- [Monorepolint Documentation](https://monorepolint.com/docs/)
- [flaviostutz/monolint - Monorepo Linter](https://github.com/flaviostutz/monolint)
- [file-structure-validator - npm](https://www.npmjs.com/package/file-structure-validator)

---

## Appendix: Current Linter Inventory

### Go (backend/.golangci.yml)
- Formatters: `gofmt`, `gofumpt`
- Linters: errcheck, govet, ineffassign, staticcheck, unused, revive, gocritic, gosec, bodyclose, rowserrcheck, gocyclo, gocognit, misspell, unconvert, exhaustive, prealloc, whitespace, nakedret, noctx, dupl, goconst, funlen, mnd, nolintlint, gochecknoglobals, perfsprint

### TypeScript (frontend/.oxlintrc.json)
- Plugins: eslint, typescript, unicorn, oxc, react, react-perf, import, jsx-a11y, promise, vitest, react-hooks
- File naming: `unicorn/filename-case`
- Import rules: order, no-cycle, no-self-import, no-duplicates, first, newline-after-import

### Python (.pre-commit-config.yaml)
- Ruff with complexity rules (C90, PLR)
- McCabe max-complexity: 7
- max-args: 5, max-branches: 12, max-returns: 6, max-statements: 50

### Custom Guards
- `check-naming-explosion-python.sh`
- `check-naming-explosion-go.sh`
- `check-naming-explosion.sh` (frontend)
- `check-file-loc.sh`

---

*Document created: 2026-02-03*
