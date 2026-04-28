# AI Coding Quality Gates - Complete Setup

## Executive Summary

✅ **Strict linting configuration** designed for AI-coded projects
✅ **Opinionated rules** to constrain AI behavior and prevent anti-patterns
✅ **Quality gates** to ensure consistency across AI sessions
✅ **Automated enforcement** via oxlint with type-awareness

---

## Why This Matters: AI vs Human Development

### Human-Coded Projects

- Developers understand long-term context
- Can make judgment calls about when to break rules
- Naturally maintain consistency within their own code
- Understand technical debt implications

### AI-Coded Projects (This Project)

- **No persistent context** across sessions
- **No judgment** about rule-breaking appropriateness
- **Inconsistent patterns** without strict guidelines
- **Accumulates technical debt** without constraints

### Solution: Strict Linting as AI Guardrails

Treat linting rules like:

- **Rust's borrow checker** - Prevents memory issues at compile time
- **TypeScript strict mode** - Prevents type errors before runtime
- **Linting for AI** - Prevents quality/consistency issues during generation

---

## Three-Tier Configuration System

### 1. `.oxlintrc.json` (RECOMMENDED FOR AI)

**Purpose**: Maximum strictness for AI-coded development

**When to use**: Primary configuration for all AI coding sessions

**Features**:

- ✅ All type safety rules at ERROR level
- ✅ Strict style consistency enforcement
- ✅ Complexity limits to force decomposition
- ✅ Named constants required (no magic numbers)
- ✅ React performance rules enforced
- ✅ Circular dependency prevention
- ✅ Descriptive naming enforced

**Apply**:

```bash
# Replace current config
mv .oxlintrc.json .oxlintrc.json.backup
cp .oxlintrc.json .oxlintrc.json

# Run linting
bunx oxlint --type-aware .
```

### 2. `.oxlintrc.json` (MODERATE STRICTNESS)

**Purpose**: Strict type safety, moderate style enforcement

**When to use**: Transitional period or mixed human/AI teams

**Features**:

- ✅ Type safety strictly enforced
- ⚠️ Style rules as warnings (not errors)
- ❌ Some stylistic rules disabled

### 3. `.oxlintrc.json` (CURRENT - TOO PERMISSIVE)

**Purpose**: Original configuration with many overrides

**Issues**:

- Too many disable overrides
- Inconsistent enforcement across directories
- Allows anti-patterns that AI commonly generates

**Status**: Should be replaced with `.ai-strict`

---

## Key Rules for AI Quality

### Type Safety (CRITICAL)

```typescript
// ❌ BAD (AI commonly generates)
function getData(id: any) {
  return data[id];
}

// ✅ GOOD (enforced by rules)
function getData(id: string): UserData | undefined {
  return data[id];
}
```

**Rules**:

- `typescript/no-explicit-any`: ERROR
- `typescript/explicit-function-return-type`: ERROR
- `typescript/no-unsafe-*`: ERROR

### Complexity Limits

```typescript
// ❌ BAD (AI tends to generate monolithic functions)
function processUser(user, options, context, flags) {
  // 150 lines of nested logic...
}

// ✅ GOOD (forced by rules)
function processUser(user: User): ProcessedUser {
  // Max 50 lines
  // Max 3 parameters
  // Max 3 nesting depth
  const validated = validateUser(user);
  const enriched = enrichUserData(validated);
  return transformUser(enriched);
}
```

**Rules**:

- `eslint/max-lines-per-function`: 50 lines
- `eslint/max-params`: 3 parameters
- `eslint/max-depth`: 3 nesting levels
- `complexity`: 10 cyclomatic complexity

### Named Constants

```typescript
// ❌ BAD (AI uses magic numbers)
if (retries > 3) {
  setTimeout(fn, 5000);
}

// ✅ GOOD (enforced by rules)
const MAX_RETRIES = 3;
const RETRY_DELAY_MS = 5000;

if (retries > MAX_RETRIES) {
  setTimeout(fn, RETRY_DELAY_MS);
}
```

**Rules**:

- `eslint/no-magic-numbers`: ERROR (except 0, 1, -1)

### Style Consistency

