# Phase 14: Code Coverage Expansion - From 56% to 80-95%

**Status**: READY FOR EXECUTION
**Current Coverage**: 56.40% (5,535/14,130 lines)
**Target Coverage**: 80-95% (11,304-13,423 lines)
**Gap**: 5,769-7,888 lines of code to cover
**Estimated Effort**: 8-10 hours
**Timeline**: Can be executed in parallel batches

---

## Executive Summary

With 100% test pass rate achieved (Phases 1-13), we now focus on expanding code coverage from 56% to the 80-95% enterprise standard. The remaining coverage gaps are concentrated in:

1. **TUI Applications** (400 lines, 20-25% coverage)
2. **Storage Layer** (730 lines, 65-70% coverage)
3. **Service Edge Cases** (1,500+ lines, 85-95% coverage)
4. **Helper Functions** (150 lines, 0% coverage)

---

## Coverage Gap Analysis

### Priority 1: Zero-Coverage Files (Highest Impact)
**Total Lines**: 20 lines | **Impact**: Quick wins

- `src/tracertm/testing_factories.py` - 20 lines (0%)
  - Factory functions for test data creation
  - Can be tested by adding factory tests
  - Estimated fix: 0.5 hours, +20 lines coverage

### Priority 2: Critical Low-Coverage (20-30%)
**Total Lines**: 379 lines | **Impact**: Major gaps

1. **TUI Applications** (379 lines)
   - `src/tracertm/tui/apps/browser.py` - 115 lines (25.93%)
   - `src/tracertm/tui/apps/dashboard.py` - 141 lines (21.30%)
   - `src/tracertm/tui/apps/graph.py` - 123 lines (25.90%)

   **Root Cause**: TUI apps require interactive testing
   **Solution**: Add Textual widget tests for each app
   **Estimated Fix**: 3-4 hours, +280 lines coverage
   **Pattern**:
   ```python
   async def test_browser_app_renders():
       app = BrowserApp()
       async with app.run_test() as pilot:
           # Test navigation, rendering
   ```

### Priority 3: Storage Layer (65-70% coverage)
**Total Lines**: 730 lines | **Impact**: Core functionality

1. `src/tracertm/storage/file_watcher.py` - 191 lines (65.27%)
   - Missing: Exception paths, edge cases
   - Add: File event edge cases, filter logic
   - Estimated: 1-1.5 hours, +60 lines

2. `src/tracertm/storage/sync_engine.py` - 278 lines (65.72%)
   - Missing: Error handling, retry logic
   - Add: Network failures, conflict scenarios
   - Estimated: 1.5-2 hours, +90 lines

3. `src/tracertm/storage/markdown_parser.py` - 263 lines (66.49%)
   - Missing: Complex parsing scenarios
   - Add: Malformed markdown, edge cases
   - Estimated: 1.5-2 hours, +85 lines

4. `src/tracertm/storage/local_storage.py` - 566 lines (82.97%)
   - Missing: Error paths, partial operations
   - Add: Database errors, recovery scenarios
   - Estimated: 1-1.5 hours, +100 lines

### Priority 4: Service Edge Cases (85-95% coverage)
**Total Lines**: 2,500+ lines | **Impact**: Comprehensive coverage

Services like query_service.py, search_service.py, etc. have good base coverage but missing edge cases:
- Exception handling paths
- Concurrent operation scenarios
- Resource cleanup
- Estimated: 2-3 hours, +300+ lines

---

## Execution Plan (8-10 hours total)

### Batch 1: Zero-Coverage Files (0.5 hours)
**Scope**: testing_factories.py only
**Task**: Create factory tests
```bash
# Create tests/unit/test_factories.py
# Test each factory function
# Target: 100% coverage
```
**Result**: +20 lines covered

### Batch 2: TUI Applications (3-4 hours)
**Scope**: browser.py, dashboard.py, graph.py

