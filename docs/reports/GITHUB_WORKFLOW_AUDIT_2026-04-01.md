# GitHub Actions Workflow Audit Report

**Date:** 2026-04-01
**Auditor:** Reed (polecat agent)
**Scope:** All 36 workflow files in `.github/workflows/`

## Executive Summary

Audited all 36 GitHub Actions workflow files. Found and fixed **73 issues** across 3 categories:
- **20 duplicate YAML `with:` keys** (syntax errors) in 13 files
- **50+ deprecated action version references** across 15 files
- **21 workflows missing `permissions:` blocks** (security concern)
- **2 unpinned `@master` action references** (security/stability risk)

All issues have been remediated.

---

## Issues Found & Fixed

### 1. Duplicate YAML `with:` Mapping Keys (20 instances, 13 files)

YAML duplicate keys are silently overwritten by the last occurrence. In these workflows, a step had two `with:` blocks, causing the first to be discarded.

| File | Line(s) | Description |
|------|---------|-------------|
| `quality.yml` | 26-28 | `setup-python@v5` - `cache` and `python-version` in separate `with:` blocks |
| `release.yml` | 25-27 | `setup-python@v5` - `cache` and `python-version` in separate `with:` blocks |
| `test.yml` | 83-85 | `setup-node@v4` - `cache`, `node-version`, `cache-dependency-path` split |
| `dependabot-auto-merge.yml` | 50-52, 59-61 | `setup-node@v4` and `setup-python@v5` - duplicate `with:` blocks |
| `architecture.yml` | 22-24 | `setup-python@v5` - duplicate `with:` blocks |
| `chaos-tests.yml` | 84-86 | `setup-python@v5` - duplicate `with:` blocks |
| `chromatic.yml` | 41-43 | `setup-node@v4` - duplicate `with:` blocks |
| `contracts.yml` | 36-38 | `setup-python@v5` - duplicate `with:` blocks |
| `performance-regression.yml` | 121-123, 249-251, 352-354 | `setup-python@v5` - 3 instances |
| `pre-commit.yml` | 17-19 | `setup-python@v5` - duplicate `with:` blocks |
| `test-pyramid.yml` | 30-32, 37-39 | `setup-python@v5` and `setup-go@v5` - 2 instances |
| `test-validation.yml` | 17-19, 41-43, 82-84 | `setup-go@v5`, `setup-bun@v2`, `setup-python@v5` - 3 instances |
| `tests.yml` | 59-61, 182-184 | `setup-python@v5` - 2 instances |

**Fix:** Merged each pair of `with:` blocks into a single block with all properties. Also removed resulting duplicate `cache:` keys in `test.yml`, `dependabot-auto-merge.yml`, and `chromatic.yml`.

### 2. Deprecated Action Versions (50+ references, 15 files)

| Old Version | New Version | Files Affected |
|-------------|-------------|----------------|
| `actions/checkout@v3` | `@v4` | `ci-cd.yml`, `naming-guard.yml` |
| `actions/setup-python@v4` | `@v5` | `ci-cd.yml`, `test.yml`, `test-validation.yml` |
| `actions/setup-go@v4` | `@v5` | `test.yml`, `test-validation.yml` |
| `actions/cache@v3` | `@v4` | `ci.yml` (10x), `go-tests.yml` (4x), `quality.yml`, `contracts.yml`, `chromatic.yml`, `tests.yml` (2x) |
| `codecov/codecov-action@v3` | `@v4` | `ci-cd.yml`, `test.yml` (3x), `tests.yml` (2x) |
| `docker/setup-buildx-action@v2` | `@v3` | `ci-cd.yml` |
| `docker/build-push-action@v4` | `@v5` | `ci-cd.yml` |
| `oven-sh/setup-bun@v1` | `@v2` | `chromatic.yml`, `contract-tests.yml`, `docs-deploy.yml` (3x), `test-validation.yml` (2x) |
| `softprops/action-gh-release@v1` | `@v2` | `release.yml` |
| `8398a7/action-slack@v3` | `@v4` | `chaos-tests.yml` |

### 3. Unpinned / Renamed Actions (2 references)

