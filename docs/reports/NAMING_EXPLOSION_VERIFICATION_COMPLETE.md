# Naming Explosion Prevention - Verification Complete

**Date**: 2026-02-02
**Task**: Verify and enhance naming explosion prevention across all three languages
**Status**: ✅ COMPLETE

---

## Summary

Successfully verified and enhanced naming explosion prevention guards across all three languages (TypeScript, Python, Go). Detection scripts are now active and violations have been identified for cleanup in Phase 2.

---

## What Was Done

### 1. Frontend (TypeScript/React) ✅

**Status**: ENHANCED - Script fixed, violations documented

**Actions Completed**:
- ✅ Verified existing detection script: `frontend/scripts/check-naming-explosion.sh`
- ✅ Verified GitHub Action: `.github/workflows/naming-guard.yml`
- ✅ Fixed script to exclude `node_modules/` (eliminated false positives)
- ✅ Tested script - working correctly
- ✅ Identified real violations (5 files)

**Script Location**:
```bash
frontend/scripts/check-naming-explosion.sh
```

**Detection Patterns**:
- Versioned: `*_v2.tsx`, `*V2.tsx`
- Prefixed: `NewDashboard.tsx`, `Enhanced*.tsx`
- Suffixed: `*_new.tsx`, `*_improved.tsx`
- Numbered: `*_2.tsx`, `*_3.tsx`

**Violations Found**:
```
apps/web/src/components/graph/EnhancedErrorState.tsx
apps/web/src/components/graph/EnhancedGraphView.tsx
apps/web/src/components/graph/nodes/QAEnhancedNode.tsx
apps/web/src/components/graph/QAEnhancedNode.tsx
apps/web/src/hooks/useQAEnhancedNodeData.ts
```

**Oxlint Rules** (already configured):
```json
{
  "rules": {
    "unicorn/filename-case": ["error", {
      "cases": {
        "camelCase": true,
        "pascalCase": true,
        "kebabCase": true
      }
    }]
  }
}
```

### 2. Python ✅

**Status**: NEW PROTECTION - Script created, violations identified

**Actions Completed**:
- ✅ Created detection script: `scripts/shell/check-naming-explosion-python.sh`
- ✅ Made script executable
- ✅ Tested script - working correctly
- ✅ Identified violations (5 files)
- ✅ Verified ruff N999 rule is configured

**Script Location**:
```bash
scripts/shell/check-naming-explosion-python.sh
```

**Detection Patterns** (Python snake_case):
- Versioned: `*_v2.py`, `*V2.py`
- Prefixed: `new_*.py`, `improved_*.py`, `enhanced_*.py`
- Suffixed: `*_new.py`, `*_improved.py`
- Numbered: `*_2.py`, `*_3.py`

**Violations Found**:
```python
src/tracertm/mcp/tools/streaming_v2.py
src/tracertm/services/spec_analytics_service_v2.py
src/tracertm/tui/apps/dashboard_v2.py
tests/unit/api/test_api_comprehensive_fixed.py
tests/unit/tui/apps/test_dashboard_v2.py
```

**Ruff N999 Configuration** (already in pyproject.toml):
```toml
[tool.ruff.lint]
select = [
    "N",    # pep8-naming (includes N999)
]

# N999 ignored only for scripts with hyphens:
"scripts/python/**" = ["N999"]
```

**Note**: Ruff N999 checks module name validity but doesn't catch AI naming patterns like `enhanced_*` or `*_v2`. The shell script fills this gap.

### 3. Go ✅

**Status**: NEW PROTECTION - Script created, no violations found

**Actions Completed**:
- ✅ Created detection script: `scripts/shell/check-naming-explosion-go.sh`
- ✅ Made script executable
- ✅ Tested script - working correctly
- ✅ No violations found (clean!)
- ✅ Verified revive `var-naming` rule is configured

**Script Location**:
```bash
scripts/shell/check-naming-explosion-go.sh
```

**Detection Patterns** (Go PascalCase):
- Versioned: `*V2.go`, `*_v2.go`
- Prefixed: `New*.go`, `Improved*.go`, `Enhanced*.go`
- Suffixed: `*New.go`, `*Improved.go`
- Numbered: `*_2.go`, `*_3.go`

**Violations Found**: None ✅

**Golangci-lint Revive Configuration** (already in .golangci.yml):
```yaml
linters-settings:
  revive:
    rules:
      - name: var-naming        # Checks variable naming
      - name: package-comments  # Requires package docs
      - name: exported          # Checks exported identifiers
```

