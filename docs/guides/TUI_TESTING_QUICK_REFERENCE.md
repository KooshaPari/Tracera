# TUI Testing Quick Reference Guide

Quick reference for writing Textual widget tests in the TracerTM project.

---

## Available Fixtures

### 1. `textual_app_context` (NEW - Recommended)
Use for widgets requiring full app lifecycle with mount/unmount control.

```python
@pytest.mark.asyncio
async def test_my_widget(textual_app_context):
    async with textual_app_context() as (app, pilot):
        widget = MyWidget()
        await app.mount(widget)
        await pilot.pause()
        
        # Test widget
        assert widget.is_mounted
        assert widget.query("Child")
```

### 2. `textual_app` (Legacy - Still Supported)
Use for simple widget tests where you just need pilot.

```python
@pytest.mark.asyncio
async def test_simple_widget(textual_app):
    widget = SimpleWidget()
    async with textual_app(widget) as pilot:
        assert widget.is_mounted
        await pilot.pause()
```

### 3. `mounted_widget` (Sync Tests Only)
Use for synchronous tests that need widget composition but not full app.

```python
def test_widget_sync(mounted_widget):
    widget = MyWidget()
    mounted_widget(widget)  # Mounts widget
    # Widget is ready for testing
```

---

## Common Patterns

### Pattern 1: Test Widget with Compose
Widgets using `with Container():` in compose() need app context.

```python
@pytest.mark.asyncio
async def test_widget_compose(textual_app_context):
    async with textual_app_context() as (app, pilot):
        widget = MyComplexWidget()
        await app.mount(widget)
        await pilot.pause()
        
        # Query composed children
        assert widget.query("Container")
        assert len(widget.children) > 0
```

### Pattern 2: Test Full App
Apps need `run_test()` to initialize properly.

```python
@pytest.mark.asyncio
async def test_full_app():
    app = MyApp()
    async with app.run_test() as pilot:
        # App is fully initialized
        assert app.query("Header")
        assert app.query("Footer")
        assert len(app.children) > 0
```

### Pattern 3: Test Widget Interactions
Use pilot methods for user interactions.

```python
@pytest.mark.asyncio
async def test_widget_interaction(textual_app_context):
    async with textual_app_context() as (app, pilot):
        widget = InteractiveWidget()
        await app.mount(widget)
        await pilot.pause()
        
        # Simulate user actions
        await pilot.click("#button")
        await pilot.press("enter")
        
        # Verify results
        assert widget.state_changed
```

### Pattern 4: Test Reactive Attributes
Test reactive attribute changes with watchers.

```python
def test_reactive_attribute():
    widget = MyWidget()
    widget.update_display = Mock()
    
    # Change reactive attribute
    widget.my_reactive_var = "new value"
    
    # Verify watcher triggered
    widget.update_display.assert_called_once()
```

### Pattern 5: Mock Internal Dependencies
Always patch at the source module.

```python
def test_with_external_dependency():
    # Import is: from tracertm.storage.conflict_resolver import ConflictResolver
    # Patch at SOURCE:
    with patch("tracertm.storage.conflict_resolver.ConflictResolver"):
        # Test code here
        pass
```

---

## Testing Checklist

### Widget Tests Should:
- ✅ Use `@pytest.mark.asyncio` for async tests
- ✅ Mount widgets in app context before querying
- ✅ Call `await pilot.pause()` after mounting
- ✅ Use `widget.query()` instead of direct attribute access
- ✅ Mock external dependencies at source module
- ✅ Test both happy path and error conditions

### Don't:
- ❌ Call `compose()` directly without app context
- ❌ Query widgets before mounting/pausing
- ❌ Patch at usage location (patch at import source)
- ❌ Use synchronous code for async operations
- ❌ Forget to mock external dependencies

---

## Common Errors & Solutions

### Error: `NoActiveAppError`
**Cause:** Trying to use widget without app context  
**Solution:** Use `textual_app_context` fixture or `app.run_test()`

```python
# BAD
widget = MyWidget()
widget.query_one("#child")  # ERROR: NoActiveAppError

# GOOD
async with textual_app_context() as (app, pilot):
    widget = MyWidget()
    await app.mount(widget)
    await pilot.pause()
    widget.query_one("#child")  # Works!
```

### Error: `IndexError: list index out of range`
**Cause:** Calling `compose()` without app context  
**Solution:** Mount widget first

```python
# BAD
widget = MyWidget()
list(widget.compose())  # ERROR: IndexError

# GOOD
async with textual_app_context() as (app, pilot):
    widget = MyWidget()
    await app.mount(widget)
    await pilot.pause()
    # Now widget.children is populated
```

### Error: `AttributeError: module 'X' does not have the attribute 'Y'`
**Cause:** Patching at wrong import location  
**Solution:** Patch where imported FROM, not where used

```python
# File: my_module.py
# from other_module import SomeClass

# BAD - patching at usage location
with patch("my_module.SomeClass"):  # Won't work

# GOOD - patching at source
with patch("other_module.SomeClass"):  # Works!
```

---

## Example Test Suite Structure

```python
"""
Tests for MyWidget
"""
import pytest
from unittest.mock import Mock, patch
from myapp.widgets.my_widget import MyWidget


class TestMyWidgetInitialization:
    """Test initialization."""
    
    def test_default_values(self):
        widget = MyWidget()
        assert widget.some_value == "default"


class TestMyWidgetComposition:
    """Test widget composition."""
    
    @pytest.mark.asyncio
    async def test_creates_children(self, textual_app_context):
        async with textual_app_context() as (app, pilot):
            widget = MyWidget()
            await app.mount(widget)
            await pilot.pause()
            
            assert widget.query("Child")


class TestMyWidgetBehavior:
    """Test widget behavior."""
    
    @pytest.mark.asyncio
    async def test_user_interaction(self, textual_app_context):
        async with textual_app_context() as (app, pilot):
            widget = MyWidget()
            await app.mount(widget)
            await pilot.pause()
            
            await pilot.click("#button")
            assert widget.button_clicked
```

---

## Useful Commands

```bash
# Run all TUI tests
pytest tests/unit/tui/ -v

# Run specific test file
pytest tests/unit/tui/widgets/test_my_widget.py -v

# Run specific test
pytest tests/unit/tui/widgets/test_my_widget.py::TestMyWidget::test_something -v

# Run with verbose output
pytest tests/unit/tui/ -v --tb=short

# Run and show print statements
pytest tests/unit/tui/ -v -s
```

---

## Resources

- **Textual Docs:** https://textual.textualize.io/
- **Testing Guide:** https://textual.textualize.io/guide/testing/
- **Project Tests:** `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/tests/unit/tui/`
- **Fixtures:** `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/tests/conftest.py`

---

Generated: December 2, 2025
For questions, see PHASE_6_COMPLETION_REPORT.md
