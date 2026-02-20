# Preventing AI Naming Explosion

## The Problem

### What Happens Without Guards

User: "Make xyz changes to dashboard class"

**AI creates naming explosion**:

```
Dashboard                    # Original (working, in use)
Dashboard_v2                 # AI's first "improvement"
EnhancedDashboard           # AI's second iteration
EnhancedDashboard_v2        # AI's third iteration
EnhancedDashboard_Modular   # AI's fourth iteration
ImprovedDashboard           # AI's fifth iteration
NewDashboard                # AI gives up on naming
```

**Result**:

- ❌ 7 implementations of the same concept
- ❌ Only the last one is actually used
- ❌ 6 orphaned files that confuse future AI sessions
- ❌ Massive technical debt
- ❌ Import confusion across codebase

### Why AI Does This

1. **False backward compatibility** - AI assumes old code must be preserved
2. **Conflict avoidance** - AI doesn't want to "break" existing code
3. **Incremental thinking** - AI treats each request as additive
4. **No cleanup instinct** - AI doesn't naturally delete unused code

---

## The Solution: Strict Naming + Deletion Rules

### Rule 1: Canonical Names Only

**Forbidden Patterns**:

```
❌ Dashboard_v2
❌ DashboardNew
❌ DashboardImproved
❌ DashboardEnhanced
❌ DashboardModular
❌ DashboardFixed
❌ DashboardUpdated
❌ DashboardRefactored
❌ DashboardV2
❌ Dashboard2
❌ NewDashboard
❌ ImprovedDashboard
```

**Allowed**:

```
✅ Dashboard              (canonical name)
✅ DashboardLayout        (distinct component)
✅ DashboardHeader        (subcomponent)
✅ DashboardMetrics       (distinct feature)
```

### Rule 2: Edit In Place, Never Duplicate

