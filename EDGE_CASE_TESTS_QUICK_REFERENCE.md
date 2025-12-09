# Edge Case Tests - Quick Reference

## Test File Location
`tests/integration/edge_cases/test_coverage_gaps.py`

## Quick Stats
- **Total Tests:** 76
- **Target Modules:** 3
- **Coverage Improvement:** +13-17% per module

---

## Test Distribution

### Sync Client (20 tests)
| Category | Tests | Focus |
|----------|-------|-------|
| Config Edge Cases | 3 | None handling, type conversion, URL normalization |
| Client Initialization | 2 | No token, close when None |
| Retry Logic | 3 | Exhausted retries, rate limiting, error types |
| API Operations | 4 | Null values, missing fields, unhealthy status |
| Conflict Resolution | 4 | All strategies (MANUAL, LOCAL_WINS, REMOTE_WINS, LAST_WRITE_WINS) |
| Data Classes | 4 | Minimal data, null timestamps, error initialization |

### Bulk Operation Service (19 tests)
| Category | Tests | Focus |
|----------|-------|-------|
| Preview Operations | 3 | All filters, warnings, large operations |
| Update Operations | 2 | All fields, rollback on error |
| Delete Operations | 2 | Filters, rollback on error |
| CSV Parsing | 6 | Empty, headers, JSON errors, validation |
| Create Operations | 4 | Invalid rows, rollback, exception handling |
| Warnings | 2 | Duplicates, large operations |

### Markdown Parser (37 tests)
| Category | Tests | Focus |
|----------|-------|-------|
| File I/O | 4 | Missing files, empty files, validation |
| Links/Config | 6 | Missing files, empty, invalid format |
| Figma/Wireframe | 3 | Figma fields, wireframe sections |
| Data Conversion | 3 | DateTime, metadata handling |
| Parsing | 7 | History tables, body sections, YAML |
| Directory Ops | 3 | Parent creation for all write ops |
| Custom Fields | 2 | Separation, inclusion in frontmatter |
| Data Classes | 7 | Minimal data, defaults, null handling |
| Listing | 3 | Nonexistent paths, type filtering |

---

## Run Commands

### Run All Tests
```bash
pytest tests/integration/edge_cases/test_coverage_gaps.py -v
```

### Run with Coverage
```bash
pytest tests/integration/edge_cases/test_coverage_gaps.py \
  --cov=src/tracertm/api/sync_client \
  --cov=src/tracertm/services/bulk_operation_service \
  --cov=src/tracertm/storage/markdown_parser \
  --cov-report=term-missing
```

### Run by Module
```bash
# Sync client tests only
pytest tests/integration/edge_cases/test_coverage_gaps.py::TestSyncClientEdgeCases -v

# Bulk operation tests only
pytest tests/integration/edge_cases/test_coverage_gaps.py::TestBulkOperationServiceEdgeCases -v

# Markdown parser tests only
pytest tests/integration/edge_cases/test_coverage_gaps.py::TestMarkdownParserEdgeCases -v
```

---

## Test Case IDs

### Sync Client (TC-SC-E1 to TC-SC-E17)
- **E1-E3:** Configuration edge cases
- **E4-E5:** Client initialization
- **E6-E8:** Retry logic
- **E9-E13:** API operations
- **E14-E17:** Conflict resolution

### Bulk Operations (TC-BOS-E1 to TC-BOS-E19)
- **E1-E3:** Preview operations
- **E4-E5:** Update operations
- **E6-E7:** Delete operations
- **E8-E15:** CSV parsing
- **E16-E19:** Create operations

### Markdown Parser (TC-MP-E1 to TC-MP-E37)
- **E1-E4:** File I/O errors
- **E5-E10:** Links/config parsing
- **E11-E13:** Figma/wireframe
- **E14-E16:** Data conversion
- **E17-E26:** Parsing edge cases
- **E27-E29:** Directory creation
- **E30-E31:** Custom fields
- **E32-E37:** Data classes

---

## Coverage Targets

| Module | Before | After | Gain |
|--------|--------|-------|------|
| sync_client.py | 70.52% | 86-88% | +16% |
| bulk_operation_service.py | 77.21% | 88-90% | +12% |
| markdown_parser.py | 73.09% | 86-88% | +15% |

---

## Key Test Patterns

### Error Path Testing
```python
# Test rollback on database error
mock_session.commit.side_effect = OperationalError("DB Error", None, None)
with pytest.raises(OperationalError):
    service.bulk_update_items("proj-1", {}, {"status": "done"})
mock_session.rollback.assert_called_once()
```

### Boundary Condition Testing
```python
# Test empty CSV file
csv_data = "Title,View,Type\n"  # Header only
result = service.bulk_create_preview("proj-1", csv_data)
assert result["total_count"] == 0
```

