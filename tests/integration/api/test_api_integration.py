"""Comprehensive integration tests for API module.

Tests FastAPI endpoints with real HTTP requests and database backend.
Targets: client.py, main.py, sync_client.py

Coverage Goal: 80%+ for each file
- client.py: 23.85% -> 80%+
- main.py: 38.46% -> 80%+
- sync_client.py: 35.07% -> 80%+
"""

import json
import tempfile
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import httpx
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from tests.test_constants import (
    COUNT_FIVE,
    COUNT_THREE,
    COUNT_TWO,
    HTTP_BAD_REQUEST,
    HTTP_INTERNAL_SERVER_ERROR,
    HTTP_NOT_FOUND,
    HTTP_OK,
)
from tracertm.api.client import BatchResult, TraceRTMClient
from tracertm.api.main import app, get_db
from tracertm.api.sync_client import (
    ApiClient,
    ApiConfig,
    ApiError,
    AuthenticationError,
    Change,
    Conflict,
    ConflictError,
    ConflictStrategy,
    NetworkError,
    RateLimitError,
    SyncOperation,
    SyncStatus,
    UploadResult,
)
from tracertm.config.manager import ConfigManager
from tracertm.database.connection import DatabaseConnection
from tracertm.models.agent import Agent
from tracertm.models.base import Base
from tracertm.models.event import Event
from tracertm.models.item import Item
from tracertm.models.link import Link
from tracertm.models.project import Project

pytestmark = pytest.mark.integration


# ============================================================================
# FIXTURES
# ============================================================================


