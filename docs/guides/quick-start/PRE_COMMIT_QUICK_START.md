# Pre-commit Quick Start Guide

## Overview

Pre-commit hooks are optimized for **speed** (<5 second target) while maintaining code quality through comprehensive CI checks.

## Installation

```bash
# Install pre-commit
pip install pre-commit

# Install hooks in your local repository
pre-commit install

# Verify installation
pre-commit --version
```

## Usage

### Automatic (Recommended)

Hooks run automatically on `git commit`:

```bash
# Make changes
git add .

# Commit (hooks run automatically, <5s)
git commit -m "feat: add new feature"
```

### Manual

Run hooks manually when needed:

```bash
# Run on all files
pre-commit run --all-files

# Run on staged files only
pre-commit run

# Run specific hook
pre-commit run ruff
pre-commit run prettier
```

## What Runs in Pre-commit (Fast Checks)

These run on every commit in **<5 seconds**:

| Hook | Purpose | Speed |
|------|---------|-------|
| **ruff** | Python linting + formatting | 0.5-1s |
| **pycln** | Remove unused imports | 0.3-0.5s |
| **prettier** | YAML/JSON/Markdown format | 0.2-0.4s |
| **basic checks** | Whitespace, EOF, merge conflicts | 0.1-0.2s |
| **gofmt** | Go code formatting | 0.2-0.3s |
| **biome** | Frontend linting + formatting | 0.5-1s |

**Total**: <5s ✅

## What Runs in CI Only (Comprehensive Checks)

These run in GitHub Actions (too slow for pre-commit):

| Check | Purpose | Speed | Why CI Only |
|-------|---------|-------|-------------|
| **mypy** | Python type checking | 10-30s | Too slow |
| **basedpyright** | Strict type checking | 15-45s | Too slow |
| **bandit** | Security scanning | 5-10s | Too slow |
| **semgrep** | Security patterns | 20-60s | Too slow |
| **interrogate** | Docstring coverage | 3-5s | Too slow |
| **tach** | Architecture boundaries | 2-4s | Too slow |
| **golangci-lint** | Go comprehensive lint | 10-30s | Too slow |
| **pytest** | Test execution | 30-120s | Too slow |

## Running Comprehensive Checks Locally

When you need to run CI-level checks locally:

```bash
# Type checking
uv run mypy src/
uv run basedpyright src/

# Security scanning
uv run bandit -r src/
semgrep --config=p/security-audit src/

# Documentation coverage
uv run interrogate -vv src/

# Architecture validation
uv run tach check

# Go comprehensive linting
cd backend && golangci-lint run

# Tests
pytest
```

## Performance Measurement

Check how fast your pre-commit hooks are:

```bash
./scripts/measure-precommit-performance.sh
```

Expected output:

```
✓ Total time: 3.2s (Target: <5s)
✓ Performance target met!
```

## Skipping Hooks

### Skip All Hooks (Not Recommended)

```bash
git commit --no-verify -m "message"
```

### Skip Specific Hook

```bash
SKIP=ruff git commit -m "message"
```

### Skip Multiple Hooks

```bash
SKIP=ruff,prettier git commit -m "message"
```

**Note**: Use sparingly! CI will catch issues anyway, but it's better to fix locally.

## Troubleshooting

### Hook Takes Too Long

1. **Measure which hook is slow**:
   ```bash
   time pre-commit run ruff --all-files
   time pre-commit run prettier --all-files
   ```

2. **Update hooks**:
   ```bash
   pre-commit autoupdate
   ```

3. **Check if slow checks were added**:
   Review `.pre-commit-config.yaml` and move slow checks to CI.

### Hook Fails

1. **See what failed**:
   ```bash
   pre-commit run --verbose --all-files
   ```

2. **Run specific hook**:
   ```bash
   pre-commit run ruff --all-files
   ```

3. **Fix the issues** or skip the hook temporarily:
   ```bash
   SKIP=ruff git commit -m "message"
   ```

