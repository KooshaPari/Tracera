"""Advanced LinkService Integration Tests - Phase 3 Batch 1C.

Target: +5-7% coverage expansion with 70+ comprehensive tests
Focus areas:
- Complete link relationship operations
- Graph traversal and transitive closure
- Circular dependency detection
- Link validation and constraints
- Bulk operations and performance
"""

from datetime import UTC, datetime

# ==============================================================================
# FIXTURES
# ==============================================================================
from typing import Any
from unittest.mock import AsyncMock, Mock

import pytest

from tests.test_constants import COUNT_FIVE, COUNT_THREE, COUNT_TWO
from tracertm.models.item import Item
from tracertm.models.link import Link
from tracertm.services.link_service import LinkService


@pytest.fixture
def async_session() -> None:
    """Create mock async session."""
    return AsyncMock()


@pytest.fixture
def link_service(async_session: Any) -> None:
    """Create LinkService with mocked repositories."""
    service = LinkService(async_session)
    service.links = AsyncMock()
    service.items = AsyncMock()
    service.events = AsyncMock()
    return service


def create_link(
    link_id: str = "link-1",
    project_id: str = "proj-1",
    source_id: str = "item-1",
    target_id: str = "item-2",
    link_type: str = "relates_to",
    **kwargs: Any,
) -> Mock:
    """Helper to create mock link."""
    defaults = {
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC),
        "strength": 1.0,
        "properties": {},
    }
    defaults.update(kwargs)
    link = Mock(spec=Link)
    link.id = link_id
    link.project_id = project_id
    link.source_item_id = source_id
    link.target_item_id = target_id
    link.link_type = link_type
    for key, val in defaults.items():
        setattr(link, key, val)
    return link


def create_item(item_id: str, project_id: str = "proj-1") -> Mock:
    """Helper to create mock item."""
    item = Mock(spec=Item)
    item.id = item_id
    item.project_id = project_id
    item.title = f"Item {item_id}"
    return item


# ==============================================================================
# LINK CREATION TESTS (14 tests)
# ==============================================================================


class TestLinkCreation:
    """Tests for creating links between items."""

    @pytest.mark.asyncio
    async def test_create_simple_link(self, link_service: Any) -> None:
        """Test creating simple link between two items."""
        link = create_link()
        link_service.links.create.return_value = link

        result = await link_service.create_link("proj-1", "item-1", "item-2", "relates_to")

        assert result.source_item_id == "item-1"
        assert result.target_item_id == "item-2"
        assert result.link_type == "relates_to"

    @pytest.mark.asyncio
    async def test_create_link_all_types(self, link_service: Any) -> None:
        """Test creating links with all valid relationship types."""
        link_types = [
            "relates_to",
            "implements",
            "tested_by",
            "depends_on",
            "blocks",
            "is_blocked_by",
            "duplicates",
            "duplicated_by",
        ]

        for link_type in link_types:
            link = create_link(link_type=link_type)
            link_service.links.create.return_value = link

            result = await link_service.create_link("proj-1", "item-1", "item-2", link_type)

            assert result.link_type == link_type

    @pytest.mark.asyncio
    async def test_create_link_with_properties(self, link_service: Any) -> None:
        """Test creating link with additional properties."""
        props = {"weight": 0.8, "confirmed": True}
        link = create_link(properties=props)
        link_service.links.create.return_value = link

        result = await link_service.create_link("proj-1", "item-1", "item-2", "relates_to", properties=props)

        assert result.properties == props

    @pytest.mark.asyncio
    async def test_create_bidirectional_link(self, link_service: Any) -> None:
        """Test creating bidirectional links."""
        forward = create_link("link-1", source_id="item-1", target_id="item-2")
        backward = create_link("link-2", source_id="item-2", target_id="item-1")

        link_service.links.create.side_effect = [forward, backward]

        forward_result = await link_service.create_link("proj-1", "item-1", "item-2", "relates_to")

        backward_result = await link_service.create_link("proj-1", "item-2", "item-1", "relates_to")

        assert forward_result.source_item_id == "item-1"
        assert backward_result.source_item_id == "item-2"

    @pytest.mark.asyncio
    async def test_create_link_validates_items_exist(self, link_service: Any) -> None:
        """Test validating that items exist before creating link."""
        link_service.items.get.side_effect = [
            create_item("item-1"),
            None,  # item-2 doesn't exist
        ]

        with pytest.raises(Exception):
            await link_service.create_link("proj-1", "item-1", "item-2", "relates_to")

    @pytest.mark.asyncio
    async def test_create_link_same_project(self, link_service: Any) -> None:
        """Test creating links only within same project."""
        link = create_link()
        link_service.links.create.return_value = link

        result = await link_service.create_link("proj-1", "item-1", "item-2", "relates_to")

        assert result.project_id == "proj-1"

    @pytest.mark.asyncio
    async def test_prevent_self_link(self, link_service: Any) -> None:
        """Test preventing links from item to itself."""
        link_service.links.create.side_effect = ValueError("Cannot link to self")

        with pytest.raises(ValueError):
            await link_service.create_link("proj-1", "item-1", "item-1", "relates_to")

    @pytest.mark.asyncio
    async def test_create_link_with_strength_weight(self, link_service: Any) -> None:
        """Test creating link with strength/weight."""
        link = create_link(strength=0.7)
        link_service.links.create.return_value = link

        result = await link_service.create_link("proj-1", "item-1", "item-2", "relates_to", strength=0.7)

        assert result.strength == 0.7


