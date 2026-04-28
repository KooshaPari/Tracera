# Implementation Checklist: Phases 11-13
## Step-by-Step Execution Guide

**Created:** 2025-10-13
**Status:** 📋 READY FOR EXECUTION

---

## Phase 14 Prep: Phen Namespace Migration (Pre-Rename)

- [ ] Review `docs/reports/consolidation/PHEN_HEXAGONAL_MIGRATION_PLAN.md` for the layer-by-layer moves.
- [ ] Generate the current import/package inventory: `python tools/generate_phen_codemap.py`.
- [ ] Stage packaging replacements using `tools/phen_namespace_manifest.json`.
- [ ] After each module migration, rerun the codemap script to confirm import counts trend toward zero.
- [ ] Block the final `src/pheno` → `src/phen` rename until the manifest diff is empty.

---

## Phase 11: Quick Wins (4-6 hours)

### Task 11.1: Move Tests to tests/ (1-2h)

**Pre-flight Checks:**
- [ ] Verify tests/ directory exists
- [ ] Check current test files run: `pytest src/pheno/infra/examples/test_status_page.py`
- [ ] Create backup branch: `git checkout -b phase-11-move-tests`

**Execution Steps:**
```bash
# 1. Create target directories
mkdir -p tests/unit/infra
mkdir -p tests/unit/mcp/qa

# 2. Move test files
mv src/pheno/infra/examples/test_status_page.py tests/unit/infra/
mv src/pheno/mcp/qa/core/test_registry.py tests/unit/mcp/qa/
mv src/pheno/mcp/qa/core/test_runner.py tests/unit/mcp/qa/
mv src/pheno/mcp/qa/core/base/test_runner.py tests/unit/mcp/qa/test_runner_base.py
mv src/pheno/mcp/qa/tui/test_compat.py tests/unit/mcp/qa/
mv src/pheno/mcp/qa/tui/widgets/core/test_widgets.py tests/unit/mcp/qa/test_widgets_core.py
mv src/pheno/mcp/qa/tui/widgets/test_widgets.py tests/unit/mcp/qa/test_widgets.py
mv src/pheno/mcp/qa/testing/test_cache.py tests/unit/mcp/qa/
mv src/pheno/mcp/qa/reporters/test_basic.py tests/unit/mcp/qa/

# 3. Update imports in moved test files (if needed)
# Use sed or manual editing

# 4. Run tests
pytest tests/unit/infra/
pytest tests/unit/mcp/qa/
```

**Verification:**
- [ ] All tests pass
- [ ] No test files remain in src/pheno/
- [ ] Imports work correctly

**Rollback (if needed):**
```bash
git checkout main
git branch -D phase-11-move-tests
```

---

### Task 11.2: Consolidate TUI (1-2h)

**Pre-flight Checks:**
- [ ] Check what's in src/pheno/tui/: `ls -la src/pheno/tui/`
- [ ] Verify ui/tui/ exists: `ls -la src/pheno/ui/tui/`
- [ ] Create backup branch: `git checkout -b phase-11-consolidate-tui`

**Execution Steps:**
```bash
# 1. Check tui/__init__.py content
cat src/pheno/tui/__init__.py

# 2. If it has unique code, merge into ui/tui/__init__.py
# Otherwise, just update imports

# 3. Find all imports of pheno.tui
grep -r "from pheno.tui\|import pheno.tui" --include="*.py" . | grep -v __pycache__

# 4. Update imports: pheno.tui → pheno.ui.tui
find . -name "*.py" -type f -exec sed -i '' 's/from pheno\.tui/from pheno.ui.tui/g' {} \;
find . -name "*.py" -type f -exec sed -i '' 's/import pheno\.tui/import pheno.ui.tui/g' {} \;

# 5. Remove old tui/ directory
rm -rf src/pheno/tui/
```

**Verification:**
- [ ] No src/pheno/tui/ directory
- [ ] All imports updated
- [ ] TUI still works
- [ ] All tests pass

**Rollback (if needed):**
```bash
git checkout main
git branch -D phase-11-consolidate-tui
```

