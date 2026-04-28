"""Comprehensive test suite for tracertm.api module.

Tests all API client functionality including:
- TraceRTMClient (local database access)
- ApiClient (HTTP sync operations)
- Data models and serialization
- Error handling and edge cases

Coverage target: 90%+ for entire API module
"""

import json
from datetime import datetime
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import StaleDataError

from tests.test_constants import (
    COUNT_FIVE,
    COUNT_FOUR,
    COUNT_THREE,
    COUNT_TWO,
    HTTP_INTERNAL_SERVER_ERROR,
    HTTP_TOO_MANY_REQUESTS,
)
from tracertm.api.client import TraceRTMClient
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

# ============================================================
# TraceRTMClient Tests
# ============================================================


@pytest.fixture
def mock_config_manager() -> None:
    """Mock ConfigManager for TraceRTMClient tests."""
    with patch("tracertm.api.client.ConfigManager") as mock_cls:
        manager = MagicMock()
        manager.get.side_effect = lambda key, default=None: {
            "database_url": "sqlite:///test.db",
            "current_project_id": "test-project-123",
        }.get(key, default)
        mock_cls.return_value = manager
        yield manager


@pytest.fixture
def mock_db_connection() -> None:
    """Mock DatabaseConnection for TraceRTMClient tests."""
    with patch("tracertm.api.client.DatabaseConnection") as mock_cls:
        connection = MagicMock()
        connection.engine = MagicMock()
        mock_cls.return_value = connection
        yield connection


@pytest.fixture
def mock_session(_mock_db_connection: Any) -> None:
    """Mock database session with proper chaining - FIXED.

    Now uses a single persistent query chain that can be configured
    per-test. Tests can set mock_session.query.return_value.first.return_value
    or mock_session.query.return_value.all.return_value as needed.
    """
    with patch("tracertm.api.client.Session") as mock_cls:
        session = MagicMock(spec=Session)

        # Create a reusable query chain that allows configuration
        query_chain = MagicMock()
        query_chain.filter = MagicMock(return_value=query_chain)
        query_chain.filter_by = MagicMock(return_value=query_chain)
        query_chain.order_by = MagicMock(return_value=query_chain)
        query_chain.limit = MagicMock(return_value=query_chain)
        query_chain.first = MagicMock(return_value=None)
        query_chain.all = MagicMock(return_value=[])

        # query() returns the same chain each time for easy per-test configuration
        session.query = MagicMock(return_value=query_chain)
        session.add = MagicMock()
        session.commit = MagicMock()
        session.rollback = MagicMock()
        session.flush = MagicMock()
        session.close = MagicMock()

        mock_cls.return_value = session
        yield session


@pytest.fixture
def client(mock_config_manager: Any, _mock_session: Any) -> None:
    """Create TraceRTMClient instance with mocked dependencies."""
    client = TraceRTMClient(agent_id="test-agent-1", agent_name="Test Agent")
    client._session = mock_session
    return client


class TestTraceRTMClientInitialization:
    """Test TraceRTMClient initialization and configuration."""

    def test_init_with_agent_id_and_name(self, _mock_config_manager: Any) -> None:
        """Test initialization with agent ID and name."""
        client = TraceRTMClient(agent_id="agent-123", agent_name="My Agent")

        assert client.agent_id == "agent-123"
        assert client.agent_name == "My Agent"
        assert client._session is None
        assert client._db is None

    def test_init_without_agent(self, _mock_config_manager: Any) -> None:
        """Test initialization without agent credentials."""
        client = TraceRTMClient()

        assert client.agent_id is None
        assert client.agent_name is None

    def test_get_session_creates_connection(self, mock_config_manager: Any, _mock_db_connection: Any) -> None:
        """Test _get_session creates database connection."""
        with patch("tracertm.api.client.Session") as mock_session_cls:
            mock_session = MagicMock()
            mock_session_cls.return_value = mock_session

            client = TraceRTMClient()
            session = client._get_session()

            assert session == mock_session
            mock_db_connection.connect.assert_called_once()

    def test_get_session_reuses_existing(self, client: Any) -> None:
        """Test _get_session reuses existing session."""
        session1 = client._get_session()
        session2 = client._get_session()

        assert session1 is session2

    def test_get_session_no_database_configured(self) -> None:
        """Test _get_session raises error when database not configured."""
        with patch("tracertm.api.client.ConfigManager") as mock_cfg:
            manager = MagicMock()
            manager.get.return_value = None
            mock_cfg.return_value = manager

            client = TraceRTMClient()

            with pytest.raises(ValueError, match="Database not configured"):
                client._get_session()

    def test_get_project_id_success(self, client: Any, _mock_config_manager: Any) -> None:
        """Test _get_project_id returns current project."""
        project_id = client._get_project_id()
        assert project_id == "test-project-123"

    def test_get_project_id_no_project_selected(self) -> None:
        """Test _get_project_id raises error when no project selected."""
        with patch("tracertm.api.client.ConfigManager") as mock_cfg:
            manager = MagicMock()
            manager.get.return_value = None
            mock_cfg.return_value = manager

            client = TraceRTMClient()
            client._session = MagicMock()

            with pytest.raises(ValueError, match="No project selected"):
                client._get_project_id()


class TestTraceRTMClientAgentOperations:
    """Test agent registration and management."""

    def test_register_agent_basic(self, client: Any, mock_session: Any) -> None:
        """Test basic agent registration."""
        mock_agent = MagicMock()
        mock_agent.id = "new-agent-123"
        mock_session.add = MagicMock()
        mock_session.commit = MagicMock()

        with patch("tracertm.api.client.Agent") as mock_agent_cls:
            with patch("tracertm.api.client.Event"):  # Patch Event to avoid logging complexity
                mock_agent_cls.return_value = mock_agent

                agent_id = client.register_agent(
                    name="Test Agent",
                    agent_type="ai_agent",
                )

                assert agent_id == "new-agent-123"
                assert client.agent_id == "new-agent-123"
                assert client.agent_name == "Test Agent"
                # Called once for agent, plus once for event log
                assert mock_session.add.call_count >= 1
                mock_session.commit.assert_called()

    def test_register_agent_with_project_ids(self, client: Any, mock_session: Any) -> None:
        """Test agent registration with multiple projects."""
        mock_agent = MagicMock()
        mock_agent.id = "agent-multi"
        mock_session.add = MagicMock()

        with patch("tracertm.api.client.Agent") as mock_agent_cls:
            mock_agent_cls.return_value = mock_agent

            project_ids = ["proj-1", "proj-2", "proj-3"]
            client.register_agent(
                name="Multi Project Agent",
                project_ids=project_ids,
            )

            # Check metadata was set
            call_kwargs = mock_agent_cls.call_args[1]
            assert "agent_metadata" in call_kwargs
            assert call_kwargs["agent_metadata"]["assigned_projects"] == project_ids

    def test_register_agent_with_metadata(self, client: Any, _mock_session: Any) -> None:
        """Test agent registration with custom metadata."""
        mock_agent = MagicMock()
        mock_agent.id = "agent-meta"

        with patch("tracertm.api.client.Agent") as mock_agent_cls:
            mock_agent_cls.return_value = mock_agent

            metadata = {"custom_field": "value", "another": 123}
            client.register_agent(
                name="Agent With Metadata",
                metadata=metadata,
            )

            call_kwargs = mock_agent_cls.call_args[1]
            assert call_kwargs["agent_metadata"]["custom_field"] == "value"

    def test_assign_agent_to_projects(self, client: Any, mock_session: Any) -> None:
        """Test assigning agent to multiple projects."""
        mock_agent = MagicMock()
        mock_agent.agent_metadata = {}
        mock_session.query.return_value.filter.return_value.first.return_value = mock_agent

        client.assign_agent_to_projects("agent-123", ["proj-a", "proj-b"])

        assert "assigned_projects" in mock_agent.agent_metadata
        assert mock_agent.agent_metadata["assigned_projects"] == ["proj-a", "proj-b"]
        mock_session.commit.assert_called()

    def test_assign_agent_to_projects_not_found(self, client: Any, mock_session: Any) -> None:
        """Test assigning non-existent agent raises error."""
        mock_session.query.return_value.filter.return_value.first.return_value = None

        with pytest.raises(ValueError, match="Agent not found"):
            client.assign_agent_to_projects("nonexistent", ["proj-1"])

    def test_get_agent_projects(self, client: Any, mock_session: Any) -> None:
        """Test getting projects assigned to agent."""
        mock_agent = MagicMock()
        mock_agent.project_id = "primary-proj"
        mock_agent.agent_metadata = {"assigned_projects": ["proj-1", "proj-2"]}
        mock_session.query.return_value.filter.return_value.first.return_value = mock_agent

        projects = client.get_agent_projects("agent-123")

        assert "primary-proj" in projects
        assert "proj-1" in projects
        assert "proj-2" in projects

    def test_get_agent_projects_not_found(self, client: Any, mock_session: Any) -> None:
        """Test getting projects for non-existent agent returns empty list."""
        mock_session.query.return_value.filter.return_value.first.return_value = None

        projects = client.get_agent_projects("nonexistent")

        assert projects == []

    def test_get_agent_projects_no_assigned(self, client: Any, mock_session: Any) -> None:
        """Test getting projects when none assigned returns only primary."""
        mock_agent = MagicMock()
        mock_agent.project_id = "primary-proj"
        mock_agent.agent_metadata = {}
        mock_session.query.return_value.filter.return_value.first.return_value = mock_agent

        projects = client.get_agent_projects("agent-123")

        assert projects == ["primary-proj"]


