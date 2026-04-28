# TypeScript Error Quick Fix Guide

**Status:** 70 errors to fix
**Target:** 0 errors with `bun run typecheck`
**Estimated Time:** 2.5 hours

---

## Top 5 Fixes (Account for 65% of errors)

### Fix 1: Property Naming (28 errors - 40%)
**Impact:** HIGHEST - Blocks all type checking

```bash
# In src/views/*.tsx files, replace:
created_at → createdAt
updated_at → updatedAt
project_id → projectId
```

**Files to update:**
- [ ] src/views/ProjectDetailView.tsx (8 errors)
- [ ] src/views/ProjectsListView.tsx (6 errors)
- [ ] src/views/ItemsTableView.tsx (6 errors)
- [ ] src/views/ItemDetailView.tsx (2 errors)

**Time:** 30 min

---

### Fix 2: Checkbox Component Props (9 errors - 13%)
**Impact:** HIGH - Component unusable

**Change:**
```typescript
// OLD
<Checkbox
  checked={checked}
  onCheckedChange={(checked) => handleChange(checked)}
/>

// NEW
<Checkbox
  checked={checked}
  onChange={(e) => handleChange(e.target.checked)}
/>
```

**Files to update:**
- [ ] src/views/ItemsTableView.tsx (lines 410, 452)
- [ ] src/views/SettingsView.tsx (lines 228, 249, 267)

**Time:** 15 min

---

### Fix 3: Unused Imports/Variables (19 errors - 27%)
**Impact:** MEDIUM - Code cleanliness

**Quick command:**
```bash
cd frontend/apps/web
bun run lint:fix  # Auto-removes unused imports
```

Or manually remove from:
- [ ] src/components/CommandPalette.tsx (BookOpen, Cloud)
- [ ] src/routes/matrix.index.tsx (redirect)
- [ ] src/views/DashboardView.tsx (FileText, Lightbulb, useItems, currentProject)
- [ ] src/views/ProjectDetailView.tsx (AlertCircle, Users, projectId, count, completed)
- [ ] src/views/ProjectsListView.tsx (DialogContent, DialogHeader, DialogTitle, useItems, useDeleteProject)

**Time:** 5 min (with eslint --fix)

---

### Fix 4: ItemStatus Enum (3 errors - 4%)
**Impact:** MEDIUM - Logic error

**Options:**
1. Check if `"closed"` should be in ItemStatus enum in `/types/index.ts`
2. Or change comparison to valid status value

**Files to update:**
- [ ] src/views/ProjectDetailView.tsx (lines 231, 275, 424)

**Time:** 10 min

---

### Fix 5: Miscellaneous (11 errors - 16%)
**Impact:** LOW-MEDIUM

1. **Settings API (2 errors)** - src/api/settings.ts
   - Add `| undefined` to optional property types OR only set defined properties

2. **Missing Project.metadata (2 errors)** - src/views/ProjectDetailView.tsx
   - Add metadata property to Project type OR remove property access

3. **Unused variables (2 errors)** - src/views/DashboardView.tsx, ProjectDetailView.tsx
   - Remove unused variables

4. **Missing imports (1 error)** - src/views/ProjectsListView.tsx
   - Import Folder icon: `import { Folder } from 'lucide-react'`

5. **Operator precedence (1 error)** - src/views/DashboardView.tsx
   - Change: `value ?? fallback || defaultValue` → `(value ?? fallback) || defaultValue`

6. **Type conversion (1 error)** - src/views/GraphView.tsx
   - Convert number to string: `String(123)`

**Time:** 15 min

---

## Step-by-Step Execution Plan

### Step 1: Identify Type Definitions (5 min)

```bash
cd /Users/kooshapari/temp-PRODVERCEL/485/kush/trace/frontend
find . -name "index.ts" -path "*/types/*" | head -5
```

Check for:
- [ ] Item type definition (should have `createdAt`, `projectId`)
- [ ] Project type definition (should have `createdAt`, `updatedAt`, `metadata`)
- [ ] ItemStatus enum values (should include all valid statuses)

### Step 2: Fix Type Definitions (10 min)

Update `/types/index.ts` or relevant type files:

```typescript
// Item type - should be camelCase
export interface Item {
  id: string;
  projectId: string;      // NOT project_id
  createdAt: string;      // NOT created_at
  updatedAt: string;      // NOT updated_at
  // ... other properties
}

// Project type
export interface Project {
  id: string;
  createdAt: string;      // NOT created_at
  updatedAt: string;      // NOT updated_at
  metadata?: object;      // Add if missing
  // ... other properties
}

// ItemStatus enum - add missing values
export type ItemStatus = 'open' | 'closed' | 'in_progress' | 'done';
```

### Step 3: Run Find/Replace in Views (20 min)

**Use IDE find/replace with regex:**

```
Search: created_at
Replace: createdAt
Scope: src/views/**/*.tsx

Search: updated_at
Replace: updatedAt
Scope: src/views/**/*.tsx

Search: project_id
Replace: projectId
Scope: src/views/**/*.tsx
```

### Step 4: Fix Checkbox Components (15 min)

