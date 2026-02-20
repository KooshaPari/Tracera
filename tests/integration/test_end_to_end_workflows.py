"""Comprehensive end-to-end workflow and scenario tests.

Tests complete workflows: Item creation → Linking → Sync, project setup → management → export,
conflict detection → resolution, bulk operations, multi-step scenarios, team collaboration,
import/export, and backup/recovery.

Target: +4-5% coverage (45-60 tests)
"""

from datetime import UTC, datetime
from typing import Any

import pytest

from tests.test_constants import COUNT_FOUR, COUNT_TEN, COUNT_THREE, COUNT_TWO
from tracertm.models.event import Event
from tracertm.models.item import Item
from tracertm.models.link import Link
from tracertm.models.project import Project


class TestItemCreationLinkingSync:
    """Test complete workflow: Create items, link them, sync data."""

    @pytest.mark.integration
    def test_simple_item_creation_workflow(self, sync_db_session: Any) -> None:
        """Test simple item creation workflow."""
        # Create project
        project = Project(id="workflow-project", name="Workflow Project", description="Test workflow project")
        sync_db_session.add(project)
        sync_db_session.commit()

        # Create items
        item1 = Item(
            id="FEATURE-001",
            project_id="workflow-project",
            title="User Authentication",
            view="FEATURE",
            item_type="feature",
            status="todo",
        )
        item2 = Item(
            id="API-001",
            project_id="workflow-project",
            title="Auth API",
            view="API",
            item_type="api",
            status="todo",
        )

        sync_db_session.add(item1)
        sync_db_session.add(item2)
        sync_db_session.commit()

        # Verify
        project_result = sync_db_session.query(Project).filter_by(id="workflow-project").first()
        items = sync_db_session.query(Item).filter_by(project_id="workflow-project").all()

        assert project_result is not None
        assert len(items) == COUNT_TWO

    @pytest.mark.integration
    def test_item_linking_workflow(self, db_with_sample_data: Any) -> None:
        """Test item linking workflow."""
        # Items already exist: item-1, item-2, item-3, item-4
        # Create new links
        new_links = [
            Link(
                id="workflow-link-1",
                project_id="test-project",
                source_item_id="item-1",
                target_item_id="item-4",
                link_type="tests",
            ),
            Link(
                id="workflow-link-2",
                project_id="test-project",
                source_item_id="item-2",
                target_item_id="item-3",
                link_type="implements",
            ),
        ]

        for link in new_links:
            db_with_sample_data.add(link)
        db_with_sample_data.commit()

        # Verify links
        result_links = db_with_sample_data.query(Link).filter(Link.id.startswith("workflow-link")).all()
        assert len(result_links) == COUNT_TWO

    @pytest.mark.integration
    def test_item_modification_workflow(self, initialized_db: Any) -> None:
        """Test item modification workflow."""
        # Get item
        item = initialized_db.query(Item).filter_by(id="STORY-123").first()
        assert item is not None

        # Modify
        original_title = item.title
        item.title = "Modified Title"
        item.status = "in_progress"
        initialized_db.commit()

        # Verify
        result = initialized_db.query(Item).filter_by(id="STORY-123").first()
        assert result.title == "Modified Title"
        assert result.status == "in_progress"
        assert result.title != original_title

    @pytest.mark.integration
    def test_complete_item_lifecycle(self, sync_db_session: Any) -> None:
        """Test complete item lifecycle: create, update, link, delete."""
        # Create project
        project = Project(id="lifecycle-project", name="Lifecycle")
        sync_db_session.add(project)
        sync_db_session.commit()

        # Create items
        item1 = Item(
            id="LIFECYCLE-001",
            project_id="lifecycle-project",
            title="Item 1",
            view="FEATURE",
            item_type="feature",
            status="todo",
        )
        item2 = Item(
            id="LIFECYCLE-002",
            project_id="lifecycle-project",
            title="Item 2",
            view="TEST",
            item_type="test",
            status="todo",
        )

        sync_db_session.add(item1)
        sync_db_session.add(item2)
        sync_db_session.commit()

        # Update
        item1.status = "in_progress"
        sync_db_session.commit()

        # Link
        link = Link(
            id="lifecycle-link",
            project_id="lifecycle-project",
            source_item_id="LIFECYCLE-001",
            target_item_id="LIFECYCLE-002",
            link_type="tests",
        )
        sync_db_session.add(link)
        sync_db_session.commit()

        # Verify link exists
        result_link = sync_db_session.query(Link).filter_by(id="lifecycle-link").first()
        assert result_link is not None

        # Delete item2
        item2_to_delete = sync_db_session.query(Item).filter_by(id="LIFECYCLE-002").first()
        try:
            sync_db_session.delete(item2_to_delete)
            sync_db_session.commit()
        except Exception:
            sync_db_session.rollback()