**Task 2A**: BrowserApp widget tests (1.5 hours)
```python
tests/tui/test_browser_app.py
- test_browser_renders_items
- test_browser_navigation
- test_browser_search
- test_browser_error_handling
```

**Task 2B**: DashboardApp widget tests (1 hour)
```python
tests/tui/test_dashboard_app.py
- test_dashboard_displays_stats
- test_dashboard_updates_on_change
- test_dashboard_error_display
```

**Task 2C**: GraphApp widget tests (1-1.5 hours)
```python
tests/tui/test_graph_app.py
- test_graph_renders_nodes
- test_graph_renders_edges
- test_graph_layout_algorithms
```

**Result**: +280 lines covered

### Batch 3: Storage Layer (4-5 hours)
**Scope**: file_watcher.py, sync_engine.py, markdown_parser.py, local_storage.py

**Task 3A**: FileWatcher edge cases (1 hour)
```python
tests/component/storage/test_file_watcher_edge_cases.py
- test_watcher_handles_rapid_changes
- test_watcher_handles_deleted_files
- test_watcher_debounce_timing
- test_watcher_exception_recovery
```

**Task 3B**: SyncEngine error scenarios (1.5 hours)
```python
tests/component/storage/test_sync_engine_errors.py
- test_sync_network_timeout_retry
- test_sync_database_lock_handling
- test_sync_conflict_resolution_complex
- test_sync_rollback_on_failure
```

**Task 3C**: Markdown parsing edge cases (1 hour)
```python
tests/component/storage/test_markdown_parser_edge_cases.py
- test_parse_malformed_yaml
- test_parse_missing_links
- test_parse_unicode_characters
- test_parse_very_long_content
```

**Task 3D**: LocalStorage recovery paths (1-1.5 hours)
```python
tests/component/storage/test_local_storage_recovery.py
- test_initialize_with_corrupted_index
- test_register_project_handles_duplicates
- test_partial_sync_cleanup
- test_database_transaction_rollback
```

**Result**: +335 lines covered

### Batch 4: Service Edge Cases (2-3 hours)
**Scope**: All service files needing exception/concurrency tests

**Examples**:
```python
tests/component/services/test_query_service_edge_cases.py
- test_query_concurrent_updates
- test_query_with_circular_dependencies
- test_query_large_dataset_performance

tests/component/services/test_search_service_concurrency.py
- test_search_concurrent_index_updates
- test_search_index_corruption_recovery
- test_search_memory_efficiency
```

**Result**: +300+ lines covered

---

## Success Metrics

### Coverage Targets by Layer
| Layer | Current | Target | Gap | Est. Hours |
|-------|---------|--------|-----|-----------|
| TUI Apps | 21-25% | 80%+ | ~280 lines | 3-4 |
| Storage | 65-70% | 85%+ | ~335 lines | 4-5 |
| Services | 85-95% | 90%+ | ~300 lines | 2-3 |
| Factories | 0% | 100% | ~20 lines | 0.5 |
| **TOTAL** | **56.40%** | **75-80%** | **~935 lines** | **8-10** |

### Final Coverage Goals
- **Minimum**: 75% overall (10,597 lines)
- **Target**: 80% overall (11,304 lines)
- **Stretch**: 85% overall (12,010 lines)

---

## Implementation Strategy

### Sequential Execution (Recommended)
1. **Week 1**: Batch 1 + Batch 2 (3.5-4.5 hours)
   - Quick wins + TUI coverage
   - Parallel: Widget tests can run in parallel

2. **Week 2**: Batch 3 (4-5 hours)
   - Storage layer comprehensive coverage
   - Sequence: file_watcher → sync_engine → markdown_parser → local_storage

3. **Week 3**: Batch 4 (2-3 hours)
   - Service edge cases
   - Parallel: Each service can be tested independently

### Parallel Execution (Fast-track)
- Run Batch 1, 2, and 3A in parallel
- Run Batch 3B, 3C, 3D sequentially after 3A completes
- Run Batch 4 independently

