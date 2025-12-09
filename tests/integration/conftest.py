"""
Integration test fixtures.

Provides database session fixtures with all tables created.
"""

import os
import tempfile
from pathlib import Path

import pytest
import pytest_asyncio
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from tracertm.models.base import Base
# Import ALL models to ensure they're registered with Base.metadata
# This is critical - SQLAlchemy only creates tables for imported models
from tracertm.models.agent import Agent
from tracertm.models.agent_event import AgentEvent
from tracertm.models.agent_lock import AgentLock
from tracertm.models.event import Event
from tracertm.models.item import Item
from tracertm.models.link import Link
from tracertm.models.project import Project


# Mark every test in this directory as integration to keep layering explicit.
pytestmark = pytest.mark.integration


@pytest.fixture(scope="function")
def test_db():
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


@pytest.fixture(scope="function")
def sync_db_session(test_db):
    """Create a synchronous database session with all tables created."""
    SessionLocal = sessionmaker(bind=test_db)
    session = SessionLocal()

    yield session

    session.close()


@pytest.fixture(scope="function")
def initialized_db(sync_db_session):
    """Database session with sample project data."""
    from tracertm.models.project import Project
    from tracertm.models.item import Item

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
        status="todo"
    )
    item2 = Item(
        id="FEATURE-456",
        project_id="test-project",
        title="Test Feature",
        view="FEATURE",
        item_type="feature",
        status="in_progress"
    )
    sync_db_session.add(item1)
    sync_db_session.add(item2)
    sync_db_session.commit()

    yield sync_db_session


@pytest.fixture(scope="function")
def db_with_sample_data(sync_db_session):
    """Database with comprehensive sample projects, items, links, and events for testing."""
    from tracertm.models.project import Project
    from tracertm.models.item import Item
    from tracertm.models.link import Link
    from tracertm.models.event import Event

    # Create sample project
    project = Project(
        id="test-project",
        name="Test Project",
        description="Comprehensive test project with full data"
    )
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
            item_metadata={"priority": "high", "assignee": "alice"}
        ),
        Item(
            id="item-2",
            project_id="test-project",
            title="Login API Endpoint",
            view="API",
            item_type="api",
            status="todo",
            item_metadata={"method": "POST", "path": "/api/auth/login"}
        ),
        Item(
            id="item-3",
            project_id="test-project",
            title="Auth Database Schema",
            view="DATABASE",
            item_type="schema",
            status="done",
            item_metadata={"tables": ["users", "sessions"]}
        ),
        Item(
            id="item-4",
            project_id="test-project",
            title="Login Integration Tests",
            view="TEST",
            item_type="test",
            status="todo",
            item_metadata={"test_type": "integration"}
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
            link_type="implements"
        ),
        Link(
            id="link-2",
            project_id="test-project",
            source_item_id="item-1",
            target_item_id="item-3",
            link_type="depends_on"
        ),
        Link(
            id="link-3",
            project_id="test-project",
            source_item_id="item-4",
            target_item_id="item-2",
            link_type="tests"
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
            data={"title": "User Authentication Feature", "view": "FEATURE"}
        ),
        Event(
            project_id="test-project",
            event_type="item_updated",
            entity_type="item",
            entity_id="item-1",
            agent_id="test-agent",
            data={"field": "status", "old_value": "todo", "new_value": "in_progress"}
        ),
        Event(
            project_id="test-project",
            event_type="link_created",
            entity_type="link",
            entity_id="link-1",
            agent_id="test-agent",
            data={"source": "item-1", "target": "item-2", "link_type": "implements"}
        ),
    ]

    for event in events:
        sync_db_session.add(event)
    sync_db_session.commit()

    yield sync_db_session


# ============================================================
# ASYNC FIXTURES FOR ASYNC TESTS (Services Tests, etc.)
# ============================================================


@pytest_asyncio.fixture(scope="session")
async def async_test_db_engine():
    """Create async test database engine with SQLite."""
    db_url = "sqlite+aiosqlite:///:memory:"

    engine = create_async_engine(
        db_url,
        echo=False,
        future=True,
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
async def db_session(async_test_db_engine):
    """
    Create an async test database session for async tests.

    This fixture provides a clean async session for each test.
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


@pytest.fixture(scope="function", autouse=True)
def isolated_cli_environment(tmp_path, monkeypatch):
    """
    Isolate CLI tests from the repository's .trace/ directory.

    Changes the working directory to a temporary directory so that
    CLI commands don't find the repository's .trace/ directory.
    """
    # Change to temp directory to avoid finding repo's .trace/
    original_cwd = os.getcwd()
    os.chdir(tmp_path)

    yield tmp_path

    # Restore original directory
    os.chdir(original_cwd)
"""
Fix for API layer test isolation issues.
This conftest patch implements proper fixture cleanup and test isolation.
"""
import pytest
from unittest.mock import patch, MagicMock
import sqlite3
import tempfile
import os


@pytest.fixture(autouse=True)
def reset_mocks():
    """Reset all mock patches between tests to prevent state pollution."""
    yield
    # Clean up any dangling patches
    patch.stopall()


@pytest.fixture
def isolated_db_session():
    """Create an isolated database session that resets after each test."""
    # Create a fresh temporary database for each test
    temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
    db_path = temp_db.name
    temp_db.close()
    
    try:
        # Initialize database
        conn = sqlite3.connect(db_path)
        conn.execute("PRAGMA foreign_keys = ON")
        conn.close()
        yield db_path
    finally:
        # Clean up database file after test
        if os.path.exists(db_path):
            try:
                os.unlink(db_path)
            except:
                pass


@pytest.fixture
def mock_api_config():
    """Provide a fresh mock API configuration for each test."""
    with patch('tracertm.api.client.ApiConfig') as mock_config:
        config_instance = MagicMock()
        config_instance.base_url = "http://localhost:8000"
        config_instance.api_key = "test-key"
        config_instance.timeout = 10
        config_instance.max_retries = 3
        mock_config.return_value = config_instance
        yield mock_config


@pytest.fixture
def mock_http_client():
    """Provide a fresh mock HTTP client for each test."""
    with patch('tracertm.api.client.httpx.Client') as mock_client:
        client_instance = MagicMock()
        mock_client.return_value = client_instance
        yield mock_client


@pytest.fixture(scope="function")
def api_test_isolation():
    """Ensure complete isolation between API tests."""
    # Setup
    import sys
    # Clear any cached imports
    modules_to_clear = [k for k in sys.modules.keys() if 'tracertm.api' in k]
    original_modules = {k: sys.modules.pop(k) for k in modules_to_clear}
    
    yield
    
    # Teardown - restore original state
    for module_name, module in original_modules.items():
        sys.modules[module_name] = module
    
    # Clear any remaining patches
    patch.stopall()


# Marker for API tests that need special isolation handling
def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line(
        "markers", "api_isolated: mark test as needing API isolation"
    )