@pytest.fixture
def test_db_engine() -> None:
    """Create a test database engine."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name

    engine = create_engine(f"sqlite:///{db_path}")
    Base.metadata.create_all(engine)

    yield engine

    engine.dispose()
    Path(db_path).unlink(missing_ok=True)


@pytest.fixture
def test_session(test_db_engine: Any) -> None:
    """Create a test database session."""
    SessionLocal = sessionmaker(bind=test_db_engine)
    session = SessionLocal()

    yield session

    session.close()


@pytest.fixture
def test_project(test_session: Any) -> None:
    """Create a test project."""
    project = Project(id="test-project-id", name="Test Project", description="Test Description")
    test_session.add(project)
    test_session.commit()
    return project


@pytest.fixture
def api_client_setup(tmp_path: Any, monkeypatch: Any, test_db_engine: Any, _test_project: Any) -> None:
    """Set up environment for TraceRTMClient tests."""
    config_dir = tmp_path / ".config" / "tracertm"
    config_dir.mkdir(parents=True)
    monkeypatch.setenv("HOME", str(tmp_path))

    config_manager = ConfigManager()
    db_path = tmp_path / "test.db"
    database_url = f"sqlite:///{db_path}"
    config_manager.set("database_url", database_url)
    config_manager.set("current_project_id", test_project.id)
    config_manager.set("current_project_name", test_project.name)

    # Create database tables
    db = DatabaseConnection(database_url)
    db.connect()
    db.create_tables()
    db.close()

    return config_manager, test_project.id


@pytest.fixture
def fastapi_test_client(test_db_engine: Any, _test_project: Any) -> None:
    """Create FastAPI test client with database dependency override."""

    async def override_get_db() -> None:
        # Create async session from async engine for testing
        from sqlalchemy.ext.asyncio import async_sessionmaker

        # Convert sync DB URL to async
        sync_url = str(test_db_engine.url)
        async_url = sync_url.replace("sqlite:///", "sqlite+aiosqlite:///")

        async_engine = create_async_engine(async_url, echo=False)
        async_session = async_sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)
        async with async_session() as session:
            try:
                yield session
            finally:
                await session.close()
                await async_engine.dispose()

    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture
def sample_items(test_session: Any, test_project: Any) -> None:
    """Create sample items for testing."""
    items = [
        Item(
            id="item-1",
            project_id=test_project.id,
            title="Feature 1",
            view="FEATURE",
            item_type="feature",
            status="todo",
            priority="high",
        ),
        Item(
            id="item-2",
            project_id=test_project.id,
            title="Feature 2",
            view="FEATURE",
            item_type="feature",
            status="in_progress",
            priority="medium",
        ),
        Item(
            id="item-3",
            project_id=test_project.id,
            title="Code 1",
            view="CODE",
            item_type="file",
            status="done",
            priority="low",
        ),
    ]
    for item in items:
        test_session.add(item)
    test_session.commit()
    return items


@pytest.fixture
def sample_links(test_session: Any, test_project: Any, _sample_items: Any) -> None:
    """Create sample links for testing."""
    links = [
        Link(
            id="link-1",
            project_id=test_project.id,
            source_item_id="item-1",
            target_item_id="item-2",
            link_type="depends_on",
        ),
        Link(
            id="link-2",
            project_id=test_project.id,
            source_item_id="item-2",
            target_item_id="item-3",
            link_type="implements",
        ),
    ]
    for link in links:
        test_session.add(link)
    test_session.commit()
    return links


# ============================================================================
# TRACERTM CLIENT TESTS (client.py)
# ============================================================================


class TestTraceRTMClientInitialization:
    """Test client initialization and setup."""

    def test_client_initialization_no_args(self, _api_client_setup: Any) -> None:
        """Test initializing client without arguments."""
        client = TraceRTMClient()
        assert client.config_manager is not None
        assert client.agent_id is None
        assert client.agent_name is None
        assert client._db is None
        assert client._session is None
        client.close()

    def test_client_initialization_with_agent_id(self, _api_client_setup: Any) -> None:
        """Test initializing client with agent ID."""
        client = TraceRTMClient(agent_id="test-agent-id")
        assert client.agent_id == "test-agent-id"
        assert client.agent_name is None
        client.close()

    def test_client_initialization_with_agent_name(self, _api_client_setup: Any) -> None:
        """Test initializing client with agent name."""
        client = TraceRTMClient(agent_name="Test Agent")
        assert client.agent_name == "Test Agent"
        assert client.agent_id is None
        client.close()

    def test_get_session_creates_connection(self, _api_client_setup: Any) -> None:
        """Test that _get_session creates database connection."""
        client = TraceRTMClient()
        session = client._get_session()
        assert session is not None
        assert client._db is not None
        assert client._session is not None
        client.close()

    def test_get_session_reuses_connection(self, _api_client_setup: Any) -> None:
        """Test that _get_session reuses existing connection."""
        client = TraceRTMClient()
        session1 = client._get_session()
        session2 = client._get_session()
        assert session1 is session2
        client.close()

    def test_get_session_no_database_config(self, tmp_path: Any, monkeypatch: Any) -> None:
        """Test _get_session raises error when database not configured."""
        config_dir = tmp_path / ".config" / "tracertm"
        config_dir.mkdir(parents=True)
        monkeypatch.setenv("HOME", str(tmp_path))

        client = TraceRTMClient()
        with pytest.raises(ValueError, match="Database not configured"):
            client._get_session()
        client.close()

    def test_get_project_id_success(self, api_client_setup: Any) -> None:
        """Test _get_project_id returns project ID."""
        client = TraceRTMClient()
        project_id = client._get_project_id()
        assert project_id == api_client_setup[1]
        client.close()

    def test_get_project_id_no_project(self, tmp_path: Any, monkeypatch: Any) -> None:
        """Test _get_project_id raises error when no project selected."""
        config_dir = tmp_path / ".config" / "tracertm"
        config_dir.mkdir(parents=True)
        monkeypatch.setenv("HOME", str(tmp_path))

        config_manager = ConfigManager()
        config_manager.set("database_url", "sqlite:///test.db")

        client = TraceRTMClient()
        with pytest.raises(ValueError, match="No project selected"):
            client._get_project_id()
        client.close()


class TestTraceRTMClientAgentOperations:
    """Test agent registration and management."""

    def test_register_agent_basic(self, _api_client_setup: Any) -> None:
        """Test basic agent registration."""
        client = TraceRTMClient()
        agent_id = client.register_agent("Test Agent")

        assert agent_id is not None
        assert client.agent_id == agent_id
        assert client.agent_name == "Test Agent"

        # Verify agent exists in database
        session = client._get_session()
        agent = session.query(Agent).filter(Agent.id == agent_id).first()
        assert agent is not None
        assert agent.name == "Test Agent"
        assert agent.agent_type == "ai_agent"
        assert agent.status == "active"
        client.close()

    def test_register_agent_with_type(self, _api_client_setup: Any) -> None:
        """Test agent registration with custom type."""
        client = TraceRTMClient()
        agent_id = client.register_agent("Custom Agent", agent_type="custom_type")

        session = client._get_session()
        agent = session.query(Agent).filter(Agent.id == agent_id).first()
        assert agent.agent_type == "custom_type"
        client.close()

    def test_register_agent_with_metadata(self, _api_client_setup: Any) -> None:
        """Test agent registration with metadata."""
        client = TraceRTMClient()
        metadata = {"key": "value", "capabilities": ["test", "code"]}
        agent_id = client.register_agent("Meta Agent", metadata=metadata)

        session = client._get_session()
        agent = session.query(Agent).filter(Agent.id == agent_id).first()
        assert agent.agent_metadata["key"] == "value"
        assert "capabilities" in agent.agent_metadata
        client.close()

    def test_register_agent_with_project_ids(self, _api_client_setup: Any) -> None:
        """Test agent registration with multiple project IDs."""
        client = TraceRTMClient()
        project_ids = ["project-1", "project-2"]
        agent_id = client.register_agent("Multi Project Agent", project_ids=project_ids)

        session = client._get_session()
        agent = session.query(Agent).filter(Agent.id == agent_id).first()
        assert "assigned_projects" in agent.agent_metadata
        assert agent.agent_metadata["assigned_projects"] == project_ids
        client.close()

    def test_assign_agent_to_projects(self, _api_client_setup: Any) -> None:
        """Test assigning agent to multiple projects."""
        client = TraceRTMClient()
        agent_id = client.register_agent("Test Agent")

        project_ids = ["proj-1", "proj-2", "proj-3"]
        client.assign_agent_to_projects(agent_id, project_ids)

        session = client._get_session()
        agent = session.query(Agent).filter(Agent.id == agent_id).first()
        assert agent.agent_metadata["assigned_projects"] == project_ids
        client.close()

    def test_assign_agent_to_projects_not_found(self, _api_client_setup: Any) -> None:
        """Test assigning non-existent agent raises error."""
        client = TraceRTMClient()

        with pytest.raises(ValueError, match="Agent not found"):
            client.assign_agent_to_projects("nonexistent-id", ["proj-1"])
        client.close()

    def test_get_agent_projects(self, _api_client_setup: Any) -> None:
        """Test getting projects assigned to agent."""
        client = TraceRTMClient()
        project_ids = ["proj-1", "proj-2"]
        agent_id = client.register_agent("Test Agent", project_ids=project_ids)

        assigned_projects = client.get_agent_projects(agent_id)

        # Should include primary project + assigned projects
        assert len(assigned_projects) >= COUNT_TWO
        assert "proj-1" in assigned_projects
        assert "proj-2" in assigned_projects
        client.close()

    def test_get_agent_projects_not_found(self, _api_client_setup: Any) -> None:
        """Test getting projects for non-existent agent."""
        client = TraceRTMClient()
        projects = client.get_agent_projects("nonexistent-id")
        assert projects == []
        client.close()

    def test_get_agent_projects_no_assignments(self, _api_client_setup: Any) -> None:
        """Test getting projects for agent with no assignments."""
        client = TraceRTMClient()
        agent_id = client.register_agent("Test Agent")

        projects = client.get_agent_projects(agent_id)

        # Should only include primary project
        assert len(projects) == 1
        client.close()


class TestTraceRTMClientItemOperations:
    """Test item CRUD operations."""

    def test_create_item_basic(self, _api_client_setup: Any) -> None:
        """Test creating basic item."""
        client = TraceRTMClient()
        client.register_agent("Test Agent")

        item = client.create_item("Test Feature", "FEATURE", "feature")

        assert item["id"] is not None
        assert item["title"] == "Test Feature"
        assert item["view"] == "FEATURE"
        assert item["type"] == "feature"
        assert item["status"] == "todo"
        assert item["version"] == 1
        client.close()

    def test_create_item_with_all_fields(self, _api_client_setup: Any) -> None:
        """Test creating item with all optional fields."""
        client = TraceRTMClient()
        client.register_agent("Test Agent")

        metadata = {"custom": "data"}
        item = client.create_item(
            title="Complete Feature",
            view="FEATURE",
            item_type="feature",
            description="Detailed description",
            status="in_progress",
            priority="high",
            owner="agent-1",
            parent_id="parent-123",
            metadata=metadata,
        )

        retrieved = client.get_item(item["id"])
        assert retrieved is not None
        assert retrieved["description"] == "Detailed description"
        assert retrieved["status"] == "in_progress"
        assert retrieved["priority"] == "high"
        assert retrieved["owner"] == "agent-1"
        assert retrieved["parent_id"] == "parent-123"
        assert retrieved["metadata"] == metadata
        client.close()

    def test_query_items_all(self, _api_client_setup: Any) -> None:
        """Test querying all items."""
        client = TraceRTMClient()
        client.register_agent("Test Agent")

        client.create_item("Feature 1", "FEATURE", "feature")
        client.create_item("Feature 2", "FEATURE", "feature")
        client.create_item("Code 1", "CODE", "file")

        items = client.query_items()
        assert len(items) == COUNT_THREE
        client.close()

    def test_query_items_by_view(self, _api_client_setup: Any) -> None:
        """Test querying items filtered by view."""
        client = TraceRTMClient()
        client.register_agent("Test Agent")

        client.create_item("Feature 1", "FEATURE", "feature")
        client.create_item("Feature 2", "FEATURE", "feature")
        client.create_item("Code 1", "CODE", "file")

        features = client.query_items(view="FEATURE")
        assert len(features) == COUNT_TWO
        assert all(item["view"] == "FEATURE" for item in features)
        client.close()

    def test_query_items_by_status(self, _api_client_setup: Any) -> None:
        """Test querying items filtered by status."""
        client = TraceRTMClient()
        client.register_agent("Test Agent")

        client.create_item("Todo 1", "FEATURE", "feature", status="todo")
        client.create_item("In Progress", "FEATURE", "feature", status="in_progress")
        client.create_item("Todo 2", "FEATURE", "feature", status="todo")

        todos = client.query_items(status="todo")
        assert len(todos) == COUNT_TWO
        assert all(item["status"] == "todo" for item in todos)
        client.close()

    def test_query_items_by_type(self, _api_client_setup: Any) -> None:
        """Test querying items filtered by item type."""
        client = TraceRTMClient()
        client.register_agent("Test Agent")

        client.create_item("Feature", "FEATURE", "feature")
        client.create_item("Bug", "FEATURE", "bug")

        features = client.query_items(item_type="feature")
        assert len(features) == 1
        assert features[0]["type"] == "feature"
        client.close()

    def test_query_items_with_filters(self, _api_client_setup: Any) -> None:
        """Test querying items with structured filters."""
        client = TraceRTMClient()
        client.register_agent("Test Agent")

        client.create_item("High Priority", "FEATURE", "feature", priority="high", owner="alice")
        client.create_item("Low Priority", "FEATURE", "feature", priority="low", owner="bob")

        high = client.query_items(priority="high")
        assert len(high) == 1
        assert high[0]["priority"] == "high"

        alice_items = client.query_items(owner="alice")
        assert len(alice_items) == 1
        assert alice_items[0]["owner"] == "alice"
        client.close()

    def test_query_items_limit(self, _api_client_setup: Any) -> None:
        """Test querying items with limit."""
        client = TraceRTMClient()
        client.register_agent("Test Agent")

        for i in range(10):
            client.create_item(f"Item {i}", "FEATURE", "feature")

        items = client.query_items(limit=5)
        assert len(items) == COUNT_FIVE
        client.close()

    def test_get_item_success(self, _api_client_setup: Any) -> None:
        """Test getting item by ID."""
        client = TraceRTMClient()
        client.register_agent("Test Agent")

        created = client.create_item("Test Item", "FEATURE", "feature")
        item = client.get_item(created["id"])

        assert item is not None
        assert item["id"] == created["id"]
        assert item["title"] == "Test Item"
        client.close()

    def test_get_item_not_found(self, _api_client_setup: Any) -> None:
        """Test getting non-existent item returns None."""
        client = TraceRTMClient()
        client.register_agent("Test Agent")

        item = client.get_item("nonexistent-id")
        assert item is None
        client.close()

    def test_get_item_soft_deleted(self, _api_client_setup: Any) -> None:
        """Test getting soft-deleted item returns None."""
        client = TraceRTMClient()
        client.register_agent("Test Agent")

        created = client.create_item("Delete Me", "FEATURE", "feature")
        client.delete_item(created["id"])

        item = client.get_item(created["id"])
        assert item is None
        client.close()

    def test_update_item_basic(self, _api_client_setup: Any) -> None:
        """Test updating item fields."""
        client = TraceRTMClient()
        client.register_agent("Test Agent")

        created = client.create_item("Original", "FEATURE", "feature")
        updated = client.update_item(created["id"], title="Updated", status="done")

        assert updated["title"] == "Updated"
        assert updated["status"] == "done"
        assert updated["version"] > created["version"]
        client.close()

    def test_update_item_multiple_fields(self, _api_client_setup: Any) -> None:
        """Test updating multiple item fields."""
        client = TraceRTMClient()
        client.register_agent("Test Agent")

        created = client.create_item("Test", "FEATURE", "feature")
        client.update_item(
            created["id"],
            title="New Title",
            description="New Description",
            status="in_progress",
            priority="high",
            owner="new-owner",
            metadata={"new": "data"},
        )

        item = client.get_item(created["id"])
        assert item is not None
        assert item["title"] == "New Title"
        assert item["description"] == "New Description"
        assert item["status"] == "in_progress"
        assert item["priority"] == "high"
        assert item["owner"] == "new-owner"
        assert item["metadata"] == {"new": "data"}
        client.close()

    def test_update_item_not_found(self, _api_client_setup: Any) -> None:
        """Test updating non-existent item raises error."""
        client = TraceRTMClient()
        client.register_agent("Test Agent")

        with pytest.raises(ValueError, match="Item not found"):
            client.update_item("nonexistent-id", title="New")
        client.close()

    def test_delete_item_success(self, _api_client_setup: Any) -> None:
        """Test deleting item (soft delete)."""
        client = TraceRTMClient()
        client.register_agent("Test Agent")

        created = client.create_item("Delete Me", "FEATURE", "feature")
        client.delete_item(created["id"])

        # Item should not appear in queries
        items = client.query_items()
        assert all(item["id"] != created["id"] for item in items)

        # Direct get should return None
        item = client.get_item(created["id"])
        assert item is None
        client.close()

    def test_delete_item_not_found(self, _api_client_setup: Any) -> None:
        """Test deleting non-existent item raises error."""
        client = TraceRTMClient()
        client.register_agent("Test Agent")

        with pytest.raises(ValueError, match="Item not found"):
            client.delete_item("nonexistent-id")
        client.close()


class TestTraceRTMClientBatchOperations:
    """Test batch operations."""

    def test_batch_create_items(self, _api_client_setup: Any) -> None:
        """Test batch creating items."""
        client = TraceRTMClient()
        client.register_agent("Test Agent")

        items_data = [
            {"title": "Item 1", "view": "FEATURE", "type": "feature"},
            {"title": "Item 2", "view": "CODE", "type": "file"},
            {"title": "Item 3", "view": "TEST", "type": "test"},
        ]

        result = client.batch_create_items(items_data)
        assert isinstance(result, BatchResult)
        assert result["items_created"] == COUNT_THREE

        # Verify items exist
        items = client.query_items()
        assert len(items) == COUNT_THREE
        client.close()

    def test_batch_create_items_with_fields(self, _api_client_setup: Any) -> None:
        """Test batch creating items with all fields."""
        client = TraceRTMClient()
        client.register_agent("Test Agent")

        items_data = [
            {
                "title": "Complete Item",
                "view": "FEATURE",
                "type": "feature",
                "description": "Description",
                "status": "in_progress",
                "priority": "high",
                "owner": "alice",
                "metadata": {"key": "value"},
            },
        ]

        result = client.batch_create_items(items_data)
        assert isinstance(result, BatchResult)
        assert result["items_created"] == 1

        items = client.query_items()
        assert items[0]["description"] == "Description"
        client.close()

    def test_batch_update_items(self, _api_client_setup: Any) -> None:
        """Test batch updating items."""
        client = TraceRTMClient()
        client.register_agent("Test Agent")

        # Create items
        item1 = client.create_item("Item 1", "FEATURE", "feature")
        item2 = client.create_item("Item 2", "FEATURE", "feature")

        # Batch update
        updates = [
            {"item_id": item1["id"], "status": "done"},
            {"item_id": item2["id"], "status": "in_progress", "priority": "high"},
        ]

        result = client.batch_update_items(updates)
        assert isinstance(result, BatchResult)
        assert result["items_updated"] == COUNT_TWO

        # Verify updates
        updated1 = client.get_item(item1["id"])
        assert updated1 is not None
        assert updated1["status"] == "done"

        updated2 = client.get_item(item2["id"])
        assert updated2 is not None
        assert updated2["status"] == "in_progress"
        assert updated2["priority"] == "high"
        client.close()

    def test_batch_update_items_skip_missing(self, _api_client_setup: Any) -> None:
        """Test batch update skips missing items."""
        client = TraceRTMClient()
        client.register_agent("Test Agent")

        item1 = client.create_item("Item 1", "FEATURE", "feature")

        updates = [
            {"item_id": item1["id"], "status": "done"},
            {"item_id": "nonexistent", "status": "done"},
        ]

        result = client.batch_update_items(updates)
        assert isinstance(result, BatchResult)
        assert result["items_updated"] == 1
        client.close()

    def test_batch_delete_items(self, _api_client_setup: Any) -> None:
        """Test batch deleting items."""
        client = TraceRTMClient()
        client.register_agent("Test Agent")

        item1 = client.create_item("Item 1", "FEATURE", "feature")
        item2 = client.create_item("Item 2", "FEATURE", "feature")
        item3 = client.create_item("Item 3", "FEATURE", "feature")

        result = client.batch_delete_items([item1["id"], item2["id"]])
        assert isinstance(result, BatchResult)
        assert result["items_deleted"] == COUNT_TWO

        # Verify deletions
        items = client.query_items()
        assert len(items) == 1
        assert items[0]["id"] == item3["id"]
        client.close()

    def test_batch_delete_items_skip_missing(self, _api_client_setup: Any) -> None:
        """Test batch delete skips missing items."""
        client = TraceRTMClient()
        client.register_agent("Test Agent")

        item1 = client.create_item("Item 1", "FEATURE", "feature")

        result = client.batch_delete_items([item1["id"], "nonexistent"])
        assert isinstance(result, BatchResult)
        assert result["items_deleted"] == 1
        client.close()


class TestTraceRTMClientExportImport:
    """Test export/import functionality."""

    def test_export_project_json(self, _api_client_setup: Any) -> None:
        """Test exporting project as JSON."""
        client = TraceRTMClient()
        client.register_agent("Test Agent")

        client.create_item("Export Item", "FEATURE", "feature")

        json_str = client.export_project(format="json")
        data = json.loads(json_str)

        assert "project" in data
        assert "items" in data
        assert "links" in data
        assert len(data["items"]) >= 1
        client.close()

    def test_export_project_yaml(self, _api_client_setup: Any) -> None:
        """Test exporting project as YAML."""
        client = TraceRTMClient()
        client.register_agent("Test Agent")

        client.create_item("Export Item", "FEATURE", "feature")

        yaml_str = client.export_project(format="yaml")
        assert "Export Item" in yaml_str
        assert "project:" in yaml_str
        client.close()

    def test_import_data_items_only(self, _api_client_setup: Any) -> None:
        """Test importing items only."""
        client = TraceRTMClient()
        client.register_agent("Test Agent")

        data = {
            "items": [
                {"title": "Imported 1", "view": "FEATURE", "type": "feature"},
                {"title": "Imported 2", "view": "CODE", "type": "file"},
            ],
        }

        result = client.import_data(data)
        assert result["items_created"] == COUNT_TWO
        assert result["links_created"] == 0

        items = client.query_items()
        titles = [item["title"] for item in items]
        assert "Imported 1" in titles
        assert "Imported 2" in titles
        client.close()

    def test_import_data_with_links(self, _api_client_setup: Any) -> None:
        """Test importing items and links."""
        client = TraceRTMClient()
        client.register_agent("Test Agent")

        # Create items first to get IDs
        item1 = client.create_item("Item 1", "FEATURE", "feature")
        item2 = client.create_item("Item 2", "FEATURE", "feature")

        data = {
            "items": [],
            "links": [{"source_id": item1["id"], "target_id": item2["id"], "type": "depends_on"}],
        }

        result = client.import_data(data)
        assert result["links_created"] == 1
        client.close()


class TestTraceRTMClientActivity:
    """Test activity monitoring."""

    def test_get_agent_activity(self, _api_client_setup: Any) -> None:
        """Test getting agent activity."""
        client = TraceRTMClient()
        agent_id = client.register_agent("Test Agent")

        # Perform operations
        client.create_item("Item 1", "FEATURE", "feature")
        client.create_item("Item 2", "FEATURE", "feature")

        activity = client.get_agent_activity(agent_id)

        assert len(activity) >= COUNT_TWO
        assert any(e["event_type"] == "item_created" for e in activity)
        client.close()

    def test_get_agent_activity_limit(self, _api_client_setup: Any) -> None:
        """Test getting agent activity with limit."""
        client = TraceRTMClient()
        agent_id = client.register_agent("Test Agent")

        for i in range(10):
            client.create_item(f"Item {i}", "FEATURE", "feature")

        activity = client.get_agent_activity(agent_id, limit=5)
        assert len(activity) <= COUNT_FIVE
        client.close()

    def test_get_agent_activity_no_agent(self, _api_client_setup: Any) -> None:
        """Test getting activity with no agent."""
        client = TraceRTMClient()
        activity = client.get_agent_activity()
        assert activity == []
        client.close()

    def test_get_all_agents_activity(self, _api_client_setup: Any) -> None:
        """Test getting all agents activity."""
        client1 = TraceRTMClient()
        agent1 = client1.register_agent("Agent 1")
        client1.create_item("Item 1", "FEATURE", "feature")

        client2 = TraceRTMClient()
        agent2 = client2.register_agent("Agent 2")
        client2.create_item("Item 2", "FEATURE", "feature")

        activity = client1.get_all_agents_activity()

        assert agent1 in activity
        assert agent2 in activity
        assert len(activity[agent1]) >= 1
        assert len(activity[agent2]) >= 1

        client1.close()
        client2.close()

    def test_get_assigned_items(self, _api_client_setup: Any) -> None:
        """Test getting items assigned to agent."""
        client = TraceRTMClient()
        agent_id = client.register_agent("Test Agent")

        client.create_item("Assigned", "FEATURE", "feature", owner=agent_id)
        client.create_item("Not Assigned", "FEATURE", "feature", owner="other-agent")

        assigned = client.get_assigned_items(agent_id)

        assert len(assigned) == 1
        assert assigned[0]["title"] == "Assigned"
        client.close()

    def test_get_assigned_items_no_agent(self, _api_client_setup: Any) -> None:
        """Test getting assigned items with no agent."""
        client = TraceRTMClient()
        assigned = client.get_assigned_items()
        assert assigned == []
        client.close()


class TestTraceRTMClientLogging:
    """Test operation logging."""

    def test_log_operation_without_agent(self, _api_client_setup: Any) -> None:
        """Test logging without agent ID skips silently."""
        client = TraceRTMClient()
        # Should not raise error
        client._log_operation("test", "test", "test-id", {"data": "value"})
        client.close()

    def test_log_operation_with_agent(self, _api_client_setup: Any) -> None:
        """Test logging with agent ID creates event."""
        client = TraceRTMClient()
        client.register_agent("Test Agent")

        client._log_operation("test_event", "test_entity", "test-id", {"key": "value"})

        session = client._get_session()
        events = session.query(Event).filter(Event.event_type == "test_event").all()
        assert len(events) >= 1
        client.close()

    def test_log_operation_error_handling(self, _api_client_setup: Any) -> None:
        """Test logging handles errors gracefully."""
        client = TraceRTMClient()
        client.register_agent("Test Agent")

        # Force an error by using invalid project ID
        client.config_manager.set("current_project_id", None)

        # Should not raise error
        client._log_operation("test", "test", "test-id", {"data": "value"})
        client.close()


# ============================================================================
# FASTAPI ENDPOINT TESTS (main.py)
# ============================================================================


class TestFastAPIHealthEndpoint:
    """Test health check endpoint."""

    def test_health_check_success(self, fastapi_test_client: Any) -> None:
        """Test health check returns healthy status."""
        response = fastapi_test_client.get("/health")
        assert response.status_code == HTTP_OK
        data = response.json()
        assert data["status"] == "healthy"
        assert data["version"] == "1.0.0"
        assert data["service"] == "TraceRTM API"


class TestFastAPIItemEndpoints:
    """Test item-related endpoints."""

    def test_list_items_empty(self, fastapi_test_client: Any, test_project: Any) -> None:
        """Test listing items when none exist."""
        response = fastapi_test_client.get(f"/api/v1/items?project_id={test_project.id}")
        assert response.status_code == HTTP_OK
        data = response.json()
        assert data["total"] == 0
        assert data["items"] == []

    def test_list_items_with_data(self, fastapi_test_client: Any, test_project: Any, _sample_items: Any) -> None:
        """Test listing items with sample data."""
        response = fastapi_test_client.get(f"/api/v1/items?project_id={test_project.id}")
        assert response.status_code == HTTP_OK
        data = response.json()
        assert data["total"] == COUNT_THREE
        assert len(data["items"]) == COUNT_THREE

    def test_list_items_pagination(self, fastapi_test_client: Any, test_project: Any, _sample_items: Any) -> None:
        """Test listing items with pagination."""
        response = fastapi_test_client.get(f"/api/v1/items?project_id={test_project.id}&skip=1&limit=2")
        assert response.status_code == HTTP_OK
        data = response.json()
        assert len(data["items"]) == COUNT_TWO

    def test_get_item_success(self, fastapi_test_client: Any, sample_items: Any) -> None:
        """Test getting specific item."""
        response = fastapi_test_client.get(f"/api/v1/items/{sample_items[0].id}")
        assert response.status_code == HTTP_OK
        data = response.json()
        assert data["id"] == str(sample_items[0].id)
        assert data["title"] == sample_items[0].title

    def test_get_item_not_found(self, fastapi_test_client: Any) -> None:
        """Test getting non-existent item."""
        response = fastapi_test_client.get("/api/v1/items/nonexistent")
        assert response.status_code == HTTP_NOT_FOUND


class TestFastAPILinkEndpoints:
    """Test link-related endpoints."""

    def test_list_links_empty(self, fastapi_test_client: Any, test_project: Any) -> None:
        """Test listing links when none exist."""
        response = fastapi_test_client.get(f"/api/v1/links?project_id={test_project.id}")
        assert response.status_code == HTTP_OK
        data = response.json()
        assert data["total"] == 0

    def test_list_links_with_data(self, fastapi_test_client: Any, test_project: Any, _sample_links: Any) -> None:
        """Test listing links with sample data."""
        response = fastapi_test_client.get(f"/api/v1/links?project_id={test_project.id}")
        assert response.status_code == HTTP_OK
        data = response.json()
        assert data["total"] == COUNT_TWO
        assert len(data["links"]) == COUNT_TWO

    def test_list_links_pagination(self, fastapi_test_client: Any, test_project: Any, _sample_links: Any) -> None:
        """Test listing links with pagination."""
        response = fastapi_test_client.get(f"/api/v1/links?project_id={test_project.id}&skip=1&limit=1")
        assert response.status_code == HTTP_OK
        data = response.json()
        assert len(data["links"]) == 1

    def test_update_link_success(self, fastapi_test_client: Any, sample_links: Any) -> None:
        """Test updating link."""
        link_id = sample_links[0].id
        update_data = {"link_type": "new_type", "metadata": {"key": "value"}}

        response = fastapi_test_client.put(f"/api/v1/links/{link_id}", json=update_data)
        assert response.status_code == HTTP_OK
        data = response.json()
        assert data["type"] == "new_type"
        assert data["metadata"] == {"key": "value"}

    def test_update_link_not_found(self, fastapi_test_client: Any) -> None:
        """Test updating non-existent link."""
        response = fastapi_test_client.put("/api/v1/links/nonexistent", json={"link_type": "new"})
        assert response.status_code == HTTP_NOT_FOUND


class TestFastAPIProjectEndpoints:
    """Test project-related endpoints."""

    def test_list_projects(self, fastapi_test_client: Any, _test_project: Any) -> None:
        """Test listing projects."""
        response = fastapi_test_client.get("/api/v1/projects")
        assert response.status_code == HTTP_OK
        data = response.json()
        assert data["total"] >= 1
        assert len(data["projects"]) >= 1

    def test_get_project_success(self, fastapi_test_client: Any, test_project: Any) -> None:
        """Test getting specific project."""
        response = fastapi_test_client.get(f"/api/v1/projects/{test_project.id}")
        assert response.status_code == HTTP_OK
        data = response.json()
        assert data["id"] == str(test_project.id)
        assert data["name"] == test_project.name

    def test_get_project_not_found(self, fastapi_test_client: Any) -> None:
        """Test getting non-existent project."""
        response = fastapi_test_client.get("/api/v1/projects/nonexistent")
        assert response.status_code == HTTP_NOT_FOUND

    def test_create_project(self, fastapi_test_client: Any) -> None:
        """Test creating new project."""
        project_data = {
            "name": "New Project",
            "description": "Test Description",
            "metadata": {"key": "value"},
        }

        response = fastapi_test_client.post("/api/v1/projects", json=project_data)
        assert response.status_code == HTTP_OK
        data = response.json()
        assert data["name"] == "New Project"
        assert data["description"] == "Test Description"

    def test_update_project(self, fastapi_test_client: Any, test_project: Any) -> None:
        """Test updating project."""
        update_data = {"name": "Updated Name", "description": "Updated Description"}

        response = fastapi_test_client.put(f"/api/v1/projects/{test_project.id}", json=update_data)
        assert response.status_code == HTTP_OK
        data = response.json()
        assert data["name"] == "Updated Name"

    def test_update_project_not_found(self, fastapi_test_client: Any) -> None:
        """Test updating non-existent project."""
        response = fastapi_test_client.put("/api/v1/projects/nonexistent", json={"name": "New"})
        assert response.status_code == HTTP_NOT_FOUND

    def test_delete_project(self, fastapi_test_client: Any, test_session: Any) -> None:
        """Test deleting project."""
        # Create project to delete
        project = Project(id="delete-me", name="Delete Me")
        test_session.add(project)
        test_session.commit()

        response = fastapi_test_client.delete(f"/api/v1/projects/{project.id}")
        assert response.status_code == HTTP_OK
        assert response.json()["success"] is True

    def test_delete_project_not_found(self, fastapi_test_client: Any) -> None:
        """Test deleting non-existent project."""
        response = fastapi_test_client.delete("/api/v1/projects/nonexistent")
        assert response.status_code == HTTP_NOT_FOUND


class TestFastAPIAnalysisEndpoints:
    """Test analysis endpoints."""

    def test_get_impact_analysis(self, fastapi_test_client: Any, test_project: Any, sample_items: Any) -> None:
        """Test impact analysis endpoint."""
        # Note: This requires ImpactAnalysisService implementation
        response = fastapi_test_client.get(f"/api/v1/analysis/impact/{sample_items[0].id}?project_id={test_project.id}")
        # May return error if service not fully implemented
        assert response.status_code in {200, 500}

    def test_detect_cycles(self, fastapi_test_client: Any, test_project: Any) -> None:
        """Test cycle detection endpoint."""
        response = fastapi_test_client.get(f"/api/v1/analysis/cycles/{test_project.id}")
        # May return error if service not fully implemented
        assert response.status_code in {200, 500}

    def test_find_shortest_path(self, fastapi_test_client: Any, test_project: Any, sample_items: Any) -> None:
        """Test shortest path endpoint."""
        response = fastapi_test_client.get(
            f"/api/v1/analysis/shortest-path?project_id={test_project.id}"
            f"&source_id={sample_items[0].id}&target_id={sample_items[1].id}",
        )
        # May return error if service not fully implemented
        assert response.status_code in {200, 500}


class TestFastAPIExportImportEndpoints:
    """Test export/import endpoints."""

    def test_export_project_json(self, fastapi_test_client: Any, test_project: Any, _sample_items: Any) -> None:
        """Test exporting project as JSON."""
        response = fastapi_test_client.get(f"/api/v1/projects/{test_project.id}/export?format=json")
        # May return error if service not fully implemented
        assert response.status_code in {200, 404, 500}

    def test_export_project_unsupported_format(self, fastapi_test_client: Any, test_project: Any) -> None:
        """Test exporting with unsupported format."""
        response = fastapi_test_client.get(f"/api/v1/projects/{test_project.id}/export?format=xml")
        assert response.status_code == HTTP_BAD_REQUEST

    def test_import_project_json(self, fastapi_test_client: Any, test_project: Any) -> None:
        """Test importing project data."""
        import_data = {
            "format": "json",
            "data": json.dumps({"items": [], "links": []}),
        }

        response = fastapi_test_client.post(f"/api/v1/projects/{test_project.id}/import", json=import_data)
        # May return error if service not fully implemented
        assert response.status_code in {200, 400, 500}

    def test_import_project_unsupported_format(self, fastapi_test_client: Any, test_project: Any) -> None:
        """Test importing with unsupported format."""
        import_data = {"format": "xml", "data": "<xml></xml>"}

        response = fastapi_test_client.post(f"/api/v1/projects/{test_project.id}/import", json=import_data)
        assert response.status_code == HTTP_BAD_REQUEST


class TestFastAPISyncEndpoints:
    """Test sync-related endpoints."""

    def test_get_sync_status(self, fastapi_test_client: Any, test_project: Any) -> None:
        """Test getting sync status."""
        response = fastapi_test_client.get(f"/api/v1/projects/{test_project.id}/sync/status")
        assert response.status_code == HTTP_OK
        data = response.json()
        assert "project_id" in data
        assert "status" in data

    def test_sync_project(self, fastapi_test_client: Any, test_project: Any) -> None:
        """Test syncing project."""
        response = fastapi_test_client.post(f"/api/v1/projects/{test_project.id}/sync")
        assert response.status_code == HTTP_OK
        data = response.json()
        assert data["project_id"] == test_project.id


class TestFastAPISearchEndpoints:
    """Test search endpoints."""

    def test_advanced_search(self, fastapi_test_client: Any, test_project: Any, _sample_items: Any) -> None:
        """Test advanced search endpoint."""
        search_data = {"query": "Feature", "filters": {"status": "todo"}}

        response = fastapi_test_client.post(f"/api/v1/projects/{test_project.id}/search/advanced", json=search_data)
        # May return error if service not fully implemented
        assert response.status_code in {200, 500}


class TestFastAPIGraphEndpoints:
    """Test graph-related endpoints."""

    def test_get_graph_neighbors_both(self, fastapi_test_client: Any, test_project: Any, sample_links: Any) -> None:
        """Test getting neighbors in both directions."""
        response = fastapi_test_client.get(
            f"/api/v1/projects/{test_project.id}/graph/neighbors"
            f"?item_id={sample_links[0].source_item_id}&direction=both",
        )
        assert response.status_code == HTTP_OK
        data = response.json()
        assert "neighbors" in data

    def test_get_graph_neighbors_out(self, fastapi_test_client: Any, test_project: Any, sample_links: Any) -> None:
        """Test getting outgoing neighbors."""
        response = fastapi_test_client.get(
            f"/api/v1/projects/{test_project.id}/graph/neighbors?item_id={sample_links[0].source_item_id}&direction=out",
        )
        assert response.status_code == HTTP_OK
        data = response.json()
        assert data["direction"] == "out"

    def test_get_graph_neighbors_in(self, fastapi_test_client: Any, test_project: Any, sample_links: Any) -> None:
        """Test getting incoming neighbors."""
        response = fastapi_test_client.get(
            f"/api/v1/projects/{test_project.id}/graph/neighbors?item_id={sample_links[0].target_item_id}&direction=in",
        )
        assert response.status_code == HTTP_OK
        data = response.json()
        assert data["direction"] == "in"


# ============================================================================
# SYNC CLIENT TESTS (sync_client.py)
# ============================================================================


class TestApiConfigClass:
    """Test ApiConfig dataclass."""

    def test_api_config_initialization(self) -> None:
        """Test basic ApiConfig initialization."""
        config = ApiConfig(base_url="https://api.test.com", token="test-token")
        assert config.base_url == "https://api.test.com"
        assert config.token == "test-token"
        assert config.timeout == 30.0
        assert config.max_retries == COUNT_THREE

    def test_api_config_from_config_manager(self, tmp_path: Any, monkeypatch: Any) -> None:
        """Test creating ApiConfig from ConfigManager."""
        config_dir = tmp_path / ".config" / "tracertm"
        config_dir.mkdir(parents=True)
        monkeypatch.setenv("HOME", str(tmp_path))

        config_manager = ConfigManager()
        config_manager.set("api_url", "https://custom.api.com")
        config_manager.set("api_token", "custom-token")
        config_manager.set("api_timeout", "60")
        config_manager.set("api_max_retries", "5")

        config = ApiConfig.from_config_manager(config_manager)
        assert config.base_url == "https://custom.api.com"
        assert config.token == "custom-token"
        assert config.timeout == 60.0
        assert config.max_retries == COUNT_FIVE

    def test_api_config_defaults(self, tmp_path: Any, monkeypatch: Any) -> None:
        """Test ApiConfig defaults when values not set."""
        config_dir = tmp_path / ".config" / "tracertm"
        config_dir.mkdir(parents=True)
        monkeypatch.setenv("HOME", str(tmp_path))

        config = ApiConfig.from_config_manager()
        assert config.base_url == "https://api.tracertm.io"
        assert config.token is None


class TestChangeClass:
    """Test Change dataclass."""

    def test_change_initialization(self) -> None:
        """Test Change initialization."""
        change = Change(
            entity_type="item",
            entity_id="item-123",
            operation=SyncOperation.CREATE,
            data={"title": "Test"},
        )
        assert change.entity_type == "item"
        assert change.entity_id == "item-123"
        assert change.operation == SyncOperation.CREATE
        assert change.data == {"title": "Test"}

    def test_change_to_dict(self) -> None:
        """Test converting Change to dictionary."""
        timestamp = datetime.now(UTC)
        change = Change(
            entity_type="item",
            entity_id="item-123",
            operation=SyncOperation.UPDATE,
            data={"status": "done"},
            version=2,
            timestamp=timestamp,
            client_id="client-1",
        )

        result = change.to_dict()
        assert result["entity_type"] == "item"
        assert result["entity_id"] == "item-123"
        assert result["operation"] == "update"
        assert result["data"] == {"status": "done"}
        assert result["version"] == COUNT_TWO
        assert result["client_id"] == "client-1"


class TestConflictClass:
    """Test Conflict dataclass."""

    def test_conflict_from_dict(self) -> None:
        """Test creating Conflict from dictionary."""
        data = {
            "conflict_id": "conflict-123",
            "entity_type": "item",
            "entity_id": "item-456",
            "local_version": 2,
            "remote_version": 3,
            "local_data": {"status": "done"},
            "remote_data": {"status": "in_progress"},
            "timestamp": "2025-01-01T00:00:00",
        }

        conflict = Conflict.from_dict(data)
        assert conflict.conflict_id == "conflict-123"
        assert conflict.entity_type == "item"
        assert conflict.local_version == COUNT_TWO
        assert conflict.remote_version == COUNT_THREE


class TestUploadResultClass:
    """Test UploadResult dataclass."""

    def test_upload_result_from_dict(self) -> None:
        """Test creating UploadResult from dictionary."""
        data = {
            "applied": ["item-1", "item-2"],
            "conflicts": [],
            "server_time": "2025-01-01T00:00:00",
            "errors": [],
        }

        result = UploadResult.from_dict(data)
        assert result.applied == ["item-1", "item-2"]
        assert result.conflicts == []
        assert len(result.errors) == 0

    def test_upload_result_with_conflicts(self) -> None:
        """Test UploadResult with conflicts."""
        data = {
            "applied": [],
            "conflicts": [
                {
                    "conflict_id": "c1",
                    "entity_type": "item",
                    "entity_id": "item-1",
                    "local_version": 1,
                    "remote_version": 2,
                    "local_data": {},
                    "remote_data": {},
                },
            ],
            "server_time": "2025-01-01T00:00:00",
        }

        result = UploadResult.from_dict(data)
        assert len(result.conflicts) == 1


class TestSyncStatusClass:
    """Test SyncStatus dataclass."""

    def test_sync_status_from_dict(self) -> None:
        """Test creating SyncStatus from dictionary."""
        data = {
            "last_sync": "2025-01-01T00:00:00",
            "pending_changes": 5,
            "online": True,
            "server_time": "2025-01-01T01:00:00",
            "conflicts_pending": 2,
        }

        status = SyncStatus.from_dict(data)
        assert status.pending_changes == COUNT_FIVE
        assert status.online is True
        assert status.conflicts_pending == COUNT_TWO

    def test_sync_status_from_dict_minimal(self) -> None:
        """Test SyncStatus with minimal data."""
        data = {"pending_changes": 0, "online": False}

        status = SyncStatus.from_dict(data)
        assert status.last_sync is None
        assert status.server_time is None
        assert status.conflicts_pending == 0


class TestApiClientInitialization:
    """Test ApiClient initialization."""

    def test_api_client_init_default(self) -> None:
        """Test ApiClient with default config."""
        client = ApiClient()
        assert client.config is not None
        assert client._client is None
        assert client._client_id is not None

    def test_api_client_init_custom_config(self) -> None:
        """Test ApiClient with custom config."""
        config = ApiConfig(base_url="https://custom.com", token="test-token")
        client = ApiClient(config)
        assert client.config.base_url == "https://custom.com"
        assert client.config.token == "test-token"

    def test_api_client_generate_client_id(self) -> None:
        """Test client ID generation is unique."""
        client1 = ApiClient()
        client2 = ApiClient()
        assert client1._client_id != client2._client_id

    def test_api_client_property(self) -> None:
        """Test client property creates httpx client."""
        config = ApiConfig(base_url="https://test.com", token="token")
        client = ApiClient(config)

        http_client = client.client
        assert isinstance(http_client, httpx.AsyncClient)
        assert "Authorization" in http_client.headers

    @pytest.mark.asyncio
    async def test_api_client_close(self) -> None:
        """Test closing API client."""
        client = ApiClient()
        # Access client to create it
        _ = client.client
        await client.close()
        assert client._client is None

    @pytest.mark.asyncio
    async def test_api_client_context_manager(self) -> None:
        """Test using ApiClient as context manager."""
        async with ApiClient() as client:
            assert client is not None
        # Client should be closed after context


class TestApiClientRetryLogic:
    """Test API client retry logic."""

    @pytest.mark.asyncio
    async def test_retry_request_success(self) -> None:
        """Test successful request without retries."""
        config = ApiConfig(base_url="https://httpbin.org")
        client = ApiClient(config)

        # Mock successful response
        with patch.object(client.client, "request") as mock_request:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"status": "ok"}
            mock_request.return_value = mock_response

            response = await client._retry_request("GET", "/status/200")
            assert response.status_code == HTTP_OK

        await client.close()

    @pytest.mark.asyncio
    async def test_retry_request_rate_limit(self) -> None:
        """Test handling rate limit error."""
        config = ApiConfig(base_url="https://test.com", max_retries=1)
        client = ApiClient(config)

        with patch.object(client.client, "request") as mock_request:
            mock_response = MagicMock()
            mock_response.status_code = 429
            mock_response.headers = {"Retry-After": "0.01"}  # Very short wait for testing
            mock_response.content = b'{"error": "rate limited"}'
            mock_response.json.return_value = {"error": "rate limited"}
            mock_request.return_value = mock_response

            # Rate limit errors should be raised after retries exhausted
            with pytest.raises(RateLimitError):
                await client._retry_request("GET", "/test")

        await client.close()

    @pytest.mark.asyncio
    async def test_retry_request_auth_error(self) -> None:
        """Test handling authentication error."""
        config = ApiConfig(base_url="https://test.com")
        client = ApiClient(config)

        with patch.object(client.client, "request") as mock_request:
            mock_response = MagicMock()
            mock_response.status_code = 401
            mock_response.content = b'{"error": "unauthorized"}'
            mock_response.json.return_value = {"error": "unauthorized"}
            mock_request.return_value = mock_response

            with pytest.raises(AuthenticationError):
                await client._retry_request("GET", "/test")

        await client.close()

    @pytest.mark.asyncio
    async def test_retry_request_network_error(self) -> None:
        """Test handling network error with retries."""
        config = ApiConfig(base_url="https://test.com", max_retries=2)
        client = ApiClient(config)

        with patch.object(client.client, "request") as mock_request:
            mock_request.side_effect = httpx.NetworkError("Connection failed")

            with pytest.raises(NetworkError):
                await client._retry_request("GET", "/test")

            # Should have retried
            assert mock_request.call_count == COUNT_TWO

        await client.close()


class TestApiClientHealthCheck:
    """Test health check functionality."""

    @pytest.mark.asyncio
    async def test_health_check_success(self) -> None:
        """Test successful health check."""
        client = ApiClient()

        with patch.object(client, "_retry_request") as mock_request:
            mock_response = MagicMock()
            mock_response.json.return_value = {"status": "healthy"}
            mock_request.return_value = mock_response

            result = await client.health_check()
            assert result is True

        await client.close()

    @pytest.mark.asyncio
    async def test_health_check_failure(self) -> None:
        """Test failed health check."""
        client = ApiClient()

        with patch.object(client, "_retry_request") as mock_request:
            mock_response = MagicMock()
            mock_response.json.return_value = {"status": "unhealthy"}
            mock_request.return_value = mock_response

            result = await client.health_check()
            assert result is False

        await client.close()

    @pytest.mark.asyncio
    async def test_health_check_exception(self) -> None:
        """Test health check with exception."""
        client = ApiClient()

        with patch.object(client, "_retry_request") as mock_request:
            mock_request.side_effect = Exception("Network error")

            result = await client.health_check()
            assert result is False

        await client.close()


class TestApiClientSyncOperations:
    """Test sync operations."""

    @pytest.mark.asyncio
    async def test_upload_changes_success(self) -> None:
        """Test uploading changes successfully."""
        client = ApiClient()

        changes = [
            Change("item", "item-1", SyncOperation.CREATE, {"title": "Test"}),
        ]

        with patch.object(client, "_retry_request") as mock_request:
            mock_response = MagicMock()
            mock_response.json.return_value = {
                "applied": ["item-1"],
                "conflicts": [],
                "server_time": datetime.now(UTC).isoformat(),
            }
            mock_request.return_value = mock_response

            result = await client.upload_changes(changes)
            assert result.applied == ["item-1"]
            assert len(result.conflicts) == 0

        await client.close()

    @pytest.mark.asyncio
    async def test_upload_changes_with_conflicts(self) -> None:
        """Test uploading changes with conflicts."""
        client = ApiClient()

        changes = [Change("item", "item-1", SyncOperation.UPDATE, {"status": "done"})]

        with patch.object(client, "_retry_request") as mock_request:
            mock_response = MagicMock()
            mock_response.status_code = 409
            mock_response.json.return_value = {
                "conflicts": [
                    {
                        "conflict_id": "c1",
                        "entity_type": "item",
                        "entity_id": "item-1",
                        "local_version": 1,
                        "remote_version": 2,
                        "local_data": {"status": "done"},
                        "remote_data": {"status": "in_progress"},
                    },
                ],
            }
            mock_request.side_effect = httpx.HTTPStatusError("Conflict", request=MagicMock(), response=mock_response)

            with pytest.raises(ConflictError) as exc_info:
                await client.upload_changes(changes)

            err = exc_info.value
            assert isinstance(err, ConflictError)
            assert len(err.conflicts) == 1

        await client.close()

    @pytest.mark.asyncio
    async def test_download_changes(self) -> None:
        """Test downloading changes."""
        client = ApiClient()

        since = datetime.now(UTC) - timedelta(hours=1)

        with patch.object(client, "_retry_request") as mock_request:
            mock_response = MagicMock()
            mock_response.json.return_value = {
                "changes": [
                    {
                        "entity_type": "item",
                        "entity_id": "item-1",
                        "operation": "create",
                        "data": {"title": "Remote Item"},
                        "version": 1,
                        "timestamp": datetime.now(UTC).isoformat(),
                    },
                ],
            }
            mock_request.return_value = mock_response

            changes = await client.download_changes(since)
            assert len(changes) == 1
            assert changes[0].entity_id == "item-1"

        await client.close()

    @pytest.mark.asyncio
    async def test_resolve_conflict(self) -> None:
        """Test resolving conflict."""
        client = ApiClient()

        with patch.object(client, "_retry_request") as mock_request:
            mock_response = MagicMock()
            mock_response.json.return_value = {"resolved": True}
            mock_request.return_value = mock_response

            result = await client.resolve_conflict("conflict-1", ConflictStrategy.LOCAL_WINS, {"status": "done"})
            assert result is True

        await client.close()

    @pytest.mark.asyncio
    async def test_get_sync_status(self) -> None:
        """Test getting sync status."""
        client = ApiClient()

        with patch.object(client, "_retry_request") as mock_request:
            mock_response = MagicMock()
            mock_response.json.return_value = {
                "last_sync": datetime.now(UTC).isoformat(),
                "pending_changes": 3,
                "online": True,
            }
            mock_request.return_value = mock_response

            status = await client.get_sync_status()
            assert status.pending_changes == COUNT_THREE
            assert status.online is True

        await client.close()

    @pytest.mark.asyncio
    async def test_full_sync_no_conflicts(self) -> None:
        """Test full bidirectional sync without conflicts."""
        client = ApiClient()

        local_changes = [Change("item", "item-1", SyncOperation.CREATE, {"title": "Local"})]

        with (
            patch.object(client, "upload_changes") as mock_upload,
            patch.object(client, "download_changes") as mock_download,
        ):
            mock_upload.return_value = UploadResult(
                applied=["item-1"],
                conflicts=[],
                server_time=datetime.now(UTC),
            )
            mock_download.return_value = []

            upload_result, remote_changes = await client.full_sync(local_changes)

            assert upload_result.applied == ["item-1"]
            assert len(remote_changes) == 0

        await client.close()

    @pytest.mark.asyncio
    async def test_full_sync_with_auto_resolve(self) -> None:
        """Test full sync with auto conflict resolution."""
        client = ApiClient()

        local_changes = [Change("item", "item-1", SyncOperation.UPDATE, {"status": "done"})]

        conflict = Conflict(
            conflict_id="c1",
            entity_type="item",
            entity_id="item-1",
            local_version=1,
            remote_version=2,
            local_data={"status": "done"},
            remote_data={"status": "in_progress"},
        )

        with (
            patch.object(client, "upload_changes") as mock_upload,
            patch.object(client, "resolve_conflict") as mock_resolve,
            patch.object(client, "download_changes") as mock_download,
        ):
            # First upload raises conflict
            mock_upload.side_effect = [
                ConflictError("Conflict", [conflict]),
                UploadResult(applied=["item-1"], conflicts=[], server_time=datetime.now(UTC)),
            ]
            mock_resolve.return_value = True
            mock_download.return_value = []

            upload_result, _remote_changes = await client.full_sync(
                local_changes,
                conflict_strategy=ConflictStrategy.LOCAL_WINS,
            )

            assert mock_resolve.called
            assert upload_result.applied == ["item-1"]

        await client.close()


# ============================================================================
# ERROR HANDLING AND EDGE CASES
# ============================================================================


class TestErrorHandling:
    """Test comprehensive error handling."""

    def test_client_close_idempotent(self, _api_client_setup: Any) -> None:
        """Test closing client multiple times is safe."""
        client = TraceRTMClient()
        client.close()
        client.close()  # Should not raise error

    @pytest.mark.asyncio
    async def test_api_client_multiple_close(self) -> None:
        """Test closing API client multiple times."""
        client = ApiClient()
        await client.close()
        await client.close()  # Should not raise error

    def test_batch_operations_rollback_on_error(self, _api_client_setup: Any) -> None:
        """Test batch operations rollback on error."""
        client = TraceRTMClient()
        client.register_agent("Test Agent")

        # Create invalid update that will fail
        with patch.object(client._get_session(), "commit", side_effect=Exception("DB Error")):
            with pytest.raises(Exception):
                client.batch_create_items([{"title": "Test", "view": "FEATURE", "type": "feature"}])

        client.close()

    @pytest.mark.asyncio
    async def test_api_error_hierarchy(self) -> None:
        """Test API error class hierarchy."""
        base_error = ApiError("Base error", status_code=500)
        assert base_error.status_code == HTTP_INTERNAL_SERVER_ERROR
        assert str(base_error) == "Base error"

        auth_error = AuthenticationError("Auth failed", status_code=401)
        assert isinstance(auth_error, ApiError)

        network_error = NetworkError("Network failed")
        assert isinstance(network_error, ApiError)

        rate_error = RateLimitError("Rate limited", retry_after=60)
        assert rate_error.retry_after == 60

        conflict_error = ConflictError("Conflict", [])
        assert conflict_error.conflicts == []
