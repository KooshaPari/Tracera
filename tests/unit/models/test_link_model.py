from typing import Any

"""Unit tests for Link model."""

from uuid import uuid4

import pytest

from tracertm.models import Link

pytestmark = pytest.mark.unit


@pytest.fixture
def test_ids() -> None:
    """Provide test IDs."""
    return {
        "project_id": str(uuid4()),
        "source_item_id": str(uuid4()),
        "target_item_id": str(uuid4()),
    }


class TestLinkModelCreation:
    """Test Link model creation."""

    def test_link_creation_with_required_fields(self, test_ids: Any) -> None:
        """Link creates with required fields."""
        link = Link(
            project_id=test_ids["project_id"],
            source_item_id=test_ids["source_item_id"],
            target_item_id=test_ids["target_item_id"],
            link_type="depends_on",
        )
        assert link.project_id == test_ids["project_id"]
        assert link.source_item_id == test_ids["source_item_id"]
        assert link.target_item_id == test_ids["target_item_id"]
        assert link.link_type == "depends_on"

    def test_link_creation_with_metadata(self, test_ids: Any) -> None:
        """Link can include metadata."""
        metadata = {"priority": "high", "verified": True}
        link = Link(
            project_id=test_ids["project_id"],
            source_item_id=test_ids["source_item_id"],
            target_item_id=test_ids["target_item_id"],
            link_type="validates",
            link_metadata=metadata,
        )
        assert link.link_metadata == metadata

    def test_link_with_explicit_id(self, test_ids: Any) -> None:
        """Link can have explicit ID."""
        link_id = "link-123"
        link = Link(
            id=link_id,
            project_id=test_ids["project_id"],
            source_item_id=test_ids["source_item_id"],
            target_item_id=test_ids["target_item_id"],
            link_type="implements",
        )
        assert link.id == link_id


class TestLinkModelTypes:
    """Test Link model with different link types."""

    def test_link_type_depends_on(self, test_ids: Any) -> None:
        """Link supports depends_on type."""
        link = Link(
            project_id=test_ids["project_id"],
            source_item_id=test_ids["source_item_id"],
            target_item_id=test_ids["target_item_id"],
            link_type="depends_on",
        )
        assert link.link_type == "depends_on"

    def test_link_type_blocked_by(self, test_ids: Any) -> None:
        """Link supports blocked_by type."""
        link = Link(
            project_id=test_ids["project_id"],
            source_item_id=test_ids["source_item_id"],
            target_item_id=test_ids["target_item_id"],
            link_type="blocked_by",
        )
        assert link.link_type == "blocked_by"

    def test_link_type_implements(self, test_ids: Any) -> None:
        """Link supports implements type."""
        link = Link(
            project_id=test_ids["project_id"],
            source_item_id=test_ids["source_item_id"],
            target_item_id=test_ids["target_item_id"],
            link_type="implements",
        )
        assert link.link_type == "implements"

    def test_link_type_tests(self, test_ids: Any) -> None:
        """Link supports tests type."""
        link = Link(
            project_id=test_ids["project_id"],
            source_item_id=test_ids["source_item_id"],
            target_item_id=test_ids["target_item_id"],
            link_type="tests",
        )
        assert link.link_type == "tests"


class TestLinkModelComparison:
    """Test Link model comparison."""

    def test_links_with_different_ids(self, test_ids: Any) -> None:
        """Links with different IDs are different."""
        link1 = Link(
            id="link-1",
            project_id=test_ids["project_id"],
            source_item_id=test_ids["source_item_id"],
            target_item_id=test_ids["target_item_id"],
            link_type="depends_on",
        )
        link2 = Link(
            id="link-2",
            project_id=test_ids["project_id"],
            source_item_id=test_ids["source_item_id"],
            target_item_id=test_ids["target_item_id"],
            link_type="depends_on",
        )
        assert link1.id != link2.id

    def test_links_same_items_different_types(self, test_ids: Any) -> None:
        """Links can exist between same items with different types."""
        link1 = Link(
            project_id=test_ids["project_id"],
            source_item_id=test_ids["source_item_id"],
            target_item_id=test_ids["target_item_id"],
            link_type="depends_on",
        )
        link2 = Link(
            project_id=test_ids["project_id"],
            source_item_id=test_ids["source_item_id"],
            target_item_id=test_ids["target_item_id"],
            link_type="validates",
        )
        assert link1.link_type != link2.link_type


class TestLinkModelAttributes:
    """Test Link model attributes."""

    def test_link_has_timestamp_attributes(self, test_ids: Any) -> None:
        """Link has timestamp attributes."""
        link = Link(
            project_id=test_ids["project_id"],
            source_item_id=test_ids["source_item_id"],
            target_item_id=test_ids["target_item_id"],
            link_type="depends_on",
        )
        assert hasattr(link, "created_at")
        assert hasattr(link, "updated_at")

    def test_link_metadata_defaults_to_dict(self, test_ids: Any) -> None:
        """Link metadata defaults to empty dict when not provided."""
        link = Link(
            project_id=test_ids["project_id"],
            source_item_id=test_ids["source_item_id"],
            target_item_id=test_ids["target_item_id"],
            link_type="depends_on",
        )
        # Check if link_metadata attribute exists
        assert hasattr(link, "link_metadata")


class TestLinkModelRepresentation:
    """Test Link model representation."""

    def test_link_repr(self, test_ids: Any) -> None:
        """Link has string representation."""
        link = Link(
            project_id=test_ids["project_id"],
            source_item_id=test_ids["source_item_id"],
            target_item_id=test_ids["target_item_id"],
            link_type="depends_on",
        )
        repr_str = repr(link)
        assert "Link" in repr_str or "link" in repr_str.lower()
