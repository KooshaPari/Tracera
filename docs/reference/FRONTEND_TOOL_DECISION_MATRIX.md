# Frontend Tool Decision Matrix

Quick reference for when to use each frontend tool.

---

## Tool Responsibilities

| Tool | Primary Purpose | Active Config | Status |
|------|----------------|---------------|--------|
| **Oxlint** | JS/TS/React linting | `.oxlintrc.json` | ⚠️ Permissive (should be AI-strict) |
| **Biome** | Code formatting | `biome.json` | ⚠️ Linting disabled (formatter only) |
| **Stylelint** | CSS/Tailwind linting | `stylelint.config.js` | ⚠️ Underpowered (needs enhancement) |

---

## When to Use Each Tool

### Use Oxlint When...

✅ Linting JavaScript/TypeScript code
✅ Checking React component quality
✅ Enforcing type safety
✅ Detecting import cycles
✅ Checking for performance anti-patterns
✅ Running type-aware checks
✅ Enforcing complexity limits

**Commands**:
```bash
bun run lint              # Check all issues
bun run lint:fix          # Auto-fix issues
bun run typecheck         # Type-aware checking
```

---

### Use Biome When...

✅ Formatting JavaScript/TypeScript code
✅ Organizing imports (as part of formatting)
✅ Ensuring consistent code style
✅ Running in CI to check formatting

❌ **Do NOT use for linting** (linting is disabled)

**Commands**:
```bash
bun run format            # Format all code
bun run format:check      # Check formatting (CI)
biome format --write src  # Format specific directory
```

---

### Use Stylelint When...

✅ Linting CSS files
✅ Enforcing Tailwind CSS conventions
✅ Checking CSS property order
✅ Detecting invalid CSS syntax
✅ Preventing CSS complexity

**Commands**:
```bash
bun run lint:css          # Check CSS issues
bun run lint:css:fix      # Auto-fix CSS issues
stylelint "**/*.css"      # Manual run
```

---

## Common Scenarios

### Scenario: "I want to check code quality before commit"

```bash
bun run quality
# Runs: lint + lint:css + typecheck + build + test
```

**What runs**:
1. Oxlint: JS/TS quality checks
2. Stylelint: CSS quality checks
3. Oxlint: Type-aware checks
4. Build: Compilation check
5. Vitest: Unit tests

---

### Scenario: "I want to fix all auto-fixable issues"

```bash
# Fix JS/TS issues
bun run lint:fix

# Format all code
bun run format

# Fix CSS issues
bun run lint:css:fix
```

**Order matters**: Run linting fixes first, then formatting.

---

### Scenario: "CI is failing on formatting"

**Problem**: Biome format check failed

**Solution**:
```bash
# Locally format everything
bun run format

# Commit the changes
git add .
git commit -m "chore: format code"
```

---

### Scenario: "I'm getting type errors"

**Problem**: Oxlint type check failed

**Solution**:
```bash
# Run type check to see errors
bun run typecheck

# Common fixes:
# 1. Add return types to functions
# 2. Replace 'any' with proper types
# 3. Add proper type imports
# 4. Fix async/await promise handling
```

---

### Scenario: "I want to ignore a specific rule"

**For Oxlint**:
```typescript
// Single line
// oxlint-disable-next-line eslint/no-magic-numbers
const timeout = 5000;

// Entire file (use sparingly!)
/* oxlint-disable typescript/no-explicit-any */
```

**For Stylelint**:
```css
/* stylelint-disable-next-line selector-max-id */
#legacy-id { }

/* stylelint-disable declaration-no-important */
.utility-override {
  margin: 0 !important;
}
/* stylelint-enable declaration-no-important */
```

---

## Tool Capabilities Comparison

| Capability | Oxlint | Biome | Stylelint |
|------------|--------|-------|-----------|
| **JS/TS Linting** | ✅ Full | ⚠️ Disabled | ❌ N/A |
| **Type Checking** | ✅ Type-aware | ❌ No | ❌ N/A |
| **React Rules** | ✅ react, react-perf, jsx-a11y | ⚠️ Basic (disabled) | ❌ N/A |
| **Import Analysis** | ✅ Cycles, sorting, duplicates | ⚠️ Basic organize | ❌ N/A |
| **Code Formatting** | ❌ N/A (use oxfmt) | ✅ Fast, reliable | ❌ N/A |
| **CSS Linting** | ❌ N/A | ❌ N/A | ✅ Full |
| **Auto-fix** | ✅ ~40% of issues | ✅ All formatting | ✅ Some CSS rules |
| **Performance** | ⚡ Fast (Rust) | ⚡ Very fast (Rust) | 🐢 Slower (Node.js) |

