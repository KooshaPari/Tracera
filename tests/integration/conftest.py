"""Integration test fixtures.

Provides database session fixtures with all tables created.
"""

import os
import tempfile
from pathlib import Path
from typing import Any

import pytest
import pytest_asyncio
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import Session, sessionmaker

# Import ALL models to ensure they're registered with Base.metadata
# This is critical - SQLAlchemy only creates tables for imported models
from tracertm.models.agent import Agent
from tracertm.models.agent_event import AgentEvent
from tracertm.models.agent_lock import AgentLock
from tracertm.models.base import Base

# Import blockchain models for version tracking and baselines
from tracertm.models.blockchain import (
    Baseline,
    BaselineItem,
    MerkleProofCache,
    SpecEmbedding,
    VersionBlock,
    VersionChainIndex,
)
from tracertm.models.event import Event
from tracertm.models.item import Item
from tracertm.models.link import Link
from tracertm.models.project import Project

# Mark every test in this directory as integration to keep layering explicit.
pytestmark = pytest.mark.integration


@pytest.fixture
def test_db() -> None:
    """Create a test database with all tables."""
    # Create temporary database file
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name

    # Create engine and tables
    engine = create_engine(f"sqlite:///{db_path}")
    Base.metadata.create_all(engine)

    yield engine

    # Cleanup
    engine.dispose()
    Path(db_path).unlink(missing_ok=True)


@pytest.fixture
def sync_db_session(test_db: Any) -> None:
    """Create a synchronous database session with all tables created."""
    SessionLocal = sessionmaker(bind=test_db)
    session = SessionLocal()

    yield session

    session.close()


@pytest.fixture
def initialized_db(sync_db_session: Any) -> None:
    """Database session with sample project data."""
    # Create test project
    project = Project(id="test-project", name="Test Project")
    sync_db_session.add(project)
    sync_db_session.commit()

    # Create test items
    item1 = Item(
        id="STORY-123",
        project_id="test-project",
        title="Test Story",
        view="STORY",
        item_type="story",
        status="todo",
    )
    item2 = Item(
        id="FEATURE-456",
        project_id="test-project",
        title="Test Feature",
        view="FEATURE",
        item_type="feature",
        status="in_progress",
    )
    sync_db_session.add(item1)
    sync_db_session.add(item2)
    sync_db_session.commit()

    return sync_db_session


@pytest.fixture
def db_with_sample_data(sync_db_session: Any) -> None:
    """Database with comprehensive sample projects, items, links, and events for testing."""
    # Create sample project
    project = Project(id="test-project", name="Test Project", description="Comprehensive test project with full data")
    sync_db_session.add(project)
    sync_db_session.commit()

    # Create sample items across different views
    items = [
        Item(
            id="item-1",
            project_id="test-project",
            title="User Authentication Feature",
            view="FEATURE",
            item_type="feature",
            status="in_progress",
            item_metadata={"priority": "high", "assignee": "alice"},
        ),
        Item(
            id="item-2",
            project_id="test-project",
            title="Login API Endpoint",
            view="API",
            item_type="api",
            status="todo",
            item_metadata={"method": "POST", "path": "/api/auth/login"},
        ),
        Item(
            id="item-3",
            project_id="test-project",
            title="Auth Database Schema",
            view="DATABASE",
            item_type="schema",
            status="done",
            item_metadata={"tables": ["users", "sessions"]},
        ),
        Item(
            id="item-4",
            project_id="test-project",
            title="Login Integration Tests",
            view="TEST",
            item_type="test",
            status="todo",
            item_metadata={"test_type": "integration"},
        ),
    ]

    for item in items:
        sync_db_session.add(item)
    sync_db_session.commit()

    # Create sample links between items
    links = [
        Link(
            id="link-1",
            project_id="test-project",
            source_item_id="item-1",
            target_item_id="item-2",
            link_type="implements",
        ),
        Link(
            id="link-2",
            project_id="test-project",
            source_item_id="item-1",
            target_item_id="item-3",
            link_type="depends_on",
        ),
        Link(
            id="link-3",
            project_id="test-project",
            source_item_id="item-4",
            target_item_id="item-2",
            link_type="tests",
        ),
    ]

    for link in links:
        sync_db_session.add(link)
    sync_db_session.commit()

    # Create sample events for history tracking
    events = [
        Event(
            project_id="test-project",
            event_type="item_created",
            entity_type="item",
            entity_id="item-1",
            agent_id="test-agent",
            data={"title": "User Authentication Feature", "view": "FEATURE"},
        ),
        Event(
            project_id="test-project",
            event_type="item_updated",
            entity_type="item",
            entity_id="item-1",
            agent_id="test-agent",
            data={"field": "status", "old_value": "todo", "new_value": "in_progress"},
        ),
        Event(
            project_id="test-project",
            event_type="link_created",
            entity_type="link",
            entity_id="link-1",
            agent_id="test-agent",
            data={"source": "item-1", "target": "item-2", "link_type": "implements"},
        ),
    ]

    for event in events:
        sync_db_session.add(event)
    sync_db_session.commit()

    return sync_db_session


# ============================================================
# ASYNC FIXTURES FOR ASYNC TESTS (Services Tests, etc.)
# ============================================================


@pytest_asyncio.fixture(scope="function")
async def async_test_db_engine() -> None:
    """Create async test database engine with SQLite - function scoped for isolation."""
    db_url = "sqlite+aiosqlite:///:memory:"

    engine = create_async_engine(
        db_url,
        echo=False,
        future=True,
        connect_args={"check_same_thread": False},
    )

    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    # Cleanup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def db_session(async_test_db_engine: Any) -> None:
    """Create an async test database session for async tests.

    This fixture provides a clean async session for each test.
    Scope is function-level to ensure complete isolation between tests.
    """
    async_session_maker = async_sessionmaker(
        async_test_db_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with async_session_maker() as session:
        try:
            yield session
        finally:
            # Always rollback to ensure test isolation
            await session.rollback()
            await session.close()


@pytest.fixture(autouse=True)
def isolated_cli_environment(tmp_path: Any, _monkeypatch: Any) -> None:
    """Isolate CLI tests from the repository's .trace/ directory.

    Changes the working directory to a temporary directory so that
    CLI commands don't find the repository's .trace/ directory.
    """
    # Change to temp directory to avoid finding repo's .trace/
    original_cwd = Path.cwd()
    os.chdir(tmp_path)

    yield tmp_path

    # Restore original directory
    os.chdir(original_cwd)
