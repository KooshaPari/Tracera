# Quality Remediation Checklist

**Master Plan:** `docs/reports/QUALITY_REMEDIATION_MASTER_PLAN.md`

---

## Batch 1: Unblock (15 min)

### Python: Fix Pytest Plugin Conflict
- [ ] Open `src/tracertm/conftest.py`
- [ ] Remove `"pytest_benchmark"` from `pytest_plugins`
- [ ] Open `tests/conftest.py`
- [ ] Remove `"pytest_benchmark.plugin"` from `pytest_plugins`
- [ ] Run: `cd /repo && pytest --collect-only 2>&1 | head -20`
- [ ] Verify: No "Plugin already registered" error

### Frontend: Create .eslintignore
- [ ] Create `frontend/.eslintignore`
- [ ] Add patterns: storybook-static/, .next/, dist/, build/, *.min.js, node_modules/
- [ ] Run: `cd frontend && bunx oxlint . --ignore-path=.eslintignore 2>&1 | tail -3`
- [ ] Verify: ~200–300 errors (down from 2,122)

---

## Batch 2: Auto-fix (20 min)

### Python: Ruff Auto-fix
- [ ] Run: `cd /repo && ruff check --fix src/ tests/`
- [ ] Verify: `ruff check src/ tests/ 2>&1 | tail -5`
- [ ] Expected: ~5,000–10,000 issues remaining

### Frontend: Oxlint Auto-fix
- [ ] Run: `cd frontend && bunx oxlint --fix --tsconfig=tsconfig.json .`
- [ ] Verify: `bunx oxlint . --ignore-path=.eslintignore 2>&1 | tail -3`
- [ ] Expected: ~500–700 issues remaining

---

## Batch 3: Manual Review (30 min)

### Python: Review F821, S101
- [ ] List F821 files: `ruff check src/ --select=F821 2>&1 | cut -d: -f1 | sort -u`
- [ ] Review top 5 files; fix or suppress
- [ ] List S101 in src/: `ruff check src/ --select=S101 2>&1 | wc -l`
- [ ] Verify: S101 only in tests/

### Frontend: Review block-scoped-var
- [ ] List top files: `bunx oxlint . 2>&1 | grep "block-scoped-var" | cut -d: -f1 | sort | uniq -c | sort -rn | head -5`
- [ ] Review each file; refactor or suppress
- [ ] Verify: <50 block-scoped-var remaining

---

## Batch 4: Dangerous Fixes (15 min)

### Python: Unsafe Ruff Fixes
- [ ] Run: `cd /repo && ruff check --fix --unsafe-fixes src/ tests/`
- [ ] Run tests: `pytest tests/ -x 2>&1 | tail -20`
- [ ] Verify: All tests pass

### Frontend: Dangerous Oxlint Fixes
- [ ] Run: `cd frontend && bunx oxlint --fix-dangerously --tsconfig=tsconfig.json .`
- [ ] Run tests: `cd frontend && bun test 2>&1 | tail -20`
- [ ] Verify: All tests pass

---

## Batch 5: Verification (15 min)

### Python: Quality Check
- [ ] Run: `make quality-python`
- [ ] Verify: All checks pass (Ruff, Mypy, Pytest)

### Frontend: Quality Check
- [ ] Run: `make quality-frontend`
- [ ] Verify: Zero warnings

### CI Enforcement
- [ ] Add `quality-python` to CI pipeline
- [ ] Add `quality-frontend` to CI pipeline
- [ ] Verify: Both run on every commit

---

## Success Criteria

✅ All checkboxes above completed  
✅ `make quality-python` passes  
✅ `make quality-frontend` passes  
✅ All tests pass (Python + Frontend)  
✅ CI enforces both checks

---

## Rollback Plan

If issues arise:
1. Revert last commit: `git revert HEAD`
2. Review specific file: `git diff HEAD~1 <file>`
3. Fix manually or suppress with `// eslint-disable-line` or `# noqa`
4. Re-run checks