### Conflict Resolution Testing
```python
# Test LOCAL_WINS strategy
await client.full_sync(changes, conflict_strategy=ConflictStrategy.LOCAL_WINS)
# Verify local data was used
args = mock_resolve.call_args
assert args[0][2] == conflict.local_data
```

### Null Handling Testing
```python
# Test None timestamp handling
data = {"last_sync": None, "online": True}
status = SyncStatus.from_dict(data)
assert status.last_sync is None
```

---

## Error Types Covered

### Sync Client
- `ApiError`: HTTP errors, generic failures
- `NetworkError`: Connection failures, timeouts
- `AuthenticationError`: 401 errors, invalid tokens
- `RateLimitError`: 429 errors, retry-after
- `ConflictError`: 409 errors, merge conflicts

### Bulk Operations
- `OperationalError`: Database connection issues
- `IntegrityError`: Constraint violations
- `ValueError`: Validation failures
- `JSONDecodeError`: Invalid JSON in CSV

### Markdown Parser
- `FileNotFoundError`: Missing files
- `ValueError`: Validation errors, invalid frontmatter
- `yaml.YAMLError`: YAML parsing errors
- `KeyError`: Missing required fields

---

## Mock Patterns

### Database Session Mock
```python
mock_session = Mock(spec=Session)
mock_session.query.return_value = mock_session
mock_session.filter.return_value = mock_session
mock_session.all.return_value = []
mock_session.commit = Mock()
mock_session.rollback = Mock()
```

### Async API Mock
```python
with patch.object(client, "_retry_request", new_callable=AsyncMock) as mock:
    mock.return_value = mock_response
    result = await client.upload_changes(changes)
```

### File System Mock
```python
path = temp_dir / "test.md"
path.write_text(content)
assert path.exists()
```

---

## Common Assertions

### Success Cases
```python
assert result["items_updated"] == 5
assert len(result["conflicts"]) == 0
assert status.online is True
assert path.exists()
```

### Error Cases
```python
with pytest.raises(ValueError, match="missing required"):
    function_call()
mock_session.rollback.assert_called_once()
assert "error message" in result["validation_errors"][0]
```

### Null/Empty Cases
```python
assert result == []
assert value is None
assert result["total_count"] == 0
```

---

## Fixtures Used

### `mock_session` (Bulk Operations)
- Mocked SQLAlchemy session
- Pre-configured with query chain
- Commit/rollback tracking

### `service` (Bulk Operations)
- BulkOperationService instance
- Uses mock_session

### `temp_dir` (Markdown Parser)
- Temporary directory for file tests
- Auto-cleanup after test

### `api_client` (Sync Client)
- ApiClient instance
- Test configuration
- Mocked HTTP client

---

## Files Generated

1. **Test Suite:** `tests/integration/edge_cases/test_coverage_gaps.py` (850+ lines)
2. **Full Report:** `EDGE_CASE_TEST_COVERAGE_REPORT.md` (comprehensive analysis)
3. **Quick Reference:** `EDGE_CASE_TESTS_QUICK_REFERENCE.md` (this file)

---

## Next Steps

1. **Run tests:**
   ```bash
   pytest tests/integration/edge_cases/test_coverage_gaps.py -v
   ```

2. **Check coverage:**
   ```bash
   pytest tests/integration/edge_cases/test_coverage_gaps.py --cov --cov-report=html
   ```

3. **Review gaps:**
   - Open `htmlcov/index.html`
   - Look for remaining uncovered lines
   - Add targeted tests if needed

4. **Verify metrics:**
   - All modules should be 85%+
   - All tests should pass
   - No false positives

---

## Troubleshooting

### Import Errors
If you see import errors, ensure:
```bash
export PYTHONPATH=/Users/kooshapari/temp-PRODVERCEL/485/kush/trace:$PYTHONPATH
```

### Test Failures
Check:
- Mock return values match expected types
- Async tests use `@pytest.mark.asyncio`
- Fixtures are properly scoped

### Coverage Not Improving
Verify:
- Tests are actually executing (no skips)
- Mocks aren't hiding code execution
- Coverage is measuring correct modules

---

## Success Indicators

- [ ] All 76 tests pass
- [ ] sync_client.py coverage ≥ 85%
- [ ] bulk_operation_service.py coverage ≥ 85%
- [ ] markdown_parser.py coverage ≥ 85%
- [ ] No test failures or errors
- [ ] Coverage report generated successfully

---

**Last Updated:** 2025-12-04
**Test Count:** 76
**Modules Covered:** 3
**Expected Coverage Gain:** +13-17% per module