```typescript
// ❌ BAD (AI generates inconsistent imports)
import { z } from 'zod';
import type { User } from './types';
import { Button } from '@/components/Button';
import React from 'react';

// ✅ GOOD (enforced by rules)
import React from 'react';
import { z } from 'zod';

import { Button } from '@/components/Button';
import type { User } from './types';
```

**Rules**:

- `eslint/sort-imports`: ERROR
- `import/order`: ERROR (grouped & alphabetized)

### React Performance

```typescript
// ❌ BAD (AI creates re-render issues)
function MyComponent() {
  return (
    <Child
      onClick={() => console.log("clicked")}
      data={{ value: 123 }}
      items={[1, 2, 3]}
    />
  );
}

// ✅ GOOD (enforced by rules)
const ITEMS = [1, 2, 3];
const DATA = { value: 123 };

function MyComponent() {
  const handleClick = useCallback(() => {
    console.log("clicked");
  }, []);

  return (
    <Child
      onClick={handleClick}
      data={DATA}
      items={ITEMS}
    />
  );
}
```

**Rules**:

- `react-perf/jsx-no-new-object-as-prop`: ERROR
- `react-perf/jsx-no-new-array-as-prop`: ERROR
- `react-perf/jsx-no-new-function-as-prop`: ERROR

---

## Phased Implementation Plan

### Phase 1: Type Safety (Week 1) - CRITICAL

**Goal**: Eliminate all type unsafety

**Tasks**:

1. Replace all `any` with proper types (8,849 violations)
2. Add explicit return types to all functions
3. Fix all `no-unsafe-*` violations
4. Enable strict null checks

**Commands**:

```bash
# Find all any usage
bunx oxlint --type-aware . | grep "no-explicit-any"

# Auto-fix what's possible
bunx oxlint --type-aware . --fix

# Manual review remaining issues
bunx oxlint --type-aware . > linting-report.txt
```

**Success Criteria**: Zero type safety errors

### Phase 2: Style Consistency (Week 2)

**Goal**: Establish consistent patterns

**Tasks**:

1. Fix all import ordering issues
2. Alphabetize object keys
3. Standardize function style (arrow functions)
4. Extract magic numbers to constants

**Auto-fixable**:

```bash
# Most style issues can be auto-fixed
bunx oxlint --type-aware . --fix

# Review changes
git diff
```

**Success Criteria**: Consistent style across codebase

### Phase 3: Complexity Reduction (Week 3)

**Goal**: Decompose monolithic code

**Tasks**:

1. Split functions > 50 lines into smaller functions
2. Reduce parameter counts (max 3)
3. Extract nested logic into helper functions
4. Simplify conditional logic

**Approach**:

- Identify violations: `bunx oxlint . | grep "max-lines-per-function"`
- Refactor one file at a time
- Run tests after each refactor

**Success Criteria**: No functions > 50 lines, max 3 params

### Phase 4: React Performance (Week 4)

**Goal**: Optimize React rendering

**Tasks**:

1. Fix hook dependency arrays
2. Remove inline object/array creation in JSX
3. Memoize callbacks and expensive computations
4. Reduce JSX nesting depth

**Tools**:

```bash
# Find React performance issues
bunx oxlint . | grep "react-perf"
bunx oxlint . | grep "jsx-max-depth"
```

**Success Criteria**: All React performance rules passing

---

## Configuration Comparison

| Rule Category     | Current          | .strict     | .ai-strict |
| ----------------- | ---------------- | ----------- | ---------- |
| Type Safety       | ⚠️ Warnings      | ✅ Errors   | ✅ Errors  |
| Style Consistency | ❌ Many disabled | ⚠️ Warnings | ✅ Errors  |
| Complexity Limits | ❌ Disabled      | ⚠️ Warnings | ✅ Errors  |
| Magic Numbers     | ❌ Disabled      | ⚠️ Warnings | ✅ Errors  |
| React Performance | ⚠️ Warnings      | ⚠️ Warnings | ✅ Errors  |
| Import Ordering   | ❌ Disabled      | ✅ Errors   | ✅ Errors  |
| Circular Deps     | ✅ Errors        | ✅ Errors   | ✅ Errors  |

**Recommendation**: Use `.ai-strict` for AI-coded development

---

## Expected Results

### Before (Current)

