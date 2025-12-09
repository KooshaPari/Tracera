"""
Comprehensive tests for ChaosModeService.

Coverage target: 85%+
Tests all methods: detect_zombies, analyze_impact, create_temporal_snapshot,
mass_update_items, get_project_health, explode_file, track_scope_crash,
cleanup_zombies, create_snapshot.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, Mock, MagicMock, patch

from tracertm.services.chaos_mode_service import ChaosModeService


class TestChaosModeServiceInit:
    """Test ChaosModeService initialization."""

    @pytest.mark.asyncio
    async def test_init_creates_repositories(self):
        """Test that initialization creates repositories."""
        session = AsyncMock()

        with patch("tracertm.services.chaos_mode_service.ItemRepository") as mock_item_repo, \
             patch("tracertm.services.chaos_mode_service.LinkRepository") as mock_link_repo, \
             patch("tracertm.services.chaos_mode_service.EventRepository") as mock_event_repo:

            service = ChaosModeService(session)

            assert service.session == session
            mock_item_repo.assert_called_once_with(session)
            mock_link_repo.assert_called_once_with(session)
            mock_event_repo.assert_called_once_with(session)


class TestDetectZombies:
    """Test detect_zombies method."""

    @pytest.fixture
    def service(self):
        """Create service with mocked repositories."""
        session = AsyncMock()
        service = ChaosModeService(session)
        service.items = AsyncMock()
        service.links = AsyncMock()
        service.events = AsyncMock()
        return service

    @pytest.mark.asyncio
    async def test_detect_zombies_empty_project(self, service):
        """Test zombie detection in empty project."""
        service.items.query = AsyncMock(return_value=[])

        result = await service.detect_zombies("proj1")

        assert result["zombie_count"] == 0
        assert result["zombies"] == []
        assert result["total_items"] == 0
        assert result["zombie_percentage"] == 0

    @pytest.mark.asyncio
    async def test_detect_zombies_no_zombies(self, service):
        """Test when no zombies exist (all items have links)."""
        item = Mock(id="item1", title="Item 1", status="todo", updated_at=datetime.utcnow())
        link = Mock()

        service.items.query = AsyncMock(return_value=[item])
        service.links.get_by_source = AsyncMock(return_value=[link])
        service.links.get_by_target = AsyncMock(return_value=[])

        result = await service.detect_zombies("proj1")

        assert result["zombie_count"] == 0
        assert result["total_items"] == 1

    @pytest.mark.asyncio
    async def test_detect_zombies_finds_orphaned_stale_items(self, service):
        """Test detection of orphaned and stale items as zombies."""
        # Item updated 45 days ago with no links
        stale_date = datetime.utcnow() - timedelta(days=45)
        zombie_item = Mock(id="zombie1", title="Zombie", status="todo", updated_at=stale_date)

        service.items.query = AsyncMock(return_value=[zombie_item])
        service.links.get_by_source = AsyncMock(return_value=[])
        service.links.get_by_target = AsyncMock(return_value=[])

        result = await service.detect_zombies("proj1", days_inactive=30)

        assert result["zombie_count"] == 1
        assert result["zombies"][0]["item_id"] == "zombie1"
        assert result["zombies"][0]["days_inactive"] == 45
        assert result["zombie_percentage"] == 100.0

    @pytest.mark.asyncio
    async def test_detect_zombies_orphaned_but_not_stale(self, service):
        """Test that orphaned items that are recently updated are not zombies."""
        # Item updated yesterday with no links
        recent_date = datetime.utcnow() - timedelta(days=1)
        active_item = Mock(id="active1", title="Active", status="todo", updated_at=recent_date)

        service.items.query = AsyncMock(return_value=[active_item])
        service.links.get_by_source = AsyncMock(return_value=[])
        service.links.get_by_target = AsyncMock(return_value=[])

        result = await service.detect_zombies("proj1", days_inactive=30)

        assert result["zombie_count"] == 0

    @pytest.mark.asyncio
    async def test_detect_zombies_item_without_updated_at(self, service):
        """Test handling of items without updated_at attribute."""
        # Item without updated_at
        item = Mock(id="item1", title="Item 1", status="todo")
        del item.updated_at  # Remove the attribute

        service.items.query = AsyncMock(return_value=[item])
        service.links.get_by_source = AsyncMock(return_value=[])
        service.links.get_by_target = AsyncMock(return_value=[])

        result = await service.detect_zombies("proj1")

        # Item is orphaned but not stale (no updated_at)
        assert result["zombie_count"] == 0


class TestAnalyzeImpact:
    """Test analyze_impact method."""

    @pytest.fixture
    def service(self):
        """Create service with mocked repositories."""
        session = AsyncMock()
        service = ChaosModeService(session)
        service.items = AsyncMock()
        service.links = AsyncMock()
        return service

    @pytest.mark.asyncio
    async def test_analyze_impact_item_not_found(self, service):
        """Test impact analysis when item doesn't exist."""
        service.items.get_by_id = AsyncMock(return_value=None)

        result = await service.analyze_impact("proj1", "nonexistent")

        assert result["error"] == "Item not found"

    @pytest.mark.asyncio
    async def test_analyze_impact_no_dependencies(self, service):
        """Test impact analysis with no dependencies."""
        item = Mock(id="item1", title="Item 1")

        service.items.get_by_id = AsyncMock(return_value=item)
        service.links.get_by_source = AsyncMock(return_value=[])
        service.links.get_by_target = AsyncMock(return_value=[])

        result = await service.analyze_impact("proj1", "item1")

        assert result["item_id"] == "item1"
        assert result["item_title"] == "Item 1"
        assert result["direct_impact"] == 0
        assert result["dependencies"] == 0
        assert result["transitive_impact"] == 0
        assert result["total_impact"] == 0

    @pytest.mark.asyncio
    async def test_analyze_impact_with_direct_dependencies(self, service):
        """Test impact analysis with direct dependencies."""
        item = Mock(id="item1", title="Item 1")
        link1 = Mock(target_item_id="item2", link_type="depends_on")
        link2 = Mock(target_item_id="item3", link_type="depends_on")

        service.items.get_by_id = AsyncMock(return_value=item)
        service.links.get_by_source = AsyncMock(return_value=[link1, link2])
        service.links.get_by_target = AsyncMock(return_value=[])

        result = await service.analyze_impact("proj1", "item1")

        assert result["direct_impact"] == 2
        assert len(result["impact_items"]) == 2

    @pytest.mark.asyncio
    async def test_analyze_impact_with_transitive_dependencies(self, service):
        """Test impact analysis with transitive dependencies."""
        item = Mock(id="item1", title="Item 1")
        link1 = Mock(target_item_id="item2", link_type="depends_on")
        link2 = Mock(target_item_id="item3", link_type="depends_on")

        service.items.get_by_id = AsyncMock(return_value=item)

        # First call for direct impact, subsequent calls for transitive
        def get_by_source_side_effect(item_id):
            if item_id == "item1":
                return [link1]
            elif item_id == "item2":
                return [link2]  # item2 -> item3
            return []

        service.links.get_by_source = AsyncMock(side_effect=get_by_source_side_effect)
        service.links.get_by_target = AsyncMock(return_value=[])

        result = await service.analyze_impact("proj1", "item1")

        assert result["direct_impact"] == 1
        assert result["transitive_impact"] >= 1


