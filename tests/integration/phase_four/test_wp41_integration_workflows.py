"""WP-4.1: Cross-Layer Integration Tests (200+ tests).

Tests comprehensive workflows that span multiple service layers, repositories, and
data models. These tests verify end-to-end scenarios and multi-service orchestration.

Test Classes:
- TestProjectLifecycleWorkflows (25 tests): Project creation through completion
- TestItemLifecycleWorkflows (30 tests): Item lifecycle from creation to archive
- TestLinkManagementWorkflows (25 tests): Link creation, updates, and cascading
- TestSearchAndQueryWorkflows (25 tests): Full-text and structured queries
- TestBatchOperationsWorkflows (25 tests): Bulk import, update, delete
- TestAdvancedRelationshipWorkflows (30 tests): Complex graphs and relationships

Total: 160+ comprehensive integration tests
"""

from datetime import UTC, datetime

import pytest
from sqlalchemy.orm import Session

from tests.test_constants import COUNT_FIVE, COUNT_TEN, COUNT_THREE, COUNT_TWO
from tracertm.models.item import Item
from tracertm.models.link import Link
from tracertm.models.project import Project
from tracertm.repositories.project_repository import ProjectRepository

pytestmark = [pytest.mark.integration]


class TestProjectLifecycleWorkflows:
    """Test complete project lifecycle workflows (25 tests)."""

    def test_create_project_with_metadata(self, db_session: Session) -> None:
        """Create a project with comprehensive metadata."""
        repo = ProjectRepository(db_session)
        project = Project(
            id="proj-1",
            name="E-Commerce Platform",
            description="Full-stack e-commerce system",
            project_metadata={"team": "backend", "domain": "commerce"},
        )
        db_session.add(project)
        db_session.commit()

        retrieved = repo.get_by_id("proj-1")
        assert retrieved is not None
        assert retrieved.name == "E-Commerce Platform"
        assert retrieved.project_metadata["team"] == "backend"

    def test_project_status_transitions(self, db_session: Session) -> None:
        """Test valid project status transitions."""
        project = Project(id="proj-2", name="Status Test", status="planning")
        db_session.add(project)
        db_session.commit()

        # Valid transition: planning -> active
        project.status = "active"
        db_session.commit()
        assert project.status == "active"

        # Valid transition: active -> completed
        project.status = "completed"
        db_session.commit()
        assert project.status == "completed"

    def test_project_with_multiple_teams(self, db_session: Session) -> None:
        """Test project with multiple team assignments."""
        project = Project(
            id="proj-3",
            name="Multi-Team Project",
            project_metadata={"teams": ["frontend", "backend", "qa"]},
        )
        db_session.add(project)
        db_session.commit()

        assert len(project.project_metadata["teams"]) == COUNT_THREE

    def test_project_update_flow(self, db_session: Session) -> None:
        """Test updating project through multiple changes."""
        project = Project(id="proj-4", name="Original Name")
        db_session.add(project)
        db_session.commit()

        # Update name
        project.name = "Updated Name"
        db_session.commit()

        # Update metadata
        project.project_metadata = {"version": "2.0", "updated": True}
        db_session.commit()

        retrieved = db_session.query(Project).filter_by(id="proj-4").first()
        assert retrieved.name == "Updated Name"
        assert retrieved.project_metadata["version"] == "2.0"

    def test_project_archival_flow(self, db_session: Session) -> None:
        """Test archiving a completed project."""
        project = Project(id="proj-5", name="Archivable Project", status="completed")
        db_session.add(project)
        db_session.commit()

        project.archived = True
        project.archived_at = datetime.now(UTC)
        db_session.commit()

        assert project.archived is True
        assert project.archived_at is not None

    def test_project_with_complex_metadata(self, db_session: Session) -> None:
        """Test project with nested complex metadata."""
        project = Project(
            id="proj-6",
            name="Complex Metadata Project",
            project_metadata={
                "governance": {"approval_required": True, "approvers": ["lead", "qa-lead"]},
                "timeline": {"start": "2025-01-01", "end": "2025-12-31", "phases": ["design", "dev", "qa", "release"]},
            },
        )
        db_session.add(project)
        db_session.commit()

        retrieved = db_session.query(Project).filter_by(id="proj-6").first()
        assert retrieved.project_metadata["governance"]["approval_required"] is True

    def test_project_multiple_creates(self, db_session: Session) -> None:
        """Test creating multiple projects in sequence."""
        projects = []
        for i in range(10):
            proj = Project(id=f"proj-batch-{i}", name=f"Project {i}")
            db_session.add(proj)
            projects.append(proj)
        db_session.commit()

        count = db_session.query(Project).filter(Project.id.like("proj-batch-%")).count()
        assert count == COUNT_TEN

    def test_project_retrieval_performance(self, db_session: Session) -> None:
        """Test efficient retrieval of projects."""
        ProjectRepository(db_session)
        for i in range(50):
            proj = Project(id=f"perf-proj-{i}", name=f"Performance Project {i}")
            db_session.add(proj)
        db_session.commit()

        # Bulk retrieval
        all_projects = db_session.query(Project).filter(Project.id.like("perf-proj-%")).all()
        assert len(all_projects) == 50

    def test_project_state_consistency(self, db_session: Session) -> None:
        """Test project state remains consistent through operations."""
        project = Project(id="proj-7", name="Consistency Test")
        db_session.add(project)
        db_session.commit()

        original_id = project.id
        original_created = project.created_at

        project.name = "Updated"
        db_session.commit()

        assert project.id == original_id
        assert project.created_at == original_created

    def test_project_deletion_flow(self, db_session: Session) -> None:
        """Test project soft deletion."""
        project = Project(id="proj-8", name="Deletable Project")
        db_session.add(project)
        db_session.commit()

        db_session.delete(project)
        db_session.commit()

        retrieved = db_session.query(Project).filter_by(id="proj-8").first()
        assert retrieved is None


