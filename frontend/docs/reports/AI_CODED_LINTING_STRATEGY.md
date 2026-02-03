# Strict Linting Strategy for AI-Coded Projects

## Philosophy

**This is an exclusively agent/AI-coded project.** Linting rules serve as **guardrails** to constrain AI behavior and prevent:
- Inconsistent code style across AI generations
- Anti-patterns that AI commonly produces
- Subtle bugs that pass tests but cause issues
- Technical debt accumulation from multiple AI iterations

## Core Principle: Enforce Strict Opinions

Unlike human-coded projects where style is subjective, **AI-coded projects benefit from strict enforcement** because:

1. **Consistency Across Agents**: Different AI sessions produce different styles without constraints
2. **Quality Gates**: AI doesn't inherently know project-specific quality standards
3. **Anti-Pattern Prevention**: AI can generate "working" code that's problematic long-term
4. **Maintainability**: Strict rules make AI-generated code more maintainable by other AI agents

---

## Rule Categories for AI Development

### 1. **Type Safety** (CRITICAL - MAXIMUM STRICTNESS)

These prevent runtime errors that AI commonly introduces:

```json
{
  "typescript/no-explicit-any": "error",
  "typescript/explicit-function-return-type": "error",
  "typescript/no-unsafe-assignment": "error",
  "typescript/no-unsafe-member-access": "error",
  "typescript/no-unsafe-call": "error",
  "typescript/no-unsafe-return": "error",
  "typescript/strict-boolean-expressions": "error",
  "typescript/no-floating-promises": "error",
  "typescript/await-thenable": "error"
}
```

**Why**: AI often:
- Uses `any` to bypass type errors quickly
- Forgets await on promises
- Creates unsafe type assertions
- Misses null/undefined cases

### 2. **Code Style Consistency** (ENFORCE STRICTLY)

Force consistent patterns across all AI-generated code:

```json
{
  "eslint/sort-imports": "error",
  "eslint/sort-keys": "error",
  "import/order": ["error", {
    "groups": [
      "builtin",
      "external",
      "internal",
      "parent",
      "sibling",
      "index"
    ],
    "alphabetize": { "order": "asc" }
  }],
  "eslint/func-style": ["error", "expression", {
    "allowArrowFunctions": true
  }]
}
```

**Why**: AI generates inconsistent import orders, function styles, and object structures without guidance.

### 3. **Naming Conventions** (ENFORCE DESCRIPTIVENESS)

Prevent AI from using ambiguous names:

```json
{
  "eslint/id-length": ["error", {
    "min": 2,
    "exceptions": ["i", "j", "x", "y", "z"],
    "properties": "never"
  }],
  "unicorn/prevent-abbreviations": ["error", {
    "allowList": {
      "props": true,
      "ref": true,
      "params": true
    }
  }]
}
```

**Why**: AI often:
- Uses single-letter variables everywhere
- Creates ambiguous abbreviations
- Produces non-descriptive names like `temp`, `data`, `obj`

### 4. **Complexity Limits** (FORCE DECOMPOSITION)

Prevent AI from generating monolithic functions:

```json
{
  "eslint/max-lines-per-function": ["error", {
    "max": 50,
    "skipBlankLines": true,
    "skipComments": true
  }],
  "eslint/max-params": ["error", 3],
  "eslint/max-depth": ["error", 3],
  "complexity": ["error", 10]
}
```

**Why**: AI tends to:
- Generate very long functions (100+ lines)
- Create functions with many parameters
- Produce deeply nested logic

### 5. **React-Specific Quality** (PREVENT PERFORMANCE ISSUES)

AI commonly creates React anti-patterns:

```json
{
  "react/jsx-max-depth": ["error", { "max": 4 }],
  "react-perf/jsx-no-new-object-as-prop": "error",
  "react-perf/jsx-no-new-array-as-prop": "error",
  "react-perf/jsx-no-new-function-as-prop": "error",
  "react/jsx-no-leaked-render": "error",
  "react-hooks/exhaustive-deps": "error"
}
```

**Why**: AI frequently:
- Creates deeply nested JSX (hard to maintain)
- Generates new objects/arrays in render (performance)
- Misses dependency arrays in hooks
- Uses inline functions as props (causes re-renders)

### 6. **Magic Numbers & Constants** (ENFORCE NAMED CONSTANTS)

Prevent mysterious values in AI-generated code:

```json
{
  "eslint/no-magic-numbers": ["error", {
    "ignore": [0, 1, -1],
    "ignoreArrayIndexes": true,
    "enforceConst": true,
    "detectObjects": false
  }]
}
```

**Why**: AI uses magic numbers without explanation:
- `if (x > 100)` - What does 100 mean?
- `timeout: 5000` - Why 5000ms?
- `maxRetries: 3` - Why 3?

