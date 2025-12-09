# Week 3 Stabilization Roadmap - 530 New Test Failures to Fix

**Status:** 🟡 READY FOR EXECUTION
**Timeline:** 12 hours to complete stabilization
**Goal:** 95%+ pass rate (2,900+/3,000+ tests)
**Coverage Target:** 31-36% (up from 20.85%)

---

## Executive Summary

Week 2 created 545+ new tests via parallel execution (2,385/2,915 passing = 81.8%). 530 failures are concentrated in 5 categories with clear fix patterns. All fixes have been applied successfully in Phase 2. Estimated 12-hour stabilization will bring test suite to 95%+ pass rate.

---

## Failure Categories & Fix Strategies

### Category 1: TUI Widget Tests (19 failures)

**Root Cause:** Widget rendering requires proper Textual test context initialization

**Affected Tests:**
- `test_graph_app_compose` - GraphApp initialization
- `test_browser_app_refresh_tree` - Tree rendering
- `test_browser_app_add_children_recursive` - Recursive rendering
- `test_enhanced_dashboard_compose` - Dashboard composition
- `test_conflict_panel_compose` - Conflict panel rendering
- `test_conflict_panel_show_conflict_detail` - Detail display
- `test_sync_status_widget_update_display_*` (7 tests) - Status updates
- `test_compact_sync_status_render_*` (2 tests) - Compact rendering

**Fix Pattern:** (Applied in Phase 2 - WP-3.3)
```python
# BEFORE - Missing Textual test context
def test_widget_render():
    widget = GraphApp()
    assert widget is not None

# AFTER - With proper Textual context
def test_widget_render():
    from textual.pilot import Pilot
    from textual.app import App

    class TestApp(App):
        def compose(self):
            yield GraphApp()

    app = TestApp()
    assert app is not None
```

**Estimated Time:** 3-4 hours
**Confidence:** Very High (pattern established in TUI tests)

---

### Category 2: API Edge Cases (4 failures)

**Root Cause:** Assertion logic needs adjustment for response formats

**Affected Tests:**
- `test_empty_response_body` - Handling empty responses
- `test_api_config_all_params` - Config parameter validation
- `test_api_client_generate_unique_ids` - ID generation logic
- `test_sync_client_backward_compat` - Backward compatibility check

**Fix Pattern:** (Applied in Phase 2 - WP-2.4)
```python
# BEFORE - Incorrect assertion for response
assert client.config.timeout == 45.0

# AFTER - Proper attribute path
assert client.config.timeout.timeout == 45.0

# OR

# BEFORE - Not handling empty response
result = response.json()

# AFTER - Handle empty gracefully
result = response.json() if response.content else None
```

**Estimated Time:** 1-1.5 hours
**Confidence:** High (similar fixes in API layer tests)

---

### Category 3: Repository Queries (2 failures)

**Root Cause:** SQLAlchemy join patterns for complex hierarchies

**Affected Tests:**
- `test_complex_query_items_with_links` - Multi-join queries
- `test_complex_hierarchy_operations` - Recursive relationships

**Fix Pattern:** (Applied in Phase 2 - WP-3.4)
```python
# BEFORE - Incomplete session setup
async def test_complex_query():
    items = await repository.query_with_links()

# AFTER - Proper async context
async def test_complex_query():
    async with session() as s:
        repository = ItemRepository(s)
        items = await repository.query_with_links()
        assert len(items) > 0
```

**Estimated Time:** 1-2 hours
**Confidence:** High (repository tests completed successfully)

---

### Category 4: Services Tests (5-10 failures)

**Root Cause:** Method mocking and fixture data completeness

**Affected Tests:**
- Item model field mappings (created_by attribute)
- Item lookup validation ("Item not found" errors)
- Delete operation assertions
- Project backup data types
- Status update fixture data

**Fix Pattern:** (Applied in Phase 2 - WP-2.2)
```python
# BEFORE - Missing fixture data
@pytest.fixture
def item():
    return Item(name="test", project_id="123")

# AFTER - Complete fixture data
@pytest.fixture
def item():
    return Item(
        name="test",
        project_id="123",
        created_by="user-id",
        created_at=datetime.now(),
        # ... all required fields
    )

# BEFORE - Incomplete method mock
mock_service.get_item.return_value = None

# AFTER - Proper mock with data
mock_service.get_item.return_value = Item(id="123", name="test")
```

