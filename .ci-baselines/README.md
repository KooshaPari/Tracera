# CI Linting Baselines

This directory contains baseline violation counts for linting enforcement in CI/CD pipelines.

## Purpose

The baseline file (`lint-baseline.json`) tracks the number of linting violations across all codebases to prevent regression while allowing incremental improvement.

## Enforcement Policy

- **Threshold**: Maximum allowed violations = baseline + 10%
- **Failure**: CI fails if current violations exceed threshold
- **Improvement**: Always allowed (violations below baseline)
- **Update**: Baselines auto-update on `main` branch when violations decrease

## Baseline Structure

```json
{
  "python_ruff": 0,           // Ruff linting violations (complexity, style, security)
  "python_mypy": 0,           // Mypy type checking errors
  "python_bandit": 0,         // Bandit security issues
  "go_lint": 0,               // golangci-lint violations (7 new linters)
  "frontend_oxlint": 0,       // Oxlint violations (AI-strict config)
  "last_updated": "...",      // ISO 8601 timestamp
  "phase": "...",             // Current enforcement phase
  "description": "..."        // Human-readable description
}
```

## Tracked Linters

### Python (`pyproject.toml`)
- **Ruff**: McCabe complexity ≤7, max-args=5, max-branches=12, max-statements=50
- **Mypy**: Strict type checking with disallow_untyped_defs
- **Bandit**: Security scanning (high severity)

### Go (`backend/.golangci.yml`)
- **golangci-lint**: 7 new linters enabled
  - `bodyclose`: HTTP response body closure
  - `rowerrcheck`: SQL row error checking
  - `gocyclo`: Cyclomatic complexity ≤15
  - `gocognit`: Cognitive complexity ≤20
  - `prealloc`: Preallocate slices
  - `exportloopref`: Loop variable capture
  - `noctx`: HTTP request context

### Frontend (`frontend/.oxlintrc.json`)
- **Oxlint**: AI-strict configuration
  - Type safety: no-explicit-any, explicit-function-return-type
  - Complexity: max-lines-per-function=50, max-params=3, complexity=10
  - React: jsx-max-depth=4, performance rules
  - Imports: no-cycle, no-self-import

## Manual Updates

To manually update baselines (requires team approval):

```bash
# Edit the baseline file
vi .ci-baselines/lint-baseline.json

# Commit and push
git add .ci-baselines/lint-baseline.json
git commit -m "ci: update linting baselines after code quality improvements"
git push
```

## Related Files

- `.github/workflows/ci.yml` - Main CI pipeline with baseline enforcement
- `.github/workflows/quality.yml` - Extended quality checks
- `pyproject.toml` - Python linting configuration
- `backend/.golangci.yml` - Go linting configuration
- `frontend/.oxlintrc.json` - Frontend linting configuration