Better:
```typescript
const MAX_ITEMS = 100;
const DEFAULT_TIMEOUT_MS = 5000;
const MAX_RETRY_ATTEMPTS = 3;
```

### 7. **Import/Export Patterns** (PROJECT-SPECIFIC)

Enforce consistent module patterns:

```json
{
  // Choose ONE approach and enforce it:

  // Option A: Named exports only (tree-shaking)
  "import/no-default-export": "error",
  "import/prefer-named-export": "error",

  // Option B: Default exports only
  "import/no-named-export": "error",
  "import/prefer-default-export": "error"
}
```

**Decision for TraceRTM**: Based on codebase analysis, project uses **named exports**. Enforce:

```json
{
  "import/no-default-export": "error",
  "import/prefer-named-export": "warn",
  "import/no-named-export": "off"
}
```

### 8. **Ternary & Conditionals** (SITUATIONAL)

**Current rule**: `eslint/no-ternary` is showing many violations.

**Decision**:
- ✅ **Allow ternaries** for simple cases (readability)
- ❌ **Forbid nested ternaries** (AI often creates unreadable chains)

```json
{
  "eslint/no-ternary": "off",  // Allow simple ternaries
  "unicorn/no-nested-ternary": "error",  // Forbid nesting
  "eslint/multiline-ternary": ["error", "always-multiline"]
}
```

### 9. **Circular Dependencies** (CRITICAL)

AI commonly creates import cycles:

```json
{
  "import/no-cycle": ["error", {
    "maxDepth": 3,
    "ignoreExternal": true
  }]
}
```

**Why**: AI doesn't track module relationships across sessions.

---

## Adjusted Configuration for AI-Coded Project

### `.oxlintrc.json` (Production Configuration)

```json
{
  "plugins": ["react", "unicorn", "jsx-a11y", "react-perf"],
  "rules": {
    // ========================================
    // TYPE SAFETY (MAXIMUM STRICTNESS)
    // ========================================
    "typescript/no-explicit-any": "error",
    "typescript/explicit-function-return-type": "error",
    "typescript/no-unsafe-assignment": "error",
    "typescript/no-unsafe-member-access": "error",
    "typescript/no-unsafe-call": "error",
    "typescript/no-unsafe-return": "error",
    "typescript/strict-boolean-expressions": "error",
    "typescript/no-floating-promises": "error",
    "typescript/await-thenable": "error",
    "typescript/no-misused-promises": "error",

    // ========================================
    // STYLE CONSISTENCY (ENFORCE STRICTLY)
    // ========================================
    "eslint/sort-imports": "error",
    "eslint/sort-keys": "error",
    "import/order": "error",
    "eslint/func-style": ["error", "expression"],

    // ========================================
    // NAMING (DESCRIPTIVE NAMES)
    // ========================================
    "eslint/id-length": ["error", {
      "min": 2,
      "exceptions": ["i", "j", "k", "x", "y", "z"],
      "properties": "never"
    }],
    "unicorn/prevent-abbreviations": ["warn", {
      "allowList": {
        "props": true,
        "ref": true,
        "params": true,
        "Params": true,
        "Args": true
      }
    }],

    // ========================================
    // COMPLEXITY LIMITS (FORCE DECOMPOSITION)
    // ========================================
    "eslint/max-lines-per-function": ["error", {
      "max": 50,
      "skipBlankLines": true,
      "skipComments": true
    }],
    "eslint/max-params": ["error", 3],
    "eslint/max-depth": ["error", 3],
    "complexity": ["error", 10],
    "eslint/max-nested-callbacks": ["error", 3],

    // ========================================
    // CONSTANTS & MAGIC NUMBERS
    // ========================================
    "eslint/no-magic-numbers": ["error", {
      "ignore": [0, 1, -1],
      "ignoreArrayIndexes": true,
      "enforceConst": true,
      "detectObjects": false
    }],

    // ========================================
    // REACT QUALITY & PERFORMANCE
    // ========================================
    "react/jsx-max-depth": ["error", { "max": 4 }],
    "react-perf/jsx-no-new-object-as-prop": "error",
    "react-perf/jsx-no-new-array-as-prop": "error",
    "react-perf/jsx-no-new-function-as-prop": "error",
    "react/jsx-no-leaked-render": "error",
    "react-hooks/exhaustive-deps": "error",
    "react/jsx-no-useless-fragment": "error",

    // ========================================
    // IMPORTS & CIRCULAR DEPENDENCIES
    // ========================================
    "import/no-cycle": ["error", { "maxDepth": 3 }],
    "import/no-self-import": "error",
    "import/no-useless-path-segments": "error",

    // ========================================
    // PROJECT-SPECIFIC: NAMED EXPORTS
    // ========================================
    "import/no-default-export": "warn",  // Warn (not error) due to TanStack Router
    "import/no-named-export": "off",
    "import/prefer-default-export": "off",

    // ========================================
    // CONDITIONALS (ALLOW SIMPLE TERNARIES)
    // ========================================
    "eslint/no-ternary": "off",
    "unicorn/no-nested-ternary": "error",
    "eslint/multiline-ternary": ["error", "always-multiline"],

    // ========================================
    // MODERN JS (ALLOW ES2020+)
    // ========================================
    "oxc/no-optional-chaining": "off",
    "oxc/no-rest-spread-properties": "off",
    "oxc/no-async-await": "off",

    // ========================================
    // DISABLE: TOO OPINIONATED WITHOUT VALUE
    // ========================================
    "eslint/no-inline-comments": "off",
    "eslint/line-comment-position": "off",
    "eslint/capitalized-comments": "off"
  },

  "overrides": [
    {
      // Test files: Relax some rules
      "files": ["**/*.test.ts", "**/*.test.tsx", "**/*.spec.ts", "**/*.spec.tsx"],
      "rules": {
        "eslint/max-lines-per-function": "off",
        "eslint/no-magic-numbers": "off",
        "typescript/no-explicit-any": "warn"
      }
    },
    {
      // Route files: Allow default exports (TanStack Router requirement)
      "files": ["**/routes/**/*.tsx"],
      "rules": {
        "import/no-default-export": "off"
      }
    }
  ]
}
```

