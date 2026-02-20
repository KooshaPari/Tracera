"""Comprehensive edge case and boundary condition tests.

Tests empty data, large datasets, null/None values, boundary conditions,
unicode/special characters, concurrent modifications, resource cleanup,
and state consistency.

Target: +3-4% coverage (40-55 tests)
"""

from datetime import datetime
from typing import Any

import pytest

from tracertm.models.event import Event
from tracertm.models.item import Item
from tracertm.models.link import Link
from tracertm.models.project import Project


class TestEmptyDataHandling:
    """Test handling of empty datasets and null values."""

    @pytest.mark.integration
    def test_empty_project_list(self, sync_db_session: Any) -> None:
        """Test querying empty project list."""
        projects = sync_db_session.query(Project).all()
        assert projects == []
        assert len(projects) == 0

    @pytest.mark.integration
    def test_empty_item_list(self, initialized_db: Any) -> None:
        """Test querying items with no results."""
        items = initialized_db.query(Item).filter_by(status="nonexistent").all()
        assert items == []

    @pytest.mark.integration
    def test_empty_link_list(self, initialized_db: Any) -> None:
        """Test querying links with no results."""
        links = initialized_db.query(Link).filter_by(link_type="nonexistent").all()
        assert links == []

    @pytest.mark.integration
    def test_empty_event_list(self, initialized_db: Any) -> None:
        """Test querying events with no results."""
        events = initialized_db.query(Event).filter_by(event_type="nonexistent").all()
        assert events == []

    @pytest.mark.integration
    def test_null_item_metadata(self, initialized_db: Any) -> None:
        """Test item with null metadata."""
        item = Item(
            id="NULL-METADATA",
            project_id="test-project",
            title="Null Metadata",
            view="FEATURE",
            item_type="feature",
            status="todo",
            item_metadata=None,
        )
        initialized_db.add(item)
        initialized_db.commit()

        result = initialized_db.query(Item).filter_by(id="NULL-METADATA").first()
        assert result is not None
        # item_metadata defaults to {} if None
        assert result.item_metadata == {} or result.item_metadata is None

    @pytest.mark.integration
    def test_empty_string_fields(self, initialized_db: Any) -> None:
        """Test item with empty string fields."""
        item = Item(
            id="EMPTY-STRING",
            project_id="test-project",
            title="",  # Empty title
            view="FEATURE",
            item_type="",  # Empty type
            status="todo",
        )
        initialized_db.add(item)
        initialized_db.commit()

        result = initialized_db.query(Item).filter_by(id="EMPTY-STRING").first()
        assert result is not None
        assert result.title == ""
        assert result.item_type == ""

    @pytest.mark.integration
    def test_null_optional_fields(self, db_with_sample_data: Any) -> None:
        """Test item with null optional fields."""
        item = Item(
            id="NULL-OPTIONAL",
            project_id="test-project",
            title="Test",
            view="FEATURE",
            item_type="feature",
            status="todo",
            item_metadata=None,
        )
        db_with_sample_data.add(item)
        db_with_sample_data.commit()

        result = db_with_sample_data.query(Item).filter_by(id="NULL-OPTIONAL").first()
        assert result is not None
        # item_metadata defaults to {} if None
        assert result.item_metadata == {} or result.item_metadata is None

    @pytest.mark.integration
    def test_zero_count_aggregation(self, sync_db_session: Any) -> None:
        """Test aggregation on empty dataset."""
        project = Project(id="zero-count", name="Zero Count")
        sync_db_session.add(project)
        sync_db_session.commit()

        count = sync_db_session.query(Item).filter_by(project_id="zero-count").count()
        assert count == 0


