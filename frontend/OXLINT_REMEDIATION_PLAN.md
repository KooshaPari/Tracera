# Oxlint Remediation Plan
## Executive Summary

**Total Issues**: 53,469 (48,422 warnings + 5,047 errors)
**Files Affected**: 776 files
**Unique Rules**: 167 rules

## Issue Breakdown by Category

| Category | Count | % |
|----------|-------|---|
| typescript-eslint | 14,990 | 28.0% |
| eslint | 14,371 | 26.9% |
| eslint-plugin-react | 7,990 | 14.9% |
| eslint-plugin-import | 4,567 | 8.5% |
| oxc | 2,252 | 4.2% |
| eslint-plugin-react-perf | 2,168 | 4.1% |
| eslint-plugin-unicorn | 1,805 | 3.4% |
| Other | 5,326 | 10.0% |

## Top 30 Rules by Violation Count

1. **6,844** - eslint-plugin-react(jsx-max-depth)
2. **4,251** - eslint(no-magic-numbers)
3. **2,915** - typescript-eslint(no-unsafe-member-access)
4. **2,149** - typescript-eslint(strict-boolean-expressions)
5. **2,090** - typescript-eslint(no-unsafe-call)
6. **2,035** - eslint-plugin-import(no-named-export)
7. **1,844** - typescript-eslint(no-unsafe-assignment)
8. **1,835** - eslint(id-length)
9. **1,553** - eslint(no-ternary)
10. **1,494** - eslint(func-style)
11. **1,452** - typescript-eslint(explicit-function-return-type)
12. **1,340** - eslint-plugin-import(group-exports)
13. **1,179** - eslint-plugin-react-perf(jsx-no-new-function-as-prop)
14. **1,176** - typescript-eslint(prefer-nullish-coalescing)
15. **1,063** - oxc(no-optional-chaining)
16. **873** - typescript-eslint(no-confusing-void-expression)
17. **823** - eslint(sort-imports)
18. **803** - eslint-plugin-unicorn(no-null)
19. **729** - eslint(sort-keys)
20. **704** - eslint(no-undefined)
21. **703** - oxc(no-rest-spread-properties)
22. **687** - typescript-eslint(explicit-module-boundary-types)
23. **545** - eslint-plugin-react-perf(jsx-no-new-object-as-prop)
24. **543** - eslint(max-lines-per-function)
25. **523** - eslint-plugin-import(exports-last)
26. **483** - oxc(no-async-await)
27. **461** - typescript-eslint(promise-function-async)
28. **439** - eslint-plugin-react(jsx-filename-extension)
29. **387** - eslint-plugin-react-perf(jsx-no-new-array-as-prop)
30. **382** - eslint(max-statements)

---

## Remediation Strategy

### Phase 1: Configuration & Rule Adjustment (Immediate)
**Goal**: Reduce noise from overly strict/opinionated rules
**Effort**: 1-2 hours
**Impact**: Eliminates ~20,000-25,000 warnings

#### 1.1 Disable Stylistic Rules (14,500 violations)
These rules are code-style preferences that don't affect correctness:

```json
{
  "rules": {
    // Style preferences - disable
    "eslint/sort-keys": "off",           // 729
    "eslint/sort-imports": "off",        // 823
    "eslint/id-length": "off",           // 1,835
    "eslint/no-ternary": "off",          // 1,553
    "eslint/func-style": "off",          // 1,494
    "eslint/no-magic-numbers": "off",    // 4,251
    "eslint/max-lines-per-function": "off", // 543
    "eslint/max-statements": "off",      // 382

    // Import style - use project conventions
    "eslint-plugin-import/no-named-export": "off",     // 2,035
    "eslint-plugin-import/group-exports": "off",       // 1,340
    "eslint-plugin-import/exports-last": "off",        // 523
    "eslint-plugin-import/prefer-default-export": "off"
  }
}
```

#### 1.2 Adjust React Rules (7,990 violations)
```json
{
  "rules": {
    // JSX depth is arbitrary - set to reasonable limit or disable
    "eslint-plugin-react/jsx-max-depth": ["warn", { "max": 10 }], // 6,844 → ~500
    "eslint-plugin-react/jsx-filename-extension": "off" // 439
  }
}
```

#### 1.3 Disable Experimental/Restrictive Features (2,798 violations)
```json
{
  "rules": {
    "oxc/no-optional-chaining": "off",        // 1,063
    "oxc/no-rest-spread-properties": "off",   // 703
    "oxc/no-async-await": "off",             // 483
    "eslint/no-undefined": "off",            // 704
    "eslint-plugin-unicorn/no-null": "off"   // 803
  }
}
```

**Phase 1 Result**: Reduces violations from **53,469 → ~28,000** (47% reduction)

---

