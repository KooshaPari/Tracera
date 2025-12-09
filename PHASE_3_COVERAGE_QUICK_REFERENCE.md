# Phase 3 Coverage Optimization - Quick Reference

**Phase Target**: 95%+ coverage across all critical paths
**Timeline**: 10 weeks
**Effort**: 60-75 hours focused work
**Current Status**: 93% (1,670+/1,795 tests)

---

## Tier 1: CRITICAL PATH (Weeks 1-2, 15 hours)

### 1. BulkOperationService [310 min = 5.2h]
**File**: `src/tracertm/services/bulk_operation_service.py` (196 statements)

```
Methods to test (5 total):
✓ bulk_update_preview()        [45 min] - Filter validation, sample generation
✓ bulk_update_items()          [60 min] - Atomic updates, event logging
✓ bulk_delete_items()          [40 min] - Soft deletes with audit
✓ bulk_create_preview()        [90 min] - CSV validation, metadata parsing
✓ bulk_create_items()          [75 min] - Bulk creation from CSV
```

**Key Test Focus**:
- CSV parsing (header validation, row validation, metadata JSON)
- Filter combinations (view, status, type, priority, owner)
- Event logging for audit trail
- Transaction atomicity
- Warning generation (large ops, duplicates, mixed status)

---

### 2. StatusWorkflowService [115 min = 1.9h]
**File**: `src/tracertm/services/status_workflow_service.py` (34 statements)

```
Methods to test (3 total):
✓ validate_transition()    [30 min] - State machine validation
✓ update_item_status()     [50 min] - Status updates with events
✓ get_status_history()     [35 min] - Audit trail retrieval
```

**Key Test Focus**:
- State machine: 5 statuses, 8 valid transitions
- Transition validation (todo→in_progress→done→todo)
- Terminal state (archived)
- Event logging with timestamps
- Progress mapping (todo:0, in_progress:50, done:100)

**State Transitions**:
```
todo ──→ in_progress, blocked
in_progress ──→ done, blocked, todo
blocked ──→ todo, in_progress
done ──→ todo (reopening)
archived ──→ TERMINAL (no transitions)
```

---

### 3. StorageHelper [455 min = 7.6h]
**File**: `src/tracertm/cli/storage_helper.py` (206 statements)

```
Methods to test (13 total):
✓ get_storage_manager()          [30 min] - Singleton pattern
✓ reset_storage_manager()        [15 min] - Test isolation
✓ get_current_project()          [25 min] - Project context
✓ require_project() [DECORATOR]  [35 min] - CLI guard
✓ with_sync() [DECORATOR]        [40 min] - Auto-sync trigger
✓ _trigger_sync()                [35 min] - Sync execution
✓ show_sync_status()             [45 min] - Status display
✓ _human_time_delta()            [30 min] - Time formatting
✓ format_item_for_display()      [40 min] - Item rendering
✓ format_link_for_display()      [35 min] - Link rendering
✓ format_items_table()           [35 min] - List rendering
✓ format_links_table()           [30 min] - Link list rendering
✓ handle_storage_error() [DEC]   [35 min] - Error handling
```

**Key Test Focus**:
- Singleton pattern (reuse, reset, config integration)
- Decorator pattern (args forwarding, return value preservation)
- Config manager integration (custom dir, defaults)
- Rich formatting (colors, truncation, tables)
- Error handling (FileNotFoundError, ValueError, generic)
- Time delta formatting (seconds to "X days ago")

---

## Tier 2: IMPORTANT FEATURES (Weeks 3-5, 18 hours)

### 4. DashboardV2 [180 min = 3h]
- Widget initialization, rendering, refresh, navigation

### 5. SyncStatusWidget [120 min = 2h]
- Status updates, rendering, callbacks

### 6. AdvancedTraceabilityService [100 min = 1.7h]
- Traceability matrix generation, relationship analysis

### 7-15. Additional Services [1,100 min = 18h total]
- ExportImportService, ImpactAnalysisService
- TraceabilityMatrixService, CriticalPathService
- ExportService, AdvancedAnalyticsService
- ApiWebhooksService, GithubImportService
- AgentPerformanceService

---

## Tier 3: NICE-TO-HAVE (Weeks 6-8, 18 hours)

### Schemas & Factories [150 min]
- item.py, link.py, event.py, testing_factories.py

### CLI & Utilities [200 min]
- help_system.py, mvp_shortcuts.py, performance.py, logging_config.py

### TUI Widgets & Adapters [350 min]
- view_switcher, state_display, conflict_panel, item_list, graph_view
- storage_adapter, browser, graph, dashboard apps