```bash
$ bunx oxlint --type-aware .
❌ 53,469 violations
  - 48,422 warnings
  - 5,047 errors
  - Type safety: 8,849 issues
  - Style consistency: Poor
  - Code quality: Mixed
```

### After Phase 1 (Type Safety)

```bash
$ bunx oxlint --type-aware .
❌ 35,000 violations (-35%)
  - 34,500 warnings
  - 500 errors
  - Type safety: 0 issues ✅
  - Style consistency: Poor
  - Code quality: Improved
```

### After Phase 4 (Complete)

```bash
$ bunx oxlint --type-aware .
❌ <5,000 violations (-91%)
  - 4,500 warnings
  - 500 errors
  - Type safety: 0 issues ✅
  - Style consistency: Excellent ✅
  - Code quality: High ✅
```

---

## AI Agent Workflow

### Before Starting Work

```bash
# 1. Pull latest config
git pull

# 2. Run linting to see current state
bunx oxlint --type-aware . > pre-work-lint.txt

# 3. Note number of violations
wc -l pre-work-lint.txt
```

### During Development

```bash
# Run linting frequently (every 10-15 minutes)
bunx oxlint --type-aware .

# Auto-fix what's possible
bunx oxlint --type-aware . --fix

# Check specific file
bunx oxlint --type-aware src/components/MyComponent.tsx
```

### Before Committing

```bash
# 1. Run full linting check
bunx oxlint --type-aware .

# 2. If violations found, fix them
bunx oxlint --type-aware . --fix

# 3. Review changes
git diff

# 4. Commit only when clean (or improving)
git add .
git commit -m "feat: add feature X (fixes 50 linting violations)"
```

### Rule Violations Policy

**NEVER bypass with `eslint-disable` unless**:

1. You document the specific technical reason
2. You link to an issue/ticket
3. You add a TODO with timeline for removal
4. You get explicit approval

Example of acceptable disable:

```typescript
// eslint-disable-next-line @typescript-eslint/no-explicit-any
// TODO(#1234): Replace with proper type after API v2 migration (Q2 2026)
// This any is required because API v1 returns inconsistent shapes
function legacyApiHandler(data: any) {
  // ...
}
```

---

## Automation & CI Integration

### Pre-commit Hook

```bash
# .husky/pre-commit
#!/bin/sh
. "$(dirname "$0")/_/husky.sh"

echo "🔍 Running oxlint..."
bunx oxlint --type-aware .

if [ $? -ne 0 ]; then
  echo "❌ Linting failed. Please fix violations before committing."
  exit 1
fi
```

### GitHub Actions

```yaml
name: Lint

on: [push, pull_request]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: oven-sh/setup-bun@v1

      - name: Install dependencies
        run: bun install

      - name: Run oxlint
        run: bunx oxlint --type-aware .

      - name: Check for violations
        run: |
          VIOLATIONS=$(bunx oxlint --type-aware . 2>&1 | wc -l)
          echo "Total violations: $VIOLATIONS"

          if [ $VIOLATIONS -gt 5000 ]; then
            echo "❌ Too many violations ($VIOLATIONS > 5000)"
            exit 1
          fi
```

### VS Code Integration

Add to `.vscode/settings.json`:

```json
{
  "eslint.enable": true,
  "eslint.validate": ["javascript", "typescript", "typescriptreact"],
  "editor.codeActionsOnSave": {
    "source.fixAll.eslint": true
  },
  "eslint.workingDirectories": [{ "mode": "auto" }]
}
```

---

## Success Metrics

### Code Quality Metrics

| Metric                   | Target | Current | After Phase 4 |
| ------------------------ | ------ | ------- | ------------- |
| Type safety violations   | 0      | 8,849   | 0 ✅          |
| Functions > 50 lines     | 0      | ~200    | 0 ✅          |
| Magic numbers            | 0      | ~500    | 0 ✅          |
| Circular dependencies    | 0      | 41      | 0 ✅          |
| React performance issues | 0      | 2,168   | 0 ✅          |
| Total violations         | <5,000 | 53,469  | <5,000 ✅     |

### AI Quality Improvements

