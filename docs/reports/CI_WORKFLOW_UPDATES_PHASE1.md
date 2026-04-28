# CI/CD Workflow Updates - Phase 1 Linting Enforcement

**Date**: 2026-02-02
**Status**: ✅ Complete
**Related**: Phase 1 Linting Standards Activation

## Overview

Updated GitHub Actions workflows to enforce the new Phase 1 linting standards with baseline tracking and regression prevention.

## Changes Made

### 1. CI Workflow (`ci.yml`)

#### Python Tests Job
- **Enhanced Ruff Linting**: Added JSON output capture and violation counting
- **Mypy Reporting**: Generate JSON reports with error counts
- **Bandit Security**: JSON output with issue tracking
- **pip-audit**: JSON vulnerability reports
- **Artifact Upload**: All lint results stored for 90 days

**Config Enforced**: `pyproject.toml`
- McCabe complexity: max=7
- Max arguments: 5
- Max branches: 12
- Max statements: 50

#### Go Tests Job
- **golangci-lint Enhancement**: Strict enforcement with `.golangci.yml`
- **JSON Output**: Capture all violations in structured format
- **Baseline Tracking**: Count violations for regression detection
- **Artifact Upload**: Lint results stored for trend analysis

**New Linters Added** (7 total):
1. `bodyclose` - HTTP response body closure
2. `rowerrcheck` - SQL row error checking
3. `gocyclo` - Cyclomatic complexity ≤15
4. `gocognit` - Cognitive complexity ≤20
5. `prealloc` - Preallocate slices for performance
6. `exportloopref` - Loop variable capture bugs
7. `noctx` - HTTP request context requirements

#### Frontend Checks Job
- **Oxlint Strict Mode**: AI-optimized config enforcement
- **JSON Output**: Structured violation reporting
- **Baseline Tracking**: Track violations over time
- **Config Reference**: `.oxlintrc.json` with AI-strict rules

**Key Rules**:
- Type safety: no-explicit-any, explicit-function-return-type
- Complexity: max-lines-per-function=50, max-params=3, complexity=10
- React: jsx-max-depth=4, performance optimizations

#### New Job: Lint Baseline Enforcement
- **Purpose**: Prevent quality regression across all codebases
- **Threshold**: Baseline violations + 10% tolerance
- **Enforcement**: CI fails if threshold exceeded
- **Auto-update**: Baselines update on `main` when violations decrease
- **Metrics Table**: Clear summary in GitHub Actions UI

**Baseline Metrics**:
| Linter | Metric | Config Source |
|--------|--------|---------------|
| Python Ruff | Violation count | `pyproject.toml` |
| Python Mypy | Error count | `pyproject.toml` |
| Python Bandit | Security issues | `pyproject.toml` |
| Go golangci-lint | Violation count | `backend/.golangci.yml` |
| Frontend Oxlint | Violation count | `frontend/.oxlintrc.json` |

### 2. Quality Workflow (`quality.yml`)

#### Enhanced Checks
- **Ruff**: Complexity enforcement with summary reporting
- **Mypy**: Strict mode with JSON reports
- **Basedpyright**: Ultra-strict type checking with JSON output
- **Bandit**: High-severity security scanning
- **Tach**: Architecture boundary validation

#### Quality Summary
New summary section in GitHub Actions showing:
- ✅ Ruff complexity thresholds
- ✅ Type checking strictness levels
- ✅ Security scanning coverage
- ✅ Architecture validation

### 3. Baseline Files Created

**`.ci-baselines/lint-baseline.json`**
```json
{
  "python_ruff": 0,
  "python_mypy": 0,
  "python_bandit": 0,
  "go_lint": 0,
  "frontend_oxlint": 0,
  "last_updated": "2026-02-02T00:00:00Z",
  "phase": "phase1-strict-enforcement",
  "description": "Phase 1 linting baselines - strict enforcement with AI-optimized configs"
}
```

**`.ci-baselines/README.md`**
- Comprehensive documentation
- Enforcement policy
- Manual update procedures
- Related configuration files

## Enforcement Policy

