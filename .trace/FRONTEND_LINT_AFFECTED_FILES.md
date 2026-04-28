# Frontend Linting - Affected Files List

**Report Date:** 2026-01-23
**Total Files Affected:** 65 files
**Total Violations:** 125
**Average Violations per File:** 1.9

---

## File Count by Category

| Category | Count | Percentage |
|----------|-------|-----------|
| Test Files (__tests__) | 50 | 77% |
| Source Components | 8 | 12% |
| Tools/Utilities | 4 | 6% |
| Routes | 2 | 3% |
| Views | 1 | 2% |

---

## Test Files (50 files, 80+ violations)

These files contain unused test utilities and mock function parameters.

### API Tests (7 files)
```
apps/web/src/__tests__/api/queries.test.ts
apps/web/src/__tests__/api/reports.test.ts
apps/web/src/__tests__/api/websocket.test.ts
apps/web/src/__tests__/api/websocket.comprehensive.test.ts
```

### Component Tests (6 files)
```
apps/web/src/__tests__/components/CreateItemForm.test.tsx
apps/web/src/__tests__/components/CreateLinkForm.test.tsx
apps/web/src/__tests__/components/EmptyState.test.tsx
apps/web/src/__tests__/components/ErrorBoundary.test.tsx
apps/web/src/__tests__/components/layout/Header.test.tsx
apps/web/src/__tests__/components/LoadingSpinner.test.tsx
```

### Accessibility Tests (3 files)
```
apps/web/src/__tests__/a11y/components.test.tsx
apps/web/src/__tests__/a11y/navigation.test.tsx
apps/web/src/__tests__/a11y/pages.test.tsx
```

### Hook Tests (7 files)
```
apps/web/src/__tests__/hooks/useLocalStorage.test.ts
apps/web/src/__tests__/hooks/useSearch.test.ts
apps/web/src/__tests__/hooks/useSearch.comprehensive.test.ts
apps/web/src/__tests__/hooks/useWebSocketHook.test.ts
```

### Integration Tests (2 files)
```
apps/web/src/__tests__/integration/app-integration.test.tsx
apps/web/src/__tests__/integration/search-flow.test.tsx
```

### Page Tests (6 files)
```
apps/web/src/__tests__/pages/Dashboard.test.tsx
apps/web/src/__tests__/pages/Items.test.tsx
apps/web/src/__tests__/pages/ProjectDetail.test.tsx
apps/web/src/__tests__/pages/ProjectsList.test.tsx
apps/web/src/__tests__/pages/Search.test.tsx
apps/web/src/__tests__/pages/Settings.test.tsx
```

### Route Tests (8 files)
```
apps/web/src/__tests__/routes/projects.$projectId.views.api.test.tsx
apps/web/src/__tests__/routes/projects.$projectId.views.code.test.tsx
apps/web/src/__tests__/routes/projects.$projectId.views.database.test.tsx
apps/web/src/__tests__/routes/projects.$projectId.views.deployment.test.tsx
apps/web/src/__tests__/routes/projects.$projectId.views.documentation.test.tsx
apps/web/src/__tests__/routes/projects.$projectId.views.feature.test.tsx
apps/web/src/__tests__/routes/projects.$projectId.views.test.test.tsx
apps/web/src/__tests__/routes/projects.$projectId.views.wireframe.test.tsx
```

### Security Tests (5 files)
```
apps/web/src/__tests__/security/auth.test.tsx
apps/web/src/__tests__/security/csp.test.ts
apps/web/src/__tests__/security/headers.test.ts
apps/web/src/__tests__/security/input-validation.test.tsx
apps/web/src/__tests__/security/xss.test.tsx
```

### Store Tests (3 files)
```
apps/web/src/__tests__/stores/authStore.test.ts
apps/web/src/__tests__/stores/itemsStore.comprehensive.test.ts
apps/web/src/__tests__/stores/websocketStore.test.ts
```