---

## Rules Coverage by Tool

### Type Safety

| Rule | Oxlint | Biome | Stylelint |
|------|--------|-------|-----------|
| No `any` | ✅ `typescript/no-explicit-any` | ⚠️ Disabled | ❌ |
| Explicit return types | ✅ `typescript/explicit-function-return-type` | ❌ | ❌ |
| Unsafe operations | ✅ `no-unsafe-*` suite | ⚠️ Disabled | ❌ |
| Floating promises | ✅ `typescript/no-floating-promises` | ❌ | ❌ |

**Winner**: Oxlint (comprehensive type safety)

---

### Complexity Limits

| Rule | Oxlint | Biome | Stylelint |
|------|--------|-------|-----------|
| Max function lines | ✅ `max-lines-per-function: 50` | ⚠️ Disabled | ❌ |
| Cyclomatic complexity | ✅ `complexity: 10` | ❌ | ❌ |
| Cognitive complexity | ❌ | ⚠️ `noExcessiveCognitiveComplexity: 15` (disabled) | ❌ |
| Max params | ✅ `max-params: 3` | ❌ | ❌ |
| Max depth | ✅ `max-depth: 3` | ❌ | ✅ `max-nesting-depth: 3` (CSS) |
| JSX depth | ✅ `react/jsx-max-depth: 4` | ❌ | ❌ |

**Winner**: Oxlint (JS/TS), Stylelint (CSS)

---

### React Quality

| Rule | Oxlint | Biome | Stylelint |
|------|--------|-------|-----------|
| Exhaustive deps | ✅ `react-hooks/exhaustive-deps` | ⚠️ `useExhaustiveDependencies` (disabled) | ❌ |
| Array index key | ✅ `react/no-array-index-key` | ⚠️ `noArrayIndexKey` (disabled) | ❌ |
| Useless fragments | ✅ `react/jsx-no-useless-fragment` | ⚠️ `noUselessFragments` (disabled) | ❌ |
| New object as prop | ✅ `react-perf/jsx-no-new-object-as-prop` | ❌ | ❌ |
| New function as prop | ✅ `react-perf/jsx-no-new-function-as-prop` | ❌ | ❌ |

**Winner**: Oxlint (comprehensive React support)

---

### Import Management

| Rule | Oxlint | Biome | Stylelint |
|------|--------|-------|-----------|
| Circular dependencies | ✅ `import/no-cycle` | ❌ | ❌ |
| Import sorting | ✅ 8-group strict order | ⚠️ Basic organize | ❌ |
| No duplicates | ✅ `import/no-duplicates` | ⚠️ Basic | ❌ |
| No default export | ✅ `import/no-default-export` | ⚠️ `noDefaultExport` (disabled) | ❌ |

**Winner**: Oxlint (import analysis is comprehensive)

---

### Formatting

| Rule | Oxlint | Biome | Stylelint |
|------|--------|-------|-----------|
| Indentation | ❌ | ✅ Configurable | ✅ CSS only |
| Line width | ❌ | ✅ 100 (configurable) | ✅ CSS only |
| Quotes | ❌ | ✅ Single/double | ❌ |
| Semicolons | ❌ | ✅ asNeeded/always | ❌ |
| Trailing commas | ❌ | ✅ all/es5/none | ❌ |

**Winner**: Biome (formatter-only mode is its strength)

---

### CSS Quality

| Rule | Oxlint | Biome | Stylelint |
|------|--------|-------|-----------|
| Selector complexity | ❌ | ❌ | ✅ Max ID, type, compound |
| Property ordering | ❌ | ❌ | ✅ Logical grouping |
| Naming conventions | ❌ | ❌ | ✅ kebab-case enforced |
| Tailwind rules | ❌ | ❌ | ✅ Tailwind-specific |
| No magic numbers | ❌ | ❌ | ✅ Require CSS vars |

**Winner**: Stylelint (CSS domain expertise)

---

## Overlap and Conflicts

### Where Tools Previously Conflicted

| Feature | Oxlint | Biome (Before Disabling) | Resolution |
|---------|--------|--------------------------|------------|
| **Unused variables** | ✅ Via TS plugin | ✅ `noUnusedVariables` | Biome disabled |
| **Exhaustive deps** | ✅ `react-hooks/exhaustive-deps` | ✅ `useExhaustiveDependencies` | Biome disabled |
| **No explicit any** | ✅ `typescript/no-explicit-any` | ✅ `noExplicitAny` | Biome disabled |
| **Import sorting** | ✅ Strict 8-group order | ✅ Basic organize | Biome disabled for linting |