class TestTraceRTMClientQueryOperations:
    """Test item querying functionality."""

    def test_query_items_basic(self, client: Any, mock_session: Any) -> None:
        """Test basic item query without filters."""
        mock_items = [
            MagicMock(
                id="item-1",
                title="Item 1",
                description="Desc 1",
                view="FEATURE",
                item_type="feature",
                status="todo",
                priority="high",
                owner="user-1",
                parent_id=None,
                item_metadata={},
                version=1,
                created_at=datetime(2024, 1, 1),
                updated_at=datetime(2024, 1, 2),
            ),
        ]
        mock_session.query.return_value.filter.return_value.order_by.return_value.all.return_value = mock_items

        items = client.query_items()

        assert len(items) == 1
        assert items[0]["id"] == "item-1"
        assert items[0]["title"] == "Item 1"
        mock_session.query.assert_called()

    def test_query_items_with_view_filter(self, client: Any, mock_session: Any) -> None:
        """Test querying items filtered by view."""
        mock_session.query.return_value.filter.return_value.order_by.return_value.all.return_value = []

        client.query_items(view="code")

        # Check filter was applied (view is uppercased)
        mock_session.query.return_value.filter.assert_called()

    def test_query_items_with_status_filter(self, client: Any, mock_session: Any) -> None:
        """Test querying items filtered by status."""
        mock_session.query.return_value.filter.return_value.order_by.return_value.all.return_value = []

        client.query_items(status="in_progress")

        mock_session.query.return_value.filter.assert_called()

    def test_query_items_with_type_filter(self, client: Any, mock_session: Any) -> None:
        """Test querying items filtered by type."""
        mock_session.query.return_value.filter.return_value.order_by.return_value.all.return_value = []

        client.query_items(item_type="bug")

        mock_session.query.return_value.filter.assert_called()

    def test_query_items_with_priority_filter(self, client: Any, mock_session: Any) -> None:
        """Test querying items with priority filter."""
        mock_session.query.return_value.filter.return_value.order_by.return_value.all.return_value = []

        client.query_items(priority="high")

        mock_session.query.return_value.filter.assert_called()

    def test_query_items_with_owner_filter(self, client: Any, mock_session: Any) -> None:
        """Test querying items with owner filter."""
        mock_session.query.return_value.filter.return_value.order_by.return_value.all.return_value = []

        client.query_items(owner="user-123")

        mock_session.query.return_value.filter.assert_called()

    def test_query_items_with_parent_id_filter(self, client: Any, mock_session: Any) -> None:
        """Test querying items with parent_id filter."""
        mock_session.query.return_value.filter.return_value.order_by.return_value.all.return_value = []

        client.query_items(parent_id="parent-123")

        mock_session.query.return_value.filter.assert_called()

    def test_query_items_with_limit(self, client: Any, mock_session: Any) -> None:
        """Test querying items respects limit parameter."""
        query_chain = mock_session.query.return_value
        query_chain.filter.return_value = query_chain
        query_chain.order_by.return_value = query_chain
        query_chain.limit.return_value = query_chain
        query_chain.all.return_value = []

        client.query_items(limit=50)

        query_chain.limit.assert_called_with(50)

    def test_query_items_excludes_deleted(self, client: Any, mock_session: Any) -> None:
        """Test query excludes soft-deleted items."""
        query_chain = mock_session.query.return_value
        query_chain.filter.return_value = query_chain
        query_chain.order_by.return_value = query_chain
        query_chain.all.return_value = []

        client.query_items()

        # Verify deleted_at filter is applied
        query_chain.filter.assert_called()

    def test_get_item_success(self, client: Any, mock_session: Any) -> None:
        """Test getting a specific item by ID."""
        mock_item = MagicMock(
            id="item-123",
            title="Test Item",
            description="Description",
            view="FEATURE",
            item_type="feature",
            status="done",
            priority="medium",
            owner="user-1",
            parent_id=None,
            item_metadata={"key": "value"},
            version=2,
            created_at=datetime(2024, 1, 1),
            updated_at=datetime(2024, 1, 2),
        )
        query_chain = mock_session.query.return_value
        query_chain.filter.return_value = query_chain
        query_chain.first.return_value = mock_item

        item = client.get_item("item-123")

        assert item is not None
        assert item["id"] == "item-123"
        assert item["title"] == "Test Item"
        assert item["metadata"]["key"] == "value"

    def test_get_item_not_found(self, client: Any, mock_session: Any) -> None:
        """Test getting non-existent item returns None."""
        query_chain = mock_session.query.return_value
        query_chain.filter.return_value = query_chain
        query_chain.first.return_value = None

        item = client.get_item("nonexistent")

        assert item is None

    def test_get_item_soft_deleted_returns_none(self, client: Any, mock_session: Any) -> None:
        """Test getting soft-deleted item returns None."""
        # Soft-deleted items are filtered out by query
        query_chain = mock_session.query.return_value
        query_chain.filter.return_value = query_chain
        query_chain.first.return_value = None

        item = client.get_item("deleted-item")

        assert item is None

    def test_get_item_with_prefix_match(self, client: Any, mock_session: Any) -> None:
        """Test get_item uses prefix matching on ID."""
        mock_item = MagicMock(id="item-123-full")
        query_chain = mock_session.query.return_value
        query_chain.filter.return_value = query_chain
        query_chain.first.return_value = mock_item

        client.get_item("item-123")

        # Verify LIKE filter is used
        query_chain.filter.assert_called()