### View Tests (6 files)
```
apps/web/src/__tests__/views/EventsTimelineView.test.tsx
apps/web/src/__tests__/views/ExportView.test.tsx
apps/web/src/__tests__/views/ImpactAnalysisView.test.tsx
apps/web/src/__tests__/views/ItemsTableView.comprehensive.test.tsx
apps/web/src/__tests__/views/ProjectDetailView.comprehensive.test.tsx
apps/web/src/__tests__/views/TraceabilityMatrixView.test.tsx
```

### Test Setup Files (2 files)
```
apps/web/src/__tests__/setup.ts
apps/web/src/__tests__/test-env.ts
```

---

## Source Code Files (15 files, 40+ violations)

### Components (3 files)
```
apps/web/src/components/CommandPalette.tsx (2 violations)
  - Unused imports

apps/web/src/components/ui/enterprise-button.tsx (1 violation)
  - Unused variable
```

### API/Services (1 file)
```
apps/web/src/api/settings.ts
  - Unused variable or import
```

### Routes (2 files)
```
apps/web/src/routes/index.tsx
  - Unused imports/variables

apps/web/src/routes/matrix.index.tsx (1 violation)
  - Unused import
```

### Views (8 files)
```
apps/web/src/views/DashboardView.tsx
  - Unused variables

apps/web/src/views/ItemsKanbanView.tsx
  - Unused variables

apps/web/src/views/ItemsTableView.tsx
  - Unused variables

apps/web/src/views/ItemsTreeView.tsx
  - Unused variables

apps/web/src/views/ProjectDetailView.tsx
  - Unused variables

apps/web/src/views/ProjectsListView.tsx (1 violation)
  - Unused import
```

---

## Tools Files (4 files, 5+ violations)

### Storybook Generator
```
tools/storybook-generator/analyzer.ts
  - Unused Node import

tools/storybook-generator/templates/story.template.ts
  - Unused function declaration
```

### Figma Generator
```
tools/figma-generator/figma-api-client.ts (2 violations)
  - Unused style IDs in loops

tools/figma-generator/code-to-design.ts (1 violation)
  - Unused path import
```

---

## Priority Fix Order

### Phase 1: CRITICAL (0 hours needed after auto-fix)
1. **JSX Undefined Component**
   - File: TBD (search for 'Folder' usage)
   - Fix: Add import statement

### Phase 2: AUTO-FIXABLE (0.5 hours)
Run: `bun run lint:fix`

Fixes automatically:
- Most unused imports (60 violations)
- Some unused variables (40 violations)
- Code formatting

### Phase 3: MANUAL REVIEW (1.5-2 hours)
Review and test after auto-fix:
- Verify auto-fixed code logic
- Check for removed functionality
- Run test suite

### Phase 4: REMAINING MANUAL (0.5-1 hour)
Fix any issues lint:fix missed:
- Unused function parameters
- Useless fallback spreads
- New-array issues

---

## Violation Heat Map

### Files by Violation Count

**1-2 Violations:** ~45 files
- Test setup files
- Most components
- Most routes

**3-5 Violations:** ~15 files
- Some test files
- Some utilities

**5+ Violations:** ~5 files
- Comprehensive test files
- Integration tests

---

## Fix Strategy by File Type

### Test Files
**Current State:** 80+ violations
**Primary Issue:** Unused test utilities (beforeEach, vi, waitFor, etc.)

**Action:**
1. Run `lint:fix` (auto-removes most unused imports)
2. Review each test file
3. Verify test still works
4. Commit changes

**Time:** 1-2 hours for all test files

### Source Components
**Current State:** 40+ violations
**Primary Issue:** Unused variables from refactoring

**Action:**
1. Run `lint:fix`
2. Manual review of each file
3. Ensure no logic affected
4. Run component tests

**Time:** 30-45 minutes

### Tools/Utilities
**Current State:** 5+ violations
**Primary Issue:** Unused imports and variables

**Action:**
1. Run `lint:fix`
2. Verify build still works
3. Check tools still function

**Time:** 15-20 minutes

---