**Note**: Revive `var-naming` enforces Go conventions but doesn't target AI naming explosion patterns. The shell script provides this layer.

---

## Test Results

### All Scripts Tested ✅

**Frontend**:
```bash
$ cd frontend && ./scripts/check-naming-explosion.sh
❌ NAMING EXPLOSION DETECTED
Found 5 violations (documented above)
```

**Python**:
```bash
$ ./scripts/shell/check-naming-explosion-python.sh
❌ NAMING EXPLOSION DETECTED
Found 5 violations (documented above)
```

**Go**:
```bash
$ ./scripts/shell/check-naming-explosion-go.sh
✅ No naming explosion detected
```

---

## Naming Rules by Language

### TypeScript/React (frontend)

**Allowed**:
```typescript
✅ Dashboard.tsx              // Canonical
✅ DashboardLayout.tsx        // Distinct component
✅ DashboardHeader.tsx        // Subcomponent
```

**Forbidden**:
```typescript
❌ Dashboard_v2.tsx           // Versioned
❌ DashboardNew.tsx           // Prefixed
❌ EnhancedDashboard.tsx      // Prefixed
❌ Dashboard_2.tsx            // Numbered
```

### Python (backend)

**Allowed**:
```python
✅ dashboard.py               # Canonical
✅ dashboard_service.py       # Distinct module
✅ dashboard_repository.py    # Submodule
```

**Forbidden**:
```python
❌ dashboard_v2.py            # Versioned
❌ new_dashboard.py           # Prefixed
❌ enhanced_dashboard.py      # Prefixed
❌ dashboard_2.py             # Numbered
```

### Go (backend)

**Allowed**:
```go
✅ dashboard.go               // Canonical
✅ dashboard_service.go       // Distinct service
✅ dashboard_repository.go    // Repository
```

**Forbidden**:
```go
❌ dashboardV2.go             // Versioned
❌ NewDashboard.go            // Prefixed
❌ EnhancedDashboard.go       // Prefixed
❌ dashboard_2.go             // Numbered
```

---

## Current Guard Status

| Language   | Detection Script | Linter Rules | GitHub Action | Violations | Status |
|------------|------------------|--------------|---------------|------------|--------|
| TypeScript | ✅ Fixed         | ✅ Oxlint    | ✅ Active     | ⚠️ 5 found | **ENHANCED** |
| Python     | ✅ New           | ⚠️ N999      | ❌ Missing    | ⚠️ 5 found | **NEW PROTECTION** |
| Go         | ✅ New           | ⚠️ var-naming| ❌ Missing    | ✅ Clean   | **NEW PROTECTION** |