### Phase 2: Type Safety Fixes (High Priority)
**Goal**: Fix actual type safety issues
**Effort**: 40-80 hours
**Impact**: Fixes real bugs, improves type safety

#### 2.1 Type-Unsafe Operations (8,849 errors - CRITICAL)
These are actual type safety issues that could cause runtime errors:

| Rule | Count | Action |
|------|-------|--------|
| typescript-eslint(no-unsafe-member-access) | 2,915 | Add proper typing, use type guards |
| typescript-eslint(no-unsafe-call) | 2,090 | Type function signatures properly |
| typescript-eslint(no-unsafe-assignment) | 1,844 | Add explicit types, avoid `any` |
| typescript-eslint(strict-boolean-expressions) | 2,149 | Use explicit boolean checks |

**Strategy**:
```typescript
// BEFORE (unsafe)
function process(data: any) {
  return data.value.map(x => x.id);
}

// AFTER (safe)
interface Data {
  value: Array<{ id: string }>;
}
function process(data: Data): string[] {
  return data.value.map(x => x.id);
}
```

**Automation**:
- Use TypeScript's `noImplicitAny`, `strictNullChecks`
- Create codemod to add type annotations
- Batch fix with find/replace patterns

#### 2.2 Missing Type Annotations (2,139 violations)
```json
{
  "rules": {
    "typescript-eslint/explicit-function-return-type": ["warn", {
      "allowExpressions": true,
      "allowTypedFunctionExpressions": true
    }], // 1,452 → ~200
    "typescript-eslint/explicit-module-boundary-types": ["warn", {
      "allowArgumentsExplicitlyTypedAsAny": true
    }] // 687 → ~100
  }
}
```

#### 2.3 Nullish Coalescing (1,176 violations)
```typescript
// BEFORE
const value = foo || defaultValue;

// AFTER
const value = foo ?? defaultValue;
```

**Automation**: ESLint --fix can auto-correct most of these

**Phase 2 Result**: Fixes **~8,000 critical type errors**

---

### Phase 3: React Performance Optimization (2,168 violations)
**Goal**: Fix performance anti-patterns
**Effort**: 20-40 hours
**Impact**: Improves React re-render performance

#### 3.1 Inline Function/Object Creation (2,111 violations)

| Rule | Count | Fix |
|------|-------|-----|
| jsx-no-new-function-as-prop | 1,179 | useCallback |
| jsx-no-new-object-as-prop | 545 | useMemo |
| jsx-no-new-array-as-prop | 387 | useMemo |

```typescript
// BEFORE
<Component onClick={() => doSomething()} data={{ id: 1 }} />

// AFTER
const handleClick = useCallback(() => doSomething(), []);
const data = useMemo(() => ({ id: 1 }), []);
<Component onClick={handleClick} data={data} />
```

**Automation**:
- Create codemod to wrap inline functions with `useCallback`
- Extract inline objects/arrays to `useMemo`

**Phase 3 Result**: Fixes **~2,000 performance issues**

---

### Phase 4: Promise/Async Handling (461 violations)
**Goal**: Ensure proper async patterns
**Effort**: 5-10 hours

```typescript
// typescript-eslint(promise-function-async) - 461 violations
// BEFORE
function fetchData(): Promise<Data> {
  return api.getData();
}

// AFTER
async function fetchData(): Promise<Data> {
  return await api.getData();
}
```

**Phase 4 Result**: Fixes **~460 async pattern issues**

---

### Phase 5: Void Expression Confusion (873 violations)
**Goal**: Clarify void-returning expressions
**Effort**: 10-15 hours

```typescript
// typescript-eslint(no-confusing-void-expression) - 873 violations
// BEFORE
const result = console.log('debug');

// AFTER
console.log('debug');
// OR
void console.log('debug'); // if intentionally ignoring
```

---

## Implementation Timeline

### Week 1: Quick Wins (Phase 1)
- **Day 1**: Configure oxlint rules, disable stylistic/opinionated rules
- **Day 2**: Test build, verify no regressions
- **Result**: 53,469 → ~28,000 violations

### Week 2-4: Critical Type Safety (Phase 2)
- **Week 2**: Fix no-unsafe-* violations (high risk areas first)
- **Week 3**: Add explicit type annotations
- **Week 4**: Fix strict boolean expressions, nullish coalescing
- **Result**: Fix ~8,000 critical errors

### Week 5-6: Performance (Phase 3)
- **Week 5**: Fix inline function creation with useCallback
- **Week 6**: Fix inline object/array creation with useMemo
- **Result**: Fix ~2,000 performance issues

### Week 7: Cleanup (Phases 4-5)
- **Day 1-2**: Fix async/promise patterns
- **Day 3-4**: Fix void expression confusion
- **Day 5**: Final review and verification
- **Result**: Fix remaining ~1,300 issues

