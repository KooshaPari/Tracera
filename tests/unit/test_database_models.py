"""Unit tests for models with database persistence.

Tests: Model creation, persistence, retrieval
"""

import logging
from typing import Any

import pytest
from sqlalchemy.orm import Session

from tests.test_constants import COUNT_THREE, COUNT_TWO
from tracertm.database.connection import DatabaseConnection
from tracertm.models.agent import Agent
from tracertm.models.item import Item
from tracertm.models.link import Link
from tracertm.models.project import Project


@pytest.fixture
def test_db(tmp_path: Any) -> None:
    """Create test database."""
    db_path = tmp_path / "test.db"
    database_url = f"sqlite:///{db_path}"

    db = DatabaseConnection(database_url)
    db.connect()
    try:
        db.create_tables()
    except Exception as e:
        logging.getLogger(__name__).debug("create_tables skipped: %s", e)

    return db


class TestItemPersistence:
    """Test Item model persistence."""

    def test_create_and_retrieve_item(self, test_db: Any) -> None:
        """Test creating and retrieving item."""
        with Session(test_db.engine) as session:
            project = Project(name="Test")
            session.add(project)
            session.commit()
            project_id = project.id

        with Session(test_db.engine) as session:
            item = Item(project_id=project_id, title="Test Item", view="FEATURE", item_type="feature")
            session.add(item)
            session.commit()
            item_id = item.id

        with Session(test_db.engine) as session:
            retrieved = session.query(Item).filter(Item.id == item_id).first()
            assert retrieved.title == "Test Item"
            assert retrieved.status == "todo"
            assert retrieved.version == 1

    def test_update_item(self, test_db: Any) -> None:
        """Test updating item."""
        with Session(test_db.engine) as session:
            project = Project(name="Test")
            session.add(project)
            session.commit()
            project_id = project.id

        with Session(test_db.engine) as session:
            item = Item(project_id=project_id, title="Original", view="FEATURE", item_type="feature")
            session.add(item)
            session.commit()
            item_id = item.id

        with Session(test_db.engine) as session:
            item = session.query(Item).filter(Item.id == item_id).first()
            item.title = "Updated"
            item.version = 2
            session.commit()

        with Session(test_db.engine) as session:
            item = session.query(Item).filter(Item.id == item_id).first()
            assert item.title == "Updated"
            assert item.version == COUNT_TWO

    def test_item_metadata_persistence(self, test_db: Any) -> None:
        """Test item metadata persistence."""
        with Session(test_db.engine) as session:
            project = Project(name="Test")
            session.add(project)
            session.commit()
            project_id = project.id

        with Session(test_db.engine) as session:
            item = Item(
                project_id=project_id,
                title="Test",
                view="FEATURE",
                item_type="feature",
                item_metadata={"priority": "high", "tags": ["urgent"]},
            )
            session.add(item)
            session.commit()
            item_id = item.id

        with Session(test_db.engine) as session:
            item = session.query(Item).filter(Item.id == item_id).first()
            assert item.item_metadata["priority"] == "high"
            assert "urgent" in item.item_metadata["tags"]


class TestLinkPersistence:
    """Test Link model persistence."""

    def test_create_and_retrieve_link(self, test_db: Any) -> None:
        """Test creating and retrieving link."""
        with Session(test_db.engine) as session:
            project = Project(name="Test")
            session.add(project)
            session.commit()
            project_id = project.id

        with Session(test_db.engine) as session:
            link = Link(project_id=project_id, source_item_id="item-1", target_item_id="item-2", link_type="depends_on")
            session.add(link)
            session.commit()
            link_id = link.id

        with Session(test_db.engine) as session:
            retrieved = session.query(Link).filter(Link.id == link_id).first()
            assert retrieved.link_type == "depends_on"
            assert retrieved.source_item_id == "item-1"


class TestAgentPersistence:
    """Test Agent model persistence."""

    def test_create_and_retrieve_agent(self, test_db: Any) -> None:
        """Test creating and retrieving agent."""
        with Session(test_db.engine) as session:
            project = Project(name="Test")
            session.add(project)
            session.commit()
            project_id = project.id

        with Session(test_db.engine) as session:
            agent = Agent(project_id=project_id, name="agent-1", agent_type="analyzer")
            session.add(agent)
            session.commit()
            agent_id = agent.id

        with Session(test_db.engine) as session:
            retrieved = session.query(Agent).filter(Agent.id == agent_id).first()
            assert retrieved.name == "agent-1"
            assert retrieved.agent_type == "analyzer"


class TestModelQueries:
    """Test model queries."""

    def test_query_items_by_view(self, test_db: Any) -> None:
        """Test querying items by view."""
        with Session(test_db.engine) as session:
            project = Project(name="Test")
            session.add(project)
            session.commit()
            project_id = project.id

        with Session(test_db.engine) as session:
            items = [
                Item(project_id=project_id, title=f"Feature {i}", view="FEATURE", item_type="feature") for i in range(3)
            ]
            items.extend([
                Item(project_id=project_id, title=f"Code {i}", view="CODE", item_type="class") for i in range(2)
            ])
            session.add_all(items)
            session.commit()

        with Session(test_db.engine) as session:
            features = session.query(Item).filter(Item.view == "FEATURE").all()
            codes = session.query(Item).filter(Item.view == "CODE").all()

            assert len(features) == COUNT_THREE
            assert len(codes) == COUNT_TWO

    def test_query_links_by_type(self, test_db: Any) -> None:
        """Test querying links by type."""
        with Session(test_db.engine) as session:
            project = Project(name="Test")
            session.add(project)
            session.commit()
            project_id = project.id

        with Session(test_db.engine) as session:
            links = [
                Link(project_id=project_id, source_item_id="i1", target_item_id="i2", link_type="depends_on"),
                Link(project_id=project_id, source_item_id="i2", target_item_id="i3", link_type="blocks"),
                Link(project_id=project_id, source_item_id="i3", target_item_id="i4", link_type="depends_on"),
            ]
            session.add_all(links)
            session.commit()

        with Session(test_db.engine) as session:
            depends = session.query(Link).filter(Link.link_type == "depends_on").all()
            blocks = session.query(Link).filter(Link.link_type == "blocks").all()

            assert len(depends) == COUNT_TWO
            assert len(blocks) == 1