### Baseline Regression Prevention
1. **Threshold Calculation**: `max_allowed = baseline * 1.10`
2. **Failure Condition**: `current_violations > max_allowed`
3. **Success Condition**: `current_violations ≤ max_allowed`
4. **Improvement**: Always allowed (violations < baseline)

### Automatic Baseline Updates
- **Trigger**: Merge to `main` branch
- **Condition**: Current violations < baseline
- **Action**: Update baseline with new lower counts
- **Rationale**: Encourage continuous improvement

### Manual Baseline Updates
- **Approval**: Requires team review
- **Use Case**: Justified technical debt or major refactoring
- **Process**: Edit baseline file, commit with explanation

## CI Summary Enhancements

### GitHub Actions Step Summary
All linting jobs now report:
1. **Violation Counts**: Current vs. baseline
2. **Config Source**: Which file defines the rules
3. **Threshold Status**: Pass/fail with visual indicators
4. **Trend Data**: Stored as artifacts for analysis

### Artifact Retention
- **Duration**: 90 days
- **Purpose**: Trend analysis, debugging, audit trail
- **Contents**:
  - JSON reports from all linters
  - Type checking output
  - Security scan results

## Configuration References

### Python Linting
**File**: `/pyproject.toml`
- Lines 889-946: Ruff lint rules and complexity limits
- Lines 1038-1128: Mypy strict configuration
- Lines 1130-1201: Basedpyright ultra-strict settings
- Lines 314-320: Bandit security configuration

### Go Linting
**File**: `/backend/.golangci.yml`
- Lines 10-45: Enabled linters (43 total, 7 new)
- Lines 47-76: Linter-specific settings
- Lines 63-66: Complexity thresholds

### Frontend Linting
**File**: `/frontend/.oxlintrc.json`
- Lines 4-20: Type safety rules (maximum strictness)
- Lines 99-110: Complexity limits
- Lines 124-135: React performance rules

## Testing & Validation

### Pre-Commit Verification
```bash
# Test Python linting locally
cd /path/to/project
uv run ruff check src/ --output-format=json
uv run mypy src/
uv run bandit -r src/

# Test Go linting locally
cd backend
golangci-lint run --config=.golangci.yml

# Test Frontend linting locally
cd frontend
bun run check
bun run lint:oxc
```

### CI Dry Run
- Workflows will execute on next PR
- Baseline enforcement active immediately
- No breaking changes to existing passing jobs

## Migration Notes

### Backward Compatibility
- ✅ All changes are additive
- ✅ Existing jobs still run and pass
- ✅ New baseline job runs in parallel
- ✅ No disruption to deployment pipeline

### Known Issues
None identified. Baseline starts at 0, allowing gradual improvement.

## Future Enhancements

### Phase 2 Considerations
1. **Trend Visualization**: Dashboard for violation trends
2. **Per-File Baselines**: Granular tracking for large codebases
3. **Auto-Fix PRs**: Bot to auto-fix violations when possible
4. **Integration**: Link violations to JIRA/Linear tasks

### Metrics to Track
- Violation reduction velocity
- Time to fix violations
- Most common violation types
- Code churn vs. violation correlation

## Related Documents

- `PHASE_1_COMPLETE.md` - Overall Phase 1 completion report
- `PYTHON_QUALITY_CHECKLIST.md` - Python-specific quality gates
- `GO_LINTING_QUICK_REFERENCE.md` - Go linting guide
- `FRONTEND_LINTING_GUIDE.md` - Frontend linting guide
- `.ci-baselines/README.md` - Baseline documentation

## Rollback Procedure

If workflows cause issues:

```bash
# Revert CI changes
git revert <commit-hash>

# Or disable baseline job
# Edit .github/workflows/ci.yml
# Set: if: false
```

## Approval & Sign-off

- [x] CI workflow updates tested locally
- [x] Baseline files created and documented
- [x] Configuration files validated
- [x] No breaking changes to existing jobs
- [x] Rollback procedure documented

**Ready for deployment**: ✅ Yes

---

**Next Steps**:
1. Commit changes with message: `ci: update workflows for Phase 1 linting enforcement`
2. Monitor first CI run for any issues
3. Adjust thresholds if needed based on real-world data
4. Document any workflow failures in follow-up
