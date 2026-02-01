# Jira Import Service - Test Implementation Examples

## Testing Patterns and Best Practices Demonstrated

### 1. Initialization Testing

**What**: Service initialization with dependency injection
**Why**: Ensures all repositories are properly wired
**How**:

```python
def test_jira_import_service_initialization(self):
    """Test JiraImportService can be instantiated with session."""
    mock_session = MagicMock()
    service = JiraImportService(mock_session)
    
    assert service.session == mock_session
    assert service.projects is not None
    assert service.items is not None
    assert service.links is not None
    assert service.events is not None
```

**Key Points**:
- Validates dependency injection
- Checks all repositories initialized
- Simple and focused assertion

---

### 2. Mapping Validation Testing

**What**: Verify all static mappings are complete
**Why**: Catch missing mappings before production use
**How**:

```python
def test_jira_status_map_completeness(self):
    """Test STATUS_MAP contains all expected Jira status mappings."""
    assert JiraImportService.STATUS_MAP["To Do"] == "todo"
    assert JiraImportService.STATUS_MAP["In Progress"] == "in_progress"
    assert JiraImportService.STATUS_MAP["In Review"] == "in_progress"
    assert JiraImportService.STATUS_MAP["Done"] == "complete"
    assert JiraImportService.STATUS_MAP["Closed"] == "complete"
```

**Key Points**:
- Tests all 5 Jira statuses
- Verifies exact mapping values
- Easy to add new statuses

---

### 3. Input Validation Testing

**What**: Validate JSON structure and required fields
**Why**: Prevent processing of malformed data
**How**:

```python
@pytest.mark.asyncio
async def test_validate_jira_export_invalid_json(self):
    """Test validation rejects invalid JSON."""
    mock_session = MagicMock()
    service = JiraImportService(mock_session)
    
    errors = await service.validate_jira_export("not valid json {")
    assert len(errors) > 0
    assert "Invalid JSON" in errors[0]
```

**Key Points**:
- Uses @pytest.mark.asyncio for async methods
- Tests error case
- Validates error message content

---

### 4. Data Transformation Testing

**What**: Verify Jira data transforms to TraceRTM format
**Why**: Ensure data integrity during import
**How**:

```python
@pytest.mark.asyncio
async def test_import_single_jira_issue_status_mapping(self):
    """Test issue import maps Jira status correctly."""
    mock_session = MagicMock()
    service = JiraImportService(mock_session)
    
    mock_item = MagicMock()
    mock_item.id = "item-123"
    service.items.create = AsyncMock(return_value=mock_item)
    service.events.log = AsyncMock()
    
    issue = {
        "key": "PROJ-1",
        "id": "123",
        "fields": {
            "summary": "Issue in progress",
            "description": "",
            "status": {"name": "In Progress"},
            "issuetype": {"name": "Story"}
        }
    }
    
    await service._import_jira_issue("project-123", issue, "agent-1")
    
    call_args = service.items.create.call_args
    assert call_args.kwargs["status"] == "in_progress"
    assert call_args.kwargs["item_type"] == "story"
```

**Key Points**:
- Mocks async operations with AsyncMock
- Validates transformation logic
- Checks call arguments to verify correct values passed

---

### 5. Metadata Preservation Testing

**What**: Verify Jira metadata stored in items
**Why**: Maintain traceability to source system
**How**:

```python
@pytest.mark.asyncio
async def test_import_single_jira_issue_metadata_storage(self):
    """Test that Jira metadata is stored in item."""
    service = JiraImportService(MagicMock())
    
    mock_item = MagicMock()
    mock_item.id = "item-123"
    service.items.create = AsyncMock(return_value=mock_item)
    service.events.log = AsyncMock()
    
    issue = {
        "key": "PROJ-1",
        "id": "123",
        "fields": {"summary": "Test"}
    }
    
    await service._import_jira_issue("project-123", issue, "agent-1")
    
    call_args = service.items.create.call_args
    metadata = call_args.kwargs["metadata"]
    assert metadata["jira_key"] == "PROJ-1"
    assert metadata["jira_id"] == "123"
```

**Key Points**:
- Extracts kwargs from mock call
- Validates metadata structure
- Ensures source traceability

---

### 6. Event Logging Testing

**What**: Verify events logged for audit trail
**Why**: Enable tracking and debugging of imports
**How**:

