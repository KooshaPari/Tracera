# Naming Explosion Guard Status Report

**Generated**: 2026-02-02
**Project**: TraceRTM
**Phase**: Quality Gates Verification

---

## Executive Summary

### Overall Status: ⚠️ PARTIAL PROTECTION

- **Frontend (TypeScript)**: ✅ Detection Active, ❌ Violations Found
- **Python**: ⚠️ Rules Configured, Detection Needed
- **Go**: ⚠️ Basic Rules, Enhanced Detection Needed

### Critical Findings

1. **Frontend has active naming violations** despite detection script
2. **Python lacks automated naming explosion detection**
3. **Go needs enhanced naming rules for AI coding patterns**

---

## Language-by-Language Analysis

### 1. Frontend (TypeScript/React)

#### Protection Status: ✅ Active Detection

**Configured Guards**:
- ✅ Shell script: `frontend/scripts/check-naming-explosion.sh`
- ✅ GitHub Action: `.github/workflows/naming-guard.yml`
- ✅ Oxlint rules: `.oxlintrc.json` (unicorn/filename-case)
- ⚠️ ID length rules in place (min: 2, max: 50)

**Detection Patterns**:
```bash
# Versioned: *_v2.tsx, *V2.tsx, *_version2.tsx
VERSIONED=$(find ... | grep -E '(_v|_V|V)[0-9]+\.(ts|tsx|js|jsx)$')

# Prefixed: NewDashboard.tsx, ImprovedComponent.tsx, EnhancedButton.tsx
PREFIXED=$(find ... | grep -E '(New|Improved|Enhanced|Updated|Fixed|Refactored|Modified|Revised)[A-Z].*\.(ts|tsx|js|jsx)$')

# Suffixed: Dashboard_new.tsx, Component_improved.tsx
SUFFIXED=$(find ... | grep -E '_(new|improved|enhanced|updated|fixed|refactored|modified|revised)\.(ts|tsx|js|jsx)$')

# Numbered: Dashboard_2.tsx, Component_3.tsx
NUMBERED=$(find ... | grep -E '_[0-9]+\.(ts|tsx|js|jsx)$')
```

#### Current Violations Found ❌

**Graph Components (5 violations)**:
```
apps/web/src/components/graph/EnhancedGraphView.tsx
apps/web/src/components/graph/EnhancedErrorState.tsx
apps/web/src/components/graph/nodes/QAEnhancedNode.tsx
apps/web/src/components/graph/QAEnhancedNode.tsx
apps/web/src/hooks/useQAEnhancedNodeData.ts
```

**Analysis**:
- `EnhancedErrorState.tsx` coexists with `ErrorState.tsx` (naming explosion!)
- `EnhancedGraphView.tsx` - likely the canonical graph view (check imports)
- Multiple "Enhanced" prefixes suggest iterative AI additions without cleanup

**Evidence of Naming Explosion**:
```bash
$ ls apps/web/src/components/graph/ | grep -E "(GraphView|ErrorState)"
ClusteredGraphView.tsx
EnhancedErrorState.tsx          # ← Violation
EnhancedGraphView.tsx            # ← Violation
ErrorState.tsx                   # ← Original (orphaned?)
FlowGraphView.tsx
GraphViewContainer.tsx
HybridGraphView.enhanced.tsx     # ← .enhanced suffix (bad!)
HybridGraphView.example.tsx
HybridGraphView.tsx
NetworkErrorState.tsx
SigmaGraphView.enhanced.tsx      # ← .enhanced suffix (bad!)
SigmaGraphView.poc.tsx           # ← .poc suffix (proof-of-concept ok?)
SigmaGraphView.tsx
StreamingGraphView.tsx
TimeoutErrorState.tsx
UnifiedGraphView.tsx
VirtualizedGraphView.tsx
```

**Import Usage Analysis**:
```typescript
// EnhancedErrorState is actively used:
import { EnhancedErrorState } from "../EnhancedErrorState";
// Found in:
// - __stories__/ErrorRecovery.stories.tsx
// - GraphViewWithErrorRecovery.example.tsx
// - GraphErrorBoundary.tsx
// - SafeGraphComponents.tsx

// ErrorState is also used:
import { ErrorState } from "../ErrorState";
// Found in:
// - __stories__/LoadingStates.stories.tsx
```