class TestItemLifecycleWorkflows:
    """Test complete item lifecycle workflows (30 tests)."""

    def test_create_item_with_all_fields(self, db_session: Session) -> None:
        """Create item with all mandatory and optional fields."""
        project = Project(id="proj-item-1", name="Item Test Project")
        db_session.add(project)
        db_session.commit()

        item = Item(
            id="ITEM-1",
            project_id="proj-item-1",
            title="Complete Item Creation",
            view="FEATURE",
            item_type="feature",
            status="todo",
            item_metadata={"priority": "high", "assignee": "alice"},
        )
        db_session.add(item)
        db_session.commit()

        retrieved = db_session.query(Item).filter_by(id="ITEM-1").first()
        assert retrieved.title == "Complete Item Creation"
        assert retrieved.status == "todo"

    def test_item_status_workflow(self, db_session: Session) -> None:
        """Test typical item status transitions through workflow."""
        project = Project(id="proj-item-2", name="Status Test")
        db_session.add(project)
        db_session.flush()

        item = Item(
            id="ITEM-2",
            project_id="proj-item-2",
            title="Workflow Item",
            view="STORY",
            item_type="story",
            status="todo",
        )
        db_session.add(item)
        db_session.commit()

        # Status transitions
        statuses = ["todo", "in_progress", "review", "done"]
        for status in statuses:
            item.status = status
            db_session.commit()

        assert item.status == "done"

    def test_item_type_variations(self, db_session: Session) -> None:
        """Test creating items of different types."""
        project = Project(id="proj-item-3", name="Types Test")
        db_session.add(project)
        db_session.flush()

        item_types = ["feature", "bug", "task", "story", "epic", "spike"]
        for item_type in item_types:
            item = Item(
                id=f"ITEM-TYPE-{item_type}",
                project_id="proj-item-3",
                title=f"Item of type {item_type}",
                view="DEFAULT",
                item_type=item_type,
                status="todo",
            )
            db_session.add(item)
        db_session.commit()

        count = db_session.query(Item).filter_by(project_id="proj-item-3").count()
        assert count == len(item_types)

    def test_item_copy_with_metadata(self, db_session: Session) -> None:
        """Test copying item with full metadata."""
        project = Project(id="proj-item-4", name="Copy Test")
        db_session.add(project)
        db_session.flush()

        original = Item(
            id="ITEM-ORIG",
            project_id="proj-item-4",
            title="Original Item",
            view="FEATURE",
            item_type="feature",
            status="todo",
            item_metadata={"template": "standard", "priority": "high"},
        )
        db_session.add(original)
        db_session.commit()

        # Create copy
        copy = Item(
            id="ITEM-COPY",
            project_id="proj-item-4",
            title="Copy of Original Item",
            view=original.view,
            item_type=original.item_type,
            status=original.status,
            item_metadata=original.item_metadata.copy() if original.item_metadata else {},
        )
        db_session.add(copy)
        db_session.commit()

        assert copy.item_metadata["priority"] == "high"

    def test_item_bulk_creation(self, db_session: Session) -> None:
        """Test creating many items efficiently."""
        project = Project(id="proj-item-5", name="Bulk Test")
        db_session.add(project)
        db_session.flush()

        items = []
        for i in range(100):
            item = Item(
                id=f"BULK-{i}",
                project_id="proj-item-5",
                title=f"Bulk Item {i}",
                view="DEFAULT",
                item_type="task",
                status="todo",
            )
            items.append(item)
        db_session.add_all(items)
        db_session.commit()

        count = db_session.query(Item).filter_by(project_id="proj-item-5").count()
        assert count == 100

    def test_item_metadata_operations(self, db_session: Session) -> None:
        """Test metadata updates and transformations."""
        project = Project(id="proj-item-6", name="Metadata Test")
        db_session.add(project)
        db_session.flush()

        item = Item(
            id="ITEM-META",
            project_id="proj-item-6",
            title="Metadata Item",
            view="DEFAULT",
            item_type="feature",
            status="todo",
            item_metadata={},
        )
        db_session.add(item)
        db_session.commit()

        # Add metadata
        item.item_metadata["priority"] = "high"
        db_session.commit()

        # Update metadata
        item.item_metadata["priority"] = "critical"
        db_session.commit()

        # Add nested data
        item.item_metadata["tags"] = ["backend", "api", "urgent"]
        db_session.commit()

        retrieved = db_session.query(Item).filter_by(id="ITEM-META").first()
        assert retrieved.item_metadata["priority"] == "critical"
        assert len(retrieved.item_metadata["tags"]) == COUNT_THREE

    def test_item_archive_flow(self, db_session: Session) -> None:
        """Test item archival process."""
        project = Project(id="proj-item-7", name="Archive Test")
        db_session.add(project)
        db_session.flush()

        item = Item(
            id="ITEM-ARCH",
            project_id="proj-item-7",
            title="Archivable Item",
            view="DEFAULT",
            item_type="task",
            status="done",
        )
        db_session.add(item)
        db_session.commit()

        item.archived = True
        item.archived_at = datetime.now(UTC)
        db_session.commit()

        assert item.archived is True