---

## Implementation Priority for AI-Coded Projects

### Phase 1: Critical Type Safety (Week 1)
**Goal**: Prevent runtime errors

1. Fix all `no-explicit-any` violations (8,849)
2. Fix all `no-unsafe-*` violations
3. Add explicit return types to functions
4. Enable strict null checks

**Why first**: Type errors cause production crashes.

### Phase 2: Consistency Enforcement (Week 2)
**Goal**: Establish consistent patterns

1. Fix import ordering (`sort-imports`)
2. Fix object key ordering (`sort-keys`)
3. Enforce function style consistency
4. Add missing named constants

**Why second**: Makes codebase predictable for future AI sessions.

### Phase 3: Complexity Reduction (Week 3)
**Goal**: Decompose monolithic functions

1. Split functions > 50 lines
2. Reduce parameter counts
3. Extract nested logic
4. Simplify deep conditionals

**Why third**: Improves maintainability and testability.

### Phase 4: React Performance (Week 4)
**Goal**: Optimize React rendering

1. Fix hook dependencies
2. Remove inline object/array creation
3. Reduce JSX nesting depth
4. Memoize expensive computations

**Why fourth**: Performance improvements after correctness.

---

## Expected Results

| Metric | Before | After Phase 1 | After Phase 4 | Change |
|--------|--------|---------------|---------------|--------|
| Type safety errors | 8,849 | 0 | 0 | -100% |
| Total violations | 53,469 | ~35,000 | <5,000 | -91% |
| AI-generated bugs | High | Medium | Low | Significant |
| Code consistency | Low | Medium | High | Dramatic |
| Maintainability | Poor | Fair | Good | Major improvement |

---

## AI Agent Instructions

When working on this codebase:

1. **Always run oxlint before committing**:
   ```bash
   bunx oxlint --type-aware .
   ```

2. **Fix violations immediately** - Don't bypass with `eslint-disable`

3. **If unsure about a rule**:
   - Check this document for rationale
   - Ask why the rule exists
   - Don't disable without documented reason

4. **Use auto-fix when available**:
   ```bash
   bunx oxlint --type-aware . --fix
   ```

5. **For unavoidable violations** (rare):
   - Document reason in comment above `eslint-disable`
   - Link to issue/ticket explaining why
   - Add TODO with timeline for removal

---

## Success Criteria

✅ All type safety rules passing (no `any`, unsafe operations)
✅ Consistent code style across all files
✅ No functions > 50 lines
✅ No circular dependencies
✅ Named constants for all "magic" values
✅ React performance rules passing
✅ AI-generated code passes all quality gates

---

## Rationale: Why Strict for AI?

**Human-coded projects**: Developers understand context, can make judgment calls, know when to break rules.

**AI-coded projects**: AI doesn't have:
- Long-term codebase context
- Understanding of project-specific patterns
- Judgment about when rules should be broken
- Knowledge of technical debt accumulation

**Therefore**: Strict, enforced rules act as **external memory and constraints** that prevent AI from introducing anti-patterns across sessions.

This is similar to:
- **Rust's borrow checker** - Prevents memory issues at compile time
- **TypeScript's strict mode** - Prevents type errors before runtime
- **Linting for AI** - Prevents quality issues during generation

The cost of strictness (more upfront fixes) is far lower than the cost of accumulated technical debt from unconstrained AI generation.