| Action | Issue | Fix |
|--------|-------|-----|
| `aquasecurity/trivy-action@master` | Unpinned to `@master` - mutable, security risk | Pinned to `@0.28.0` in `ci.yml`, `security-scans.yml` |
| `returntocorp/semgrep-action@v1` | Deprecated org name | Updated to `semgrep/semgrep-action@v1` in `ci.yml` |

### 4. Missing `permissions:` Blocks (21 files)

Added `permissions: contents: read` at workflow level to all workflows lacking permission declarations. This enforces least-privilege access and follows GitHub's recommended security practices.

**Files updated:** `architecture.yml`, `canary-deploy.yml`, `chaos-tests.yml`, `chromatic.yml`, `ci-cd.yml`, `ci.yml`, `contract-tests.yml`, `contracts.yml`, `docs-deploy.yml`, `docs-performance.yml`, `go-tests.yml`, `naming-guard.yml`, `openapi-docs.yml`, `performance-regression.yml`, `pre-commit.yml`, `quality.yml`, `schema-validation.yml`, `secret-scanning.yml`, `test-validation.yml`, `test.yml`, `tests.yml`

---

## Key Workflows Verified

### ci.yml (1522 lines)
- Fixed 10 `actions/cache@v3` -> `@v4`
- Fixed `aquasecurity/trivy-action@master` -> `@0.28.0`
- Fixed `returntocorp/semgrep-action@v1` -> `semgrep/semgrep-action@v1`
- Added workflow-level `permissions: contents: read`
- Docker build job retains job-level `permissions: contents: read, packages: write`

### ci-cd.yml (107 lines)
- Fixed all `@v3` checkout, `@v4` setup-python, `@v3` codecov references
- Fixed `docker/setup-buildx-action@v2` -> `@v3`
- Fixed `docker/build-push-action@v4` -> `@v5`
- Added `permissions: contents: read`

### quality.yml (121 lines)
- Fixed duplicate `with:` blocks on `setup-python@v5`
- Fixed `actions/cache@v3` -> `@v4`
- Added `permissions: contents: read`

### go-tests.yml (556 lines)
- Fixed 4 `actions/cache@v3` -> `@v4`
- Added `permissions: contents: read`

### test.yml (131 lines)
- Fixed `setup-go@v4` -> `@v5`, `setup-python@v4` -> `@v5`
- Fixed 3 `codecov/codecov-action@v3` -> `@v4`
- Fixed duplicate `with:` blocks on `setup-node@v4` + removed duplicate `cache:` key
- Added `permissions: contents: read`

### contract-tests.yml (207 lines)
- Fixed `oven-sh/setup-bun@v1` -> `@v2`
- Added `permissions: contents: read`

### security-scans.yml (117 lines)
- Fixed `aquasecurity/trivy-action@master` -> `@0.28.0`
- Added `permissions: contents: read`

### release.yml (58 lines)
- Fixed duplicate `with:` blocks on `setup-python@v5`
- Fixed `softprops/action-gh-release@v1` -> `@v2`

### dependabot-auto-merge.yml (157 lines)
- Fixed 2 duplicate `with:` blocks (`setup-node@v4`, `setup-python@v5`)
- Removed resulting duplicate `cache:` keys

---

## Remaining Observations (Not Fixed - Advisory)

1. **ci-cd.yml is largely redundant with ci.yml** - Both define CI/CD pipelines with similar structure but ci.yml is the comprehensive one. Consider removing ci-cd.yml.

2. **test.yml is largely redundant with go-tests.yml** - go-tests.yml has a much more comprehensive Go test setup. Consider removing test.yml or consolidating.

3. **Python version matrix inconsistency** - Some workflows use Python 3.9/3.10/3.11 (test.yml), others use 3.11/3.12 (quality.yml), others only 3.12 (ci.yml). Consider standardizing.

4. **Go version inconsistency** - Workflows reference Go 1.21, 1.22, 1.23, and 1.24. Standardize on 1.23 across all workflows.

5. **No `concurrency:` on most workflows** - Only `chromatic.yml` uses concurrency groups. Consider adding to other PR-triggered workflows to cancel stale runs.

---

## Verification

Post-fix verification confirmed:
- **0** deprecated action references remaining
- **0** duplicate `with:` blocks remaining
- **0** files missing permissions declarations
- **All 36 workflow files** pass structural YAML validation
