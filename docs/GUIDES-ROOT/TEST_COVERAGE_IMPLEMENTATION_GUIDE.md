# Test Coverage Implementation Guide - 100% Coverage Roadmap

**Project**: Trace RTM  
**Goal**: Achieve 100% coverage across Statement, Function, Branch, User Story, and all test levels  
**Status**: Implementation Ready  
**Date**: November 21, 2024

---

## Quick Start

### Prerequisites
```bash
cd /Users/kooshapari/temp-PRODVERCEL/485/kush/trace
source .venv/bin/activate

# Or use directly
.venv/bin/python -m pip install pytest pytest-cov pytest-asyncio pytest-mock pytest-xdist hypothesis faker factory-boy
```

### Run Coverage Analysis
```bash
# Baseline coverage
.venv/bin/python -m pytest --cov=src --cov-report=term-missing --cov-report=html

# Branch coverage
.venv/bin/python -m pytest --cov=src --cov-branch --cov-report=term-missing

# By module
.venv/bin/python -m pytest --cov=src --cov-report=term-missing:skip-covered
```

---

## Coverage Dimensions Explained

### 1. **Statement Coverage (Line Coverage)**
- **Definition**: Percentage of executable statements that have been executed
- **Target**: 100%
- **How to measure**: `pytest --cov=src --cov-report=term-missing`
- **Benefit**: Ensures all code paths are executed at least once

**Example**:
```python
def process(value):
    if value > 0:
        return value * 2  # Line 1: Must execute
    else:
        return 0  # Line 2: Must execute
    # Every line must be hit

# Tests needed
assert process(5) == 10  # Covers Line 1
assert process(-1) == 0  # Covers Line 2
```

### 2. **Function Coverage**
- **Definition**: Percentage of functions/methods that have tests
- **Target**: 100%
- **How to measure**: Count functions vs. tested functions
- **Benefit**: Ensures every function is exercised

**Checklist**:
```
- [ ] Every public function has at least one test
- [ ] Every method in every class has tests
- [ ] Private functions (if important) have tests
- [ ] Static methods and class methods tested
- [ ] Async functions properly tested with asyncio
```

### 3. **Branch Coverage**
- **Definition**: Percentage of conditional branches (if/else, try/except, loops) executed
- **Target**: 100%
- **How to measure**: `pytest --cov=src --cov-branch --cov-report=term-missing`
- **Benefit**: Ensures all decision paths are tested

**Example**:
```python
def classify(age):
    if age < 18:  # Branch 1: True path
        return "Minor"
    elif age < 65:  # Branch 2: True path  
        return "Adult"
    else:  # Branch 3: False path
        return "Senior"

# Tests needed - one for each branch
assert classify(10) == "Minor"   # Branch 1 True
assert classify(30) == "Adult"   # Branch 2 True
assert classify(70) == "Senior"  # Branch 3 True
```

### 4. **Code Path Coverage**
- **Definition**: All meaningful combinations of conditions tested
- **Target**: 100%
- **Benefit**: Catches edge case interactions

**Example**:
```python
def process(value, validate=False):
    if validate:
        if value:  # Path 1: validate=True, value=True
            return "OK"
        else:  # Path 2: validate=True, value=False
            return "Invalid"
    else:  # Path 3: validate=False (ignore value)
        return "Skipped"

# Tests needed - one per path
assert process(True, True) == "OK"
assert process(False, True) == "Invalid"
assert process(True, False) == "Skipped"
```

### 5. **User Story Coverage**
- **Definition**: Every user requirement/story has acceptance tests
- **Target**: 100%
- **Benefit**: Validates features work as expected

**Example**:
```
User Story: As a user, I want to create a project

Acceptance Criteria:
- [ ] User can enter project name
- [ ] User can set project description  
- [ ] Project is saved to database
- [ ] User is redirected to project page

Tests needed:
def test_create_project_with_name()
def test_create_project_with_description()
def test_project_saved_to_db()
def test_redirect_after_creation()
```

---

## Test Level Breakdown

### Unit Tests (60% of Total Tests)

**Focus**: Individual units in isolation

**Scope**:
- Individual functions
- Individual methods
- Class behavior
- Error handling