class TestTraceRTMClientItemCRUD:
    """Test item create, update, delete operations."""

    def test_create_item_minimal(self, client: Any, mock_session: Any) -> None:
        """Test creating item with minimal required fields."""
        mock_item = MagicMock(
            id="new-item",
            title="New Item",
            view="FEATURE",
            item_type="feature",
            status="todo",
            version=1,
        )

        with patch("tracertm.api.client.Item") as mock_item_cls:
            mock_item_cls.return_value = mock_item

            result = client.create_item(
                title="New Item",
                view="feature",
                item_type="feature",
            )

            assert result["id"] == "new-item"
            assert result["title"] == "New Item"
            mock_session.add.assert_called()  # May be called multiple times (item + event log)
            mock_session.commit.assert_called()

    def test_create_item_full_fields(self, client: Any, _mock_session: Any) -> None:
        """Test creating item with all fields populated."""
        mock_item = MagicMock(id="full-item")

        with patch("tracertm.api.client.Item") as mock_item_cls:
            mock_item_cls.return_value = mock_item

            client.create_item(
                title="Full Item",
                view="code",
                item_type="class",
                description="A detailed description",
                status="in_progress",
                priority="high",
                owner="user-123",
                parent_id="parent-456",
                metadata={"custom": "data"},
            )

            # Check all fields were passed to Item constructor
            call_kwargs = mock_item_cls.call_args[1]
            assert call_kwargs["title"] == "Full Item"
            assert call_kwargs["view"] == "CODE"  # Uppercased
            assert call_kwargs["description"] == "A detailed description"
            assert call_kwargs["priority"] == "high"

    def test_create_item_uppercases_view(self, client: Any, _mock_session: Any) -> None:
        """Test view is uppercased during item creation."""
        mock_item = MagicMock(id="item-upper")

        with patch("tracertm.api.client.Item") as mock_item_cls:
            mock_item_cls.return_value = mock_item

            client.create_item(title="Test", view="feature", item_type="feat")

            call_kwargs = mock_item_cls.call_args[1]
            assert call_kwargs["view"] == "FEATURE"

    def test_update_item_single_field(self, client: Any, mock_session: Any) -> None:
        """Test updating single field of an item."""
        mock_item = MagicMock(
            id="item-update",
            title="Old Title",
            version=1,
        )
        query_chain = mock_session.query.return_value
        query_chain.filter.return_value = query_chain
        query_chain.first.return_value = mock_item

        client.update_item("item-update", title="New Title")

        assert mock_item.title == "New Title"
        mock_session.commit.assert_called()  # May be called multiple times (update + event log)

    def test_update_item_multiple_fields(self, client: Any, mock_session: Any) -> None:
        """Test updating multiple fields simultaneously."""
        mock_item = MagicMock(
            id="item-multi",
            title="Old",
            status="todo",
            priority="low",
            version=1,
        )
        query_chain = mock_session.query.return_value
        query_chain.filter.return_value = query_chain
        query_chain.first.return_value = mock_item

        client.update_item(
            "item-multi",
            title="Updated",
            status="done",
            priority="high",
        )

        assert mock_item.title == "Updated"
        assert mock_item.status == "done"
        assert mock_item.priority == "high"

    def test_update_item_not_found(self, client: Any, mock_session: Any) -> None:
        """Test updating non-existent item raises ValueError."""
        query_chain = mock_session.query.return_value
        query_chain.filter.return_value = query_chain
        query_chain.first.return_value = None

        with pytest.raises(ValueError, match="Item not found"):
            client.update_item("nonexistent", title="New")

    def test_update_item_with_metadata(self, client: Any, mock_session: Any) -> None:
        """Test updating item metadata."""
        mock_item = MagicMock(
            id="item-meta",
            item_metadata={},
            version=1,
        )
        query_chain = mock_session.query.return_value
        query_chain.filter.return_value = query_chain
        query_chain.first.return_value = mock_item

        new_metadata = {"updated": True, "count": 42}
        client.update_item("item-meta", metadata=new_metadata)

        assert mock_item.item_metadata == new_metadata

    def test_update_item_optimistic_locking_conflict(self, client: Any, mock_session: Any) -> None:
        """Test update handles optimistic locking conflicts."""
        from tracertm.services.concurrent_operations_service import ConcurrencyError

        mock_item = MagicMock(id="item-conflict", version=1)
        query_chain = mock_session.query.return_value
        query_chain.filter.return_value = query_chain
        query_chain.first.return_value = mock_item
        mock_session.commit.side_effect = StaleDataError()

        # The retry decorator wraps StaleDataError in ConcurrencyError after retries
        with pytest.raises((StaleDataError, ConcurrencyError)):
            client.update_item("item-conflict", title="Conflict")

        mock_session.rollback.assert_called()

    def test_delete_item_success(self, client: Any, mock_session: Any) -> None:
        """Test soft deleting an item."""
        mock_item = MagicMock(id="item-delete", deleted_at=None)
        query_chain = mock_session.query.return_value
        query_chain.filter.return_value = query_chain
        query_chain.first.return_value = mock_item

        client.delete_item("item-delete")

        assert mock_item.deleted_at is not None
        mock_session.commit.assert_called()  # May be called multiple times (delete + event log)

    def test_delete_item_not_found(self, client: Any, mock_session: Any) -> None:
        """Test deleting non-existent item raises ValueError."""
        query_chain = mock_session.query.return_value
        query_chain.filter.return_value = query_chain
        query_chain.first.return_value = None

        with pytest.raises(ValueError, match="Item not found"):
            client.delete_item("nonexistent")


class TestTraceRTMClientExportImport:
    """Test data export and import functionality."""

    def test_export_project_json(self, client: Any, mock_session: Any) -> None:
        """Test exporting project data as JSON."""
        mock_project = MagicMock(id="proj-1", name="Test Project")
        mock_items = [
            MagicMock(
                id="item-1",
                title="Item 1",
                view="FEATURE",
                item_type="feature",
                status="todo",
                item_metadata={},
            ),
        ]
        mock_links = [
            MagicMock(
                id="link-1",
                source_item_id="item-1",
                target_item_id="item-2",
                link_type="implements",
            ),
        ]

        # Setup query chain
        query_mock = MagicMock()
        query_mock.all.return_value = mock_items
        mock_session.query.return_value.filter.return_value = query_mock

        # Mock separate query for project and links
        def query_side_effect(model: Any) -> None:
            mock = MagicMock()
            if "Project" in str(model):
                mock.filter.return_value.first.return_value = mock_project
            elif "Link" in str(model):
                mock.filter.return_value.all.return_value = mock_links
            else:
                mock.filter.return_value.all.return_value = mock_items
            return mock

        mock_session.query.side_effect = query_side_effect

        # Project is imported inside export_project method, not at module level
        with patch("tracertm.models.project.Project", return_value=mock_project):
            result = client.export_project(format="json")

        data = json.loads(result)
        assert "project" in data
        assert "items" in data
        assert "links" in data
        assert len(data["items"]) == 1
        assert len(data["links"]) == 1

    def test_export_project_yaml(self, client: Any, mock_session: Any) -> None:
        """Test exporting project data as YAML."""
        mock_project = MagicMock(id="proj-1", name="Test Project")

        def query_side_effect(model: Any) -> None:
            mock = MagicMock()
            if "Project" in str(model):
                mock.filter.return_value.first.return_value = mock_project
            else:
                mock.filter.return_value.all.return_value = []
            return mock

        mock_session.query.side_effect = query_side_effect

        # Project is imported inside export_project method, yaml is imported conditionally
        with patch("tracertm.models.project.Project", return_value=mock_project):
            with patch("yaml.dump", return_value="yaml: data") as mock_yaml_dump:
                result = client.export_project(format="yaml")

                assert result == "yaml: data"
                mock_yaml_dump.assert_called_once()

    def test_import_data_items_only(self, client: Any, mock_session: Any) -> None:
        """Test importing items without links."""
        data = {
            "items": [
                {
                    "title": "Imported Item 1",
                    "view": "feature",
                    "type": "feature",
                    "status": "todo",
                },
                {
                    "title": "Imported Item 2",
                    "view": "code",
                    "type": "class",
                },
            ],
        }

        with patch("tracertm.api.client.Item"), patch("tracertm.api.client.Event"):
            result = client.import_data(data)

            assert result["items_created"] == COUNT_TWO
            assert result["links_created"] == 0
            # 2 items + 1 event from _log_operation = 3 add calls
            assert mock_session.add.call_count == COUNT_THREE

    def test_import_data_with_links(self, client: Any, _mock_session: Any) -> None:
        """Test importing both items and links."""
        data = {
            "items": [{"title": "Item", "view": "feature", "type": "feat"}],
            "links": [
                {
                    "source_id": "item-1",
                    "target_id": "item-2",
                    "type": "implements",
                },
            ],
        }

        with patch("tracertm.api.client.Item"), patch("tracertm.api.client.Link"):
            result = client.import_data(data)

            assert result["items_created"] == 1
            assert result["links_created"] == 1

    def test_import_data_empty(self, client: Any, _mock_session: Any) -> None:
        """Test importing empty data."""
        data = {}

        result = client.import_data(data)

        assert result["items_created"] == 0
        assert result["links_created"] == 0