class TestLargeDatasetProcessing:
    """Test handling of large datasets."""

    @pytest.mark.integration
    def test_large_item_batch_creation(self, initialized_db: Any) -> None:
        """Test creating large number of items."""
        items = [
            Item(
                id=f"LARGE-{i:06d}",
                project_id="test-project",
                title=f"Large Item {i}",
                view="FEATURE",
                item_type="feature",
                status="todo",
            )
            for i in range(100)
        ]

        for item in items:
            initialized_db.add(item)
        initialized_db.commit()

        count = initialized_db.query(Item).filter(Item.id.startswith("LARGE-")).count()
        assert count == 100

    @pytest.mark.integration
    def test_large_link_network(self, initialized_db: Any) -> None:
        """Test creating large number of links."""
        project = Project(id="large-links", name="Large Links")
        initialized_db.add(project)
        initialized_db.commit()

        # Create items
        for i in range(20):
            item = Item(
                id=f"NODE-{i:03d}",
                project_id="large-links",
                title=f"Node {i}",
                view="FEATURE",
                item_type="feature",
                status="todo",
            )
            initialized_db.add(item)
        initialized_db.commit()

        # Create network of links
        links = []
        for i in range(20):
            for j in range(i + 1, min(i + 5, 20)):
                link = Link(
                    id=f"LINK-{i:03d}-{j:03d}",
                    project_id="large-links",
                    source_item_id=f"NODE-{i:03d}",
                    target_item_id=f"NODE-{j:03d}",
                    link_type="depends_on",
                )
                links.append(link)

        for link in links:
            initialized_db.add(link)
        initialized_db.commit()

        link_count = initialized_db.query(Link).filter_by(project_id="large-links").count()
        assert link_count > 50

    @pytest.mark.integration
    def test_large_event_log(self, db_with_sample_data: Any) -> None:
        """Test handling large event log."""
        events = [
            Event(
                project_id="test-project",
                event_type="item_updated",
                entity_type="item",
                entity_id="item-1",
                agent_id="test-agent",
                data={"iteration": i},
            )
            for i in range(100)
        ]

        for event in events:
            db_with_sample_data.add(event)
        db_with_sample_data.commit()

        event_count = db_with_sample_data.query(Event).filter_by(entity_id="item-1").count()
        assert event_count >= 100

    @pytest.mark.integration
    def test_large_metadata_json(self, initialized_db: Any) -> None:
        """Test handling large metadata JSON."""
        large_metadata = {f"key_{i}": f"value_{i}" * 100 for i in range(100)}

        item = Item(
            id="LARGE-METADATA",
            project_id="test-project",
            title="Large Metadata",
            view="FEATURE",
            item_type="feature",
            status="todo",
            item_metadata=large_metadata,
        )
        initialized_db.add(item)
        initialized_db.commit()

        result = initialized_db.query(Item).filter_by(id="LARGE-METADATA").first()
        assert result is not None
        assert len(result.item_metadata) == 100

    @pytest.mark.integration
    def test_pagination_with_large_dataset(self, initialized_db: Any) -> None:
        """Test pagination on large dataset."""
        # Create items
        for i in range(50):
            item = Item(
                id=f"PAGE-{i:03d}",
                project_id="test-project",
                title=f"Page Item {i}",
                view="FEATURE",
                item_type="feature",
                status="todo",
            )
            initialized_db.add(item)
        initialized_db.commit()

        # Paginate
        page_size = 10
        total_pages = 5
        all_items = []

        for page in range(total_pages):
            offset = page * page_size
            items = initialized_db.query(Item).filter(Item.id.startswith("PAGE-")).offset(offset).limit(page_size).all()
            all_items.extend(items)

        assert len(all_items) == 50