**Why Biome was disabled**: To eliminate conflicts, team chose to disable Biome linting entirely rather than configure boundaries.

---

## Current Tool Weaknesses

### Oxlint Weaknesses

1. **Running in Permissive Mode**: `.oxlintrc.json` has massive overrides that disable most strict rules in `src/**`
2. **AI-Strict Not Active**: `.oxlintrc.json.ai-strict` exists but is not used
3. **No Formatting**: Relies on separate formatter (Biome or oxfmt)

**Fix**: Activate `.oxlintrc.json.ai-strict`

---

### Biome Weaknesses

1. **Linting Disabled**: All meaningful linting rules are turned off
2. **Formatter vs Formatter**: Competes with oxfmt for formatting role
3. **Unclear Role**: Is it a linter or formatter? (Currently: formatter only)

**Fix**: Formalize formatter-only role, remove linting entirely from config

---

### Stylelint Weaknesses

1. **Basic Config**: Only uses `recommended` and `tailwindcss` presets
2. **No Complexity Limits**: Unlike oxlint's strict limits for JS
3. **No Naming Enforcement**: Allows inconsistent class naming
4. **No Magic Number Prevention**: Raw pixel values allowed

**Fix**: Enhance config with strictness matching oxlint philosophy (see audit report)

---

## Recommended Configuration Summary

### Oxlint: Primary Linter (AI-Strict Mode)

**File**: `.oxlintrc.json`

**Key Settings**:
- Type safety: All `typescript/*` rules on `error`
- Complexity: `max-lines-per-function: 50`, `complexity: 10`, `max-params: 3`
- React: All `react-perf/*` rules on `error`
- Imports: Strict 8-group ordering
- Magic numbers: `error` (allow only 0, 1, -1)

**Overrides**: Only for tests, configs, and routes (keep source code strict)

---

### Biome: Formatter Only

**File**: `biome.json`

**Key Settings**:
```json
{
  "linter": { "enabled": false },
  "formatter": {
    "enabled": true,
    "indentStyle": "tab",
    "indentWidth": 2,
    "lineWidth": 100
  }
}
```

**Rationale**: Eliminates conflict with oxlint, preserves fast formatting

---

### Stylelint: Enhanced CSS Linter

**File**: `stylelint.config.js`

**Key Additions Needed**:
- Complexity limits: `selector-max-compound-selectors: 4`, `max-nesting-depth: 3`
- Naming: `selector-class-pattern` (kebab-case), `custom-property-pattern` (kebab-case)
- Magic numbers: Disallow raw px values, require CSS variables
- Property ordering: Logical grouping (positioning → box model → visual)

**Rationale**: Matches oxlint's strictness philosophy for CSS domain

---

## Quick Commands Reference

### Daily Development

```bash
# Before committing
bun run quality              # Full quality check (lint + typecheck + test + build)

# Fix issues
bun run lint:fix             # Auto-fix JS/TS
bun run format               # Format code
bun run lint:css:fix         # Auto-fix CSS

# Check specific issues
bun run lint                 # JS/TS linting only
bun run typecheck            # Type checking only
bun run lint:css             # CSS linting only
```

---

### CI/CD

```bash
# In CI pipeline
bun run lint                 # Oxlint (should use AI-strict)
bun run lint:css             # Stylelint
bun run typecheck            # Type-aware checking
biome format --check .       # Formatting check
bun run test                 # Unit tests
bun run build                # Build check
```

---

### Troubleshooting

```bash
# Oxlint reports too many errors
oxlint --fix .               # Auto-fix first
oxlint --max-warnings=100 .  # Temporary during migration

# Biome format check failing
biome format --write .       # Format locally, commit changes

# Stylelint failing on vendor CSS
# Add to stylelint.config.js ignoreFiles:
# "node_modules/**", "dist/**", "vendor/**"

# Need to see what rule is failing
oxlint --format=json . > errors.json
# Parse errors.json to find most common rule violations
```

---

## Decision Tree: Which Tool for What?

