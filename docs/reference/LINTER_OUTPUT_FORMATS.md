# Linter Output Formats - Quick Reference

This document describes the configured output formats for all linters in the project. The goal is to have all linters output results grouped by file so that issues can be easily passed to agents for fixing.

## Summary

All linters are configured to use **file-grouped output formats** for easy processing by AI agents and developers:

| Linter | Output Format | Config Location |
|--------|--------------|-----------------|
| golangci-lint | `grouped-line-number` | `backend/.golangci.yml` |
| ruff | `grouped` | Makefile, CI workflows, pre-commit |
| oxlint | `stylish` | `frontend/package.json` scripts |

---

## Go Linting (golangci-lint)

### Configuration File
**File:** `/backend/.golangci.yml`

```yaml
# Output format: grouped for file-based processing (easier for agents to fix)
# Use --out-format=json in CI for structured output; grouped-line-number for local dev
output:
  format: grouped-line-number  # Groups issues by file for easy processing
  print-issued-lines: true
  print-linter-name: true
  uniq-by-line: true
  sort-results: true
```

### Makefile Invocation
**File:** `/Makefile`

```makefile
lint-go: ## Go linters only (gofumpt check + vet + golangci-lint)
	@echo '$(GREEN)Running Go linters...$(NC)'
	@cd backend && gofumpt -w .
	@cd backend && go vet ./... && golangci-lint run --timeout=5m --out-format=grouped-line-number
	# Note: grouped-line-number format groups issues by file for easy processing by agents
	# Alternative formats: json, json-line, tab, colored-line-number, line-number, checkstyle
```

### CI Workflow
**File:** `/.github/workflows/ci.yml`

```yaml
- name: Capture Go linting baseline
  if: always()
  working-directory: backend
  run: |
    # Use grouped output for file-based processing (easier for agents to fix)
    golangci-lint run --timeout=5m --config=.golangci.yml --out-format=grouped-line-number > /tmp/go-lint-results-grouped.txt || true
    # Also output JSON for CI parsing
    golangci-lint run --timeout=5m --config=.golangci.yml --out-format=json > /tmp/go-lint-results.json || true
```

### Available Output Formats
- `grouped-line-number` - Groups issues by file with line numbers (default, recommended)
- `json` - JSON output for CI parsing
- `json-line` - JSON lines format
- `tab` - Tab-separated output
- `colored-line-number` - Colored output with line numbers
- `line-number` - Simple line number format
- `checkstyle` - Checkstyle XML format

---

## Python Linting (ruff)

### Makefile Invocation
**File:** `/Makefile`

```makefile
lint-python: ## Python linters only (ruff check + format check)
	@echo '$(GREEN)Running Python linters...$(NC)'
	$(RUFF) format src/ tests/
	$(RUFF) check src/ tests/ --output-format=grouped
	# Note: grouped format groups issues by file for easy processing by agents
	# Alternative formats: concise, json, github, gitlab, junit, azure, grouped, stylish
```

### CI Workflows
**Files:** `/.github/workflows/quality.yml`, `/.github/workflows/ci.yml`

```yaml
- name: Ruff lint (strict complexity enforcement)
  run: |
    # Use grouped output format for file-based processing (easier for agents to fix)
    uv run ruff check . --output-format=grouped > /tmp/quality-ruff-results-grouped.txt || true
    # Also output JSON for CI parsing
    uv run ruff check . --output-format=json > /tmp/quality-ruff-results.json || true
```

### Pre-commit Hook
**File:** `/.pre-commit-config.yaml`

```yaml
# Ruff - Lightning-fast linting and formatting (Python)
# Uses pyproject.toml config with complexity rules (C90, PLR)
# Note: Output format defaults to text (grouped by file for easy processing)
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.14.0
    hooks:
      - id: ruff
        args: [--fix, --exit-non-zero-on-fix, --output-format=grouped]
        # Complexity limits from pyproject.toml:
        # - McCabe max-complexity: 7
        # - max-args: 5, max-branches: 12, max-returns: 6, max-statements: 50
        # Output: grouped by file for easy processing by agents
```