**Example**:
```python
# tests/unit/test_user_service.py
import pytest
from unittest.mock import Mock
from src.services.user_service import UserService

class TestUserService:
    @pytest.fixture
    def service(self):
        return UserService(db=Mock())
    
    def test_create_user_success(self, service):
        """Test successful user creation."""
        user = service.create("john@example.com", "John")
        assert user.email == "john@example.com"
        assert user.name == "John"
    
    def test_create_user_invalid_email(self, service):
        """Test error handling for invalid email."""
        with pytest.raises(ValueError):
            service.create("invalid-email", "John")
    
    def test_create_user_duplicate_email(self, service):
        """Test error handling for duplicate email."""
        service.db.user_exists.return_value = True
        with pytest.raises(DuplicateError):
            service.create("john@example.com", "John")
```

**Coverage Target**: 95%+

---

### Integration Tests (25% of Total Tests)

**Focus**: Components working together

**Scope**:
- Service-to-database interactions
- API endpoint handling
- Event bus publishing/handling
- CLI command execution

**Example**:
```python
# tests/integration/test_user_workflow.py
import pytest
from src.db import SessionLocal
from src.services.user_service import UserService
from src.models.user import User

@pytest.mark.asyncio
async def test_user_creation_and_retrieval(db_session):
    """Test user creation and retrieval from database."""
    service = UserService(db=db_session)
    
    # Create
    user = service.create("john@example.com", "John")
    db_session.commit()
    
    # Retrieve
    retrieved = db_session.query(User).filter_by(email="john@example.com").first()
    assert retrieved.name == "John"
    assert retrieved.email == "john@example.com"

@pytest.mark.asyncio
async def test_project_creation_event(db_session, event_bus):
    """Test event is published when project is created."""
    service = ProjectService(db=db_session, event_bus=event_bus)
    
    project = service.create(name="Test Project")
    db_session.commit()
    
    # Verify event was published
    events = event_bus.get_events('project_created')
    assert len(events) == 1
    assert events[0].project_id == project.id
```

**Coverage Target**: 85%+

---

### E2E Tests (10% of Total Tests)

**Focus**: Complete user workflows

**Scope**:
- Full feature workflows
- User-facing CLI interactions
- API-to-database flows
- Acceptance criteria validation

**Example**:
```python
# tests/e2e/test_user_project_workflow.py
from click.testing import CliRunner
from src.cli.main import cli

def test_user_creates_project_and_adds_items():
    """Test complete workflow: create project, add items."""
    runner = CliRunner()
    
    # Create project
    result = runner.invoke(cli, ['project', 'create', '--name', 'My Project'])
    assert result.exit_code == 0
    assert 'My Project' in result.output
    
    # Create item in project
    result = runner.invoke(cli, [
        'item', 'create',
        '--project', 'My Project',
        '--title', 'Feature 1'
    ])
    assert result.exit_code == 0
    
    # Verify item exists
    result = runner.invoke(cli, ['project', 'show', '--name', 'My Project'])
    assert 'Feature 1' in result.output

def test_user_cannot_create_duplicate_project():
    """Test validation: cannot create duplicate project."""
    runner = CliRunner()
    
    # Create first project
    runner.invoke(cli, ['project', 'create', '--name', 'Duplicate'])
    
    # Try to create duplicate
    result = runner.invoke(cli, ['project', 'create', '--name', 'Duplicate'])
    assert result.exit_code != 0
    assert 'already exists' in result.output
```

**Coverage Target**: 80%+

---

### Performance Tests (5% of Total Tests)

**Focus**: Performance benchmarks and optimization

```python
# tests/performance/test_performance.py
import pytest
from src.services.project_service import ProjectService

@pytest.mark.benchmark
def test_query_large_dataset_performance(benchmark, db_session):
    """Benchmark querying large dataset."""
    service = ProjectService(db=db_session)
    
    # Create 10k items
    for i in range(10000):
        service.create_item(f"item_{i}")
    
    # Benchmark query
    result = benchmark(service.list_items)
    assert len(result) == 10000
    assert result.total_time < 1.0  # Must complete in <1 second

@pytest.mark.benchmark
def test_memory_usage(benchmark, db_session):
    """Benchmark memory usage."""
    service = ProjectService(db=db_session)
    
    result = benchmark(service.process_large_batch, 10000)
    assert result is not None
```

