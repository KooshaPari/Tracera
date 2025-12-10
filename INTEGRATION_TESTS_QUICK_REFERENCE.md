# Integration Scenario Tests - Quick Reference

## Overview
- **36 integration tests** created for cross-module workflows
- **50+ template framework** for future expansion
- **Target:** +5% coverage improvement
- **Status:** Ready for async compatibility fixes

## Test Files

### Core Integration Tests
```bash
# Location
tests/integration/workflows/test_cross_module_workflows.py

# Test Classes (6 classes, 21 tests)
- TestItemCreationLinkingSyncExport (4 tests)
- TestProjectSetupItemManagementWorkflow (3 tests)
- TestSyncAndConflictWorkflows (4 tests)
- TestBulkOperationsWithRollback (4 tests)
- TestAdvancedIntegrationPatterns (4 tests)
- TestStateConsistencyAndRecovery (2 tests)
```

### Advanced Scenarios
```bash
# Location
tests/integration/workflows/test_advanced_scenarios.py

# Test Classes (7 classes, 15 tests)
- TestComplexDependencyWorkflows (4 tests)
- TestConcurrentAccessAndLocking (3 tests)
- TestDataMigrationAndTransformation (3 tests)
- TestExportImportCycles (3 tests)
- TestErrorRecoveryAndResilience (2 tests)
```

## Running Tests

### Run all integration workflow tests
```bash
pytest tests/integration/workflows/ -v
```

### Run specific test class
```bash
pytest tests/integration/workflows/test_cross_module_workflows.py::TestItemCreationLinkingSyncExport -v
```

### Run specific test
```bash
pytest tests/integration/workflows/test_cross_module_workflows.py::TestItemCreationLinkingSyncExport::test_create_item_link_sync_export_happy_path -v
```

### Run with coverage
```bash
pytest tests/integration/workflows/ --cov=src/tracertm --cov-report=html
```

## Test Categories

### 1. Item Lifecycle (4 tests)
Tests complete item creation → linking → sync → export flow
- Happy path item workflow
- Dependent status transitions
- Bulk linking at scale
- Export after modifications

### 2. Project Management (3 tests)
Tests project creation and item management
- Project creation with items
- Bulk item updates
- Cascading updates

### 3. Sync & Conflict (4 tests)
Tests synchronization and conflict resolution
- Bidirectional sync
- Conflict detection
- Rollback on error
- Merge resolution

### 4. Bulk Operations (4 tests)
Tests bulk CRUD with transaction safety
- Bulk create with links
- Selective rollback
- Cascade delete
- State transitions

### 5. Advanced Patterns (4 tests)
Tests complex graph and multi-view operations
- Graph analysis
- Impact analysis
- Cross-view references
- Multi-project isolation

### 6. State Consistency (2 tests)
Tests data consistency and recovery
- Partial commit consistency
- Orphan link recovery

### 7-11. Advanced Scenarios (15 tests)
Complex dependencies, concurrent access, data migration, export/import cycles, error recovery

## Coverage Targets

### Before Integration Tests
- Cross-module coverage: ~30-35%

### After Integration Tests
- Cross-module coverage: ~35-40%
- **Improvement: +5% (target)**

## Key Integration Points Tested

| Point | Tests | Services |
|-------|-------|----------|
| ItemRepo ↔ LinkRepo | 11 | Item + Link management |
| ProjectRepo ↔ ItemRepo | 3 | Project + Item lifecycle |
| SyncService ↔ ConflictResolver | 4 | Sync + Conflict handling |
| BulkOpService ↔ Repos | 4 | Bulk operations |
| GraphService ↔ LinkRepo | 4 | Graph analysis |

## Files Location

```
tests/integration/workflows/
├── test_cross_module_workflows.py (1,181 lines, 21 tests)
├── test_advanced_scenarios.py (850+ lines, 15 tests)
└── INTEGRATION_SCENARIOS_SUMMARY.md
```

---

**Created:** December 10, 2024
**Status:** Ready for Execution
**Target:** +5% coverage improvement
