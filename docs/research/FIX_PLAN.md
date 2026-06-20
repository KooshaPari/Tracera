# Frontend Fix Plan: 0 Errors, 100% Clean/Pass

**Goal**: Achieve 0 errors across lint, typecheck, test, and build with no feature regressions. Implement partial/missing features where applicable.

## Current Status Summary

- **Lint**: ❌ Stack overflow at root, ✅ Works at app level (minor warnings)
- **Typecheck**: ❌ 50+ TypeScript errors
- **Test**: ❌ Missing test files in env-manager
- **Build**: ❌ Desktop app Tailwind CSS v4 PostCSS config error

---

## Phase 1: Critical Build Blockers (Must Fix First)

### 1.1 Fix Tailwind CSS v4 PostCSS Configuration

**Priority**: 🔴 CRITICAL - Blocks build
**Issue**: Desktop app uses Tailwind CSS v4 which requires `@tailwindcss/postcss` plugin
**Files**: `frontend/apps/desktop/postcss.config.js`
**Solution**:

```js
// Install: bun add -D @tailwindcss/postcss
// Update postcss.config.js:
export default {
  plugins: {
    '@tailwindcss/postcss': {},
    autoprefixer: {},
  },
};
```

**Dependencies**: None
**Risk**: Low - Configuration change only

---

## Phase 2: API Method Alignment (Type Errors)

### 2.1 Fix Agents API Methods

**Priority**: 🔴 HIGH - Type errors
**Issue**: `agents.ts` uses `runTask`, `getTask`, `cancelTask` but endpoints.ts has different methods
**Files**: `frontend/apps/web/src/api/agents.ts`
**Current**: Uses `agentsApi.runTask`, `agentsApi.getTask`, `agentsApi.cancelTask`
**Available in endpoints.ts**: `getNextTask`, `submitTaskResult`, `submitTaskError`, `assignTask`
**Solution Options**:

- **Option A**: Add missing methods to `agentsApi` in `endpoints.ts`
  - `runTask`: Could map to `assignTask` + `submitTaskResult`
  - `getTask`: Could map to `getNextTask`
  - `cancelTask`: Could map to `submitTaskError` with cancel status
- **Option B**: Update `agents.ts` to use existing methods
  **Recommendation**: Option A - Implement missing methods to maintain API compatibility
  **Dependencies**: None
  **Risk**: Medium - Need to verify feature parity

### 2.2 Fix Graph API Methods

**Priority**: 🔴 HIGH - Type errors
**Issue**: `graph.ts` uses `get()`, `analyzeImpact()`, `analyzeDependencies()` but endpoints.ts has different names
**Files**: `frontend/apps/web/src/api/graph.ts`
**Current**:

- `graphApi.get` ❌ (doesn't exist)
- `graphApi.analyzeImpact` ❌ (should be `getImpactAnalysis`)
- `graphApi.analyzeDependencies` ❌ (should be `getDependencyAnalysis`)
  **Available in endpoints.ts**:
- `getFullGraph()`, `getAncestors()`, `getDescendants()` ✅
- `getImpactAnalysis()` ✅
- `getDependencyAnalysis()` ✅
  **Solution**:
- Add `get()` method to `graphApi` that calls `getFullGraph()` or make it an alias
- Update `graph.ts` to use `getImpactAnalysis` and `getDependencyAnalysis`
  **Dependencies**: None
  **Risk**: Low - Simple method mapping

### 2.3 Fix Reports API Methods

**Priority**: 🔴 HIGH - Type errors
**Issue**: `reports.ts` uses `exportProject`, `importProject` but endpoints.ts has `export`, `import`
**Files**: `frontend/apps/web/src/api/reports.ts`
**Current**: `exportImportApi.exportProject`, `exportImportApi.importProject` ❌
**Available in endpoints.ts**: `exportImportApi.export`, `exportImportApi.import` ✅
**Solution**:

- Add `exportProject` and `importProject` as aliases/wrappers in `endpoints.ts`, OR
- Update `reports.ts` to use `export` and `import` directly
  **Recommendation**: Add wrapper methods to maintain API naming consistency
  **Dependencies**: None
  **Risk**: Low - Simple wrapper methods

### 2.4 Fix Impact API Methods

**Priority**: 🔴 HIGH - Type errors
**Issue**: `impact.ts` uses `analyzeImpact`, `analyzeDependencies` but should use `getImpactAnalysis`, `getDependencyAnalysis`
**Files**: `frontend/apps/web/src/api/impact.ts`
**Solution**: Update to use correct method names from `graphApi`
**Dependencies**: 2.2 (Graph API fixes)
**Risk**: Low - Simple rename

### 2.5 Fix Search API Return Type

**Priority**: 🔴 HIGH - Type error
**Issue**: `search.ts` returns `SearchResult` but should return `SearchResult[]`
**Files**: `frontend/apps/web/src/api/search.ts`
**Solution**: Fix return type annotation
**Dependencies**: None
**Risk**: Low - Type fix only

### 2.6 Remove Unused Imports

**Priority**: 🟡 MEDIUM - Type warnings
**Issue**: `handleApiResponse` imported but unused in several files
**Files**:

- `frontend/apps/web/src/api/events.ts`
- `frontend/apps/web/src/api/matrix.ts`
- `frontend/apps/web/src/api/settings.ts`
- `frontend/apps/web/src/api/system.ts`
  **Solution**: Remove unused imports
  **Dependencies**: None
  **Risk**: None - Cleanup only

---

## Phase 3: Missing UI Components

### 3.1 Create/Locate Missing UI Components

**Priority**: 🔴 HIGH - Type errors
**Issue**: Missing components referenced in `enterprise-table.tsx`:

- `@/components/ui/table`
- `@/components/ui/dropdown-menu`
- `@/components/ui/input`
- `@/components/ui/badge`
- `@/components/ui/checkbox`
  **Files**: `frontend/apps/web/src/components/ui/enterprise-table.tsx`
  **Solution Options**:
- **Option A**: Check if components exist in `@tracertm/ui` package and import from there
- **Option B**: Create missing components (shadcn/ui style)
- **Option C**: Check if they're in a different location
  **Action**: First search codebase for existing components, then create if missing
  **Dependencies**: None
  **Risk**: Medium - May need to create components

---

## Phase 4: Router and Navigation Fixes

### 4.1 Fix App.tsx Router

**Priority**: 🔴 HIGH - Type error
**Issue**: `App.tsx` imports `react-router-dom` but project uses `@tanstack/react-router`
**Files**: `frontend/apps/web/src/App.tsx`
**Solution**:

- Check if `App.tsx` is legacy/unused (many routes use `@tanstack/react-router`)
- If unused: Remove or mark as legacy
- If used: Migrate to `@tanstack/react-router` or remove `react-router-dom` dependency
  **Dependencies**: None
  **Risk**: Medium - Need to verify if file is actually used

### 4.2 Fix CommandPalette Navigation Types

**Priority**: 🔴 HIGH - Multiple type errors
**Issue**: `navigate()` calls use string but `@tanstack/react-router` expects typed route options
**Files**: `frontend/apps/web/src/components/CommandPalette.tsx`
**Solution**: Update `navigate()` calls to use proper typed route paths or cast appropriately
**Dependencies**: 4.1
**Risk**: Low - Type casting or route path updates

---

## Phase 5: Component Type Fixes

### 5.1 Fix Enterprise Table Types

**Priority**: 🔴 HIGH - Multiple type errors
**Issue**:

- Type-only imports not using `type` keyword (verbatimModuleSyntax)
- Table options type mismatches
- Column definition type issues
  **Files**: `frontend/apps/web/src/components/ui/enterprise-table.tsx`
  **Solution**:
- Fix imports: `import type { ColumnDef, ... }`
- Fix `pageCount` type (remove undefined or make optional in table options)
- Fix column definition types
  **Dependencies**: 3.1 (UI components)
  **Risk**: Medium - Complex type fixes

### 5.2 Fix Enterprise Button Types

**Priority**: 🟡 MEDIUM - Type errors
**Issue**:

- MotionStyle type compatibility
- ButtonGroupProps className missing
  **Files**: `frontend/apps/web/src/components/ui/enterprise-button.tsx`
  **Solution**: Fix type compatibility issues
  **Dependencies**: None
  **Risk**: Low - Type fixes

### 5.3 Fix API Docs Wrapper Types

**Priority**: 🟡 MEDIUM - Type errors
**Issue**: RedocStandaloneProps and SwaggerUIProps type compatibility with `exactOptionalPropertyTypes`
**Files**:

- `frontend/apps/web/src/components/api-docs/redoc-wrapper.tsx`
- `frontend/apps/web/src/components/api-docs/swagger-ui-wrapper.tsx`
  **Solution**: Fix optional property types (add `undefined` or make properties required)
  **Dependencies**: None
  **Risk**: Low - Type fixes

### 5.4 Fix Header Component

**Priority**: 🟡 MEDIUM - Type error
**Issue**: Missing argument in function call
**Files**: `frontend/apps/web/src/components/layout/Header.tsx`
**Solution**: Add missing argument or fix function signature
**Dependencies**: None
**Risk**: Low - Simple fix

### 5.5 Remove Unused React Imports

**Priority**: 🟢 LOW - Warnings
**Issue**: Unused `React` imports in API docs wrappers
**Files**: API docs wrapper components
**Solution**: Remove unused imports
**Dependencies**: None
**Risk**: None - Cleanup

---

## Phase 6: Test Infrastructure

### 6.1 Fix env-manager Test Script

**Priority**: 🔴 HIGH - Test failure
**Issue**: `@tracertm/env-manager` has no test files, causing test script to fail
**Files**: `frontend/packages/env-manager/package.json`
**Solution Options**:

- **Option A**: Add minimal test file (e.g., `src/index.test.ts`)
- **Option B**: Make test script conditional (check if test files exist)
- **Option C**: Update turbo.json to allow test failures for packages without tests
  **Recommendation**: Option A - Add minimal test to ensure package works
  **Dependencies**: None
  **Risk**: Low - Simple test addition

---

## Phase 7: Lint Configuration

### 7.1 Fix Biome Stack Overflow

**Priority**: 🟡 MEDIUM - Lint failure at root
**Issue**: Biome crashes with stack overflow when running at root level
**Possible Causes**:

- Large node_modules directory
- Circular configuration
- Too many files to process
- Biome version bug
  **Solution**:
- Add `biome.json` with proper ignores (node_modules, dist, coverage, etc.)
- Try running with `--max-diagnostics` limit
- Update Biome version if bug
- Consider splitting lint by package
  **Dependencies**: None
  **Risk**: Low - Configuration fix

### 7.2 Fix Coverage CSS Lint Warnings

**Priority**: 🟢 LOW - Warnings only
**Issue**: `!important` styles in generated coverage CSS files
**Files**: `frontend/apps/web/coverage/base.css`
**Solution**: Add coverage directory to Biome ignore list
**Dependencies**: 7.1
**Risk**: None - Ignore generated files

---

## Phase 8: Verification & Testing

### 8.1 Run Full Test Suite

**Priority**: 🔴 CRITICAL - Final verification
**Actions**:

- Run `bun run typecheck` - Should pass with 0 errors
- Run `bun run test` - Should pass all tests
- Run `bun run build` - Should build all packages successfully
- Run `bun run lint` - Should pass (or at least app-level should pass)
  **Dependencies**: All previous phases
  **Risk**: None - Verification only

### 8.2 Feature Regression Testing

**Priority**: 🔴 CRITICAL - Ensure no regressions
**Test Areas**:

- API methods work correctly (agents, graph, reports, impact, search)
- Navigation works (CommandPalette, routes)
- UI components render (table, buttons, forms)
- Build outputs are correct
  **Dependencies**: 8.1
  **Risk**: None - Testing only

---

## Implementation Order

1. **Phase 1** (Build blockers) - Must fix first
2. **Phase 2** (API methods) - Fixes most type errors
3. **Phase 3** (UI components) - Required for Phase 5
4. **Phase 4** (Router) - Required for navigation fixes
5. **Phase 5** (Component types) - Depends on 3 and 4
6. **Phase 6** (Tests) - Can be done in parallel
7. **Phase 7** (Lint) - Can be done in parallel
8. **Phase 8** (Verification) - Final step

---

## Risk Assessment

**High Risk** (Requires careful testing):

- API method implementations (2.1, 2.2, 2.3) - Need to verify feature parity
- UI component creation (3.1) - May affect existing functionality
- Router migration (4.1) - Could break navigation

**Medium Risk**:

- Type fixes in complex components (5.1)
- Test infrastructure changes (6.1)

**Low Risk**:

- Configuration changes (1.1, 7.1)
- Simple type fixes (2.4, 2.5, 2.6, 5.2, 5.3, 5.4, 5.5)
- Cleanup tasks (7.2)

---

## Success Criteria

✅ **0 TypeScript errors** - `bun run typecheck` passes
✅ **0 Test failures** - `bun run test` passes
✅ **0 Build errors** - `bun run build` succeeds
✅ **0 Lint errors** - `bun run lint` passes (or app-level passes)
✅ **No feature regressions** - All existing functionality works
✅ **Missing features implemented** - Partial/missing API methods implemented

---

## Estimated Effort

- **Phase 1**: 15 minutes
- **Phase 2**: 2-3 hours (API method implementation)
- **Phase 3**: 1-2 hours (component creation/location)
- **Phase 4**: 1 hour (router fixes)
- **Phase 5**: 2-3 hours (type fixes)
- **Phase 6**: 30 minutes
- **Phase 7**: 1 hour
- **Phase 8**: 1 hour (verification)

**Total**: ~8-11 hours

---

## Notes

- All fixes should maintain backward compatibility where possible
- API method implementations should match backend API contracts
- UI components should follow existing design system patterns
- Type fixes should not change runtime behavior
- Test coverage should be maintained or improved