**Legend**:
- ✅ = Fully implemented and tested
- ⚠️ = Partial (rule exists but doesn't catch all AI patterns)
- ❌ = Not implemented

---

## Files Created/Modified

### Created ✅
1. `scripts/shell/check-naming-explosion-python.sh` - Python detection script
2. `scripts/shell/check-naming-explosion-go.sh` - Go detection script
3. `docs/reports/NAMING_EXPLOSION_GUARD_STATUS.md` - Detailed analysis
4. `docs/reports/NAMING_EXPLOSION_VERIFICATION_COMPLETE.md` - This file

### Modified ✅
1. `frontend/scripts/check-naming-explosion.sh` - Fixed to exclude `node_modules/`

---

## Violations to Address in Phase 2

### Frontend (5 files)
```
apps/web/src/components/graph/EnhancedErrorState.tsx
apps/web/src/components/graph/EnhancedGraphView.tsx
apps/web/src/components/graph/nodes/QAEnhancedNode.tsx
apps/web/src/components/graph/QAEnhancedNode.tsx
apps/web/src/hooks/useQAEnhancedNodeData.ts
```

**Recommended Action**:
1. Check if `ErrorState.tsx` exists (it does) → consolidate
2. Rename `EnhancedGraphView.tsx` to `GraphView.tsx` (if canonical)
3. Consolidate QA node components

### Python (5 files)
```
src/tracertm/mcp/tools/streaming_v2.py
src/tracertm/services/spec_analytics_service_v2.py
src/tracertm/tui/apps/dashboard_v2.py
tests/unit/api/test_api_comprehensive_fixed.py
tests/unit/tui/apps/test_dashboard_v2.py
```

**Recommended Action**:
1. Consolidate `streaming.py` and `streaming_v2.py`
2. Consolidate `spec_analytics_service.py` and `spec_analytics_service_v2.py`
3. Consolidate TUI dashboard variants
4. Rename test files (remove `_fixed` suffix)

### Go (0 files) ✅
No violations found - Go code is clean!

---

## Next Steps (Phase 2)

### Immediate (Next Sprint)

1. **Add GitHub Actions** for Python and Go:
   ```yaml
   # .github/workflows/python-naming-guard.yml
   # .github/workflows/go-naming-guard.yml
   ```

2. **Clean up violations**:
   - Frontend: 5 files to consolidate
   - Python: 5 files to consolidate
   - Go: Clean ✅

3. **Add to pre-commit hooks**:
   ```yaml
   # .pre-commit-config.yaml
   - id: naming-explosion-check
     name: Check naming explosion
     entry: scripts/shell/check-naming-explosion-python.sh
     language: system
     types: [python]
   ```

### Future Enhancements

1. **Semgrep integration** for import-level detection
2. **Import graph analysis** to detect orphaned files
3. **Auto-fix tooling** via MCP
4. **Cross-language consistency checker**

---

## How to Use the Guards

### Manual Check (All Languages)

```bash
# Frontend
cd frontend && ./scripts/check-naming-explosion.sh

# Python
./scripts/shell/check-naming-explosion-python.sh

# Go
./scripts/shell/check-naming-explosion-go.sh

# All at once (create master script if needed)
```

### CI/CD Integration

**Frontend**: Already integrated via `.github/workflows/naming-guard.yml`

**Python & Go**: Add GitHub Actions (see recommendations above)

### Pre-commit Hook

```bash
# Install pre-commit
pip install pre-commit

# Add to .pre-commit-config.yaml (see examples above)

# Install hooks
pre-commit install
```

---

## Documentation

All naming explosion prevention documentation is centralized:

1. **Main guide**: `frontend/docs/reports/AI_NAMING_EXPLOSION_PREVENTION.md`
2. **Status report**: `docs/reports/NAMING_EXPLOSION_GUARD_STATUS.md`
3. **This verification**: `docs/reports/NAMING_EXPLOSION_VERIFICATION_COMPLETE.md`

Update `AGENTS.md` and `CLAUDE.md` to reference these docs.

---

## Conclusion

### What We Achieved ✅

1. **Verified** existing frontend protection (working, needed fix for false positives)
2. **Created** new Python detection (working, found violations)
3. **Created** new Go detection (working, no violations found)
4. **Tested** all three scripts successfully
5. **Documented** all violations for Phase 2 cleanup
6. **Identified** gaps in linter rules (N999, var-naming don't catch AI patterns)

### Key Insights

1. **Frontend violations exist** despite having a detection script
   - Reason: Script wasn't run in CI/CD before commits
   - Fix: Enforce in pre-commit or CI

2. **Python violations exist** because no detection existed before
   - Reason: Ruff N999 doesn't catch AI patterns
   - Fix: New script fills the gap

3. **Go is clean** - good AI hygiene or less iteration?
   - Likely: Less AI iteration on Go backend
   - Good: No cleanup needed

4. **Shell scripts are essential** - linter rules alone don't catch AI naming patterns
   - N999: Checks module validity, not "enhanced_*"
   - var-naming: Checks Go style, not "EnhancedDashboard"
   - Solution: Shell scripts detect file-level patterns

### Risk Assessment

**Current Risk**: ⚠️ MEDIUM

- Frontend: Violations exist, but detected
- Python: Violations exist, now detected
- Go: Clean

**Phase 2 Risk Mitigation**:
- Add GitHub Actions for Python/Go (blocks PRs)
- Clean up existing violations (prevents confusion)
- Add pre-commit hooks (prevents local commits)

**Long-term**: With all guards in place, risk becomes LOW

---

## Task Complete ✅

All requirements met:

1. ✅ Checked naming explosion guards are active (frontend: yes, Python/Go: created)
2. ✅ Ran detection scripts (all three languages tested)
3. ✅ Tested against example violations (all scripts work)
4. ✅ Created missing guards for Python and Go (shell scripts)
5. ✅ Documented current naming protection status (detailed report)

**Deliverables**:
- 2 new shell scripts (Python, Go)
- 1 fixed shell script (frontend)
- 2 comprehensive reports (status + verification)
- All violations documented for Phase 2

**Ready for Phase 2**: Cleanup violations and add GitHub Actions.