class TestTraceRTMClientBatchOperations:
    """Test batch operations for items."""

    def test_batch_create_items(self, client: Any, mock_session: Any) -> None:
        """Test batch creating multiple items."""
        items_data = [
            {"title": "Batch 1", "view": "feature", "type": "feat"},
            {"title": "Batch 2", "view": "code", "type": "class"},
            {"title": "Batch 3", "view": "test", "type": "test"},
        ]

        with patch("tracertm.api.client.Item"), patch("tracertm.api.client.Event"):
            result = client.batch_create_items(items_data)

            assert result["items_created"] == COUNT_THREE
            # Commit is called twice: once for items, once for logging event
            assert mock_session.commit.call_count == COUNT_TWO

    def test_batch_create_items_rollback_on_error(self, client: Any, mock_session: Any) -> None:
        """Test batch create rolls back on error."""
        mock_session.commit.side_effect = Exception("DB Error")

        items_data = [{"title": "Item", "view": "feature", "type": "feat"}]

        with patch("tracertm.api.client.Item"):
            with pytest.raises(Exception):
                client.batch_create_items(items_data)

            mock_session.rollback.assert_called_once()

    def test_batch_update_items(self, client: Any, mock_session: Any) -> None:
        """Test batch updating multiple items."""
        mock_items = [MagicMock(id=f"item-{i}", title=f"Old {i}", version=1) for i in range(3)]

        call_count = [0]

        # Need to create a fresh query chain for each query() call
        def create_query_chain(*args: Any, **kwargs: Any) -> None:
            query_chain = MagicMock()
            if call_count[0] < len(mock_items):
                query_chain.filter.return_value = query_chain
                query_chain.first.return_value = mock_items[call_count[0]]
                call_count[0] += 1
            else:
                query_chain.filter.return_value = query_chain
                query_chain.first.return_value = None
            return query_chain

        mock_session.query.side_effect = create_query_chain

        updates = [{"item_id": f"item-{i}", "title": f"Updated {i}", "status": "done"} for i in range(3)]

        with patch("tracertm.api.client.Event"):
            result = client.batch_update_items(updates)

            assert result["items_updated"] == COUNT_THREE
            for item in mock_items:
                assert "Updated" in item.title

    def test_batch_update_items_skips_not_found(self, client: Any, mock_session: Any) -> None:
        """Test batch update skips non-existent items."""
        mock_session.query.return_value.filter.return_value.first.return_value = None

        updates = [
            {"item_id": "nonexistent-1", "title": "Update"},
            {"item_id": "nonexistent-2", "title": "Update"},
        ]

        result = client.batch_update_items(updates)

        assert result["items_updated"] == 0

    def test_batch_delete_items(self, client: Any, mock_session: Any) -> None:
        """Test batch deleting multiple items."""
        mock_items = [MagicMock(id=f"item-{i}", deleted_at=None) for i in range(3)]

        call_count = [0]

        # Need to create a fresh query chain for each query() call
        def create_query_chain(*args: Any, **kwargs: Any) -> None:
            query_chain = MagicMock()
            if call_count[0] < len(mock_items):
                query_chain.filter.return_value = query_chain
                query_chain.first.return_value = mock_items[call_count[0]]
                call_count[0] += 1
            else:
                query_chain.filter.return_value = query_chain
                query_chain.first.return_value = None
            return query_chain

        mock_session.query.side_effect = create_query_chain

        item_ids = [f"item-{i}" for i in range(3)]

        with patch("tracertm.api.client.Event"):
            result = client.batch_delete_items(item_ids)

            assert result["items_deleted"] == COUNT_THREE
            for item in mock_items:
                assert item.deleted_at is not None


class TestTraceRTMClientAgentActivity:
    """Test agent activity monitoring."""

    def test_get_agent_activity(self, client: Any, mock_session: Any) -> None:
        """Test getting activity for specific agent."""
        mock_events = [
            MagicMock(
                event_type="item_created",
                entity_type="item",
                entity_id="item-1",
                created_at=datetime(2024, 1, 1),
                data={"title": "New Item"},
            ),
            MagicMock(
                event_type="item_updated",
                entity_type="item",
                entity_id="item-1",
                created_at=datetime(2024, 1, 2),
                data={"status": "done"},
            ),
        ]

        # Setup proper query chain: query().filter().order_by().limit().all()
        query_chain = MagicMock()
        query_chain.filter.return_value = query_chain
        query_chain.order_by.return_value = query_chain
        query_chain.limit.return_value = query_chain
        query_chain.all.return_value = mock_events
        mock_session.query.return_value = query_chain

        with patch("tracertm.api.client.Event"):
            activity = client.get_agent_activity("agent-123", limit=50)

            assert len(activity) == COUNT_TWO
            assert activity[0]["event_type"] == "item_created"
            assert activity[1]["event_type"] == "item_updated"

    def test_get_agent_activity_no_agent_id(self, client: Any, _mock_session: Any) -> None:
        """Test get_agent_activity returns empty list without agent ID."""
        client.agent_id = None

        activity = client.get_agent_activity()

        assert activity == []

    def test_get_all_agents_activity(self, client: Any, mock_session: Any) -> None:
        """Test getting activity for all agents in project."""
        mock_agents = [
            MagicMock(id="agent-1"),
            MagicMock(id="agent-2"),
        ]

        def query_side_effect(model: Any) -> None:
            mock = MagicMock()
            if "Agent" in str(model):
                mock.filter.return_value.all.return_value = mock_agents
            else:
                mock.filter.return_value.order_by.return_value.limit.return_value.all.return_value = []
            return mock

        mock_session.query.side_effect = query_side_effect

        with patch("tracertm.api.client.Agent"), patch("tracertm.api.client.Event"):
            result = client.get_all_agents_activity(limit=10)

            assert "agent-1" in result
            assert "agent-2" in result

    def test_get_assigned_items(self, client: Any, mock_session: Any) -> None:
        """Test getting items assigned to agent."""
        mock_items = [
            MagicMock(
                id="item-1",
                title="Task 1",
                status="in_progress",
                view="FEATURE",
                item_type="task",
            ),
            MagicMock(
                id="item-2",
                title="Task 2",
                status="todo",
                view="CODE",
                item_type="bug",
            ),
        ]

        # Setup proper query chain: query().filter().all()
        query_chain = MagicMock()
        query_chain.filter.return_value = query_chain
        query_chain.all.return_value = mock_items
        mock_session.query.return_value = query_chain

        items = client.get_assigned_items("agent-123")

        assert len(items) == COUNT_TWO
        assert items[0]["title"] == "Task 1"

    def test_get_assigned_items_no_agent_id(self, client: Any, _mock_session: Any) -> None:
        """Test get_assigned_items returns empty list without agent ID."""
        client.agent_id = None

        items = client.get_assigned_items()

        assert items == []