---

### Task 11.3: Merge Small Modules (2-3h)

#### 11.3a: grpc/ → infra/grpc/

**Execution Steps:**
```bash
# 1. Create target directory
mkdir -p src/pheno/infra/grpc

# 2. Move files
cp -r src/pheno/grpc/* src/pheno/infra/grpc/

# 3. Update imports
find . -name "*.py" -type f -exec sed -i '' 's/from pheno\.grpc/from pheno.infra.grpc/g' {} \;
find . -name "*.py" -type f -exec sed -i '' 's/import pheno\.grpc/import pheno.infra.grpc/g' {} \;

# 4. Remove old directory
rm -rf src/pheno/grpc/
```

**Verification:**
- [ ] No src/pheno/grpc/
- [ ] All imports updated
- [ ] Tests pass

---

#### 11.3b: stream/ → events/streaming/

**Execution Steps:**
```bash
# 1. Create target directory
mkdir -p src/pheno/events/streaming

# 2. Move files
cp -r src/pheno/stream/* src/pheno/events/streaming/

# 3. Update imports
find . -name "*.py" -type f -exec sed -i '' 's/from pheno\.stream/from pheno.events.streaming/g' {} \;
find . -name "*.py" -type f -exec sed -i '' 's/import pheno\.stream/import pheno.events.streaming/g' {} \;

# 4. Remove old directory
rm -rf src/pheno/stream/
```

**Verification:**
- [ ] No src/pheno/stream/
- [ ] All imports updated
- [ ] Tests pass

---

#### 11.3c: qa/ → testing/qa/

**Execution Steps:**
```bash
# 1. Create target directory
mkdir -p src/pheno/testing/qa

# 2. Move files
cp -r src/pheno/qa/* src/pheno/testing/qa/

# 3. Update imports
find . -name "*.py" -type f -exec sed -i '' 's/from pheno\.qa/from pheno.testing.qa/g' {} \;
find . -name "*.py" -type f -exec sed -i '' 's/import pheno\.qa/import pheno.testing.qa/g' {} \;

# 4. Remove old directory
rm -rf src/pheno/qa/
```

**Verification:**
- [ ] No src/pheno/qa/
- [ ] All imports updated
- [ ] Tests pass

---

#### 11.3d: multi_cloud/ → deployment/multi_cloud/

**Execution Steps:**
```bash
# 1. Create target directory
mkdir -p src/pheno/deployment/multi_cloud

# 2. Move files
cp -r src/pheno/multi_cloud/* src/pheno/deployment/multi_cloud/

# 3. Update imports
find . -name "*.py" -type f -exec sed -i '' 's/from pheno\.multi_cloud/from pheno.deployment.multi_cloud/g' {} \;
find . -name "*.py" -type f -exec sed -i '' 's/import pheno\.multi_cloud/import pheno.deployment.multi_cloud/g' {} \;

# 4. Remove old directory
rm -rf src/pheno/multi_cloud/
```

**Verification:**
- [ ] No src/pheno/multi_cloud/
- [ ] All imports updated
- [ ] Tests pass

---

### Phase 11 Final Verification

**Checklist:**
- [ ] All tests moved to tests/
- [ ] TUI consolidated
- [ ] 4 small modules merged
- [ ] All tests pass: `pytest tests/`
- [ ] No broken imports
- [ ] Code still runs
- [ ] Commit changes: `git commit -am "Phase 11: Quick wins complete"`

**Metrics:**
- [ ] 4 directories removed
- [ ] ~500 LOC deduplicated
- [ ] Cleaner structure

---

## Phase 12: Medium Consolidations (6-9 hours)

### Task 12.1: Merge Monitoring & Observability (2-3h)

**Pre-flight Checks:**
- [ ] Audit monitoring/ directory
- [ ] Audit observability/ directory
- [ ] Identify overlaps
- [ ] Create backup branch: `git checkout -b phase-12-observability`

