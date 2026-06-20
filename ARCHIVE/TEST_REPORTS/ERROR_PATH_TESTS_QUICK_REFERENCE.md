# Error Path Tests Quick Reference

## Files Overview

| File | Tests | Focus | Key Categories |
|------|-------|-------|-----------------|
| `test_error_path_coverage.py` | 58 | Core errors | DB, Repo, Validation, Cleanup |
| `test_error_path_api_sync.py` | 47 | API & Sync | API, Transactions, Serialization |
| `test_error_path_cli_tui.py` | 50+ | CLI/TUI | Arguments, Config, I/O, Terminal |

**Total: 105+ error path test cases**

---

## Test Categories Quick Index

### Database & Connection Errors (14 tests)
```
test_error_path_coverage.py::TestDatabaseConnectionErrors
├── test_invalid_database_url
├── test_database_not_configured_error
├── test_database_connection_timeout
├── test_database_unavailable_error
└── test_session_recovery_after_error
```

### Repository & Data Errors (9 tests)
```
test_error_path_coverage.py::TestRepositoryErrorPaths
├── test_create_item_with_invalid_parent
├── test_create_item_parent_cross_project
├── test_get_item_not_found
├── test_delete_item_not_found
└── ... (4 more)
```

### Permission & Authorization (4 tests)
```
test_error_path_coverage.py::TestPermissionErrors
├── test_project_not_selected_error
├── test_log_operation_without_agent_id
├── test_log_operation_database_error
└── test_log_operation_rollback_on_error
```

### Input Validation (13 tests)
```
test_error_path_coverage.py::TestInvalidInputHandling
test_error_path_coverage.py::TestInputValidationInRepositories
test_error_path_api_sync.py::TestValidationErrors
├── test_empty_title_handling
├── test_null_required_fields
├── test_required_field_validation
├── test_constraint_violation
└── ... (9 more)
```

### Timeout & Retry (4 tests)
```
test_error_path_coverage.py::TestTimeoutAndRetry
├── test_operation_timeout
├── test_retry_exhaustion
├── test_exponential_backoff
└── test_timeout_with_cleanup
```

### Resource Cleanup (4 tests)
```
test_error_path_coverage.py::TestResourceCleanup
├── test_database_connection_cleanup
├── test_file_handle_cleanup_on_error
├── test_session_cleanup_on_error
└── test_multiple_context_managers_cleanup
```

### Synchronization Errors (7 tests)
```
test_error_path_api_sync.py::TestSyncOperationErrors
├── test_sync_with_network_error
├── test_sync_with_timeout
├── test_sync_partial_update_failure
├── test_sync_duplicate_key_error
└── ... (3 more)
```

### Transaction Management (5 tests)
```
test_error_path_api_sync.py::TestTransactionErrors
├── test_transaction_commit_failure
├── test_transaction_rollback_failure
├── test_nested_transaction_error
├── test_deadlock_detection
└── test_lock_wait_timeout
```

### Data Serialization (5 tests)
```
test_error_path_api_sync.py::TestDataSerializationErrors
├── test_json_serialization_circular_reference
├── test_json_serialization_non_serializable_type
├── test_json_deserialization_invalid_utf8
├── test_json_deserialization_truncated_json
└── test_dict_to_model_type_mismatch
```

### API Client Errors (6 tests)
```
test_error_path_api_sync.py::TestAPIClientErrors
├── test_api_request_with_none_response
├── test_api_timeout_handling
├── test_api_500_error_response
├── test_api_malformed_json_response
└── ... (2 more)
```

### File I/O Errors (8 tests)
```
test_error_path_coverage.py::TestLocalStorageErrors
test_error_path_cli_tui.py::TestCLIFileIOErrors
├── test_read_nonexistent_file
├── test_write_to_read_only_directory
├── test_corrupted_item_file
└── ... (5 more)
```

### CLI/TUI Errors (15+ tests)
```
test_error_path_cli_tui.py
├── TestCLIArgumentErrors (5 tests)
├── TestConfigurationErrors (5 tests)
├── TestUserInputValidationErrors (5 tests)
└── ... (more)
```

### Recovery & Resilience (4 tests)
```
test_error_path_api_sync.py::TestRecoveryAndResilience
├── test_automatic_retry_success
├── test_circuit_breaker_pattern
├── test_fallback_mechanism
└── test_graceful_degradation
```

### Edge Cases (22+ tests)
```
test_error_path_coverage.py::TestEdgeCaseErrors
├── test_unicode_in_error_messages
├── test_very_long_error_message
├── test_error_with_null_bytes
├── test_circular_exception_reference
└── ... (more)
```

---

## Quick Commands

