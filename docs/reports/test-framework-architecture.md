# TraceRTM - Test Framework Architecture

**Author:** Murat (Test Architect)
**Date:** 2025-11-20
**Version:** 1.0
**Framework**: pytest + pytest-asyncio + pytest-cov

---

## Executive Summary

This document defines the production-ready test framework architecture for TraceRTM, a Python 3.12+ CLI tool with PostgreSQL backend. The framework uses **pytest** as the test runner with async support, coverage reporting, benchmarking, and property-based testing capabilities.

**Framework Stack:**
- **Test Runner**: pytest 8.0+
- **Async Support**: pytest-asyncio 0.23+
- **Coverage**: pytest-cov 4.0+ (80%+ target)
- **Benchmarking**: pytest-benchmark 4.0+ (performance tests)
- **Property Testing**: hypothesis 6.0+ (event sourcing validation)
- **Mocking**: pytest-mock 3.12+ (unit tests)
- **Database**: Docker PostgreSQL 16 (integration tests)
- **CLI Testing**: subprocess + pytest (E2E tests)

**Test Directory Structure:**
```
tests/
├── unit/                    # 60% of tests - Fast, no DB
│   ├── test_repositories/
│   ├── test_services/
│   ├── test_schemas/
│   └── test_utils/
├── integration/             # 30% of tests - Real DB
│   ├── test_database/
│   ├── test_concurrency/
│   ├── test_event_sourcing/
│   └── test_search/
├── e2e/                     # 10% of tests - Full CLI
│   ├── test_cli_workflows/
│   └── test_agent_coordination/
├── performance/             # Separate suite
│   ├── test_query_performance/
│   └── test_load_testing/
├── fixtures/
│   ├── conftest.py          # Shared fixtures
│   ├── factories.py         # Data factories
│   └── docker-compose.yml   # Test PostgreSQL
└── pytest.ini               # Configuration
```

---

## 1. Framework Configuration

### 1.1 pytest.ini

```ini
# pytest.ini - Main pytest configuration
[pytest]
# Test discovery
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*

# Async support
asyncio_mode = auto

# Coverage
addopts =
    --strict-markers
    --strict-config
    --cov=tracertm
    --cov-report=html:test-results/coverage
    --cov-report=term-missing
    --cov-report=xml
    --cov-fail-under=80
    -v
    --tb=short
    --maxfail=5

# Markers
markers =
    unit: Unit tests (fast, no DB)
    integration: Integration tests (real DB)
    e2e: End-to-end tests (full CLI)
    performance: Performance benchmarks
    slow: Slow tests (>1s)
    asyncio: Async tests

# Timeout
timeout = 300  # 5 minutes max per test

# Warnings
filterwarnings =
    error
    ignore::DeprecationWarning
    ignore::PendingDeprecationWarning
```

### 1.2 pyproject.toml (Test Dependencies)

```toml
# pyproject.toml - Test dependencies
[project.optional-dependencies]
dev = [
    # Test framework
    "pytest>=8.0",
    "pytest-asyncio>=0.23",
    "pytest-cov>=4.0",
    "pytest-mock>=3.12",
    "pytest-benchmark>=4.0",
    "pytest-timeout>=2.2",
    "pytest-xdist>=3.5",  # Parallel execution

    # Property testing
    "hypothesis>=6.0",

    # Database testing
    "pytest-postgresql>=5.0",
    "docker>=7.0",

    # Linting & formatting
    "ruff>=0.1",
    "mypy>=1.8",

    # Type stubs
    "types-PyYAML",
    "types-setuptools",
]
```

### 1.3 Docker Compose (Test Database)

```yaml
# tests/fixtures/docker-compose.yml
version: '3.8'

services:
  test-db:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: test
      POSTGRES_PASSWORD: test
      POSTGRES_DB: tracertm_test
    ports:
      - "5433:5432"  # Different port to avoid conflicts
    volumes:
      - test-db-data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U test"]


### 2.2 Project Fixtures

```python
# tests/fixtures/conftest.py (continued)
from uuid import UUID, uuid4
from tracertm.models import Project
from tracertm.repositories import ProjectRepository

@pytest.fixture
async def test_project(test_session):
    """Create test project."""
    repo = ProjectRepository(test_session)
    project = await repo.create(
        name=f"test-project-{uuid4().hex[:8]}",
        description="Test project for automated tests",
        config={}
    )
    return project