**Execution Steps:**
```bash
# 1. Create target structure
mkdir -p src/pheno/observability/metrics

# 2. Move monitoring code
cp -r src/pheno/monitoring/* src/pheno/observability/metrics/

# 3. Update imports
find . -name "*.py" -type f -exec sed -i '' 's/from pheno\.monitoring/from pheno.observability.metrics/g' {} \;

# 4. Consolidate duplicates (manual review needed)
# Review and merge any duplicate code

# 5. Remove old directory
rm -rf src/pheno/monitoring/
```

**Verification:**
- [ ] No src/pheno/monitoring/
- [ ] All imports updated
- [ ] Observability works
- [ ] Tests pass

---

### Task 12.2: Consolidate Utility Files (3-4h)

**Pre-flight Checks:**
- [ ] List all utility files
- [ ] Identify overlaps
- [ ] Plan consolidation
- [ ] Create backup branch: `git checkout -b phase-12-utilities`

**Execution Steps:**
```bash
# 1. Create target structure
mkdir -p src/pheno/dev/utils

# 2. Move and consolidate utilities (manual review needed)
# This requires careful analysis of each utility file

# 3. Update imports
# Update based on specific moves

# 4. Remove old utility files
# After verification
```

**Verification:**
- [ ] Utilities consolidated
- [ ] All imports updated
- [ ] Tests pass

---

### Phase 12 Final Verification

**Checklist:**
- [ ] Observability consolidated
- [ ] Utilities consolidated
- [ ] All tests pass
- [ ] No broken imports
- [ ] Commit changes

---

## Phase 13: Major Consolidations (8-12 hours)

### Task 13.1: Merge Orchestrator & Workflow (4-6h)

**Pre-flight Checks:**
- [ ] Deep audit of both directories
- [ ] Identify all overlaps
- [ ] Plan merge strategy
- [ ] Create backup branch: `git checkout -b phase-13-workflow`

**Execution Steps:**
```bash
# 1. Create target structure
mkdir -p src/pheno/workflow/orchestration

# 2. Move orchestrator code
cp -r src/pheno/orchestrator/* src/pheno/workflow/orchestration/

# 3. Consolidate duplicates (complex, manual review)
# This requires deep analysis

# 4. Update imports
find . -name "*.py" -type f -exec sed -i '' 's/from pheno\.orchestrator/from pheno.workflow.orchestration/g' {} \;

# 5. Remove old directory
rm -rf src/pheno/orchestrator/
```

**Verification:**
- [ ] No src/pheno/orchestrator/
- [ ] All imports updated
- [ ] Workflow works
- [ ] Extensive testing

---

### Task 13.2: Consolidate Base Classes (4-6h)

**Pre-flight Checks:**
- [ ] Audit all 27 base classes
- [ ] Identify common patterns
- [ ] Plan consolidation
- [ ] Create backup branch: `git checkout -b phase-13-base-classes`

**Execution Steps:**
```bash
# 1. Create target structure
mkdir -p src/pheno/core/base

# 2. Move common base classes
# Requires careful analysis

# 3. Update imports
# Based on specific moves

# 4. Keep domain-specific bases in place
```

**Verification:**
- [ ] Common bases consolidated
- [ ] Domain bases remain
- [ ] All imports updated
- [ ] Extensive testing

---

### Phase 13 Final Verification

**Checklist:**
- [ ] Workflow consolidated
- [ ] Base classes consolidated
- [ ] All tests pass
- [ ] No broken imports
- [ ] Commit changes

---

## Overall Completion Checklist

### Phase 11 ✅
- [ ] Tests moved
- [ ] TUI consolidated
- [ ] Small modules merged
- [ ] All tests pass

### Phase 12 ✅
- [ ] Observability consolidated
- [ ] Utilities consolidated
- [ ] All tests pass

### Phase 13 ✅
- [ ] Workflow consolidated
- [ ] Base classes consolidated
- [ ] All tests pass

### Final Steps
- [ ] Create final report
- [ ] Update documentation
- [ ] Celebrate! 🎉

---

**Checklist Created By:** Augment Agent
**Date:** 2025-10-13
**Status:** Ready for execution
**Start with:** Phase 11, Task 11.1
