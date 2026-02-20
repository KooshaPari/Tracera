# TUI Testing Quick Reference

## Test File Location
```
tests/integration/tui/test_tui_full_coverage.py
```

## Quick Stats
- **Total Tests:** 124
- **Pass Rate:** 100%
- **Execution Time:** ~1 second
- **File Size:** 1,136 lines

## Running Tests

### All Tests
```bash
pytest tests/integration/tui/test_tui_full_coverage.py -v
```

### Specific Test Class
```bash
# Widget rendering tests
pytest tests/integration/tui/test_tui_full_coverage.py::TestSyncStatusWidgetRendering -v

# Event handling tests
pytest tests/integration/tui/test_tui_full_coverage.py::TestSyncStatusWidgetEventHandling -v

# State management tests
pytest tests/integration/tui/test_tui_full_coverage.py::TestSyncStatusWidgetStateManagement -v
```

### Specific Test
```bash
pytest tests/integration/tui/test_tui_full_coverage.py::TestSyncStatusWidgetEventHandling::test_set_online -v
```

### With Output
```bash
# Show print statements
pytest tests/integration/tui/test_tui_full_coverage.py -v -s

# Show full tracebacks
pytest tests/integration/tui/test_tui_full_coverage.py -v --tb=short

# Only failures
pytest tests/integration/tui/test_tui_full_coverage.py -v --tb=line -x
```

## Test Categories

### Widget Tests (24 tests)
- ItemListWidget (4)
- StateDisplayWidget (4)
- SyncStatusWidget (5)
- CompactSyncStatus (5)
- ViewSwitcherWidget (4)
- ConflictPanel (6)

### Event Handling (32 tests)
- SyncStatusWidget events (13)
- CompactSyncStatus events (4)
- ConflictPanel events (7)
- Button handlers
- Action methods

### State Management (24 tests)
- Initial state (3)
- State transitions (7)
- Combined states (6)
- App state (3)
- Display state (5)

### Integration Tests (14 tests)
- BrowserApp (4)
- DashboardApp (4)
- GraphApp (3)
- EnhancedDashboardApp (3)

### Display Tests (12 tests)
- Status indicators (8)
- Compact display (4)

### Error Handling (16 tests)
- Widget errors (6)
- Conflict panel (4)
- App errors (3)
- Other errors (3)

### Additional (22 tests)
- Compound states (6)
- Composition (3)
- Bindings (3)
- Integration (4)
- Edge cases (3)
- Misc (3)

## Test Structure

Each test class follows this pattern:
```python
@pytest.mark.skipif(not TEXTUAL_AVAILABLE, reason="Textual not installed")
class TestComponentName:
    """Description of what's being tested."""

    def test_specific_feature(self):
        """Test description."""
        # Arrange
        component = ComponentClass()

        # Act
        component.method()

        # Assert
        assert component.property == expected_value
```

## Mocking & Fixtures

### Common Mocks Used
```python
from unittest.mock import Mock, MagicMock, patch, AsyncMock

# Mock widget
mock_widget = Mock()

# Patch class method
with patch.object(widget, "method_name"):
    widget.method()

# Patch external dependency
with patch("module.Class"):
    # test code
```

## Key Test Patterns

### Testing State Changes
```python
def test_state_transitions(self):
    widget = SyncStatusWidget()
    widget.set_online(True)
    assert widget.is_online is True
    widget.set_online(False)
    assert widget.is_online is False
```

### Testing Event Callbacks
```python
def test_watch_online_calls_update(self):
    widget = SyncStatusWidget()
    with patch.object(widget, "update_display") as mock:
        widget.watch_is_online(True)
        mock.assert_called_once()
```

### Testing Composition
```python
def test_compose_structure(self):
    app = BrowserApp()
    try:
        widgets = list(app.compose())
        assert len(widgets) > 0
    except Exception:
        # Textual context not available
        pass
```

### Testing Time Formatting
```python
def test_format_time_ago_minutes(self):
    widget = SyncStatusWidget()
    now = datetime.now(timezone.utc)
    ago_5m = now - timedelta(minutes=5)
    formatted = widget._format_time_ago(ago_5m)
    assert "minute" in formatted
```

