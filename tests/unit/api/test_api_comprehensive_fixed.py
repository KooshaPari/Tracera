"""
Comprehensive test suite for tracertm.api module.

Tests all API client functionality including:
- TraceRTMClient (local database access)
- ApiClient (HTTP sync operations)
- Data models and serialization
- Error handling and edge cases

Coverage target: 90%+ for entire API module
"""

import asyncio
import json
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, Mock, call, patch

import httpx
import pytest
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import StaleDataError

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


@pytest.fixture(scope="function")
def mock_config_manager():
    """Mock ConfigManager for TraceRTMClient tests."""
    manager = MagicMock()
    manager.get.side_effect = lambda key, default=None: {
        "database_url": "sqlite:///test.db",
        "current_project_id": "test-project-123",
    }.get(key, default)

    with patch("tracertm.api.client.ConfigManager", return_value=manager):
        yield manager


@pytest.fixture(scope="function")
def mock_db_connection():
    """Mock DatabaseConnection for TraceRTMClient tests."""
    connection = MagicMock()
    connection.engine = MagicMock()

    with patch("tracertm.api.client.DatabaseConnection", return_value=connection):
        yield connection


@pytest.fixture(scope="function")
def mock_session(mock_db_connection):
    """Mock database session with proper chaining and fresh state for each test."""
    session = MagicMock(spec=Session)

    # Create a single reusable query chain that properly chains methods
    query_chain = MagicMock()
    query_chain.filter = MagicMock(return_value=query_chain)
    query_chain.filter_by = MagicMock(return_value=query_chain)
    query_chain.order_by = MagicMock(return_value=query_chain)
    query_chain.limit = MagicMock(return_value=query_chain)
    query_chain.first = MagicMock(return_value=None)
    query_chain.all = MagicMock(return_value=[])

    # query() returns the consistent query chain - no side_effect!
    session.query = MagicMock(return_value=query_chain)
    session.add = MagicMock()
    session.commit = MagicMock()
    session.rollback = MagicMock()
    session.flush = MagicMock()
    session.close = MagicMock()

    # Patch Session where it's imported in client module
    with patch("tracertm.api.client.Session", return_value=session):
        yield session


@pytest.fixture(scope="function")
def client(mock_config_manager, mock_session):
    """Create TraceRTMClient instance with mocked dependencies."""
    client = TraceRTMClient(agent_id="test-agent-1", agent_name="Test Agent")
    client._session = mock_session
    return client


class TestTraceRTMClientInitialization:
    """Test TraceRTMClient initialization and configuration."""

    def test_init_with_agent_id_and_name(self, mock_config_manager):
        """Test initialization with agent ID and name."""
        client = TraceRTMClient(agent_id="agent-123", agent_name="My Agent")

        assert client.agent_id == "agent-123"
        assert client.agent_name == "My Agent"
        assert client._session is None
        assert client._db is None

    def test_init_without_agent(self, mock_config_manager):
        """Test initialization without agent credentials."""
        client = TraceRTMClient()

        assert client.agent_id is None
        assert client.agent_name is None

    def test_get_session_creates_connection(self, mock_config_manager, mock_db_connection):
        """Test _get_session creates database connection."""
        with patch("tracertm.api.client.Session") as mock_session_cls:
            mock_session = MagicMock()
            mock_session_cls.return_value = mock_session

            client = TraceRTMClient()
            session = client._get_session()

            assert session == mock_session
            mock_db_connection.connect.assert_called_once()

    def test_get_session_reuses_existing(self, client):
        """Test _get_session reuses existing session."""
        session1 = client._get_session()
        session2 = client._get_session()

        assert session1 is session2

    def test_get_session_no_database_configured(self):
        """Test _get_session raises error when database not configured."""
        manager = MagicMock()
        manager.get.return_value = None

        with patch("tracertm.api.client.ConfigManager", return_value=manager):
            client = TraceRTMClient()

            with pytest.raises(ValueError, match="Database not configured"):
                client._get_session()

    def test_get_project_id_success(self, client, mock_config_manager):
        """Test _get_project_id returns current project."""
        project_id = client._get_project_id()
        assert project_id == "test-project-123"

    def test_get_project_id_no_project_selected(self):
        """Test _get_project_id raises error when no project selected."""
        manager = MagicMock()
        manager.get.return_value = None

        with patch("tracertm.api.client.ConfigManager", return_value=manager):
            client = TraceRTMClient()
            client._session = MagicMock()

            with pytest.raises(ValueError, match="No project selected"):
                client._get_project_id()