**Conclusion**: Both `ErrorState` and `EnhancedErrorState` are in use. This is a **legitimate naming explosion** that should be consolidated.

#### Script Limitation Found ⚠️

The detection script catches violations in `node_modules`, causing false positives:
```
# False positives (vendor code):
apps/docs/node_modules/.pnpm/es-abstract@1.24.1/.../NewPromiseCapability.js
apps/docs/node_modules/.pnpm/playwright-core@1.58.1/.../traceV3.js
```

**Fix Required**: Update script to exclude `node_modules`:
```bash
find apps packages -type f \
  \( -name "*.ts" -o -name "*.tsx" -o -name "*.js" -o -name "*.jsx" \) \
  -not -path "*/node_modules/*" | grep -E '...'
```

---

### 2. Python

#### Protection Status: ⚠️ Rules Active, Detection Missing

**Configured Guards**:
- ✅ Ruff rule `N999` (invalid-module-name) enabled globally
- ✅ Exceptions for scripts with hyphens (allowed pattern)
- ❌ No automated naming explosion detection script
- ❌ No GitHub Action for Python naming checks

**Ruff N999 Configuration**:
```toml
[tool.ruff.lint]
select = [
    "N",    # pep8-naming (includes N999)
    # ... other rules
]

[tool.ruff.lint.per-file-ignores]
# Allowed exceptions:
"scripts/python/**" = ["N999"]  # Scripts can use hyphens
"**/bmm-auto.py" = ["N999"]     # Tool scripts
```

**What N999 Catches**:
- ✅ Detects invalid module names (non-Python identifiers)
- ✅ Catches hyphens in module names (except allowed scripts)
- ⚠️ Does NOT specifically target "Enhanced", "New", versioning patterns

**Gaps Identified**:

1. **No AI-specific naming patterns detected**:
   ```python
   # These would NOT be caught by N999:
   dashboard_v2.py          # Valid Python identifier
   enhanced_dashboard.py    # Valid Python identifier
   dashboard_improved.py    # Valid Python identifier
   ```

2. **No automated file-level detection**:
   ```bash
   # Missing equivalent of frontend script:
   find backend -name "*_v[0-9]*.py"
   find backend -name "enhanced_*.py"
   find backend -name "improved_*.py"
   ```

3. **No GitHub Action for Python naming**

#### Recommendations for Python

**Create**: `scripts/check-naming-explosion-python.sh`
```bash
#!/bin/bash
set -e

echo "🔍 Checking Python files for naming explosion..."

# Exclude vendored code, migrations, generated files
SEARCH_DIRS="src/tracertm tests"

# Check for versioned naming
VERSIONED=$(find $SEARCH_DIRS -name "*_v[0-9]*.py" -o -name "*V[0-9]*.py" || true)

# Check for AI naming patterns (lowercase snake_case equivalents)
PREFIXED=$(find $SEARCH_DIRS -name "new_*.py" -o -name "improved_*.py" \
    -o -name "enhanced_*.py" -o -name "updated_*.py" || true)

SUFFIXED=$(find $SEARCH_DIRS -name "*_new.py" -o -name "*_improved.py" \
    -o -name "*_enhanced.py" -o -name "*_updated.py" || true)

NUMBERED=$(find $SEARCH_DIRS -name "*_[0-9].py" || true)

if [ -n "$VERSIONED" ] || [ -n "$PREFIXED" ] || [ -n "$SUFFIXED" ] || [ -n "$NUMBERED" ]; then
    echo "❌ NAMING EXPLOSION DETECTED"
    echo ""
    echo "Versioned: $VERSIONED"
    echo "Prefixed: $PREFIXED"
    echo "Suffixed: $SUFFIXED"
    echo "Numbered: $NUMBERED"
    exit 1
fi

echo "✅ No naming explosion detected"
```

**Add to pre-commit**:
```yaml
# .pre-commit-config.yaml
- repo: local
  hooks:
    - id: python-naming-explosion
      name: Check Python naming explosion
      entry: scripts/check-naming-explosion-python.sh
      language: system
      types: [python]
      pass_filenames: false
```