In ItemsTableView.tsx (lines 410, 452):
```typescript
// OLD
<Checkbox
  checked={isChecked}
  onCheckedChange={toggleRow}
/>

// NEW
<Checkbox
  checked={isChecked}
  onChange={(e) => toggleRow(e.target.checked)}
/>
```

In SettingsView.tsx (lines 228, 249, 267): Same fix

### Step 5: Auto-Fix Unused Imports (5 min)

```bash
cd /Users/kooshapari/temp-PRODVERCEL/485/kush/trace/frontend/apps/web
bun run lint:fix
```

### Step 6: Fix Miscellaneous Issues (10 min)

**DashboardView.tsx line 454:**
```typescript
// OLD
value ?? fallback || defaultValue

// NEW
(value ?? fallback) || defaultValue
```

**GraphView.tsx line 151:**
```typescript
// OLD
nodeSingular.style('property') = 123

// NEW
nodeSingular.style('property') = String(123)
```

**ProjectsListView.tsx line 445:**
```typescript
// Add import
import { Folder } from 'lucide-react'
```

### Step 7: Validate (5 min)

```bash
cd /Users/kooshapari/temp-PRODVERCEL/485/kush/trace/frontend
bun run typecheck
# Expected: 0 errors, all packages pass
```

### Step 8: Run Full Quality Checks (10 min)

```bash
cd /Users/kooshapari/temp-PRODVERCEL/485/kush/trace/frontend/apps/web
bun run lint
bun run test:run
```

### Step 9: Commit Changes (5 min)

```bash
git add .
git commit -m "fix: resolve 70 TypeScript type errors in @tracertm/web

- Standardize property naming: created_at → createdAt, updated_at → updatedAt
- Fix checkbox component props: onCheckedChange → onChange
- Add missing metadata property to Project type
- Update ItemStatus enum with all valid values
- Remove unused imports and variables
- Fix operator precedence and type conversions"
```

---

## Validation Checklist

Before considering done:

- [ ] TypeCheck passes: `bun run typecheck` → 0 errors
- [ ] Linting passes: `bun run lint` → 0 warnings/errors
- [ ] Tests pass: `bun run test:run` → all passing
- [ ] No new unused imports
- [ ] All property names consistent (camelCase)
- [ ] Checkbox components working correctly
- [ ] Status comparisons using enum values
- [ ] All missing imports resolved
- [ ] Committed and pushed to git

---

## Time Breakdown

| Phase | Duration | Tasks |
|-------|----------|-------|
| Analysis | 5 min | Identify type definitions |
| Type Updates | 10 min | Standardize naming in types |
| View Updates | 20 min | Find/replace in 4 files |
| Component Fix | 15 min | Update 5 Checkbox components |
| Auto-fix | 5 min | Run eslint --fix |
| Misc Fixes | 10 min | Handle 6 individual issues |
| Validation | 5 min | Run full typecheck suite |
| Testing | 10 min | Run linter + tests |
| Commit | 5 min | Git commit and push |
| **TOTAL** | **2.5 hours** | |

---

## Key Files to Edit

1. **/types/index.ts** or **/types/Item.ts** - Type definitions (update naming)
2. **src/views/ProjectDetailView.tsx** - 14 errors (property names, status, metadata)
3. **src/views/ProjectsListView.tsx** - 12 errors (property names, imports)
4. **src/views/ItemsTableView.tsx** - 9 errors (property names, checkbox props)
5. **src/views/SettingsView.tsx** - 6 errors (checkbox props)
6. **src/api/settings.ts** - 2 errors (optional property types)
7. **src/views/DashboardView.tsx** - 5 errors (unused, operators)
8. **src/views/GraphView.tsx** - 1 error (type conversion)

---

## Prevention Strategy

### Add to tsconfig.json:
```json
{
  "compilerOptions": {
    "strict": true,
    "exactOptionalPropertyTypes": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noImplicitAny": true,
    "noImplicitThis": true,
    "strictNullChecks": true,
    "strictFunctionTypes": true,
    "strictBindCallApply": true,
    "strictPropertyInitialization": true
  }
}
```

### Add to ESLint:
```json
{
  "rules": {
    "@typescript-eslint/no-unused-vars": ["error", { "argsIgnorePattern": "^_" }],
    "@typescript-eslint/explicit-function-return-types": "error"
  }
}
```

### Pre-commit hook:
```bash
#!/bin/bash
npm run typecheck || exit 1
npm run lint || exit 1
```

---

## Questions & Answers

**Q: Should I use snake_case or camelCase?**
A: Use camelCase - it's the JavaScript/TypeScript convention and matches the type definitions.

**Q: Can I just ignore these errors?**
A: No - strict TypeScript settings prevent compilation. These must be fixed.

**Q: Why is property naming the biggest issue?**
A: It accounts for 40% of errors and breaks the type system's ability to validate code.

**Q: How can I prevent this in the future?**
A: Use strict TypeScript settings and run typecheck in pre-commit hooks.

---

## Support

**Need help?**
- Check the detailed error report: `/trace/TYPESCRIPT_ERROR_REPORT.md`
- Review individual error details: `/trace/TYPESCRIPT_ERRORS.json`
- Run validation after each fix phase