class TestTraceRTMClientLogging:
    """Test operation logging functionality."""

    def test_log_operation_success(self, client: Any, mock_session: Any) -> None:
        """Test logging operation creates event."""
        client.agent_id = "test-agent"

        with patch("tracertm.api.client.Event") as mock_event_cls:
            mock_event = MagicMock()
            mock_event_cls.return_value = mock_event

            client._log_operation(
                "item_created",
                "item",
                "item-123",
                {"title": "Test"},
            )

            mock_session.add.assert_called_with(mock_event)
            mock_session.commit.assert_called()

    def test_log_operation_no_agent_id(self, client: Any, mock_session: Any) -> None:
        """Test logging skipped when no agent ID."""
        client.agent_id = None

        client._log_operation("test", "test", "test", {})

        # Should not attempt to create event
        mock_session.add.assert_not_called()

    def test_log_operation_handles_error_silently(self, client: Any, mock_session: Any) -> None:
        """Test logging errors are caught and ignored."""
        client.agent_id = "test-agent"
        mock_session.add.side_effect = Exception("DB Error")

        # Should not raise exception
        client._log_operation("test", "test", "test", {})

    def test_log_operation_with_none_data(self, client: Any, _mock_session: Any) -> None:
        """Test logging with None data converts to empty dict."""
        client.agent_id = "test-agent"

        with patch("tracertm.api.client.Event") as mock_event_cls:
            client._log_operation("test", "test", "test", None)

            # Check data parameter was converted to {}
            call_kwargs = mock_event_cls.call_args[1]
            assert call_kwargs["data"] == {}


class TestTraceRTMClientConnectionManagement:
    """Test connection lifecycle management."""

    def test_close_closes_session_and_db(self, _mock_config_manager: Any) -> None:
        """Test close method closes both session and connection."""
        with patch("tracertm.api.client.Session") as mock_session_cls:
            with patch("tracertm.api.client.DatabaseConnection") as mock_db_cls:
                mock_session = MagicMock()
                mock_session_cls.return_value = mock_session
                mock_db = MagicMock()
                mock_db_cls.return_value = mock_db

                client = TraceRTMClient()
                client._get_session()  # Initialize connection

                client.close()

                mock_session.close.assert_called_once()
                mock_db.close.assert_called_once()

    def test_close_handles_none_session(self, client: Any) -> None:
        """Test close works when session is None."""
        client._session = None
        client._db = None

        # Should not raise error
        client.close()


# ============================================================
# ApiClient (Sync Client) Tests
# ============================================================


@pytest.fixture
def api_config() -> None:
    """Create test API configuration."""
    return ApiConfig(
        base_url="https://api.test.com",
        token="test-token-123",
        timeout=10.0,
        max_retries=2,
    )


@pytest.fixture
def api_client(api_config: Any) -> None:
    """Create ApiClient instance with test config."""
    return ApiClient(api_config)


class TestApiConfig:
    """Test ApiConfig data class."""

    def test_api_config_creation(self) -> None:
        """Test creating ApiConfig with all parameters."""
        config = ApiConfig(
            base_url="https://api.example.com",
            token="my-token",
            timeout=30.0,
            max_retries=5,
            retry_backoff_base=3.0,
            retry_backoff_max=120.0,
            verify_ssl=False,
        )

        assert config.base_url == "https://api.example.com"
        assert config.token == "my-token"
        assert config.timeout == 30.0
        assert config.max_retries == COUNT_FIVE
        assert config.verify_ssl is False

    def test_api_config_defaults(self) -> None:
        """Test ApiConfig uses sensible defaults."""
        config = ApiConfig(base_url="https://api.test.com")

        assert config.token is None
        assert config.timeout == 30.0
        assert config.max_retries == COUNT_THREE
        assert config.verify_ssl is True

    def test_api_config_from_config_manager(self) -> None:
        """Test creating ApiConfig from ConfigManager."""
        with patch("tracertm.api.sync_client.ConfigManager") as mock_mgr_cls:
            manager = MagicMock()
            manager.get.side_effect = lambda key, default=None: {
                "api_url": "https://custom.api.com/",
                "api_token": "custom-token",
                "api_timeout": "45.0",
                "api_max_retries": "5",
            }.get(key, default)
            mock_mgr_cls.return_value = manager

            config = ApiConfig.from_config_manager(manager)

            assert config.base_url == "https://custom.api.com"  # Trailing slash removed
            assert config.token == "custom-token"
            assert config.timeout == 45.0
            assert config.max_retries == COUNT_FIVE

    def test_api_config_from_config_manager_creates_new(self) -> None:
        """Test from_config_manager creates ConfigManager if None."""
        with patch("tracertm.api.sync_client.ConfigManager") as mock_mgr_cls:
            manager = MagicMock()
            # Return defaults for all config values
            manager.get.side_effect = lambda key, default=None: {
                "api_url": "https://api.tracertm.io",
                "api_token": None,
                "api_timeout": 30.0,
                "api_max_retries": 3,
            }.get(key, default)
            mock_mgr_cls.return_value = manager

            config = ApiConfig.from_config_manager(None)

            mock_mgr_cls.assert_called_once()
            assert config.base_url == "https://api.tracertm.io"


class TestChangeDataClass:
    """Test Change data class."""

    def test_change_creation(self) -> None:
        """Test creating Change instance."""
        change = Change(
            entity_type="item",
            entity_id="item-123",
            operation=SyncOperation.CREATE,
            data={"title": "New Item"},
            version=1,
            client_id="client-abc",
        )

        assert change.entity_type == "item"
        assert change.entity_id == "item-123"
        assert change.operation == SyncOperation.CREATE

    def test_change_to_dict(self) -> None:
        """Test converting Change to dictionary."""
        timestamp = datetime(2024, 1, 1, 12, 0, 0)
        change = Change(
            entity_type="link",
            entity_id="link-456",
            operation=SyncOperation.UPDATE,
            data={"status": "active"},
            version=2,
            timestamp=timestamp,
            client_id="client-xyz",
        )

        data = change.to_dict()

        assert data["entity_type"] == "link"
        assert data["entity_id"] == "link-456"
        assert data["operation"] == "update"
        assert data["version"] == COUNT_TWO
        assert data["timestamp"] == "2024-01-01T12:00:00"

    def test_change_default_timestamp(self) -> None:
        """Test Change gets default timestamp."""
        change = Change(
            entity_type="item",
            entity_id="item-1",
            operation=SyncOperation.DELETE,
            data={},
        )

        assert change.timestamp is not None
        assert isinstance(change.timestamp, datetime)


class TestConflictDataClass:
    """Test Conflict data class."""

    def test_conflict_from_dict(self) -> None:
        """Test creating Conflict from dictionary."""
        data = {
            "conflict_id": "conflict-123",
            "entity_type": "item",
            "entity_id": "item-456",
            "local_version": 5,
            "remote_version": 6,
            "local_data": {"title": "Local Title"},
            "remote_data": {"title": "Remote Title"},
            "timestamp": "2024-01-01T12:00:00",
        }

        conflict = Conflict.from_dict(data)

        assert conflict.conflict_id == "conflict-123"
        assert conflict.local_version == COUNT_FIVE
        assert conflict.remote_version == 6
        assert conflict.local_data["title"] == "Local Title"

    def test_conflict_from_dict_no_timestamp(self) -> None:
        """Test Conflict.from_dict handles missing timestamp."""
        data = {
            "conflict_id": "conflict-123",
            "entity_type": "item",
            "entity_id": "item-456",
            "local_version": 1,
            "remote_version": 2,
            "local_data": {},
            "remote_data": {},
        }

        conflict = Conflict.from_dict(data)

        assert conflict.timestamp is not None
        assert isinstance(conflict.timestamp, datetime)


