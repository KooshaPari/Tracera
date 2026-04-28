# Frontend Linting Violations - Detailed Breakdown

**Report Date:** 2026-01-23
**Tool:** Oxlint (OXC)
**Scope:** Frontend application source code (apps/web/src)

---

## Quick Stats

- **Total Violations:** 125
- **Errors:** 0
- **Warnings:** 125
- **Files Affected:** ~60+ files
- **Fixable:** 115+ (automatic with lint:fix)

---

## Violation Categories

### Category 1: Unused Variables (115 violations)
**Percentage:** 92% of all violations
**Fixable:** YES (with lint:fix or manual removal)

#### Breakdown by Type

**A. Unused Imports (60+ violations)**
Test utilities that are imported but not used in the test.

```
beforeEach - 8 occurrences
afterEach - 4 occurrences
vi (vitest) - 12 occurrences
waitFor - 6 occurrences
fireEvent - 4 occurrences
within - 2 occurrences
act - 2 occurrences
redirect - 1 occurrence
GraphView - 1 occurrence
ItemsTableView - 1 occurrence
ProjectsListView - 1 occurrence
Users icon - 1 occurrence
And 20+ others
```

**Common Pattern:**
```typescript
// ❌ Imported but unused
import { beforeEach, describe, expect, it, vi } from "vitest";
// vi is never called

// ✅ Fixed
import { describe, expect, it } from "vitest";
```

**B. Unused Function Parameters (45+ violations)**
Mock functions and callbacks with parameters that aren't utilized.

```
size - 1 occurrence
onOpenChange - 1 occurrence
projectId - 1 occurrence
itemsTotal - 1 occurrence
count - 1 occurrence
completed - 1 occurrence
data - 2 occurrences
type - 3 occurrences
listener - 2 occurrences
event - 1 occurrence
route - 1 occurrence
_delay - 1 occurrence
fn - 1 occurrence
And 25+ others
```

**Common Pattern:**
```typescript
// ❌ Parameter not used
function setupMock(fn: () => void, delay: number) {
  return 123; // delay never used
}

// ✅ Fixed - prefix with underscore
function setupMock(fn: () => void, _delay: number) {
  return 123;
}

// ✅ Or remove if truly not needed
function setupMock(fn: () => void) {
  return 123;
}
```

**C. Unused Local Variables (10+ violations)**
Variables declared but never referenced in the code.

```
itemsArray - 1 occurrence
status - 1 occurrence
returnType - 1 occurrence
container - 3 occurrences
result - 2 occurrences
listbox - 1 occurrence
mockRef - 1 occurrence
addRecentProject - 1 occurrence
```

**Common Pattern:**
```typescript
// ❌ Variable declared but not used
const { data, result } = fetchData();
console.log(data);

// ✅ Fixed - remove unused
const { data } = fetchData();
console.log(data);
```

**D. Unused Catch Parameters (2+ violations)**
Error caught but not handled or logged.

```
error - 2 occurrences
```

**Common Pattern:**
```typescript
// ❌ Error parameter unused
try {
  doSomething();
} catch (error) {
  // error not logged or handled
}

// ✅ Fixed - either use it or prefix
try {
  doSomething();
} catch (_error) {
  // Intentionally ignored
}

// ✅ Or handle it properly
try {
  doSomething();
} catch (error) {
  console.error('Operation failed:', error);
}
```

---

### Category 2: Useless Fallback in Spread (6 violations)
**Percentage:** 5% of all violations
**Fixable:** YES (manual removal)

**Problem:** Spreading `undefined` is unnecessary and can indicate logic errors.

```typescript
// ❌ Problem - undefined spread does nothing
const result = { ...config, ...undefined, ...overrides };

// ✅ Solution - remove the undefined spread
const result = { ...config, ...overrides };
```

**Occurrence Patterns:**
- Conditional fallbacks that resolve to undefined
- Accidental undefined in spread chains
- Dead code from refactoring

**Fix Strategy:**
```typescript
// Before
const settings = {
  ...defaults,
  ...(condition ? custom : undefined),
  ...overrides
};

// After (Option 1 - conditional spread)
const settings = {
  ...defaults,
  ...(condition && custom),
  ...overrides
};

// After (Option 2 - merge utility)
const settings = merge(defaults, condition ? custom : {}, overrides);
```