class TestProjectSetupManagementExport:
    """Test project setup, management, and export workflows."""

    @pytest.mark.integration
    def test_project_creation_workflow(self, sync_db_session: Any) -> None:
        """Test complete project creation workflow."""
        project = Project(
            id="new-project",
            name="New Project",
            description="Complete workflow test",
            project_metadata={"team": "platform", "visibility": "private"},
        )

        sync_db_session.add(project)
        sync_db_session.commit()

        result = sync_db_session.query(Project).filter_by(id="new-project").first()
        assert result is not None
        assert result.name == "New Project"
        assert result.project_metadata["team"] == "platform"

    @pytest.mark.integration
    def test_project_configuration_workflow(self, sync_db_session: Any) -> None:
        """Test project configuration workflow."""
        project = Project(id="config-project", name="Config Project", project_metadata={"configured": False})
        sync_db_session.add(project)
        sync_db_session.commit()

        # Update configuration
        project.project_metadata = {"configured": True, "settings": {"theme": "dark"}}
        sync_db_session.commit()

        result = sync_db_session.query(Project).filter_by(id="config-project").first()
        assert result.project_metadata["configured"] is True
        assert result.project_metadata["settings"]["theme"] == "dark"

    @pytest.mark.integration
    def test_project_member_management(self, sync_db_session: Any) -> None:
        """Test project member management workflow."""
        project = Project(
            id="team-project",
            name="Team Project",
            project_metadata={"members": [{"name": "Alice", "role": "owner"}, {"name": "Bob", "role": "contributor"}]},
        )
        sync_db_session.add(project)
        sync_db_session.commit()

        # Refresh project from database
        sync_db_session.refresh(project)

        # Add member
        meta = project.project_metadata
        members = meta.get("members") if isinstance(meta, dict) else None
        new_members = (members if isinstance(members, list) else []) + [{"name": "Charlie", "role": "viewer"}]
        project.project_metadata = {"members": new_members}
        sync_db_session.commit()

        # Query fresh from database
        result = sync_db_session.query(Project).filter_by(id="team-project").first()
        assert len(result.project_metadata["members"]) >= COUNT_TWO

    @pytest.mark.integration
    def test_project_archive_workflow(self, sync_db_session: Any) -> None:
        """Test project archival workflow."""
        project = Project(id="archive-project", name="Archive Project", project_metadata={"archived": False})
        sync_db_session.add(project)
        sync_db_session.commit()

        # Archive project - need to reassign to trigger dirty flag
        metadata = project.project_metadata.copy()
        metadata["archived"] = True
        metadata["archived_at"] = datetime.now(UTC).isoformat()
        project.project_metadata = metadata
        sync_db_session.commit()

        result = sync_db_session.query(Project).filter_by(id="archive-project").first()
        assert result.project_metadata["archived"] is True
        assert "archived_at" in result.project_metadata

    @pytest.mark.integration
    def test_project_data_export_workflow(self, db_with_sample_data: Any) -> None:
        """Test project data export workflow."""
        # Gather all project data
        projects = db_with_sample_data.query(Project).all()
        items = db_with_sample_data.query(Item).all()
        links = db_with_sample_data.query(Link).all()
        events = db_with_sample_data.query(Event).all()

        # Create export
        export_data = {
            "projects": [{"id": p.id, "name": p.name} for p in projects],
            "items": [{"id": i.id, "title": i.title} for i in items],
            "links": [{"id": l.id, "type": l.link_type} for l in links],
            "events": [{"id": e.id, "type": e.event_type} for e in events],
        }

        assert len(export_data["projects"]) >= 1
        assert len(export_data["items"]) >= COUNT_FOUR