### Hook Not Running

1. **Verify installation**:
   ```bash
   ls -la .git/hooks/pre-commit
   ```

2. **Reinstall if needed**:
   ```bash
   pre-commit uninstall
   pre-commit install
   ```

3. **Check hook is enabled**:
   ```bash
   grep "id: ruff" .pre-commit-config.yaml
   ```

## Best Practices

### DO ✅

- Let hooks run automatically on every commit
- Keep pre-commit fast (<5s target)
- Run comprehensive checks locally before pushing
- Update hooks regularly: `pre-commit autoupdate`
- Measure performance: `./scripts/measure-precommit-performance.sh`

### DON'T ❌

- Don't add slow checks to pre-commit (move to CI)
- Don't skip hooks regularly (fix issues instead)
- Don't disable hooks entirely
- Don't add test execution to pre-commit
- Don't add comprehensive type checking to pre-commit

## Configuration

### Pre-commit Config

Location: `.pre-commit-config.yaml`

```yaml
# Performance settings
default_stages: [pre-commit]
fail_fast: true  # Stop on first error
minimum_pre_commit_version: 2.15.0

# Hooks run in parallel automatically (v3.0+)
```

### CI Integration

All comprehensive checks run in CI:

- **Quality Checks**: `.github/workflows/quality.yml`
  - Type checking (mypy, basedpyright)
  - Security (bandit, semgrep)
  - Documentation (interrogate)
  - Architecture (tach)

- **CI/CD Pipeline**: `.github/workflows/ci.yml`
  - Go linting (golangci-lint)
  - Frontend checks (biome, TypeScript)
  - Tests (pytest, Go tests, Playwright)

## Examples

### Normal Workflow

```bash
# Make changes
vim src/module.py

# Stage changes
git add src/module.py

# Commit (hooks run automatically, <5s)
git commit -m "feat: add new module"

# Output:
# ruff.....................................................................Passed
# pycln....................................................................Passed
# prettier.................................................................Passed
# trailing-whitespace......................................................Passed
# [main abc1234] feat: add new module
```

### Before Pushing

```bash
# Run comprehensive checks locally
uv run mypy src/
uv run pytest

# Push (CI will run all checks)
git push
```

### When Hook Fails

```bash
# Commit fails with hook error
git commit -m "fix bug"
# ruff.....................................................................Failed
# - hook id: ruff
# - exit code: 1
#
# src/module.py:10:1: E501 Line too long (120 > 88 characters)

# Fix the issue
vim src/module.py

# Stage and commit again
git add src/module.py
git commit -m "fix bug"
# ruff.....................................................................Passed
# [main abc1234] fix bug
```

## Performance Optimization

### Current Performance

| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| Total time | <5s | ~3s | ✅ Met |
| Hook count | 8-12 fast hooks | 11 hooks | ✅ Good |
| Parallel execution | Enabled | Enabled | ✅ Good |
| File filtering | Enabled | Enabled | ✅ Good |

### How We Achieved <5s

1. **Moved slow checks to CI**:
   - mypy, basedpyright, bandit, semgrep → CI only
   - pytest, golangci-lint comprehensive → CI only

2. **Enabled parallel execution**:
   - Pre-commit v3.0+ runs hooks in parallel automatically
   - Independent hooks run simultaneously

3. **Optimized file filtering**:
   - `pass_filenames: true` on all hooks
   - Only staged files are checked
   - Excluded build directories and caches

4. **Enabled fail-fast**:
   - `fail_fast: true` stops on first error
   - Faster feedback for developers

## See Also

- [Pre-commit Optimization Guide](PRE_COMMIT_OPTIMIZATION.md) - Detailed optimization documentation
- [Quality Checks Workflow](../../.github/workflows/quality.yml) - CI quality checks
- [CI/CD Pipeline](../../.github/workflows/ci.yml) - Full CI/CD pipeline
- [Performance Measurement Script](../../scripts/measure-precommit-performance.sh) - Measure hook speed