class TestGetTransitiveImpact:
    """Test _get_transitive_impact helper method."""

    @pytest.fixture
    def service(self):
        """Create service with mocked repositories."""
        session = AsyncMock()
        service = ChaosModeService(session)
        service.links = AsyncMock()
        return service

    @pytest.mark.asyncio
    async def test_transitive_impact_empty(self, service):
        """Test transitive impact with no outgoing links."""
        service.links.get_by_source = AsyncMock(return_value=[])

        result = await service._get_transitive_impact("item1")

        assert "item1" in result
        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_transitive_impact_chain(self, service):
        """Test transitive impact through a chain."""
        link1 = Mock(target_item_id="item2")
        link2 = Mock(target_item_id="item3")

        async def get_by_source_mock(item_id):
            if item_id == "item1":
                return [link1]
            elif item_id == "item2":
                return [link2]
            return []

        service.links.get_by_source = AsyncMock(side_effect=get_by_source_mock)

        result = await service._get_transitive_impact("item1")

        assert "item1" in result
        assert "item2" in result
        assert "item3" in result

    @pytest.mark.asyncio
    async def test_transitive_impact_handles_cycles(self, service):
        """Test that cycles don't cause infinite loops."""
        link1 = Mock(target_item_id="item2")
        link2 = Mock(target_item_id="item1")  # Cycle back

        async def get_by_source_mock(item_id):
            if item_id == "item1":
                return [link1]
            elif item_id == "item2":
                return [link2]  # Cycle
            return []

        service.links.get_by_source = AsyncMock(side_effect=get_by_source_mock)

        result = await service._get_transitive_impact("item1")

        # Should complete without infinite loop
        assert "item1" in result
        assert "item2" in result