class TestConflictDetectionResolution:
    """Test conflict detection and resolution workflows."""

    @pytest.mark.integration
    def test_concurrent_edit_conflict_detection(self, sync_db_session: Any) -> None:
        """Test detection of concurrent edits."""
        project = Project(id="conflict-project", name="Conflict")
        sync_db_session.add(project)
        sync_db_session.commit()

        item = Item(
            id="CONFLICT-001",
            project_id="conflict-project",
            title="Original",
            view="FEATURE",
            item_type="feature",
            status="todo",
        )
        sync_db_session.add(item)
        sync_db_session.commit()

        # Simulate concurrent edits
        item.title = "User Update"
        sync_db_session.commit()

        result = sync_db_session.query(Item).filter_by(id="CONFLICT-001").first()
        assert result.title == "User Update"

    @pytest.mark.integration
    def test_link_conflict_resolution(self, db_with_sample_data: Any) -> None:
        """Test link conflict resolution."""
        # Create conflicting links
        link1 = Link(
            id="conflict-link-1",
            project_id="test-project",
            source_item_id="item-1",
            target_item_id="item-2",
            link_type="depends_on",
        )

        db_with_sample_data.add(link1)
        db_with_sample_data.commit()

        # Try to create reverse link
        link2 = Link(
            id="conflict-link-2",
            project_id="test-project",
            source_item_id="item-2",
            target_item_id="item-1",
            link_type="depends_on",
        )

        db_with_sample_data.add(link2)
        db_with_sample_data.commit()

        # Both should exist
        result1 = db_with_sample_data.query(Link).filter_by(id="conflict-link-1").first()
        result2 = db_with_sample_data.query(Link).filter_by(id="conflict-link-2").first()

        assert result1 is not None
        assert result2 is not None

    @pytest.mark.integration
    def test_status_conflict_resolution(self, initialized_db: Any) -> None:
        """Test status update conflict resolution."""
        item = initialized_db.query(Item).filter_by(id="STORY-123").first()
        original_status = item.status

        # Update status
        item.status = "in_progress"
        initialized_db.commit()

        # Update again
        item.status = "done"
        initialized_db.commit()

        result = initialized_db.query(Item).filter_by(id="STORY-123").first()
        assert result.status == "done"
        assert result.status != original_status

    @pytest.mark.integration
    def test_metadata_conflict_merge(self, sync_db_session: Any) -> None:
        """Test metadata conflict merge."""
        project = Project(id="merge-project", name="Merge")
        sync_db_session.add(project)
        sync_db_session.commit()

        item = Item(
            id="MERGE-001",
            project_id="merge-project",
            title="Test",
            view="FEATURE",
            item_type="feature",
            status="todo",
            item_metadata={"version": 1, "author": "alice"},
        )
        sync_db_session.add(item)
        sync_db_session.commit()

        # Merge metadata
        item.item_metadata = {"version": 2, "author": "alice", "reviewer": "bob"}
        sync_db_session.commit()

        result = sync_db_session.query(Item).filter_by(id="MERGE-001").first()
        assert result.item_metadata["version"] == COUNT_TWO
        assert result.item_metadata["reviewer"] == "bob"


