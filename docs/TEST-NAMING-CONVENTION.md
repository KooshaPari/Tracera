# Test Naming Convention & Standards

**Date:** 2025-11-21  
**Status:** ✅ **ESTABLISHED**

---

## Test ID Format: TC-X.Y.Z

### Format Definition
```
TC-X.Y.Z-[test-name]

Where:
  X = Epic number (1-12)
  Y = Story number within epic (1-9)
  Z = Test case number within story (1-99)
  test-name = kebab-case description
```

### Examples
```
TC-1.1.1-successful-installation
TC-1.4.2-configuration-hierarchy
TC-2.3.5-detect-concurrent-updates
TC-5.1.3-multiple-agents-registration
TC-6.5.2-execute-saved-search
```

---

## Test File Organization

### Structure
```
tests/
├── unit/
│   ├── test_models_comprehensive.py
│   ├── test_database_models.py
│   ├── test_edge_cases.py
│   ├── test_performance.py
│   └── test_validation.py
├── integration/
│   ├── test_epic_1_*.py
│   ├── test_epic_2_*.py
│   └── ...
├── e2e/
│   ├── test_workflows_*.py
│   └── test_critical_paths_*.py
└── conftest.py
```

### Naming Pattern
```
test_epic_X_story_Y_*.py
test_epic_1_story_1_installation.py
test_epic_2_story_3_item_update.py
```

---

## Test Function Naming

### Pattern
```
def test_tc_X_Y_Z_description(fixture):
    """
    TC-X.Y.Z: Story Title - Test Case Description
    
    Given: Precondition
    When: Action
    Then: Expected result
    """
```

### Example
```python
def test_tc_1_4_1_set_configuration_value(config_manager):
    """
    TC-1.4.1: Configuration Management - Set Configuration Value
    
    Given: Configuration manager initialized
    When: Set a configuration value
    Then: Value is stored and retrievable
    """
    config_manager.set("key", "value")
    assert config_manager.get("key") == "value"
```

---

## Test Docstring Format

### Required Fields
```python
def test_tc_X_Y_Z_name(fixture):
    """
    TC-X.Y.Z: Story Title - Test Case Description
    
    FR: FR-XXX (Functional Requirement)
    Story: X.Y (Story ID)
    Type: Unit|Integration|E2E
    Priority: P0|P1|P2
    
    Given: Precondition
    When: Action
    Then: Expected result
    And: Additional assertion
    """
```

### Example
```python
def test_tc_2_3_1_update_item_title(test_db):
    """
    TC-2.3.1: Item Update - Update Item Title
    
    FR: FR11
    Story: 2.3
    Type: Integration
    Priority: P0
    
    Given: Item exists in database
    When: Update item title
    Then: Title is updated
    And: Version is incremented
    """
```

---

## Test Type Classification

### Unit Tests
- **Prefix:** `test_unit_`
- **Location:** `tests/unit/`
- **Scope:** Single function/method
- **Dependencies:** Mocked

### Integration Tests
- **Prefix:** `test_integration_`
- **Location:** `tests/integration/`
- **Scope:** Multiple components
- **Dependencies:** Real database

### E2E Tests
- **Prefix:** `test_e2e_`
- **Location:** `tests/e2e/`
- **Scope:** Complete workflow
- **Dependencies:** Full system

### Performance Tests
- **Prefix:** `test_perf_`
- **Location:** `tests/unit/` or `tests/integration/`
- **Scope:** Performance metrics
- **Dependencies:** Real data

### Security Tests
- **Prefix:** `test_security_`
- **Location:** `tests/integration/`
- **Scope:** Security scenarios
- **Dependencies:** Real system

---

## Test Traceability Mapping

### Bidirectional Traceability
```
FR (Functional Requirement)
  ↓
Story (User Story)
  ↓
Test Case (TC-X.Y.Z)
  ↓
Test Function (test_tc_X_Y_Z_name)
```

### Example
```
FR11 (Update item)
  ↓
Story 2.3 (Item Update with Optimistic Locking)
  ↓
TC-2.3.1 (Update item title)
  ↓
test_tc_2_3_1_update_item_title()
```

---

## Test Metadata

### Pytest Markers
```python
@pytest.mark.unit
@pytest.mark.integration
@pytest.mark.e2e
@pytest.mark.performance
@pytest.mark.security
@pytest.mark.slow
@pytest.mark.critical
```

### Example
```python
@pytest.mark.integration
@pytest.mark.critical
def test_tc_2_3_1_update_item_title(test_db):
    """..."""
```

---

## Test Coverage Requirements

### By Story
- Minimum 3 test cases per story
- Mix of positive, negative, edge cases
- At least 1 integration test per story

### By Epic
- Minimum 15 test cases per epic
- All FRs covered
- All workflows tested

### Overall
- Minimum 80% code coverage
- 100% FR coverage
- 100% story coverage

---

## Test Review Checklist

- [ ] Test has TC-X.Y.Z ID
- [ ] Test has proper docstring
- [ ] Test has FR reference
- [ ] Test has story reference
- [ ] Test has type classification
- [ ] Test has priority level
- [ ] Test follows naming convention
- [ ] Test is in correct location
- [ ] Test has proper assertions
- [ ] Test is independent

---

## CI/CD Integration

### Test Execution Order
1. Unit tests (fast)
2. Integration tests (medium)
3. E2E tests (slow)
4. Performance tests (optional)

### Coverage Gates
- Minimum 80% code coverage
- All tests passing
- No skipped tests
- Traceability complete

---

**Status:** ✅ **NAMING CONVENTION ESTABLISHED**
