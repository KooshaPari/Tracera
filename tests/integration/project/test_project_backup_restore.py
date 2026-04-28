from typing import Any

"""Integration tests for Epic 6: Project Backup & Restore (Story 6.6, FR53)."""

import pytest

from tests.test_constants import COUNT_TWO

pytestmark = pytest.mark.integration
from sqlalchemy.orm import Session

from tracertm.config.manager import ConfigManager
from tracertm.database.connection import DatabaseConnection
from tracertm.models.item import Item
from tracertm.models.link import Link
from tracertm.models.project import Project
from tracertm.services.project_backup_service import ProjectBackupService


@pytest.fixture
def project_with_data_setup(tmp_path: Any, monkeypatch: Any) -> None:
    """Set up project with items and links for testing."""
    config_dir = tmp_path / ".config" / "tracertm"
    config_dir.mkdir(parents=True)
    monkeypatch.setenv("HOME", str(tmp_path))

    config_manager = ConfigManager()

    db_path = tmp_path / "test.db"
    database_url = f"sqlite:///{db_path}"
    config_manager.set("database_url", database_url)

    db = DatabaseConnection(database_url)
    db.connect()
    db.create_tables()

    with Session(db.engine) as session:
        project = Project(name="test-project", description="Test project")
        session.add(project)
        session.commit()
        project_id = str(project.id)

        # Create items
        item1 = Item(
            project_id=project_id,
            title="Item 1",
            view="FEATURE",
            item_type="feature",
            status="todo",
        )
        item2 = Item(
            project_id=project_id,
            title="Item 2",
            view="CODE",
            item_type="file",
            status="in_progress",
            parent_id=None,
        )
        session.add(item1)
        session.add(item2)
        session.flush()

        # Create link
        link = Link(
            project_id=project_id,
            source_item_id=item1.id,
            target_item_id=item2.id,
            link_type="implements",
        )
        session.add(link)
        session.commit()

    return project_id, database_url


def test_project_backup(project_with_data_setup: Any) -> None:
    """Test project backup (Story 6.6, FR53)."""
    project_id, database_url = project_with_data_setup

    db = DatabaseConnection(database_url)
    db.connect()

    with Session(db.engine) as session:
        service = ProjectBackupService(session)
        backup_data = service.backup_project(project_id)

        assert "project" in backup_data
        assert "items" in backup_data
        assert "links" in backup_data
        assert backup_data["project"]["id"] == project_id
        assert len(backup_data["items"]) == COUNT_TWO
        assert len(backup_data["links"]) == 1


def test_project_restore(project_with_data_setup: Any) -> None:
    """Test project restore (Story 6.6, FR53)."""
    project_id, database_url = project_with_data_setup

    db = DatabaseConnection(database_url)
    db.connect()

    with Session(db.engine) as session:
        service = ProjectBackupService(session)

        # Create backup
        backup_data = service.backup_project(project_id)

        # Restore as new project
        new_project_id = service.restore_project(backup_data, project_name="restored-project")

        # Verify restored project
        restored_project = session.query(Project).filter(Project.id == new_project_id).first()
        assert restored_project is not None
        assert restored_project.name == "restored-project"

        # Verify items restored
        items = session.query(Item).filter(Item.project_id == new_project_id).all()
        assert len(items) == COUNT_TWO

        # Verify links restored
        links = session.query(Link).filter(Link.project_id == new_project_id).all()
        assert len(links) == 1


def test_project_clone(project_with_data_setup: Any) -> None:
    """Test project cloning (Story 6.5, FR46)."""
    project_id, database_url = project_with_data_setup

    db = DatabaseConnection(database_url)
    db.connect()

    with Session(db.engine) as session:
        service = ProjectBackupService(session)

        # Clone project
        new_project_id = service.clone_project(project_id, "cloned-project")

        # Verify cloned project
        cloned_project = session.query(Project).filter(Project.id == new_project_id).first()
        assert cloned_project is not None
        assert cloned_project.name == "cloned-project"

        # Verify items cloned
        items = session.query(Item).filter(Item.project_id == new_project_id).all()
        assert len(items) == COUNT_TWO

        # Verify links cloned
        links = session.query(Link).filter(Link.project_id == new_project_id).all()
        assert len(links) == 1


def test_project_template_creation(project_with_data_setup: Any) -> None:
    """Test template creation (Story 6.5, FR46)."""
    project_id, database_url = project_with_data_setup

    db = DatabaseConnection(database_url)
    db.connect()

    with Session(db.engine) as session:
        service = ProjectBackupService(session)

        # Create template
        template_id = service.create_template(project_id, "my-template")

        # Verify template
        template = session.query(Project).filter(Project.id == template_id).first()
        assert template is not None
        assert template.project_metadata.get("is_template") is True
        assert template.project_metadata.get("template_name") == "my-template"

        # List templates
        templates = service.list_templates()
        assert len(templates) == 1
        assert templates[0]["template_name"] == "my-template"