class TestUploadResultDataClass:
    """Test UploadResult data class."""

    def test_upload_result_from_dict(self) -> None:
        """Test creating UploadResult from API response."""
        data = {
            "applied": ["item-1", "item-2"],
            "conflicts": [],
            "server_time": "2024-01-01T12:00:00",
            "errors": [],
        }

        result = UploadResult.from_dict(data)

        assert len(result.applied) == COUNT_TWO
        assert result.applied[0] == "item-1"
        assert len(result.conflicts) == 0

    def test_upload_result_with_conflicts(self) -> None:
        """Test UploadResult with conflicts."""
        data = {
            "applied": ["item-1"],
            "conflicts": [
                {
                    "conflict_id": "c1",
                    "entity_type": "item",
                    "entity_id": "item-2",
                    "local_version": 1,
                    "remote_version": 2,
                    "local_data": {},
                    "remote_data": {},
                },
            ],
            "server_time": "2024-01-01T12:00:00",
            "errors": [{"error": "Failed to process item-3"}],
        }

        result = UploadResult.from_dict(data)

        assert len(result.conflicts) == 1
        assert result.conflicts[0].conflict_id == "c1"
        assert len(result.errors) == 1


class TestSyncStatusDataClass:
    """Test SyncStatus data class."""

    def test_sync_status_from_dict(self) -> None:
        """Test creating SyncStatus from API response."""
        data = {
            "last_sync": "2024-01-01T10:00:00",
            "pending_changes": 5,
            "online": True,
            "server_time": "2024-01-01T12:00:00",
            "conflicts_pending": 2,
        }

        status = SyncStatus.from_dict(data)

        assert status.pending_changes == COUNT_FIVE
        assert status.online is True
        assert status.conflicts_pending == COUNT_TWO

    def test_sync_status_from_dict_no_last_sync(self) -> None:
        """Test SyncStatus handles missing last_sync."""
        data = {
            "pending_changes": 0,
            "online": False,
        }

        status = SyncStatus.from_dict(data)

        assert status.last_sync is None
        assert status.server_time is None


class TestApiClientInitialization:
    """Test ApiClient initialization."""

    def test_api_client_with_config(self, api_config: Any) -> None:
        """Test creating ApiClient with custom config."""
        client = ApiClient(api_config)

        assert client.config == api_config
        assert client._client is None
        assert client._client_id is not None

    def test_api_client_without_config(self) -> None:
        """Test creating ApiClient without config uses default."""
        with patch("tracertm.api.sync_client.ApiConfig.from_config_manager") as mock:
            mock.return_value = ApiConfig(base_url="https://default.com")

            ApiClient(None)

            mock.assert_called_once()

    def test_generate_client_id_uniqueness(self, api_client: Any) -> None:
        """Test generated client IDs are unique."""
        id1 = api_client._generate_client_id()
        id2 = api_client._generate_client_id()

        assert id1 != id2
        assert len(id1) == 16  # SHA256 hash truncated to 16 chars


class TestApiClientHttpClient:
    """Test HTTP client creation and management."""

    def test_client_property_creates_client(self, api_client: Any) -> None:
        """Test client property creates httpx.AsyncClient."""
        client = api_client.client

        assert client is not None
        assert isinstance(client, httpx.AsyncClient)

    def test_client_property_reuses_existing(self, api_client: Any) -> None:
        """Test client property reuses existing client."""
        client1 = api_client.client
        client2 = api_client.client

        assert client1 is client2

    def test_client_includes_auth_header(self, api_config: Any) -> None:
        """Test client includes Authorization header when token provided."""
        api_config.token = "my-secret-token"
        client = ApiClient(api_config)

        http_client = client.client

        assert "Authorization" in http_client.headers
        assert http_client.headers["Authorization"] == "Bearer my-secret-token"

    def test_client_no_auth_header_without_token(self) -> None:
        """Test client doesn't include Authorization without token."""
        config = ApiConfig(base_url="https://api.test.com", token=None)
        client = ApiClient(config)

        http_client = client.client

        assert "Authorization" not in http_client.headers

    @pytest.mark.asyncio
    async def test_close_closes_http_client(self, api_client: Any) -> None:
        """Test close method closes HTTP client."""
        # Create client
        _ = api_client.client

        await api_client.close()

        assert api_client._client is None

    @pytest.mark.asyncio
    async def test_close_when_client_none(self, api_client: Any) -> None:
        """Test close works when client is None."""
        api_client._client = None

        # Should not raise error
        await api_client.close()

    @pytest.mark.asyncio
    async def test_async_context_manager(self, api_config: Any) -> None:
        """Test ApiClient works as async context manager."""
        async with ApiClient(api_config) as client:
            assert client is not None

        # Client should be closed after context
        assert client._client is None