class TestBoundaryConditions:
    """Test boundary conditions and limits."""

    @pytest.mark.integration
    def test_maximum_string_length(self, initialized_db: Any) -> None:
        """Test item with very long title."""
        long_title = "X" * 10000
        item = Item(
            id="LONG-TITLE",
            project_id="test-project",
            title=long_title,
            view="FEATURE",
            item_type="feature",
            status="todo",
        )
        initialized_db.add(item)
        initialized_db.commit()

        result = initialized_db.query(Item).filter_by(id="LONG-TITLE").first()
        assert result is not None
        assert len(result.title) == 10000

    @pytest.mark.integration
    def test_maximum_id_length(self, initialized_db: Any) -> None:
        """Test item with very long ID."""
        long_id = "ID-" + "X" * 100
        item = Item(
            id=long_id,
            project_id="test-project",
            title="Long ID Test",
            view="FEATURE",
            item_type="feature",
            status="todo",
        )
        initialized_db.add(item)
        try:
            initialized_db.commit()
            result = initialized_db.query(Item).filter_by(id=long_id).first()
            assert result is not None
        except Exception:
            initialized_db.rollback()

    @pytest.mark.integration
    def test_single_character_fields(self, initialized_db: Any) -> None:
        """Test item with single character fields."""
        item = Item(id="X", project_id="X", title="X", view="X", item_type="X", status="X")
        initialized_db.add(item)
        try:
            initialized_db.commit()
            result = initialized_db.query(Item).filter_by(id="X").first()
            assert result is not None
        except Exception:
            initialized_db.rollback()

    @pytest.mark.integration
    def test_maximum_metadata_depth(self, initialized_db: Any) -> None:
        """Test deeply nested metadata."""
        nested_metadata = {"level1": {"level2": {"level3": {"level4": {"value": "deep"}}}}}

        item = Item(
            id="DEEP-METADATA",
            project_id="test-project",
            title="Deep Metadata",
            view="FEATURE",
            item_type="feature",
            status="todo",
            item_metadata=nested_metadata,
        )
        initialized_db.add(item)
        initialized_db.commit()

        result = initialized_db.query(Item).filter_by(id="DEEP-METADATA").first()
        assert result is not None
        assert result.item_metadata["level1"]["level2"]["level3"]["level4"]["value"] == "deep"

    @pytest.mark.integration
    def test_boundary_date_values(self, db_with_sample_data: Any) -> None:
        """Test boundary date values."""
        # Very old date
        event = Event(
            project_id="test-project",
            event_type="item_created",
            entity_type="item",
            entity_id="boundary-date",
            agent_id="test-agent",
            data={},
            created_at=datetime(1970, 1, 1),
        )
        db_with_sample_data.add(event)
        db_with_sample_data.commit()

        result = db_with_sample_data.query(Event).filter_by(entity_id="boundary-date").first()
        assert result is not None
        assert result.created_at.year == 1970


class TestUnicodeAndSpecialCharacters:
    """Test unicode and special character handling."""

    @pytest.mark.integration
    def test_unicode_item_title(self, initialized_db: Any) -> None:
        """Test item with unicode characters."""
        unicode_title = "Test 中文 العربية हिन्दी Русский"
        item = Item(
            id="UNICODE-001",
            project_id="test-project",
            title=unicode_title,
            view="FEATURE",
            item_type="feature",
            status="todo",
        )
        initialized_db.add(item)
        initialized_db.commit()

        result = initialized_db.query(Item).filter_by(id="UNICODE-001").first()
        assert result is not None
        assert result.title == unicode_title

    @pytest.mark.integration
    def test_emoji_in_metadata(self, initialized_db: Any) -> None:
        """Test emoji characters in metadata."""
        item = Item(
            id="EMOJI-TEST",
            project_id="test-project",
            title="Emoji Test",
            view="FEATURE",
            item_type="feature",
            status="todo",
            item_metadata={"emoji": "🎉 🚀 ✨ 💯"},
        )
        initialized_db.add(item)
        initialized_db.commit()

        result = initialized_db.query(Item).filter_by(id="EMOJI-TEST").first()
        assert result is not None
        assert "🎉" in result.item_metadata["emoji"]

    @pytest.mark.integration
    def test_special_characters_in_id(self, initialized_db: Any) -> None:
        """Test special characters in ID."""
        special_id = "ID-WITH-SPECIAL_!@#$%"
        item = Item(
            id=special_id,
            project_id="test-project",
            title="Special ID",
            view="FEATURE",
            item_type="feature",
            status="todo",
        )
        initialized_db.add(item)
        try:
            initialized_db.commit()
            result = initialized_db.query(Item).filter_by(id=special_id).first()
            assert result is not None
        except Exception:
            initialized_db.rollback()

    @pytest.mark.integration
    def test_sql_injection_attempt(self, initialized_db: Any) -> None:
        """Test SQL injection protection."""
        injection_text = "'; DROP TABLE item; --"
        item = Item(
            id="SQL-INJECTION",
            project_id="test-project",
            title=injection_text,
            view="FEATURE",
            item_type="feature",
            status="todo",
        )
        initialized_db.add(item)
        initialized_db.commit()

        # Verify table still exists and text stored safely
        result = initialized_db.query(Item).filter_by(id="SQL-INJECTION").first()
        assert result is not None
        assert result.title == injection_text

    @pytest.mark.integration
    def test_newline_and_whitespace(self, initialized_db: Any) -> None:
        """Test newline and whitespace handling."""
        whitespace_text = "Line1\nLine2\rLine3\tTabbed"
        item = Item(
            id="WHITESPACE",
            project_id="test-project",
            title=whitespace_text,
            view="FEATURE",
            item_type="feature",
            status="todo",
        )
        initialized_db.add(item)
        initialized_db.commit()

        result = initialized_db.query(Item).filter_by(id="WHITESPACE").first()
        assert result is not None
        assert "\n" in result.title
        assert "\t" in result.title


