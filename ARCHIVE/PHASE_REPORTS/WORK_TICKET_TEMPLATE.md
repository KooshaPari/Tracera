# Work Ticket Template - Agent Execution

Copy this template for each work package ticket. Fill in details and assign to agent.

---

## TICKET TEMPLATE

### Header
```
Ticket ID: WP-[PHASE].[PRIORITY]
Title: [Brief title]
Component: [Module name]
Effort: [Hours]
Priority: [P0/P1/P2]
Assigned to: [Agent Name]
Status: [ ] Not Started [ ] In Progress [ ] Complete
```

---

## Example: WP-2.1 - Query Service Integration Tests

### Ticket Header
```
Ticket ID: WP-2.1
Title: Query Service Integration Tests - 80+ Test Coverage
Component: services/query_service.py
Effort: 30 hours
Priority: P0
Assigned to: Test Implementation Agent
Status: [X] Not Started [ ] In Progress [ ] Complete
```

### Objective
Implement comprehensive integration tests for `query_service.py` with real database (no mocks) achieving >80% coverage.

### Scope
**Create:** `tests/integration/test_query_service.py`

**Coverage Target:** 80+ tests covering:
- Basic CRUD operations (10 tests)
- Filtering by all attributes (15 tests)
- Pagination & sorting (10 tests)
- Complex join queries (15 tests)
- Error conditions (10 tests)
- Performance edge cases (10 tests)

### Acceptance Criteria
- [ ] File created: `tests/integration/test_query_service.py`
- [ ] 80+ test functions (test_* methods)
- [ ] All tests passing: `pytest tests/integration/test_query_service.py -v`
- [ ] Coverage >80%: Query service module fully covered
- [ ] No mocks for service layer (real database)
- [ ] Database cleanup/teardown working
- [ ] Docstrings on all test classes/methods
- [ ] PR created with description

### Prerequisites
- [ ] Agent understands fixture setup (see `tests/integration/conftest.py`)
- [ ] Agent can run pytest locally
- [ ] Agent familiar with query_service.py API
- [ ] Database SQLite available

### Key Files to Study
```
- src/tracertm/services/query_service.py (TARGET)
- src/tracertm/schemas/item.py (Data schemas)
- tests/integration/conftest.py (Fixtures)
- tests/integration/TEMPLATE.py (Example structure)
```

### Test Structure
```python
import pytest
from tests.integration_full.fixtures import get_test_db, create_sample_items

class TestQueryServiceBasicOperations:
    """CRUD operations on query service"""

    @pytest.fixture(autouse=True)
    def setup(self):
        self.db = get_test_db()
        self.service = QueryService(self.db)
        yield
        self.db.close()

    def test_query_all_items(self):
        """Test retrieving all items from database"""
        items = create_sample_items(self.db, 10)
        results = self.service.query_items()
        assert len(results) == 10
        # More assertions

    def test_query_with_filter_status(self):
        """Test querying items by status filter"""
        # Setup
        items = create_sample_items(self.db, 5)
        items[0].status = "APPROVED"
        items[1].status = "REJECTED"
        self.db.commit()

        # Execute
        results = self.service.query_items(filters={"status": "APPROVED"})

        # Verify
        assert len(results) == 1
        assert results[0].status == "APPROVED"
```

### Test Patterns Available

**Pattern 1: Sync Test (Standard)**
```python
def test_basic_operation(self):
    """Test synchronous operation"""
    data = self.service.operation(input_data)
    assert data is not None
```

**Pattern 2: Async Test (Database I/O)**
```python
@pytest.mark.asyncio
async def test_async_database_operation(self):
    """Test asynchronous database operation"""
    db = await get_test_db_async()
    item = await self.service.create_async(data)
    assert item.id is not None
    await db.close()
```

**Pattern 3: Parametrized Test (Multiple Cases)**
```python
@pytest.mark.parametrize("input,expected", [
    (data1, result1),
    (data2, result2),
])
def test_multiple_cases(self, input, expected):
    result = self.service.process(input)
    assert result == expected
```

**Pattern 4: Error Test (Exception Handling)**
```python
def test_error_condition(self):
    """Test error handling"""
    with pytest.raises(ValueError):
        self.service.process(invalid_data)
```

### Test Categories (Examples)

**Category 1: Basic Operations (10 tests)**
```python
def test_query_all_items(self): ...
def test_query_items_with_limit(self): ...
def test_query_items_with_offset(self): ...
def test_query_single_item_by_id(self): ...
def test_get_item_not_found(self): ...
# ... 5 more
```

**Category 2: Filtering (15 tests)**
```python
def test_filter_by_status(self): ...
def test_filter_by_type(self): ...
def test_filter_by_priority(self): ...
def test_filter_by_owner(self): ...
def test_filter_by_multiple_criteria(self): ...
# ... 10 more (one per filterable field)
```