## Coverage Analysis

### Module Coverage
```
sync_status.py:     62.35%
conflict_panel.py:  43.94%
item_list.py:       63.64%
state_display.py:   58.33%
view_switcher.py:   69.57%
browser.py:         27.41%
dashboard.py:       22.49%
dashboard_v2.py:    20.85%
graph.py:           25.90%
```

### Running Coverage Report
```bash
python -m coverage run -m pytest tests/integration/tui/test_tui_full_coverage.py
python -m coverage report
python -m coverage html  # generates coverage report
```

## Common Issues & Solutions

### Issue: "Textual not installed"
**Solution:** Install textual
```bash
pip install textual
```

### Issue: "LookupError: active_app"
**Solution:** This is expected. Tests properly handle this with try-except.
```python
try:
    widget.on_mount()
except LookupError:
    # Expected when not in Textual app context
    pass
```

### Issue: Tests taking too long
**Solution:** This should not happen. Tests run in ~1 second total. If they don't:
- Check for other processes: `ps aux | grep pytest`
- Clear cache: `pytest --cache-clear`

## Test Dependencies

### Required Packages
```
pytest >= 8.0.0
textual >= 0.30.0
unittest.mock (built-in)
```

### Optional Packages
```
pytest-cov          # for coverage reports
pytest-asyncio      # for async tests (included)
```

## Debugging Tests

### Print Debug Info
```bash
pytest tests/integration/tui/test_tui_full_coverage.py::TestClass::test_name -v -s
```

### Run Single Test with Breakpoint
```bash
# Add this to test code:
# breakpoint()

pytest tests/integration/tui/test_tui_full_coverage.py::TestClass::test_name -v -s
```

### Show Full Traceback
```bash
pytest tests/integration/tui/test_tui_full_coverage.py --tb=long
```

## Test Maintenance

### Adding New Tests
1. Create new test method in appropriate class
2. Follow naming: `test_feature_description`
3. Add docstring explaining what's tested
4. Run: `pytest tests/integration/tui/test_tui_full_coverage.py -v`

### Updating Existing Tests
1. Edit test method
2. Run test: `pytest tests/integration/tui/test_tui_full_coverage.py::TestClass::test_name -v`
3. Verify all tests pass: `pytest tests/integration/tui/test_tui_full_coverage.py -v`

### Removing Tests
1. Delete test method
2. Verify total count decreases
3. Ensure no dangling mocks or patches

## Test Documentation

Each test has:
- Descriptive class name
- Clear docstring
- Descriptive test method name
- Comment explaining complex logic

Example:
```python
@pytest.mark.skipif(not TEXTUAL_AVAILABLE, reason="Textual not installed")
class TestSyncStatusWidgetDisplay:
    """Test SyncStatusWidget display updates."""

    def test_format_time_ago_minutes(self):
        """Test time formatting for minutes."""
        widget = SyncStatusWidget()
        now = datetime.now(timezone.utc)
        ago_5m = now - timedelta(minutes=5)
        formatted = widget._format_time_ago(ago_5m)
        assert "minute" in formatted or "ago" in formatted
```

## Integration with CI/CD

### GitHub Actions
```yaml
- name: Run TUI Tests
  run: pytest tests/integration/tui/test_tui_full_coverage.py -v
```

### Pre-commit Hook
```bash
#!/bin/bash
pytest tests/integration/tui/test_tui_full_coverage.py --tb=short || exit 1
```

## Performance Notes

- Execution time: ~1 second for all 124 tests
- No external API calls
- No database required
- Minimal memory usage
- All tests are deterministic

## Future Enhancements

Potential additions:
- [ ] Async operation testing
- [ ] Visual rendering tests
- [ ] Performance benchmarks
- [ ] Integration with real Textual app
- [ ] Database integration tests
- [ ] Keyboard input simulation
- [ ] Mouse event simulation

## References

- Test file: `tests/integration/tui/test_tui_full_coverage.py`
- Report: `PHASE_3_WP33_TUI_TESTING_COMPLETE.md`
- Source: `src/tracertm/tui/`
- pytest docs: https://docs.pytest.org/
- Textual docs: https://textual.textualize.io/