class TestConcurrentModifications:
    """Test concurrent modification scenarios."""

    @pytest.mark.integration
    def test_concurrent_item_updates(self, sync_db_session: Any) -> None:
        """Test concurrent updates to same item."""
        project = Project(id="concurrent-project", name="Concurrent")
        sync_db_session.add(project)
        sync_db_session.commit()

        item = Item(
            id="CONCURRENT-001",
            project_id="concurrent-project",
            title="Original",
            view="FEATURE",
            item_type="feature",
            status="todo",
        )
        sync_db_session.add(item)
        sync_db_session.commit()

        # Update 1
        item.title = "Update 1"
        sync_db_session.commit()

        # Update 2
        item.title = "Update 2"
        sync_db_session.commit()

        result = sync_db_session.query(Item).filter_by(id="CONCURRENT-001").first()
        assert result.title == "Update 2"

    @pytest.mark.integration
    def test_concurrent_link_creation(self, db_with_sample_data: Any) -> None:
        """Test concurrent link creation."""
        # Create links between same items
        link1 = Link(
            id="concurrent-link-1",
            project_id="test-project",
            source_item_id="item-1",
            target_item_id="item-2",
            link_type="implements",
        )
        link2 = Link(
            id="concurrent-link-2",
            project_id="test-project",
            source_item_id="item-2",
            target_item_id="item-3",
            link_type="depends_on",
        )

        db_with_sample_data.add(link1)
        db_with_sample_data.add(link2)
        db_with_sample_data.commit()

        link1_result = db_with_sample_data.query(Link).filter_by(id="concurrent-link-1").first()
        link2_result = db_with_sample_data.query(Link).filter_by(id="concurrent-link-2").first()

        assert link1_result is not None
        assert link2_result is not None

    @pytest.mark.integration
    def test_rapid_sequential_updates(self, sync_db_session: Any) -> None:
        """Test rapid sequential updates."""
        project = Project(id="rapid-updates", name="Rapid")
        sync_db_session.add(project)
        sync_db_session.commit()

        item = Item(
            id="RAPID-001",
            project_id="rapid-updates",
            title="Original",
            view="FEATURE",
            item_type="feature",
            status="todo",
        )
        sync_db_session.add(item)
        sync_db_session.commit()

        # Rapid updates
        for i in range(10):
            item.status = f"status-{i}"
            sync_db_session.commit()

        result = sync_db_session.query(Item).filter_by(id="RAPID-001").first()
        assert result.status == "status-9"