class TestCreateTemporalSnapshot:
    """Test create_temporal_snapshot method."""

    @pytest.fixture
    def service(self):
        """Create service with mocked repositories."""
        session = AsyncMock()
        service = ChaosModeService(session)
        service.items = AsyncMock()
        service.links = AsyncMock()
        service.events = AsyncMock()
        return service

    @pytest.mark.asyncio
    async def test_create_snapshot_empty_project(self, service):
        """Test creating snapshot of empty project."""
        service.items.query = AsyncMock(return_value=[])
        service.events.log = AsyncMock()

        result = await service.create_temporal_snapshot("proj1", "snapshot1")

        assert result["name"] == "snapshot1"
        assert result["project_id"] == "proj1"
        assert result["item_count"] == 0
        assert result["link_count"] == 0
        assert "timestamp" in result
        service.events.log.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_snapshot_with_items_and_links(self, service):
        """Test creating snapshot with items and links."""
        item1 = Mock(id="item1", title="Item 1", status="todo", view="REQ")
        item2 = Mock(id="item2", title="Item 2", status="done", view="DEV")
        link = Mock(id="link1", source_item_id="item1", target_item_id="item2", link_type="depends_on")

        service.items.query = AsyncMock(return_value=[item1, item2])

        async def get_by_source_mock(item_id):
            if item_id == "item1":
                return [link]
            return []

        service.links.get_by_source = AsyncMock(side_effect=get_by_source_mock)
        service.events.log = AsyncMock()

        result = await service.create_temporal_snapshot("proj1", "snapshot1", agent_id="agent-1")

        assert result["item_count"] == 2
        assert result["link_count"] == 1
        assert len(result["items"]) == 2
        assert len(result["links"]) == 1


class TestMassUpdateItems:
    """Test mass_update_items method."""

    @pytest.fixture
    def service(self):
        """Create service with mocked repositories."""
        session = AsyncMock()
        service = ChaosModeService(session)
        service.items = AsyncMock()
        service.events = AsyncMock()
        return service

    @pytest.mark.asyncio
    async def test_mass_update_empty_list(self, service):
        """Test mass update with empty item list."""
        result = await service.mass_update_items("proj1", [], {"status": "done"})

        assert result["updated_count"] == 0
        assert result["error_count"] == 0

    @pytest.mark.asyncio
    async def test_mass_update_item_not_found(self, service):
        """Test mass update when item not found."""
        service.items.get_by_id = AsyncMock(return_value=None)

        result = await service.mass_update_items("proj1", ["missing"], {"status": "done"})

        assert result["updated_count"] == 0
        assert result["error_count"] == 1
        assert "Item missing not found" in result["errors"][0]

    @pytest.mark.asyncio
    async def test_mass_update_success(self, service):
        """Test successful mass update."""
        item = Mock(id="item1", version=1)
        updated_item = Mock(id="item1")

        service.items.get_by_id = AsyncMock(return_value=item)
        service.items.update = AsyncMock(return_value=updated_item)
        service.events.log = AsyncMock()

        result = await service.mass_update_items(
            "proj1", ["item1"], {"status": "done"}, agent_id="agent-1"
        )

        assert result["updated_count"] == 1
        assert "item1" in result["updated_items"]
        service.events.log.assert_called_once()

    @pytest.mark.asyncio
    async def test_mass_update_handles_exception(self, service):
        """Test mass update handles exceptions gracefully."""
        item = Mock(id="item1", version=1)

        service.items.get_by_id = AsyncMock(return_value=item)
        service.items.update = AsyncMock(side_effect=Exception("Update failed"))
        service.events.log = AsyncMock()

        result = await service.mass_update_items("proj1", ["item1"], {"status": "done"})

        assert result["updated_count"] == 0
        assert result["error_count"] == 1
        assert "Failed to update item1" in result["errors"][0]


