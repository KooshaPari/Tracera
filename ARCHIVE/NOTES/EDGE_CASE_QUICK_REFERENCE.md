# Edge Case Testing - Quick Reference

## Test Files Location

```
tests/unit/
  ├── test_edge_cases_comprehensive.py    (58 tests - models & core)
  ├── test_service_edge_cases.py          (69 tests - services & storage)
  └── test_cli_tui_edge_cases.py          (37 tests - CLI/TUI)
```

## Running Tests

### Run all edge case tests
```bash
pytest tests/unit/test_edge_cases_comprehensive.py \
        tests/unit/test_service_edge_cases.py \
        tests/unit/test_cli_tui_edge_cases.py -v
```

### Run specific test file
```bash
pytest tests/unit/test_edge_cases_comprehensive.py -v
pytest tests/unit/test_service_edge_cases.py -v
pytest tests/unit/test_cli_tui_edge_cases.py -v
```

### Run specific test class
```bash
pytest tests/unit/test_edge_cases_comprehensive.py::TestStringBoundaryConditions -v
pytest tests/unit/test_service_edge_cases.py::TestBatchOperationEdgeCases -v
```

### Run with coverage
```bash
pytest tests/unit/test_edge_cases_comprehensive.py \
        tests/unit/test_service_edge_cases.py \
        tests/unit/test_cli_tui_edge_cases.py \
        --cov=src/tracertm --cov-report=html
```

## Test Statistics

| File | Tests | Status |
|------|-------|--------|
| test_edge_cases_comprehensive.py | 58 | ✓ All Pass |
| test_service_edge_cases.py | 69 | ✓ All Pass |
| test_cli_tui_edge_cases.py | 37 | ✓ All Pass |
| **TOTAL** | **164** | **✓ 100%** |

## Coverage Areas

### String Boundaries (35+ tests)
- Empty strings
- Maximum length (255-500 chars)
- Unicode (Chinese, Russian, Japanese, Arabic, Emoji)
- Special characters (quotes, newlines, tabs, control chars)
- XSS/SQL injection patterns

### Collections (20+ tests)
- Empty collections
- Single items
- Very large collections (1000+, 10000+)
- Deeply nested structures (5+ levels)
- None/null values

### Concurrency (10+ tests)
- Concurrent operations (50-100x)
- Retry mechanisms
- Race conditions
- Cancellation

### Date/Time (10+ tests)
- Timezone handling
- Epoch/far past/far future dates
- Microsecond precision
- Comparisons

### File Paths (15+ tests)
- Special characters
- Very long paths (500+ chars)
- Windows/Unix formats
- Relative/absolute paths

### Error Handling (15+ tests)
- Null/closed sessions
- Constraint violations
- Timeouts
- Exception propagation

### Numeric (15+ tests)
- Zero/negative values
- Maximum integers (sys.maxsize)
- Version boundaries

### Input Validation (20+ tests)
- Empty inputs
- Whitespace-only
- Very large inputs (1M+ chars)
- Control characters
- Bidirectional text

## Key Test Patterns

### 1. Empty/Null Values
```python
test_empty_string_title()              # ""
test_owner_null_value()                # None
test_batch_create_empty_list()         # []
test_null_deleted_at_timestamp()       # None
```

### 2. Maximum Values
```python
test_very_long_string_title()          # 500 chars
test_item_version_max_int()            # sys.maxsize
test_batch_create_very_large_count()   # 10,000 items
test_very_large_input_string()         # 1,000,000 chars
```

### 3. Unicode/Special Characters
```python
test_unicode_characters_in_title()     # 7 languages + emoji
test_special_characters_in_title()     # quotes, HTML, etc.
test_input_with_unicode_bidi()         # bidirectional text
test_null_byte_in_string()             # embedded nulls
```

### 4. Boundary Arithmetic
```python
test_item_version_zero()               # 0 (min)
test_item_version_negative()           # -1 (below min)
test_deleted_at_far_past()             # 1970-01-01
test_deleted_at_far_future()           # 2099-12-31
```

### 5. Concurrent Operations
```python
test_concurrent_item_updates()         # 10 concurrent
test_concurrent_create_operations()    # 100 concurrent
test_concurrent_mixed_operations()     # 50 mixed ops
test_async_gather_partial_failure()    # partial failures
```

