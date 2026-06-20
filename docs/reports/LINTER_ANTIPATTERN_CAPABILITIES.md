# Linter Antipattern Detection Capabilities Report

**Date**: 2026-02-02
**Context**: Phase 3 completion, Phase 4 planning
**Goal**: Achieve <500 lines per file across entire codebase

---

## Executive Summary

**Current State**: Our linters detect **function-level** complexity and style antipatterns but do **NOT** have built-in **file-level LOC (lines of code)** limits. We need custom tooling for file size enforcement.

**Key Findings**:
- ✅ Function complexity limits: **YES** (via C901, gocognit, funlen)
- ✅ Function length limits: **YES** (via PLR0915, funlen in Go)
- ❌ **File size/LOC limits: NO** (not built into ruff, golangci-lint, oxlint)
- ✅ Other antipatterns: **YES** (many - see detailed list below)

---

## Current Antipattern Detection by Linter

### Python (ruff) ✅

**Complexity Antipatterns** (Active):
- **C901**: McCabe cyclomatic complexity (max=7)
- **PLR0911**: Too many return statements (max=6)
- **PLR0912**: Too many branches (max=12)
- **PLR0913**: Too many arguments (max=5) ⚠️ **Most common violation**
- **PLR0915**: Too many statements in function (max=50)
- **PLR1702**: Too many nested blocks (max=5)
- **PLR2004**: Magic value comparison (avoid hardcoded constants)

**Other Antipatterns Detected**:
- **S** (Security): Hardcoded passwords, insecure file permissions, binding to 0.0.0.0
- **B** (Bugbear): Common bugs like mutable default arguments, unused loop variables
- **A** (Annotations): Missing type annotations
- **ASYNC**: Async/await misuse (blocking calls in async functions)
- **SIM**: Code simplification opportunities
- **RUF**: Ruff-specific Python antipatterns

**Missing**:
- ❌ **File LOC limit** - NO built-in rule for file size
- ❌ **Class size limit** - NO built-in rule for class LOC
- ❌ **Module import count** - Not enforced

---

### Go (golangci-lint) ✅

**Complexity Antipatterns** (Active):
- **gocyclo**: Cyclomatic complexity detection
- **gocognit**: Cognitive complexity (min=12)
- **funlen**: Function length limits (**lines: 80, statements: 50**)
- **dupl**: Duplicate code detection (85% similarity threshold)
- **goconst**: Repeated strings → constants (3+ occurrences)
- **mnd**: Magic number detection (avoid hardcoded numbers)

**Other Antipatterns Detected**:
- **gochecknoglobals**: No global variables
- **unconvert**: Unnecessary type conversions
- **exhaustive**: Exhaustive switch/type-switch coverage
- **perfsprint**: Performance anti-patterns (inefficient string formatting)
- **nolintlint**: Validates proper //nolint usage
- **misspell**: Typos in code/comments

**Missing**:
- ❌ **File LOC limit** - NO built-in rule for file size
- ❌ **Package size limit** - Not enforced

---

### TypeScript/Frontend (oxlint) ⚠️

**Status**: AI-strict config enabled, but **limited file-level antipattern detection**

**Antipatterns Detected** (oxlint AI-strict):
- React hooks rules (dependency arrays, exhaustive deps)
- TypeScript type safety (no-any, no-explicit-any)
- JSX accessibility (a11y rules)
- React performance (jsx-max-depth: **ACTIVE**, max=4)

**Missing**:
- ❌ **File LOC limit** - NO built-in rule
- ❌ **Component complexity** - Limited (only jsx-max-depth)
- ❌ **Import count** - Not enforced

---

## Files Exceeding 500 Lines (Current State)

### Python: 20 files >500 lines