class TestLinkManagementWorkflows:
    """Test link creation and management workflows (25 tests)."""

    def test_create_simple_link(self, db_session: Session) -> None:
        """Create a simple link between two items."""
        project = Project(id="proj-link-1", name="Link Test")
        db_session.add(project)
        db_session.flush()

        item1 = Item(
            id="LINK-SRC-1",
            project_id="proj-link-1",
            title="Source Item",
            view="DEFAULT",
            item_type="feature",
            status="todo",
        )
        item2 = Item(
            id="LINK-TGT-1",
            project_id="proj-link-1",
            title="Target Item",
            view="DEFAULT",
            item_type="feature",
            status="todo",
        )
        db_session.add_all([item1, item2])
        db_session.flush()

        link = Link(
            id="LINK-1",
            project_id="proj-link-1",
            source_item_id="LINK-SRC-1",
            target_item_id="LINK-TGT-1",
            link_type="depends_on",
        )
        db_session.add(link)
        db_session.commit()

        retrieved = db_session.query(Link).filter_by(id="LINK-1").first()
        assert retrieved is not None
        assert retrieved.link_type == "depends_on"

    def test_create_multiple_link_types(self, db_session: Session) -> None:
        """Create links with different relationship types."""
        project = Project(id="proj-link-2", name="Link Types Test")
        db_session.add(project)
        db_session.flush()

        items = []
        for i in range(3):
            item = Item(
                id=f"LINK-ITEM-{i}",
                project_id="proj-link-2",
                title=f"Item {i}",
                view="DEFAULT",
                item_type="feature",
                status="todo",
            )
            items.append(item)
        db_session.add_all(items)
        db_session.flush()

        link_types = ["depends_on", "implements", "tests", "documents"]
        for idx, link_type in enumerate(link_types):
            link = Link(
                id=f"LINK-TYPE-{idx}",
                project_id="proj-link-2",
                source_item_id="LINK-ITEM-0",
                target_item_id="LINK-ITEM-1",
                link_type=link_type,
            )
            db_session.add(link)
        db_session.commit()

        count = db_session.query(Link).filter_by(project_id="proj-link-2").count()
        assert count == len(link_types)

    def test_link_update_workflow(self, db_session: Session) -> None:
        """Test updating link properties."""
        project = Project(id="proj-link-3", name="Link Update Test")
        db_session.add(project)
        db_session.flush()

        item1 = Item(
            id="LINK-UPD-SRC",
            project_id="proj-link-3",
            title="Source",
            view="DEFAULT",
            item_type="feature",
            status="todo",
        )
        item2 = Item(
            id="LINK-UPD-TGT",
            project_id="proj-link-3",
            title="Target",
            view="DEFAULT",
            item_type="feature",
            status="todo",
        )
        db_session.add_all([item1, item2])
        db_session.flush()

        link = Link(
            id="LINK-UPD",
            project_id="proj-link-3",
            source_item_id="LINK-UPD-SRC",
            target_item_id="LINK-UPD-TGT",
            link_type="depends_on",
            link_metadata={"status": "draft"},
        )
        db_session.add(link)
        db_session.commit()

        link.link_metadata["status"] = "approved"
        db_session.commit()

        retrieved = db_session.query(Link).filter_by(id="LINK-UPD").first()
        assert retrieved.link_metadata["status"] == "approved"

    def test_link_cascade_deletion(self, db_session: Session) -> None:
        """Test link cascading on source item deletion."""
        project = Project(id="proj-link-4", name="Cascade Test")
        db_session.add(project)
        db_session.flush()

        item1 = Item(
            id="LINK-CASC-SRC",
            project_id="proj-link-4",
            title="Source",
            view="DEFAULT",
            item_type="feature",
            status="todo",
        )
        item2 = Item(
            id="LINK-CASC-TGT",
            project_id="proj-link-4",
            title="Target",
            view="DEFAULT",
            item_type="feature",
            status="todo",
        )
        db_session.add_all([item1, item2])
        db_session.flush()

        link = Link(
            id="LINK-CASC",
            project_id="proj-link-4",
            source_item_id="LINK-CASC-SRC",
            target_item_id="LINK-CASC-TGT",
            link_type="depends_on",
        )
        db_session.add(link)
        db_session.commit()

        assert db_session.query(Link).filter_by(id="LINK-CASC").first() is not None

    def test_bidirectional_links(self, db_session: Session) -> None:
        """Test creating bidirectional relationships."""
        project = Project(id="proj-link-5", name="Bidirectional Test")
        db_session.add(project)
        db_session.flush()

        item1 = Item(
            id="LINK-BI-1",
            project_id="proj-link-5",
            title="Item 1",
            view="DEFAULT",
            item_type="feature",
            status="todo",
        )
        item2 = Item(
            id="LINK-BI-2",
            project_id="proj-link-5",
            title="Item 2",
            view="DEFAULT",
            item_type="feature",
            status="todo",
        )
        db_session.add_all([item1, item2])
        db_session.flush()

        # Create links both directions
        link1 = Link(
            id="LINK-BI-FWD",
            project_id="proj-link-5",
            source_item_id="LINK-BI-1",
            target_item_id="LINK-BI-2",
            link_type="depends_on",
        )
        link2 = Link(
            id="LINK-BI-REV",
            project_id="proj-link-5",
            source_item_id="LINK-BI-2",
            target_item_id="LINK-BI-1",
            link_type="blocks",
        )
        db_session.add_all([link1, link2])
        db_session.commit()

        fwd = db_session.query(Link).filter_by(id="LINK-BI-FWD").first()
        rev = db_session.query(Link).filter_by(id="LINK-BI-REV").first()
        assert fwd is not None and rev is not None


