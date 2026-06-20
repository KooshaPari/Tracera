# Phase 5 Maximum Strictness - Cleanup Strategy

**Status:** Phase 4 - Incremental Cleanup
**Date:** 2026-02-07
**Baseline:** 43,106 violations remaining (after auto-fix of 1,022 files)

---

## Cleanup Progress

### ✅ Phase 1-3: Complete
- ✅ Configuration updates (11 Go linters, 9 Python categories)
- ✅ Baselines generated
- ✅ CI integration (Makefile targets for external tools)
- ✅ Auto-fix applied (1,022 files, 1,239 file changes)

### 🟡 Phase 4: Incremental Cleanup (6-8 weeks)

**Starting baseline:** 43,106 violations
**Target:** 50% reduction (21,500 violations fixed) by Week 8

---

## Violation Priority Matrix

### Python Violations by Impact

| Rank | Code | Count | Impact | Effort | Strategy |
|------|------|-------|--------|--------|----------|
| 1 | **ANN001** | 10,222 | Type safety 🔴 | High | Semi-automated (add annotations) |
| 2 | **PLR6301** | 10,863 | False positive 🟢 | Low | Ignore (methods are intentionally instance methods) |
| 3 | **PLR2004** | 3,763 | Magic values 🟡 | Medium | Extract constants |
| 4 | **DOC201** | 2,590 | Documentation 🟡 | Medium | Add return docs |
| 5 | **PLC0415** | 1,952 | Import order 🟢 | Low | Refactor lazy imports |
| 6 | **ANN201** | 1,192 | Type safety 🔴 | Medium | Add return types |
| 7 | **SLF001** | 1,096 | Private access 🟢 | Low | Review/ignore |
| 8 | **CPY001** | 1,055 | Copyright 🟢 | Low | Add headers (scripted) |
| 9 | **ARG002** | 927 | Unused args 🟡 | Low | Prefix with `_` or remove |
| 10 | **ARG001** | 845 | Unused args 🟡 | Low | Prefix with `_` or remove |
| 11 | **BLE001** | 694 | Broad except 🔴 | High | Make specific |
| 12 | **ANN401** | 684 | `Any` type 🔴 | High | Add proper types |
| 13 | **E501** | 609 | Line length 🟢 | Low | Reformat (auto) |
| 14 | **ANN202** | 588 | Private return 🟡 | Low | Add return types |
| 15 | **D205** | 546 | Docstring blank 🟢 | Low | Auto-fix |

### Security Findings (Semgrep - 26 findings)

| Severity | Finding | Count | Action |
|----------|---------|-------|--------|
| HIGH | SQL injection risk (text()) | 8 | ✅ FALSE POSITIVE - parameterized |
| MEDIUM | Logger credential leak | 18 | Review/sanitize logs |

---

## Phased Cleanup Plan (Weeks 3-8)

### Week 3: Critical Security & Type Safety (P0) 🔴

**Focus:** ANN (type annotations), BLE001 (broad exceptions), ANN401 (Any types)

**Target files (25-30):**
- `src/tracertm/api/routers/*.py` - Add type annotations (highest traffic)
- `src/tracertm/services/*.py` - Fix broad exceptions
- `src/tracertm/repositories/*.py` - Replace `Any` with proper types

**Expected:** ~3,000-4,000 violations fixed

**Agent delegation:**
```bash
# Launch 3 parallel agents
- Agent 1: Add type annotations to API routers (ANN001, ANN201)
- Agent 2: Fix broad exceptions in services (BLE001)
- Agent 3: Replace Any types in repositories (ANN401)
```

---

### Week 4: Magic Values & Documentation (P1) 🟡

**Focus:** PLR2004 (magic values), DOC201 (return docs)

**Target files (20-25):**
- `src/tracertm/services/*.py` - Extract magic numbers to constants
- `src/tracertm/api/handlers/*.py` - Add return documentation

**Expected:** ~2,500-3,000 violations fixed

**Agent delegation:**
```bash
# Launch 2 parallel agents
- Agent 1: Extract constants from magic values (PLR2004)
- Agent 2: Add return documentation to docstrings (DOC201)
```

---

### Week 5: Unused Arguments & Imports (P1) 🟡

**Focus:** ARG001/ARG002 (unused args), PLC0415 (import order)

**Target files (30-40):**
- All services and handlers - prefix unused args with `_`
- Refactor lazy imports to top-level

**Expected:** ~3,700-4,000 violations fixed

**Agent delegation:**
```bash
# Launch 2 parallel agents
- Agent 1: Fix unused arguments (ARG001, ARG002)
- Agent 2: Refactor lazy imports (PLC0415)
```

---

### Week 6: Low-Hanging Fruit (P2) 🟢

**Focus:** CPY001 (copyright), D205 (docstring blank), E501 (line length)

**Target:** Scripted/automated fixes

**Script:**
```python
# add_copyright_headers.py
for file in python_files:
    if not has_copyright_header(file):
        prepend_copyright(file)
```

**Expected:** ~2,200-2,500 violations fixed

---

### Weeks 7-8: PLR6301 Review & Final Cleanup

**Focus:** Review PLR6301 (no-self-use) - likely false positives