---

### Security Tests (5% of Total Tests)

**Focus**: Security validation

```python
# tests/security/test_security.py
import pytest
from src.auth import authenticate
from src.db import SessionLocal

def test_password_not_stored_plain():
    """Test passwords are hashed, not plain text."""
    user = create_test_user("test@example.com", "password123")
    
    assert user.password != "password123"
    assert user.password.startswith("$2b$")  # bcrypt

def test_sql_injection_prevention():
    """Test SQL injection is prevented."""
    result = query_user(email="'; DROP TABLE users; --")
    assert result is None  # Should not execute malicious SQL

def test_unauthorized_access_blocked():
    """Test unauthorized users cannot access resources."""
    response = get_project(project_id=1, auth_token="invalid")
    assert response.status_code == 401

def test_xss_prevention():
    """Test XSS attack is prevented."""
    xss_payload = "<script>alert('xss')</script>"
    project = create_project(name=xss_payload)
    
    output = render_project(project)
    assert "<script>" not in output  # Script should be escaped
```

---

## Module-by-Module Coverage Plan

### models/ (User, Project, Item, Link, etc.)

**Target**: 100% Statement, Function, Branch

```python
# tests/unit/models/test_user.py
class TestUserModel:
    def test_user_creation(self):
        user = User(email="test@example.com", name="Test")
        assert user.email == "test@example.com"
    
    def test_user_validation(self):
        with pytest.raises(ValueError):
            User(email="invalid", name="")
    
    def test_user_methods(self):
        user = User(email="test@example.com")
        assert user.is_admin() == False
        assert str(user) == "Test (test@example.com)"
```

### services/ (Business Logic)

**Target**: 100% Statement, Function, Branch

```python
# tests/unit/services/test_project_service.py
class TestProjectService:
    def test_create_project(self, service):
        project = service.create("Test", owner_id=1)
        assert project.name == "Test"
    
    def test_create_project_validates_name(self, service):
        with pytest.raises(ValidationError):
            service.create("", owner_id=1)
    
    def test_list_projects(self, service):
        service.create("Project 1", owner_id=1)
        service.create("Project 2", owner_id=1)
        projects = service.list_by_owner(owner_id=1)
        assert len(projects) == 2
```

### repositories/ (Data Access)

**Target**: 100% Statement, Function, Branch

```python
# tests/unit/repositories/test_project_repository.py
class TestProjectRepository:
    def test_save_project(self, repo, db_session):
        project = Project(name="Test")
        repo.save(project)
        db_session.commit()
        
        found = db_session.query(Project).filter_by(name="Test").first()
        assert found.name == "Test"
    
    def test_find_by_id(self, repo, db_session):
        # Create and save
        project = repo.save(Project(name="Test"))
        
        # Find
        found = repo.find_by_id(project.id)
        assert found.name == "Test"
```

### CLI Commands

**Target**: 100% Statement, Function, Branch

```python
# tests/unit/cli/test_project_commands.py
def test_create_project_command(runner, db):
    result = runner.invoke(cli, ['project', 'create', '--name', 'Test'])
    assert result.exit_code == 0
    assert db.query(Project).filter_by(name='Test').first() is not None

def test_create_project_no_name(runner):
    result = runner.invoke(cli, ['project', 'create'])
    assert result.exit_code != 0
    assert 'name' in result.output
```

---

## Test Data Management

### Using Factories

```python
# tests/factories/user_factory.py
import factory
from src.models.user import User

class UserFactory(factory.Factory):
    class Meta:
        model = User
    
    id = factory.Sequence(lambda n: n)
    email = factory.Faker('email')
    name = factory.Faker('name')
    password = factory.PostGenerationMethodCall('set_password', 'password')
    is_active = True

# Usage in tests
user = UserFactory.create(email="custom@example.com")
users = UserFactory.create_batch(10)
```

### Using Fixtures

```python
# tests/conftest.py
@pytest.fixture
def admin_user(db_session):
    user = User(email="admin@example.com", is_admin=True)
    db_session.add(user)
    db_session.commit()
    return user

@pytest.fixture
def sample_project(admin_user, db_session):
    project = Project(name="Sample", owner=admin_user)
    db_session.add(project)
    db_session.commit()
    return project
```