### Integration Services [400 min]
- figma.py, plugin_service.py, external_integration_service.py
- project_backup_service.py, jira_import_service.py, cache_service.py

---

## Quick Test Checklist

### For Each Service:
- [ ] Unit tests with mocked dependencies
- [ ] Integration tests with real database
- [ ] Edge case coverage (empty, None, boundary values)
- [ ] Error path validation (exceptions, rollbacks)
- [ ] Performance baseline (if applicable)
- [ ] Event logging verification
- [ ] Transaction atomicity (for data mutations)

### For Each Method:
- [ ] Happy path (normal execution)
- [ ] Error conditions (invalid input)
- [ ] Boundary cases (min/max values)
- [ ] Empty/null handling
- [ ] Type validation

---

## Testing Quick Start

### Test Structure Template
```python
import pytest
from unittest.mock import Mock, patch
from src.tracertm.services.bulk_operation_service import BulkOperationService
from src.tracertm.models import Item, Event

@pytest.fixture
def session():
    """Mock SQLAlchemy session"""
    return Mock()

@pytest.fixture
def service(session):
    """Service under test"""
    return BulkOperationService(session)

class TestBulkUpdatePreview:
    def test_basic_preview(self, service, session):
        # Arrange
        session.query.return_value.filter.return_value.count.return_value = 50
        session.query.return_value.filter.return_value.limit.return_value.all.return_value = []

        # Act
        result = service.bulk_update_preview(
            project_id="proj-1",
            filters={"status": "todo"},
            updates={"status": "in_progress"}
        )

        # Assert
        assert result["total_count"] == 50
        assert len(result["sample_items"]) == 0
        assert "warnings" in result
```

---

## Coverage Targets by Tier

| Tier | Target | Files | Statements | Est. Time |
|------|--------|-------|-----------|-----------|
| 1 | 95%+ | 3 | 436 | 15h |
| 2 | 85%+ | 9 | ~900 | 18h |
| 3 | 75%+ | 20+ | ~1,000 | 18h |
| **TOTAL** | **95%** | **32+** | **~2,300** | **51h** |

---

## Weekly Milestones

**Week 1**:
- [ ] BulkOperationService coverage 95%+
- [ ] StatusWorkflowService coverage 100%

**Week 2**:
- [ ] StorageHelper coverage 95%+
- [ ] 15+ hours of Tier 1 tests complete

**Week 3-4**:
- [ ] DashboardV2, SyncStatusWidget coverage 85%+
- [ ] 5+ additional services covered

**Week 5-8**:
- [ ] All Tier 2 services 85%+
- [ ] Tier 3 schemas and utilities 75%+

**Week 9-10**:
- [ ] Gap filling and optimization
- [ ] Performance baselines set
- [ ] All tests green

---

## Common Pitfalls to Avoid

1. **Incomplete Fixture Setup**
   - Always mock external dependencies
   - Pre-populate test data consistently

2. **Missing Edge Cases**
   - Empty results, None values, boundary conditions
   - Large operations (100+, 1000+ items)

3. **Event Logging Not Tested**
   - Verify Event objects created correctly
   - Check audit trail integrity

4. **Transaction Behavior Ignored**
   - Test rollback on error
   - Verify atomicity constraints

5. **Performance Not Measured**
   - Set baselines for bulk operations
   - Monitor regression

---

## Key Files Reference

**Tier 1** (Must have 95%+):
```
src/tracertm/services/bulk_operation_service.py
src/tracertm/services/status_workflow_service.py
src/tracertm/cli/storage_helper.py
```

**Tier 2** (Should have 85%+):
```
src/tracertm/tui/apps/dashboard_v2.py
src/tracertm/tui/widgets/sync_status.py
src/tracertm/services/advanced_traceability_enhancements_service.py
```

**Tier 3** (Nice to have 75%+):
```
src/tracertm/schemas/*.py
src/tracertm/tui/widgets/*.py
src/tracertm/services/*_service.py (remaining)
```

---

## Commands to Run

```bash
# Generate coverage report
python -m pytest --cov=src --cov-report=html --cov-report=term-missing

# Run specific service tests
pytest tests/integration/test_bulk_operation_service.py -v

# Check coverage for single file
python -m pytest --cov=src/tracertm/services/bulk_operation_service --cov-report=term-missing

# Run with coverage minimum threshold
pytest --cov=src --cov-fail-under=95 --cov-report=html
```

---

## Support & Questions

Refer to main analysis document: `PHASE_3_COVERAGE_GAP_ANALYSIS.md`

For implementation questions:
1. Check test pattern in existing tests
2. Review fixture definitions in conftest.py
3. Consult service docstrings for business logic

---

**Last Updated**: 2024-12-09
**Version**: 1.0