@pytest.fixture
async def test_project_with_items(test_session, test_project):
    """Create test project with 100 items."""
    from tests.fixtures.factories import ItemFactory

    items = []
    for i in range(100):
        item = await ItemFactory.create(
            session=test_session,
            project_id=test_project.id,
            type="task",
            title=f"Task {i}"
        )
        items.append(item)

    return test_project, items
```

### 2.3 CLI Fixtures

```python
# tests/fixtures/conftest.py (continued)
import subprocess
import tempfile
import os

@pytest.fixture
def cli_runner():
    """CLI test runner with isolated environment."""
    def run_cli(args, env=None):
        """Run CLI command and return result."""
        cmd = ["rtm"] + args
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            env={**os.environ, **(env or {})}
        )
        return result

    return run_cli

@pytest.fixture
def temp_config_dir():
    """Temporary config directory for CLI tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_dir = os.path.join(tmpdir, ".config", "tracertm")
        os.makedirs(config_dir, exist_ok=True)
        yield config_dir
```

---

## 3. Data Factories

### 3.1 Item Factory

```python
# tests/fixtures/factories.py
from uuid import UUID, uuid4
from datetime import datetime
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from tracertm.models import Item, Link, Event, Agent
from tracertm.schemas import ItemCreate, LinkCreate

class ItemFactory:
    """Factory for creating test items."""

    @staticmethod
    async def create(
        session: AsyncSession,
        project_id: UUID,
        type: str = "task",
        view: str = "FEATURE",
        title: Optional[str] = None,
        description: str = "",
        status: str = "todo",
        owner: Optional[str] = None,
        parent_id: Optional[UUID] = None,
        metadata: Optional[dict] = None,
        **kwargs
    ) -> Item:
        """Create a test item."""
        item = Item(
            id=uuid4(),
            project_id=project_id,
            type=type,
            view=view,
            title=title or f"{type}-{uuid4().hex[:8]}",
            description=description,
            status=status,
            owner=owner,
            parent_id=parent_id,
            metadata=metadata or {},
            progress=0.0,
            version=1,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            **kwargs
        )
        session.add(item)
        await session.commit()
        await session.refresh(item)
        return item

    @staticmethod
    async def create_hierarchy(
        session: AsyncSession,
        project_id: UUID,
        epic_count: int = 1,
        features_per_epic: int = 3,
        stories_per_feature: int = 5,
        tasks_per_story: int = 3
    ) -> dict:
        """Create a full hierarchy of items."""
        hierarchy = {"epics": [], "features": [], "stories": [], "tasks": []}

        for e in range(epic_count):
            epic = await ItemFactory.create(
                session, project_id, type="epic", view="FEATURE", title=f"Epic {e}"
            )
            hierarchy["epics"].append(epic)

            for f in range(features_per_epic):
                feature = await ItemFactory.create(
                    session, project_id, type="feature", view="FEATURE",
                    title=f"Feature {e}.{f}", parent_id=epic.id
                )
                hierarchy["features"].append(feature)

                for s in range(stories_per_feature):
                    story = await ItemFactory.create(
                        session, project_id, type="story", view="FEATURE",
                        title=f"Story {e}.{f}.{s}", parent_id=feature.id
                    )
                    hierarchy["stories"].append(story)

                    for t in range(tasks_per_story):
                        task = await ItemFactory.create(
                            session, project_id, type="task", view="FEATURE",
                            title=f"Task {e}.{f}.{s}.{t}", parent_id=story.id
                        )
                        hierarchy["tasks"].append(task)

        return hierarchy

class LinkFactory:
    """Factory for creating test links."""

    @staticmethod
    async def create(
        session: AsyncSession,
        project_id: UUID,
        source_item_id: UUID,
        target_item_id: UUID,
        link_type: str = "implements",
        metadata: Optional[dict] = None,
        **kwargs
    ) -> Link:
        """Create a test link."""
        link = Link(
            id=uuid4(),
            project_id=project_id,
            source_item_id=source_item_id,
            target_item_id=target_item_id,
            link_type=link_type,
            metadata=metadata or {},
            created_at=datetime.utcnow(),
            **kwargs
        )
        session.add(link)
        await session.commit()
        await session.refresh(link)
        return link

class EventFactory:
    """Factory for creating test events."""

    @staticmethod
    async def create(
        session: AsyncSession,
        project_id: UUID,
        item_id: Optional[UUID],
        event_type: str,
        event_data: dict,
        agent_id: str = "test-agent",
        **kwargs
    ) -> Event:
        """Create a test event."""
        event = Event(
            id=uuid4(),
            project_id=project_id,
            item_id=item_id,
            event_type=event_type,
            event_data=event_data,
            timestamp=datetime.utcnow(),
            agent_id=agent_id,
            **kwargs
        )
        session.add(event)
        await session.commit()
        await session.refresh(event)
        return event

class AgentFactory:
    """Factory for creating test agents."""

    @staticmethod
    async def create(
        session: AsyncSession,
        agent_id: Optional[str] = None,
        name: Optional[str] = None,
        type: str = "test",
        config: Optional[dict] = None,
        **kwargs
    ) -> Agent:
        """Create a test agent."""
        agent_id = agent_id or f"agent-{uuid4().hex[:8]}"
        agent = Agent(
            id=agent_id,
            name=name or f"Test Agent {agent_id}",
            type=type,
            config=config or {},
            created_at=datetime.utcnow(),
            last_active=datetime.utcnow(),
            **kwargs
        )
        session.add(agent)
        await session.commit()
        await session.refresh(agent)
        return agent
```

---

## 4. Test Examples

### 4.1 Unit Test Example

```python
# tests/unit/test_repositories/test_item_repository.py
import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4
from tracertm.repositories import ItemRepository
from tracertm.schemas import ItemCreate, ItemUpdate
from tracertm.exceptions import ConcurrencyError
from tracertm.models import Item

@pytest.mark.unit
@pytest.mark.asyncio
async def test_create_item_with_optimistic_locking():
    """Item created with version=1 for optimistic locking."""
    # Arrange
    mock_session = AsyncMock()
    repo = ItemRepository(mock_session)
    project_id = uuid4()

    item_data = ItemCreate(
        type="feature",
        view="FEATURE",
        title="User Authentication",
        description="Implement OAuth 2.0",
        status="todo"
    )

    # Act
    item = await repo.create(project_id=project_id, data=item_data)

    # Assert
    assert item.version == 1
    assert item.status == "todo"
    assert item.title == "User Authentication"
    mock_session.add.assert_called_once()
    mock_session.commit.assert_called_once()

@pytest.mark.unit
@pytest.mark.asyncio
async def test_update_item_version_conflict():
    """Update fails when version mismatch (optimistic lock)."""
    # Arrange
    mock_session = AsyncMock()
    repo = ItemRepository(mock_session)

    # Simulate item with version=2
    existing_item = Item(
        id=uuid4(),
        project_id=uuid4(),
        type="feature",
        view="FEATURE",
        title="Old Title",
        version=2
    )

    # Mock get_by_id to return existing item
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = existing_item
    mock_session.execute.return_value = mock_result

    # Act & Assert
    with pytest.raises(ConcurrencyError, match="modified by another agent"):
        await repo.update(
            item_id=existing_item.id,
            data=ItemUpdate(title="New Title"),
            expected_version=1  # Stale version
        )
```

### 4.2 Integration Test Example

```python
# tests/integration/test_concurrency/test_optimistic_locking.py
import pytest
import asyncio
from tests.fixtures.factories import ItemFactory
from tracertm.repositories import ItemRepository
from tracertm.schemas import ItemUpdate
from tracertm.exceptions import ConcurrencyError

@pytest.mark.integration
@pytest.mark.asyncio
async def test_concurrent_updates_different_items(test_session, test_project):
    """1000 agents updating different items should succeed."""
    # Arrange
    repo = ItemRepository(test_session)

    # Create 1000 items
    items = []
    for i in range(1000):
        item = await ItemFactory.create(
            session=test_session,
            project_id=test_project.id,
            type="task",
            title=f"Task {i}"
        )
        items.append(item)

    # Act - Spawn 1000 concurrent updates
    async def update_item(item):
        await repo.update(
            item_id=item.id,
            data=ItemUpdate(status="in_progress"),
            expected_version=item.version
        )

    import time
    start = time.time()
    await asyncio.gather(*[update_item(item) for item in items])
    duration = time.time() - start

    # Assert
    assert duration < 5.0  # Should complete in <5 seconds

    # Verify all items updated
    updated_items = await repo.get_by_view(test_project.id, "FEATURE")
    assert all(item.status == "in_progress" for item in updated_items)
```

### 4.3 E2E Test Example

```python
# tests/e2e/test_cli_workflows/test_project_init.py
import pytest
import json
import os

@pytest.mark.e2e
def test_project_initialization_workflow(cli_runner, temp_config_dir):
    """User can initialize project and create first item."""
    # Arrange
    env = {"TRACERTM_CONFIG_DIR": temp_config_dir}

    # Act - Initialize project
    result = cli_runner(["project", "init", "test-project"], env=env)

    # Assert
    assert result.returncode == 0
    assert "Project created" in result.stdout

    # Act - Create first item
    result = cli_runner(
        ["create", "epic", "User Authentication", "--format", "json"],
        env=env
    )

    # Assert
    assert result.returncode == 0
    item = json.loads(result.stdout)
    assert item["type"] == "epic"
    assert item["title"] == "User Authentication"
    assert item["status"] == "todo"
```

### 4.4 Performance Test Example

```python
# tests/performance/test_query_performance.py
import pytest
from tests.fixtures.factories import ItemFactory

@pytest.mark.performance
@pytest.mark.benchmark
def test_simple_query_performance(benchmark, test_session, test_project):
    """Simple item lookup should complete in <50ms."""
    # Arrange - Create 10K items
    import asyncio

    async def setup():
        items = []
        for i in range(10000):
            item = await ItemFactory.create(
                session=test_session,
                project_id=test_project.id,
                type="task",
                title=f"Task {i}"
            )
            items.append(item)
        return items[0].id  # Return first item ID

    test_item_id = asyncio.run(setup())

    # Act - Benchmark query
    async def query():
        from tracertm.repositories import ItemRepository
        repo = ItemRepository(test_session)
        return await repo.get_by_id(test_item_id)

    result = benchmark(asyncio.run, query())

    # Assert
    assert benchmark.stats.mean < 0.055  # 55ms max (10% tolerance)
    assert result is not None
```

---

## 5. Running Tests

### 5.1 Local Development

```bash
# Run all tests
pytest

# Run specific test levels
pytest tests/unit -m unit
pytest tests/integration -m integration
pytest tests/e2e -m e2e

# Run with coverage
pytest --cov=tracertm --cov-report=html

# Run performance tests
pytest tests/performance --benchmark-only

# Run in parallel (faster)
pytest -n auto  # Uses all CPU cores

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/unit/test_repositories/test_item_repository.py

# Run specific test function
pytest tests/unit/test_repositories/test_item_repository.py::test_create_item_with_optimistic_locking
```

### 5.2 CI/CD Integration

```bash
# CI command (strict mode)
pytest \
  --cov=tracertm \
  --cov-report=xml \
  --cov-fail-under=80 \
  --maxfail=1 \
  --tb=short \
  -v

# Performance regression check
pytest tests/performance \
  --benchmark-only \
  --benchmark-compare=baseline.json \
  --benchmark-compare-fail=mean:10%
```

---

## 6. Summary

**Framework Status:** ✅ **PRODUCTION-READY**

**Key Components:**
- ✅ pytest configuration (pytest.ini)
- ✅ Test dependencies (pyproject.toml)
- ✅ Docker PostgreSQL (docker-compose.yml)
- ✅ Shared fixtures (conftest.py)
- ✅ Data factories (factories.py)
- ✅ Test examples (unit, integration, E2E, performance)

**Next Steps:**
1. ✅ Test Design: COMPLETE
2. ✅ Test Framework: COMPLETE
3. ⏭️ Test Automation: Generate comprehensive test suite
4. ⏭️ Requirements Trace: Map FRs to tests
5. ⏭️ CI/CD Pipeline: Automate test execution

**Ready for:** Test automation generation (Workflow #4)

---

_This test framework architecture provides a production-ready foundation for TraceRTM testing. All patterns follow pytest best practices and support the 60/30/10 test distribution (unit/integration/E2E)._
```

---

## 2. Shared Fixtures (conftest.py)

### 2.1 Database Fixtures

```python
# tests/fixtures/conftest.py
import pytest
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import NullPool
from tracertm.models import Base
from tracertm.core.database import get_session

# Test database URL
TEST_DATABASE_URL = "postgresql+asyncpg://test:test@localhost:5433/tracertm_test"

@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def test_engine():
    """Create test database engine."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        poolclass=NullPool,  # No connection pooling for tests
        echo=False
    )

    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    # Drop all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()

@pytest.fixture
async def test_session(test_engine):
    """Create test database session with transaction rollback."""
    async_session = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )

    async with async_session() as session:
        async with session.begin():
            yield session
            # Rollback transaction after test
            await session.rollback()
```


