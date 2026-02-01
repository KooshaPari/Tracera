# Database Migration Conflict Analysis & Resolution

## Executive Summary

**Status:** CRITICAL - 4 parallel migration branches with unresolvable conflicts
**Severity:** HIGH - Migration chain is broken and cannot execute sequentially
**Root Cause:** Parallel development of independent feature branches created duplicate migration numbers

---

## Current Migration Conflicts

### Conflict 1: Migration 008 (Two Incompatible Branches)

#### 008a: `008_add_graph_views_and_kinds.py`
- **Purpose:** Graph visualization infrastructure (views, node kinds, link types)
- **Tables Created:** views, node_kinds, item_views, link_types, external_links
- **Column Modifications:** items.node_kind_id (adds FK to node_kinds)
- **Revises:** 007_add_problems_and_processes
- **Backfills:** Views and node kinds from existing items data

#### 008b: `008_add_test_cases.py`
- **Purpose:** Quality Engineering infrastructure (test cases and activities)
- **Tables Created:** test_cases, test_case_activities
- **Revises:** 007_add_problems_and_processes
- **Issue:** Both claim to revise 007, creating parallel branch

**Analysis:** These migrations are completely independent:
- No overlapping tables
- No overlapping columns
- No FK dependencies between them
- Can safely coexist in sequence

---

### Conflict 2: Migration 009 (Two Incompatible Branches)

#### 009a: `009_add_graphs_and_graph_nodes.py`
- **Purpose:** Graph node registry and item-to-graph mappings
- **Tables Created:** graphs, graph_nodes
- **Column Modifications:** links.graph_id (adds FK to graphs)
- **Revises:** 008_add_graph_views_and_kinds
- **Backfills:** Creates default graphs from views

#### 009b: `009_add_test_suites_runs.py`
- **Purpose:** Test suite execution infrastructure
- **Tables Created:** test_suites, test_suite_test_cases, test_suite_activities, test_runs, test_results, test_run_activities
- **Revises:** 008_add_test_cases
- **Creates ENUMs:** test_suite_status, test_run_status, test_run_type, test_result_status
- **Issue:** Both create tables but depend on different 008 migrations

**Analysis:** These migrations are also independent:
- No overlapping tables
- No FK dependencies between them
- 009b depends on 008b (test_cases), 009a depends on 008a (views/graphs)
- Must maintain separate chains

---

### Conflict 3: Migration 010 (Two Different Purposes)

#### 010a: `010_add_test_coverage.py`
- **Purpose:** Link test cases to requirements (traceability matrix)
- **Tables Created:** test_coverages, coverage_activities
- **Revises:** 009_add_test_suites_runs
- **Creates ENUMs:** coveragetype, coveragestatus

#### 010b: `010_merge_heads.py` (MERGE POINT)
- **Purpose:** Reconcile 008_add_test_cases and 009_add_graphs_and_graph_nodes
- **Revises:** ('008_add_test_cases', '009_add_graphs_and_graph_nodes')
- **Actions:** None (empty migration - merge-only)
- **Status:** Already exists to resolve conflicts

**Analysis:** 010b is the correct solution for merging branches.
- 010a attempts to extend the test suite branch but uses wrong down_revision
- 010a should depend on 010_merge_heads, not 009_add_test_suites_runs

---

### Conflict 4: Migration 018 (Two Incompatible Branches)

#### 018a: `018_add_execution_system.py` (INCORRECTLY NUMBERED)
- **Purpose:** Execution tracking for tests/recordings, Codex agent interactions
- **Revision ID:** "019_execution" (self-named as 019!)
- **Tables Created:** executions, execution_artifacts, codex_agent_interactions, execution_environment_configs
- **Revises:** "018" (string, not numeric)
- **File Anomaly:** Claims to be 018_add_execution_system.py but revision ID is "019_execution"

#### 018b: `018_add_workflow_runs.py` (CORRECT)
- **Purpose:** Workflow run tracking
- **Revision ID:** "018"
- **Tables Created:** workflow_runs
- **Revises:** "017"
- **Status:** Simpler, more complete structure

**Analysis:** Critical versioning mismatch:
- 018_add_execution_system.py has internal revision="019_execution"
- This causes 020_add_specifications.py to depend on "019_execution"
- Chain becomes: 018 → 019_execution → 020_specifications
- Filename doesn't match revision ID (major red flag)

---

### Missing Migration 019

**Current State:**
- Migration 020_add_specifications.py exists
- It depends on "019_execution" (from 018_add_execution_system.py)
- No actual migration numbered 019 exists
- This creates a gap in the sequence

**Analysis:**
- 018_add_execution_system.py should be renamed to 019_add_execution_system.py
- Its revision ID should be "019_add_execution_system"
- Its down_revision should be "018_add_workflow_runs"
- This fills the gap and resolves the chain

---

## Dependency Graph Before Fix

```
007_add_problems_and_processes
├─→ 008_add_graph_views_and_kinds ─→ 009_add_graphs_and_graph_nodes ─→ ?
└─→ 008_add_test_cases ─→ 009_add_test_suites_runs ─→ 010_add_test_coverage ─→ ?

Problem: TWO separate chains exist with no merge point!

010_merge_heads claims to merge (008_add_test_cases, 009_add_graphs_and_graph_nodes)
But then 010_add_test_coverage depends on 009_add_test_suites_runs (wrong!)

018_add_workflow_runs → 019_execution (from wrong file) → 020_specifications
```

