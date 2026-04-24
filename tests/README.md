# TraceRTM Test Suite

Test index, config docs, and SQL fixtures: [docs/](docs/), [sql/](sql/).

**Test Framework**: pytest 7.4+  
**Coverage Target**: 80%+ (90%+ for business logic)  
**Test Strategy**: Unit → Integration → E2E

---

## Quick Start

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run all tests
pytest

# Run with coverage
pytest --cov=tracertm --cov-report=html

# Run specific test categories
pytest -m unit          # Fast unit tests only
pytest -m integration   # Integration tests (requires PostgreSQL)
pytest -m e2e           # End-to-end CLI tests
pytest -m agent         # Agent coordination tests

# Run tests in parallel (faster)
pytest -n auto

# Run specific test file
pytest tests/unit/test_item_repository.py

# Run specific test function
pytest tests/unit/test_item_repository.py::test_create_item_valid
```

---

## Test Directory Structure

```
tests/
├── conftest.py                 # Shared fixtures and configuration
├── README.md                   # This file
├── factories/                  # Test data factories
│   ├── __init__.py
│   ├── item_factory.py         # Item factory with faker
│   ├── project_factory.py      # Project factory
│   └── link_factory.py         # Link factory
├── fixtures/                   # Test fixtures and helpers
│   ├── __init__.py
│   ├── database.py             # Database fixtures
│   └── cli.py                  # CLI test helpers
├── unit/                       # Unit tests (fast, isolated)
│   ├── __init__.py
│   ├── test_item_repository.py
│   ├── test_link_repository.py
│   ├── test_project_repository.py
│   └── test_validators.py
├── integration/                # Integration tests (database, file system)
│   ├── __init__.py
│   ├── test_database_operations.py
│   ├── test_event_log.py
│   └── test_concurrent_operations.py
└── e2e/                        # End-to-end tests (full CLI workflows)
    ├── __init__.py
    ├── test_project_initialization.py
    ├── test_item_crud_workflow.py
    └── test_agent_coordination.py
```

---

## Test Categories

### Unit Tests (`tests/unit/`)
**Purpose**: Test individual functions/classes in isolation  
**Speed**: <100ms per test  
**Dependencies**: None (mocked)  
**Coverage Target**: 90%+

**Example**:
```python
@pytest.mark.unit
def test_create_item_valid(item_factory):
    item = item_factory.create(title="Test Feature", view="FEATURE")
    assert item.title == "Test Feature"
    assert item.view == "FEATURE"
```

### Integration Tests (`tests/integration/`)
**Purpose**: Test component interactions (database, file system)  
**Speed**: <1s per test  
**Dependencies**: PostgreSQL test database  
**Coverage Target**: 80%+

**Example**:
```python
@pytest.mark.integration
def test_item_repository_create(db_session):
    repo = ItemRepository(db_session)
    item = repo.create(title="Test", view="FEATURE")
    assert item.id is not None
```

### E2E Tests (`tests/e2e/`)
**Purpose**: Test complete user workflows via CLI  
**Speed**: <5s per test  
**Dependencies**: Full system (database, CLI)  
**Coverage Target**: 100% of critical workflows

**Example**:
```python
@pytest.mark.e2e
def test_create_and_show_item(cli_runner):
    result = cli_runner.invoke(app, ["create", "feature", "Test"])
    assert result.exit_code == 0
    assert "Created" in result.stdout
```

### Agent Tests (`tests/integration/`)
**Purpose**: Test concurrent agent operations  
**Speed**: <10s per test  
**Dependencies**: PostgreSQL, agent pool  
**Coverage Target**: 100% of concurrency scenarios

**Example**:
```python
@pytest.mark.agent
@pytest.mark.slow
def test_concurrent_updates_1000_agents(db_session, mock_agent_pool):
    # Test optimistic locking with 1000 concurrent agents
    pass
```

---

## Test Fixtures

### Database Fixtures
- `test_db_engine`: Session-scoped database engine
- `db_session`: Function-scoped database session (auto-rollback)
- `temp_project_dir`: Temporary directory for file operations

### Factory Fixtures
- `item_factory`: Create test items with faker data
- `project_factory`: Create test projects
- `link_factory`: Create test links between items

### CLI Fixtures
- `cli_runner`: Typer CLI test runner
- `test_config`: Test configuration dictionary

### Agent Fixtures
- `mock_agent_pool`: Mock agent pool for concurrency testing

---

## Writing Tests

### Test Naming Convention
```python
# Format: test_<function>_<scenario>
def test_create_item_valid():           # Happy path
def test_create_item_missing_title():   # Negative case
def test_create_item_invalid_view():    # Edge case
```

### Test Structure (AAA Pattern)
```python
def test_example():
    # Arrange: Set up test data
    item = ItemFactory.create()
    
    # Act: Execute the operation
    result = repository.update(item.id, title="New Title")
    
    # Assert: Verify the outcome
    assert result.title == "New Title"
```

### Assertion Best Practices
```python
# ✅ Good: Specific assertions
assert item.title == "Expected Title"
assert item.status == "todo"

# ❌ Bad: Generic assertions
assert item is not None
assert len(items) > 0
```

---

## Running Tests in CI

```yaml
# .github/workflows/test.yml
- name: Run tests
  run: |
    pytest --cov=tracertm --cov-report=xml
    
- name: Upload coverage
  uses: codecov/codecov-action@v3
```

---

## Test Data Management

### Using Factories
```python
from tests.factories import ItemFactory

# Create item with defaults
item = ItemFactory.create()

# Create item with overrides
item = ItemFactory.create(title="Custom Title", view="CODE")

# Create multiple items
items = ItemFactory.create_batch(10)
```

### Using Fixtures
```python
@pytest.fixture
def sample_project(db_session):
    project = Project(name="Test Project")
    db_session.add(project)
    db_session.commit()
    return project
```

---

## Troubleshooting

### Tests Failing Locally
1. Check PostgreSQL is running: `pg_isready`
2. Verify test database exists: `psql -l | grep tracertm_test`
3. Run migrations: `alembic upgrade head`
4. Clear pytest cache: `pytest --cache-clear`

### Slow Tests
1. Run only fast tests: `pytest -m "not slow"`
2. Use parallel execution: `pytest -n auto`
3. Profile slow tests: `pytest --durations=10`

### Coverage Issues
1. Check missing coverage: `pytest --cov-report=term-missing`
2. View HTML report: `open htmlcov/index.html`
3. Exclude test files: Already configured in `pyproject.toml`

---

## Next Steps

1. ✅ Test framework setup complete
2. → Create test factories (`tests/factories/`)
3. → Write unit tests for Epic 1 (Project Foundation)
4. → Run `*test-design` for Epic 1 to create test-design-epic-1.md
5. → Implement Epic 1 stories with TDD approach

---

**Framework Version**: 1.0  
**Last Updated**: 2025-11-21  
**Maintained By**: TEA (Murat - Master Test Architect)