---

### Category 3: New Array Misuse (2 violations)
**Percentage:** 2% of all violations
**Fixable:** YES (manual refactoring)

**Problem:** `new Array(n)` is ambiguous - could mean array of length n OR array containing n as single element.

```typescript
// ❌ Ambiguous - is this length or single element?
const arr = new Array(5);

// ✅ Clear - creating array of length 5
const arr = Array.from({ length: 5 });
const arr = [0, 1, 2, 3, 4];

// ✅ Clear - creating array with single element
const arr = [5];
```

**Occurrences:**
- Array creation with numeric argument
- Potential for off-by-one errors
- Code clarity issue

---

### Category 4: Const Comparison (1 violation)
**Percentage:** <1% of all violations
**Fixable:** YES (remove dead code)

**Problem:** Comparing constant values that will always be true/false.

```typescript
// ❌ Always true - dead code
if (true || !true) {
  // This branch always executes
}

// ✅ Remove dead logic
if (true) {
  // or just remove the condition entirely
}
```

**Issue:** Indicates incomplete refactoring or debugging code left in place.

---

### Category 5: React/JSX Issues (1 violation)
**Percentage:** <1% of all violations
**Fixable:** YES (add import)

**Problem:** 'Folder' component is referenced but not imported or defined.

```typescript
// ❌ 'Folder' is undefined
export function FileExplorer() {
  return <Folder name="root" />;
}

// ✅ Import the component
import { Folder } from '@/components/ui/icons';

export function FileExplorer() {
  return <Folder name="root" />;
}
```

**Impact:** CRITICAL - will cause runtime error
**File:** Appears in one component file
**Fix Time:** < 2 minutes

---

## Affected Files by Issue Count

### Top Files with Issues

1. **test files in `__tests__/`** (80+ violations)
   - Imported test utilities that aren't used
   - Mock functions with unused parameters
   - Several test setup issues