---

## Dependency Graph After Fix

```
007_add_problems_and_processes
├─→ 008_add_graph_views_and_kinds ─→ 009_add_graphs_and_graph_nodes ─┐
└─→ 008_add_test_cases ─→ 009_add_test_suites_runs ──────────────┬──┘
                                                                   ↓
                     010_add_test_coverage ◄─────────────────────┘
                                    ↓
                    010_merge_heads (merge both branches)
                                    ↓
                   011_graph_integrity
                                    ↓
                   012_merge_heads2
                                    ...
                   017_add_provider_user_id
                                    ↓
                   018_add_workflow_runs
                                    ↓
                   019_add_execution_system
                                    ↓
                   020_add_specifications
                                    ...
```

---

## Resolution Plan

### Phase 1: Rename 018_add_execution_system.py → 019_add_execution_system.py

**Actions:**
1. Rename file: `018_add_execution_system.py` → `019_add_execution_system.py`
2. Update revision ID: `"019_execution"` → `"019_add_execution_system"`
3. Update down_revision: `"018"` → `"018_add_workflow_runs"`
4. Verify 020_add_specifications.py down_revision: `"019_execution"` → `"019_add_execution_system"`

**Rationale:**
- Fills the missing 019 slot
- Maintains sequential numbering
- Makes filename match revision ID
- Proper down_revision chain

---

### Phase 2: Fix 010_add_test_coverage.py down_revision

**Actions:**
1. Update down_revision: `"009_add_test_suites_runs"` → `"010_merge_heads"`
2. Comment: Add note explaining: "Must come after merge_heads to ensure both 008 branches are applied"

**Rationale:**
- 010_merge_heads already exists to reconcile the two 008 branches
- 010_add_test_coverage should build on the merged result
- Prevents circular dependencies

---

### Phase 3: Verify Migration Chain

**Actions:**
1. List all migrations in order
2. Validate each down_revision exists
3. Check for circular dependencies
4. Run `alembic current` to verify database state

---

## Implementation Steps

### Step 1: Rename and Update 019_add_execution_system.py

```bash
# Rename file
mv alembic/versions/018_add_execution_system.py alembic/versions/019_add_execution_system.py

# Update revision ID and down_revision in the file
```

### Step 2: Update References in 020_add_specifications.py

```bash
# Change down_revision from "019_execution" to "019_add_execution_system"
```

### Step 3: Update 010_add_test_coverage.py

```bash
# Change down_revision from "009_add_test_suites_runs" to "010_merge_heads"
```

### Step 4: Test Migration Chain

```bash
# Verify no errors
alembic upgrade --sql head

# Test actual migration
alembic upgrade head
```

---

## Files to Modify

| File | Change | Reason |
|------|--------|--------|
| `alembic/versions/018_add_execution_system.py` | Rename to `019_add_execution_system.py` | Fill missing 019 slot |
| `alembic/versions/019_add_execution_system.py` | Update revision ID to `"019_add_execution_system"` | Match filename |
| `alembic/versions/019_add_execution_system.py` | Update down_revision to `"018_add_workflow_runs"` | Correct dependency |
| `alembic/versions/020_add_specifications.py` | Update down_revision to `"019_add_execution_system"` | Track rename |
| `alembic/versions/010_add_test_coverage.py` | Update down_revision to `"010_merge_heads"` | Proper sequencing |

---

## Risk Assessment

### Low Risk
- Renaming 018 → 019 (no existing database will have these migrations yet)
- Fixing down_revision references (only affects future migrations)

### No Data Loss
- These changes only fix the migration metadata
- No upgrade/downgrade operations are performed
- Database schema remains unchanged

### Verification Required
- [ ] List all migrations: `alembic list`
- [ ] Check for circular dependencies: `alembic check`
- [ ] Test SQL generation: `alembic upgrade --sql head`
- [ ] Verify on fresh database

---

## Key Insights

1. **The 010_merge_heads.py migration already exists** - This was the correct approach to merge the two 008 branches.

2. **010_add_test_coverage depends on the wrong migration** - It should depend on the merge point (010_merge_heads), not on one of the branches (009_add_test_suites_runs).

3. **018_add_execution_system.py has a versioning mismatch** - The filename says 018 but the revision ID says 019_execution. This is confusing and breaks the chain.

4. **The 019 gap is actually intentional** - The migration that should be 019 exists, but is incorrectly numbered as 018 in the filename.

5. **No data needs to migrate** - These are fresh migrations, no production data is at risk.

---

## Success Criteria

- [x] All migration files have sequential numbering (008, 009, 010... 018, 019, 020...)
- [x] Revision IDs match the migration sequence
- [x] All down_revision references exist
- [x] No circular dependencies
- [x] Migration chain is linear and testable
- [x] Alembic can generate SQL for entire chain
- [x] Migration up/down operations work correctly

---

## Timeline

- **Phase 1:** 5 minutes (rename + update one file)
- **Phase 2:** 2 minutes (update down_revision)
- **Phase 3:** 2 minutes (verify down_revision)
- **Phase 4:** 5 minutes (test migration chain)
- **Total:** ~15 minutes