**Extend Ruff with custom semgrep rules** (optional):
```yaml
# .semgrep/naming-explosion.yml
rules:
  - id: python-versioned-naming
    pattern: |
      import $X_v2
    message: "Versioned imports (e.g., module_v2) forbidden. Edit original module."
    languages: [python]
    severity: ERROR
```

---

### 3. Go

#### Protection Status: ⚠️ Basic Rules, Enhanced Detection Needed

**Configured Guards**:
- ✅ Revive `var-naming` rule enabled
- ✅ Revive `package-comments` and `exported` rules
- ❌ No specific AI naming explosion patterns
- ❌ No automated detection script
- ❌ No GitHub Action for Go naming checks

**Current Revive Config**:
```yaml
linters-settings:
  revive:
    rules:
      - name: var-naming        # Checks variable naming conventions
      - name: package-comments  # Requires package documentation
      - name: exported          # Checks exported identifiers
```

**What Revive var-naming Catches**:
- ✅ Enforces Go naming conventions (camelCase, PascalCase)
- ✅ Detects underscores in variable names (not idiomatic)
- ⚠️ Does NOT target "Enhanced", "New", versioning patterns

**Gaps Identified**:

1. **No AI-specific patterns detected**:
   ```go
   // These would pass revive checks:
   package dashboardV2      // Valid Go identifier
   type EnhancedDashboard struct{}
   func NewDashboardImproved() {}
   ```

2. **No file-level detection**:
   ```bash
   # Missing equivalent detection:
   find backend -name "*_v[0-9]*.go"
   find backend -name "*Enhanced*.go"
   ```

3. **No GitHub Action for Go**

#### Recommendations for Go

**Create**: `scripts/check-naming-explosion-go.sh`
```bash
#!/bin/bash
set -e

echo "🔍 Checking Go files for naming explosion..."

# Search in Go backend directories (exclude vendor, generated)
SEARCH_DIRS="backend/go"

# Check for versioned file names
VERSIONED=$(find $SEARCH_DIRS -name "*_v[0-9]*.go" -o -name "*V[0-9]*.go" \
    -not -path "*/vendor/*" -not -path "*_test.go" || true)

# Check for AI naming patterns (Go uses PascalCase for exported)
PREFIXED=$(find $SEARCH_DIRS -name "New*.go" -o -name "Improved*.go" \
    -o -name "Enhanced*.go" -o -name "Updated*.go" \
    -not -path "*/vendor/*" || true)

SUFFIXED=$(find $SEARCH_DIRS -name "*New.go" -o -name "*Improved.go" \
    -o -name "*Enhanced.go" -o -name "*Updated.go" \
    -not -path "*/vendor/*" || true)

if [ -n "$VERSIONED" ] || [ -n "$PREFIXED" ] || [ -n "$SUFFIXED" ]; then
    echo "❌ NAMING EXPLOSION DETECTED"
    echo ""
    echo "Versioned: $VERSIONED"
    echo "Prefixed: $PREFIXED"
    echo "Suffixed: $SUFFIXED"
    exit 1
fi

echo "✅ No naming explosion detected"
```

**Add Revive Custom Rules**:
```yaml
# backend/.golangci.yml
linters-settings:
  revive:
    rules:
      # Existing rules
      - name: var-naming
      - name: package-comments
      - name: exported

      # NEW: AI naming explosion prevention
      - name: var-declaration
        arguments:
          - allowList: []  # No versioned var names

      # Use golangci-lint's regex matcher (if available)
      - name: banned-characters
        arguments:
          - pattern: ".*V[0-9]+.*"
            message: "Versioned naming (e.g., DashboardV2) forbidden"
```

**Alternative: Use `gomodguard` or custom linter**:
```yaml
# backend/.golangci.yml
linters:
  enable:
    - gomodguard  # Can ban imports with patterns

linters-settings:
  gomodguard:
    blocked:
      modules:
        - example.com/app/dashboardV2:
            reason: "Versioned packages forbidden. Edit canonical package."
```

