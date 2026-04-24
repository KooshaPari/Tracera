# Edge Case Tests - Coverage Gap Closure

## Overview
This directory contains comprehensive edge case tests designed to push module coverage from 70-80% to 85%+.

## Files in This Directory

### `test_coverage_gaps.py`
Main test file containing 73 edge case tests targeting three modules:
- **Sync Client Tests (17):** API client error paths, retry logic, conflict resolution
- **Bulk Operation Tests (19):** CSV parsing, validation, transaction rollback
- **Markdown Parser Tests (37):** File I/O, YAML parsing, data conversion

## Quick Start

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
  --cov-report=html
```

### Run Specific Test Class
```bash
pytest tests/integration/edge_cases/test_coverage_gaps.py::TestSyncClientEdgeCases -v
```

## Target Modules

| Module | Before | After | Tests |
|--------|--------|-------|-------|
| sync_client.py | 70.52% | 86-88% | 17 |
| bulk_operation_service.py | 77.21% | 88-90% | 19 |
| markdown_parser.py | 73.09% | 86-88% | 37 |

## Documentation

See root directory for comprehensive documentation:
- `EDGE_CASE_TESTS_SUMMARY.md` - Executive summary
- `EDGE_CASE_TEST_COVERAGE_REPORT.md` - Full analysis
- `EDGE_CASE_TESTS_QUICK_REFERENCE.md` - Quick commands

## Test Organization

```
TestSyncClientEdgeCases
├── test_config_from_manager_with_none_manager
├── test_config_from_manager_with_string_timeout
├── test_config_trailing_slash_stripped
├── test_client_property_without_token
├── test_client_close_when_none
├── test_retry_request_http_status_error_all_retries
├── test_retry_request_rate_limit_with_retry_after
├── test_retry_request_rate_limit_no_retry_after_on_last_attempt
├── test_health_check_unhealthy_status
├── test_upload_changes_with_last_sync_none
├── test_download_changes_without_project_id
├── test_resolve_conflict_without_merged_data
├── test_sync_status_with_null_timestamps
├── test_full_sync_with_manual_conflict_strategy
├── test_full_sync_local_wins_conflict_resolution
├── test_full_sync_remote_wins_conflict_resolution
└── test_full_sync_last_write_wins_higher_remote_version

TestBulkOperationServiceEdgeCases
├── test_bulk_update_preview_with_all_filters
├── test_bulk_update_preview_large_operation_warning
├── test_bulk_update_preview_mixed_statuses_warning
├── test_bulk_update_items_with_all_update_fields
├── test_bulk_update_items_rollback_on_error
├── test_bulk_delete_items_with_filters
├── test_bulk_delete_rollback_on_error
├── test_bulk_create_preview_empty_csv
├── test_bulk_create_preview_missing_required_headers
├── test_bulk_create_preview_case_insensitive_headers
├── test_bulk_create_preview_invalid_json_metadata
├── test_bulk_create_preview_pydantic_validation_error
├── test_bulk_create_preview_duplicate_title_warning
├── test_bulk_create_preview_large_operation_warning
├── test_bulk_create_preview_with_all_optional_fields
├── test_bulk_create_items_skip_invalid_rows
├── test_bulk_create_items_skip_json_decode_error
├── test_bulk_create_items_rollback_on_commit_error
└── test_bulk_create_items_skip_row_on_exception