---

## Coverage Enforcement

### pytest.ini Configuration

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
asyncio_mode = auto

# Coverage requirements
addopts = 
    --cov=src
    --cov-branch
    --cov-report=term-missing:skip-covered
    --cov-report=html
    --cov-report=xml
    --cov-fail-under=100
    -v

[coverage:run]
branch = True
source = src
omit = 
    */migrations/*
    */tests/*

[coverage:report]
exclude_lines =
    pragma: no cover
    def __repr__
    raise AssertionError
    raise NotImplementedError
    if __name__ == .__main__.:
    if TYPE_CHECKING:
    @abstractmethod
    @abstract
skip_covered = True
fail_under = 100

[coverage:html]
directory = htmlcov
```

### GitHub Actions

```yaml
# .github/workflows/coverage.yml
name: Test Coverage

on: [push, pull_request]

jobs:
  coverage:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: "3.12"
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -e ".[dev]"
      
      - name: Run tests with coverage
        run: |
          pytest --cov=src --cov-branch --cov-report=xml --cov-report=term-missing
      
      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v3
        with:
          files: ./coverage.xml
          flags: unittests
          fail_ci_if_error: true
          minimum_coverage: 100
```

---

## Implementation Checklist

### Step 1: Setup
- [ ] Install pytest, pytest-cov, pytest-asyncio, pytest-mock
- [ ] Configure pytest.ini or pyproject.toml
- [ ] Create conftest.py with shared fixtures
- [ ] Create factories for test data

### Step 2: Analysis
- [ ] Run baseline coverage: `pytest --cov=src --cov-report=term-missing`
- [ ] Identify coverage gaps
- [ ] Prioritize by criticality

### Step 3: Unit Tests
- [ ] Cover all models
- [ ] Cover all services
- [ ] Cover all utilities
- [ ] Cover all repositories
- [ ] Cover all CLI commands
- [ ] Cover error paths

### Step 4: Integration Tests
- [ ] Test service interactions
- [ ] Test database operations
- [ ] Test event handling
- [ ] Test API endpoints
- [ ] Test CLI workflows

### Step 5: E2E Tests
- [ ] Test complete user workflows
- [ ] Test acceptance criteria
- [ ] Test error scenarios
- [ ] Test edge cases

### Step 6: Special Tests
- [ ] Performance baselines
- [ ] Security validation
- [ ] Concurrency handling
- [ ] Large data handling

### Step 7: Enforcement
- [ ] Configure CI/CD
- [ ] Set coverage requirements
- [ ] Add pre-commit hooks
- [ ] Monitor coverage trends

---

## Commands Reference

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=term-missing

# Branch coverage
pytest --cov=src --cov-branch --cov-report=term-missing

# HTML report
pytest --cov=src --cov-report=html
# Then open: htmlcov/index.html

# Specific test file
pytest tests/unit/test_models.py

# Specific test class
pytest tests/unit/test_models.py::TestUser

# Specific test
pytest tests/unit/test_models.py::TestUser::test_creation

# Run in parallel
pytest -n auto

# Stop on first failure
pytest -x

# Show print statements
pytest -s

# Verbose
pytest -vv

# Run only failed tests
pytest --lf

# Fail fast with short summary
pytest -x --tb=short
```

---

## Success Metrics

✅ **100% Statement Coverage** - Every line executed  
✅ **100% Function Coverage** - Every function tested  
✅ **100% Branch Coverage** - Every condition path tested  
✅ **100% User Story Coverage** - All requirements tested  
✅ **95%+ Unit Tests** - Comprehensive unit testing  
✅ **85%+ Integration Tests** - Component interaction testing  
✅ **80%+ E2E Tests** - Workflow testing  
✅ **Automated Enforcement** - CI/CD coverage gates  
✅ **Zero Flaky Tests** - Deterministic test results  
✅ **Fast Execution** - Tests run in <30 seconds  

---

## Next: Execution

Ready to start implementing tests? Follow this workflow:

1. Run `pytest --cov=src --cov-report=term-missing` to see gaps
2. Create test files for each module
3.