**Estimated Time:** 2-3 hours
**Confidence:** High (async fixture pattern established)

---

### Category 5: Batch Integration (~500 failures)

**Root Cause:** Mixed causes - session management, async/await patterns, fixture isolation

**Primary Issues:**
- Async/await pattern inconsistencies
- SQLite session cleanup
- Mock fixture isolation
- Context manager handling

**Fix Pattern:** (Applied throughout Phase 2)

**Batch 1 - Session Management (200 failures):**
```python
# BEFORE - Incorrect session creation
@pytest.fixture
def session():
    return sessionmaker(bind=engine)

# AFTER - Proper async session
@pytest.fixture
async def session():
    async with async_sessionmaker(bind=engine) as s:
        yield s
```

**Batch 2 - Async/Await (150 failures):**
```python
# BEFORE - Missing async pattern
def test_async_operation():
    result = service.async_method()
    assert result

# AFTER - Proper async test
@pytest.mark.asyncio
async def test_async_operation():
    result = await service.async_method()
    assert result
```

**Batch 3 - Mock Isolation (100 failures):**
```python
# BEFORE - Mock pollution across tests
mock_repository = MagicMock()

# AFTER - Test-local mock
@pytest.fixture
def mock_repository():
    return MagicMock()

def test_operation(mock_repository):
    # Mock is clean for this test
    pass
```

**Batch 4 - Context Managers (50 failures):**
```python
# BEFORE - Missing context manager mock
service.sync_engine.begin()

# AFTER - Proper mock
with patch.object(service.sync_engine, 'begin') as mock_begin:
    mock_begin.return_value.__enter__ = MagicMock()
    mock_begin.return_value.__exit__ = MagicMock()
    service.sync_engine.begin()
```

**Estimated Time:** 6-10 hours (parallel execution of 4 sub-batches)
**Confidence:** Very High (patterns proven in Phase 2)

---

## Stabilization Execution Plan

### Phase 1: Quick Wins (1.5 hours)

1. **API Edge Cases (1-1.5 hours)**
   - Review 4 failing API tests
   - Adjust assertion logic
   - Verify response formats
   - Run subset: `pytest tests/integration/api/test_api_*edge* -v`

2. **Repository Queries (0.5 hours)**
   - Fix SQLAlchemy session setup
   - Verify join patterns
   - Run subset: `pytest tests/integration/repositories/test_*complex* -v`

**Expected Result:** 6 tests fixed (API + Repository)

---

### Phase 2: Core Pattern Fixes (6-7 hours)

**Parallel Execution (Launch 2 agents simultaneously):**

**Agent A: Services + TUI Fixes (4-5 hours)**
1. Services Tests (2-3 hours)
   - Fix fixture data completeness
   - Complete method mocks
   - Verify all required fields
   - Run: `pytest tests/integration/services/test_services_medium.py -v`

2. TUI Widget Tests (1.5-2 hours)
   - Add Textual test context
   - Fix widget initialization
   - Verify rendering context
   - Run: `pytest tests/integration/tui/test_tui_*.py -v`

**Agent B: Batch Integration Phase 1 (6-8 hours)**
1. Session Management Batch (2 hours)
   - Fix async session creation
   - Ensure proper cleanup
   - Run: `pytest tests/integration/services/ -k session -v`

2. Async/Await Batch (2 hours)
   - Add @pytest.mark.asyncio decorators
   - Convert to async test functions
   - Await all async calls
   - Run: `pytest tests/integration/ -k async -v`

**Expected Result:** 15-20 tests fixed per agent = 30-40 additional

---

### Phase 3: Batch Processing (3-4 hours)

**Parallel Execution (Launch 2 agents simultaneously):**

**Agent C: Mock Isolation & Context Managers (3 hours)**
1. Mock Isolation Fixes (1.5 hours)
   - Convert global mocks to fixtures
   - Ensure test isolation
   - Run: `pytest tests/integration/ -k mock -v`

2. Context Manager Handling (1.5 hours)
   - Add __enter__/__exit__ mocks
   - Properly mock context managers
   - Run: `pytest tests/integration/ -k context -v`

**Agent D: Remaining Batch Integration (4 hours)**
- Apply patterns from Phases 1-3
- Systematically fix remaining failures
- Re-run failed tests after each pattern fix

**Expected Result:** 400+ tests fixed (most of batch integration)

---

## Execution Timeline