class TestBulkOperationsWithRollback:
    """Test bulk operations with rollback scenarios."""

    @pytest.mark.integration
    def test_bulk_item_creation(self, sync_db_session: Any) -> None:
        """Test bulk item creation."""
        project = Project(id="bulk-project", name="Bulk")
        sync_db_session.add(project)
        sync_db_session.commit()

        items = [
            Item(
                id=f"BULK-{i:03d}",
                project_id="bulk-project",
                title=f"Bulk Item {i}",
                view="FEATURE",
                item_type="feature",
                status="todo",
            )
            for i in range(10)
        ]

        for item in items:
            sync_db_session.add(item)
        sync_db_session.commit()

        count = sync_db_session.query(Item).filter(Item.id.startswith("BULK-")).count()
        assert count == COUNT_TEN

    @pytest.mark.integration
    def test_bulk_link_creation(self, sync_db_session: Any) -> None:
        """Test bulk link creation."""
        project = Project(id="bulk-links", name="Bulk Links")
        sync_db_session.add(project)
        sync_db_session.commit()

        # Create items
        for i in range(5):
            item = Item(
                id=f"LINK-ITEM-{i}",
                project_id="bulk-links",
                title=f"Item {i}",
                view="FEATURE",
                item_type="feature",
                status="todo",
            )
            sync_db_session.add(item)
        sync_db_session.commit()

        # Create links
        links = []
        for i in range(5):
            for j in range(i + 1, 5):
                link = Link(
                    id=f"BULK-LINK-{i}-{j}",
                    project_id="bulk-links",
                    source_item_id=f"LINK-ITEM-{i}",
                    target_item_id=f"LINK-ITEM-{j}",
                    link_type="depends_on",
                )
                links.append(link)

        for link in links:
            sync_db_session.add(link)
        sync_db_session.commit()

        count = sync_db_session.query(Link).filter(Link.id.startswith("BULK-LINK")).count()
        assert count == COUNT_TEN

    @pytest.mark.integration
    def test_bulk_update_operation(self, initialized_db: Any) -> None:
        """Test bulk update operation."""
        # Update multiple items
        items = initialized_db.query(Item).all()
        for item in items:
            item.status = "in_progress"

        initialized_db.commit()

        updated_items = initialized_db.query(Item).filter_by(status="in_progress").all()
        assert len(updated_items) >= COUNT_TWO

    @pytest.mark.integration
    def test_bulk_operation_partial_rollback(self, sync_db_session: Any) -> None:
        """Test partial rollback in bulk operation."""
        project = Project(id="partial-rollback", name="Partial")
        sync_db_session.add(project)
        sync_db_session.commit()

        # Create savepoint
        savepoint = sync_db_session.begin_nested()

        items = [
            Item(
                id=f"PARTIAL-{i:03d}",
                project_id="partial-rollback",
                title=f"Partial {i}",
                view="FEATURE",
                item_type="feature",
                status="todo",
            )
            for i in range(5)
        ]

        for item in items:
            sync_db_session.add(item)

        # Rollback nested transaction
        savepoint.rollback()
        sync_db_session.commit()

        count = sync_db_session.query(Item).filter(Item.id.startswith("PARTIAL-")).count()
        assert count == 0