### Available Output Formats
- `grouped` - Groups issues by file (default, recommended)
- `concise` - Minimal output
- `json` - JSON format for parsing
- `github` - GitHub Actions annotations
- `gitlab` - GitLab CI code quality
- `junit` - JUnit XML format
- `azure` - Azure Pipelines format
- `stylish` - Human-readable with colors

---

## Frontend Linting (oxlint)

### Package.json Scripts
**File:** `/frontend/package.json`

```json
{
  "scripts": {
    "lint": "oxfmt . && oxlint -f stylish --type-check --type-aware .",
    "lint:fix": "oxfmt . && oxlint -f stylish --type-check --type-aware --fix .",
    "typecheck": "oxfmt . && oxlint -f stylish apps/web/src --promise-plugin --react-plugin --vitest-plugin --jsx-a11y-plugin --react-perf-plugin --node-plugin --jsdoc-plugin --import-plugin --type-check --type-aware"
  }
}
```

### Makefile Invocation
**File:** `/Makefile`

```makefile
lint-frontend: ## Frontend linters only (oxlint via bun). See docs/checklists/OXC_IMPLEMENTATION_CHECKLIST.md
	@echo '$(GREEN)Running frontend linters (oxlint)...$(NC)'
	@cd frontend && bun run format
	@cd frontend && bun run lint
	# Note: oxlint uses -f stylish format (compact, file-grouped output)
	# Alternative formats: compact, json, stylish (default), github
```

### Pre-commit Hook
**File:** `/.pre-commit-config.yaml`

```yaml
  # Frontend - oxlint (fast, strict linting)
  # Uses standard .oxlintrc.json (AI-strict config moved to CI)
  - repo: local
    hooks:
      - id: oxlint-frontend
        name: oxlint (frontend - standard config)
        entry: bash -c 'cd frontend && bun run lint'
        language: system
        pass_filenames: false
        files: ^frontend/.*\.(js|ts|tsx|jsx|mjs|cjs)$
```

### Available Output Formats
- `stylish` - Compact, file-grouped output (default, recommended)
- `compact` - Minimal output
- `json` - JSON format for parsing
- `github` - GitHub Actions annotations

---

## Other Linters

### Type Checking (ty)
- **Tool:** `ty`
- **Usage:** `ty check src/ --error-on-warning`
- **Note:** Does not support output format options; output is naturally grouped by file

### Security Scanning
- **Bandit:** `--format json` for CI parsing
- **Semgrep:** JSON output available via `--json` flag
- **pip-audit:** `--format json` for structured output

---

## Design Rationale

1. **File-Grouped Output:** All linters are configured to group issues by file, making it easier for AI agents to:
   - Identify which files need fixing
   - Process issues in batches
   - Generate targeted fixes

2. **Dual Output in CI:** CI workflows output both grouped text (for human review) and JSON (for programmatic parsing)

3. **Consistent Format:** All linters use similar output format conventions:
   - `grouped` or `grouped-line-number` for human-readable, file-grouped output
   - `json` for structured parsing in CI

4. **Documentation:** Each linter invocation includes comments explaining the format choice and available alternatives

---

## Running Linters

### All Linters
```bash
make lint
```

### Individual Language Linters
```bash
make lint-go       # Go (golangci-lint)
make lint-python   # Python (ruff)
make lint-frontend # Frontend (oxlint)
```

### Quality Checks (with grouped output)
```bash
make quality       # Run all quality checks
make quality-go    # Go lint + build + test
make quality-python # Python lint + type-check + test
make quality-frontend # Frontend lint + typecheck + build + test
```

---

## References

- [golangci-lint Output Formats](https://golangci-lint.run/usage/configuration/#output-format)
- [Ruff Output Formats](https://docs.astral.sh/ruff/settings/#output_format)
- [oxlint Output Formats](https://oxc.rs/docs/guides/linter/overview)
