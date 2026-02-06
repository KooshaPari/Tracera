# Immediate Actions - Linting Hardening

**Date**: 2026-02-02
**Priority**: URGENT
**Estimated Time**: 14 hours (Phase 1 only)

---

## 🚨 Critical Issues Found

### All Languages Have Same 3 Problems:

1. ❌ **NO NAMING EXPLOSION PREVENTION** - AI creates Dashboard_v2, NewDashboard, etc.
2. ❌ **MISSING/DISABLED COMPLEXITY LIMITS** - AI generates 1000-line functions
3. ❌ **MAGIC NUMBERS ALLOWED** - Literal values everywhere without constants

---

## Phase 1: Immediate Actions (Do Today)

### 1. Frontend - MOST URGENT (4 hours)

**Problem**: AI-strict config exists but is NOT active. Current config has 60+ rules disabled.

**Action**:
```bash
cd frontend

# Backup current config
mv .oxlintrc.json .oxlintrc.json.backup

# Activate AI-strict
cp .oxlintrc.json.ai-strict .oxlintrc.json

# Check current violations
bunx oxlint --type-aware . > linting-baseline.txt
wc -l linting-baseline.txt

# Auto-fix what's possible
bunx oxlint --type-aware . --fix

# Commit changes
git add .oxlintrc.json linting-baseline.txt
git commit -m "refactor: activate AI-strict oxlint configuration"
```

**Expected Impact**: 500-2000 new errors, ~40% auto-fixable

---

### 2. Python - HIGH PRIORITY (4 hours)

**Problem**: ZERO complexity enforcement. AI can generate arbitrarily complex functions.

**Action**:
```bash
# Edit pyproject.toml
```

Add to `[tool.ruff.lint]` section:
```toml
select = [
    # ... existing rules (E, W, F, I, B, C4, UP, etc.) ...
    "C90",      # McCabe complexity
    "PLR0911",  # too-many-return-statements
    "PLR0912",  # too-many-branches
    "PLR0913",  # too-many-arguments (>5)
    "PLR0915",  # too-many-statements
    "PLR1702",  # too-many-nested-blocks
    "PLR2004",  # magic-value-comparison (MAGIC NUMBERS!)
]

[tool.ruff.lint.mccabe]
max-complexity = 7  # Strict for AI-coding

[tool.ruff.lint.pylint]
max-args = 5
max-branches = 12
max-returns = 6
max-statements = 50
```

**Check violations**:
```bash
cd /path/to/python/backend
ruff check . --select C90,PLR > ruff-complexity-baseline.txt
```

**Commit**:
```bash
git add pyproject.toml ruff-complexity-baseline.txt
git commit -m "refactor: add complexity limits to ruff configuration"
```

**Expected Impact**: 200-400 functions need refactoring

---

### 3. Go - MEDIUM PRIORITY (6 hours)

**Problem**: Missing 7 critical linters, complexity too lenient (15/20 vs target 10/12)

**Action**:
```bash
# Edit backend/.golangci.yml
```

Add to `linters.enable` section:
```yaml
linters:
  enable:
    # ... existing linters ...
    - dupl              # Duplicate code detection
    - goconst           # Repeated strings → constants
    - funlen            # Function length limits
    - mnd               # Magic number detection
    - nolintlint        # Validate //nolint usage
    - gochecknoglobals  # No global variables
    - perfsprint        # Performance optimization
```

Add/update settings:
```yaml
linters-settings:
  gocyclo:
    min-complexity: 10  # Down from 15

  gocognit:
    min-complexity: 12  # Down from 20

  funlen:
    lines: 80
    statements: 50

  mnd:
    checks:
      - argument
      - case
      - condition
      - operation
      - return
      - assign
```

**Check violations**:
```bash
cd backend
golangci-lint run --out-format=json > golangci-baseline.json
```

**Commit**:
```bash
git add .golangci.yml golangci-baseline.json
git commit -m "refactor: add missing linters and tighten complexity limits"
```

**Expected Impact**: 300-600 new violations from 7 new linters

---

## Quick Commands Reference

### Check Current State