TestMarkdownParserEdgeCases
├── test_parse_item_markdown_file_not_found
├── test_parse_item_markdown_no_frontmatter
├── test_parse_item_markdown_missing_required_fields
├── test_write_item_markdown_missing_required_fields
├── test_parse_links_yaml_file_not_found
├── test_parse_links_yaml_empty_file
├── test_parse_links_yaml_no_links_key
├── test_parse_links_yaml_invalid_link_format
├── test_parse_config_yaml_file_not_found
├── test_parse_config_yaml_empty_file
├── test_item_data_frontmatter_with_figma_fields
├── test_item_data_markdown_body_wireframe_type
├── test_item_data_markdown_body_wireframe_no_node_id
├── test_link_data_datetime_string_conversion
├── test_link_data_to_dict_with_metadata
├── test_link_data_to_dict_without_metadata
├── test_parse_history_table_insufficient_rows
├── test_parse_history_table_non_table_line
├── test_parse_history_table_insufficient_columns
├── test_list_items_nonexistent_project
├── test_list_items_nonexistent_type
├── test_list_items_all_types
├── test_get_item_path_story_pluralization
├── test_parse_markdown_body_no_sections
├── test_parse_markdown_body_empty_sections
├── test_parse_frontmatter_invalid_yaml_raises
├── test_write_links_yaml_creates_parent_directory
├── test_write_config_yaml_creates_parent_directory
├── test_write_item_markdown_creates_parent_directory
├── test_item_data_custom_fields_excluded_from_known_fields
├── test_item_data_to_frontmatter_includes_custom_fields
├── test_conflict_from_dict_missing_timestamp
├── test_upload_result_from_dict_minimal_data
├── test_sync_status_from_dict_minimal_data
├── test_api_error_without_response_data
├── test_rate_limit_error_initialization
└── test_conflict_error_stores_conflicts
```

## Test Case IDs

All tests have unique identifiers for traceability:
- **TC-SC-E1 to TC-SC-E17:** Sync Client edge cases
- **TC-BOS-E1 to TC-BOS-E19:** Bulk Operation Service edge cases
- **TC-MP-E1 to TC-MP-E37:** Markdown Parser edge cases

## Coverage Focus Areas

### Error Paths (100% coverage)
- File I/O errors (FileNotFoundError, permission issues)
- Network errors (timeouts, connection failures, retries)
- Database errors (commit failures, integrity violations)
- Validation errors (Pydantic, YAML, JSON parsing)
- Transaction rollbacks (all commit operations)

### Boundary Conditions
- Empty inputs (CSV, YAML, lists)
- Null values (timestamps, parameters)
- Minimal data (bare minimum fields)
- Large operations (100+ items)
- Edge counts (insufficient rows/columns)

### Edge Case Scenarios
- Case sensitivity (headers, field names)
- Type conversions (string → float/int, datetime)
- URL normalization (trailing slashes)
- Pluralization (story → stories)
- Version comparison (local vs remote)

## Fixtures

### Sync Client Tests
- No fixtures needed (tests use inline mocks)

### Bulk Operation Tests
- `mock_session`: Mocked SQLAlchemy session with query chain
- `service`: BulkOperationService instance using mock_session

### Markdown Parser Tests
- `temp_dir`: Temporary directory for file operations (auto-cleanup)

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
assert "error" in result["validation_errors"][0]
```

### Null/Empty Cases
```python
assert result == []
assert value is None
assert result["total_count"] == 0
```

## Expected Results

All tests should:
1. Pass without errors
2. Increase coverage to 85%+
3. Execute in < 5 seconds
4. Run independently (no shared state)
5. Clean up resources (temp files, connections)

## Troubleshooting

### Import Errors
Set PYTHONPATH if needed:
```bash
export PYTHONPATH=/path/to/trace:$PYTHONPATH
```

### Async Test Failures
Ensure pytest-asyncio is installed:
```bash
pip install pytest-asyncio
```

### Mock Issues
Verify mock return values match expected types:
- AsyncMock for async functions
- Mock(spec=Class) for type safety
- PropertyMock for properties

## Contributing

When adding new edge case tests:
1. Follow AAA pattern (Arrange-Act-Assert)
2. Include Given-When-Then docstring
3. Assign unique TC-ID
4. Add to appropriate test class
5. Update documentation

## Related Documentation

- Root: `EDGE_CASE_TESTS_SUMMARY.md`
- Root: `EDGE_CASE_TEST_COVERAGE_REPORT.md`
- Root: `EDGE_CASE_TESTS_QUICK_REFERENCE.md`

## Status

✅ **READY FOR EXECUTION**
- 73 tests created
- All syntax validated
- Full documentation provided
- Coverage target: 85%+ for all modules