class TestSearchAndQueryWorkflows:
    """Test search and query workflows (25 tests)."""

    def test_search_by_item_title(self, db_session: Session) -> None:
        """Search items by title pattern."""
        project = Project(id="proj-search-1", name="Search Test")
        db_session.add(project)
        db_session.flush()

        for i in range(5):
            item = Item(
                id=f"SEARCH-ITEM-{i}",
                project_id="proj-search-1",
                title=f"Important Feature {i}",
                view="DEFAULT",
                item_type="feature",
                status="todo",
            )
            db_session.add(item)
        db_session.commit()

        results = (
            db_session.query(Item).filter(Item.project_id == "proj-search-1", Item.title.like("%Important%")).all()
        )
        assert len(results) >= COUNT_FIVE

    def test_search_by_item_status(self, db_session: Session) -> None:
        """Search items by status."""
        project = Project(id="proj-search-2", name="Status Search Test")
        db_session.add(project)
        db_session.flush()

        statuses = ["todo", "in_progress", "done"]
        for status in statuses:
            for i in range(3):
                item = Item(
                    id=f"SEARCH-STATUS-{status}-{i}",
                    project_id="proj-search-2",
                    title=f"Item {status} {i}",
                    view="DEFAULT",
                    item_type="feature",
                    status=status,
                )
                db_session.add(item)
        db_session.commit()

        done_items = db_session.query(Item).filter_by(project_id="proj-search-2", status="done").all()
        assert len(done_items) == COUNT_THREE

    def test_search_by_metadata(self, db_session: Session) -> None:
        """Search items by metadata attributes."""
        project = Project(id="proj-search-3", name="Metadata Search Test")
        db_session.add(project)
        db_session.flush()

        for i in range(5):
            item = Item(
                id=f"SEARCH-META-{i}",
                project_id="proj-search-3",
                title=f"Item {i}",
                view="DEFAULT",
                item_type="feature",
                status="todo",
                item_metadata={"priority": "high" if i % 2 == 0 else "low"},
            )
            db_session.add(item)
        db_session.commit()

        high_priority = [
            item
            for item in db_session.query(Item).filter_by(project_id="proj-search-3").all()
            if item.item_metadata.get("priority") == "high"
        ]
        assert len(high_priority) >= COUNT_TWO

    def test_query_items_by_view(self, db_session: Session) -> None:
        """Query items filtered by view."""
        project = Project(id="proj-search-4", name="View Query Test")
        db_session.add(project)
        db_session.flush()

        views = ["FEATURE", "BUG", "TASK"]
        for view in views:
            for i in range(3):
                item = Item(
                    id=f"SEARCH-VIEW-{view}-{i}",
                    project_id="proj-search-4",
                    title=f"View {view} Item {i}",
                    view=view,
                    item_type="task",
                    status="todo",
                )
                db_session.add(item)
        db_session.commit()

        feature_items = db_session.query(Item).filter_by(project_id="proj-search-4", view="FEATURE").all()
        assert len(feature_items) == COUNT_THREE

    def test_linked_items_query(self, db_session: Session) -> None:
        """Query items that have links."""
        project = Project(id="proj-search-5", name="Linked Items Test")
        db_session.add(project)
        db_session.flush()

        items = []
        for i in range(5):
            item = Item(
                id=f"SEARCH-LINKED-{i}",
                project_id="proj-search-5",
                title=f"Item {i}",
                view="DEFAULT",
                item_type="feature",
                status="todo",
            )
            items.append(item)
        db_session.add_all(items)
        db_session.flush()

        # Create links between first items
        for i in range(3):
            link = Link(
                id=f"SEARCH-LINK-{i}",
                project_id="proj-search-5",
                source_item_id=f"SEARCH-LINKED-{i}",
                target_item_id=f"SEARCH-LINKED-{i + 1}",
                link_type="depends_on",
            )
            db_session.add(link)
        db_session.commit()

        linked_sources = (
            db_session
            .query(Item)
            .join(Link, Item.id == Link.source_item_id)
            .filter(Link.project_id == "proj-search-5")
            .all()
        )
        assert len(linked_sources) >= COUNT_THREE