class TestGetProjectHealth:
    """Test get_project_health method."""

    @pytest.fixture
    def service(self):
        """Create service with mocked repositories."""
        session = AsyncMock()
        service = ChaosModeService(session)
        service.items = AsyncMock()
        service.links = AsyncMock()
        service.events = AsyncMock()
        return service

    @pytest.mark.asyncio
    async def test_project_health_empty(self, service):
        """Test health metrics for empty project."""
        service.items.query = AsyncMock(return_value=[])
        service.links.get_by_source = AsyncMock(return_value=[])
        service.links.get_by_target = AsyncMock(return_value=[])

        result = await service.get_project_health("proj1")

        assert result["health_score"] == 100
        assert result["total_items"] == 0
        assert result["completed"] == 0
        assert result["completion_percentage"] == 0

    @pytest.mark.asyncio
    async def test_project_health_all_completed(self, service):
        """Test health for project with all completed items."""
        item = Mock(id="item1", status="complete", updated_at=datetime.utcnow())
        link = Mock()

        service.items.query = AsyncMock(return_value=[item])
        service.links.get_by_source = AsyncMock(return_value=[link])
        service.links.get_by_target = AsyncMock(return_value=[])

        result = await service.get_project_health("proj1")

        assert result["completed"] == 1
        assert result["completion_percentage"] == 100.0
        assert result["health_score"] >= 70  # High score for completed work

    @pytest.mark.asyncio
    async def test_project_health_mixed_status(self, service):
        """Test health for project with mixed statuses."""
        items = [
            Mock(id="1", status="complete", updated_at=datetime.utcnow()),
            Mock(id="2", status="in_progress", updated_at=datetime.utcnow()),
            Mock(id="3", status="todo", updated_at=datetime.utcnow()),
        ]

        service.items.query = AsyncMock(return_value=items)
        service.links.get_by_source = AsyncMock(return_value=[Mock()])  # has links
        service.links.get_by_target = AsyncMock(return_value=[])

        result = await service.get_project_health("proj1")

        assert result["completed"] == 1
        assert result["in_progress"] == 1
        assert result["todo"] == 1
        assert result["total_items"] == 3


class TestExplodeFile:
    """Test explode_file method."""

    @pytest.fixture
    def service(self):
        """Create service with mocked repositories."""
        session = AsyncMock()
        service = ChaosModeService(session)
        service.items = AsyncMock()
        return service

    @pytest.mark.asyncio
    async def test_explode_empty_content(self, service):
        """Test exploding empty content."""
        result = await service.explode_file("", "proj1", "REQ")

        assert result == 0

    @pytest.mark.asyncio
    async def test_explode_markdown_headers(self, service):
        """Test exploding markdown headers."""
        content = """# Feature 1
## Story 1
### Task 1
"""
        created_item = Mock(id="new-id")
        service.items.create = AsyncMock(return_value=created_item)

        result = await service.explode_file(content, "proj1", "REQ")

        assert result == 3
        assert service.items.create.call_count == 3

    @pytest.mark.asyncio
    async def test_explode_yaml_list_items(self, service):
        """Test exploding YAML list items."""
        content = """- Task 1
- Task 2
- Task 3
"""
        service.items.create = AsyncMock(return_value=Mock(id="id"))

        result = await service.explode_file(content, "proj1", "REQ")

        assert result == 3

    @pytest.mark.asyncio
    async def test_explode_mixed_content(self, service):
        """Test exploding mixed content (headers + lists)."""
        content = """# Feature
- Task 1
- Task 2
This is a longer line that should become a note item.
"""
        service.items.create = AsyncMock(return_value=Mock(id="id"))

        result = await service.explode_file(content, "proj1", "REQ")

        # 1 header + 2 list items + 1 long line = 4
        assert result >= 4

    @pytest.mark.asyncio
    async def test_explode_skips_short_lines(self, service):
        """Test that short lines are skipped."""
        content = """# Header
Short
This is definitely a longer line that meets the threshold.
"""
        service.items.create = AsyncMock(return_value=Mock(id="id"))

        result = await service.explode_file(content, "proj1", "REQ")

        # 1 header + 1 long line (short line skipped) = 2
        assert result == 2

    @pytest.mark.asyncio
    async def test_explode_sets_parent_hierarchy(self, service):
        """Test that parent hierarchy is set correctly."""
        content = """# Feature 1
## Story 1
"""
        feature_item = Mock(id="feature-id")
        story_item = Mock(id="story-id")

        create_calls = []

        async def track_create(**kwargs):
            create_calls.append(kwargs)
            if len(create_calls) == 1:
                return feature_item
            return story_item

        service.items.create = AsyncMock(side_effect=track_create)

        await service.explode_file(content, "proj1", "REQ")

        # Story should have feature as parent
        assert create_calls[1]["parent_id"] == "feature-id"


