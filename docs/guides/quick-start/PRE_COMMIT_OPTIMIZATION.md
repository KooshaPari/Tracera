# Pre-commit Hook Optimization Guide

## Overview

The pre-commit hooks have been optimized for speed, targeting **<5 second execution time** to maintain fast developer workflow while ensuring code quality.

## Performance Strategy

### Fast Checks (Pre-commit) - Target: <5s

These run on every commit:

- ✅ **Ruff** - Lightning-fast Python linting and formatting
- ✅ **pycln** - Remove unused imports
- ✅ **Prettier** - YAML/JSON/Markdown formatting
- ✅ **Basic checks** - Trailing whitespace, EOF, merge conflicts, etc.
- ✅ **gofmt** - Go code formatting
- ✅ **Biome** - Frontend linting and formatting

### Comprehensive Checks (CI Only)

These run in GitHub Actions for thorough validation:

- 🔍 **MyPy** - Python type checking
- 🔍 **basedpyright** - Ultra-strict type checking
- 🔍 **Bandit** - Security vulnerability scanning
- 🔍 **Semgrep** - Advanced security pattern detection
- 🔍 **Interrogate** - Docstring coverage enforcement
- 🔍 **Tach** - Architecture boundary enforcement
- 🔍 **golangci-lint** - Comprehensive Go linting
- 🔍 **pytest** - Full test suite execution

## Key Optimizations

### 1. Parallel Execution

Pre-commit v3.0+ runs independent hooks in parallel automatically:

```yaml
# No configuration needed - automatic parallel execution
```

### 2. File Filtering

Hooks only check changed files:

```yaml
- id: ruff
  args: [--fix, --exit-non-zero-on-fix]
  pass_filenames: true  # Only check staged files
```

### 3. Fail Fast

Stop on first error for immediate feedback:

```yaml
fail_fast: true  # Stop on first error
```

### 4. Optimized Exclusions

Skip unnecessary directories:

```yaml
exclude: |
  (?x)^(
    \.venv/|
    node_modules/|
    \.next/|
    .*\.lock$|
    .*\.log$
  )
```

## Measuring Performance

Run the performance measurement script:

```bash
./scripts/measure-precommit-performance.sh
```

Expected output:

```
🔍 Measuring pre-commit hook performance...
Target: <5s total execution time

Running pre-commit on all files...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Performance Report
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✓ Total time: 3.2s (Target: <5s)
✓ Performance target met!
```

## Manual Check Execution

Run comprehensive checks locally when needed:

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

# Full test suite
pytest
```

## Skipping Hooks

Skip specific hooks when necessary:

```bash
# Skip all hooks (not recommended)
git commit --no-verify

# Skip specific hook
SKIP=ruff git commit -m "message"

# Skip multiple hooks
SKIP=ruff,prettier git commit -m "message"
```

## Troubleshooting

### Hook Takes Too Long

1. **Check what files are being processed**:
   ```bash
   pre-commit run --verbose --all-files
   ```

2. **Profile individual hooks**:
   ```bash
   time pre-commit run ruff --all-files
   time pre-commit run prettier --all-files
   ```

3. **Update hooks to latest versions**:
   ```bash
   pre-commit autoupdate
   ```

### Hook Fails on Specific Files

1. **Run hook on specific file**:
   ```bash
   pre-commit run ruff --files src/module.py
   ```

2. **Check exclusion patterns**:
   Review the `exclude` section in `.pre-commit-config.yaml`

3. **Verify file is staged**:
   ```bash
   git status
   ```

## CI Integration

All comprehensive checks run in CI workflows:

- **Quality Checks** - `.github/workflows/quality.yml`
  - Type checking (mypy, basedpyright)
  - Security scanning (bandit, semgrep)
  - Documentation coverage (interrogate)
  - Architecture validation (tach)

- **CI/CD Pipeline** - `.github/workflows/ci.yml`
  - Go linting (golangci-lint)
  - Frontend checks (biome, TypeScript)
  - Full test suites (pytest, Go tests, Playwright)

## Best Practices

### 1. Keep Pre-commit Fast

- ✅ Only add fast checks (<1s each)
- ❌ Avoid test execution in pre-commit
- ❌ Avoid comprehensive type checking in pre-commit
- ❌ Avoid security scans in pre-commit

### 2. Use CI for Comprehensive Validation

- ✅ Run full test suites in CI
- ✅ Run thorough type checking in CI
- ✅ Run security scans in CI
- ✅ Run architecture validation in CI

### 3. Optimize Hook Configuration

```yaml
# Good: Fast, focused checks
- id: ruff
  args: [--fix]
  pass_filenames: true