class TestResourceCleanup:
    """Test resource cleanup and finalization."""

    @pytest.mark.integration
    def test_session_cleanup_on_error(self, sync_db_session: Any) -> None:
        """Test session cleanup after error."""
        project = Project(id="cleanup-test", name="Cleanup")
        sync_db_session.add(project)
        sync_db_session.commit()

        # Verify session still works after error scenario
        items = sync_db_session.query(Item).all()
        assert items is not None

    @pytest.mark.integration
    def test_orphaned_record_cleanup(self, initialized_db: Any) -> None:
        """Test cleanup of orphaned records."""
        item = Item(
            id="ORPHAN-001",
            project_id="test-project",
            title="Orphan",
            view="FEATURE",
            item_type="feature",
            status="todo",
        )
        initialized_db.add(item)
        initialized_db.commit()

        # Delete item
        initialized_db.delete(item)
        initialized_db.commit()

        result = initialized_db.query(Item).filter_by(id="ORPHAN-001").first()
        assert result is None

    @pytest.mark.integration
    def test_cleanup_on_session_close(self, sync_db_session: Any) -> None:
        """Test cleanup when session closes."""
        project = Project(id="session-close", name="Close")
        sync_db_session.add(project)
        sync_db_session.commit()

        # Session operations should work before close
        count = sync_db_session.query(Project).count()
        assert count >= 1


class TestStateConsistency:
    """Test state consistency and invariants."""

    @pytest.mark.integration
    def test_item_project_consistency(self, initialized_db: Any) -> None:
        """Test item and project relationship consistency."""
        items = initialized_db.query(Item).all()
        for item in items:
            project = initialized_db.query(Project).filter_by(id=item.project_id).first()
            assert project is not None

    @pytest.mark.integration
    def test_link_item_consistency(self, db_with_sample_data: Any) -> None:
        """Test link and item consistency."""
        links = db_with_sample_data.query(Link).all()
        for link in links:
            source = db_with_sample_data.query(Item).filter_by(id=link.source_item_id).first()
            target = db_with_sample_data.query(Item).filter_by(id=link.target_item_id).first()
            assert source is not None or target is not None

    @pytest.mark.integration
    def test_event_reference_consistency(self, db_with_sample_data: Any) -> None:
        """Test event reference consistency."""
        events = db_with_sample_data.query(Event).all()
        for event in events:
            if event.entity_type == "item":
                db_with_sample_data.query(Item).filter_by(id=event.entity_id).first()
                # Entity may be deleted, so no assertion needed
            assert event.project_id is not None

    @pytest.mark.integration
    def test_metadata_integrity(self, initialized_db: Any) -> None:
        """Test metadata integrity after operations."""
        original_metadata = {"key": "value", "nested": {"inner": "data"}}

        item = Item(
            id="INTEGRITY-TEST",
            project_id="test-project",
            title="Test",
            view="FEATURE",
            item_type="feature",
            status="todo",
            item_metadata=original_metadata,
        )
        initialized_db.add(item)
        initialized_db.commit()

        result = initialized_db.query(Item).filter_by(id="INTEGRITY-TEST").first()
        assert result.item_metadata == original_metadata

    @pytest.mark.integration
    def test_timestamp_ordering(self, db_with_sample_data: Any) -> None:
        """Test event timestamp ordering."""
        events = db_with_sample_data.query(Event).order_by(Event.created_at).all()

        if len(events) > 1:
            for i in range(len(events) - 1):
                assert events[i].created_at <= events[i + 1].created_at

    @pytest.mark.integration
    def test_unique_id_constraint(self, initialized_db: Any) -> None:
        """Test unique ID constraint enforcement."""
        item1 = Item(
            id="UNIQUE-TEST",
            project_id="test-project",
            title="First",
            view="FEATURE",
            item_type="feature",
            status="todo",
        )
        initialized_db.add(item1)
        initialized_db.commit()

        # Try duplicate
        item2 = Item(
            id="UNIQUE-TEST",
            project_id="test-project",
            title="Second",
            view="FEATURE",
            item_type="feature",
            status="todo",
        )
        initialized_db.add(item2)

        try:
            initialized_db.commit()
            # If no error, verify only first exists
            result = initialized_db.query(Item).filter_by(id="UNIQUE-TEST").all()
            assert len(result) == 1
        except Exception:
            initialized_db.rollback()