**Strategy:**
1. Analyze which methods are intentionally instance methods (access self later, design pattern)
2. Add `per-file-ignores` for legitimate cases
3. Convert remaining methods to `@staticmethod` where appropriate

**Expected:** ~10,000 violations reviewed, ~500-1,000 fixed, rest ignored with justification

---

## High-Value Manual Fix Examples

### Fix 1: Add Type Annotations (ANN001, ANN201)

**Before:**
```python
def create_item(db, project_id, data):  # Missing all type annotations
    item = Item(**data)
    db.add(item)
    return item
```

**After:**
```python
def create_item(
    db: AsyncSession,
    project_id: str,
    data: dict[str, Any],
) -> Item:
    item = Item(**data)
    db.add(item)
    return item
```

**Impact:** Prevents runtime None bugs, enables IDE autocomplete

---

### Fix 2: Fix Broad Exceptions (BLE001)

**Before:**
```python
try:
    result = dangerous_operation()
except Exception:  # Swallows all errors!
    logger.error("Failed")
    return None
```

**After:**
```python
try:
    result = dangerous_operation()
except (ValueError, KeyError, DatabaseError) as e:  # Specific!
    logger.error(f"Operation failed: {e}")
    raise
```

**Impact:** Makes failures visible, prevents silent data corruption

---

### Fix 3: Extract Magic Values (PLR2004)

**Before:**
```python
if status_code == 200:  # Magic number!
    process_success()
elif status_code == 404:  # Magic number!
    handle_not_found()
```

**After:**
```python
HTTP_OK = 200
HTTP_NOT_FOUND = 404

if status_code == HTTP_OK:
    process_success()
elif status_code == HTTP_NOT_FOUND:
    handle_not_found()
```

**Impact:** Self-documenting code, fewer typo bugs

---

### Fix 4: Fix Unused Arguments (ARG001, ARG002)

**Before:**
```python
def process(data, context, config):  # context, config unused!
    return transform(data)
```

**After:**
```python
def process(data, _context, _config):  # Prefix with _ to acknowledge
    return transform(data)
```

**Impact:** Code clarity, signals intentional interface compatibility

---

## Progress Tracking

### Metrics Dashboard

**Create:** `.quality/progress-tracker.py`

**Tracks:**
- Violations by category (weekly snapshots)
- Fix velocity (violations/week)
- High-impact vs low-impact ratio
- Time to target (50% reduction)

**Commands:**
```bash
# Snapshot current violations
.quality/progress-tracker.py snapshot

# Compare against baseline
.quality/progress-tracker.py compare

# Generate weekly report
.quality/progress-tracker.py report --week 3
```

---

## Agent Swarm Strategy

### Week 3 Swarm (Type Safety)

**Launch 3 parallel agents:**

1. **type-annotator**: Add ANN001/ANN201 to API routers
   - Files: `src/tracertm/api/routers/*.py`
   - Target: ~800-1,000 violations

2. **exception-fixer**: Fix BLE001 in services
   - Files: `src/tracertm/services/*.py`
   - Target: ~400-500 violations

3. **any-replacer**: Replace ANN401 in repositories
   - Files: `src/tracertm/repositories/*.py`
   - Target: ~300-400 violations

**Total:** ~1,500-1,900 violations fixed in Week 3

---

### Week 4 Swarm (Quality)

**Launch 2 parallel agents:**

1. **constant-extractor**: Extract PLR2004 magic values
   - Files: `src/tracertm/services/*.py`, `src/tracertm/api/handlers/*.py`
   - Target: ~1,500-2,000 violations

2. **doc-enricher**: Add DOC201 return documentation
   - Files: All public functions
   - Target: ~1,000-1,500 violations

**Total:** ~2,500-3,500 violations fixed in Week 4

---

## Success Milestones

### Week 3 Checkpoint
- ✅ 3,000-4,000 violations fixed
- ✅ All critical type annotations added (API layer)
- ✅ All broad exceptions made specific (services layer)
- **Progress:** ~10% baseline cleared

### Week 4 Checkpoint
- ✅ 5,500-7,500 violations fixed (cumulative)
- ✅ Magic values extracted to constants
- ✅ All public functions documented
- **Progress:** ~17% baseline cleared

### Week 8 Target
- ✅ 21,500 violations fixed (50% baseline)
- ✅ All high-impact violations resolved
- ✅ Remaining violations: Low-priority or false positives
- **Progress:** 50% baseline cleared

---

## Next Actions

### Immediate (This Week)
1. ✅ Auto-fix applied (1,022 files committed)
2. ⏳ Launch Week 3 agent swarm (type safety)
3. ⏳ Create progress tracking dashboard

### Short-term (Week 4)
1. Launch Week 4 agent swarm (quality)
2. Review semgrep security findings
3. Add copyright headers (scripted)

### Medium-term (Weeks 5-8)
1. Continue incremental cleanup (10-20 files/week)
2. Review PLR6301 false positives
3. Document patterns and anti-patterns

---

**Document Status:** ACTIVE - Week 3 Swarm Ready
**Last Updated:** 2026-02-07
**Next:** Launch type-annotator, exception-fixer, any-replacer agents