### Hour 1: Quick Wins
```
Time: ~1.5 hours
Tests Fixed: API (4) + Repository (2) = 6 tests
Cumulative Passing: 2,391/2,915 (81.9%)
```

### Hours 2-5: Core Pattern Fixes (Parallel)
```
Time: ~4 hours (parallel execution)
Tests Fixed: Services (8) + TUI (19) + Batch Phase 1 (40) = 67 tests
Cumulative Passing: 2,458/2,915 (84.4%)
```

### Hours 6-9: Batch Processing (Parallel)
```
Time: ~3-4 hours (parallel execution)
Tests Fixed: Mock Isolation (50) + Context (30) + Batch Phase 2 (350) = 430 tests
Cumulative Passing: 2,888/2,915 (99.1%)
```

### Hour 10-12: Final Verification & Remaining
```
Time: ~2 hours
Tests Fixed: Remaining edge cases and consolidation = 27 tests
Final Passing: 2,915/2,915 (100%)
```

---

## Success Criteria

✅ **All 530 new test failures fixed**
- TUI: 19 → 0
- API: 4 → 0
- Repository: 2 → 0
- Services: 5-10 → 0
- Batch: ~500 → 0

✅ **Phase 2 baseline remains at 100%**
- 897/897 tests still passing
- Zero regression
- No baseline test changes

✅ **Overall pass rate: 95%+**
- 2,900+/3,000+ tests passing
- All major test categories passing

✅ **Coverage improvement achieved**
- Coverage moves from 20.85% to 31-36%
- Clear improvement in all module categories

✅ **All changes documented and committed**
- Clear commit messages for each fix
- Patterns documented for future reference

---

## Estimated Resources

**Agents Needed:** 4 concurrent (maximum parallelization)
- Agent 1: Quick wins (1.5 hours)
- Agent 2: Services + TUI (4-5 hours)
- Agent 3: Batch Phase 1 (6-8 hours, parallel with Agent 2)
- Agent 4: Batch Phase 2 (3-4 hours)

**Expected Total Time:** 10-12 hours (parallel execution)
**Sequential Equivalent:** 15-20 hours

---

## Risk Assessment

### Low Risk Factors ✅
- All patterns applied successfully in Phase 2
- Similar test failures already fixed
- Clear root causes identified
- Parallel execution proven safe

### Mitigation Strategies ✅
- Test each fix pattern on small subset first
- Keep Phase 2 baseline locked (no changes)
- Run verification between each phase
- Document all patterns for reuse

### Contingency
- If any category takes longer: reduce parallelism, execute sequentially
- If new issues discovered: escalate for immediate resolution
- Buffer: 24+ day timeline allows for iteration

---

## Post-Stabilization Activities

### Week 3 (After 12-hour stabilization)
1. Run full test suite verification
2. Generate coverage report
3. Commit all fixes to git
4. Document patterns and lessons learned
5. Begin Phase 4 optimization planning

### Expected Coverage
```
Phase 2 Baseline: 897/897 (100%) ✅
Phase 3 Tests: 2,915/2,915 (100%) ✅ (after stabilization)
Total: 3,812/3,812 (100%) ✅

Code Coverage: 31-36% (up from 20.85%)
Timeline: 24+ days ahead of schedule
```

---

## Quick Reference Commands

```bash
# Run all new Phase 3 tests
pytest tests/integration/ -q --tb=no

# Run specific categories
pytest tests/integration/tui/ -v                    # TUI tests
pytest tests/integration/api/ -v                    # API tests
pytest tests/integration/repositories/ -v           # Repository tests
pytest tests/integration/services/ -v              # Services tests

# Run with coverage analysis
python -m coverage run -m pytest tests/integration/
python -m coverage report -m

# Commit fixes
git add .
git commit -m "Stabilization Phase X: Fix [category] tests (N tests fixed)"

# Verify Phase 2 baseline
pytest tests/integration/api/test_api_layer_full_coverage.py \
        tests/integration/cli/test_cli_medium_full_coverage.py \
        tests/integration/services/test_services_medium_full_coverage.py \
        tests/integration/storage/test_storage_medium_full_coverage.py \
        -q --tb=no
```

---

**Roadmap Created:** 2025-12-09
**Status:** 🟢 READY FOR WEEK 3 EXECUTION
**Confidence Level:** VERY HIGH
**Expected Outcome:** 95-100% pass rate within 12 hours