**Top Violators**:
1. `src/tracertm/api/main.py` - **9,768 lines** ⚠️ CRITICAL
2. `src/tracertm/api/routers/item_specs.py` - **3,203 lines**
3. `src/tracertm/services/spec_analytics_service.py` - **2,664 lines**
4. `src/tracertm/cli/commands/item.py` - **2,059 lines**
5. `src/tracertm/mcp/tools/param.py` - **1,822 lines**
6. `src/tracertm/storage/local_storage.py` - **1,712 lines**
7. `src/tracertm/cli/commands/project.py` - **1,388 lines**
8. `src/tracertm/repositories/item_spec_repository.py` - **1,350 lines**
9. `src/tracertm/api/client.py` - **1,335 lines**
10. `src/tracertm/api/routers/specifications.py` - **1,304 lines**
11. `src/tracertm/schemas/item_spec.py` - **1,223 lines**
12. `src/tracertm/services/stateless_ingestion_service.py` - **1,072 lines**
13. `src/tracertm/storage/sync_engine.py` - **1,068 lines**
14. `src/tracertm/models/item_spec.py` - **1,066 lines**
15. `src/tracertm/services/item_spec_service.py` - **1,036 lines**
16. `src/tracertm/cli/commands/import_cmd.py` - **1,027 lines**
17. `src/tracertm/cli/commands/link.py` - **1,017 lines**
18. `src/tracertm/services/ai_tools.py` - **993 lines**
19. `src/tracertm/cli/commands/design.py` - **897 lines**
20. `src/tracertm/repositories/specification_repository.py` - **850 lines**

**Total Python files >500 lines**: 20
**Largest file**: main.py at 9,768 lines (19.5x over limit!)

---

### Go: 20 files >500 lines

**Top Violators**:
1. `backend/docs/tracertm_docs.go` - **6,799 lines** (auto-generated swagger)
2. `backend/docs/docs.go` - **6,799 lines** (auto-generated swagger)
3. `backend/internal/db/queries.sql.go` - **4,045 lines** (auto-generated sqlc)
4. `backend/pkg/proto/tracertm/v1/tracertm.pb.go` - **2,005 lines** (auto-generated protobuf)
5. `backend/tests/integration/service_integration_test.go` - **1,490 lines**
6. `backend/tests/integration/endpoints_test.go` - **1,479 lines**
7. `backend/internal/equivalence/handler.go` - **1,310 lines**
8. `backend/internal/handlers/item_handler_test.go` - **1,238 lines**
9. `backend/internal/services/temporal_service_test.go` - **1,214 lines**
10. `backend/internal/equivalence/handler_test.go` - **1,159 lines**

**Note**: 4 of top 10 are **auto-generated** (swagger, sqlc, protobuf) - exclude from refactoring

---

### TypeScript/Frontend: Multiple large files

**Note**: Many frontend files appear to be in `node_modules` or generated. Need to filter to source files only.

**Action Required**: Run filtered scan on `frontend/apps/` and `frontend/packages/` only

---

## Antipattern Detection Summary Table

| Antipattern | Python (ruff) | Go (golangci) | TS (oxlint) |
|-------------|---------------|---------------|-------------|
| **File LOC limit** | ❌ NO | ❌ NO | ❌ NO |
| **Function complexity** | ✅ C901 (max=7) | ✅ gocognit (12) | ⚠️ Limited |
| **Function length** | ✅ PLR0915 (50 stmt) | ✅ funlen (80 lines) | ❌ NO |
| **Too many args** | ✅ PLR0913 (max=5) | ⚠️ No direct rule | ⚠️ No direct rule |
| **Too many branches** | ✅ PLR0912 (max=12) | ✅ gocyclo | ⚠️ Limited |
| **Too many returns** | ✅ PLR0911 (max=6) | ⚠️ No direct rule | ❌ NO |
| **Nested blocks** | ✅ PLR1702 (max=5) | ✅ Via gocognit | ⚠️ jsx-max-depth |
| **Magic numbers** | ✅ PLR2004 | ✅ mnd | ❌ NO |
| **Duplicate code** | ⚠️ Limited | ✅ dupl (85%) | ❌ NO |
| **Repeated strings** | ⚠️ Limited | ✅ goconst (3+) | ❌ NO |
| **Global variables** | ⚠️ Limited | ✅ gochecknoglobals | ❌ NO |
| **Security issues** | ✅ S rules | ⚠️ gosec (disabled) | ⚠️ Limited |
| **Type safety** | ✅ ANN rules | ✅ Via type system | ✅ AI-strict |

---

## Missing Antipattern Detection

