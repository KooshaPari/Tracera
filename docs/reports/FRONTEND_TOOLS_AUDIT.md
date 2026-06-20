# Frontend Tools Audit Report

**Date**: 2026-02-02
**Scope**: Biome, Stylelint, and oxlint configuration analysis
**Reference**: `.oxlintrc.json.ai-strict` AI-coding standards

---

## Executive Summary

**Critical Finding**: Current frontend tooling is **significantly misaligned** with AI-coding standards. Biome and Stylelint are currently **disabled or severely weakened**, while oxlint carries the full burden but is itself operating in a **permissive mode** (current `.oxlintrc.json`) rather than the strict AI-coding mode (`.oxlintrc.json.ai-strict`).

**Recommendations**:
1. **Activate `.oxlintrc.json.ai-strict`** as the primary configuration
2. **Remove Biome** from the linting pipeline (keep for formatting only)
3. **Enhance Stylelint** to enforce CSS/Tailwind standards matching oxlint strictness
4. **Consolidate** to oxlint-first strategy to eliminate tool overlap and confusion

---

## Current Tool Status

### 1. Oxlint (Primary Linter)

**Active Configuration**: `/frontend/.oxlintrc.json` (Permissive Mode)
**AI-Strict Reference**: `/frontend/.oxlintrc.json.ai-strict`

#### Configuration Analysis