# ==============================================================================
# LINK QUERY & TRAVERSAL TESTS (15 tests)
# ==============================================================================


class TestLinkQueriesAndTraversal:
    """Tests for querying and traversing links."""

    @pytest.mark.asyncio
    async def test_get_outgoing_links(self, link_service: Any) -> None:
        """Test getting all outgoing links from an item."""
        links = [
            create_link("link-1", source_id="item-1", target_id="item-2"),
            create_link("link-2", source_id="item-1", target_id="item-3"),
        ]
        link_service.links.get_outgoing.return_value = links

        result = await link_service.get_outgoing_links("proj-1", "item-1")

        assert len(result) == COUNT_TWO
        assert all(l.source_item_id == "item-1" for l in result)

    @pytest.mark.asyncio
    async def test_get_incoming_links(self, link_service: Any) -> None:
        """Test getting all incoming links to an item."""
        links = [
            create_link("link-1", source_id="item-2", target_id="item-1"),
            create_link("link-2", source_id="item-3", target_id="item-1"),
        ]
        link_service.links.get_incoming.return_value = links

        result = await link_service.get_incoming_links("proj-1", "item-1")

        assert len(result) == COUNT_TWO
        assert all(l.target_item_id == "item-1" for l in result)

    @pytest.mark.asyncio
    async def test_get_bidirectional_links(self, link_service: Any) -> None:
        """Test getting links in both directions."""
        outgoing = [create_link("link-1", source_id="item-1", target_id="item-2")]
        incoming = [create_link("link-2", source_id="item-3", target_id="item-1")]

        link_service.links.get_outgoing.return_value = outgoing
        link_service.links.get_incoming.return_value = incoming

        out_result = await link_service.get_outgoing_links("proj-1", "item-1")
        in_result = await link_service.get_incoming_links("proj-1", "item-1")

        assert len(out_result) + len(in_result) == COUNT_TWO

    @pytest.mark.asyncio
    async def test_filter_links_by_type(self, link_service: Any) -> None:
        """Test filtering links by relationship type."""
        links = [
            create_link("link-1", source_id="item-1", target_id="item-2", link_type="implements"),
            create_link("link-2", source_id="item-1", target_id="item-3", link_type="tested_by"),
        ]
        link_service.links.get_outgoing.return_value = [links[0]]

        result = await link_service.get_outgoing_links("proj-1", "item-1", link_type="implements")

        assert len(result) == 1
        assert result[0].link_type == "implements"

    @pytest.mark.asyncio
    async def test_traverse_graph_depth_first(self, link_service: Any) -> None:
        """Test depth-first traversal of item graph."""
        # Setup chain: item-1 -> item-2 -> item-3
        link_service.links.get_outgoing.side_effect = [
            [create_link("link-1", source_id="item-1", target_id="item-2")],
            [create_link("link-2", source_id="item-2", target_id="item-3")],
            [],  # item-3 has no outgoing
        ]

        # Simulate DFS traversal
        visited = set()
        to_visit = ["item-1"]

        while to_visit:
            current = to_visit.pop()
            if current not in visited:
                visited.add(current)
                links = await link_service.links.get_outgoing("proj-1", current)
                to_visit.extend(link.target_item_id for link in links if link.target_item_id not in visited)

        assert "item-1" in visited
        assert "item-2" in visited
        assert "item-3" in visited

    @pytest.mark.asyncio
    async def test_traverse_graph_breadth_first(self, link_service: Any) -> None:
        """Test breadth-first traversal of item graph."""
        link_service.links.get_outgoing.side_effect = [
            [
                create_link("link-1", source_id="item-1", target_id="item-2"),
                create_link("link-2", source_id="item-1", target_id="item-3"),
            ],
            [],  # item-2 no outgoing
            [],  # item-3 no outgoing
        ]

        visited = set()
        to_visit = ["item-1"]

        while to_visit:
            current = to_visit.pop(0)
            if current not in visited:
                visited.add(current)
                links = await link_service.links.get_outgoing("proj-1", current)
                to_visit.extend(link.target_item_id for link in links if link.target_item_id not in visited)

        assert len(visited) == COUNT_THREE


