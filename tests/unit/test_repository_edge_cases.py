"""Phase 15A: Quick Wins - Repository Layer Edge Cases.

Focus: Edge cases and boundary conditions for repositories
Target: LinkRepository and other repository methods
Coverage Goal: Increase repository coverage with edge cases
"""

from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from tests.test_constants import COUNT_FIVE, COUNT_TEN, COUNT_TWO
from tracertm.models.link import Link
from tracertm.repositories.link_repository import LinkRepository


class TestLinkRepositoryEdgeCases:
    """Edge cases for LinkRepository."""

    @pytest.mark.asyncio
    async def test_link_repository_init(self) -> None:
        """Test repository initialization."""
        mock_session = AsyncMock(spec=AsyncSession)
        repo = LinkRepository(mock_session)

        assert repo.session is mock_session

    @pytest.mark.asyncio
    async def test_create_link_minimal(self) -> None:
        """Test creating link with minimal required fields."""
        mock_session = AsyncMock(spec=AsyncSession)
        repo = LinkRepository(mock_session)

        link = await repo.create(
            project_id="proj-1",
            source_item_id="item-1",
            target_item_id="item-2",
            link_type="depends_on",
        )

        assert link.project_id == "proj-1"
        assert link.source_item_id == "item-1"
        assert link.target_item_id == "item-2"
        assert link.link_type == "depends_on"
        assert link.metadata == {}

    @pytest.mark.asyncio
    async def test_create_link_with_metadata(self) -> None:
        """Test creating link with metadata."""
        mock_session = AsyncMock(spec=AsyncSession)
        repo = LinkRepository(mock_session)

        metadata = {"priority": "high", "comment": "Critical dependency"}
        link = await repo.create(
            project_id="proj-1",
            source_item_id="item-1",
            target_item_id="item-2",
            link_type="depends_on",
            metadata=metadata,
        )

        assert link.metadata == metadata

    @pytest.mark.asyncio
    async def test_create_link_with_empty_metadata(self) -> None:
        """Test creating link with explicitly empty metadata."""
        mock_session = AsyncMock(spec=AsyncSession)
        repo = LinkRepository(mock_session)

        link = await repo.create(
            project_id="proj-1",
            source_item_id="item-1",
            target_item_id="item-2",
            link_type="related_to",
            metadata={},
        )

        assert link.metadata == {}

    @pytest.mark.asyncio
    async def test_create_link_with_none_metadata(self) -> None:
        """Test creating link with None metadata (should default to empty dict)."""
        mock_session = AsyncMock(spec=AsyncSession)
        repo = LinkRepository(mock_session)

        link = await repo.create(
            project_id="proj-1",
            source_item_id="item-1",
            target_item_id="item-2",
            link_type="related_to",
            metadata=None,
        )

        assert link.metadata == {}

    @pytest.mark.asyncio
    async def test_create_link_generates_uuid(self) -> None:
        """Test that link creation generates valid UUID."""
        mock_session = AsyncMock(spec=AsyncSession)
        repo = LinkRepository(mock_session)

        link = await repo.create(
            project_id="proj-1",
            source_item_id="item-1",
            target_item_id="item-2",
            link_type="depends_on",
        )

        # UUID should be string format
        assert isinstance(link.id, str)
        assert len(link.id) == 36  # Standard UUID format

    @pytest.mark.asyncio
    async def test_create_link_different_link_types(self) -> None:
        """Test creating links with different link types."""
        mock_session = AsyncMock(spec=AsyncSession)
        repo = LinkRepository(mock_session)

        link_types = [
            "depends_on",
            "related_to",
            "parent_of",
            "child_of",
            "implements",
            "tests",
        ]

        for link_type in link_types:
            link = await repo.create(
                project_id="proj-1",
                source_item_id="item-1",
                target_item_id="item-2",
                link_type=link_type,
            )
            assert link.link_type == link_type

    @pytest.mark.asyncio
    async def test_create_link_same_source_target(self) -> None:
        """Test creating self-referential link (edge case)."""
        mock_session = AsyncMock(spec=AsyncSession)
        repo = LinkRepository(mock_session)

        link = await repo.create(
            project_id="proj-1",
            source_item_id="item-1",
            target_item_id="item-1",
            link_type="related_to",
        )

        assert link.source_item_id == link.target_item_id

    @pytest.mark.asyncio
    async def test_create_link_calls_session_methods(self) -> None:
        """Test that create calls appropriate session methods."""
        mock_session = AsyncMock(spec=AsyncSession)
        repo = LinkRepository(mock_session)

        await repo.create(project_id="proj-1", source_item_id="item-1", target_item_id="item-2", link_type="depends_on")

        mock_session.add.assert_called_once()
        mock_session.flush.assert_called_once()
        mock_session.refresh.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_by_id_found(self) -> None:
        """Test getting link by ID when it exists."""
        mock_session = AsyncMock(spec=AsyncSession)
        mock_link = Link(
            id="link-1",
            project_id="proj-1",
            source_item_id="item-1",
            target_item_id="item-2",
            link_type="depends_on",
        )
        # Use MagicMock for result object (sync methods)
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_link
        mock_session.execute = AsyncMock(return_value=mock_result)

        repo = LinkRepository(mock_session)
        result = await repo.get_by_id("link-1")

        assert result is mock_link

    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self) -> None:
        """Test getting link by ID when it doesn't exist."""
        mock_session = AsyncMock(spec=AsyncSession)
        # Use MagicMock for result object (sync methods)
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute = AsyncMock(return_value=mock_result)

        repo = LinkRepository(mock_session)
        result = await repo.get_by_id("nonexistent")

        assert result is None

    @pytest.mark.asyncio
    async def test_get_by_project_empty(self) -> None:
        """Test getting links for project with no links."""
        mock_session = AsyncMock(spec=AsyncSession)
        # Use MagicMock for result and scalars (sync methods)
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = []
        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalars
        mock_session.execute = AsyncMock(return_value=mock_result)

        repo = LinkRepository(mock_session)
        result = await repo.get_by_project("proj-1")

        assert result == []

    @pytest.mark.asyncio
    async def test_get_by_project_multiple_links(self) -> None:
        """Test getting multiple links for a project."""
        mock_session = AsyncMock(spec=AsyncSession)
        mock_links = [
            Link(
                id="link-1",
                project_id="proj-1",
                source_item_id="item-1",
                target_item_id="item-2",
                link_type="depends_on",
            ),
            Link(
                id="link-2",
                project_id="proj-1",
                source_item_id="item-2",
                target_item_id="item-3",
                link_type="related_to",
            ),
        ]
        # Use MagicMock for result and scalars (sync methods)
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = mock_links
        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalars
        mock_session.execute = AsyncMock(return_value=mock_result)

        repo = LinkRepository(mock_session)
        result = await repo.get_by_project("proj-1")

        assert len(result) == COUNT_TWO
        assert all(isinstance(link, Link) for link in result)

    @pytest.mark.asyncio
    async def test_get_by_source_no_links(self) -> None:
        """Test getting links from source item with no outgoing links."""
        mock_session = AsyncMock(spec=AsyncSession)
        # Use MagicMock for result and scalars (sync methods)
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = []
        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalars
        mock_session.execute = AsyncMock(return_value=mock_result)

        repo = LinkRepository(mock_session)
        result = await repo.get_by_source("item-1")

        assert result == []

    @pytest.mark.asyncio
    async def test_get_by_source_multiple_links(self) -> None:
        """Test getting multiple links from source item."""
        mock_session = AsyncMock(spec=AsyncSession)
        mock_links = [
            Link(
                id="link-1",
                project_id="proj-1",
                source_item_id="item-1",
                target_item_id="item-2",
                link_type="depends_on",
            ),
            Link(
                id="link-2",
                project_id="proj-1",
                source_item_id="item-1",
                target_item_id="item-3",
                link_type="related_to",
            ),
        ]
        # Use MagicMock for result and scalars (sync methods)
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = mock_links
        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalars
        mock_session.execute = AsyncMock(return_value=mock_result)

        repo = LinkRepository(mock_session)
        result = await repo.get_by_source("item-1")

        assert len(result) == COUNT_TWO
        assert all(link.source_item_id == "item-1" for link in result)

    @pytest.mark.asyncio
    async def test_get_by_target_no_links(self) -> None:
        """Test getting links to target item with no incoming links."""
        mock_session = AsyncMock(spec=AsyncSession)
        # Use MagicMock for result and scalars (sync methods)
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = []
        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalars
        mock_session.execute = AsyncMock(return_value=mock_result)

        repo = LinkRepository(mock_session)
        result = await repo.get_by_target("item-1")

        assert result == []

    @pytest.mark.asyncio
    async def test_get_by_target_multiple_links(self) -> None:
        """Test getting multiple links to target item."""
        mock_session = AsyncMock(spec=AsyncSession)
        mock_links = [
            Link(
                id="link-1",
                project_id="proj-1",
                source_item_id="item-1",
                target_item_id="item-3",
                link_type="depends_on",
            ),
            Link(
                id="link-2",
                project_id="proj-1",
                source_item_id="item-2",
                target_item_id="item-3",
                link_type="related_to",
            ),
        ]
        # Use MagicMock for result and scalars (sync methods)
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = mock_links
        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalars
        mock_session.execute = AsyncMock(return_value=mock_result)

        repo = LinkRepository(mock_session)
        result = await repo.get_by_target("item-3")

        assert len(result) == COUNT_TWO
        assert all(link.target_item_id == "item-3" for link in result)

    @pytest.mark.asyncio
    async def test_get_by_item_no_links(self) -> None:
        """Test getting links for item with no connections."""
        mock_session = AsyncMock(spec=AsyncSession)
        # Use MagicMock for result and scalars (sync methods)
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = []
        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalars
        mock_session.execute = AsyncMock(return_value=mock_result)

        repo = LinkRepository(mock_session)
        result = await repo.get_by_item("item-1")

        assert result == []

    @pytest.mark.asyncio
    async def test_get_by_item_as_source_and_target(self) -> None:
        """Test getting links where item is both source and target."""
        mock_session = AsyncMock(spec=AsyncSession)
        mock_links = [
            Link(
                id="link-1",
                project_id="proj-1",
                source_item_id="item-1",
                target_item_id="item-2",
                link_type="depends_on",
            ),
            Link(
                id="link-2",
                project_id="proj-1",
                source_item_id="item-3",
                target_item_id="item-1",
                link_type="related_to",
            ),
        ]
        # Use MagicMock for result and scalars (sync methods)
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = mock_links
        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalars
        mock_session.execute = AsyncMock(return_value=mock_result)

        repo = LinkRepository(mock_session)
        result = await repo.get_by_item("item-1")

        assert len(result) == COUNT_TWO

    @pytest.mark.asyncio
    async def test_delete_link_found(self) -> None:
        """Test deleting existing link."""
        mock_session = AsyncMock(spec=AsyncSession)
        mock_result = AsyncMock()
        mock_result.rowcount = 1
        mock_session.execute.return_value = mock_result

        repo = LinkRepository(mock_session)
        result = await repo.delete("link-1")

        assert result is True

    @pytest.mark.asyncio
    async def test_delete_link_not_found(self) -> None:
        """Test deleting non-existent link."""
        mock_session = AsyncMock(spec=AsyncSession)
        mock_result = AsyncMock()
        mock_result.rowcount = 0
        mock_session.execute.return_value = mock_result

        repo = LinkRepository(mock_session)
        result = await repo.delete("nonexistent")

        assert result is False

    @pytest.mark.asyncio
    async def test_delete_by_item_no_links(self) -> None:
        """Test deleting links for item with no connections."""
        mock_session = AsyncMock(spec=AsyncSession)
        mock_result = AsyncMock()
        mock_result.rowcount = 0
        mock_session.execute.return_value = mock_result

        repo = LinkRepository(mock_session)
        count = await repo.delete_by_item("item-1")

        assert count == 0

    @pytest.mark.asyncio
    async def test_delete_by_item_multiple_links(self) -> None:
        """Test deleting multiple links for an item."""
        mock_session = AsyncMock(spec=AsyncSession)
        mock_result = AsyncMock()
        mock_result.rowcount = 5
        mock_session.execute.return_value = mock_result

        repo = LinkRepository(mock_session)
        count = await repo.delete_by_item("item-1")

        assert count == COUNT_FIVE

    @pytest.mark.asyncio
    async def test_delete_by_item_as_source_and_target(self) -> None:
        """Test that delete_by_item removes links where item is source or target."""
        mock_session = AsyncMock(spec=AsyncSession)
        mock_result = AsyncMock()
        mock_result.rowcount = 10
        mock_session.execute.return_value = mock_result

        repo = LinkRepository(mock_session)
        count = await repo.delete_by_item("item-1")

        # Should delete all links where item is either source or target
        assert count == COUNT_TEN

    @pytest.mark.asyncio
    async def test_link_metadata_special_characters(self) -> None:
        """Test creating link with special characters in metadata."""
        mock_session = AsyncMock(spec=AsyncSession)
        repo = LinkRepository(mock_session)

        metadata = {
            "comment": "Test with special chars: @#$%^&*()",
            "unicode": "Test with unicode: \u2713 \u2717 \u00e9",
        }

        link = await repo.create(
            project_id="proj-1",
            source_item_id="item-1",
            target_item_id="item-2",
            link_type="related_to",
            metadata=metadata,
        )

        assert link.metadata == metadata

    @pytest.mark.asyncio
    async def test_link_metadata_nested_structure(self) -> None:
        """Test creating link with complex nested metadata."""
        mock_session = AsyncMock(spec=AsyncSession)
        repo = LinkRepository(mock_session)

        metadata = {
            "validation": {
                "required": True,
                "constraints": ["not_null", "unique"],
            },
            "history": [
                {"user": "user1", "timestamp": "2025-01-01"},
                {"user": "user2", "timestamp": "2025-01-02"},
            ],
        }

        link = await repo.create(
            project_id="proj-1",
            source_item_id="item-1",
            target_item_id="item-2",
            link_type="validates",
            metadata=metadata,
        )

        assert link.metadata == metadata

    @pytest.mark.asyncio
    async def test_multiple_links_same_items_different_types(self) -> None:
        """Test creating multiple links between same items with different types."""
        mock_session = AsyncMock(spec=AsyncSession)
        repo = LinkRepository(mock_session)

        link1 = await repo.create(
            project_id="proj-1",
            source_item_id="item-1",
            target_item_id="item-2",
            link_type="depends_on",
        )

        link2 = await repo.create(
            project_id="proj-1",
            source_item_id="item-1",
            target_item_id="item-2",
            link_type="related_to",
        )

        # Should create two separate links
        assert link1.id != link2.id
        assert link1.link_type != link2.link_type

    @pytest.mark.asyncio
    async def test_link_with_very_long_ids(self) -> None:
        """Test creating link with very long IDs (boundary test)."""
        mock_session = AsyncMock(spec=AsyncSession)
        repo = LinkRepository(mock_session)

        long_id = "a" * 255  # Very long ID

        link = await repo.create(
            project_id=long_id,
            source_item_id=long_id,
            target_item_id=long_id,
            link_type="related_to",
        )

        assert link.project_id == long_id

    @pytest.mark.asyncio
    async def test_link_with_numeric_string_ids(self) -> None:
        """Test creating link with numeric string IDs."""
        mock_session = AsyncMock(spec=AsyncSession)
        repo = LinkRepository(mock_session)

        link = await repo.create(
            project_id="12345",
            source_item_id="67890",
            target_item_id="11111",
            link_type="depends_on",
        )

        assert link.project_id == "12345"
        assert link.source_item_id == "67890"

    @pytest.mark.asyncio
    async def test_bidirectional_links(self) -> None:
        """Test creating bidirectional links between items."""
        mock_session = AsyncMock(spec=AsyncSession)
        repo = LinkRepository(mock_session)

        # Link from A to B
        link1 = await repo.create(
            project_id="proj-1",
            source_item_id="item-A",
            target_item_id="item-B",
            link_type="depends_on",
        )

        # Link from B to A (reverse direction)
        link2 = await repo.create(
            project_id="proj-1",
            source_item_id="item-B",
            target_item_id="item-A",
            link_type="depends_on",
        )

        assert link1.source_item_id == link2.target_item_id
        assert link1.target_item_id == link2.source_item_id
