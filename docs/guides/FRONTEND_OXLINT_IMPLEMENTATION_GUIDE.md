# Frontend Oxlint Implementation Guide

**Quick Start:** Follow phases 1–5 below to remediate 2,122 oxlint issues.

---

## Phase 1: Create .eslintignore (5 min)

**File:** `frontend/.eslintignore`

```
# Generated/minified code
apps/storybook/storybook-static/
.next/
dist/
build/
*.min.js
node_modules/
.turbo/
coverage/
```

**Verify:**
```bash
cd frontend && bunx oxlint . --ignore-path=.eslintignore 2>&1 | tail -5
```

Expected: ~200–300 errors (down from 2,122).

---

## Phase 2: Auto-fix Safe Issues (10 min)

**Command:**
```bash
cd frontend && bunx oxlint --fix --tsconfig=tsconfig.json .
```

**What it fixes:**
- prefer-add-event-listener (49)
- no-extend-native (35)
- require-post-message-target-origin (22)
- no-control-regex (16)
- valid-typeof (2)

**Verify:**
```bash
bunx oxlint . --ignore-path=.eslintignore 2>&1 | tail -3
```

---

## Phase 3: Manual Review (30 min)

**Top files with block-scoped-var errors:**
```bash
bunx oxlint . 2>&1 | grep "block-scoped-var" | cut -d: -f1 | sort | uniq -c | sort -rn | head -10
```

**For each file:**
1. Open in editor
2. Review variable scope issues
3. Either refactor or add `// eslint-disable-line block-scoped-var`

**Common patterns:**
- `var` in loops → change to `let`
- Variable used outside block → move declaration

---

## Phase 4: Dangerous Fixes (10 min)

**Command:**
```bash
cd frontend && bunx oxlint --fix-dangerously --tsconfig=tsconfig.json .
```

**Then verify:**
```bash
cd frontend && bun test 2>&1 | tail -20
```

---

## Phase 5: CI Enforcement (5 min)

**Add to Makefile:**
```makefile
quality-frontend:
	cd frontend && bunx oxlint --deny-warnings .

.PHONY: quality-frontend
```

**Run:**
```bash
make quality-frontend
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "File is too long" warnings | Ignore storybook-static in .eslintignore |
| Parse errors (await, export) | Check TS/JSX syntax; may need tsconfig fix |
| Too many block-scoped-var | Use `--fix-dangerously` or manual refactor |

---

## Success Criteria

✅ `bunx oxlint . --ignore-path=.eslintignore` returns 0 errors  
✅ `bun test` passes  
✅ `make quality-frontend` passes  
✅ CI enforces oxlint on every commit