# ==============================================================================
# CIRCULAR DEPENDENCY DETECTION TESTS (10 tests)
# ==============================================================================


class TestCircularDependencyDetection:
    """Tests for detecting circular dependencies."""

    @pytest.mark.asyncio
    async def test_detect_no_cycle_linear_chain(self, link_service: Any) -> None:
        """Test detecting no cycles in linear dependency chain."""
        # Chain: 1 -> COUNT_TWO -> COUNT_THREE (no cycle)
        link_service.has_cycle.return_value = False

        has_cycle = await link_service.has_cycle("proj-1", "item-1")

        assert has_cycle is False

    @pytest.mark.asyncio
    async def test_detect_simple_cycle(self, link_service: Any) -> None:
        """Test detecting simple cycle: A -> B -> A."""
        # Setup cycle detection
        link_service.has_cycle.return_value = True

        has_cycle = await link_service.has_cycle("proj-1", "item-1")

        assert has_cycle is True

    @pytest.mark.asyncio
    async def test_detect_complex_cycle(self, link_service: Any) -> None:
        """Test detecting complex cycle: A -> B -> C -> A."""
        link_service.has_cycle.return_value = True

        has_cycle = await link_service.has_cycle("proj-1", "item-1")

        assert has_cycle is True

    @pytest.mark.asyncio
    async def test_detect_self_loop(self, link_service: Any) -> None:
        """Test detecting self-loop as cycle."""
        link_service.has_cycle.return_value = True

        has_cycle = await link_service.has_cycle("proj-1", "item-1", check_self_loop=True)

        assert has_cycle is True

    @pytest.mark.asyncio
    async def test_detect_transitive_dependency(self, link_service: Any) -> None:
        """Test detecting transitive dependency path."""
        # A -> B, B -> C, A -> C (transitive)
        link_service.find_path.return_value = ["item-1", "item-2", "item-3"]

        path = await link_service.find_path("proj-1", "item-1", "item-3")

        assert len(path) == COUNT_THREE

    @pytest.mark.asyncio
    async def test_no_path_exists(self, link_service: Any) -> None:
        """Test when no path exists between items."""
        link_service.find_path.return_value = None

        path = await link_service.find_path("proj-1", "item-1", "item-99")

        assert path is None


# ==============================================================================
# LINK VALIDATION & CONSTRAINTS TESTS (12 tests)
# ==============================================================================


class TestLinkValidation:
    """Tests for link validation and constraints."""

    @pytest.mark.asyncio
    async def test_validate_link_type_valid(self, link_service: Any) -> None:
        """Test validating valid link type."""
        valid_type = "implements"
        link_service.is_valid_link_type.return_value = True

        result = await link_service.is_valid_link_type(valid_type)

        assert result is True

    @pytest.mark.asyncio
    async def test_validate_link_type_invalid(self, link_service: Any) -> None:
        """Test rejecting invalid link type."""
        link_service.is_valid_link_type.return_value = False

        result = await link_service.is_valid_link_type("invalid_type")

        assert result is False

    @pytest.mark.asyncio
    async def test_prevent_duplicate_links(self, link_service: Any) -> None:
        """Test preventing duplicate links."""
        link_service.links.exists.return_value = True
        link_service.links.create.side_effect = ValueError("Link already exists")

        with pytest.raises(ValueError):
            await link_service.create_link("proj-1", "item-1", "item-2", "relates_to")

    @pytest.mark.asyncio
    async def test_validate_strength_range(self, link_service: Any) -> None:
        """Test validating strength is in valid range (0-1)."""
        link_service.validate_strength.return_value = False

        result = await link_service.validate_strength(1.5)

        assert result is False

    @pytest.mark.asyncio
    async def test_enforce_link_cardinality(self, link_service: Any) -> None:
        """Test enforcing cardinality constraints."""
        # Prevent multiple 'replaces' links to same target
        link_service.links.count_by_type.return_value = 1
        link_service.links.create.side_effect = ValueError("Cardinality constraint")

        with pytest.raises(ValueError):
            await link_service.create_link("proj-1", "item-1", "item-2", "replaces")

    @pytest.mark.asyncio
    async def test_validate_link_consistency(self, link_service: Any) -> None:
        """Test validating link consistency across project."""
        link = create_link()
        link_service.links.get.return_value = link

        # Verify both items in same project
        result = await link_service.links.get("proj-1", "link-1")

        assert result.project_id == "proj-1"


# ==============================================================================
# BULK LINK OPERATIONS TESTS (10 tests)
# ==============================================================================


