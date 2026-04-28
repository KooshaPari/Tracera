# Testing Guide

> Comprehensive testing strategies for Pheno-SDK applications

---

## Table of Contents

- [Testing Philosophy](#testing-philosophy)
- [Test Types](#test-types)
- [Unit Testing](#unit-testing)
- [Integration Testing](#integration-testing)
- [End-to-End Testing](#end-to-end-testing)
- [Testing Best Practices](#testing-best-practices)
- [Fixtures and Mocks](#fixtures-and-mocks)
- [Coverage](#coverage)
- [CI/CD Integration](#cicd-integration)

---

## Testing Philosophy

Pheno-SDK makes testing easy through:

1. **In-Memory Implementations** - Fast unit tests without external dependencies
2. **Dependency Injection** - Easy to swap real implementations with mocks
3. **Clear Interfaces** - Test against abstractions, not implementations
4. **Async Support** - Full pytest-asyncio integration

---

## Test Types

### 1. Unit Tests
- Test individual functions/classes in isolation
- Use in-memory implementations
- Fast execution (<1ms per test)
- No external dependencies

### 2. Integration Tests
- Test interaction between components
- Use real implementations (database, storage, etc.)
- Moderate execution time
- Require test infrastructure

### 3. End-to-End Tests
- Test complete user workflows
- Full application stack
- Slow execution
- Production-like environment

---

## Unit Testing

### Testing with In-Memory Implementations

```python
import pytest
from adapter_kit import InMemoryRepository
from dataclasses import dataclass
from typing import Optional

@dataclass
class User:
    id: Optional[str]
    email: str
    name: str

class UserService:
    def __init__(self, repo):
        self.repo = repo

    async def create_user(self, email: str, name: str) -> User:
        user = User(id=None, email=email, name=name)
        return await self.repo.save(user)

    async def get_user(self, user_id: str) -> Optional[User]:
        return await self.repo.get_by_id(user_id)

# Unit tests - fast, no external dependencies
@pytest.mark.asyncio
async def test_create_user():
    """Test user creation with in-memory repository."""
    repo = InMemoryRepository()
    service = UserService(repo)

    user = await service.create_user("test@example.com", "Test User")

    assert user.id is not None
    assert user.email == "test@example.com"
    assert user.name == "Test User"

@pytest.mark.asyncio
async def test_get_user():
    """Test user retrieval."""
    repo = InMemoryRepository()
    service = UserService(repo)

    # Create user
    created = await service.create_user("test@example.com", "Test User")

    # Retrieve user
    retrieved = await service.get_user(created.id)

    assert retrieved is not None
    assert retrieved.id == created.id
    assert retrieved.email == created.email

@pytest.mark.asyncio
async def test_get_nonexistent_user():
    """Test retrieving non-existent user."""
    repo = InMemoryRepository()
    service = UserService(repo)

    user = await service.get_user("nonexistent-id")

    assert user is None
```

### Testing with Storage Kit

```python
from storage_kit import StorageClient
from storage_kit.providers import InMemoryStorageProvider

@pytest.mark.asyncio
async def test_file_upload():
    """Test file upload with in-memory storage."""
    client = StorageClient(InMemoryStorageProvider())

    # Upload file
    file = await client.upload("test.txt", b"Hello World")

    assert file.path == "test.txt"
    assert file.size == len(b"Hello World")

    # Download and verify
    data = await client.download("test.txt")
    assert data == b"Hello World"

@pytest.mark.asyncio
async def test_file_not_found():
    """Test downloading non-existent file."""
    client = StorageClient(InMemoryStorageProvider())

    with pytest.raises(FileNotFoundError):
        await client.download("nonexistent.txt")
```

### Testing with Vector Kit

```python
from vector_kit import SemanticSearch
from vector_kit.embeddings import InMemoryEmbeddings
from vector_kit.stores import InMemoryVectorStore

@pytest.mark.asyncio
async def test_semantic_search():
    """Test semantic search with in-memory components."""
    search = SemanticSearch(
        embedding_provider=InMemoryEmbeddings(),
        vector_store=InMemoryVectorStore()
    )

    # Index documents
    await search.index_documents([
        "Python is a programming language",
        "JavaScript is for web development",
        "Machine learning uses neural networks"
    ])

    # Search
    results = await search.search("programming", k=2)

    assert len(results) == 2
    assert "Python" in results[0].document.text
```

---

## Integration Testing

### Testing with Real Database

```python
import pytest
from db_kit import Database

@pytest.fixture
async def database():
    """Provide real database for integration tests."""
    db = Database.supabase()

    # Setup: Create test data
    yield db

    # Teardown: Clean up test data
    # await db.delete("users", filters={"email": {"like": "test%"}})

@pytest.mark.integration
@pytest.mark.asyncio
async def test_user_crud_operations(database):
    """Test CRUD operations with real database."""
    # Create
    user = await database.insert("users", {
        "email": "test@example.com",
        "username": "testuser",
        "active": True
    })
    assert user["id"] is not None
    user_id = user["id"]

    # Read
    retrieved = await database.get_single("users", filters={"id": user_id})
    assert retrieved["email"] == "test@example.com"

    # Update
    await database.update(
        "users",
        data={"username": "updated"},
        filters={"id": user_id}
    )
    updated = await database.get_single("users", filters={"id": user_id})
    assert updated["username"] == "updated"

    # Delete
    deleted_count = await database.delete("users", filters={"id": user_id})
    assert deleted_count == 1

    # Verify deletion
    not_found = await database.get_single("users", filters={"id": user_id})
    assert not_found is None
```

### Testing with Real Storage

```python
import pytest
from storage_kit import StorageClient
from storage_kit.providers import LocalStorageProvider
import tempfile
import shutil

@pytest.fixture
def storage_client():
    """Provide storage client with temporary directory."""
    temp_dir = tempfile.mkdtemp()
    client = StorageClient(LocalStorageProvider(base_path=temp_dir))

    yield client

    # Cleanup
    shutil.rmtree(temp_dir)

@pytest.mark.integration
@pytest.mark.asyncio
async def test_file_operations(storage_client):
    """Test file operations with real storage."""
    # Upload
    file = await storage_client.upload(
        "documents/test.txt",
        b"Test content",
        content_type="text/plain",
        metadata={"author": "test"}
    )
    assert file.path == "documents/test.txt"

    # Download
    content = await storage_client.download("documents/test.txt")
    assert content == b"Test content"

    # Delete
    await storage_client.delete("documents/test.txt")
```

---

## End-to-End Testing

### Testing FastAPI Application

```python
import pytest
from httpx import AsyncClient
from api import app

@pytest.fixture
async def client():
    """Provide HTTP client for API testing."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

@pytest.mark.e2e
@pytest.mark.asyncio
async def test_user_registration_flow(client):
    """Test complete user registration flow."""
    # Step 1: Register user
    response = await client.post("/register", json={
        "email": "newuser@example.com",
        "password": "SecurePass123",
        "username": "newuser"
    })
    assert response.status_code == 201
    user_id = response.json()["id"]

    # Step 2: Verify email (mock)
    response = await client.post(f"/verify-email", json={
        "user_id": user_id,
        "code": "123456"
    })
    assert response.status_code == 200

    # Step 3: Login
    response = await client.post("/login", json={
        "email": "newuser@example.com",
        "password": "SecurePass123"
    })
    assert response.status_code == 200
    token = response.json()["access_token"]

    # Step 4: Access protected resource
    response = await client.get(
        "/profile",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["email"] == "newuser@example.com"
```

---

## Testing Best Practices

### 1. Test Organization

```
tests/
├── unit/
│   ├── test_services.py
│   ├── test_repositories.py
│   └── test_utils.py
├── integration/
│   ├── test_database.py
│   ├── test_storage.py
│   └── test_api.py
├── e2e/
│   └── test_workflows.py
├── conftest.py (shared fixtures)
└── __init__.py
```

### 2. Naming Conventions

```python
# Good test names
def test_create_user_with_valid_data():
    """Test that users can be created with valid data."""
    pass

def test_create_user_fails_with_duplicate_email():
    """Test that creating user with duplicate email fails."""
    pass

def test_get_user_returns_none_for_invalid_id():
    """Test that getting user with invalid ID returns None."""
    pass

# Bad test names
def test_user():
    pass

def test_1():
    pass
```

### 3. AAA Pattern (Arrange, Act, Assert)

```python
@pytest.mark.asyncio
async def test_user_service_create():
    # Arrange
    repo = InMemoryRepository()
    service = UserService(repo)
    email = "test@example.com"
    name = "Test User"

    # Act
    user = await service.create_user(email, name)

    # Assert
    assert user.id is not None
    assert user.email == email
    assert user.name == name
```

### 4. One Assertion Per Test (When Possible)

```python
# Good - focused tests
@pytest.mark.asyncio
async def test_user_has_id_after_creation():
    service = UserService(InMemoryRepository())
    user = await service.create_user("test@example.com", "Test")
    assert user.id is not None

@pytest.mark.asyncio
async def test_user_email_is_correct():
    service = UserService(InMemoryRepository())
    user = await service.create_user("test@example.com", "Test")
    assert user.email == "test@example.com"

# Also acceptable - related assertions
@pytest.mark.asyncio
async def test_user_creation():
    service = UserService(InMemoryRepository())
    user = await service.create_user("test@example.com", "Test")
    assert user.id is not None
    assert user.email == "test@example.com"
    assert user.name == "Test"
```

---

## Fixtures and Mocks

### Shared Fixtures

```python
# conftest.py
import pytest
from adapter_kit import InMemoryRepository, Container
from observability import StructuredLogger

@pytest.fixture
def logger():
    """Provide logger for tests."""
    return StructuredLogger("test")

@pytest.fixture
def repository():
    """Provide in-memory repository."""
    return InMemoryRepository()

@pytest.fixture
def container():
    """Provide DI container with test dependencies."""
    container = Container()
    container.register_instance(StructuredLogger, StructuredLogger("test"))
    container.register(InMemoryRepository, InMemoryRepository)
    return container
```

### Mocking External Services

```python
from unittest.mock import AsyncMock, MagicMock, patch

@pytest.mark.asyncio
async def test_send_welcome_email():
    """Test welcome email sending."""
    # Mock email service
    email_service = AsyncMock()
    email_service.send.return_value = True

    service = UserService(repository=InMemoryRepository(), email=email_service)

    user = await service.create_user("test@example.com", "Test")

    # Verify email was sent
    email_service.send.assert_called_once_with(
        to="test@example.com",
        subject="Welcome!",
        body=ANY
    )

@pytest.mark.asyncio
async def test_external_api_call():
    """Test external API integration."""
    with patch('httpx.AsyncClient.get') as mock_get:
        mock_response = MagicMock()
        mock_response.json.return_value = {"data": "test"}
        mock_get.return_value = mock_response

        result = await fetch_external_data()

        assert result["data"] == "test"
        mock_get.assert_called_once()
```

### Parametrized Tests

```python
@pytest.mark.parametrize("email,expected", [
    ("valid@example.com", True),
    ("also.valid+tag@example.co.uk", True),
    ("invalid", False),
    ("@example.com", False),
    ("user@", False),
])
def test_email_validation(email, expected):
    """Test email validation with various inputs."""
    assert validate_email(email) == expected

@pytest.mark.parametrize("age,expected", [
    (17, False),  # Too young
    (18, True),   # Minimum age
    (65, True),   # Valid
    (150, False), # Too old
])
def test_age_validation(age, expected):
    """Test age validation."""
    assert validate_age(age) == expected
```

---

## Coverage

### Measuring Coverage

```bash
# Install coverage tools
pip install pytest-cov

# Run with coverage
pytest --cov=app --cov-report=html --cov-report=term

# View HTML report
open htmlcov/index.html
```

### Coverage Configuration

```ini
# pytest.ini or pyproject.toml
[tool.pytest.ini_options]
addopts = """
    --cov=app
    --cov-report=html
    --cov-report=term-missing
    --cov-fail-under=80
"""
```

### Coverage Goals

- **Minimum:** 80% overall coverage
- **Target:** 90%+ coverage
- **Critical paths:** 100% coverage (authentication, payments, etc.)

### Ignoring Lines from Coverage

```python
def debug_function():  # pragma: no cover
    """Debug function not tested."""
    print("Debug info")

if TYPE_CHECKING:  # pragma: no cover
    from typing import TYPE_CHECKING
```

---

## CI/CD Integration

### GitHub Actions

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-asyncio pytest-cov

      - name: Run unit tests
        run: pytest tests/unit -v

      - name: Run integration tests
        env:
          NEXT_PUBLIC_SUPABASE_URL: ${{ secrets.SUPABASE_URL }}
          NEXT_PUBLIC_SUPABASE_ANON_KEY: ${{ secrets.SUPABASE_KEY }}
        run: pytest tests/integration -v

      - name: Check coverage
        run: pytest --cov=app --cov-fail-under=80

      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

### Pre-commit Hooks

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.0.0
    hooks:
      - id: black

  - repo: https://github.com/charliermarsh/ruff-pre-commit
    rev: v0.1.0
    hooks:
      - id: ruff

  - repo: local
    hooks:
      - id: pytest-unit
        name: pytest-unit
        entry: pytest tests/unit -v
        language: system
        pass_filenames: false
        always_run: true
```

---

## Summary

Effective testing with Pheno-SDK:

1. **Use in-memory implementations** for fast unit tests
2. **Test against interfaces** not implementations
3. **Organize tests** by type (unit/integration/e2e)
4. **Maintain high coverage** (80%+ minimum)
5. **Automate testing** in CI/CD pipeline
6. **Mock external dependencies** appropriately
7. **Write clear, focused tests** with good names

Happy testing! 🧪
