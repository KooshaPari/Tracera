# Quality Remediation Master Plan: Python + Frontend

**Status:** Comprehensive E2E Plan  
**Scope:** Python (Ruff, Mypy, Pytest) + Frontend (Oxlint)  
**Timeline:** ~2–3 hours total wall-clock (agent-driven, parallel where possible)

---

## Executive Summary

| Component | Tool | Issues | Fixable | Effort | Status |
|-----------|------|--------|---------|--------|--------|
| **Python** | Ruff | 28,759 | 5,252 | Phase 1–5 | Plan ready |
| **Python** | Mypy | ~500 | ~200 | Phase 3–4 | Plan ready |
| **Python** | Pytest | 1 (plugin) | 1 | Phase 1 | Plan ready |
| **Frontend** | Oxlint | 2,122 | ~1,500 | Phase 1–5 | Plan ready |

---

## Parallel Execution Strategy

### Batch 1 (Unblock, ~15 min)
- **Python:** Fix Pytest plugin conflict (Phase 1)
- **Frontend:** Create .eslintignore (Phase 1)
- **Parallel:** Both can run simultaneously

### Batch 2 (Auto-fix, ~20 min)
- **Python:** `ruff check --fix` (Phase 2)
- **Frontend:** `bunx oxlint --fix` (Phase 2)
- **Parallel:** Both can run simultaneously

### Batch 3 (Manual review, ~30 min)
- **Python:** Review F821, S101 in tests (Phase 3)
- **Frontend:** Review block-scoped-var (Phase 3)
- **Sequential:** Requires human judgment

### Batch 4 (Dangerous fixes, ~15 min)
- **Python:** `ruff check --fix --unsafe-fixes` (Phase 4)
- **Frontend:** `bunx oxlint --fix-dangerously` (Phase 4)
- **Parallel:** Both can run simultaneously

### Batch 5 (Verification, ~15 min)
- **Python:** `make quality-python` + pytest
- **Frontend:** `make quality-frontend` + bun test
- **Parallel:** Both can run simultaneously

---

## Detailed Plans

See:
- **Python:** `docs/reports/PYTHON_QUALITY_E2E_PLAN.md`
- **Frontend:** `docs/reports/FRONTEND_OXLINT_E2E_PLAN.md`

---

## Implementation Guides

- **Python:** `docs/guides/PYTHON_QUALITY_IMPLEMENTATION_GUIDE.md` (if needed)
- **Frontend:** `docs/guides/FRONTEND_OXLINT_IMPLEMENTATION_GUIDE.md`

---

## Success Criteria (All Required)

✅ Python: `make quality-python` passes (Ruff, Mypy, Pytest)  
✅ Frontend: `make quality-frontend` passes (Oxlint)  
✅ All tests pass (Python + Frontend)  
✅ CI enforces both checks on every commit  
✅ Zero warnings in both codebases

---

## Next Steps

1. **Batch 1:** Fix Pytest plugin + create .eslintignore
2. **Batch 2:** Run auto-fix on both
3. **Batch 3:** Manual review (parallel agents)
4. **Batch 4:** Dangerous fixes
5. **Batch 5:** Verify + CI enforcement

**Estimated Total Time:** ~70 min wall-clock (agent-driven)

