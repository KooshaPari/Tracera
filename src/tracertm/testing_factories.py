"""
Manual factories for test data generation.

Provides factory functions for creating test instances of Pydantic models.
Compatible with Pydantic v2 (no pydantic-factories dependency).
"""

import uuid
from datetime import UTC, datetime

from tracertm.models import Item, Link, Project


def create_item(
    id: str | None = None,
    title: str = "Test Item",
    view: str = "FEATURE",
    item_type: str = "feature",
    project_id: str = "test-project",
    status: str = "todo",
    priority: str = "medium",
    description: str = "",
) -> Item:
    """Create a test item with custom values."""
    return Item(
        id=id or str(uuid.uuid4()),
        title=title,
        view=view,
        item_type=item_type,
        project_id=project_id,
        status=status,
        priority=priority,
        description=description,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )


def create_link(
    id: str | None = None,
    source_item_id: str = "source",
    target_item_id: str = "target",
    link_type: str = "depends_on",
    project_id: str = "test-project",
) -> Link:
    """Create a test link with custom values."""
    return Link(
        id=id or str(uuid.uuid4()),
        source_item_id=source_item_id,
        target_item_id=target_item_id,
        link_type=link_type,
        project_id=project_id,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )


def create_project(
    id: str | None = None,
    name: str = "Test Project",
    description: str = "A test project",
) -> Project:
    """Create a test project with custom values."""
    return Project(
        id=id or str(uuid.uuid4()),
        name=name,
        description=description,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