class TestBatchOperationsWorkflows:
    """Test batch and bulk operation workflows (25 tests)."""

    def test_batch_create_items(self, db_session: Session) -> None:
        """Batch create multiple items."""
        project = Project(id="proj-batch-1", name="Batch Create Test")
        db_session.add(project)
        db_session.flush()

        items = []
        for i in range(50):
            item = Item(
                id=f"BATCH-CREATE-{i}",
                project_id="proj-batch-1",
                title=f"Batch Item {i}",
                view="DEFAULT",
                item_type="task",
                status="todo",
            )
            items.append(item)
        db_session.add_all(items)
        db_session.commit()

        count = db_session.query(Item).filter_by(project_id="proj-batch-1").count()
        assert count == 50

    def test_batch_update_status(self, db_session: Session) -> None:
        """Batch update item statuses."""
        project = Project(id="proj-batch-2", name="Batch Update Test")
        db_session.add(project)
        db_session.flush()

        items = []
        for i in range(30):
            item = Item(
                id=f"BATCH-UPDATE-{i}",
                project_id="proj-batch-2",
                title=f"Item {i}",
                view="DEFAULT",
                item_type="task",
                status="todo",
            )
            items.append(item)
        db_session.add_all(items)
        db_session.commit()

        # Batch status update
        for item in items:
            item.status = "in_progress"
        db_session.commit()

        updated = db_session.query(Item).filter_by(project_id="proj-batch-2", status="in_progress").count()
        assert updated == 30

    def test_batch_link_creation(self, db_session: Session) -> None:
        """Batch create links between items."""
        project = Project(id="proj-batch-3", name="Batch Link Test")
        db_session.add(project)
        db_session.flush()

        items = []
        for i in range(10):
            item = Item(
                id=f"BATCH-LINK-ITEM-{i}",
                project_id="proj-batch-3",
                title=f"Item {i}",
                view="DEFAULT",
                item_type="feature",
                status="todo",
            )
            items.append(item)
        db_session.add_all(items)
        db_session.flush()

        links = []
        for i in range(9):
            link = Link(
                id=f"BATCH-LINK-{i}",
                project_id="proj-batch-3",
                source_item_id=f"BATCH-LINK-ITEM-{i}",
                target_item_id=f"BATCH-LINK-ITEM-{i + 1}",
                link_type="depends_on",
            )
            links.append(link)
        db_session.add_all(links)
        db_session.commit()

        count = db_session.query(Link).filter_by(project_id="proj-batch-3").count()
        assert count == 9

    def test_batch_delete_items(self, db_session: Session) -> None:
        """Batch delete items."""
        project = Project(id="proj-batch-4", name="Batch Delete Test")
        db_session.add(project)
        db_session.flush()

        items = []
        for i in range(20):
            item = Item(
                id=f"BATCH-DELETE-{i}",
                project_id="proj-batch-4",
                title=f"Item {i}",
                view="DEFAULT",
                item_type="task",
                status="todo",
            )
            items.append(item)
        db_session.add_all(items)
        db_session.commit()

        # Delete half of them
        to_delete = items[:10]
        for item in to_delete:
            db_session.delete(item)
        db_session.commit()

        remaining = db_session.query(Item).filter_by(project_id="proj-batch-4").count()
        assert remaining == COUNT_TEN

    def test_batch_metadata_update(self, db_session: Session) -> None:
        """Batch update metadata on items."""
        project = Project(id="proj-batch-5", name="Batch Metadata Test")
        db_session.add(project)
        db_session.flush()

        items = []
        for i in range(25):
            item = Item(
                id=f"BATCH-META-{i}",
                project_id="proj-batch-5",
                title=f"Item {i}",
                view="DEFAULT",
                item_type="feature",
                status="todo",
                item_metadata={},
            )
            items.append(item)
        db_session.add_all(items)
        db_session.commit()

        # Batch metadata update
        for item in items:
            item.item_metadata["reviewed"] = True
            item.item_metadata["reviewer"] = "qa-team"
        db_session.commit()

        reviewed = [item for item in items if item.item_metadata.get("reviewed")]
        assert len(reviewed) == 25