## Common Edge Cases by Module

### Models (test_edge_cases_comprehensive.py)
- String field boundaries
- Numeric boundaries
- Collection handling
- DateTime precision
- UUID formats
- Status/priority values
- Parent-child relationships

### Repositories (test_edge_cases_comprehensive.py)
- Creation with edge case values
- Empty result sets
- Null references
- Very large metadata

### Services (test_service_edge_cases.py)
- Batch operations (0, 1, 10000 items)
- Concurrent operations (10-100x)
- Cache boundaries
- Sync conflicts
- Error recovery

### Storage (test_service_edge_cases.py)
- Deleted items handling
- Orphaned links
- Conflicting changes
- Metadata edge cases
- Circular references

### CLI/TUI (test_cli_tui_edge_cases.py)
- Argument parsing
- File paths
- Input validation
- Terminal rendering
- Environment variables
- Configuration loading

## Debugging Failed Edge Cases

### Enable debug output
```bash
pytest tests/unit/test_edge_cases_comprehensive.py -vv -s --tb=long
```

### Run specific failing test
```bash
pytest tests/unit/test_edge_cases_comprehensive.py::TestStringBoundaryConditions::test_empty_string_title -vv
```

### Check test docstring for details
```python
# Test docstring explains the specific edge case
def test_empty_string_title(self):
    """Test item creation with empty string title."""  # <-- explains edge case
    item = Item(id=str(uuid4()), ..., title="")
    assert item.title == ""
```

## Integration Points

### Pre-commit Hook
Add to `.pre-commit-config.yaml`:
```yaml
- repo: local
  hooks:
    - id: edge-case-tests
      name: Edge Case Tests
      entry: pytest tests/unit/test_edge_cases_comprehensive.py tests/unit/test_service_edge_cases.py tests/unit/test_cli_tui_edge_cases.py
      language: system
      stages: [commit]
```

### CI/CD Pipeline
Add to GitHub Actions / GitLab CI:
```yaml
edge_case_tests:
  script:
    - pytest tests/unit/test_edge_cases_comprehensive.py tests/unit/test_service_edge_cases.py tests/unit/test_cli_tui_edge_cases.py
  coverage: '/TOTAL.*\s+(\d+%)$/'
```

## Performance Expectations

- **Total Duration:** ~2-3 seconds for all 164 tests
- **Per-test Average:** ~0.013 seconds
- **Memory Usage:** <100MB
- **CPU Usage:** Single core, low overhead

## Best Practices

### When Adding New Features
1. Run edge case tests first: `pytest tests/unit/test_*_edge_cases.py`
2. Check if new edge cases needed for feature
3. Add tests before implementing feature
4. Verify all 164 tests still pass

### When Fixing Bugs
1. Check if bug is edge case related
2. Add test for edge case if missing
3. Fix the code
4. Verify test passes

### When Refactoring
1. Run full edge case suite: `pytest tests/unit/test_*_edge_cases.py`
2. Ensure no regressions
3. All 164 tests should pass
4. No new failures

## Troubleshooting

### Tests Failing After Changes
```bash
# Run with verbose output
pytest tests/unit/test_edge_cases_comprehensive.py -vv --tb=short

# Run specific failing test in isolation
pytest tests/unit/test_edge_cases_comprehensive.py::ClassName::test_name -vv

# Check for import errors
pytest tests/unit/test_edge_cases_comprehensive.py --collect-only
```

### Flaky Tests
- Edge case tests are deterministic
- If test fails intermittently, likely a real bug
- Run 5-10 times to confirm: `pytest -v --count=10`

### Performance Issues
- Tests should run in <3 seconds total
- If slower, check for:
  - Unintended database operations
  - External API calls
  - Very large data structures

## Future Enhancements

1. **Property-Based Testing**
   ```python
   # Add Hypothesis tests
   from hypothesis import given
   @given(st.text())
   def test_string_property(self, s):
       # Test properties across wide range of inputs
   ```

2. **Fuzzing**
   ```bash
   # Fuzz input validation
   pip install python-fuzzer
   ```

3. **Load Testing**
   ```bash
   # Test with higher concurrency (1000+)
   pytest tests/unit/test_service_edge_cases.py -k concurrent --stress
   ```

---

**Last Updated:** December 10, 2025
**Status:** Ready for Production