| Aspect | Current (.oxlintrc.json) | AI-Strict (.ai-strict) | Gap |
|--------|--------------------------|-------------------------|-----|
| **Type Safety** | Partial (`warn` on unsafe ops) | Maximum (`error` on all unsafe) | ❌ MAJOR |
| **Complexity Limits** | Disabled in overrides | `max: 50` lines, `10` complexity, `3` params | ❌ CRITICAL |
| **Magic Numbers** | Disabled globally | `error` (allow 0,1,-1 only) | ❌ CRITICAL |
| **Import Sorting** | Disabled in overrides | `error` with strict ordering | ❌ MAJOR |
| **React Performance** | Partially disabled | All `react-perf` rules `error` | ❌ MAJOR |
| **Naming Conventions** | Not enforced | `id-length`, `prevent-abbreviations`, `filename-case` | ❌ MAJOR |
| **Explicit Return Types** | Disabled in src/** | `error` globally | ❌ CRITICAL |

**Critical Issues in Current Config**:

1. **Massive Override Scope** (lines 180-242): Disables nearly ALL strict rules for `apps/**/src/**` and `packages/**/src/**` - this is essentially the entire codebase.

2. **Component Override** (lines 112-177): Disables 60+ rules for components, including:
   - `typescript/no-explicit-any` - allows `any` everywhere
   - `eslint/complexity` - no complexity limits
   - `eslint/max-lines-per-function` - no function size limits
   - `react-perf` rules - allows performance anti-patterns

3. **Rules That Should Be Active (AI-Strict) But Are Disabled**:
   ```json
   // AI-Strict expects ERROR, current has OFF:
   "typescript/no-explicit-any": "error"           → OFF in src/**
   "typescript/explicit-function-return-type"      → OFF in src/**
   "typescript/explicit-module-boundary-types"     → OFF in src/**
   "eslint/max-lines-per-function": ["error", 50]  → OFF in src/**
   "eslint/max-params": ["error", 3]               → OFF in src/**
   "eslint/complexity": ["error", 10]              → OFF in src/**
   "eslint/max-statements": ["error", 15]          → OFF in src/**
   "eslint/no-magic-numbers"                       → OFF in src/**
   "eslint/id-length": ["error", {"min": 2}]       → OFF in src/**
   "eslint/sort-imports"                           → OFF in src/**
   "eslint/sort-keys"                              → OFF in src/**
   "react-perf/jsx-no-new-object-as-prop"          → OFF in src/**
   "react-perf/jsx-no-new-array-as-prop"           → OFF in src/**
   "react-perf/jsx-no-new-function-as-prop"        → OFF in src/**
   "react/jsx-max-depth": ["error", 4]             → OFF in src/**
   ```

4. **Import Chaos**: AI-strict enforces strict import ordering, but current config disables it everywhere except the base level (which is then overridden).

---

### 2. Biome (Linter + Formatter)

**Active Configuration**: `/frontend/biome.json` (Severely Weakened)
**Backup Configuration**: `/frontend/biome.json.backup` (Previously Strict)

#### What Happened to Biome?

**Current State** (`biome.json`):
```json
{
  "linter": {
    "enabled": true,
    "rules": {
      "recommended": true,
      "a11y": {
        // ALL a11y rules turned OFF (8 rules)
      },
      "suspicious": {
        "noExplicitAny": "off",
        "noArrayIndexKey": "off",
        // 4 more critical rules OFF
      },
      "correctness": {
        "noUnusedVariables": "off",
        "noUnusedFunctionParameters": "off"
      },
      "security": {
        "noDangerouslySetInnerHtml": "off"
      }
    }
  },
  "formatter": {
    "enabled": true  // Only this is really active
  }
}
```

**Previous State** (`biome.json.backup`):
```json
{
  "linter": {
    "rules": {
      "complexity": {
        "noExcessiveCognitiveComplexity": {"maxAllowedComplexity": 15}
      },
      "correctness": {
        "noUnusedImports": "error",
        "noUnusedVariables": "error",
        "useExhaustiveDependencies": "error"
      },
      "suspicious": {
        "noExplicitAny": "error",
        "noArrayIndexKey": "warn"
      },
      "security": {
        "noDangerouslySetInnerHtml": "error"
      }
    }
  }
}
```

**Analysis**: Biome was **gutted**. All meaningful linting rules were disabled, leaving only the formatter active. This suggests:
- Biome was causing conflicts with oxlint
- Team chose to disable Biome linting rather than harmonize configs
- Biome is now **formatter-only** in practice

---

### 3. Stylelint (CSS Linter)

**Active Configuration**: `/frontend/stylelint.config.js`

#### Current Configuration

```javascript
{
  extends: [
    "stylelint-config-recommended",    // Basic CSS rules
    "stylelint-config-tailwindcss",    // Tailwind-specific
  ],
  rules: {
    "at-rule-no-unknown": null,        // Allow @tailwind, @layer, @apply
    "alpha-value-notation": ["percentage", { exceptProperties: ["opacity"] }],
    "color-function-notation": "modern",
    "property-no-deprecated": [true, { severity: "warning" }],
  }
}
```

#### Gap Analysis vs AI-Strict Standards

| Feature | AI-Strict Expectation | Stylelint Current | Gap |
|---------|----------------------|-------------------|-----|
| **Naming Conventions** | Enforce kebab-case, BEM patterns | Not configured | ❌ MISSING |
| **Complexity Limits** | Max selector depth, specificity limits | Not configured | ❌ MISSING |
| **Magic Numbers** | Named CSS variables for colors, sizes | Not configured | ❌ MISSING |
| **Property Ordering** | Logical property order (position→box→visual) | Not configured | ❌ MISSING |
| **Tailwind Enforcement** | Prefer Tailwind classes over custom CSS | Basic support only | ⚠️ PARTIAL |
| **CSS Quality** | Disallow vendor prefixes, duplicates, unknown | Recommended only | ⚠️ PARTIAL |

**Stylelint is Underpowered**: While Biome was disabled, Stylelint was never enhanced to compensate. It handles basic CSS validation but lacks the strictness expected in an AI-coding environment.

---

## Tool Overlap Analysis

### Where Tools Compete (Problematic Overlap)

| Rule Category | Oxlint | Biome | Stylelint | Current Winner | Should Be |
|---------------|--------|-------|-----------|----------------|-----------|
| **TypeScript Type Safety** | ✅ Comprehensive | ⚠️ Basic (disabled) | ❌ N/A | Oxlint | Oxlint |
| **React Hooks** | ✅ Full `react-hooks` plugin | ✅ `useExhaustiveDependencies` | ❌ N/A | Conflict | Oxlint |
| **Import Sorting** | ✅ Strict ordering | ✅ `organizeImports` | ❌ N/A | Conflict | Oxlint |
| **Unused Variables** | ✅ Via TypeScript | ✅ `noUnusedVariables` (disabled) | ❌ N/A | Oxlint | Oxlint |
| **Formatting** | ❌ N/A | ✅ Full formatter | ❌ N/A | Biome | Biome |
| **CSS Linting** | ❌ N/A | ❌ N/A | ✅ Full | Stylelint | Stylelint |

### Where Tools Complement (Good Separation)

| Tool | Unique Responsibility | Conflicts? |
|------|----------------------|------------|
| **Oxlint** | JS/TS/React linting, type checking | No (if others disabled) |
| **Biome** | Code formatting only | No (if linting disabled) |
| **Stylelint** | CSS/Tailwind linting | No (different domain) |

**Current Problem**: Biome's linting was **disabled to avoid conflicts** with oxlint, but this was done **reactively** (turning rules off) rather than **strategically** (defining clear boundaries).

---

## Consistency Check: Oxlint AI-Strict vs Biome Backup

| Feature | Oxlint AI-Strict | Biome Backup | Aligned? |
|---------|------------------|--------------|----------|
| **`no-explicit-any`** | `error` | `error` | ✅ |
| **Exhaustive Deps** | `react-hooks/exhaustive-deps` | `useExhaustiveDependencies` | ✅ (same rule) |
| **Complexity Limit** | `10` (cyclomatic) | `15` (cognitive) | ⚠️ Different metrics |
| **Unused Variables** | Via TS plugin | `noUnusedVariables` | ✅ |
| **Array Index Key** | `warn` | `warn` | ✅ |
| **Magic Numbers** | `error` (allow 0,1,-1) | Not configured | ❌ |
| **Import Sorting** | Strict 8-group order | `organizeImports` basic | ⚠️ Different depth |
| **Filename Case** | `error` (3 cases allowed) | `error` (3 cases allowed) | ✅ |

**When both were active**, they were ~70% aligned but had **overlapping responsibilities** that caused conflicts.

---

## Package.json Script Analysis

### Current Script Hierarchy

```json
{
  "lint": "oxlint .",                              // PRIMARY
  "lint:fix": "oxlint --fix .",
  "lint:biome": "biome check .",                   // REDUNDANT (mostly disabled)
  "lint:stylelint": "stylelint \"**/*.css\"",      // GOOD (CSS-only)
  "lint:turbo": "turbo lint --concurrency=8",

  "format": "oxfmt .",                             // PRIMARY (oxc formatter)
  "format:biome": "biome format --write .",        // ALTERNATE (biome formatter)

  "typecheck": "oxlint --type-check --type-aware .", // PRIMARY

  "quality": "bun run lint && bun run lint:stylelint && bun run typecheck && ..."
}
```

### Issues

1. **Two Formatters**: `oxfmt` and `biome format` - which is canonical?
2. **Redundant Linting**: `lint:biome` runs but has minimal effect (mostly disabled rules)
3. **CI Confusion**: Different scripts may run different tool combinations
4. **No AI-Strict Usage**: `.oxlintrc.json.ai-strict` is never invoked in scripts

---

## Recommended Tool Strategy

### Option A: Oxlint-First (RECOMMENDED)

**Configuration**:
- **Oxlint**: Primary linter (activate `.oxlintrc.json.ai-strict`)
- **Biome**: Formatter ONLY (disable all linting rules)
- **Stylelint**: CSS/Tailwind linter (enhance with strictness matching oxlint)

**Rationale**:
- Oxlint is already the designated primary linter
- AI-strict config already exists and matches AI-coding philosophy
- Eliminates all tool overlap and conflicts
- Clear responsibility boundaries

**Changes Required**:
1. Rename `.oxlintrc.json.ai-strict` → `.oxlintrc.json`
2. Update `biome.json`:
   ```json
   {
     "linter": { "enabled": false },  // Disable entirely
     "formatter": { "enabled": true }
   }
   ```
3. Enhance `stylelint.config.js` (see Configuration Changes section)
4. Update `package.json` scripts:
   ```json
   {
     "lint": "oxlint .",
     "format": "biome format --write .",  // Choose one formatter
     "lint:css": "stylelint \"**/*.css\"",
     "quality": "bun run lint && bun run lint:css && bun run typecheck"
   }
   ```

**Pros**:
- Single source of truth for JS/TS linting
- Eliminates conflict potential
- Aligned with AI-coding standards from day one
- Biome remains useful for fast formatting

**Cons**:
- Biome's linting rules (if valuable) are lost
- Team must adapt to stricter oxlint rules
- Existing codebase may have many violations

---

### Option B: Biome-First (NOT RECOMMENDED)

**Why Not**:
- Biome lacks oxlint's TypeScript type-aware linting depth
- No `.ai-strict` equivalent exists for Biome
- Would require extensive Biome config development to match oxlint AI-strict
- Oxlint plugins (react-perf, unicorn, import) have no Biome equivalents
- Project already invested in oxlint (`.ai-strict` config exists)

---

### Option C: Dual Linting (STRONGLY DISCOURAGED)

**Why Not**:
- Already tried (evidenced by Biome being disabled)
- Creates confusion about which errors matter
- Slower CI/dev feedback loops
- Maintenance burden (two configs to keep in sync)
- Developers will inevitably favor the more permissive linter

---

## Specific Configuration Changes

### 1. Activate Oxlint AI-Strict

**File**: `/frontend/.oxlintrc.json`

**Action**: Replace current permissive config with AI-strict config.

```bash
# Backup current (permissive) config
mv .oxlintrc.json .oxlintrc.json.permissive