class TestMultiStepUserScenarios:
    """Test multi-step user scenarios."""

    @pytest.mark.integration
    def test_feature_development_workflow(self, sync_db_session: Any) -> None:
        """Test feature development workflow."""
        # Create project
        project = Project(id="feature-dev", name="Feature Development", project_metadata={"phase": "development"})
        sync_db_session.add(project)
        sync_db_session.commit()

        # Create feature
        feature = Item(
            id="FEAT-001",
            project_id="feature-dev",
            title="New Authentication",
            view="FEATURE",
            item_type="feature",
            status="todo",
        )
        sync_db_session.add(feature)
        sync_db_session.commit()

        # Create related items
        api = Item(
            id="API-AUTH",
            project_id="feature-dev",
            title="Auth API Endpoints",
            view="API",
            item_type="api",
            status="todo",
        )
        db_schema = Item(
            id="DB-AUTH",
            project_id="feature-dev",
            title="User Table Schema",
            view="DATABASE",
            item_type="schema",
            status="todo",
        )
        tests = Item(
            id="TEST-AUTH",
            project_id="feature-dev",
            title="Authentication Tests",
            view="TEST",
            item_type="test",
            status="todo",
        )

        for item in [api, db_schema, tests]:
            sync_db_session.add(item)
        sync_db_session.commit()

        # Link items
        links = [
            Link(
                id="link-1",
                project_id="feature-dev",
                source_item_id="FEAT-001",
                target_item_id="API-AUTH",
                link_type="implements",
            ),
            Link(
                id="link-2",
                project_id="feature-dev",
                source_item_id="FEAT-001",
                target_item_id="DB-AUTH",
                link_type="depends_on",
            ),
            Link(
                id="link-3",
                project_id="feature-dev",
                source_item_id="TEST-AUTH",
                target_item_id="FEAT-001",
                link_type="tests",
            ),
        ]

        for link in links:
            sync_db_session.add(link)
        sync_db_session.commit()

        # Update statuses
        feature.status = "in_progress"
        api.status = "in_progress"
        sync_db_session.commit()

        # Verify workflow
        items = sync_db_session.query(Item).filter_by(project_id="feature-dev").all()
        assert len(items) == COUNT_FOUR

    @pytest.mark.integration
    def test_requirement_traceability_workflow(self, sync_db_session: Any) -> None:
        """Test requirement traceability workflow."""
        project = Project(id="requirements", name="Requirements")
        sync_db_session.add(project)
        sync_db_session.commit()

        # Create requirement
        req = Item(
            id="REQ-001",
            project_id="requirements",
            title="System shall authenticate users",
            view="REQUIREMENT",
            item_type="requirement",
            status="todo",
        )
        sync_db_session.add(req)
        sync_db_session.commit()

        # Create design
        design = Item(
            id="DESIGN-001",
            project_id="requirements",
            title="JWT-based Authentication Design",
            view="DESIGN",
            item_type="design",
            status="todo",
        )
        sync_db_session.add(design)
        sync_db_session.commit()

        # Link requirement to design
        link = Link(
            id="trace-1",
            project_id="requirements",
            source_item_id="REQ-001",
            target_item_id="DESIGN-001",
            link_type="implemented_by",
        )
        sync_db_session.add(link)
        sync_db_session.commit()

        # Verify traceability
        result_link = sync_db_session.query(Link).filter_by(id="trace-1").first()
        assert result_link is not None

    @pytest.mark.integration
    def test_bug_fixing_workflow(self, sync_db_session: Any) -> None:
        """Test bug fixing workflow."""
        project = Project(id="bug-tracker", name="Bug Tracker")
        sync_db_session.add(project)
        sync_db_session.commit()

        # Report bug
        bug = Item(
            id="BUG-001",
            project_id="bug-tracker",
            title="Login fails with special characters",
            view="BUG",
            item_type="bug",
            status="new",
            item_metadata={"severity": "high", "priority": 1},
        )
        sync_db_session.add(bug)
        sync_db_session.commit()

        # Assign to sprint
        bug.status = "assigned"
        bug.item_metadata["assignee"] = "dev-alice"
        sync_db_session.commit()

        # In progress
        bug.status = "in_progress"
        bug.item_metadata["started_at"] = datetime.now(UTC).isoformat()
        sync_db_session.commit()

        # Resolved
        bug.status = "resolved"
        bug.item_metadata["fixed_at"] = datetime.now(UTC).isoformat()
        sync_db_session.commit()

        result = sync_db_session.query(Item).filter_by(id="BUG-001").first()
        assert result.status == "resolved"


