# Strict Linting Policy - Rule Justifications

## Philosophy

**Default**: All rules are ENABLED and set to ERROR unless there's a legitimate technical or architectural reason to disable.

**Approach**: Fix the code, not the rules. Only disable rules when:

1. The rule conflicts with established project architecture
2. The rule is objectively incorrect for the use case
3. Fixing would require unreasonable refactoring with no tangible benefit
4. The rule is experimental/unstable

---

## Rules Analysis - Keep vs. Disable

### ✅ KEEP STRICT (Must Fix Code)

#### Type Safety (14,990 violations) - ALL KEEP

| Rule                                              | Count | Justification                                                    |
| ------------------------------------------------- | ----- | ---------------------------------------------------------------- |
| `typescript-eslint/no-unsafe-member-access`       | 2,915 | **CRITICAL** - Prevents runtime errors from undefined properties |
| `typescript-eslint/no-unsafe-call`                | 2,090 | **CRITICAL** - Prevents calling non-functions                    |
| `typescript-eslint/no-unsafe-assignment`          | 1,844 | **CRITICAL** - Type safety fundamental                           |
| `typescript-eslint/strict-boolean-expressions`    | 2,149 | **IMPORTANT** - Prevents falsy bugs (`0`, `""`, `null`)          |
| `typescript-eslint/prefer-nullish-coalescing`     | 1,176 | **AUTO-FIX** - Use `??` instead of `\|\|`                        |
| `typescript-eslint/explicit-function-return-type` | 1,452 | **KEEP** - Documentation & type inference                        |
| `typescript-eslint/no-confusing-void-expression`  | 873   | **KEEP** - Clarifies intent                                      |
| `typescript-eslint/promise-function-async`        | 461   | **KEEP** - Consistency                                           |

**Action**: Fix all 14,990 violations. These are real type safety issues.

#### React Hooks (41 violations) - ALL KEEP

| Rule                         | Count | Justification                                        |
| ---------------------------- | ----- | ---------------------------------------------------- |
| `react-hooks/rules-of-hooks` | ~40   | **CRITICAL** - Hooks must follow rules or app breaks |

**Action**: Fix hook violations immediately.

#### Async/Await Safety (483 violations) - DISABLE SELECTIVELY

| Rule                 | Count | Decision                                                |
| -------------------- | ----- | ------------------------------------------------------- |
| `oxc/no-async-await` | 483   | **DISABLE** - Modern JS standard, no reason to restrict |

---

### 🔄 ADJUST (Change Severity or Config)

#### React Performance (2,168 violations) - WARN, NOT ERROR

| Rule                                     | Count | Justification                                      |
| ---------------------------------------- | ----- | -------------------------------------------------- |
| `react-perf/jsx-no-new-function-as-prop` | 1,179 | **WARN** - Performance issue, but not breaking     |
| `react-perf/jsx-no-new-object-as-prop`   | 545   | **WARN** - Can cause re-renders, fixable over time |
| `react-perf/jsx-no-new-array-as-prop`    | 387   | **WARN** - Same as above                           |

**Action**: Keep as warnings, fix during refactors.

#### JSX Depth (6,844 violations) - ADJUST LIMIT

| Rule                  | Count | Decision                                                             |
| --------------------- | ----- | -------------------------------------------------------------------- |
| `react/jsx-max-depth` | 6,844 | **ADJUST** - Set limit to 8 instead of 5. Complex components happen. |

**Action**: Configure `{ "max": 8 }`, fix egregious violations (>10 depth).

#### Magic Numbers (4,251 violations) - DISABLE WITH EXCEPTIONS

| Rule                      | Count | Decision                                                            |
| ------------------------- | ----- | ------------------------------------------------------------------- |
| `eslint/no-magic-numbers` | 4,251 | **DISABLE GLOBALLY** - Too noisy. Enable only for critical modules. |

**Justification**:

- Config values (port 3000, timeouts) are self-documenting
- Array indices (0, 1) don't need constants
- React props (default values) are clear in context

**Action**: Disable globally, enable for business logic modules only.

---

### ❌ DISABLE (Stylistic or Anti-Pattern for Project)

#### Import/Export Style (4,567 violations) - ARCHITECTURAL CHOICE

