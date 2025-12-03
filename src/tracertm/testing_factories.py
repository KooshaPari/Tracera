"""
Pydantic factories for test data generation.

Provides factory classes for creating test instances of Pydantic models.
"""


from pydantic_factories import ModelFactory

from tracertm.models import Item, Link, Project


class ItemFactory(ModelFactory[Item]):
    """Factory for generating Item instances."""

    __model__ = Item

    class Config:
        """Factory configuration."""

        arbitrary_types_allowed = True


class LinkFactory(ModelFactory[Link]):
    """Factory for generating Link instances."""

    __model__ = Link

    class Config:
        """Factory configuration."""

        arbitrary_types_allowed = True


class ProjectFactory(ModelFactory[Project]):
    """Factory for generating Project instances."""

    __model__ = Project

    class Config:
        """Factory configuration."""

        arbitrary_types_allowed = True


def create_item(
    title: str = "Test Item",
    view: str = "FEATURE",
    item_type: str = "feature",
) -> Item:
    """Create a test item with custom values."""
    return ItemFactory.create(  # type: ignore
        title=title,
        view=view,
        item_type=item_type,
    )


def create_link(
    source_item_id: str = "source",
    target_item_id: str = "target",
    link_type: str = "depends_on",
) -> Link:
    """Create a test link with custom values."""
    return LinkFactory.create(  # type: ignore
        source_item_id=source_item_id,
        target_item_id=target_item_id,
        link_type=link_type,
    )


def create_project(
    name: str = "Test Project",
    description: str = "A test project",
) -> Project:
    """Create a test project with custom values."""
    return ProjectFactory.create(  # type: ignore
        name=name,
        description=description,
    )