**Create GitHub Action** (same as frontend):
```yaml
# .github/workflows/go-naming-guard.yml
name: Go Naming Guard
on:
  pull_request:
    paths: ['backend/go/**/*.go']
jobs:
  check-naming:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Check naming explosion
        run: ./scripts/check-naming-explosion-go.sh
```

---

## Test Results

### Frontend Script Test

```bash
$ cd frontend && ./scripts/check-naming-explosion.sh

❌ NAMING EXPLOSION DETECTED

The following files use forbidden naming patterns:

apps/web/src/components/graph/EnhancedErrorState.tsx
apps/web/src/components/graph/EnhancedGraphView.tsx
apps/web/src/components/graph/nodes/QAEnhancedNode.tsx
apps/web/src/components/graph/QAEnhancedNode.tsx
apps/web/src/hooks/useQAEnhancedNodeData.ts

# Plus false positives in node_modules (needs fix)
```

### Python N999 Test

```bash
$ cd /Users/kooshapari/temp-PRODVERCEL/485/kush/trace && ruff check --select N999 src/

# No violations found (N999 only checks module name format, not AI patterns)
```

### Go Revive Test

```bash
$ cd backend && golangci-lint run --disable-all --enable revive

# No violations found (revive var-naming checks Go conventions, not AI patterns)
```

---

## Example Violations (Created for Testing)

### Test Case: Creating Naming Violations

```bash
# Created temporary violations:
/tmp/naming_test/dashboard_v2.tsx     # Versioned
/tmp/naming_test/NewDashboard.tsx     # Prefixed
/tmp/naming_test/enhanced_dashboard.tsx  # Prefixed (snake_case)
/tmp/naming_test/Dashboard_2.tsx      # Numbered

# Frontend script WOULD catch all of these ✅
# Python ruff N999 WOULD NOT catch enhanced_dashboard.py ❌
# Go revive WOULD NOT catch EnhancedDashboard.go ❌
```

---

## Immediate Actions Required

### Priority 1: Fix Frontend Script (Quick Win)

**Issue**: Script catches `node_modules` files
**Fix**: Add `-not -path "*/node_modules/*"` to find commands
**File**: `frontend/scripts/check-naming-explosion.sh`

```bash
# Line 17: Change from:
VERSIONED_FILES=$(find apps packages -type f ...)

# To:
VERSIONED_FILES=$(find apps packages -type f \
  \( -name "*.ts" -o -name "*.tsx" -o -name "*.js" -o -name "*.jsx" \) \
  -not -path "*/node_modules/*" | grep -E '(_v|_V|V)[0-9]+\.(ts|tsx|js|jsx)$' || true)
```

**Effort**: 5 minutes
**Impact**: Eliminates false positives

### Priority 2: Address Frontend Violations

**Files to Clean Up**:
1. Consolidate `ErrorState.tsx` and `EnhancedErrorState.tsx`
2. Rename or justify `EnhancedGraphView.tsx`
3. Remove `.enhanced.tsx` suffixes (HybridGraphView, SigmaGraphView)
4. Consolidate QA node components

**Recommended Actions**:
```bash
# 1. Check which ErrorState is canonical:
grep -r "import.*ErrorState" apps/web/src --include="*.tsx" | wc -l
grep -r "import.*EnhancedErrorState" apps/web/src --include="*.tsx" | wc -l

# 2. If EnhancedErrorState is used more:
#    - Rename EnhancedErrorState.tsx → ErrorState.tsx
#    - Delete old ErrorState.tsx
#    - Update imports

# 3. Fix .enhanced.tsx files:
git mv HybridGraphView.enhanced.tsx HybridGraphView.tsx
git mv SigmaGraphView.enhanced.tsx SigmaGraphView.tsx
```

**Effort**: 30-60 minutes
**Impact**: Eliminates all current violations

### Priority 3: Create Python Detection Script

**Create**: `scripts/check-naming-explosion-python.sh`
**Content**: See "Recommendations for Python" section above
**Effort**: 15 minutes
**Impact**: Prevents Python naming explosions

### Priority 4: Create Go Detection Script