| Rule                           | Count | Decision    | Justification                             |
| ------------------------------ | ----- | ----------- | ----------------------------------------- |
| `import/no-named-export`       | 2,035 | **DISABLE** | Project uses named exports (tree-shaking) |
| `import/group-exports`         | 1,340 | **DISABLE** | Not required for project style            |
| `import/exports-last`          | 523   | **DISABLE** | Conflicts with component structure        |
| `import/prefer-default-export` | ~200  | **DISABLE** | Contradicts no-named-export               |

**Justification**:

- Named exports enable better tree-shaking
- IDE auto-import works better with named exports
- Consistency with established codebase pattern

#### Code Style (9,088 violations) - SUBJECTIVE PREFERENCES

| Rule                            | Count | Decision    | Justification                            |
| ------------------------------- | ----- | ----------- | ---------------------------------------- |
| `eslint/id-length`              | 1,835 | **DISABLE** | `i`, `x`, `y` are universally understood |
| `eslint/no-ternary`             | 1,553 | **DISABLE** | Ternaries are idiomatic JavaScript       |
| `eslint/func-style`             | 1,494 | **DISABLE** | Both `function` and `=>` are valid       |
| `eslint/sort-keys`              | 729   | **DISABLE** | Logical grouping > alphabetical          |
| `eslint/sort-imports`           | 823   | **DISABLE** | Manual organization preferred            |
| `eslint/max-lines-per-function` | 543   | **DISABLE** | Component complexity varies              |
| `eslint/max-statements`         | 382   | **DISABLE** | Same as above                            |
| `eslint/no-undefined`           | 704   | **DISABLE** | `undefined` is valid JavaScript          |

**Justification**: These are style preferences with no technical benefit.

#### Experimental JS Features (1,769 violations) - MODERN STANDARDS

| Rule                            | Count | Decision    | Justification                     |
| ------------------------------- | ----- | ----------- | --------------------------------- |
| `oxc/no-optional-chaining`      | 1,063 | **DISABLE** | ES2020 standard, prevents crashes |
| `oxc/no-rest-spread-properties` | 703   | **DISABLE** | ES2018 standard, idiomatic        |

**Justification**: These are modern JS features supported everywhere.

#### Unicorn Rules (803 violations) - OPINIONATED

| Rule              | Count | Decision    | Justification                          |
| ----------------- | ----- | ----------- | -------------------------------------- |
| `unicorn/no-null` | 803   | **DISABLE** | `null` is valid for API contracts, DOM |

**Justification**: Some APIs require `null` (not `undefined`).

---

## Final Rule Configuration

### Global Rules (Strict Enforcement)

```json
{
  "rules": {
    // ========================================================================
    // TYPE SAFETY - ALL ERRORS (Fix code, not rules)
    // ========================================================================
    "typescript-eslint/no-unsafe-member-access": "error",
    "typescript-eslint/no-unsafe-call": "error",
    "typescript-eslint/no-unsafe-assignment": "error",
    "typescript-eslint/no-unsafe-return": "error",
    "typescript-eslint/strict-boolean-expressions": "error",
    "typescript-eslint/prefer-nullish-coalescing": "error",
    "typescript-eslint/no-floating-promises": "error",
    "typescript-eslint/no-misused-promises": "error",

    // Type annotations - WARN (gradual enforcement)
    "typescript-eslint/explicit-function-return-type": [
      "warn",
      {
        "allowExpressions": true,
        "allowTypedFunctionExpressions": true,
        "allowHigherOrderFunctions": true
      }
    ],
    "typescript-eslint/explicit-module-boundary-types": [
      "warn",
      {
        "allowArgumentsExplicitlyTypedAsAny": true
      }
    ],

    // Void expressions - WARN
    "typescript-eslint/no-confusing-void-expression": "warn",
    "typescript-eslint/promise-function-async": "warn",

    // ========================================================================
    // REACT - ERRORS (Critical correctness)
    // ========================================================================
    "react-hooks/rules-of-hooks": "error",
    "react-hooks/exhaustive-deps": "warn",
    "react/react-in-jsx-scope": "off", // React 17+
    "react/self-closing-comp": ["error", { "component": true, "html": false }],
    "react/jsx-max-depth": ["warn", { "max": 8 }], // Adjusted from default 5
    "react/jsx-filename-extension": "off", // .tsx is standard

    // React Performance - WARN (fix during refactors)
    "react-perf/jsx-no-new-function-as-prop": "warn",
    "react-perf/jsx-no-new-object-as-prop": "warn",
    "react-perf/jsx-no-new-array-as-prop": "warn",

    // ========================================================================
    // IMPORTS - KEEP STRICT
    // ========================================================================
    "import/no-cycle": ["error", { "maxDepth": 3 }],
    "import/no-duplicates": "error",

    // Import style - DISABLE (project uses named exports)
    "import/no-named-export": "off",
    "import/prefer-default-export": "off",
    "import/group-exports": "off",
    "import/exports-last": "off",

    // ========================================================================
    // CODE CORRECTNESS - ERRORS
    // ========================================================================
    "eslint/eqeqeq": ["error", "always"],
    "eslint/no-duplicate-imports": "error",

    // ========================================================================
    // STYLE PREFERENCES - DISABLE (Subjective)
    // ========================================================================
    "eslint/sort-keys": "off",
    "eslint/sort-imports": "off",
    "eslint/id-length": "off",
    "eslint/no-ternary": "off",
    "eslint/func-style": "off",
    "eslint/no-magic-numbers": "off",
    "eslint/max-lines-per-function": "off",
    "eslint/max-statements": "off",
    "eslint/no-undefined": "off",

    // ========================================================================
    // MODERN JS - DISABLE (ES2018+ standards)
    // ========================================================================
    "oxc/no-optional-chaining": "off",
    "oxc/no-rest-spread-properties": "off",
    "oxc/no-async-await": "off",

    // ========================================================================
    // OPINIONATED - DISABLE
    // ========================================================================
    "unicorn/no-null": "off"
  }
}
```