### Critical Gaps ⚠️

**File-level antipatterns NOT detected**:
1. ❌ **File size (LOC)** - No linter enforces <500 line limit
2. ❌ **Class size** - No linter enforces class LOC limits
3. ❌ **Import count** - No linter flags excessive imports
4. ❌ **Exported function count** - No limit on public API surface
5. ❌ **File responsibility** - No "single responsibility" checker for files

**Structural antipatterns NOT detected**:
1. ❌ **God objects/classes** - No detection for classes with too many methods
2. ❌ **Deep inheritance** - No inheritance depth limits
3. ❌ **Circular dependencies** - Not checked by linters (need madge/dpdm)
4. ❌ **Dead code** - Limited detection (vulture for Python exists but not active)

---

## Recommendations

### Immediate Actions (Phase 4)

**1. Custom File LOC Checker** (REQUIRED)
```bash
# Add to naming explosion check script or create new script
scripts/shell/check-file-size-violations.sh

# Scan for files >500 lines
find src -name "*.py" -exec wc -l {} \; | awk '$1 > 500 {print}'
find backend -name "*.go" ! -path "*/vendor/*" -exec wc -l {} \; | awk '$1 > 500 {print}'
find frontend/apps -name "*.ts" -o -name "*.tsx" | xargs wc -l | awk '$1 > 500 {print}'
```

**2. Activate Additional Ruff Rules**
```toml
[tool.ruff.lint]
select = [
    "PLR0904",  # Too many public methods (max=20)
    "PLR6301",  # Method could be a function (no self usage)
]
```

**3. Enable Go gosec** (security antipatterns)
```yaml
linters:
  enable:
    - gosec  # Security-focused Go linter
```

**4. Add madge/dpdm** for circular dependency detection (Frontend)
```bash
bun add -d madge dpdm
# Add to CI: madge --circular frontend/apps/
```

---

### Phase 4 Execution Strategy

**Goal**: Bring ALL files to <500 lines

**Targets**:
- Python: 20 files (main.py: 9,768 → <500 requires ~20 more modules!)
- Go: 16 files (excluding auto-generated)
- Frontend: TBD (scan source files only)

**Approach**:
1. **Wave 1**: main.py decomposition (9,768 → <500 lines)
   - Extract remaining 10+ high-complexity functions
   - Create additional handler modules (github, oauth, chat, health, device)
   - Target: 20+ modules, each <500 lines

2. **Wave 2**: Other Python 500+ line files (19 files)
   - item_specs.py (3,203 lines) → split routers
   - spec_analytics_service.py (2,664 lines) → extract analytics modules
   - CLI commands (item, project, import, link, design) → extract subcommands

3. **Wave 3**: Go 500+ line files (16 files)
   - handlers (equivalence, item) → extract handlers
   - tests → table-driven conversions + split by feature

4. **Wave 4**: Frontend (after source scan)

**Estimated Effort**: 50-100 agent-hours (async swarm: 8-16 hours wall clock)

---

## Conclusion

**Answer to User's Questions**:

1. **Do linters check for file LOC antipatterns?** ❌ **NO** - None of our linters (ruff, golangci-lint, oxlint) have built-in file size limits. We need custom tooling.

2. **What other antipatterns do they check?** ✅ **MANY**:
   - Function complexity (C901, gocognit)
   - Function length (PLR0915, funlen)
   - Too many arguments (PLR0913)
   - Too many branches/returns (PLR0911, PLR0912)
   - Magic numbers (PLR2004, mnd)
   - Duplicate code (dupl in Go)
   - Security issues (S rules, gosec)
   - Type safety (mypy, TypeScript strict mode)

3. **What's missing?**:
   - ❌ File LOC limits
   - ❌ Class size limits
   - ❌ Import count limits
   - ❌ Circular dependency detection (need madge/dpdm)
   - ❌ Dead code detection (need vulture)

**Next Step**: Launch Phase 4 agent swarm to decompose all files >500 lines, starting with main.py (9,768 → <500)

---

**Report Status**: 🟢 COMPLETE
**Recommendation**: Proceed to Phase 4 with custom file LOC enforcement
**Owner**: BMAD Master / Tech Lead