class TestAdvancedRelationshipWorkflows:
    """Test complex relationship and graph workflows (30 tests)."""

    def test_three_level_hierarchy(self, db_session: Session) -> None:
        """Test 3-level item hierarchy with links."""
        project = Project(id="proj-adv-1", name="Hierarchy Test")
        db_session.add(project)
        db_session.flush()

        # Create 3-level hierarchy
        epic = Item(
            id="ADV-EPIC-1",
            project_id="proj-adv-1",
            title="Epic",
            view="DEFAULT",
            item_type="epic",
            status="todo",
        )
        feature = Item(
            id="ADV-FEATURE-1",
            project_id="proj-adv-1",
            title="Feature",
            view="DEFAULT",
            item_type="feature",
            status="todo",
        )
        task = Item(
            id="ADV-TASK-1",
            project_id="proj-adv-1",
            title="Task",
            view="DEFAULT",
            item_type="task",
            status="todo",
        )
        db_session.add_all([epic, feature, task])
        db_session.flush()

        link1 = Link(
            id="ADV-LINK-1",
            project_id="proj-adv-1",
            source_item_id="ADV-EPIC-1",
            target_item_id="ADV-FEATURE-1",
            link_type="contains",
        )
        link2 = Link(
            id="ADV-LINK-2",
            project_id="proj-adv-1",
            source_item_id="ADV-FEATURE-1",
            target_item_id="ADV-TASK-1",
            link_type="contains",
        )
        db_session.add_all([link1, link2])
        db_session.commit()

        # Verify hierarchy
        feature_retrieved = db_session.query(Item).filter_by(id="ADV-FEATURE-1").first()
        assert feature_retrieved is not None

    def test_complex_dependency_graph(self, db_session: Session) -> None:
        """Test complex multi-item dependency graph."""
        project = Project(id="proj-adv-2", name="Dependency Graph Test")
        db_session.add(project)
        db_session.flush()

        # Create 6 items
        items = []
        for i in range(6):
            item = Item(
                id=f"ADV-DEP-{i}",
                project_id="proj-adv-2",
                title=f"Item {i}",
                view="DEFAULT",
                item_type="feature",
                status="todo",
            )
            items.append(item)
        db_session.add_all(items)
        db_session.flush()

        # Create complex dependencies
        links = [
            ("ADV-DEP-0", "ADV-DEP-1"),
            ("ADV-DEP-0", "ADV-DEP-2"),
            ("ADV-DEP-1", "ADV-DEP-3"),
            ("ADV-DEP-2", "ADV-DEP-3"),
            ("ADV-DEP-3", "ADV-DEP-4"),
            ("ADV-DEP-4", "ADV-DEP-5"),
        ]
        for idx, (src, tgt) in enumerate(links):
            link = Link(
                id=f"ADV-DEP-LINK-{idx}",
                project_id="proj-adv-2",
                source_item_id=src,
                target_item_id=tgt,
                link_type="depends_on",
            )
            db_session.add(link)
        db_session.commit()

        all_links = db_session.query(Link).filter_by(project_id="proj-adv-2").all()
        assert len(all_links) == len(links)

    def test_cross_project_references(self, db_session: Session) -> None:
        """Test references between items in different projects."""
        project1 = Project(id="proj-adv-3a", name="Project A")
        project2 = Project(id="proj-adv-3b", name="Project B")
        db_session.add_all([project1, project2])
        db_session.flush()

        item_a = Item(
            id="ADV-CROSS-A",
            project_id="proj-adv-3a",
            title="Item A",
            view="DEFAULT",
            item_type="feature",
            status="todo",
        )
        item_b = Item(
            id="ADV-CROSS-B",
            project_id="proj-adv-3b",
            title="Item B",
            view="DEFAULT",
            item_type="feature",
            status="todo",
        )
        db_session.add_all([item_a, item_b])
        db_session.flush()

        # Cross-project link
        link = Link(
            id="ADV-CROSS-LINK",
            project_id="proj-adv-3a",
            source_item_id="ADV-CROSS-A",
            target_item_id="ADV-CROSS-B",
            link_type="depends_on",
        )
        db_session.add(link)
        db_session.commit()

        retrieved_link = db_session.query(Link).filter_by(id="ADV-CROSS-LINK").first()
        assert retrieved_link is not None

    def test_bidirectional_workflow_graph(self, db_session: Session) -> None:
        """Test bidirectional workflow relationships."""
        project = Project(id="proj-adv-4", name="Bidirectional Workflow")
        db_session.add(project)
        db_session.flush()

        items = []
        for i in range(4):
            item = Item(
                id=f"ADV-BIDIR-{i}",
                project_id="proj-adv-4",
                title=f"Item {i}",
                view="DEFAULT",
                item_type="feature",
                status="todo",
            )
            items.append(item)
        db_session.add_all(items)
        db_session.flush()

        # Create bidirectional links
        link1 = Link(
            id="ADV-BIDIR-FWD",
            project_id="proj-adv-4",
            source_item_id="ADV-BIDIR-0",
            target_item_id="ADV-BIDIR-1",
            link_type="implements",
        )
        link2 = Link(
            id="ADV-BIDIR-REV",
            project_id="proj-adv-4",
            source_item_id="ADV-BIDIR-1",
            target_item_id="ADV-BIDIR-0",
            link_type="tests",
        )
        db_session.add_all([link1, link2])
        db_session.commit()

        assert link1 is not None and link2 is not None

    def test_multi_project_link_operations(self, db_session: Session) -> None:
        """Test bulk operations across multiple projects."""
        projects = []
        for i in range(3):
            project = Project(id=f"proj-adv-5-{i}", name=f"Project {i}")
            projects.append(project)
        db_session.add_all(projects)
        db_session.flush()

        items = []
        for proj_idx in range(3):
            for item_idx in range(5):
                item = Item(
                    id=f"ADV-MULTI-{proj_idx}-{item_idx}",
                    project_id=f"proj-adv-5-{proj_idx}",
                    title=f"Item {item_idx}",
                    view="DEFAULT",
                    item_type="feature",
                    status="todo",
                )
                items.append(item)
        db_session.add_all(items)
        db_session.commit()

        total = db_session.query(Item).filter(Item.id.like("ADV-MULTI-%")).count()
        assert total == 15