---

## Automation Tools

### 1. Custom Codemod (jscodeshift)
```javascript
// Transform inline functions to useCallback
module.exports = function transformer(file, api) {
  const j = api.jscodeshift;
  const root = j(file.source);

  // Find JSX attributes with arrow functions
  root.find(j.JSXAttribute)
    .filter(path => {
      return j.ArrowFunctionExpression.check(path.value.value?.expression);
    })
    .forEach(path => {
      // Wrap with useCallback...
    });

  return root.toSource();
};
```

### 2. Batch Type Annotation Script
```bash
#!/bin/bash
# Add return types to functions missing them
bunx ts-add-return-types apps/web/src/**/*.tsx
```

### 3. ESLint Auto-Fix
```bash
# Fix auto-fixable issues
bunx eslint apps/web/src --fix --rule 'typescript-eslint/prefer-nullish-coalescing: error'
```

---

## Rollout Strategy

### Incremental Approach
1. **Don't block development**: Warnings only initially
2. **Fix by directory**: Start with most critical paths (auth, API, core)
3. **Gradual error enforcement**: Enable strict rules file-by-file
4. **CI Integration**: Add oxlint to pre-commit hooks after Phase 1

### Metrics
- Track violations per week
- Target: < 5,000 remaining issues by end of Week 7
- Final goal: < 500 violations (mostly false positives)

---

## Configuration File Changes

### `.oxlintrc.json` (Create/Update)
```json
{
  "rules": {
    // Phase 1: Disable stylistic rules
    "eslint/sort-keys": "off",
    "eslint/sort-imports": "off",
    "eslint/id-length": "off",
    "eslint/no-ternary": "off",
    "eslint/func-style": "off",
    "eslint/no-magic-numbers": "off",
    "eslint/max-lines-per-function": "off",
    "eslint/max-statements": "off",
    "eslint-plugin-import/no-named-export": "off",
    "eslint-plugin-import/group-exports": "off",
    "eslint-plugin-import/exports-last": "off",
    "eslint/no-undefined": "off",
    "eslint-plugin-unicorn/no-null": "off",
    "oxc/no-optional-chaining": "off",
    "oxc/no-rest-spread-properties": "off",
    "oxc/no-async-await": "off",

    // Phase 1: Adjust React rules
    "eslint-plugin-react/jsx-max-depth": ["warn", { "max": 10 }],
    "eslint-plugin-react/jsx-filename-extension": "off",

    // Phase 2: Keep type safety (errors)
    "typescript-eslint/no-unsafe-member-access": "error",
    "typescript-eslint/no-unsafe-call": "error",
    "typescript-eslint/no-unsafe-assignment": "error",
    "typescript-eslint/strict-boolean-expressions": "error",

    // Phase 2: Warn on missing types (gradual fix)
    "typescript-eslint/explicit-function-return-type": ["warn", {
      "allowExpressions": true,
      "allowTypedFunctionExpressions": true
    }],

    // Phase 3: Warn on performance issues
    "eslint-plugin-react-perf/jsx-no-new-function-as-prop": "warn",
    "eslint-plugin-react-perf/jsx-no-new-object-as-prop": "warn",
    "eslint-plugin-react-perf/jsx-no-new-array-as-prop": "warn"
  }
}
```

---

## Expected Outcomes

### After Phase 1 (Week 1)
- **Violations**: 53,469 → ~28,000 (47% reduction)
- **Developer friction**: Minimal
- **Build time**: No change
- **Type safety**: No change

### After All Phases (Week 7)
- **Violations**: 53,469 → <5,000 (91% reduction)
- **Type safety**: Significantly improved
- **Performance**: Fewer unnecessary re-renders
- **Code quality**: More maintainable, typed codebase
- **CI time**: +30s for oxlint check

---

## Risk Mitigation

1. **Backup/Branch**: Work in feature branch `fix/oxlint-remediation`
2. **Incremental PRs**: Submit fixes in digestible chunks (< 50 files per PR)
3. **Test coverage**: Run full test suite after each phase
4. **Stakeholder communication**: Share weekly progress reports
5. **Rollback plan**: Keep configuration changes reversible

---

## Team Capacity

**Estimated effort**: 80-120 developer hours
**Timeline**: 7 weeks
**Recommended allocation**:
- 1 senior developer (lead, 60%)
- 1-2 mid-level developers (implementation, 40%)
- Code review: Distribute across team

---

## Success Criteria

✅ All type-unsafe operations fixed (Phase 2)
✅ React performance anti-patterns eliminated (Phase 3)
✅ < 5,000 total violations remaining
✅ No new violations introduced in CI
✅ Build and test suite pass
✅ Developer experience improved (fewer false positives)