---

## Testing Patterns to Use

### Pattern 1: TUI Widget Testing
```python
@pytest.mark.asyncio
async def test_widget_renders():
    app = MyApp()
    async with app.run_test() as pilot:
        # Query and interact with widgets
        assert app.query("ItemList")
```

### Pattern 2: Exception Path Testing
```python
@patch('module.external_call')
def test_error_recovery(mock_call):
    mock_call.side_effect = Exception("Network error")
    result = function_under_test()
    assert result.error_handled
    assert result.retry_attempted
```

### Pattern 3: Concurrency Testing
```python
@pytest.mark.asyncio
async def test_concurrent_operations():
    tasks = [operation() for _ in range(10)]
    results = await asyncio.gather(*tasks)
    assert len(results) == 10
    assert all(r.success for r in results)
```

### Pattern 4: Edge Case Testing
```python
@pytest.mark.parametrize("input,expected", [
    ("", empty_result),
    ("\n" * 100, valid_result),
    ("🎉", unicode_result),
])
def test_edge_cases(input, expected):
    result = parse(input)
    assert result == expected
```

---

## Files to Create

**New Test Files** (Will be created during execution):
- `tests/unit/test_factories.py` (20 lines)
- `tests/tui/test_browser_app.py` (80 lines)
- `tests/tui/test_dashboard_app.py` (70 lines)
- `tests/tui/test_graph_app.py` (75 lines)
- `tests/component/storage/test_file_watcher_edge_cases.py` (60 lines)
- `tests/component/storage/test_sync_engine_errors.py` (100 lines)
- `tests/component/storage/test_markdown_parser_edge_cases.py` (80 lines)
- `tests/component/storage/test_local_storage_recovery.py` (95 lines)
- `tests/component/services/test_*_edge_cases.py` (300+ lines)

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|-----------|
| TUI tests flaky | Med | Use Textual testing framework properly |
| Concurrency race conditions | Med | Use asyncio locks, deterministic tests |
| Storage layer complexity | High | Focus on documented paths first |
| Time underestimation | Med | Batch execute, track progress |

---

## Deployment Instructions

### Phase 14A: Zero Coverage (0.5 hours)
```bash
Task(
  subagent_type='qa-test-coverage-expert',
  prompt="Create tests for testing_factories.py to reach 100% coverage"
)
```

### Phase 14B: TUI Applications (3-4 hours)
```bash
Task(
  subagent_type='qa-test-coverage-expert',
  prompt="Add Textual widget tests for browser.py, dashboard.py, graph.py"
)
```

### Phase 14C: Storage Layer (4-5 hours)
```bash
Task(
  subagent_type='qa-test-coverage-expert',
  prompt="Add edge case and error scenario tests for storage layer"
)
```

### Phase 14D: Service Edge Cases (2-3 hours)
```bash
Task(
  subagent_type='qa-test-coverage-expert',
  prompt="Add concurrency and exception tests for service layer"
)
```

---

## Next Steps

1. **Review this plan** - Confirm scope and timeline
2. **Execute Batch 1** - Quick wins with zero-coverage files
3. **Execute Batch 2** - TUI widget coverage
4. **Execute Batch 3** - Storage layer comprehensive testing
5. **Execute Batch 4** - Service layer edge cases
6. **Final validation** - Ensure 75-80% coverage achieved
7. **Documentation** - Create coverage improvement guide

---

## Conclusion

Phase 14 will systematically expand coverage from 56% to 75-80% by targeting:
- Zero-coverage files (quick wins)
- Critical TUI layer gaps (major impact)
- Storage layer edge cases (robustness)
- Service layer concurrency (reliability)

With proven testing patterns and clear execution plan, 80% coverage is achievable in 8-10 hours.

---

**Status**: Ready for Phase 14 execution
**Last Updated**: 2025-12-03
**Initiative Progress**: 100% pass rate complete, coverage expansion phase ready
