# Python Quality Tools Action Items

**Executed:** 2026-02-10  
**Repository:** /Users/kooshapari/temp-PRODVERCEL/485/kush/trace  
**Full Report:** `/docs/reports/PYTHON_QUALITY_REPORT_2026-02-10.md`

---

## Quick Status Matrix

| Tool | Status | Violations | Action |
|------|--------|-----------|--------|
| mypy | ❌ FAIL | 933 errors | Fix union type guards, null checks |
| basedpyright | ❌ FAIL | 1188 errors | Fix generic types, missing imports |
| tach | ❌ FAIL | 2 circular deps | Refactor tracertm.models & tracertm.core |
| ruff lint | ❌ FAIL | 1802 violations | 176 auto-fixable, 1600+ manual |
| ruff format | ❌ FAIL | 343 files | Run `ruff format .` |
| vulture | ⚠️ WARNING | 31 dead items | Remove unused code or add # noqa |
| pip-audit | ⚠️ TIMEOUT | N/A | Network issue; retry in CI |
| LOC guard | ❌ FAIL | 7 files | Update allowlist or refactor |
| naming check | ⏭️ SKIP | N/A | Not executed (requires --lang) |

---

## CRITICAL PATH (Do First)

### 1. Format All Files (Blocker for Other Tools)
```bash
cd /Users/kooshapari/temp-PRODVERCEL/485/kush/trace
python -m ruff format .
# ~1 min wall-clock; fixes 343 files automatically
```

**Files Affected:**
- `/tests/unit/tui/apps/test_tui_comprehensive.py` - syntax error (invalid statements)
- `/tests/unit/validation/test_model_validation_comprehensive.py` - multi-line formatting

**Why First:** Formatting is a prerequisite for clean type-checking and linting output.

---

### 2. Fix Circular Dependencies (Architecture)
```bash
# Detection
tach check  # Currently fails with circular deps
```

**Affected Modules:**
- `tracertm.models` - Circular import detected
- `tracertm.core` - Circular import detected

**Actions:**
1. Identify circular import chain in each module
2. Extract shared types/utilities to a third module
3. Reverse-import where appropriate
4. Re-run `tach check`

**Estimated Effort:** 30-45 min (depends on cycle complexity)

---

### 3. Fix Type Safety (High Impact)
**mypy errors:** 933 across 151 files  
**basedpyright errors:** 1188 across many files

#### Quick Wins (30 min):
```bash
# Auto-fix ruff violations (176 fixable)
cd /Users/kooshapari/temp-PRODVERCEL/485/kush/trace
python -m ruff check --fix src/tracertm/
```

#### Manual Fixes Required (2-4 hours):
1. **Union type guards** (src/tracertm/api/main.py:6675-6707)
   - Add null checks before accessing `.id`, `.status`, etc.
   - Example:
     ```python
     if webhook_integration:
         webhook_id = webhook_integration.id  # Now safe
     ```