| Issue                    | Before     | After                      |
| ------------------------ | ---------- | -------------------------- |
| AI generates `any` types | Common     | Prevented by linting       |
| Inconsistent imports     | Every file | Consistent across codebase |
| Monolithic functions     | 100+ lines | Max 50 lines enforced      |
| Magic numbers everywhere | Common     | Named constants required   |
| React re-render issues   | Frequent   | Prevented by perf rules    |
| Circular dependencies    | 41 found   | 0 (prevented at commit)    |

---

## Documentation Files

| File                               | Purpose                            |
| ---------------------------------- | ---------------------------------- |
| `AI_CODED_LINTING_STRATEGY.md`     | Overall strategy and rationale     |
| `AI_CODING_QUALITY_GATES.md`       | This file - implementation guide   |
| `.oxlintrc.json`                   | Recommended strict configuration   |
| `.oxlintrc.json`                   | Moderate strict configuration      |
| `STRICT_LINTING_JUSTIFICATIONS.md` | Original analysis (pre-AI context) |

---

## Naming Explosion Prevention (CRITICAL)

### The Problem

AI commonly creates naming explosions when asked to modify code:

```
User: "Make changes to Dashboard"

AI creates:
✗ Dashboard.tsx (original, orphaned)
✗ Dashboard_v2.tsx
✗ EnhancedDashboard.tsx
✗ NewDashboard.tsx  <-- Currently being used
```

**Result**: 4 files, 3 orphaned, massive confusion for future AI sessions.

### The Solution

**Automated Detection**:

```bash
# Run naming check
./scripts/check-naming-explosion.sh

# Automatically blocks:
# - *_v2.tsx, *V2.tsx (versioned)
# - NewDashboard.tsx, ImprovedComponent.tsx (prefixed)
# - Dashboard_new.tsx, Component_improved.tsx (suffixed)
# - Dashboard_2.tsx, Component_3.tsx (numbered)
```

**Enforcement**:

- ✅ Pre-commit hook blocks versioned names
- ✅ GitHub Actions blocks PRs with naming explosion
- ✅ Clear error messages with remediation steps

**See**: `AI_NAMING_EXPLOSION_PREVENTION.md` for complete guide

---

## Quick Start

### Step 1: Apply Strict Configuration

```bash
cd frontend

# Strict config is the default: frontend/.oxlintrc.json
```

### Step 2: Run Initial Linting

```bash
# See current violations
bunx oxlint --type-aware . > linting-baseline.txt

# Count violations
wc -l linting-baseline.txt
```

### Step 3: Start Phase 1 (Type Safety)

```bash
# Auto-fix what's possible
bunx oxlint --type-aware . --fix

# Manually fix remaining type issues
# Focus on: no-explicit-any, explicit-function-return-type
```

### Step 4: Track Progress

```bash
# After each session
bunx oxlint --type-aware . > linting-progress-$(date +%Y%m%d).txt

# Compare
wc -l linting-baseline.txt
wc -l linting-progress-*.txt
```

---

## Support & Questions

### Common Questions

**Q: Can I disable a rule if it's blocking me?**
A: Only with documentation, issue link, and explicit approval. AI-coded projects need strict guardrails.

**Q: What if a rule produces false positives?**
A: Document the case, create an override for specific files/patterns, keep rule enabled globally.

**Q: How do I handle third-party code with violations?**
A: Add to overrides section with clear comment explaining why.

**Q: Can I adjust complexity limits (50 lines, 3 params)?**
A: Only with architectural justification. Limits exist to prevent AI bloat.

### Getting Help

1. Check `AI_CODED_LINTING_STRATEGY.md` for rule rationale
2. Review example violations in oxlint output
3. Ask specific questions with code examples
4. Create issue with reproduction case

---

## Conclusion

**This strict linting configuration is essential for AI-coded projects** because:

1. **Prevents anti-patterns** that AI commonly generates
2. **Enforces consistency** across multiple AI sessions
3. **Maintains quality** without human code review
4. **Reduces technical debt** from unconstrained generation
5. **Creates predictable codebase** for future AI work

The upfront cost of fixing violations is **far lower** than the long-term cost of accumulated technical debt from permissive linting.

**Next Steps**:

1. Apply `.ai-strict` configuration
2. Begin Phase 1 (Type Safety fixes)
3. Track progress weekly
4. Achieve <5,000 violations by Phase 4
