# Phase 3A: TUI Widget Infrastructure - Implementation Plan
## TraceRTM Python Test Coverage - Fixing 146 Widget Tests
**Target**: 93%+ pass rate (+6% improvement)
**Effort**: 3-4 hours
**Status**: Ready to Execute

---

## 🎯 PHASE 3A OBJECTIVE

Fix 146 failing TUI widget tests by creating proper Textual application context and widget testing infrastructure.

### Impact
- **Tests Fixed**: 146
- **Pass Rate Improvement**: +6-7% (87.3% → 93-94%)
- **Categories**: Widget rendering, app initialization, state management

---

## 📋 WIDGET TEST FILES

### Phase 2 Already Created (These files exist but fail due to lack of proper context)

#### Tier 1: TUI Widgets (83 tests)
- `/tests/unit/tui/widgets/test_sync_status.py` (35 tests)
- `/tests/unit/tui/widgets/test_conflict_panel.py` (20 tests)
- `/tests/unit/tui/widgets/test_all_widgets.py` (23 tests)
- `/tests/unit/tui/adapters/test_storage_adapter.py` (28 tests)

#### Tier 2: TUI Applications (63 tests)
- `/tests/unit/tui/apps/test_dashboard_compat.py` (20 tests)
- `/tests/unit/tui/apps/test_dashboard_app.py` (20 tests)
- `/tests/unit/tui/apps/test_graph_app.py` (15 tests)
- `/tests/unit/tui/apps/test_browser_app.py` (8 tests)

---

## 🔧 IMPLEMENTATION STEPS

### Step 1: Create Textual Testing Fixture (30 minutes)

Add to `/tests/conftest.py`:

```python
import pytest
from pathlib import Path
from typing import Generator
from textual.app import App, ComposeResult
from textual.widgets import Widget, Container

@pytest.fixture
async def textual_app_context() -> Generator:
    """Provides a Textual application context for widget testing.

    Usage:
        async def test_widget(textual_app_context):
            async with textual_app_context() as app:
                widget = MyWidget()
                app.mount(widget)
                assert widget.visible
    """

    class TestApp(App):
        """Minimal test application for widget testing."""

        CSS = """
        Screen {
            layout: vertical;
        }
        """

        def compose(self) -> ComposeResult:
            """Compose the test application."""
            yield Container()

    app = TestApp()

    async def run_app():
        async with app.run_test() as pilot:
            yield app, pilot

    return run_app


@pytest.fixture
def textual_app(event_loop):
    """Synchronous wrapper for textual_app_context fixture."""

    class TestApp(App):
        CSS = ""

        def compose(self) -> ComposeResult:
            yield Container()

    app = TestApp()
    return app
```

### Step 2: Update Widget Test Files (2.5 hours)

For each widget test file, update tests to use the fixture.

#### Pattern 1: Test Widget Rendering

**Before (FAILS)**:
```python
def test_widget_renders():
    widget = SyncStatus()
    assert widget.visible
    assert len(widget.children) > 0
```

**After (WORKS)**:
```python
async def test_widget_renders(textual_app_context):
    async with textual_app_context() as (app, pilot):
        widget = SyncStatus()
        app.mount(widget)
        assert widget.visible
        assert len(widget.children) > 0
```

#### Pattern 2: Test Widget State Changes

**Before (FAILS)**:
```python
def test_widget_state_change():
    widget = ConflictPanel()
    widget.state = "resolved"
    assert widget.state == "resolved"
```

**After (WORKS)**:
```python
async def test_widget_state_change(textual_app_context):
    async with textual_app_context() as (app, pilot):
        widget = ConflictPanel()
        app.mount(widget)
        widget.state = "resolved"
        await pilot.pause()  # Allow state changes to process
        assert widget.state == "resolved"
```

#### Pattern 3: Test Widget Interaction