2. **tools/storybook-generator/** (5-10 violations)
   - `analyzer.ts` - unused Node import
   - Other generator files

3. **tools/figma-generator/** (5-10 violations)
   - `figma-api-client.ts` - unused style IDs
   - `code-to-design.ts` - unused path import

4. **Various component files** (20+ violations)
   - Refactored code with remnant imports
   - Unused function parameters in callbacks

---

## Fix Priority Matrix

### Tier 1: Critical (Fix Immediately)
```
Issue: JSX undefined component
File: 1 file
Time: < 2 min
Action: Add import statement
```

### Tier 2: High Priority (This Sprint)
```
Issue: Unused imports from test utilities
Count: 60+ occurrences
Time: 30-45 minutes
Action: Remove or comment out unused imports
Tools: bun run lint:fix (can auto-fix many)
```

### Tier 3: Medium Priority (Next Sprint)
```
Issue: Unused function parameters
Count: 45+ occurrences
Time: 1.5-2 hours
Action: Prefix with _ or remove parameters
Tools: Manual review required
```

### Tier 4: Low Priority (Polish)
```
Issue: Unused local variables
Count: 10+ occurrences
Action: Remove unused variables

Issue: Useless spread fallbacks
Count: 6 occurrences
Action: Remove undefined spreads

Issue: New-array misuse
Count: 2 occurrences
Action: Use Array.from() instead

Issue: Const comparisons
Count: 1 occurrence
Action: Remove dead code
```

---

## Automated Fix Procedure

### Step 1: Run Auto-Fix
```bash
cd /Users/kooshapari/temp-PRODVERCEL/485/kush/trace/frontend
bun run lint:fix
```

**What gets fixed automatically:**
- Most unused imports removal
- Some unused variable cleanup
- Formatting issues

**What still needs manual review:**
- Unused function parameters (requires context)
- Useless fallback spreads (logic review needed)
- Array constructor issues (refactoring required)

### Step 2: Manual Review
After auto-fix, manually handle remaining issues:

```bash
# Check what's left
bun run lint
```

### Step 3: Verify
```bash
# Run tests to ensure nothing broke
bun run test

# Final lint check
bun run lint
```

---

## File-by-File Violation List

### Format: [File] - [Issue Type] x [Count]

**Test Files (Major Contributor):**
```
__tests__/api/websocket.test.ts - no-unused-vars (2), parameters (2)
__tests__/api/queries.test.ts - no-unused-vars (1)
__tests__/api/reports.test.ts - no-unused-vars (2)
__tests__/hooks/useWebSocketHook.test.ts - no-unused-vars (1)
__tests__/lib/enterprise-optimizations.test.ts - no-unused-vars (1-2)
[~60 more test files with 1-3 violations each]
```

**Tool Files:**
```
tools/storybook-generator/analyzer.ts - no-unused-vars (1)
tools/storybook-generator/templates/story.template.ts - no-unused-vars (1)
tools/figma-generator/figma-api-client.ts - no-unused-vars (2)
tools/figma-generator/code-to-design.ts - no-unused-vars (1)
```

**Source Components:**
```
Various component files - no-unused-vars (20+)
Various hook files - no-unused-vars (10+)
Various utility files - no-unused-vars (5+)
```

---

## Prevention Strategies

### 1. Pre-Commit Linting
Add git hook to prevent commits with lint errors:

```bash
# .husky/pre-commit
bun run lint || exit 1
```

### 2. IDE Integration
Configure VSCode to auto-fix on save:

```json
// .vscode/settings.json
{
  "editor.codeActionsOnSave": {
    "source.fixAll": true
  },
  "[typescript]": {
    "editor.defaultFormatter": "biomejs.biome"
  }
}
```

### 3. PR Review Checklist
- [ ] No new lint warnings
- [ ] All imports are used
- [ ] No unused parameters (should be prefixed with _)
- [ ] `bun run lint` passes before merging

### 4. Team Training
- Explain purpose of each rule
- Show examples of violations
- Demonstrate auto-fix capabilities
- Make it part of code review process

---

## Next Steps

1. **Immediate (Today)**
   - Fix critical JSX undefined issue
   - Run `bun run lint:fix`
   - Test application

2. **Short-term (This Week)**
   - Review auto-fixed code
   - Handle remaining unused variables
   - Run full test suite

3. **Follow-up (This Sprint)**
   - Update team on findings
   - Add pre-commit linting
   - Document in team guide

4. **Long-term (Process Improvement)**
   - Add to CI/CD pipeline
   - Integrate with IDE setup
   - Regular lint reviews

---

## Tool Configuration Reference

### Biome Configuration
**Location:** `frontend/biome.json`

Current configuration uses "recommended" rule set which includes:
- Unused variable detection
- Safe practices
- Code clarity rules
- React best practices

### Available CLI Commands

```bash
# Check violations (read-only)
bun run lint

# Auto-fix issues
bun run lint:fix

# Check formatting
bun run format:check

# Apply formatting
bun run format

# Run all checks
bun run check
```

---

## Appendix: Example Fixes

### Example 1: Unused Import
```typescript
// BEFORE
import { beforeEach, describe, expect, it, vi } from "vitest";

describe("MyComponent", () => {
  it("should render", () => {
    expect(true).toBe(true);
  });
});

// AFTER
import { describe, expect, it } from "vitest";

describe("MyComponent", () => {
  it("should render", () => {
    expect(true).toBe(true);
  });
});
```

### Example 2: Unused Parameter
```typescript
// BEFORE
setInterval: vi.fn((fn: () => void, delay: number) => {
  return 123 as any;
})

// AFTER
setInterval: vi.fn((_fn: () => void, _delay?: number) => {
  return 123 as any;
})

// OR
setInterval: vi.fn(() => {
  return 123 as any;
})
```

### Example 3: Unused Variable
```typescript
// BEFORE
const { data, result } = fetchItems();
console.log(data);

// AFTER
const { data } = fetchItems();
console.log(data);
```

### Example 4: Useless Spread
```typescript
// BEFORE
const config = {
  ...defaults,
  ...(isDarkMode ? theme : undefined),
  ...userOverrides
};

// AFTER
const config = {
  ...defaults,
  ...(isDarkMode && theme),
  ...userOverrides
};
```

### Example 5: Array Constructor
```typescript
// BEFORE
const padding = new Array(4 + 1).join(" ");

// AFTER
const padding = Array.from({ length: 5 }).join(" ");
```

---

**Report Complete**
**Generated:** 2026-01-23
**Last Updated:** Current session