# Bad: Slow, comprehensive checks
- id: mypy
  args: [--strict]
  pass_filenames: false
```

### 4. Monitor Performance

Regularly measure hook performance:

```bash
# Weekly check
./scripts/measure-precommit-performance.sh

# Target: <5s total time
# Alert if >10s
```

## Configuration Reference

### Pre-commit Config

Location: `.pre-commit-config.yaml`

```yaml
# Performance settings
default_stages: [commit]
fail_fast: true
minimum_pre_commit_version: 2.15.0

# Parallel execution (automatic in v3.0+)
```

### CI Quality Workflow

Location: `.github/workflows/quality.yml`

Runs comprehensive checks on:
- Every push to main/develop
- Every pull request
- Matrix testing across Python versions

### CI/CD Workflow

Location: `.github/workflows/ci.yml`

Runs full validation including:
- Python tests with coverage
- Go tests with coverage
- Frontend E2E tests
- Security scanning
- Docker image builds

## Performance Benchmarks

| Hook | Typical Time | Status |
|------|-------------|--------|
| ruff | 0.5-1s | ✅ Fast |
| pycln | 0.3-0.5s | ✅ Fast |
| prettier | 0.2-0.4s | ✅ Fast |
| basic checks | 0.1-0.2s | ✅ Fast |
| gofmt | 0.2-0.3s | ✅ Fast |
| biome | 0.5-1s | ✅ Fast |
| **Total** | **<5s** | ✅ **Target Met** |

Checks moved to CI:

| Hook | Typical Time | Reason |
|------|-------------|--------|
| mypy | 10-30s | Too slow |
| basedpyright | 15-45s | Too slow |
| bandit | 5-10s | Too slow |
| semgrep | 20-60s | Too slow |
| interrogate | 3-5s | Too slow |
| tach | 2-4s | Too slow |
| golangci-lint | 10-30s | Too slow |
| pytest | 30-120s | Too slow |

## Migration Notes

### What Changed

1. **Removed from pre-commit**:
   - MyPy type checking → CI only
   - basedpyright type checking → CI only
   - Bandit security scanning → CI only
   - Semgrep security scanning → CI only
   - Interrogate docstring coverage → CI only
   - Tach architecture checking → CI only
   - golangci-lint comprehensive linting → CI only

2. **Kept in pre-commit**:
   - Ruff linting and formatting (fast)
   - pycln unused import removal (fast)
   - Prettier formatting (fast)
   - Basic file checks (fast)
   - gofmt (fast)
   - Biome frontend (fast)

3. **Performance improvements**:
   - Enabled `fail_fast: true`
   - Added `pass_filenames: true` where applicable
   - Optimized exclusion patterns
   - Automatic parallel execution

### Developer Impact

**Before**: 45-90s commit time (slow, frustrating)
**After**: <5s commit time (fast, seamless)

**Quality not compromised**: All checks still run in CI before merge.

## See Also

- [Pre-commit Framework Documentation](https://pre-commit.com/)
- [Quality Checks Workflow](../../.github/workflows/quality.yml)
- [CI/CD Pipeline](../../.github/workflows/ci.yml)
- [Contributing Guide](../../../README.md#contributing)