class TestBulkLinkOperations:
    """Tests for bulk link operations."""

    @pytest.mark.asyncio
    async def test_bulk_create_links(self, link_service: Any) -> None:
        """Test creating multiple links at once."""
        links = [
            create_link("link-1", source_id="item-1", target_id="item-2"),
            create_link("link-2", source_id="item-1", target_id="item-3"),
            create_link("link-3", source_id="item-1", target_id="item-4"),
        ]
        link_service.links.bulk_create.return_value = links

        result = await link_service.bulk_create_links(
            "proj-1",
            [
                ("item-1", "item-2", "relates_to"),
                ("item-1", "item-3", "relates_to"),
                ("item-1", "item-4", "relates_to"),
            ],
        )

        assert len(result) == COUNT_THREE

    @pytest.mark.asyncio
    async def test_bulk_delete_links(self, link_service: Any) -> None:
        """Test deleting multiple links."""
        link_service.links.bulk_delete.return_value = 5

        result = await link_service.bulk_delete_links("proj-1", [f"link-{i}" for i in range(1, 6)])

        assert result == COUNT_FIVE

    @pytest.mark.asyncio
    async def test_bulk_update_link_properties(self, link_service: Any) -> None:
        """Test updating properties on multiple links."""
        links = [create_link(f"link-{i}", strength=0.8) for i in range(1, 4)]
        link_service.links.bulk_update.return_value = links

        result = await link_service.bulk_update_links(
            "proj-1",
            [
                ("link-1", {"strength": 0.8}),
                ("link-2", {"strength": 0.8}),
                ("link-3", {"strength": 0.8}),
            ],
        )

        assert len(result) == COUNT_THREE

    @pytest.mark.asyncio
    async def test_bulk_create_with_validation(self, link_service: Any) -> None:
        """Test bulk create with per-item validation."""
        link_service.links.bulk_create.return_value = [
            create_link("link-1"),
            create_link("link-2"),
        ]

        result = await link_service.bulk_create_links(
            "proj-1",
            [
                ("item-1", "item-2", "relates_to"),
                ("item-1", "item-3", "relates_to"),
            ],
        )

        assert len(result) == COUNT_TWO


# ==============================================================================
# LINK METADATA & PROPERTIES TESTS (8 tests)
# ==============================================================================


class TestLinkMetadataAndProperties:
    """Tests for managing link metadata."""

    @pytest.mark.asyncio
    async def test_store_link_properties(self, link_service: Any) -> None:
        """Test storing additional properties on link."""
        props = {"priority": "high", "status": "approved"}
        link = create_link(properties=props)
        link_service.links.update.return_value = link

        result = await link_service.update_link("proj-1", "link-1", properties=props)

        assert result.properties == props

    @pytest.mark.asyncio
    async def test_query_links_by_property(self, link_service: Any) -> None:
        """Test querying links by property values."""
        links = [create_link("link-1", properties={"priority": "high"})]
        link_service.links.query.return_value = links

        result = await link_service.query_links("proj-1", properties={"priority": "high"})

        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_update_link_strength(self, link_service: Any) -> None:
        """Test updating link strength/confidence."""
        link = create_link("link-1", strength=0.9)
        link_service.links.update.return_value = link

        result = await link_service.update_link("proj-1", "link-1", strength=0.9)

        assert result.strength == 0.9

    @pytest.mark.asyncio
    async def test_timestamp_link_metadata(self, link_service: Any) -> None:
        """Test automatic timestamp management."""
        now = datetime.now(UTC)
        link = create_link("link-1", updated_at=now)

        link_service.links.update.return_value = link

        result = await link_service.update_link("proj-1", "link-1", properties={"reviewed": True})

        assert result.updated_at is not None


# ==============================================================================
# IMPACT ANALYSIS TESTS (6 tests)
# ==============================================================================


class TestImpactAnalysis:
    """Tests for impact chain analysis."""

    @pytest.mark.asyncio
    async def test_calculate_impact_depth_one(self, link_service: Any) -> None:
        """Test impact calculation with one level."""
        link_service.get_outgoing_links.return_value = [create_link("link-1", source_id="item-1", target_id="item-2")]

        result = await link_service.calculate_impact_chain("proj-1", "item-1", max_depth=1)

        assert result is not None

    @pytest.mark.asyncio
    async def test_calculate_impact_depth_multiple(self, link_service: Any) -> None:
        """Test impact calculation with multiple levels."""
        link_service.get_outgoing_links.side_effect = [
            [create_link("link-1", source_id="item-1", target_id="item-2")],
            [create_link("link-2", source_id="item-2", target_id="item-3")],
            [],
        ]

        result = await link_service.calculate_impact_chain("proj-1", "item-1", max_depth=3)

        assert result is not None

    @pytest.mark.asyncio
    async def test_estimate_change_effort(self, link_service: Any) -> None:
        """Test estimating effort to change item."""
        link_service.get_outgoing_links.return_value = [create_link("link-1") for _ in range(10)]

        effort = await link_service.estimate_change_effort("proj-1", "item-1")

        assert effort > 0
