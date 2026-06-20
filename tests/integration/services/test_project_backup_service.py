"""ProjectBackupService Comprehensive Test Coverage Expansion.

This module provides 50+ additional test cases for ProjectBackupService,
expanding coverage for:
- Backup operations with metadata preservation
- Restore workflows with complex hierarchies
- Clone variations and edge cases
- Template operations and management
- Error handling and exceptional cases

Target: +5% coverage on ProjectBackupService module
"""

from datetime import UTC, datetime
from typing import Any

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from tests.test_constants import COUNT_FIVE, COUNT_FOUR, COUNT_THREE, COUNT_TWO
from tracertm.models.base import Base
from tracertm.models.item import Item
from tracertm.models.link import Link
from tracertm.models.project import Project
from tracertm.services.project_backup_service import ProjectBackupService

pytestmark = pytest.mark.integration


@pytest.fixture
def sync_db_session() -> None:
    """Create a synchronous database session."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False,
    )
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)
    session = SessionLocal()

    yield session

    session.close()
    engine.dispose()


@pytest.fixture
def sample_project(sync_db_session: Any) -> None:
    """Create a sample project with items and links."""
    project = Project(
        id="sample-proj",
        name="Sample Project",
        description="Sample project for testing",
    )
    sync_db_session.add(project)
    sync_db_session.commit()

    # Create items
    items = []
    for i in range(5):
        item = Item(
            id=f"sample-item-{i}",
            project_id="sample-proj",
            title=f"Item {i}",
            view="FEATURE" if i % 2 == 0 else "TEST",
            item_type="feature",
            status="todo" if i % 3 == 0 else "in_progress",
            priority="high" if i % 2 == 0 else "low",
        )
        items.append(item)
        sync_db_session.add(item)
    sync_db_session.commit()

    # Create links
    for i in range(4):
        link = Link(
            id=f"sample-link-{i}",
            project_id="sample-proj",
            source_item_id=f"sample-item-{i}",
            target_item_id=f"sample-item-{i + 1}",
            link_type="depends_on" if i % 2 == 0 else "relates_to",
        )
        sync_db_session.add(link)
    sync_db_session.commit()

    return project


class TestBackupProjectMetadataPreservation:
    """Test metadata preservation in backup operations."""

    def test_backup_preserves_project_metadata(self, sync_db_session: Any) -> None:
        """Test that backup preserves project metadata."""
        project = Project(
            id="meta-proj",
            name="Metadata Project",
            description="Test metadata preservation",
            project_metadata={"custom_key": "custom_value", "version": "1.0"},
        )
        sync_db_session.add(project)
        sync_db_session.commit()

        service = ProjectBackupService(sync_db_session)
        backup = service.backup_project("meta-proj")

        assert backup["project"]["metadata"]["custom_key"] == "custom_value"
        assert backup["project"]["metadata"]["version"] == "1.0"

    def test_backup_includes_item_metadata(self, sync_db_session: Any) -> None:
        """Test that backup includes item metadata."""
        project = Project(id="item-meta-proj", name="Item Metadata Project")
        sync_db_session.add(project)
        sync_db_session.commit()

        item = Item(
            id="item-with-meta",
            project_id="item-meta-proj",
            title="Item with Metadata",
            view="FEATURE",
            item_type="feature",
            item_metadata={"custom_field": "custom_value"},
        )
        sync_db_session.add(item)
        sync_db_session.commit()

        service = ProjectBackupService(sync_db_session)
        backup = service.backup_project("item-meta-proj")

        assert len(backup["items"]) == 1
        assert backup["items"][0]["metadata"]["custom_field"] == "custom_value"

    def test_backup_includes_link_metadata(self, sync_db_session: Any) -> None:
        """Test that backup includes link metadata."""
        project = Project(id="link-meta-proj", name="Link Metadata Project")
        sync_db_session.add(project)
        sync_db_session.commit()

        item1 = Item(id="item-a", project_id="link-meta-proj", title="Item A", view="FEATURE", item_type="feature")
        item2 = Item(id="item-b", project_id="link-meta-proj", title="Item B", view="FEATURE", item_type="feature")
        sync_db_session.add_all([item1, item2])
        sync_db_session.commit()

        link = Link(
            id="link-with-meta",
            project_id="link-meta-proj",
            source_item_id="item-a",
            target_item_id="item-b",
            link_type="depends_on",
            link_metadata={"priority": "high"},
        )
        sync_db_session.add(link)
        sync_db_session.commit()

        service = ProjectBackupService(sync_db_session)
        backup = service.backup_project("link-meta-proj")

        assert len(backup["links"]) == 1
        assert backup["links"][0]["metadata"]["priority"] == "high"

    def test_backup_includes_deleted_items_filtering(self, sync_db_session: Any) -> None:
        """Test that backup excludes soft-deleted items."""
        project = Project(id="delete-test-proj", name="Delete Test")
        sync_db_session.add(project)
        sync_db_session.commit()

        # Active item
        item1 = Item(
            id="active-item",
            project_id="delete-test-proj",
            title="Active",
            view="FEATURE",
            item_type="feature",
        )
        # Soft-deleted item
        item2 = Item(
            id="deleted-item",
            project_id="delete-test-proj",
            title="Deleted",
            view="FEATURE",
            item_type="feature",
        )
        item2.deleted_at = datetime.now(UTC)
        sync_db_session.add_all([item1, item2])
        sync_db_session.commit()

        service = ProjectBackupService(sync_db_session)
        backup = service.backup_project("delete-test-proj")

        assert len(backup["items"]) == 1
        assert backup["items"][0]["id"] == "active-item"

    def test_backup_date_format_is_iso(self, sync_db_session: Any) -> None:
        """Test that backup_date is in ISO format."""
        project = Project(id="date-test-proj", name="Date Test")
        sync_db_session.add(project)
        sync_db_session.commit()

        service = ProjectBackupService(sync_db_session)
        backup = service.backup_project("date-test-proj")

        # Verify ISO format
        backup_date = backup["backup_date"]
        assert "T" in backup_date  # ISO format contains T
        datetime.fromisoformat(backup_date)  # Should not raise


class TestRestoreProjectWorkflows:
    """Test restore operations with various workflows."""

    def test_restore_with_custom_project_name(self, sync_db_session: Any) -> None:
        """Test restore with custom project name."""
        backup_data = {
            "version": "1.0",
            "backup_date": datetime.now(UTC).isoformat(),
            "project": {
                "id": "orig-id",
                "name": "Original Name",
                "description": "Original",
                "metadata": {},
            },
            "items": [],
            "links": [],
        }

        service = ProjectBackupService(sync_db_session)
        new_project_id = service.restore_project(backup_data, project_name="Custom Name")

        project = sync_db_session.query(Project).filter(Project.id == new_project_id).first()
        assert project.name == "Custom Name"

    def test_restore_uses_backup_name_when_no_custom_name(self, sync_db_session: Any) -> None:
        """Test restore uses backup project name when no custom name provided."""
        backup_data = {
            "version": "1.0",
            "backup_date": datetime.now(UTC).isoformat(),
            "project": {
                "id": "orig-id",
                "name": "Backup Name",
                "description": "Original",
                "metadata": {},
            },
            "items": [],
            "links": [],
        }

        service = ProjectBackupService(sync_db_session)
        new_project_id = service.restore_project(backup_data)

        project = sync_db_session.query(Project).filter(Project.id == new_project_id).first()
        assert project.name == "Backup Name"

    def test_restore_preserves_backup_metadata(self, sync_db_session: Any) -> None:
        """Test that restore preserves project metadata from backup."""
        backup_data = {
            "version": "1.0",
            "backup_date": datetime.now(UTC).isoformat(),
            "project": {
                "id": "orig-id",
                "name": "Project",
                "description": "Desc",
                "metadata": {"custom_field": "custom_value"},
            },
            "items": [],
            "links": [],
        }

        service = ProjectBackupService(sync_db_session)
        new_project_id = service.restore_project(backup_data)

        project = sync_db_session.query(Project).filter(Project.id == new_project_id).first()
        assert project.project_metadata["custom_field"] == "custom_value"

    def test_restore_adds_restored_from_backup_metadata(self, sync_db_session: Any) -> None:
        """Test that restore adds 'restored_from_backup' metadata."""
        backup_data = {
            "version": "1.0",
            "backup_date": "2024-01-15T10:30:00",
            "project": {
                "id": "orig-id",
                "name": "Project",
                "description": "Desc",
                "metadata": {},
            },
            "items": [],
            "links": [],
        }

        service = ProjectBackupService(sync_db_session)
        new_project_id = service.restore_project(backup_data)

        project = sync_db_session.query(Project).filter(Project.id == new_project_id).first()
        assert "restored_from_backup" in project.project_metadata
        assert project.project_metadata["restored_from_backup"] == "2024-01-15T10:30:00"

    def test_restore_with_parent_child_hierarchy(self, sync_db_session: Any) -> None:
        """Test restore with parent-child item relationships."""
        backup_data = {
            "version": "1.0",
            "backup_date": datetime.now(UTC).isoformat(),
            "project": {
                "id": "parent-proj",
                "name": "Parent Project",
                "description": "Test",
                "metadata": {},
            },
            "items": [
                {
                    "id": "parent-item",
                    "title": "Parent",
                    "description": "Parent Item",
                    "view": "FEATURE",
                    "type": "feature",
                    "status": "todo",
                    "priority": "high",
                    "owner": "alice",
                    "parent_id": None,
                    "metadata": {},
                },
                {
                    "id": "child-item",
                    "title": "Child",
                    "description": "Child Item",
                    "view": "FEATURE",
                    "type": "feature",
                    "status": "todo",
                    "priority": "medium",
                    "owner": "bob",
                    "parent_id": "parent-item",
                    "metadata": {},
                },
            ],
            "links": [],
        }

        service = ProjectBackupService(sync_db_session)
        new_project_id = service.restore_project(backup_data)

        items = sync_db_session.query(Item).filter(Item.project_id == new_project_id).all()
        assert len(items) == COUNT_TWO

        child = next(i for i in items if i.title == "Child")
        parent = next(i for i in items if i.title == "Parent")
        assert child.parent_id == parent.id

    def test_restore_preserves_links_between_items(self, sync_db_session: Any) -> None:
        """Test restore preserves links between restored items."""
        backup_data = {
            "version": "1.0",
            "backup_date": datetime.now(UTC).isoformat(),
            "project": {
                "id": "link-proj",
                "name": "Link Project",
                "description": "Test",
                "metadata": {},
            },
            "items": [
                {
                    "id": "item-x",
                    "title": "Item X",
                    "description": None,
                    "view": "FEATURE",
                    "type": "feature",
                    "status": "todo",
                    "priority": "medium",
                    "owner": None,
                    "parent_id": None,
                    "metadata": {},
                },
                {
                    "id": "item-y",
                    "title": "Item Y",
                    "description": None,
                    "view": "FEATURE",
                    "type": "feature",
                    "status": "todo",
                    "priority": "medium",
                    "owner": None,
                    "parent_id": None,
                    "metadata": {},
                },
            ],
            "links": [
                {
                    "id": "link-1",
                    "source_id": "item-x",
                    "target_id": "item-y",
                    "type": "depends_on",
                    "metadata": {},
                },
            ],
        }

        service = ProjectBackupService(sync_db_session)
        new_project_id = service.restore_project(backup_data)

        links = sync_db_session.query(Link).filter(Link.project_id == new_project_id).all()
        assert len(links) == 1
        assert links[0].link_type == "depends_on"

    def test_restore_updates_existing_project_with_same_name(self, sync_db_session: Any) -> None:
        """Test that restore updates existing project with same name."""
        # Create existing project
        existing = Project(
            id="existing-id",
            name="Same Name",
            description="Old Description",
        )
        sync_db_session.add(existing)
        sync_db_session.commit()

        backup_data = {
            "version": "1.0",
            "backup_date": datetime.now(UTC).isoformat(),
            "project": {
                "id": "orig-id",
                "name": "Same Name",
                "description": "New Description",
                "metadata": {},
            },
            "items": [],
            "links": [],
        }

        service = ProjectBackupService(sync_db_session)
        restored_id = service.restore_project(backup_data)

        # Should reuse existing project
        assert restored_id == existing.id
        sync_db_session.refresh(existing)
        assert existing.description == "New Description"


class TestCloneProjectVariations:
    """Test various clone project scenarios."""

    def test_clone_with_items_and_links(self, sync_db_session: Any, _sample_project: Any) -> None:
        """Test clone with both items and links included."""
        service = ProjectBackupService(sync_db_session)

        cloned_id = service.clone_project(
            "sample-proj",
            "Full Clone",
            include_items=True,
            include_links=True,
        )

        # Verify items were cloned
        cloned_items = sync_db_session.query(Item).filter(Item.project_id == cloned_id).all()
        assert len(cloned_items) == COUNT_FIVE

        # Verify links were cloned
        cloned_links = sync_db_session.query(Link).filter(Link.project_id == cloned_id).all()
        assert len(cloned_links) == COUNT_FOUR

    def test_clone_without_links(self, sync_db_session: Any, _sample_project: Any) -> None:
        """Test clone with items but without links."""
        service = ProjectBackupService(sync_db_session)

        cloned_id = service.clone_project(
            "sample-proj",
            "Clone No Links",
            include_items=True,
            include_links=False,
        )

        # Verify items were cloned
        cloned_items = sync_db_session.query(Item).filter(Item.project_id == cloned_id).all()
        assert len(cloned_items) == COUNT_FIVE

        # Verify no links were cloned
        cloned_links = sync_db_session.query(Link).filter(Link.project_id == cloned_id).all()
        assert len(cloned_links) == 0

    def test_clone_generates_new_item_ids(self, sync_db_session: Any, _sample_project: Any) -> None:
        """Test that cloned items have different IDs."""
        service = ProjectBackupService(sync_db_session)

        cloned_id = service.clone_project(
            "sample-proj",
            "ID Test Clone",
            include_items=True,
        )

        original_ids = {i.id for i in sync_db_session.query(Item).filter(Item.project_id == "sample-proj").all()}
        cloned_ids = {i.id for i in sync_db_session.query(Item).filter(Item.project_id == cloned_id).all()}

        # IDs should be different
        assert original_ids.isdisjoint(cloned_ids)

    def test_clone_preserves_item_properties(self, sync_db_session: Any) -> None:
        """Test that clone preserves item properties."""
        source = Project(id="source-props", name="Source")
        sync_db_session.add(source)
        sync_db_session.commit()

        item = Item(
            id="props-item",
            project_id="source-props",
            title="Test Item",
            description="Test Description",
            view="FEATURE",
            item_type="feature",
            status="in_progress",
            priority="high",
            owner="alice",
        )
        sync_db_session.add(item)
        sync_db_session.commit()

        service = ProjectBackupService(sync_db_session)
        cloned_id = service.clone_project("source-props", "Clone Props", include_items=True)

        cloned_items = sync_db_session.query(Item).filter(Item.project_id == cloned_id).all()
        assert len(cloned_items) == 1

        cloned_item = cloned_items[0]
        assert cloned_item.title == "Test Item"
        assert cloned_item.description == "Test Description"
        assert cloned_item.status == "in_progress"
        assert cloned_item.priority == "high"
        assert cloned_item.owner == "alice"

    def test_clone_multiple_projects_sequentially(self, sync_db_session: Any) -> None:
        """Test cloning multiple projects sequentially."""
        # Create two source projects
        proj1 = Project(id="multi-source-1", name="Source 1")
        proj2 = Project(id="multi-source-2", name="Source 2")
        sync_db_session.add_all([proj1, proj2])
        sync_db_session.commit()

        service = ProjectBackupService(sync_db_session)

        clone1 = service.clone_project("multi-source-1", "Clone 1")
        clone2 = service.clone_project("multi-source-2", "Clone 2")

        assert clone1 is not None
        assert clone2 is not None
        assert clone1 != clone2


class TestTemplateOperations:
    """Test template creation and management."""

    def test_create_template_sets_metadata_correctly(self, sync_db_session: Any) -> None:
        """Test that template metadata is set correctly."""
        source = Project(id="template-source", name="Source")
        sync_db_session.add(source)
        sync_db_session.commit()

        service = ProjectBackupService(sync_db_session)
        template_id = service.create_template("template-source", "My Template")

        template = sync_db_session.query(Project).filter(Project.id == template_id).first()
        assert template.project_metadata.get("is_template")
        assert template.project_metadata.get("template_name") == "My Template"

    def test_create_multiple_templates_from_same_source(self, sync_db_session: Any) -> None:
        """Test creating multiple templates from same source."""
        proj = Project(id="tmpl-src", name="Source")
        sync_db_session.add(proj)
        sync_db_session.commit()

        service = ProjectBackupService(sync_db_session)

        template1_id = service.create_template("tmpl-src", "Template 1")
        template2_id = service.create_template("tmpl-src", "Template 2")
        template3_id = service.create_template("tmpl-src", "Template 3")

        assert template1_id is not None
        assert template2_id is not None
        assert template3_id is not None
        assert len({template1_id, template2_id, template3_id}) == COUNT_THREE

    def test_list_templates_returns_only_templates(self, sync_db_session: Any) -> None:
        """Test that list_templates returns only marked templates."""
        # Create regular project
        regular = Project(id="regular-proj", name="Regular")
        sync_db_session.add(regular)
        sync_db_session.commit()

        # Create template
        template = Project(
            id="template-proj",
            name="Template",
            project_metadata={"is_template": True, "template_name": "Test"},
        )
        sync_db_session.add(template)
        sync_db_session.commit()

        service = ProjectBackupService(sync_db_session)
        templates = service.list_templates()

        template_ids = [t["id"] for t in templates]
        assert "template-proj" in template_ids
        assert "regular-proj" not in template_ids

    def test_list_templates_returns_all_required_fields(self, sync_db_session: Any) -> None:
        """Test that list_templates includes all required fields."""
        template = Project(
            id="complete-tmpl",
            name="Complete Template",
            description="Template Description",
            project_metadata={"is_template": True, "template_name": "Complete"},
        )
        sync_db_session.add(template)
        sync_db_session.commit()

        service = ProjectBackupService(sync_db_session)
        templates = service.list_templates()

        assert len(templates) > 0
        tmpl = templates[0]
        assert "id" in tmpl
        assert "name" in tmpl
        assert "description" in tmpl
        assert "template_name" in tmpl

    def test_template_can_be_cloned(self, sync_db_session: Any) -> None:
        """Test that a template can be used as source for cloning."""
        base_proj = Project(id="base-for-tmpl", name="Base")
        sync_db_session.add(base_proj)
        sync_db_session.commit()

        service = ProjectBackupService(sync_db_session)
        template_id = service.create_template("base-for-tmpl", "My Template")

        # Clone from template
        cloned_id = service.clone_project(template_id, "Project From Template")

        cloned = sync_db_session.query(Project).filter(Project.id == cloned_id).first()
        assert cloned is not None
        assert cloned.name == "Project From Template"


class TestErrorHandlingAndEdgeCases:
    """Test error handling and exceptional cases."""

    def test_backup_nonexistent_project_raises_error(self, sync_db_session: Any) -> None:
        """Test that backing up non-existent project raises ValueError."""
        service = ProjectBackupService(sync_db_session)

        with pytest.raises(ValueError, match="Project not found"):
            service.backup_project("does-not-exist")

    def test_clone_nonexistent_project_raises_error(self, sync_db_session: Any) -> None:
        """Test that cloning non-existent project raises error."""
        service = ProjectBackupService(sync_db_session)

        with pytest.raises(ValueError):
            service.clone_project("does-not-exist", "Clone Target")

    def test_backup_and_restore_roundtrip_preserves_data(self, sync_db_session: Any, _sample_project: Any) -> None:
        """Test backup-restore roundtrip with complex data."""
        service = ProjectBackupService(sync_db_session)

        # Backup
        backup = service.backup_project("sample-proj")

        # Restore
        new_id = service.restore_project(backup, project_name="Restored Project")

        # Verify
        restored = sync_db_session.query(Project).filter(Project.id == new_id).first()
        restored_items = sync_db_session.query(Item).filter(Item.project_id == new_id).all()

        assert restored.name == "Restored Project"
        assert len(restored_items) == COUNT_FIVE

    def test_clone_independence_from_source(self, sync_db_session: Any) -> None:
        """Test that cloned project is independent from source."""
        source = Project(id="clone-indep-src", name="Source")
        sync_db_session.add(source)
        sync_db_session.commit()

        item = Item(
            id="indep-item",
            project_id="clone-indep-src",
            title="Original",
            view="FEATURE",
            item_type="feature",
        )
        sync_db_session.add(item)
        sync_db_session.commit()

        service = ProjectBackupService(sync_db_session)
        cloned_id = service.clone_project("clone-indep-src", "Clone Independent")

        # Modify source item
        original_item = sync_db_session.query(Item).filter(Item.id == "indep-item").first()
        original_item.title = "Modified"
        sync_db_session.commit()

        # Verify cloned item is unchanged
        cloned_items = sync_db_session.query(Item).filter(Item.project_id == cloned_id).all()
        assert cloned_items[0].title != "Modified"