## Batch Processing Recommendation

### Batch 1: Auto-Fix All (5 minutes)
```bash
cd frontend
bun run lint:fix
```

Expected to fix: ~100-110 violations automatically

### Batch 2: Review Test Files (1 hour)
```bash
# Review changes to __tests__ directory
git diff apps/web/src/__tests__/
```

Expected to fix: ~80+ violations

### Batch 3: Verify Build & Tests (30 minutes)
```bash
bun run build
bun run test
```

### Batch 4: Manual Cleanup (1 hour)
```bash
# For remaining violations:
bun run lint

# Review each violation context
# Make targeted fixes
```

### Batch 5: Final Check (15 minutes)
```bash
bun run lint
bun run format
```

**Total Time:** ~3 hours

---

## Files Ready for Immediate Fix

These files are safe to run `lint:fix` on without concern:

### All Test Files (50 files)
- Lint:fix can safely remove unused test imports
- No business logic impact
- Tests may need minor updates

### All View Files (8 files)
- Mostly cosmetic fixes
- No critical logic impact

### Component Files (3 files)
- Safe to auto-fix
- May need minor review

### Tools Files (4 files)
- Safe to auto-fix
- Verify build afterward

**Action:** Safe to `lint:fix` all 65 files at once

---

## Post-Fix Verification

After running fixes, verify:

1. **Build succeeds**
   ```bash
   bun run build
   ```

2. **All tests pass**
   ```bash
   bun run test
   ```

3. **No new lint warnings**
   ```bash
   bun run lint
   ```

4. **Code formatting is correct**
   ```bash
   bun run format:check
   ```

5. **Git diff looks reasonable**
   ```bash
   git diff apps/web/src/
   ```

---

## Common Patterns by File

### Test File Pattern
```typescript
// BEFORE
import { beforeEach, describe, expect, it, vi, waitFor } from "vitest";

describe("Component", () => {
  beforeEach(() => {
    // setup
  });

  it("should work", () => {
    expect(true).toBe(true);
  });
});

// AFTER (auto-fixed)
import { describe, expect, it } from "vitest";

describe("Component", () => {
  it("should work", () => {
    expect(true).toBe(true);
  });
});
```

### Component Pattern
```typescript
// BEFORE
export function MyComponent() {
  const unused = someValue;
  return <div>Content</div>;
}

// AFTER (auto-fixed)
export function MyComponent() {
  return <div>Content</div>;
}
```

### Tools Pattern
```typescript
// BEFORE
import * as path from 'path'; // unused

for (const [id, style] of Object.entries(styles)) {
  // only style is used, id is unused
}

// AFTER (auto-fixed)
for (const [_id, style] of Object.entries(styles)) {
  // or remove id entirely
}
```

---

## File Checklist for Manual Review

Print this checklist and mark off files as you review:

```
Test Files to Review:
☐ apps/web/src/__tests__/api/queries.test.ts
☐ apps/web/src/__tests__/api/reports.test.ts
☐ apps/web/src/__tests__/api/websocket.test.ts
☐ [continue for all 50 test files]

Source Files to Review:
☐ apps/web/src/components/CommandPalette.tsx
☐ apps/web/src/routes/index.tsx
☐ apps/web/src/views/DashboardView.tsx
☐ [continue for all 15 source files]

Tools to Review:
☐ tools/storybook-generator/analyzer.ts
☐ tools/figma-generator/figma-api-client.ts
☐ [continue for all tools]
```

---

## Summary

**Total Files:** 65
**Total Violations:** 125
**Average per File:** 1.9

**By Category:**
- Test files: 50 files, 80+ violations
- Source files: 15 files, 40+ violations
- Tools: 4 files, 5+ violations

**Estimated Fix Time:** 3-4 hours
- Auto-fix: 5 minutes
- Manual review: 2-3 hours
- Testing & verification: 30-45 minutes

**Safety:** All files are safe to auto-fix
**Next Step:** Run `bun run lint:fix` and verify with tests

---

**Report Complete**