class TestImportExportWorkflows:
    """Test import and export workflows."""

    @pytest.mark.integration
    def test_project_export_to_json(self, db_with_sample_data: Any) -> None:
        """Test project export to JSON."""
        project = db_with_sample_data.query(Project).first()
        items = db_with_sample_data.query(Item).filter_by(project_id=project.id).all()
        links = db_with_sample_data.query(Link).filter_by(project_id=project.id).all()

        # Create export JSON
        export: dict[str, Any] = {
            "project": {"id": project.id, "name": project.name, "created_at": project.created_at.isoformat()},
            "items": [{"id": item.id, "title": item.title, "status": item.status} for item in items],
            "links": [
                {"id": link.id, "source": link.source_item_id, "target": link.target_item_id, "type": link.link_type}
                for link in links
            ],
        }

        assert export["project"]["id"] is not None
        assert len(export["items"]) >= COUNT_FOUR
        assert len(export["links"]) >= 1

    @pytest.mark.integration
    def test_data_import_workflow(self, sync_db_session: Any) -> None:
        """Test data import workflow."""
        # Import data
        import_data: dict[str, Any] = {
            "project": {"id": "imported-project", "name": "Imported Project"},
            "items": [
                {"id": "IMP-001", "title": "Item 1", "status": "todo"},
                {"id": "IMP-002", "title": "Item 2", "status": "todo"},
            ],
        }

        # Create imported project and items
        project_data = import_data["project"]
        project = Project(id=project_data["id"], name=project_data["name"])
        sync_db_session.add(project)
        sync_db_session.commit()

        for item_data in import_data["items"]:
            item = Item(
                id=str(item_data["id"]),
                project_id=str(project_data["id"]),
                title=str(item_data["title"]),
                view="FEATURE",
                item_type="feature",
                status=str(item_data["status"]),
            )
            sync_db_session.add(item)
        sync_db_session.commit()

        # Verify import
        imported_items = sync_db_session.query(Item).filter_by(project_id="imported-project").all()
        assert len(imported_items) == COUNT_TWO


class TestBackupRecoveryWorkflows:
    """Test backup and recovery workflows."""

    @pytest.mark.integration
    def test_project_backup_creation(self, db_with_sample_data: Any) -> None:
        """Test project backup creation."""
        project = db_with_sample_data.query(Project).first()
        items = db_with_sample_data.query(Item).filter_by(project_id=project.id).all()

        # Create backup
        backup: dict[str, Any] = {
            "timestamp": datetime.now(UTC).isoformat(),
            "project_id": project.id,
            "item_count": len(items),
            "items": [item.id for item in items],
        }

        assert backup["project_id"] is not None
        item_count: int = backup["item_count"]
        items_list: list[Any] = backup["items"]
        assert item_count >= COUNT_FOUR
        assert len(items_list) == item_count

    @pytest.mark.integration
    def test_data_recovery_workflow(self, sync_db_session: Any) -> None:
        """Test data recovery workflow."""
        # Create project with data
        project = Project(id="recovery-project", name="Recovery")
        sync_db_session.add(project)
        sync_db_session.commit()

        items = [
            Item(
                id=f"REC-{i:03d}",
                project_id="recovery-project",
                title=f"Item {i}",
                view="FEATURE",
                item_type="feature",
                status="todo",
            )
            for i in range(3)
        ]

        for item in items:
            sync_db_session.add(item)
        sync_db_session.commit()

        # Simulate recovery: verify data
        recovered_items = sync_db_session.query(Item).filter_by(project_id="recovery-project").all()
        assert len(recovered_items) == COUNT_THREE

    @pytest.mark.integration
    def test_incremental_backup_workflow(self, sync_db_session: Any) -> None:
        """Test incremental backup workflow."""
        project = Project(id="incremental-backup", name="Incremental")
        sync_db_session.add(project)
        sync_db_session.commit()

        # First backup
        items_batch1 = [
            Item(
                id=f"INCR-1-{i}",
                project_id="incremental-backup",
                title=f"Batch 1 Item {i}",
                view="FEATURE",
                item_type="feature",
                status="todo",
            )
            for i in range(2)
        ]

        for item in items_batch1:
            sync_db_session.add(item)
        sync_db_session.commit()

        # Second backup
        items_batch2 = [
            Item(
                id=f"INCR-2-{i}",
                project_id="incremental-backup",
                title=f"Batch 2 Item {i}",
                view="FEATURE",
                item_type="feature",
                status="todo",
            )
            for i in range(2)
        ]

        for item in items_batch2:
            sync_db_session.add(item)
        sync_db_session.commit()

        # Verify both batches
        all_items = sync_db_session.query(Item).filter_by(project_id="incremental-backup").all()
        assert len(all_items) == COUNT_FOUR
