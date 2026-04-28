# File Structure Linters - Implementation Checklist

## Priority 1 Tools (Implement Immediately)

### Go - Add GCI for Import Organization

- [ ] Install GCI: `go install github.com/daixiang0/gci@latest`
- [ ] Update `backend/.golangci.yml` with GCI configuration (see `file_structure_linters_gci_config.yml`)
- [ ] Run initial check: `cd backend && golangci-lint run --disable-all --enable=gci`
- [ ] Auto-fix imports: `cd backend && golangci-lint run --fix`
- [ ] Verify imports are organized: Standard → Default → Local
- [ ] Add to CI: Ensure `.github/workflows/ci.yml` includes GCI checks

**Reference:** `docs/research/file_structure_linters_gci_config.yml`

---

### Python - Enable Ruff Import Sorting

- [ ] Review current `pyproject.toml` for existing `[tool.ruff]` section
- [ ] Add `[tool.ruff.lint.isort]` section (see `file_structure_linters_ruff_config.toml`)
- [ ] Run import sorting: `make lint-python-fix`
- [ ] Verify imports are sorted correctly
- [ ] Add to pre-commit: Already included via `ruff` hook
- [ ] Update CI if needed: Already included in `.github/workflows/quality.yml`

**Reference:** `docs/research/file_structure_linters_ruff_config.toml`

---

### Python - Add import-linter for Architecture

- [ ] Install import-linter: `uv pip install import-linter` or `pip install import-linter`
- [ ] Add to `pyproject.toml` (see `file_structure_linters_import_linter_config.toml`)
- [ ] Update contract definitions to match actual project structure
- [ ] Run initial check: `uv run import-linter` or `import-linter`
- [ ] Add to Makefile: Add `lint-imports` target
- [ ] Add to pre-commit: Create new hook in `.pre-commit-config.yaml`
- [ ] Add to CI: Add step to `.github/workflows/quality.yml`

**Reference:** `docs/research/file_structure_linters_import_linter_config.toml`

---

### TypeScript - Add eslint-plugin-boundaries

- [ ] Install plugin: `cd frontend && bun add -D eslint-plugin-boundaries`
- [ ] Update `frontend/.oxlintrc.json` with boundaries rules
- [ ] Configure element types to match project structure
- [ ] Run initial check: `cd frontend && bun run lint`
- [ ] Add to package.json scripts: Add `lint:boundaries` target
- [ ] Fix violations incrementally (may require refactoring)
- [ ] Add to CI: Update `.github/workflows/quality.yml` frontend lint step

**Reference:** `docs/research/file_structure_linters_boundaries_config.json`

---

## Priority 2 Tools (Evaluate for Specific Needs)

### monolint - For Complex Monorepo Structure

- [ ] Evaluate: Do we need custom monorepo structure validation?
- [ ] If yes: `npm install -g monolint` or `bun add -g monolint`
- [ ] Create monolint configuration file
- [ ] Add to CI: Create dedicated monorepo structure check job

---

### go-header - For License Headers

- [ ] Evaluate: Do we need to enforce license headers?
- [ ] If yes: Add to `backend/.golangci.yml` linters
- [ ] Create license header template
- [ ] Add missing headers to existing files

---

### gomodguard - For Module Restrictions

- [ ] Evaluate: Do we need to restrict/replace specific modules?
- [ ] If yes: Add to `backend/.golangci.yml` linters
- [ ] Configure allowed/banned modules in `linters-settings.gomodguard`

---

## CI/CD Integration Steps

### Update GitHub Actions

- [ ] Review `.github/workflows/ci.yml` for Go linting
- [ ] Review `.github/workflows/quality.yml` for Python/TypeScript linting
- [ ] Add GCI check to Go quality job
- [ ] Add import-linter check to Python quality job
- [ ] Add boundaries check to TypeScript quality job
- [ ] Ensure all checks run on pull requests
- [ ] Add failure notifications for contract violations

---

### Update Pre-commit Hooks

- [ ] Review `.pre-commit-config.yaml`
- [ ] Add import-linter hook for Python architecture
- [ ] Ensure GCI runs via golangci-lint hook
- [ ] Test hooks: `pre-commit run --all-files`

---

### Update Makefile

- [ ] Add `lint-imports` target for import-linter
- [ ] Add `lint-boundaries` target for frontend boundaries check
- [ ] Update `quality-python` to include import-linter
- [ ] Update `quality-frontend` to include boundaries check
- [ ] Test new targets: `make lint-imports`, `make quality-python`, etc.

---

## Verification Steps

### Go
- [ ] Create test file with disorganized imports
- [ ] Run GCI: verify imports are reorganized
- [ ] Check CI: verify GCI runs and catches violations

### Python
- [ ] Create test import violation (e.g., domain → infrastructure)
- [ ] Run import-linter: verify contract is detected
- [ ] Run ruff: verify imports are sorted
- [ ] Check CI: verify both tools run

### TypeScript
- [ ] Create test boundary violation (e.g., components → stores)
- [ ] Run boundaries linter: verify violation is detected
- [ ] Check CI: verify boundaries check runs

---

## Rollback Plan

If any tool causes issues:

1. **GCI**: Remove from `backend/.golangci.yml` and revert changes
2. **import-linter**: Remove from `pyproject.toml`, pre-commit, and CI
3. **eslint-plugin-boundaries**: Remove from `.oxlintrc.json` and package.json
4. **Ruff imports**: Comment out `[tool.ruff.lint.isort]` section

---

## Notes

- **Incremental Rollout**: Consider enabling rules as warnings first, then errors
- **Auto-fix**: Use `--fix` flags where available to ease adoption
- **Team Communication**: Document new rules in team wiki/onboarding
- **IDE Integration**: Ensure editor configurations match CI rules

---

## Quick Reference

| Tool | Install Command | Check Command | Fix Command |
|------|-----------------|---------------|-------------|
| GCI | `go install github.com/daixiang0/gci@latest` | `golangci-lint run --enable=gci` | `golangci-lint run --fix` |
| import-linter | `uv pip install import-linter` | `import-linter` | Manual (architectural) |
| boundaries | `bun add -D eslint-plugin-boundaries` | `bun run lint:boundaries` | Manual (refactoring) |
| Ruff imports | (Already installed) | `ruff check` | `ruff check --fix` |

---

*Checklist created: 2026-02-03*