```
Is it a code quality check?
├─ Yes
│  ├─ JavaScript/TypeScript?
│  │  └─ Use: Oxlint (`bun run lint`)
│  ├─ CSS?
│  │  └─ Use: Stylelint (`bun run lint:css`)
│  └─ Type safety?
│     └─ Use: Oxlint type-aware (`bun run typecheck`)
│
└─ No, is it code formatting?
   └─ Use: Biome (`bun run format`)

Is it an import issue?
└─ Use: Oxlint (`import/no-cycle`, `import/no-duplicates`)

Is it a React performance issue?
└─ Use: Oxlint (`react-perf/*` rules)

Is it a complexity issue?
├─ JavaScript?
│  └─ Use: Oxlint (`max-lines-per-function`, `complexity`)
└─ CSS?
   └─ Use: Stylelint (`max-nesting-depth`, `selector-max-*`)
```

---

## Tool Selection Rationale

### Why Oxlint for Linting?

✅ Rust-based (extremely fast)
✅ Type-aware linting (detects type errors)
✅ Comprehensive plugin ecosystem (react, unicorn, import, jsx-a11y)
✅ AI-strict config already exists
✅ Active development and maintenance
✅ Drop-in ESLint replacement

### Why Biome for Formatting?

✅ Rust-based (extremely fast)
✅ Zero-config formatting (works out of the box)
✅ Consistent with industry standards (Prettier-compatible)
✅ Reliable (deterministic output)
✅ No linting conflicts (since linting is disabled)

### Why Stylelint for CSS?

✅ CSS domain expertise (understands CSS specs)
✅ Tailwind plugin support
✅ Property ordering rules
✅ Browser compatibility checking
✅ No JS linter offers equivalent CSS depth

---

## Anti-Patterns to Avoid

### ❌ Using Multiple Linters for JS/TS

**Bad**:
```bash
oxlint . && biome check .  # Redundant, conflicting
```

**Good**:
```bash
oxlint .                   # Single source of truth
```

---

### ❌ Disabling Rules Everywhere

**Bad** (current state):
```json
// .oxlintrc.json
{
  "files": ["apps/**/src/**"],  // Entire codebase!
  "rules": {
    "typescript/no-explicit-any": "off",
    "complexity": "off",
    // ... 60 more rules off
  }
}
```

**Good**:
```json
// .oxlintrc.json (AI-strict)
{
  "files": ["**/*.test.ts"],  // Only tests get relaxed rules
  "rules": {
    "eslint/max-lines-per-function": "off"
  }
}
```

---

### ❌ Ignoring Tool Output

**Bad**:
```bash
# Developer ignores errors
bun run lint  # 50 errors
# ... commits anyway
```

**Good**:
```bash
# Developer fixes errors
bun run lint:fix  # Auto-fix
oxlint .          # Check remaining
# Fix manually, then commit
```

---

### ❌ Inconsistent Formatting

**Bad**:
```bash
# Different developers use different formatters
bun run format:biome  # Developer A
bun run format:oxfmt  # Developer B
# Git diffs full of formatting changes
```

**Good**:
```bash
# Everyone uses same formatter
bun run format        # Always Biome
# Or configure IDE to use Biome on save
```

---

## Tool Performance Comparison

### Benchmark: Linting 1000 TypeScript Files

| Tool | Time | Speed |
|------|------|-------|
| **Oxlint** | ~2-3 seconds | ⚡⚡⚡ |
| **Biome** (when linting enabled) | ~3-4 seconds | ⚡⚡⚡ |
| **ESLint** (for reference) | ~30-60 seconds | 🐢 |

**Why fast matters**: Faster feedback → more frequent checks → higher quality

---

### Benchmark: Formatting 1000 Files

| Tool | Time | Speed |
|------|------|-------|
| **Biome** | ~1-2 seconds | ⚡⚡⚡ |
| **Prettier** (for reference) | ~5-10 seconds | ⚡⚡ |

---

## IDE Integration

### VS Code Setup

**Recommended Extensions**:
1. **Oxlint** (`oxc.oxc-vscode`) - For linting
2. **Biome** (`biomejs.biome`) - For formatting
3. **Stylelint** (`stylelint.vscode-stylelint`) - For CSS

**Settings** (`.vscode/settings.json`):
```json
{
  "editor.defaultFormatter": "biomejs.biome",
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.fixAll.oxlint": true,
    "source.fixAll.stylelint": true
  },
  "[typescript]": {
    "editor.defaultFormatter": "biomejs.biome"
  },
  "[css]": {
    "editor.defaultFormatter": "stylelint.vscode-stylelint"
  }
}
```

---

## Next Steps

1. ✅ **Review this decision matrix** with team
2. ✅ **Activate AI-strict oxlint config** (`.oxlintrc.json.ai-strict` → `.oxlintrc.json`)
3. ✅ **Formalize Biome as formatter-only** (disable linting in `biome.json`)
4. ✅ **Enhance Stylelint** (add complexity, naming, magic number rules)
5. ✅ **Update CI/CD** to use new tool boundaries
6. ✅ **Document in CONTRIBUTING.md** to guide new developers

---

**Document Version**: 1.0
**Last Updated**: 2026-02-02
**Related**: See `/docs/reports/FRONTEND_TOOLS_AUDIT.md` for detailed analysis