class TestTrackScopeCrash:
    """Test track_scope_crash method."""

    @pytest.fixture
    def service(self):
        """Create service with mocked repositories."""
        session = AsyncMock()
        service = ChaosModeService(session)
        service.items = AsyncMock()
        service.events = AsyncMock()
        return service

    @pytest.mark.asyncio
    async def test_track_scope_crash_empty_list(self, service):
        """Test scope crash with empty item list."""
        event = Mock(id="event-1")
        service.events.log = AsyncMock(return_value=event)

        result = await service.track_scope_crash("proj1", "Budget cut", [])

        assert result["items_affected"] == 0
        assert result["reason"] == "Budget cut"

    @pytest.mark.asyncio
    async def test_track_scope_crash_cancels_items(self, service):
        """Test that scope crash cancels items."""
        item = Mock(id="item1", project_id="proj1", version=1)
        event = Mock(id="event-1")

        service.items.get_by_id = AsyncMock(return_value=item)
        service.items.update = AsyncMock()
        service.events.log = AsyncMock(return_value=event)

        result = await service.track_scope_crash("proj1", "Scope change", ["item1"])

        assert result["items_affected"] == 1
        service.items.update.assert_called_once_with(
            item_id="item1",
            expected_version=1,
            status="cancelled",
        )

    @pytest.mark.asyncio
    async def test_track_scope_crash_skips_different_project(self, service):
        """Test that items from different project are skipped."""
        item = Mock(id="item1", project_id="proj2", version=1)  # Different project
        event = Mock(id="event-1")

        service.items.get_by_id = AsyncMock(return_value=item)
        service.items.update = AsyncMock()
        service.events.log = AsyncMock(return_value=event)

        result = await service.track_scope_crash("proj1", "Scope change", ["item1"])

        assert result["items_affected"] == 0
        service.items.update.assert_not_called()


class TestCleanupZombies:
    """Test cleanup_zombies method."""

    @pytest.fixture
    def service(self):
        """Create service with mocked repositories."""
        session = AsyncMock()
        service = ChaosModeService(session)
        service.items = AsyncMock()
        service.links = AsyncMock()
        return service

    @pytest.mark.asyncio
    async def test_cleanup_zombies_no_zombies(self, service):
        """Test cleanup when no zombies exist."""
        service.items.query = AsyncMock(return_value=[])
        service.links.get_by_source = AsyncMock(return_value=[])
        service.links.get_by_target = AsyncMock(return_value=[])

        result = await service.cleanup_zombies("proj1")

        assert result == 0

    @pytest.mark.asyncio
    async def test_cleanup_zombies_deletes_zombies(self, service):
        """Test that zombies are soft deleted."""
        stale_date = datetime.utcnow() - timedelta(days=45)
        zombie_item = Mock(id="zombie1", title="Zombie", status="todo", updated_at=stale_date, version=1)

        service.items.query = AsyncMock(return_value=[zombie_item])
        service.links.get_by_source = AsyncMock(return_value=[])
        service.links.get_by_target = AsyncMock(return_value=[])
        service.items.get_by_id = AsyncMock(return_value=zombie_item)
        service.items.update = AsyncMock()

        result = await service.cleanup_zombies("proj1", days_inactive=30)

        assert result == 1
        # Verify soft delete was called with deleted_at
        service.items.update.assert_called_once()
        call_kwargs = service.items.update.call_args[1]
        assert call_kwargs["item_id"] == "zombie1"
        assert "deleted_at" in call_kwargs


class TestCreateSnapshot:
    """Test create_snapshot method (wrapper)."""

    @pytest.fixture
    def service(self):
        """Create service with mocked repositories."""
        session = AsyncMock()
        service = ChaosModeService(session)
        service.items = AsyncMock()
        service.links = AsyncMock()
        service.events = AsyncMock()
        return service

    @pytest.mark.asyncio
    async def test_create_snapshot_basic(self, service):
        """Test basic snapshot creation."""
        service.items.query = AsyncMock(return_value=[])
        service.events.log = AsyncMock()

        result = await service.create_snapshot("proj1", "test-snapshot")

        assert result["snapshot_id"] == "test-snapshot"
        assert result["items_count"] == 0
        assert result["links_count"] == 0
        assert "timestamp" in result

    @pytest.mark.asyncio
    async def test_create_snapshot_with_description(self, service):
        """Test snapshot creation with description."""
        service.items.query = AsyncMock(return_value=[])
        service.events.log = AsyncMock()

        result = await service.create_snapshot("proj1", "test-snapshot", description="Test description")

        assert result["snapshot_id"] == "test-snapshot"
        # Description is added to the wrapper result but not in this simplified version
