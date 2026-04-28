"""MCP test configuration and fixtures."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any
from unittest.mock import MagicMock, patch

import pytest

if TYPE_CHECKING:
    from collections.abc import Callable
    from datetime import datetime


@pytest.fixture
def mock_mcp_server() -> None:
    """Create a mock MCP server for testing.

    Returns a mock object that can be used to verify tool registrations
    and simulate MCP server behavior without requiring FastMCP.
    """
    mock = MagicMock()
    mock.tools = {}
    mock.resources = {}
    mock.prompts = {}

    def mock_tool(*args: Any, **kwargs: Any) -> None:
        def decorator(fn: Callable[..., Any]) -> None:
            mock.tools[fn.__name__] = {
                "fn": fn,
                "description": kwargs.get("description", ""),
            }
            return fn

        return decorator

    def mock_resource(uri: str) -> None:
        def decorator(fn: Callable[..., Any]) -> None:
            mock.resources[uri] = {
                "fn": fn,
            }
            return fn

        return decorator

    def mock_prompt(name: str) -> None:
        def decorator(fn: Callable[..., Any]) -> None:
            mock.prompts[name] = {
                "fn": fn,
            }
            return fn

        return decorator

    mock.tool = mock_tool
    mock.resource = mock_resource
    mock.prompt = mock_prompt

    return mock


@pytest.fixture
def mock_storage() -> None:
    """Create a mock storage manager for testing."""
    mock = MagicMock()

    # Create a mock session context manager
    mock_session = MagicMock()
    mock.get_session.return_value.__enter__ = MagicMock(return_value=mock_session)
    mock.get_session.return_value.__exit__ = MagicMock(return_value=None)

    return mock


@pytest.fixture
def mock_config() -> None:
    """Create a mock config manager for testing."""
    mock = MagicMock()
    mock.get.return_value = "test-project-id"
    return mock


@pytest.fixture
def sample_project() -> None:
    """Create a sample project for testing."""
    return {
        "id": "proj-001",
        "name": "Test Project",
        "description": "A test project for unit tests",
    }


@pytest.fixture
def sample_items() -> None:
    """Create sample items for testing."""
    return [
        {
            "id": "item-001",
            "title": "Feature 1",
            "view": "FEATURE",
            "item_type": "feature",
            "status": "todo",
            "priority": "high",
        },
        {
            "id": "item-002",
            "title": "Story 1",
            "view": "STORY",
            "item_type": "story",
            "status": "in_progress",
            "priority": "medium",
        },
        {
            "id": "item-003",
            "title": "Test 1",
            "view": "TEST",
            "item_type": "test",
            "status": "done",
            "priority": "low",
        },
    ]


@pytest.fixture
def sample_links() -> None:
    """Create sample links for testing."""
    return [
        {
            "id": "link-001",
            "source_id": "item-001",
            "target_id": "item-002",
            "link_type": "parent_of",
        },
        {
            "id": "link-002",
            "source_id": "item-002",
            "target_id": "item-003",
            "link_type": "tested_by",
        },
    ]


@pytest.fixture
def mock_context() -> None:
    """Create a mock MCP context for testing."""
    mock = MagicMock()

    async def mock_report_progress(progress: int, total: int, message: str = "") -> None:
        pass

    mock.report_progress = mock_report_progress
    return mock


class MockItem:
    """Mock Item model for testing."""

    def __init__(
        self,
        id: str,
        title: str,
        view: str = "FEATURE",
        item_type: str = "feature",
        status: str = "todo",
        priority: str = "medium",
        owner: str | None = None,
        project_id: str = "test-project",
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
        deleted_at: datetime | None = None,
    ) -> None:
        self.id = id
        self.title = title
        self.view = view
        self.item_type = item_type
        self.status = status
        self.priority = priority
        self.owner = owner
        self.project_id = project_id
        self.created_at = created_at
        self.updated_at = updated_at
        self.deleted_at = deleted_at


class MockLink:
    """Mock Link model for testing."""

    def __init__(
        self,
        id: str,
        source_id: str,
        target_id: str,
        link_type: str = "relates_to",
        project_id: str = "test-project",
        created_at: datetime | None = None,
        deleted_at: datetime | None = None,
    ) -> None:
        self.id = id
        self.source_id = source_id
        self.target_id = target_id
        self.link_type = link_type
        self.project_id = project_id
        self.created_at = created_at
        self.deleted_at = deleted_at


class MockProject:
    """Mock Project model for testing."""

    def __init__(
        self,
        id: str,
        name: str,
        description: str = "",
        created_at: datetime | None = None,
        deleted_at: datetime | None = None,
    ) -> None:
        self.id = id
        self.name = name
        self.description = description
        self.created_at = created_at
        self.deleted_at = deleted_at


@pytest.fixture
def mock_items_factory() -> None:
    """Factory fixture to create mock items."""

    def factory(count: int = 3, project_id: str = "test-project") -> list[MockItem]:
        return [
            MockItem(
                id=f"item-{i:03d}",
                title=f"Item {i}",
                project_id=project_id,
            )
            for i in range(count)
        ]

    return factory


@pytest.fixture
def mock_links_factory() -> None:
    """Factory fixture to create mock links."""

    def factory(items: list[MockItem]) -> list[MockLink]:
        return [
            MockLink(
                id=f"link-{i:03d}",
                source_id=items[i].id,
                target_id=items[i + 1].id,
                project_id=items[i].project_id,
            )
            for i in range(len(items) - 1)
        ]

    return factory