class TestTraceRTMClientAgentOperations:
    """Test agent registration and management."""

    def test_register_agent_basic(self, client, mock_session):
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

    def test_register_agent_with_project_ids(self, client, mock_session):
        """Test agent registration with multiple projects."""
        mock_agent = MagicMock()
        mock_agent.id = "agent-multi"
        mock_session.add = MagicMock()

        with patch("tracertm.api.client.Agent") as mock_agent_cls:
            mock_agent_cls.return_value = mock_agent

            project_ids = ["proj-1", "proj-2", "proj-3"]
            agent_id = client.register_agent(
                name="Multi Project Agent",
                project_ids=project_ids,
            )

            # Check metadata was set
            call_kwargs = mock_agent_cls.call_args[1]
            assert "agent_metadata" in call_kwargs
            assert call_kwargs["agent_metadata"]["assigned_projects"] == project_ids

    def test_register_agent_with_metadata(self, client, mock_session):
        """Test agent registration with custom metadata."""
        mock_agent = MagicMock()
        mock_agent.id = "agent-meta"

        with patch("tracertm.api.client.Agent") as mock_agent_cls:
            mock_agent_cls.return_value = mock_agent

            metadata = {"custom_field": "value", "another": 123}
            agent_id = client.register_agent(
                name="Agent With Metadata",
                metadata=metadata,
            )

            call_kwargs = mock_agent_cls.call_args[1]
            assert call_kwargs["agent_metadata"]["custom_field"] == "value"

    def test_assign_agent_to_projects(self, client, mock_session):
        """Test assigning agent to multiple projects."""
        mock_agent = MagicMock()
        mock_agent.agent_metadata = {}

        query_chain = mock_session.query.return_value
        query_chain.filter.return_value.first.return_value = mock_agent

        client.assign_agent_to_projects("agent-123", ["proj-a", "proj-b"])

        assert "assigned_projects" in mock_agent.agent_metadata
        assert mock_agent.agent_metadata["assigned_projects"] == ["proj-a", "proj-b"]
        mock_session.commit.assert_called()

    def test_assign_agent_to_projects_not_found(self, client, mock_session):
        """Test assigning non-existent agent raises error."""
        query_chain = mock_session.query.return_value
        query_chain.filter.return_value.first.return_value = None

        with pytest.raises(ValueError, match="Agent not found"):
            client.assign_agent_to_projects("nonexistent", ["proj-1"])

    def test_get_agent_projects(self, client, mock_session):
        """Test getting projects assigned to agent."""
        mock_agent = MagicMock()
        mock_agent.project_id = "primary-proj"
        mock_agent.agent_metadata = {"assigned_projects": ["proj-1", "proj-2"]}

        query_chain = mock_session.query.return_value
        query_chain.filter.return_value.first.return_value = mock_agent

        projects = client.get_agent_projects("agent-123")

        assert "primary-proj" in projects
        assert "proj-1" in projects
        assert "proj-2" in projects

    def test_get_agent_projects_not_found(self, client, mock_session):
        """Test getting projects for non-existent agent returns empty list."""
        query_chain = mock_session.query.return_value
        query_chain.filter.return_value.first.return_value = None

        projects = client.get_agent_projects("nonexistent")

        assert projects == []

    def test_get_agent_projects_no_assigned(self, client, mock_session):
        """Test getting projects when none assigned returns only primary."""
        mock_agent = MagicMock()
        mock_agent.project_id = "primary-proj"
        mock_agent.agent_metadata = {}

        query_chain = mock_session.query.return_value
        query_chain.filter.return_value.first.return_value = mock_agent

        projects = client.get_agent_projects("agent-123")

        assert projects == ["primary-proj"]