### Override: Test Files (Relaxed but still type-safe)

```json
{
  "files": ["**/*.test.ts", "**/*.test.tsx", "**/*.spec.ts", "**/*.spec.tsx"],
  "rules": {
    "typescript-eslint/no-explicit-any": "off", // Mocking needs any
    "typescript-eslint/no-unsafe-assignment": "off", // Test setup
    "typescript-eslint/no-unsafe-member-access": "off", // Test assertions
    "eslint/no-magic-numbers": "off", // Test data
    "eslint/max-lines-per-function": "off" // Long test suites OK
  }
}
```

---

## Expected Results

### Current: 53,469 violations

- 48,422 warnings
- 5,047 errors

### After Configuration: ~15,000 violations (72% reduction)

- Type safety: 14,990 (ALL MUST FIX)
- React perf: 2,168 (warn, gradual fix)
- React hooks: 41 (CRITICAL - fix immediately)

### Violations Eliminated by Disabling Subjective Rules: ~38,000

- Style preferences: 9,088
- Import style: 4,567
- Modern JS restrictions: 1,769
- JSX depth (adjusted limit): ~6,300
- Magic numbers: 4,251
- Other stylistic: ~12,000

---

## Implementation Priority

### Week 1: Critical Fixes

1. **React Hooks violations** (41) - IMMEDIATE
2. **no-unsafe-call** (2,090) - Type functions properly
3. **no-unsafe-assignment** (1,844) - Add explicit types

### Week 2-3: Type Safety

4. **no-unsafe-member-access** (2,915) - Add type guards
5. **strict-boolean-expressions** (2,149) - Explicit checks
6. **prefer-nullish-coalescing** (1,176) - Auto-fix with ESLint

### Week 4+: Gradual Improvement

7. **explicit-function-return-type** (1,452) - Add return types
8. **React performance warnings** (2,168) - useCallback/useMemo
9. **Other warnings** - Fix during normal development

---

## Automation Scripts

### 1. Auto-fix Nullish Coalescing

```bash
bunx eslint apps/web/src --fix --rule 'typescript-eslint/prefer-nullish-coalescing: error'
```

### 2. Find Critical Type Safety Issues

```bash
bunx oxlint --type-aware apps/web/src \
  --filter "typescript-eslint/no-unsafe-" \
  --format=json > critical-type-issues.json
```

### 3. Generate Type Annotation TODOs

```bash
bunx ts-add-return-types apps/web/src/**/*.tsx
```

---

## Success Metrics

✅ **Zero** type-unsafe operations (`no-unsafe-*`)
✅ **Zero** React hooks violations
✅ < 500 warnings (mostly React perf, being fixed incrementally)
✅ All new code passes strict checks
✅ CI enforces rules (no new violations)