**Wrong Approach** (AI's default):

```typescript
// Step 1: AI reads Dashboard.tsx
class Dashboard {
  render() {
    return <div>Original</div>;
  }
}

// Step 2: AI creates Dashboard_v2.tsx (BAD!)
class Dashboard_v2 {
  render() {
    return <div>Improved</div>;
  }
}

// Step 3: AI updates imports to use Dashboard_v2
import { Dashboard_v2 } from './Dashboard_v2';
```

**Correct Approach** (enforced):

```typescript
// Step 1: AI reads Dashboard.tsx
class Dashboard {
  render() {
    return <div>Original</div>;
  }
}

// Step 2: AI EDITS Dashboard.tsx directly
class Dashboard {
  render() {
    return <div>Improved</div>;
  }
}

// Step 3: No import changes needed
import { Dashboard } from './Dashboard';
```

### Rule 3: Delete Unused Code Immediately

**Pattern to detect**:

```bash
# Find orphaned files
git log --all --format=%H -- '*Dashboard*.tsx' | while read commit; do
  git show $commit:path/to/file
done

# If old Dashboard.tsx exists and isn't imported anywhere: DELETE IT
```

**Automated check**:

```typescript
// In pre-commit hook
import { findUnusedExports } from 'ts-unused-exports';

const unused = findUnusedExports();
if (unused.includes('Dashboard_v2')) {
  throw new Error('Found versioned naming: Dashboard_v2. Use canonical naming.');
}
```

---

## Linting Rules for Naming Explosion

### ESLint Plugin: `no-versioned-names`

Add to `.oxlintrc.json`:

```json
{
  "rules": {
    "unicorn/filename-case": [
      "error",
      {
        "cases": {
          "camelCase": true,
          "pascalCase": true
        }
      }
    ],

    // Custom rule: Prevent versioned naming
    "no-restricted-syntax": [
      "error",
      {
        "selector": "Identifier[name=/.*[Vv]\\d+$/]",
        "message": "Versioned naming (e.g., Dashboard_v2) is forbidden. Edit the original file instead."
      },
      {
        "selector": "Identifier[name=/^(New|Improved|Enhanced|Updated|Fixed|Refactored).+/]",
        "message": "Prefix naming (e.g., NewDashboard, ImprovedDashboard) is forbidden. Edit the original file instead."
      },
      {
        "selector": "Identifier[name=/.*_(new|improved|enhanced|updated|fixed|refactored)$/i]",
        "message": "Suffix naming (e.g., Dashboard_improved) is forbidden. Edit the original file instead."
      }
    ]
  }
}
```

### File Naming Validation

Create `.eslintrc.filenames.js`:

```javascript
module.exports = {
  rules: {
    'filenames/match-regex': ['error', '^[a-z][a-zA-Z0-9]*$', true],
    'filenames/no-versioning': [
      'error',
      {
        patterns: [
          /v\d+/i, // _v2, V2, v2
          /version\d+/i, // version2
          /_\d+$/, // _2, _3
          /^new/i, // NewDashboard
          /^improved/i, // ImprovedDashboard
          /^enhanced/i, // EnhancedDashboard
          /^updated/i, // UpdatedDashboard
          /^fixed/i, // FixedDashboard
          /^refactored/i, // RefactoredDashboard
        ],
      },
    ],
  },
};
```

---

## AI Agent Instructions

### Before Making Changes

**MANDATORY CHECKLIST**:

1. ✅ **Identify the canonical file**

   ```bash
   # Find the file that's actually imported/used
   rg "import.*Dashboard" --type tsx

   # This is your target - edit THIS file
   ```

2. ✅ **Check for versioned variants**

   ```bash
   # Look for naming explosion
   ls *Dashboard*.tsx

   # If you see Dashboard_v2.tsx, Dashboard_new.tsx, etc.
   # These are ORPHANED and should be DELETED
   ```

3. ✅ **Verify it's the active implementation**
   ```bash
   # Ensure this file is actually used
   rg "Dashboard" --type tsx | grep -v "Dashboard_"
   ```

### During Changes

**RULE**: Never create `ComponentName_v2` or `NewComponentName`

**Instead**:

1. Read the current file
2. Edit it directly
3. Test the changes
4. Commit

**Example workflow**:

```typescript
// ❌ WRONG - Creating new version
// AI reads Dashboard.tsx
// AI writes to Dashboard_v2.tsx
// AI updates imports

// ✅ CORRECT - Editing in place
// AI reads Dashboard.tsx
// AI uses Edit tool on Dashboard.tsx
// No import changes needed
```

### After Changes

**MANDATORY CLEANUP**:

1. ✅ **Delete orphaned versions**

   ```bash
   # Remove old versions
   rm Dashboard_v2.tsx
   rm EnhancedDashboard.tsx
   rm NewDashboard.tsx
   ```

2. ✅ **Verify no broken imports**

   ```bash
   # Check for references to deleted files
   rg "Dashboard_v2|NewDashboard|EnhancedDashboard" --type tsx

   # Should return nothing
   ```

3. ✅ **Update any stale imports**
   ```typescript
   // Fix any lingering imports
   import { Dashboard } from './Dashboard'; // ✅ Good
   // not
   import { Dashboard_v2 } from './Dashboard_v2'; // ❌ Delete this
   ```

---

## Pattern Recognition: When AI Is About to Explode Names

### Warning Signs

**AI says**:

- "I'll create a new version to preserve backward compatibility"
- "Let me make Dashboard_v2 to avoid breaking changes"
- "I'll create EnhancedDashboard with the improvements"
- "Creating NewDashboard to implement these changes"

**Response**:

```
❌ STOP. Do not create versioned or prefixed names.

✅ Instead:
1. Edit Dashboard.tsx directly
2. Delete any orphaned Dashboard_*.tsx files
3. This is an aggressively evolving project
4. Backward compatibility is NOT a goal
5. There should be ONE canonical implementation
```

### Auto-Detection Script

Create `.husky/pre-commit-naming-check`:

```bash
#!/bin/bash

# Check for naming explosion patterns
VERSIONED=$(find . -type f \( -name "*_v[0-9]*.tsx" -o -name "*_v[0-9]*.ts" \))
PREFIXED=$(find . -type f \( -name "New*.tsx" -o -name "Improved*.tsx" -o -name "Enhanced*.tsx" \))
SUFFIXED=$(find . -type f \( -name "*_new.tsx" -o -name "*_improved.tsx" -o -name "*_enhanced.tsx" \))

if [ -n "$VERSIONED" ] || [ -n "$PREFIXED" ] || [ -n "$SUFFIXED" ]; then
  echo "❌ NAMING EXPLOSION DETECTED"
  echo ""
  echo "Found versioned/prefixed files:"
  echo "$VERSIONED"
  echo "$PREFIXED"
  echo "$SUFFIXED"
  echo ""
  echo "Action required:"
  echo "1. Edit the original file in place"
  echo "2. Delete the versioned/prefixed files"
  echo "3. Update imports to use canonical names"
  echo ""
  exit 1
fi

echo "✅ No naming explosion detected"
```

---

## Examples from Real Projects

### Example 1: Dashboard Evolution

**Bad** (naming explosion):

```
components/
├── Dashboard.tsx                    # Orphaned (not used)
├── Dashboard_v2.tsx                 # Orphaned (not used)
├── EnhancedDashboard.tsx           # Orphaned (not used)
├── EnhancedDashboard_v2.tsx        # Orphaned (not used)
├── EnhancedDashboard_Modular.tsx   # Currently in use
└── ImprovedDashboard.tsx           # Being developed
```

**Good** (canonical naming):

```
components/
├── Dashboard.tsx              # Single canonical implementation
├── DashboardLayout.tsx        # Distinct layout component
├── DashboardHeader.tsx        # Subcomponent
└── DashboardMetrics.tsx       # Feature module
```

### Example 2: User Profile

**Bad**:

```
UserProfile.tsx          # Original
UserProfileNew.tsx       # "Improved" version
EnhancedUserProfile.tsx  # "Better" version
UserProfile_v3.tsx       # Third iteration
```

**Good**:

```
UserProfile.tsx          # Single source of truth (edited in place)
```

### Example 3: API Client

**Bad**:

```
ApiClient.ts
ApiClient_v2.ts
ImprovedApiClient.ts
ApiClientRefactored.ts
NewApiClient.ts
```

**Good**:

```
ApiClient.ts             # Core client (edited in place)
ApiClientAuth.ts         # Auth extension
ApiClientCache.ts        # Cache extension
```

---

## Automated Enforcement

### GitHub Action: Block Naming Explosion

`.github/workflows/naming-guard.yml`:

```yaml
name: Naming Explosion Guard

on: [pull_request]

jobs:
  check-naming:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
        with:
          fetch-depth: 0

      - name: Check for versioned naming
        run: |
          # Find versioned files in PR
          VERSIONED=$(git diff --name-only origin/main... | grep -E '_(v|V)[0-9]+\.(ts|tsx|js|jsx)$' || true)
          PREFIXED=$(git diff --name-only origin/main... | grep -E '^(New|Improved|Enhanced|Updated).*\.(ts|tsx|js|jsx)$' || true)

          if [ -n "$VERSIONED" ] || [ -n "$PREFIXED" ]; then
            echo "❌ Naming explosion detected in PR"
            echo ""
            echo "Versioned files:"
            echo "$VERSIONED"
            echo ""
            echo "Prefixed files:"
            echo "$PREFIXED"
            echo ""
            echo "See docs/reports/AI_NAMING_EXPLOSION_PREVENTION.md"
            exit 1
          fi

      - name: Check for orphaned files
        run: |
          # Find files that aren't imported anywhere
          bunx ts-unused-exports --showLineNumber
```

---

## Project-Specific Rules for TraceRTM

### Naming Conventions

**Components**:

```
✅ Dashboard.tsx
✅ DashboardLayout.tsx (distinct layout variant)
❌ Dashboard_v2.tsx
❌ NewDashboard.tsx
```

**Features**:

```
✅ UserProfile.tsx
✅ UserProfileSettings.tsx (distinct feature)
❌ UserProfile_improved.tsx
❌ EnhancedUserProfile.tsx
```

**Routes**:

```
✅ dashboard.tsx
✅ dashboard.layout.tsx (specific layout)
❌ dashboard_compat.tsx
❌ dashboard-new.tsx
```

### Backward Compatibility Policy

**Policy**: NO backward compatibility for internal components.

This is an **aggressively evolving project**:

- ✅ Break internal APIs freely
- ✅ Edit files in place
- ✅ Delete unused code immediately
- ❌ Don't preserve old implementations
- ❌ Don't version internal components
- ❌ Don't create compatibility layers

**Exception**: Public API contracts (if applicable)

- Only create versioned APIs if external consumers exist
- Even then, prefer API evolution over versioning

---

## Summary: The Golden Rules

### ✅ DO

1. **Edit in place** - Modify the existing file
2. **Use canonical names** - One name per concept
3. **Delete orphans** - Remove unused implementations immediately
4. **Check imports** - Verify what's actually used
5. **Test after editing** - Ensure changes work

### ❌ DON'T

1. **Create \_v2 files** - Never version component names
2. **Add prefixes** - No New*, Improved*, Enhanced\*
3. **Preserve old code** - Delete unused implementations
4. **Assume backward compat** - This is an evolving project
5. **Leave orphans** - Clean up immediately

### 🚨 When You See Naming Explosion

```bash
# 1. Identify the active file
rg "import.*Dashboard" --type tsx

# 2. Delete orphaned versions
rm Dashboard_v2.tsx EnhancedDashboard.tsx NewDashboard.tsx

# 3. Edit the canonical file
# Use Edit tool on Dashboard.tsx

# 4. Verify no broken imports
rg "Dashboard_|NewDashboard|EnhancedDashboard" --type tsx

# 5. Commit cleanup
git add .
git commit -m "refactor: consolidate Dashboard to canonical implementation"
```

---

## Enforcement Checklist

- [ ] Add naming rules to `.oxlintrc.json`
- [ ] Create pre-commit hook for naming checks
- [ ] Add GitHub Action to block versioned names
- [ ] Document canonical naming in `AGENTS.md`
- [ ] Run initial cleanup to remove existing orphans
- [ ] Add to AI agent instructions

**Status**: Ready to implement
**Priority**: CRITICAL (prevents unbounded technical debt)