```python
@pytest.mark.asyncio
async def test_import_single_jira_issue_event_logging(self):
    """Test that event is logged when issue is imported."""
    service = JiraImportService(MagicMock())
    
    mock_item = MagicMock()
    mock_item.id = "item-123"
    service.items.create = AsyncMock(return_value=mock_item)
    service.events.log = AsyncMock()
    
    issue = {"key": "PROJ-1", "id": "123", "fields": {"summary": "Test"}}
    
    await service._import_jira_issue("project-123", issue, "agent-1")
    
    service.events.log.assert_called_once()
    call_args = service.events.log.call_args
    assert call_args.kwargs["event_type"] == "jira_issue_imported"
    assert call_args.kwargs["entity_type"] == "item"
    assert call_args.kwargs["entity_id"] == "item-123"
    assert call_args.kwargs["agent_id"] == "agent-1"
```

**Key Points**:
- Verifies mock was called exactly once
- Validates all event parameters
- Ensures correct agent context

---

### 7. Relationship/Link Testing

**What**: Verify issue links created correctly
**Why**: Maintain traceability between related items
**How**:

```python
@pytest.mark.asyncio
async def test_import_jira_links_basic(self):
    """Test importing links between Jira issues."""
    service = JiraImportService(MagicMock())
    
    mock_link = MagicMock()
    mock_link.id = "link-123"
    service.links.create = AsyncMock(return_value=mock_link)
    
    issue = {
        "key": "PROJ-1",
        "id": "123",
        "fields": {
            "issuelinks": [
                {
                    "type": {"name": "relates to"},
                    "outwardIssue": {"key": "PROJ-2"}
                }
            ]
        }
    }
    
    issue_map = {"PROJ-1": "item-1", "PROJ-2": "item-2"}
    
    result = await service._import_jira_links(
        "project-123", issue, issue_map, "agent-1"
    )
    
    assert len(result) == 1
    service.links.create.assert_called_once()
    call_args = service.links.create.call_args
    assert call_args.kwargs["source_item_id"] == "item-1"
    assert call_args.kwargs["target_item_id"] == "item-2"
    assert call_args.kwargs["link_type"] == "relates_to"
```

**Key Points**:
- Maps issue keys to item IDs
- Validates link creation parameters
- Tests link type mapping

---

### 8. Error Handling - Missing Target Testing

**What**: Gracefully skip links with missing targets
**Why**: Prevent cascading failures from incomplete data
**How**:

```python
@pytest.mark.asyncio
async def test_import_jira_links_missing_target(self):
    """Test that links with missing target issues are skipped."""
    service = JiraImportService(MagicMock())
    service.links.create = AsyncMock()
    
    issue = {
        "key": "PROJ-1",
        "id": "123",
        "fields": {
            "issuelinks": [
                {
                    "type": {"name": "relates to"},
                    "outwardIssue": {"key": "PROJ-UNKNOWN"}
                }
            ]
        }
    }
    
    issue_map = {"PROJ-1": "item-1"}
    
    result = await service._import_jira_links(
        "project-123", issue, issue_map, "agent-1"
    )
    
    assert len(result) == 0
    service.links.create.assert_not_called()
```

**Key Points**:
- Tests graceful degradation
- Verifies no exception thrown
- Confirms mock not called for invalid case

---

### 9. Partial Failure Testing

**What**: Continue import despite some items failing
**Why**: Maximize successful imports despite errors
**How**:

```python
@pytest.mark.asyncio
async def test_import_jira_project_partial_import_failure(self):
    """Test import with some issues failing but others succeeding."""
    service = JiraImportService(MagicMock())
    
    mock_project = MagicMock()
    mock_project.id = "proj-123"
    service.projects.create = AsyncMock(return_value=mock_project)
    
    mock_item = MagicMock()
    mock_item.id = "item-1"
    service.items.create = AsyncMock(
        side_effect=[
            mock_item,  # First issue succeeds
            Exception("Database error")  # Second issue fails
        ]
    )
    
    service.events.log = AsyncMock()
    service.links.create = AsyncMock()
    
    valid_data = json.dumps({
        "issues": [
            {"key": "PROJ-1", "id": "123", "fields": {"summary": "Issue 1"}},
            {"key": "PROJ-2", "id": "124", "fields": {"summary": "Issue 2"}}
        ]
    })
    
    result = await service.import_jira_project("TestProject", valid_data)
    
    assert result["success"] is True
    assert result["items_imported"] == 1
    assert any("Failed to import PROJ-2" in error for error in result["errors"])
```

**Key Points**:
- Uses side_effect to simulate mixed success/failure
- Validates partial success reporting
- Verifies error details captured

---

### 10. Default Value Testing

**What**: Use sensible defaults for unknown values
**Why**: Handle unexpected data gracefully
**How**:

```python
@pytest.mark.asyncio
async def test_import_jira_issue_unknown_status(self):
    """Test issue import with unmapped status defaults to todo."""
    service = JiraImportService(MagicMock())
    
    mock_item = MagicMock()
    mock_item.id = "item-123"
    service.items.create = AsyncMock(return_value=mock_item)
    service.events.log = AsyncMock()
    
    issue = {
        "key": "PROJ-1",
        "id": "123",
        "fields": {
            "summary": "Test",
            "status": {"name": "Unknown Status"},
            "issuetype": {"name": "Task"}
        }
    }
    
    await service._import_jira_issue("project-123", issue, "agent-1")
    
    call_args = service.items.create.call_args
    assert call_args.kwargs["status"] == "todo"
```

**Key Points**:
- Tests fallback behavior
- Validates default values
- Prevents import failures from unknown values

---

### 11. Null/Missing Field Testing

**What**: Handle completely missing nested fields
**Why**: Prevent KeyError exceptions
**How**:

```python
@pytest.mark.asyncio
async def test_import_jira_issue_none_status_name(self):
    """Test handling of None status name."""
    service = JiraImportService(MagicMock())
    
    mock_item = MagicMock()
    mock_item.id = "item-123"
    service.items.create = AsyncMock(return_value=mock_item)
    service.events.log = AsyncMock()
    
    issue = {
        "key": "PROJ-1",
        "id": "123",
        "fields": {
            "summary": "Test",
            "status": {},  # No 'name' key
            "issuetype": {}  # No 'name' key
        }
    }
    
    await service._import_jira_issue("project-123", issue, "agent-1")
    
    call_args = service.items.create.call_args
    assert call_args.kwargs["status"] == "todo"
    assert call_args.kwargs["item_type"] == "task"
```

**Key Points**:
- Tests robustness with missing nested values
- Validates default fallbacks
- Prevents exceptions from incomplete data

---

### 12. Full Workflow Testing

**What**: Test complete project import with multiple operations
**Why**: Validate end-to-end functionality
**How**:

```python
@pytest.mark.asyncio
async def test_import_jira_project_success(self):
    """Test successful import of Jira project with issues."""
    service = JiraImportService(MagicMock())
    
    mock_project = MagicMock()
    mock_project.id = "proj-123"
    service.projects.create = AsyncMock(return_value=mock_project)
    
    mock_item = MagicMock()
    mock_item.id = "item-1"
    service.items.create = AsyncMock(return_value=mock_item)
    
    service.events.log = AsyncMock()
    service.links.create = AsyncMock()
    
    valid_data = json.dumps({
        "issues": [
            {
                "key": "PROJ-1",
                "id": "123",
                "fields": {
                    "summary": "Issue 1",
                    "description": "Description 1",
                    "status": {"name": "To Do"},
                    "issuetype": {"name": "Task"}
                }
            },
            {
                "key": "PROJ-2",
                "id": "124",
                "fields": {
                    "summary": "Issue 2",
                    "description": "Description 2",
                    "status": {"name": "Done"},
                    "issuetype": {"name": "Story"}
                }
            }
        ]
    })
    
    result = await service.import_jira_project("TestProject", valid_data)
    
    assert result["success"] is True
    assert result["project_id"] == "proj-123"
    assert result["items_imported"] == 2
    assert len(result["errors"]) == 0
```

**Key Points**:
- Tests complete workflow
- Validates multiple operations
- Confirms success reporting

---

## Testing Principles Applied

### 1. **AAA Pattern (Arrange, Act, Assert)**
Every test follows three distinct phases:
- **Arrange**: Set up test data and mocks
- **Act**: Call the method under test
- **Assert**: Verify results and behavior

### 2. **Single Responsibility**
Each test focuses on one specific behavior, making failures easy to diagnose.

### 3. **Isolation**
Tests don't depend on each other; mocks ensure no external dependencies.

### 4. **Clarity**
Descriptive test names explain what is being tested and why it matters.

### 5. **Comprehensive Assertions**
Tests verify both return values AND side effects (mock calls).

### 6. **Edge Case Coverage**
Tests include boundary conditions, missing data, and error scenarios.

### 7. **Async Support**
Proper use of @pytest.mark.asyncio for async method testing.

### 8. **Mock Verification**
Tests verify correct interactions with dependencies, not just return values.

---

## Best Practices Summary

| Pattern | Benefit | Example |
|---------|---------|---------|
| AAA (Arrange-Act-Assert) | Clear test structure | Setup → Call → Verify |
| Single responsibility | Easy debugging | One behavior per test |
| Isolation via mocks | Fast, reliable tests | No external dependencies |
| Descriptive names | Self-documenting | test_import_jira_issue_missing_fields |
| Multiple assertions | Complete validation | Check return + mock calls |
| Edge case tests | Robustness | Unknown values, missing fields |
| Async support | Real-world testing | @pytest.mark.asyncio |
| Error scenarios | Reliability | Exception handling, degradation |

All 36 tests implement these best practices consistently.