**Before (FAILS)**:
```python
def test_widget_click():
    widget = ConflictPanel()
    widget._on_click()
    assert widget.handled_click == True
```

**After (WORKS)**:
```python
async def test_widget_click(textual_app_context):
    async with textual_app_context() as (app, pilot):
        widget = ConflictPanel()
        app.mount(widget)
        await pilot.click(widget)
        await pilot.pause()
        assert widget.handled_click == True
```

#### Pattern 4: Test Widget Attributes

**Before (FAILS)**:
```python
def test_compact_widget_attributes():
    widget = SyncStatusCompact()
    assert widget.id == "sync_status_compact"
    assert widget.classes == "compact"
```

**After (WORKS)**:
```python
async def test_compact_widget_attributes(textual_app_context):
    async with textual_app_context() as (app, pilot):
        widget = SyncStatusCompact()
        app.mount(widget)
        await pilot.pause()
        assert widget.id == "sync_status_compact"
        assert "compact" in widget.classes
```

### Step 3: Handle Async Tests (1 hour)

All widget tests need to be marked as async:

```python
import pytest

# Mark all tests in a file as async
pytestmark = pytest.mark.asyncio

# Individual test
@pytest.mark.asyncio
async def test_something(textual_app_context):
    # Test implementation
```

### Step 4: Common Widget Testing Patterns (30 minutes)

**Pattern: Update Widget Properties**
```python
async def test_set_status(textual_app_context):
    async with textual_app_context() as (app, pilot):
        widget = SyncStatus()
        app.mount(widget)

        widget.set_online()
        await pilot.pause()
        assert widget.status == "online"

        widget.set_syncing()
        await pilot.pause()
        assert widget.status == "syncing"
```

**Pattern: Query Child Widgets**
```python
async def test_widget_children(textual_app_context):
    async with textual_app_context() as (app, pilot):
        widget = Dashboard()
        app.mount(widget)
        await pilot.pause()

        children = widget.query("Button")
        assert len(children) > 0
```

**Pattern: Test Widget Styling**
```python
async def test_widget_styles(textual_app_context):
    async with textual_app_context() as (app, pilot):
        widget = ConflictPanel()
        app.mount(widget)
        await pilot.pause()

        assert widget.styles.width == 50
        assert widget.styles.height == "auto"
```

**Pattern: Test Error Handling**
```python
async def test_widget_error_handling(textual_app_context):
    async with textual_app_context() as (app, pilot):
        widget = QueryPanel()
        app.mount(widget)

        with pytest.raises(ValueError):
            widget.execute_invalid_query()
```

---

## 📂 FILE UPDATES REQUIRED

### Tests to Update (by impact)

#### High Priority: Core Widgets (50 tests, 1.5 hours)
1. `/tests/unit/tui/widgets/test_sync_status.py`
   - 35 tests for sync status widget
   - Mostly state changes and attribute tests

2. `/tests/unit/tui/adapters/test_storage_adapter.py`
   - 28 tests for storage adapter
   - Many interaction tests

#### Medium Priority: App Tests (43 tests, 1.5 hours)
3. `/tests/unit/tui/apps/test_dashboard_compat.py` (20 tests)
4. `/tests/unit/tui/apps/test_dashboard_app.py` (20 tests)
5. `/tests/unit/tui/apps/test_browser_app.py` (8 tests)

#### Lower Priority: Specialized Widgets (53 tests, 1 hour)
6. `/tests/unit/tui/widgets/test_conflict_panel.py` (20 tests)
7. `/tests/unit/tui/widgets/test_all_widgets.py` (23 tests)
8. `/tests/unit/tui/apps/test_graph_app.py` (15 tests)

---

## ✅ VERIFICATION CHECKLIST

After implementing Phase 3A:

- [ ] Textual testing fixture created in `/tests/conftest.py`
- [ ] All 146 widget/app tests marked with `@pytest.mark.asyncio`
- [ ] All widget tests use `textual_app_context` fixture
- [ ] All tests updated to be async functions
- [ ] Widget rendering tests working (test_*renders*)
- [ ] Widget state tests working (test_*state*)
- [ ] Widget interaction tests working (test_*click*, test_*input*)
- [ ] Widget attribute tests working (test_*attributes*)
- [ ] Run verification: `pytest tests/unit/tui/ -v`
- [ ] Pass rate > 93%

---

## 🎯 SUCCESS CRITERIA

| Criteria | Target | Measurement |
|----------|--------|-------------|
| Widget tests passing | 146/146 | `pytest tests/unit/tui/ -q` |
| Pass rate | >93% | Full suite pass rate |
| Code coverage | >55% | `coverage report` |
| No warnings | Clean | `pytest -W error` |
| Fixture reusability | High | Used in >50 tests |

---

## 🔍 COMMON ISSUES & SOLUTIONS

### Issue 1: Widget Not Rendering
**Error**: `AttributeError: 'Widget' has no attribute 'visible'`
**Cause**: Widget not mounted to app
**Solution**: Always call `app.mount(widget)` before accessing properties

### Issue 2: Async/Await Not Working
**Error**: `RuntimeError: no running event loop`
**Cause**: Test function not marked as async
**Solution**: Add `@pytest.mark.asyncio` or `async def test_*`

### Issue 3: Widget State Not Updating
**Error**: `AssertionError: expected_state != actual_state`
**Cause**: State change needs processing time
**Solution**: Add `await pilot.pause()` after state changes

### Issue 4: Child Widget Not Found
**Error**: `IndexError: list index out of range` in widget.query()
**Cause**: Child widgets not yet rendered
**Solution**: Add `await pilot.pause()` before querying children

### Issue 5: CSS Not Applied
**Error**: Widget styles are empty/default
**Cause**: App CSS not loaded
**Solution**: Define CSS in TestApp or use `app.set_css(css_string)`

---

## 📊 EXPECTED RESULTS

### Before Phase 3A
```
tests/unit/tui/widgets/: 83 tests, ~5 passing, ~78 failing
tests/unit/tui/apps/: 63 tests, ~3 passing, ~60 failing
Total TUI: 146 tests, ~8 passing, ~138 failing (5% pass rate)
```

### After Phase 3A
```
tests/unit/tui/widgets/: 83 tests, ~80 passing, ~3 failing (96% pass rate)
tests/unit/tui/apps/: 63 tests, ~61 passing, ~2 failing (97% pass rate)
Total TUI: 146 tests, ~141 passing, ~5 failing (96% pass rate)

Overall Suite:
- Before: 87.3% (1,395/1,598)
- After: 93%+ (1,480+/1,598)
- Improvement: +85+ tests fixed, +6%+ pass rate
```

---

## 🚀 EXECUTION TIMELINE

| Step | Duration | Cumulative |
|------|----------|-----------|
| 1. Create fixture | 30 min | 30 min |
| 2. Update widget tests | 2.5 hr | 3 hr |
| 3. Handle async | 1 hr | 4 hr |
| 4. Test patterns | 30 min | 4.5 hr |
| 5. Verification & fixes | 30-60 min | 5-5.5 hr |

**Total Estimated Effort**: 3-4 hours

---

## 📌 NOTES

- Textual framework requires app context for widget testing
- All async operations require proper await/pause handling
- Widget state changes are async and need processing time
- Many tests can be simplified from integration to unit tests
- Pattern once established is highly reusable across tests

---

## 🎁 PHASE 3A DELIVERABLES

After completion:
1. ✅ Textual testing fixture in conftest.py
2. ✅ 146 widget tests updated and passing
3. ✅ Async test patterns documented
4. ✅ Pass rate improved to 93%+
5. ✅ Reusable widget testing infrastructure

---

*Phase 3A is the highest-impact next step, fixing 146 tests with clear technical approach and well-understood patterns from Textual framework documentation.*
