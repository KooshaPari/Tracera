"""Manual factories for test data generation.

Provides factory functions for creating test instances of Pydantic models.
Compatible with Pydantic v2 (no pydantic-factories dependency).
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import UTC, datetime

from tracertm.models import Item, Link, Project


@dataclass
class ItemFactoryConfig:
    """Configuration for creating test items."""

    title: str = "Test Item"
    view: str = "FEATURE"
    item_type: str = "feature"
    project_id: str = "test-project"
    status: str = "todo"
    priority: str = "medium"
    description: str = ""


def create_item(
    id: str | None = None,
    config: ItemFactoryConfig | None = None,
) -> Item:
    """Create a test item with custom values."""
    cfg = config or ItemFactoryConfig()
    return Item(
        id=id or str(uuid.uuid4()),
        title=cfg.title,
        view=cfg.view,
        item_type=cfg.item_type,
        project_id=cfg.project_id,
        status=cfg.status,
        priority=cfg.priority,
        description=cfg.description,
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
