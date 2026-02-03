# Naming Explosion Prevention - Quick Reference

**Last Updated**: 2026-02-02

---

## Quick Check (Run These Commands)

```bash
# Frontend (TypeScript/React)
cd frontend && ./scripts/check-naming-explosion.sh

# Python
./scripts/shell/check-naming-explosion-python.sh

# Go
./scripts/shell/check-naming-explosion-go.sh
```

---

## Forbidden Patterns (All Languages)

### ❌ NEVER DO THIS

```
# Versioned
Dashboard_v2.tsx       (frontend)
service_v2.py          (python)
dashboardV2.go         (go)

# Prefixed
NewDashboard.tsx       (frontend)
enhanced_service.py    (python)
ImprovedHandler.go     (go)

# Suffixed
Dashboard_new.tsx      (frontend)
service_improved.py    (python)
handlerNew.go          (go)

# Numbered
Dashboard_2.tsx        (frontend)
service_2.py           (python)
handler_2.go           (go)
```

### ✅ DO THIS INSTEAD

```
# Edit in place
Dashboard.tsx          (frontend)
service.py             (python)
handler.go             (go)

# Or use distinct names
DashboardLayout.tsx    (frontend - different component)
service_auth.py        (python - different module)
handler_admin.go       (go - different handler)
```

---

## The Rule

**EDIT IN PLACE. NEVER CREATE VERSIONED COPIES.**

1. Read the existing file
2. Edit it directly
3. Delete any old versions
4. Update imports if needed
5. Commit

---

## Why This Matters

```
# What AI does without guards:
Dashboard.tsx          # Original (orphaned)
Dashboard_v2.tsx       # First iteration (orphaned)
EnhancedDashboard.tsx # Second iteration (orphaned)
NewDashboard.tsx       # Third iteration (in use)

# Result: 4 files, 3 orphans, massive confusion

# What we enforce:
Dashboard.tsx          # One file, always current
```

---

## Current Status (2026-02-02)

| Language   | Guard Script | Violations | Action Needed |
|------------|--------------|------------|---------------|
| Frontend   | ✅ Active    | ⚠️ 5 files | Clean up in Phase 2 |
| Python     | ✅ Active    | ⚠️ 5 files | Clean up in Phase 2 |
| Go         | ✅ Active    | ✅ Clean   | None |

---

## If You See a Violation

### Step 1: Identify Canonical File
```bash
# Find which file is actually used
grep -r "import.*Dashboard" src/ --include="*.tsx"
grep -r "from.*dashboard" src/ --include="*.py"
grep -r "import.*dashboard" . --include="*.go"
```

### Step 2: Consolidate
```bash
# Keep the one that's imported most
# Edit that file with your changes
# Delete ALL others

git rm Dashboard_v2.tsx
git rm EnhancedDashboard.tsx
```

### Step 3: Update Imports
```bash
# Fix any lingering imports
grep -r "Dashboard_v2" src/ --include="*.tsx"
# Replace with canonical name
```

### Step 4: Commit
```bash
git add .
git commit -m "refactor: consolidate Dashboard to canonical name"
```

---

## For AI Agents

**CRITICAL**: Before making changes:

1. ❌ DON'T create `Component_v2` or `NewComponent`
2. ✅ DO read the existing file
3. ✅ DO edit it in place
4. ✅ DO delete any old versions you find
5. ✅ DO run the naming check before committing

---

## Detection Scripts

### Frontend
```bash
frontend/scripts/check-naming-explosion.sh
```

### Python
```bash
scripts/shell/check-naming-explosion-python.sh
```

### Go
```bash
scripts/shell/check-naming-explosion-go.sh
```

---

## GitHub Actions

**Frontend**: ✅ `.github/workflows/naming-guard.yml`
**Python**: ❌ TODO (Phase 2)
**Go**: ❌ TODO (Phase 2)

---

## Full Documentation

- **Prevention Guide**: `frontend/docs/reports/AI_NAMING_EXPLOSION_PREVENTION.md`
- **Status Report**: `docs/reports/NAMING_EXPLOSION_GUARD_STATUS.md`
- **Verification**: `docs/reports/NAMING_EXPLOSION_VERIFICATION_COMPLETE.md`

---

## Common Questions

**Q: What if I need a new version of the API?**
A: Use import path versioning (`/api/v2/`) not file versioning (`api_v2.py`)

**Q: What about temporary experiments?**
A: Use git branches, not file names (`git checkout -b experiment/new-dashboard`)

**Q: What if the old file is still used?**
A: Then it's not "old" - both are canonical. Use distinct names: `DashboardV1.tsx` + `DashboardV2.tsx` → `DashboardLegacy.tsx` + `Dashboard.tsx`

**Q: What about test files?**
A: Same rule. Edit `test_dashboard.py` in place, don't create `test_dashboard_v2.py`

---

## Examples of Good Naming

### Frontend
```
components/
├── Dashboard.tsx              # Main component
├── DashboardLayout.tsx        # Layout variant
├── DashboardHeader.tsx        # Subcomponent
└── DashboardMetrics.tsx       # Feature module
```

### Python
```
services/
├── dashboard_service.py       # Main service
├── dashboard_repository.py    # Data layer
└── dashboard_analytics.py     # Analytics feature
```

### Go
```
dashboard/
├── dashboard.go               # Main handler
├── dashboard_service.go       # Service layer
└── dashboard_repository.go    # Data layer
```

---

## Red Flags

If you see ANY of these in a file listing:
- `*_v2`, `*_v3`, `*V2`, `*V3`
- `New*`, `Improved*`, `Enhanced*`, `Updated*`
- `*_new`, `*_improved`, `*_enhanced`, `*_updated`
- `*_2`, `*_3`

→ **STOP. Run the detection script. Clean up immediately.**

---

## Phase 2 Cleanup Plan

### Frontend (5 violations)
1. Consolidate `ErrorState.tsx` and `EnhancedErrorState.tsx`
2. Rename or consolidate `EnhancedGraphView.tsx`
3. Fix QA node components

### Python (5 violations)
1. Consolidate `streaming.py` and `streaming_v2.py`
2. Consolidate service variants
3. Consolidate TUI dashboard variants

### Go (0 violations)
✅ Already clean - good job!

---

**Remember**: ONE canonical name per concept. Edit in place. Delete old versions. Always.