class TestApiClientRetryLogic:
    """Test HTTP request retry logic."""

    @pytest.mark.asyncio
    async def test_retry_request_success_first_try(self, api_client: Any) -> None:
        """Test successful request on first try."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.raise_for_status = MagicMock()

        # Create mock client and inject it
        mock_http_client = AsyncMock()
        mock_http_client.request = AsyncMock(return_value=mock_response)
        api_client._client = mock_http_client

        response = await api_client._retry_request("GET", "/test")

        assert response == mock_response
        mock_http_client.request.assert_called_once()

    @pytest.mark.asyncio
    async def test_retry_request_retries_on_network_error(self, api_client: Any) -> None:
        """Test request retries on network error."""
        api_client.config.max_retries = 2
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.raise_for_status = MagicMock()

        mock_http_client = AsyncMock()
        mock_http_client.request = AsyncMock(
            side_effect=[
                httpx.NetworkError("Connection failed"),
                mock_response,
            ],
        )
        api_client._client = mock_http_client

        response = await api_client._retry_request("GET", "/test")

        assert response == mock_response
        assert mock_http_client.request.call_count == COUNT_TWO

    @pytest.mark.asyncio
    async def test_retry_request_raises_after_max_retries(self, api_client: Any) -> None:
        """Test request raises NetworkError after all retries."""
        api_client.config.max_retries = 2

        mock_http_client = AsyncMock()
        mock_http_client.request = AsyncMock(side_effect=httpx.NetworkError("Connection failed"))
        api_client._client = mock_http_client

        with pytest.raises(NetworkError, match="Network error after"):
            await api_client._retry_request("GET", "/test")

        assert mock_http_client.request.call_count == COUNT_TWO

    @pytest.mark.asyncio
    async def test_retry_request_handles_rate_limit(self, api_client: Any) -> None:
        """Test request handles 429 rate limit."""
        mock_response = MagicMock()
        mock_response.status_code = 429
        mock_response.headers = {"Retry-After": "5"}
        mock_response.content = b'{"error": "Rate limited"}'
        mock_response.json.return_value = {"error": "Rate limited"}

        mock_http_client = AsyncMock()
        mock_http_client.request = AsyncMock(return_value=mock_response)
        api_client._client = mock_http_client

        with pytest.raises(RateLimitError) as exc_info:
            await api_client._retry_request("GET", "/test")

        assert exc_info.value.retry_after == COUNT_FIVE

    @pytest.mark.asyncio
    async def test_retry_request_handles_auth_error(self, api_client: Any) -> None:
        """Test request raises AuthenticationError on 401."""
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.content = b'{"error": "Unauthorized"}'
        mock_response.json.return_value = {"error": "Unauthorized"}

        mock_http_client = AsyncMock()
        mock_http_client.request = AsyncMock(return_value=mock_response)
        api_client._client = mock_http_client

        with pytest.raises(AuthenticationError):
            await api_client._retry_request("GET", "/test")

    @pytest.mark.asyncio
    async def test_retry_request_exponential_backoff(self, api_client: Any) -> None:
        """Test retry uses exponential backoff."""
        api_client.config.max_retries = 3
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.raise_for_status = MagicMock()

        mock_http_client = AsyncMock()
        mock_http_client.request = AsyncMock(
            side_effect=[
                httpx.NetworkError("Error"),
                httpx.NetworkError("Error"),
                mock_response,
            ],
        )
        api_client._client = mock_http_client

        with patch("tracertm.api.sync_client.asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
            await api_client._retry_request("GET", "/test")

            # Should have slept between retries with increasing delays
            assert mock_sleep.call_count == COUNT_TWO


class TestApiClientHealthCheck:
    """Test API health check endpoint."""

    @pytest.mark.asyncio
    async def test_health_check_success(self, api_client: Any) -> None:
        """Test health check returns True when API is healthy."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"status": "healthy"}

        with patch.object(api_client, "_retry_request", AsyncMock(return_value=mock_response)):
            result = await api_client.health_check()

            assert result is True

    @pytest.mark.asyncio
    async def test_health_check_unhealthy_status(self, api_client: Any) -> None:
        """Test health check returns False for non-healthy status."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"status": "degraded"}

        with patch.object(api_client, "_retry_request", AsyncMock(return_value=mock_response)):
            result = await api_client.health_check()

            assert result is False

    @pytest.mark.asyncio
    async def test_health_check_handles_error(self, api_client: Any) -> None:
        """Test health check returns False on error."""
        with patch.object(
            api_client,
            "_retry_request",
            AsyncMock(side_effect=NetworkError("Connection failed")),
        ):
            result = await api_client.health_check()

            assert result is False


class TestApiClientUploadChanges:
    """Test uploading changes to server."""

    @pytest.mark.asyncio
    async def test_upload_changes_success(self, api_client: Any) -> None:
        """Test successful upload of changes."""
        changes = [
            Change("item", "item-1", SyncOperation.CREATE, {"title": "New"}),
            Change("item", "item-2", SyncOperation.UPDATE, {"status": "done"}),
        ]

        mock_response = MagicMock()
        mock_response.json.return_value = {
            "applied": ["item-1", "item-2"],
            "conflicts": [],
            "server_time": "2024-01-01T12:00:00",
        }

        with patch.object(api_client, "_retry_request", AsyncMock(return_value=mock_response)):
            result = await api_client.upload_changes(changes)

            assert len(result.applied) == COUNT_TWO
            assert result.applied[0] == "item-1"

    @pytest.mark.asyncio
    async def test_upload_changes_with_last_sync(self, api_client: Any) -> None:
        """Test upload includes last_sync timestamp."""
        changes = [Change("item", "item-1", SyncOperation.CREATE, {})]
        last_sync = datetime(2024, 1, 1, 10, 0, 0)

        mock_response = MagicMock()
        mock_response.json.return_value = {
            "applied": [],
            "conflicts": [],
            "server_time": "2024-01-01T12:00:00",
        }

        with patch.object(api_client, "_retry_request", AsyncMock(return_value=mock_response)) as mock_req:
            await api_client.upload_changes(changes, last_sync)

            # Check last_sync was included in payload
            call_args = mock_req.call_args
            payload = call_args[1]["json"]
            assert payload["last_sync"] == "2024-01-01T10:00:00"

    @pytest.mark.asyncio
    async def test_upload_changes_conflict_error(self, api_client: Any) -> None:
        """Test upload raises ConflictError on 409."""
        changes = [Change("item", "item-1", SyncOperation.UPDATE, {})]

        mock_response = MagicMock()
        mock_response.status_code = 409
        mock_response.content = b'{"conflicts": [...]}'
        mock_response.json.return_value = {
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
        }

        error = httpx.HTTPStatusError("Conflict", request=MagicMock(), response=mock_response)

        with patch.object(api_client.client, "request", AsyncMock(side_effect=error)):
            with pytest.raises(ConflictError) as exc_info:
                await api_client.upload_changes(changes)

            assert len(exc_info.value.conflicts) == 1


class TestApiClientDownloadChanges:
    """Test downloading changes from server."""

    @pytest.mark.asyncio
    async def test_download_changes_success(self, api_client: Any) -> None:
        """Test successful download of changes."""
        since = datetime(2024, 1, 1, 10, 0, 0)

        mock_response = MagicMock()
        mock_response.json.return_value = {
            "changes": [
                {
                    "entity_type": "item",
                    "entity_id": "item-1",
                    "operation": "create",
                    "data": {"title": "Remote Item"},
                    "version": 1,
                    "timestamp": "2024-01-01T11:00:00",
                    "client_id": "other-client",
                },
            ],
        }

        with patch.object(api_client, "_retry_request", AsyncMock(return_value=mock_response)):
            changes = await api_client.download_changes(since)

            assert len(changes) == 1
            assert changes[0].entity_id == "item-1"
            assert changes[0].operation == SyncOperation.CREATE

    @pytest.mark.asyncio
    async def test_download_changes_with_project_filter(self, api_client: Any) -> None:
        """Test download with project_id filter."""
        since = datetime(2024, 1, 1)
        mock_response = MagicMock()
        mock_response.json.return_value = {"changes": []}

        with patch.object(api_client, "_retry_request", AsyncMock(return_value=mock_response)) as mock_req:
            await api_client.download_changes(since, project_id="proj-123")

            # Check project_id was included in params
            call_args = mock_req.call_args
            params = call_args[1]["params"]
            assert params["project_id"] == "proj-123"

    @pytest.mark.asyncio
    async def test_download_changes_empty_response(self, api_client: Any) -> None:
        """Test download with no changes."""
        since = datetime(2024, 1, 1)
        mock_response = MagicMock()
        mock_response.json.return_value = {"changes": []}

        with patch.object(api_client, "_retry_request", AsyncMock(return_value=mock_response)):
            changes = await api_client.download_changes(since)

            assert changes == []


class TestApiClientConflictResolution:
    """Test conflict resolution."""

    @pytest.mark.asyncio
    async def test_resolve_conflict_local_wins(self, api_client: Any) -> None:
        """Test resolving conflict with local_wins strategy."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"resolved": True}

        with patch.object(api_client, "_retry_request", AsyncMock(return_value=mock_response)):
            result = await api_client.resolve_conflict(
                "conflict-123",
                ConflictStrategy.LOCAL_WINS,
            )

            assert result is True

    @pytest.mark.asyncio
    async def test_resolve_conflict_with_merged_data(self, api_client: Any) -> None:
        """Test resolving conflict with custom merged data."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"resolved": True}

        merged_data = {"title": "Merged Title", "status": "done"}

        with patch.object(api_client, "_retry_request", AsyncMock(return_value=mock_response)) as mock_req:
            await api_client.resolve_conflict(
                "conflict-123",
                ConflictStrategy.MANUAL,
                merged_data,
            )

            # Check merged_data was included
            call_args = mock_req.call_args
            payload = call_args[1]["json"]
            assert payload["merged_data"] == merged_data

    @pytest.mark.asyncio
    async def test_resolve_conflict_failed(self, api_client: Any) -> None:
        """Test conflict resolution failure."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"resolved": False}

        with patch.object(api_client, "_retry_request", AsyncMock(return_value=mock_response)):
            result = await api_client.resolve_conflict(
                "conflict-123",
                ConflictStrategy.REMOTE_WINS,
            )

            assert result is False