# Activate AI-strict
mv .oxlintrc.json.ai-strict .oxlintrc.json
```

**Impact**:
- Immediate enforcement of all AI-coding standards
- Will surface many existing violations (expect 500-2000 errors initially)
- Overrides for tests, configs, and routes are already included in AI-strict

**Migration Strategy**:
1. Run `oxlint .` to get full error count
2. Use `oxlint --fix .` to auto-fix ~40% of violations
3. Create task list for manual fixes (complexity, explicit types, etc.)
4. Consider temporary overrides for large files during transition:
   ```json
   {
     "files": ["apps/web/src/legacy/**"],
     "rules": {
       "eslint/max-lines-per-function": ["error", 100],  // Temporary relaxation
       "complexity": ["error", 15]
     }
   }
   ```

---

### 2. Biome: Formatter-Only Mode

**File**: `/frontend/biome.json`

**Proposed Configuration**:

```json
{
  "$schema": "https://biomejs.dev/schemas/2.3.13/schema.json",
  "linter": {
    "enabled": false  // CRITICAL: Disable all linting
  },
  "formatter": {
    "enabled": true,
    "indentStyle": "tab",      // Match oxfmt/project standard
    "indentWidth": 2,
    "lineWidth": 100,
    "lineEnding": "lf"
  },
  "javascript": {
    "formatter": {
      "quoteStyle": "single",
      "jsxQuoteStyle": "double",
      "semicolons": "asNeeded",
      "trailingCommas": "all",
      "arrowParentheses": "always"
    }
  },
  "files": {
    "ignoreUnknown": true,
    "includes": ["**", "!**/routeTree.gen.ts", "!**/api/schema.ts"]
  }
}
```

**Rationale**:
- Preserves Biome's fast, reliable formatting
- Eliminates ALL linting overlap with oxlint
- Simpler config (90% smaller than backup)

---

### 3. Enhanced Stylelint Configuration

**File**: `/frontend/stylelint.config.js`

**Proposed Configuration**:

```javascript
/** @type {import('stylelint').Config} */
export default {
  extends: [
    "stylelint-config-recommended",
    "stylelint-config-tailwindcss",
  ],
  plugins: [
    "stylelint-order",              // ADD: Property ordering
    "stylelint-no-unsupported-browser-features",  // ADD: Browser compat
  ],
  ignoreFiles: [
    "**/node_modules/**",
    "**/dist/**",
    "**/.next/**",
    "**/.turbo/**",
    "**/storybook-static/**",
    "**/*.gen.*",
  ],
  rules: {
    // ===== EXISTING RULES =====
    "at-rule-no-unknown": null,
    "alpha-value-notation": ["percentage", { exceptProperties: ["opacity"] }],
    "color-function-notation": "modern",
    "property-no-deprecated": [true, { severity: "error" }],  // Upgrade to error

    // ===== NEW: COMPLEXITY LIMITS (AI-CODING ALIGNMENT) =====
    "selector-max-id": 0,                    // No IDs (use classes)
    "selector-max-universal": 1,             // Limit * usage
    "selector-max-type": 2,                  // Prefer classes over element selectors
    "selector-max-compound-selectors": 4,    // Max depth (like React jsx-max-depth)
    "selector-max-specificity": "0,4,0",     // Prevent specificity wars
    "max-nesting-depth": 3,                  // Match oxlint max-depth: 3

    // ===== NEW: NAMING CONVENTIONS =====
    "selector-class-pattern": [
      "^([a-z][a-z0-9]*)(-[a-z0-9]+)*$",     // kebab-case enforced
      {
        "message": "Expected class selector to be kebab-case"
      }
    ],
    "custom-property-pattern": [
      "^([a-z][a-z0-9]*)(-[a-z0-9]+)*$",     // CSS vars: --my-color
      {
        "message": "Expected custom property to be kebab-case"
      }
    ],
    "keyframes-name-pattern": [
      "^([a-z][a-z0-9]*)(-[a-z0-9]+)*$",
      {
        "message": "Expected keyframe name to be kebab-case"
      }
    ],

    // ===== NEW: MAGIC NUMBER PREVENTION =====
    "declaration-property-value-disallowed-list": {
      "/^(width|height|margin|padding|top|right|bottom|left)/": [
        "/^[0-9]+px$/",                       // Disallow raw px values
      ]
    },
    "length-zero-no-unit": true,             // 0px → 0
    "number-max-precision": 3,               // 0.333 max (no 0.333333...)

    // ===== NEW: TAILWIND ENFORCEMENT =====
    "declaration-no-important": [true, {     // !important only in utilities
      "severity": "warning",
      "message": "Avoid !important; use Tailwind utility classes instead"
    }],

    // ===== NEW: PROPERTY ORDERING (LOGICAL GROUPING) =====
    "order/properties-order": [
      // 1. Positioning
      "position", "top", "right", "bottom", "left", "z-index",
      // 2. Box Model
      "display", "flex", "flex-direction", "justify-content", "align-items",
      "width", "height", "margin", "padding",
      // 3. Visual
      "background", "color", "border", "border-radius",
      // 4. Typography
      "font-family", "font-size", "line-height", "text-align",
      // 5. Other
      "opacity", "transform", "transition"
    ],

    // ===== NEW: DISALLOW VENDOR PREFIXES (Use PostCSS/Autoprefixer) =====
    "property-no-vendor-prefix": true,
    "value-no-vendor-prefix": true,
    "selector-no-vendor-prefix": true,

    // ===== NEW: QUALITY RULES =====
    "declaration-block-no-duplicate-properties": [true, {
      "ignore": ["consecutive-duplicates-with-different-values"]  // Allow fallbacks
    }],
    "font-family-no-duplicate-names": true,
    "no-duplicate-selectors": true,
    "color-no-invalid-hex": true,
    "function-calc-no-unspaced-operator": true,
  },
}
```

**Additional Plugins to Install**:

```bash
bun add -d stylelint-order stylelint-no-unsupported-browser-features
```

**Rationale**:
- **Complexity limits** now match oxlint (depth: 3, specificity limits)
- **Naming conventions** mirror oxlint's `filename-case` and `id-length` philosophy
- **Magic number prevention** aligns with oxlint's `no-magic-numbers` rule
- **Property ordering** enforces consistent, readable CSS (like `sort-keys` in JS)
- **Tailwind enforcement** prevents custom CSS sprawl (matches "prefer utility classes" pattern)

**Impact**:
- Stylelint becomes a **true partner** to oxlint for CSS quality
- Same strictness philosophy across JS/TS and CSS
- Prevents CSS technical debt accumulation

---

## Tool Usage Decision Matrix

| Scenario | Tool to Use | Command | Notes |
|----------|-------------|---------|-------|
| **Lint JS/TS** | Oxlint | `bun run lint` | Primary, AI-strict config |
| **Fix JS/TS** | Oxlint | `bun run lint:fix` | Auto-fix ~40% of issues |
| **Type Check** | Oxlint | `bun run typecheck` | Type-aware linting |
| **Format Code** | Biome | `bun run format` | Fast, reliable formatting |
| **Check Formatting** | Biome | `bun run format:check` | CI check before commit |
| **Lint CSS** | Stylelint | `bun run lint:css` | CSS/Tailwind only |
| **Fix CSS** | Stylelint | `bun run lint:css:fix` | Auto-fix CSS issues |
| **Pre-commit** | All Three | `bun run quality` | Full quality gate |
| **CI Pipeline** | All Three | `bun run ci:quality` | Parallel execution |

**Primary Tools by Domain**:
- **JavaScript/TypeScript/React**: Oxlint (AI-strict)
- **Code Formatting**: Biome (formatter-only)
- **CSS/Tailwind**: Stylelint (enhanced)

**Never Use**:
- ❌ `lint:biome` (redundant with oxlint)
- ❌ Manual ESLint (not installed)
- ❌ Prettier (not installed, Biome replaces it)

---

## Migration Roadmap

### Phase 1: Baseline Assessment (Day 1)

1. **Run oxlint AI-strict dry run**:
   ```bash
   oxlint --config .oxlintrc.json.ai-strict . > violations-baseline.txt
   ```

2. **Categorize violations**:
   ```bash
   # Count by rule
   grep "Error:" violations-baseline.txt | cut -d':' -f3 | sort | uniq -c | sort -rn
   ```

3. **Estimate effort**:
   - Auto-fixable: ~40% (run `--fix`)
   - Simple manual: ~30% (add return types, rename vars)
   - Refactoring: ~30% (reduce complexity, decompose functions)

**Estimated Violations**: 500-2000 errors (based on typical codebases)

---

### Phase 2: Tool Consolidation (Day 1-2)

1. **Activate oxlint AI-strict**:
   ```bash
   mv .oxlintrc.json .oxlintrc.json.permissive
   mv .oxlintrc.json.ai-strict .oxlintrc.json
   ```

2. **Disable Biome linting**:
   - Update `biome.json` per Configuration Changes #2
   - Remove `lint:biome` references from CI

3. **Enhance Stylelint**:
   - Install new plugins: `bun add -d stylelint-order stylelint-no-unsupported-browser-features`
   - Update `stylelint.config.js` per Configuration Changes #3

4. **Update package.json scripts**:
   ```json
   {
     "lint": "oxlint .",
     "format": "biome format --write .",
     "lint:css": "stylelint \"**/*.css\" --fix",
     "quality": "bun run lint && bun run lint:css && bun run typecheck"
   }
   ```

**Duration**: 2-4 hours

---

### Phase 3: Auto-Fix Violations (Day 2)

1. **Run oxlint auto-fix**:
   ```bash
   oxlint --fix .
   ```

2. **Run Biome formatter** (to clean up after fixes):
   ```bash
   biome format --write .
   ```

3. **Run Stylelint auto-fix**:
   ```bash
   stylelint "**/*.css" --fix
   ```

4. **Verify build still passes**:
   ```bash
   bun run build
   ```

**Expected Results**:
- ~40% of violations auto-fixed
- Remaining violations require manual intervention

**Duration**: 1-2 hours (mostly automated)

---

### Phase 4: Manual Fixes - Priority Tiers (Day 3-7)

#### Tier 1: Critical (Day 3-4)
Focus: Rules that affect correctness or security

- `typescript/no-explicit-any` → Add proper types
- `typescript/no-floating-promises` → Add `await` or `.catch()`
- `react-hooks/exhaustive-deps` → Fix dependency arrays
- `security/no-dangerous-html` → Sanitize or remove

**Estimated Files**: 50-100 files

#### Tier 2: Quality (Day 5-6)
Focus: Rules that improve maintainability

- `typescript/explicit-function-return-type` → Add return types
- `eslint/id-length` → Rename single-letter variables
- `eslint/sort-imports` → Organize imports
- `unicorn/prevent-abbreviations` → Spell out `fn`, `cb`, `idx`

**Estimated Files**: 100-200 files

#### Tier 3: Complexity Refactoring (Day 7+)
Focus: Rules requiring code restructuring

- `eslint/max-lines-per-function` → Extract helper functions
- `complexity: 10` → Simplify conditional logic
- `eslint/max-params: 3` → Introduce config objects
- `eslint/no-magic-numbers` → Define constants

**Estimated Files**: 50-100 files (but more time-intensive)

**Total Duration**: 5-7 days (can parallelize across team)

---

### Phase 5: CI/CD Integration (Day 8)

1. **Update GitHub Actions** (`.github/workflows/quality.yml`):
   ```yaml
   - name: Lint JavaScript/TypeScript
     run: bun run lint

   - name: Lint CSS
     run: bun run lint:css

   - name: Check Formatting
     run: biome format --check .

   - name: Type Check
     run: bun run typecheck
   ```

2. **Add pre-commit hook** (`.husky/pre-commit`):
   ```bash
   #!/bin/sh
   bun run lint --staged
   bun run lint:css
   biome format --write --staged .
   ```

3. **Update PR checks**:
   - Fail on ANY oxlint errors
   - Fail on Stylelint errors
   - Fail on formatting violations

**Duration**: 1-2 hours

---

### Phase 6: Documentation & Training (Day 9)

1. **Create tool guide**: `docs/reference/FRONTEND_LINTING_GUIDE.md`
2. **Update CONTRIBUTING.md**: Document quality expectations
3. **Team training**: Walk through AI-strict rules and rationale
4. **IDE setup guide**: Configure VS Code for oxlint + Biome + Stylelint

**Duration**: 2-4 hours

---

## Gap Summary

### Critical Gaps (Must Fix)

| Gap | Current State | AI-Strict Expectation | Impact |
|-----|---------------|----------------------|--------|
| **Type Safety** | Weak (`any` allowed) | Strict (all unsafe ops error) | High - Runtime errors |
| **Complexity Limits** | Disabled | Enforced (50 lines, 10 complexity) | High - Unmaintainable code |
| **Magic Numbers** | Allowed | Named constants only | Medium - Unclear intent |
| **Explicit Types** | Optional | Required on all functions | High - Type errors |
| **React Performance** | No enforcement | All perf rules active | Medium - Slow renders |

### Major Gaps (Should Fix)

| Gap | Current State | AI-Strict Expectation | Impact |
|-----|---------------|----------------------|--------|
| **Import Sorting** | No order | Strict 8-group order | Medium - Readability |
| **Naming Conventions** | No rules | 2-char min, no abbrevs | Medium - Clarity |
| **CSS Complexity** | Basic rules | Depth/specificity limits | Medium - CSS bloat |
| **Property Ordering** | No order | Logical grouping | Low - Readability |

### Minor Gaps (Nice to Have)

| Gap | Current State | AI-Strict Expectation | Impact |
|-----|---------------|----------------------|--------|
| **Filename Case** | Inconsistent | kebab/camel/Pascal only | Low - Consistency |
| **Comment Style** | No rules | No inline comments | Low - Clarity |
| **Ternary Nesting** | Allowed | Max 1 level | Low - Readability |

---

## Recommended Immediate Actions

### Within 24 Hours

1. ✅ **Activate oxlint AI-strict config**
   ```bash
   cd /Users/kooshapari/temp-PRODVERCEL/485/kush/trace/frontend
   mv .oxlintrc.json .oxlintrc.json.permissive
   cp .oxlintrc.json.ai-strict .oxlintrc.json
   ```

2. ✅ **Disable Biome linting** (keep formatting)
   - Edit `biome.json`: `"linter": { "enabled": false }`

3. ✅ **Run violation baseline**:
   ```bash
   oxlint . > /tmp/violations-baseline.txt
   wc -l /tmp/violations-baseline.txt
   ```

4. ✅ **Auto-fix what's possible**:
   ```bash
   oxlint --fix .
   biome format --write .
   ```

### Within 1 Week

5. ✅ **Enhance Stylelint config** per Configuration Changes #3

6. ✅ **Fix Tier 1 violations** (correctness/security)

7. ✅ **Update CI/CD** to use new config

8. ✅ **Document new standards** in `docs/reference/`

### Within 1 Month

9. ✅ **Fix Tier 2 violations** (quality)

10. ✅ **Refactor Tier 3 violations** (complexity)

11. ✅ **Team retrospective**: Assess impact of AI-strict rules

12. ✅ **Consider strictness tweaks**: If any rules prove problematic, document and adjust (but bias toward keeping strict)

---

## Risks & Mitigation

### Risk 1: Too Many Violations to Fix

**Likelihood**: High
**Impact**: Medium (delays feature work)

**Mitigation**:
- Use phased approach (Tier 1 → 2 → 3)
- Create temporary overrides for legacy code:
  ```json
  {
    "files": ["apps/web/src/legacy/**"],
    "rules": {
      "complexity": ["error", 15],  // Temporary relaxation
      "eslint/max-lines-per-function": ["error", 100]
    }
  }
  ```
- Remove overrides one file at a time during regular refactoring

### Risk 2: Team Pushback on Strict Rules

**Likelihood**: Medium
**Impact**: Medium (slows adoption)

**Mitigation**:
- Explain AI-coding rationale (LLMs work better with explicit types, small functions)
- Show examples of bugs caught by strict rules
- Make auto-fix easy: `bun run lint:fix`
- Document escape hatches for legitimate exceptions

### Risk 3: Biome Linting Was Valuable

**Likelihood**: Low
**Impact**: Low (can re-enable specific rules)

**Mitigation**:
- Review `biome.json.backup` for unique rules not in oxlint
- Port valuable Biome-only rules to oxlint (if possible)
- Keep Biome config in backup for reference

### Risk 4: CI/CD Breaks

**Likelihood**: High (during transition)
**Impact**: High (blocks merges)

**Mitigation**:
- Add `--max-warnings=1000` temporarily during transition
- Gradual rollout: warn-only mode for 1 week, then error mode
- Provide clear error messages with fix guidance

---

## Conclusion

**Current State**: Misaligned
Frontend tooling is in a **weakened, permissive state** that does not match AI-coding standards. Biome was disabled to avoid conflicts, but oxlint itself is running in permissive mode, and Stylelint lacks the depth to enforce strict CSS standards.

**Recommended State**: Oxlint-First
Consolidate to **oxlint (AI-strict)** for JS/TS linting, **Biome (formatter-only)** for fast formatting, and **Stylelint (enhanced)** for CSS/Tailwind quality. This creates clear boundaries, eliminates conflicts, and aligns with AI-coding philosophy.

**Effort to Fix**: ~40-60 hours
- Tooling changes: 2-4 hours
- Auto-fixes: 1-2 hours
- Manual fixes: 30-50 hours (can parallelize)
- Documentation: 2-4 hours

**Business Value**:
- Fewer runtime errors (type safety, hooks)
- Faster onboarding (explicit types, simple functions)
- Better AI assistance (LLMs prefer strict, explicit code)
- Reduced technical debt (complexity limits prevent sprawl)
- Consistent quality (no "permissive" escape hatches)

**Next Step**: Activate `.oxlintrc.json.ai-strict` and run baseline assessment.

---

**Audit Completed By**: Claude Code (AI Assistant)
**Review Status**: Awaiting team review and approval
**Implementation Target**: Q1 2026