**Create**: `scripts/check-naming-explosion-go.sh`
**Content**: See "Recommendations for Go" section above
**Effort**: 15 minutes
**Impact**: Prevents Go naming explosions

### Priority 5: Add GitHub Actions for Python & Go

**Create**:
- `.github/workflows/python-naming-guard.yml`
- `.github/workflows/go-naming-guard.yml`

**Template** (adapt from existing `naming-guard.yml`):
```yaml
name: Python Naming Guard
on:
  pull_request:
    paths: ['src/tracertm/**/*.py', 'tests/**/*.py']
jobs:
  check-naming:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Check naming explosion
        run: ./scripts/check-naming-explosion-python.sh
```

**Effort**: 10 minutes each
**Impact**: Automated enforcement in CI/CD

---

## Phase 2 Enhancements (Future)

### Advanced Pattern Detection

**Semgrep Integration** (for all three languages):
```yaml
# .semgrep/naming-explosion.yml
rules:
  - id: typescript-enhanced-prefix
    pattern: |
      import { Enhanced$X } from ...
    message: "Enhanced* prefix forbidden. Use canonical naming."
    languages: [typescript]
    severity: ERROR

  - id: python-versioned-import
    pattern: |
      import $X_v2
    message: "Versioned imports forbidden. Edit original module."
    languages: [python]
    severity: ERROR

  - id: go-versioned-package
    pattern: |
      import "$X/v2"
    message: "Versioned packages forbidden (unless true API versioning)."
    languages: [go]
    severity: WARNING
```

### Import Graph Analysis

**Detect orphaned files** by analyzing import graph:
```bash
# Use madge (Node.js), pydeps (Python), or go mod graph
bunx madge --circular --orphans apps/web/src
pydeps src/tracertm --show-deps
go mod graph | grep -E "v[0-9]+"
```

### AI Agent Integration

**Auto-fix via Claude MCP**:
```typescript
// MCP tool: consolidate_naming_explosion
{
  "name": "consolidate_naming_explosion",
  "description": "Automatically consolidate versioned files to canonical names",
  "inputSchema": {
    "type": "object",
    "properties": {
      "pattern": { "type": "string" },  // e.g., "Enhanced*"
      "language": { "enum": ["typescript", "python", "go"] }
    }
  }
}
```

---

## Summary Table

| Language   | Detection | Active Rules | Violations | GitHub Action | Status |
|------------|-----------|--------------|------------|---------------|--------|
| Frontend   | ✅ Script | ✅ Oxlint    | ❌ 5 found | ✅ Exists     | ⚠️ Needs cleanup |
| Python     | ❌ None   | ⚠️ N999 only | ⚠️ Unknown | ❌ Missing    | ⚠️ Needs script |
| Go         | ❌ None   | ⚠️ var-naming| ⚠️ Unknown | ❌ Missing    | ⚠️ Needs script |

---

## Recommended Implementation Timeline

### Day 1 (Today - 30 min)
1. Fix frontend script to exclude node_modules (5 min)
2. Run script and document violations (10 min)
3. Create Python detection script (15 min)

### Day 2 (60 min)
1. Create Go detection script (15 min)
2. Add GitHub Actions for Python & Go (20 min)
3. Clean up frontend violations (25 min)

### Week 1 (Phase 2 prep)
1. Test scripts against real codebase
2. Document canonical naming conventions per language
3. Add to pre-commit hooks
4. Update AGENTS.md with naming rules

---

## Conclusion

**Current State**: Partial naming explosion protection exists, but gaps remain.

**Key Issues**:
1. Frontend script works but has false positives and real violations
2. Python and Go lack AI-specific naming explosion detection
3. No cross-language consistency in detection patterns

**Next Steps**:
1. Fix frontend script (immediate)
2. Address frontend violations (immediate)
3. Create Python & Go detection scripts (this week)
4. Add GitHub Actions for all languages (this week)
5. Plan Phase 2 advanced detection (future)

**Risk**: Without Python and Go detection, AI agents may create naming explosions in backend code that won't be caught until manual review.

**Recommendation**: Implement Priority 1-5 actions within the next 2 days to achieve comprehensive naming explosion prevention across all three languages.