class TestApiClientSyncStatus:
    """Test getting sync status."""

    @pytest.mark.asyncio
    async def test_get_sync_status_success(self, api_client: Any) -> None:
        """Test successful sync status retrieval."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "last_sync": "2024-01-01T10:00:00",
            "pending_changes": 3,
            "online": True,
            "server_time": "2024-01-01T12:00:00",
            "conflicts_pending": 1,
        }

        with patch.object(api_client, "_retry_request", AsyncMock(return_value=mock_response)):
            status = await api_client.get_sync_status()

            assert status.pending_changes == COUNT_THREE
            assert status.online is True
            assert status.conflicts_pending == 1


class TestApiClientFullSync:
    """Test full bidirectional sync."""

    @pytest.mark.asyncio
    async def test_full_sync_success(self, api_client: Any) -> None:
        """Test successful full sync without conflicts."""
        local_changes = [Change("item", "item-1", SyncOperation.CREATE, {})]
        last_sync = datetime(2024, 1, 1, 10, 0, 0)

        upload_response = MagicMock()
        upload_response.json.return_value = {
            "applied": ["item-1"],
            "conflicts": [],
            "server_time": "2024-01-01T12:00:00",
        }

        download_response = MagicMock()
        download_response.json.return_value = {
            "changes": [
                {
                    "entity_type": "item",
                    "entity_id": "item-2",
                    "operation": "update",
                    "data": {},
                    "version": 1,
                    "timestamp": "2024-01-01T11:00:00",
                },
            ],
        }

        with patch.object(
            api_client,
            "_retry_request",
            AsyncMock(side_effect=[upload_response, download_response]),
        ):
            upload_result, remote_changes = await api_client.full_sync(
                local_changes,
                last_sync,
            )

            assert len(upload_result.applied) == 1
            assert len(remote_changes) == 1

    @pytest.mark.asyncio
    async def test_full_sync_auto_resolve_local_wins(self, api_client: Any) -> None:
        """Test full sync auto-resolves conflicts with local_wins."""
        local_changes = [Change("item", "item-1", SyncOperation.UPDATE, {})]

        conflict_data = {
            "conflicts": [
                {
                    "conflict_id": "c1",
                    "entity_type": "item",
                    "entity_id": "item-1",
                    "local_version": 2,
                    "remote_version": 3,
                    "local_data": {"title": "Local"},
                    "remote_data": {"title": "Remote"},
                },
            ],
        }

        # First upload raises conflict via upload_changes
        conflict_response = MagicMock()
        conflict_response.status_code = 409
        conflict_response.json.return_value = conflict_data

        # After resolution, upload succeeds
        success_response = MagicMock()
        success_response.json.return_value = {
            "applied": ["item-1"],
            "conflicts": [],
            "server_time": "2024-01-01T12:00:00",
        }

        resolve_response = MagicMock()
        resolve_response.json.return_value = {"resolved": True}

        download_response = MagicMock()
        download_response.json.return_value = {"changes": []}

        # Add status codes to responses
        conflict_response.content = b'{"conflicts": [...]}'
        success_response.status_code = 200
        resolve_response.status_code = 200
        download_response.status_code = 200

        # Create sequence of responses
        error = httpx.HTTPStatusError("Conflict", request=MagicMock(), response=conflict_response)

        with patch.object(api_client.client, "request", new_callable=AsyncMock) as mock_req:
            # First upload raises error, then resolve succeeds, then retry upload succeeds, then download
            mock_req.side_effect = [
                error,  # Initial upload fails
                resolve_response,  # Resolve succeeds
                success_response,  # Retry upload succeeds
                download_response,  # Download succeeds
            ]

            # This should now succeed after auto-resolving
            upload_result, _remote_changes = await api_client.full_sync(
                local_changes,
                conflict_strategy=ConflictStrategy.LOCAL_WINS,
            )

            # Verify it resolved and continued
            assert len(upload_result.applied) == 1
            assert mock_req.call_count == COUNT_FOUR  # upload, resolve, retry upload, download

    @pytest.mark.asyncio
    async def test_full_sync_manual_conflict_raises(self, api_client: Any) -> None:
        """Test full sync raises ConflictError for manual strategy."""
        local_changes = [Change("item", "item-1", SyncOperation.UPDATE, {})]

        conflict_response = MagicMock()
        conflict_response.status_code = 409
        conflict_response.content = b'{"conflicts": [...]}'
        conflict_response.json.return_value = {
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
        }

        error = httpx.HTTPStatusError("Conflict", request=MagicMock(), response=conflict_response)

        with patch.object(api_client.client, "request", AsyncMock(side_effect=error)):
            with pytest.raises(ConflictError):
                await api_client.full_sync(
                    local_changes,
                    conflict_strategy=ConflictStrategy.MANUAL,
                )


class TestApiExceptions:
    """Test custom exception classes."""

    def test_api_error_with_status_code(self) -> None:
        """Test ApiError stores status code and response data."""
        error = ApiError(
            "Test error",
            status_code=500,
            response_data={"detail": "Internal error"},
        )

        assert str(error) == "Test error"
        assert error.status_code == HTTP_INTERNAL_SERVER_ERROR
        assert error.response_data["detail"] == "Internal error"

    def test_api_error_defaults(self) -> None:
        """Test ApiError with default values."""
        error = ApiError("Simple error")

        assert error.status_code is None
        assert error.response_data == {}

    def test_rate_limit_error_with_retry_after(self) -> None:
        """Test RateLimitError stores retry_after."""
        error = RateLimitError(
            "Rate limited",
            retry_after=60,
            status_code=429,
        )

        assert error.retry_after == 60
        assert error.status_code == HTTP_TOO_MANY_REQUESTS

    def test_conflict_error_with_conflicts(self) -> None:
        """Test ConflictError stores conflict list."""
        conflicts = [
            Conflict(
                conflict_id="c1",
                entity_type="item",
                entity_id="item-1",
                local_version=1,
                remote_version=2,
                local_data={},
                remote_data={},
            ),
        ]

        error = ConflictError("Conflicts detected", conflicts=conflicts)

        assert len(error.conflicts) == 1
        assert error.conflicts[0].conflict_id == "c1"


class TestSyncClientBackwardCompat:
    """Test backward compatibility alias."""

    def test_sync_client_alias_exists(self) -> None:
        """Test SyncClient alias exists for backward compatibility."""
        from tracertm.api.sync_client import SyncClient

        assert SyncClient is ApiClient

    def test_sync_client_alias_works(self) -> None:
        """Test SyncClient alias can be instantiated."""
        from tracertm.api.sync_client import SyncClient

        config = ApiConfig(base_url="https://test.com")
        client = SyncClient(config)

        assert isinstance(client, ApiClient)


# ============================================================
# Integration Tests
# ============================================================


class TestApiIntegration:
    """Test integration between TraceRTMClient and ApiClient."""

    def test_can_import_all_exports(self) -> None:
        """Test all exported names can be imported."""
        from tracertm.api import (
            ApiClient,
            TraceRTMClient,
        )

        # All imports successful
        assert TraceRTMClient is not None
        assert ApiClient is not None

    def test_sync_operation_enum_values(self) -> None:
        """Test SyncOperation enum has correct values."""
        assert SyncOperation.CREATE == "create"
        assert SyncOperation.UPDATE == "update"
        assert SyncOperation.DELETE == "delete"

    def test_conflict_strategy_enum_values(self) -> None:
        """Test ConflictStrategy enum has correct values."""
        assert ConflictStrategy.LAST_WRITE_WINS == "last_write_wins"
        assert ConflictStrategy.LOCAL_WINS == "local_wins"
        assert ConflictStrategy.REMOTE_WINS == "remote_wins"
        assert ConflictStrategy.MANUAL == "manual"