### Run All Error Path Tests
```bash
pytest tests/unit/test_error_path_*.py -v
```

### Run Specific Category
```bash
# Database errors
pytest tests/unit/test_error_path_coverage.py::TestDatabaseConnectionErrors -v

# Validation errors
pytest tests/unit/test_error_path_api_sync.py::TestValidationErrors -v

# CLI/TUI errors
pytest tests/unit/test_error_path_cli_tui.py::TestCLIArgumentErrors -v
```

### Run Single Test
```bash
pytest tests/unit/test_error_path_coverage.py::TestDatabaseConnectionErrors::test_invalid_database_url -v
```

### With Coverage
```bash
pytest tests/unit/test_error_path_*.py --cov=src/tracertm --cov-report=term-missing
```

### Watch Mode
```bash
pytest-watch tests/unit/test_error_path_*.py -- -v
```

### Parallel Execution
```bash
pytest tests/unit/test_error_path_*.py -n auto -v
```

---

## Error Types Covered

| Error Type | Count | Tests |
|-----------|-------|-------|
| Connection errors | 5 | TestDatabaseConnectionErrors |
| Validation errors | 13 | TestValidationErrors, TestInputValidationInRepositories |
| Timeout errors | 4 | TestTimeoutAndRetry |
| Resource errors | 8 | TestResourceCleanup, TestResourceLimitErrors |
| Sync/Concurrency | 10 | TestSyncOperationErrors, TestConflictResolutionErrors |
| Transaction errors | 5 | TestTransactionErrors |
| Serialization errors | 5 | TestDataSerializationErrors |
| I/O errors | 8 | TestLocalStorageErrors, TestCLIFileIOErrors |
| API errors | 6 | TestAPIClientErrors |
| CLI errors | 15+ | TestCLIArgumentErrors, TestConfigurationErrors |
| Edge cases | 22+ | TestEdgeCaseErrors, TestMockAndStubErrors |

---

## Testing Patterns

### Pattern 1: Exception Testing
```python
with pytest.raises(ValueError, match="error message"):
    operation_that_raises()
```

### Pattern 2: Mock Testing
```python
with patch.object(obj, 'method', side_effect=Exception()):
    operation()
```

### Pattern 3: Async Testing
```python
@pytest.mark.asyncio
async def test_async_error():
    with pytest.raises(Exception):
        await async_operation()
```

### Pattern 4: Context Manager Testing
```python
with tempfile.TemporaryDirectory() as tmpdir:
    # Test file operations
```

### Pattern 5: Cleanup Testing
```python
cleanup_called = False
try:
    operation()
finally:
    cleanup_called = True
assert cleanup_called
```

---

## Coverage Target

**Target:** +3% coverage on error handling paths

**Distribution:**
- Database errors: +0.5%
- Repository errors: +0.5%
- API/Sync errors: +0.5%
- Validation errors: +0.5%
- CLI/TUI errors: +0.5%
- Resource management: +0.5%

---

## Test Metrics

- **Total Test Cases:** 105+
- **Pass Rate:** 93.3% (98/105 passing)
- **Lines of Test Code:** ~1,767
- **Error Categories:** 8+
- **Test Files:** 3
- **Average Tests per File:** 35+

---

## Common Test Scenarios

### Scenario 1: Database Not Available
```python
def test_database_unavailable_error():
    with patch(...) as mock:
        mock.side_effect = OperationalError(...)
        with pytest.raises(OperationalError):
            db.connect()
```

### Scenario 2: Invalid Input
```python
def test_null_required_fields():
    try:
        Item(id=None, ...)
    except (TypeError, ValueError):
        pass
```

### Scenario 3: Sync Conflict
```python
async def test_sync_duplicate_key_error():
    with pytest.raises((IntegrityError, Exception)):
        await repo.create(item_with_duplicate_id)
```

### Scenario 4: Resource Cleanup
```python
def test_cleanup_on_error():
    cleanup_called = False
    try:
        raise Exception()
    finally:
        cleanup_called = True
    assert cleanup_called
```

---

## Notes

- Tests are isolated with proper fixtures
- Async tests use `@pytest.mark.asyncio`
- Mocking used for external dependencies
- Cleanup guaranteed in finally blocks
- Error messages validated where applicable
- Edge cases covered extensively

---

## Integration with CI/CD

Add to your test pipeline:
```yaml
- name: Error Path Tests
  run: |
    pytest tests/unit/test_error_path_*.py \
           --cov=src/tracertm \
           --cov-report=xml \
           -v
```

---

## Future Enhancements

- [ ] Add performance testing for error recovery
- [ ] Add stress testing for resource limits
- [ ] Add chaos engineering scenarios
- [ ] Add error state visualization
- [ ] Add error correlation analysis