2. **FastMCP stub assignments** (src/tracertm/mcp/tools/params/*.py)
   - Fix type incompatibility: `_StubMCP` ← `FastMCP[Any]`
   - May require casting or stub update

3. **Generic types in isinstance()** (workflows/activities.py:340)
   - Replace `isinstance(x, Type[T])` with runtime type checks

4. **TUI widget imports** (src/tracertm/tui/widgets/sync_status.py)
   - Ensure textual library is in pyproject.toml
   - Add textual type stubs if missing

---

## HIGH PRIORITY (Do Second)

### 4. Fix Missing Docstrings (400+ violations)
```bash
# Identify files with missing docstrings
python -m ruff check --select D103 src/tracertm/ | head -20

# Use auto-docstring tools or batch fix
# Tool recommendation: pydocstyle + automated generation
```

**Example Fix:**
```python
# Before
def process_item(item_id: str) -> Item:
    return get_item(item_id)

# After
def process_item(item_id: str) -> Item:
    """Fetch and return an item by ID."""
    return get_item(item_id)
```

**Estimated Effort:** 2-3 hours (400 functions × ~30s each)

---

### 5. Remove Dead Code (31 items)
**Files Affected:**
- `src/tracertm/tui/widgets/sync_status.py` - 11 unused items
- `src/tracertm/utils/figma.py` - 6 unused functions
- `src/tracertm/vault/client.py` - 5 unused items
- `src/tracertm/workflows/activities.py` - 1 unused function

**Actions:**
1. Review each item to confirm it's truly unused
2. Remove or mark with `# noqa: F841` if intentional (e.g., framework hooks)
3. Re-run vulture to confirm

**Estimated Effort:** 30-45 min

---

## MEDIUM PRIORITY (Do Third)

### 6. Fix Exception Handling Anti-Patterns (65+ violations)
**TRY300:** Return statements in try blocks should move to else  
**TRY401:** Redundant exception object in logging calls

**Example Fix:**
```python
# Before (TRY300)
try:
    result = process()
    return result
except Exception as exc:
    handle(exc)

# After
try:
    result = process()
except Exception as exc:
    handle(exc)
else:
    return result
```

**Files Affected:**
- `src/tracertm/workflows/tasks.py` - 2+ violations
- `src/tracertm/workflows/worker.py` - logger.exception redundancy

**Estimated Effort:** 1-2 hours

---

### 7. Update LOC Allowlist (7 files over limit)
```bash
# Current limits exceeded
cat config/loc-allowlist.txt

# Add or update these entries:
src/tracertm/clients/linear_client.py 870
src/tracertm/repositories/integration_repository.py 857
src/tracertm/clients/github_client.py 742
# (plus 4 Go backend files)
```

**Alternative:** Refactor large files into smaller modules (prefer this for >700 LOC)

**Estimated Effort:** 15 min (allowlist) or 2-3 hours (refactor)

---

## LOWER PRIORITY (Optional)

### 8. Reduce Private Member Access (200+ SLF001 violations)
This is a code smell but not blocking. Indicates tight coupling between modules.

### 9. Reduce Function Parameter Count (100+ PLR0913 violations)
Consider dataclass parameters or configuration objects for functions with 6+ params.

### 10. Address Line Length Issues (250+ E501 violations)
Auto-fixable with line wrapping; can be deferred if format pass is clean.

---

## Retry pip-audit on Network Stability
```bash
# Requires stable network connection to PyPI
pip-audit --skip-editable
# Expected: CVE scan results or clean status
```

**Note:** Can be run in CI environment where network is more stable.

---

## Execution Plan (Phased)

### Phase 1: Blockers (1-2 hours)
1. Run `ruff format .` (auto)
2. Run `ruff check --fix` (auto)
3. Break circular dependencies (manual investigation)

### Phase 2: Type Safety (2-4 hours)
1. Fix union type guards
2. Resolve FastMCP assignments
3. Fix TUI widget types

### Phase 3: Documentation (2-3 hours)
1. Add missing docstrings (D103)
2. Remove dead code (vulture)

### Phase 4: Quality Polish (1-2 hours)
1. Fix exception handling patterns
2. Update LOC allowlist or refactor

### Phase 5: Verification (30 min)
1. Re-run all tools
2. Verify clean output

---

## Expected Outcome

**Before:** 933 mypy errors + 1188 basedpyright + 1802 ruff violations + 2 circular deps + 343 formatting issues  
**After:** All tools passing or <50 acceptable warnings  
**Wall-Clock Effort:** ~10-12 hours (agent-driven, can be parallelized)  
**Critical Path:** Formatting → Type Safety → Circular Deps

---

## Tools Reference

| Tool | Command | Purpose |
|------|---------|---------|
| mypy | `python -m mypy src/tracertm/` | Static type checking |
| basedpyright | `basedpyright src/tracertm/` | Strict type validation |
| ruff lint | `python -m ruff check src/tracertm/` | Code quality violations |
| ruff format | `python -m ruff format .` | Auto-formatting |
| tach | `tach check` | Module boundary enforcement |
| vulture | `python -m vulture src/tracertm/` | Dead code detection |
| pip-audit | `pip-audit` | Dependency vulnerabilities |
| LOC check | `python scripts/quality/check_file_loc.py` | File size enforcement |

---

**Report Generated:** 2026-02-10  
**Next Review:** After Phase 5 verification

