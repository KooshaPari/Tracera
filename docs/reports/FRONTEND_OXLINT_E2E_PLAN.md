# Frontend Oxlint: End-to-End Remediation Plan

**Status:** Plan  
**Scope:** Frontend linting with `bunx oxlint --fix` — root-cause driven, phased WBS with DAG dependencies.  
**Baseline:** 1,375 warnings + 747 errors across 1,037 files (34.9s scan).

---

## 1. Root Cause Summary

### 1.1 Oxlint Issues (2,122 total)

| Root Cause | Rule(s) | Count | Fix Strategy |
|-----------|---------|-------|--------------|
| **Minified/generated code** | block-scoped-var, no-unused-vars, consistent-function-scoping | 1,084 + 639 + 175 = 1,898 | Exclude `storybook-static/`, `.next/`, `dist/`, `build/` from linting; add `.eslintignore` patterns. |
| **DOM/event patterns** | prefer-add-event-listener, no-extend-native, require-post-message-target-origin | 49 + 35 + 22 = 106 | Auto-fix where safe; review unsafe patterns manually. |
| **Control flow issues** | no-cond-assign, no-unsafe-finally, no-func-assign | 27 + 8 + 27 = 62 | Auto-fix; some require manual refactoring. |
| **Regex/type issues** | no-control-regex, valid-typeof, no-instanceof-builtins | 16 + 2 + 1 = 19 | Auto-fix safe cases; review edge cases. |
| **Syntax/parse errors** | Unexpected token, await outside async, export modifier, etc. | 5 | Manual review; likely TS/JSX edge cases. |

### 1.2 Key Insights

- **~90% of errors** are in generated/minified code (storybook-static, .next, dist).
- **~10% in source** (apps/, packages/) — fixable with `--fix` and `--fix-dangerously`.
- **No type-aware flag** in oxlint; use `--tsconfig` for import resolution.

---

## 2. Phased WBS with DAG Dependencies

| Phase | Task | Depends On | Effort | Exit Criteria |
|-------|------|-----------|--------|---------------|
| **1** | Add `.eslintignore` for generated dirs | — | 1 task, ~5 min | Exclude storybook-static, .next, dist, build |
| **2** | Run `bunx oxlint --fix` on src/ | 1 | 1 task, ~10 min | Auto-fix safe issues; report remaining |
| **3** | Manual review & fix unsafe patterns | 2 | 2–3 tasks, ~30 min | block-scoped-var, no-cond-assign, control flow |
| **4** | Run `bunx oxlint --fix-dangerously` | 3 | 1 task, ~10 min | Apply dangerous fixes; verify no regressions |
| **5** | Verify zero errors; add CI gate | 4 | 1 task, ~5 min | `make quality-frontend` passes; CI enforces |

---

## 3. Phase 1: Add .eslintignore

**Task:** Create/update `.eslintignore` in frontend root.

```
# Generated/minified code
apps/storybook/storybook-static/
.next/
dist/
build/
*.min.js
node_modules/
```

**Exit:** `bunx oxlint . --ignore-path=.eslintignore` reports only source issues.

---

## 4. Phase 2: Auto-fix Safe Issues

**Command:**
```bash
cd frontend && bunx oxlint --fix --tsconfig=tsconfig.json .
```

**Expected:** ~500–700 issues auto-fixed (prefer-add-event-listener, no-extend-native, etc.).

---

## 5. Phase 3: Manual Review

**Focus:** block-scoped-var, no-cond-assign, no-unsafe-finally.  
**Approach:** Review each file; refactor or suppress with `// eslint-disable-line`.

---

## 6. Phase 4: Dangerous Fixes

**Command:**
```bash
cd frontend && bunx oxlint --fix-dangerously --tsconfig=tsconfig.json .
```

**Verify:** Run tests; check for behavioral changes.

---

## 7. Phase 5: CI & Enforcement

**Add to Makefile:**
```bash
quality-frontend:
	cd frontend && bunx oxlint --deny-warnings .
```

**Exit:** All tests pass; CI enforces zero warnings.

---

## Quick Reference

| Step | Command | Time |
|------|---------|------|
| 1 | Create `.eslintignore` | 5 min |
| 2 | `bunx oxlint --fix .` | 10 min |
| 3 | Manual review (3–5 files) | 30 min |
| 4 | `bunx oxlint --fix-dangerously .` | 10 min |
| 5 | Run tests + CI | 15 min |
| **Total** | | **~70 min** |