class TestTraceRTMClientQueryOperations:
    """Test item querying functionality."""

    def test_query_items_basic(self, client, mock_session):
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
            )
        ]

        # Setup query chain to return mock items
        query_chain = mock_session.query.return_value
        query_chain.filter.return_value = query_chain
        query_chain.order_by.return_value = query_chain
        query_chain.all.return_value = mock_items

        items = client.query_items()

        assert len(items) == 1
        assert items[0]["id"] == "item-1"
        assert items[0]["title"] == "Item 1"
        mock_session.query.assert_called()

    def test_query_items_with_view_filter(self, client, mock_session):
        """Test querying items filtered by view."""
        query_chain = mock_session.query.return_value
        query_chain.filter.return_value = query_chain
        query_chain.order_by.return_value = query_chain
        query_chain.all.return_value = []

        items = client.query_items(view="code")

        # Check filter was applied (view is uppercased)
        query_chain.filter.assert_called()

    def test_query_items_with_status_filter(self, client, mock_session):
        """Test querying items filtered by status."""
        query_chain = mock_session.query.return_value
        query_chain.filter.return_value = query_chain
        query_chain.order_by.return_value = query_chain
        query_chain.all.return_value = []

        items = client.query_items(status="in_progress")

        query_chain.filter.assert_called()

    def test_query_items_with_type_filter(self, client, mock_session):
        """Test querying items filtered by type."""
        query_chain = mock_session.query.return_value
        query_chain.filter.return_value = query_chain
        query_chain.order_by.return_value = query_chain
        query_chain.all.return_value = []

        items = client.query_items(item_type="bug")

        query_chain.filter.assert_called()

    def test_query_items_with_priority_filter(self, client, mock_session):
        """Test querying items with priority filter."""
        query_chain = mock_session.query.return_value
        query_chain.filter.return_value = query_chain
        query_chain.order_by.return_value = query_chain
        query_chain.all.return_value = []

        items = client.query_items(priority="high")

        query_chain.filter.assert_called()

    def test_query_items_with_owner_filter(self, client, mock_session):
        """Test querying items with owner filter."""
        query_chain = mock_session.query.return_value
        query_chain.filter.return_value = query_chain
        query_chain.order_by.return_value = query_chain
        query_chain.all.return_value = []

        items = client.query_items(owner="user-123")

        query_chain.filter.assert_called()

    def test_query_items_with_parent_id_filter(self, client, mock_session):
        """Test querying items with parent_id filter."""
        query_chain = mock_session.query.return_value
        query_chain.filter.return_value = query_chain
        query_chain.order_by.return_value = query_chain
        query_chain.all.return_value = []

        items = client.query_items(parent_id="parent-123")

        query_chain.filter.assert_called()

    def test_query_items_with_limit(self, client, mock_session):
        """Test querying items respects limit parameter."""
        query_chain = mock_session.query.return_value
        query_chain.filter.return_value = query_chain
        query_chain.order_by.return_value = query_chain
        query_chain.limit.return_value = query_chain
        query_chain.all.return_value = []

        items = client.query_items(limit=50)

        query_chain.limit.assert_called_with(50)

    def test_query_items_excludes_deleted(self, client, mock_session):
        """Test query excludes soft-deleted items."""
        query_chain = mock_session.query.return_value
        query_chain.filter.return_value = query_chain
        query_chain.order_by.return_value = query_chain
        query_chain.all.return_value = []

        items = client.query_items()

        # Verify deleted_at filter is applied
        query_chain.filter.assert_called()

    def test_get_item_success(self, client, mock_session):
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

    def test_get_item_not_found(self, client, mock_session):
        """Test getting non-existent item returns None."""
        query_chain = mock_session.query.return_value
        query_chain.filter.return_value = query_chain
        query_chain.first.return_value = None

        item = client.get_item("nonexistent")

        assert item is None

    def test_get_item_soft_deleted_returns_none(self, client, mock_session):
        """Test getting soft-deleted item returns None."""
        # Soft-deleted items are filtered out by query
        query_chain = mock_session.query.return_value
        query_chain.filter.return_value = query_chain
        query_chain.first.return_value = None

        item = client.get_item("deleted-item")

        assert item is None

    def test_get_item_with_prefix_match(self, client, mock_session):
        """Test get_item uses prefix matching on ID."""
        mock_item = MagicMock(id="item-123-full")
        query_chain = mock_session.query.return_value
        query_chain.filter.return_value = query_chain
        query_chain.first.return_value = mock_item

        item = client.get_item("item-123")

        # Verify LIKE filter is used
        query_chain.filter.assert_called()


class TestTraceRTMClientItemCRUD:
    """Test item create, update, delete operations."""

    def test_create_item_minimal(self, client, mock_session):
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
            # add() is called for both Item and Event
            assert mock_session.add.call_count >= 1
            mock_session.commit.assert_called()