```bash
# Frontend violations
cd frontend
bunx oxlint --type-aware . | wc -l

# Python violations
cd backend/python  # or wherever Python code lives
ruff check . | wc -l

# Go violations
cd backend
golangci-lint run | grep -c "^backend/"
```

### After Phase 1 Completion

```bash
# Create baseline reports for tracking
./scripts/create-linting-baseline.sh

# Expected output:
# frontend/linting-baseline.txt (current: ~53k lines → expect: 500-2000)
# backend/ruff-baseline.txt (unknown → expect: 400-800)
# backend/golangci-baseline.json (current: ~150 → expect: 450-750)
```

---

## What Happens Next (Phase 2-4)

### Phase 2 (Weeks 2-3): Fix Critical Violations
- Type safety issues
- Security vulnerabilities
- Correctness bugs
- **Effort**: 80-120 hours (parallelizable across languages)

### Phase 3 (Weeks 4-5): Complexity Refactoring
- Split long functions
- Reduce parameter counts
- Extract nested logic
- **Effort**: 80-110 hours (needs careful refactoring)

### Phase 4 (Week 6): Style & Consistency
- Fix import ordering
- Extract magic numbers
- Remove duplication
- **Effort**: 25-40 hours (mostly auto-fixable)

---

## Risk Mitigation

### If Too Many Errors

**Option A**: Incremental rollout
```toml
# Start with lower limits
[tool.ruff.lint.mccabe]
max-complexity = 15  # Instead of 7

# Gradually tighten:
# Week 1: 15
# Week 2: 12
# Week 3: 10
# Week 4: 7 (target)
```

**Option B**: Warning-only first
```yaml
# .golangci.yml
issues:
  max-issues-per-linter: 0
  max-same-issues: 0
  # Don't fail CI yet
  new: false
```

**Option C**: Selective enablement
```bash
# Enable one new linter at a time
# Week 1: dupl only
# Week 2: + goconst
# Week 3: + funlen
# etc.
```

---

## Success Criteria (End of Phase 1)

- [ ] Frontend: AI-strict config active, baseline captured
- [ ] Python: Complexity rules added, baseline captured
- [ ] Go: 7 new linters added, baseline captured
- [ ] All changes committed to git
- [ ] CI updated (if needed)
- [ ] Team notified of changes

---

## Support & Questions

### Detailed Audit Reports

1. **Python**: `docs/reports/PYTHON_LINTING_AI_CODING_AUDIT.md`
2. **Go**: `docs/reports/GO_LINTING_AUDIT_AI_CODING.md`
3. **Frontend**: `docs/reports/FRONTEND_TOOLS_AUDIT.md`
4. **Master Plan**: `docs/reports/COMPREHENSIVE_LINTING_AUDIT_MASTER_PLAN.md`

### Quick Reference

- **AI Agent Guide**: `AI_AGENT_QUICK_REFERENCE.md`
- **Naming Explosion**: `docs/reports/AI_NAMING_EXPLOSION_PREVENTION.md`
- **AI Coding Strategy**: `docs/reports/AI_CODED_LINTING_STRATEGY.md`

---

## Time Breakdown (Phase 1 Only)

| Task | Time | Can Parallelize? |
|------|------|------------------|
| Frontend config activation | 1h | No |
| Frontend baseline + auto-fix | 2h | No |
| Frontend testing | 1h | No |
| Python config updates | 1h | Yes (with Go) |
| Python baseline | 2h | Yes (with Go) |
| Python testing | 1h | Yes (with Go) |
| Go config updates | 2h | Yes (with Python) |
| Go baseline | 2h | Yes (with Python) |
| Go testing | 2h | Yes (with Python) |
| **Total Sequential** | **4h** | (Frontend only) |
| **Total Parallel** | **10h** | (Python + Go together) |
| **Total Combined** | **14h** | (Frontend, then Python+Go) |

**Optimal execution**: Do frontend first (blocks team), then Python + Go in parallel.

---

## Ready to Execute

All audit work is complete. Configuration changes are documented. Baseline commands are prepared.

**Status**: ✅ Ready for implementation
**Approval needed**: Tech Lead sign-off
**Next step**: Execute Phase 1 actions above

**Questions?** Review the master plan document for full context.