**Category 3: Pagination & Sorting (10 tests)**
```python
def test_pagination_first_page(self): ...
def test_pagination_middle_page(self): ...
def test_pagination_last_page(self): ...
def test_sort_by_created_date(self): ...
def test_sort_by_title_ascending(self): ...
# ... 5 more
```

**Category 4: Complex Queries (15 tests)**
```python
def test_join_query_items_and_links(self): ...
def test_query_with_nested_filters(self): ...
def test_query_with_aggregation(self): ...
def test_query_with_grouping(self): ...
# ... 11 more
```

**Category 5: Error Handling (10 tests)**
```python
def test_query_with_invalid_filter(self): ...
def test_query_database_disconnected(self): ...
def test_query_large_result_set(self): ...
def test_query_timeout(self): ...
# ... 6 more
```

### Running Tests During Development
```bash
# Run all tests in file
pytest tests/integration/test_query_service.py -v

# Run specific test class
pytest tests/integration/test_query_service.py::TestQueryServiceBasicOperations -v

# Run with coverage
pytest tests/integration/test_query_service.py -v --cov=src/tracertm/services/query_service

# Run with output
pytest tests/integration/test_query_service.py -v -s

# Run with timeout (catch hangs)
pytest tests/integration/test_query_service.py -v --timeout=10
```

### Coverage Report
```bash
# Generate HTML report
pytest tests/integration/test_query_service.py --cov=src/tracertm/services/query_service --cov-report=html

# View report
open htmlcov/index.html

# Check missing lines
pytest tests/integration/test_query_service.py --cov=src/tracertm/services/query_service --cov-report=term-with-missing
```

### What NOT to Do
- ❌ Don't mock the service being tested
- ❌ Don't mock the database layer
- ❌ Don't use patch() on repository methods
- ❌ Don't skip error cases
- ❌ Don't test implementation, test behavior

### What TO Do
- ✅ Use real SQLite database (in-memory)
- ✅ Create real test data via factories
- ✅ Test business logic thoroughly
- ✅ Test error paths
- ✅ Test performance characteristics
- ✅ Clean up after each test (teardown)

### Common Issues & Solutions

**Issue: Tests timing out**
```python
# Solution: Add fixture cleanup
@pytest.fixture(autouse=True)
def setup(self):
    self.db = get_test_db()
    yield
    self.db.close()  # Important!
```

**Issue: Tests interfering with each other**
```python
# Solution: Use fresh database per test
@pytest.fixture(autouse=True)
def setup(self):
    self.db = get_test_db()  # Fresh DB
    # Clear tables
    self.db.query(Item).delete()
    self.db.commit()
    yield
    self.db.close()
```

**Issue: Coverage not increasing**
```bash
# Debug: See what lines NOT covered
pytest tests/integration/test_query_service.py \
    --cov=src/tracertm/services/query_service \
    --cov-report=term-with-missing
# Look for lines with "0" coverage count
```

### Deliverables Checklist
- [ ] File: `tests/integration/test_query_service.py` created
- [ ] 80+ test methods implemented
- [ ] All tests passing locally
- [ ] Coverage report shows >80%
- [ ] Docstrings complete
- [ ] No print() statements
- [ ] No skipped tests (@pytest.mark.skip)
- [ ] Git branch created
- [ ] PR submitted with:
  - [ ] Description of tests added
  - [ ] Coverage report screenshot
  - [ ] List of 80+ test methods
  - [ ] Any issues encountered

### PR Template
```markdown
## WP-2.1: Query Service Integration Tests

**Summary:** Added 80+ integration tests for query_service.py achieving >80% coverage.

**Test Categories:**
- Basic operations: 10 tests
- Filtering: 15 tests
- Pagination/sorting: 10 tests
- Complex queries: 15 tests
- Error handling: 10 tests
- Performance: 10 tests

**Coverage:** >80% (2,092 → 2,500+ lines covered)

**Tests Passing:** 80/80 ✅

**New Test Methods:**
1. test_query_all_items
2. test_query_with_limit
3. test_query_with_offset
... (full list)

**Known Issues:** None

**Testing Instructions:**
```bash
pytest tests/integration/test_query_service.py -v
```

**Screenshots:**
[Coverage report showing >80%]
```

### Questions?
- Check: `tests/integration/TEMPLATE.py` for example
- Review: `tests/integration/conftest.py` for fixtures
- Ask: Agent leads in daily standup

### Sign-Off
- Agent: _________________ Date: _______
- Lead Review: _________________ Date: _______

---

## Use This Template For Every Ticket

Each of the 32 work packages should be created as its own ticket using this template.

**Quick Copy-Paste for New Tickets:**
```markdown
### Ticket: WP-[X.Y]
**Title:** [Title from WORK_PACKAGES_AGENTS.md]
**Deliverables:** [From work package]
**Success Criteria:** [From work package]
**Effort:** [X] hours
**Priority:** [P0/P1/P2]

[Follow template structure above]
```

---

*Last Updated: December 8, 2025*
