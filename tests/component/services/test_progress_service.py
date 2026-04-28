from datetime import UTC, datetime, timedelta
from typing import Any

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from tests.test_constants import COUNT_TWO

# Import ALL models to ensure they're registered with Base.metadata
from tracertm.models.base import Base
from tracertm.models.item import Item
from tracertm.models.link import Link
from tracertm.models.project import Project
from tracertm.services.progress_service import ProgressService


def _session() -> None:
    engine = create_engine("sqlite:///:memory:")
    # All models are already imported above, so Base.metadata is complete
    Base.metadata.create_all(engine)
    return Session(bind=engine)


def _ensure_project(session: Any, project_id: Any) -> None:
    """Ensure a project exists before creating items (foreign key requirement)."""
    existing = session.query(Project).filter(Project.id == project_id).first()
    if not existing:
        project = Project(id=project_id, name=f"Test Project {project_id}")
        session.add(project)
        session.commit()


def _seed_items(session: Any, project_id: Any = "proj-1") -> None:
    # CRITICAL: Create project first to satisfy foreign key constraint
    _ensure_project(session, project_id)

    parent = Item(
        id="p1",
        project_id=project_id,
        title="Parent",
        view="FEATURE",
        item_type="epic",
        status="in_progress",
    )
    child_done = Item(
        id="c1",
        project_id=project_id,
        title="Done",
        view="FEATURE",
        item_type="story",
        status="complete",
        parent_id="p1",
    )
    child_todo = Item(
        id="c2",
        project_id=project_id,
        title="Todo",
        view="FEATURE",
        item_type="story",
        status="todo",
        parent_id="p1",
    )
    session.add_all([parent, child_done, child_todo])
    session.commit()
    return parent, child_done, child_todo


def test_calculate_completion_leaf() -> None:
    session = _session()
    # CRITICAL: Create project first to satisfy foreign key constraint
    _ensure_project(session, "proj")

    item = Item(id="i1", project_id="proj", title="Leaf", view="FEATURE", item_type="story", status="complete")
    session.add(item)
    session.commit()

    svc = ProgressService(session)
    assert svc.calculate_completion("i1") == 100.0


def test_calculate_completion_parent_average() -> None:
    session = _session()
    parent, _child_done, _child_todo = _seed_items(session)
    svc = ProgressService(session)
    pct = svc.calculate_completion(parent.id)
    assert pct == (100.0 + 0.0) / 2


def test_get_blocked_items_returns_blockers() -> None:
    session = _session()
    # CRITICAL: Create project first to satisfy foreign key constraint
    _ensure_project(session, "proj")

    blocked = Item(id="b1", project_id="proj", title="Blocked", view="FEATURE", item_type="story", status="in_progress")
    blocker = Item(id="blk1", project_id="proj", title="Blocker", view="FEATURE", item_type="story", status="todo")

    session.add_all([
        blocked,
        blocker,
        Link(id="l1", project_id="proj", source_item_id="blk1", target_item_id="b1", link_type="blocks"),
    ])
    session.commit()

    svc = ProgressService(session)
    results = svc.get_blocked_items("proj")
    assert results[0]["item_id"] == "b1"
    assert results[0]["blockers"][0]["id"] == "blk1"


def test_get_stalled_items_filters_by_threshold() -> None:
    session = _session()
    # CRITICAL: Create project first to satisfy foreign key constraint
    _ensure_project(session, "proj")

    old = Item(
        id="old",
        project_id="proj",
        title="Old",
        view="FEATURE",
        item_type="story",
        status="in_progress",
        updated_at=datetime.now(UTC) - timedelta(days=10),
    )
    fresh = Item(
        id="fresh",
        project_id="proj",
        title="Fresh",
        view="FEATURE",
        item_type="story",
        status="in_progress",
        updated_at=datetime.now(UTC),
    )
    session.add_all([old, fresh])
    session.commit()

    svc = ProgressService(session)
    stalled = svc.get_stalled_items("proj", days_threshold=7)
    ids = [s["item_id"] for s in stalled]
    assert "old" in ids and "fresh" not in ids


def test_calculate_velocity_counts_created_and_completed() -> None:
    session = _session()
    # CRITICAL: Create project first to satisfy foreign key constraint
    _ensure_project(session, "proj")

    now = datetime.now(UTC)
    old = datetime.now(UTC) - timedelta(days=30)  # created outside the 7-day window
    # Both done and created items will have created_at set to now by default
    # They will both be counted in items_created since they're in the 7-day window
    done = Item(
        id="done",
        project_id="proj",
        title="Done",
        view="FEATURE",
        item_type="story",
        status="complete",
        updated_at=now,
    )
    created = Item(id="new", project_id="proj", title="New", view="FEATURE", item_type="story", status="todo")
    old_created = Item(
        id="old_new",
        project_id="proj",
        title="Old New",
        view="FEATURE",
        item_type="story",
        status="todo",
        created_at=old,
    )
    session.add_all([done, created, old_created])
    session.commit()

    svc = ProgressService(session)
    v = svc.calculate_velocity("proj", days=7)
    assert v["items_completed"] == 1
    assert v["items_created"] == COUNT_TWO  # Both done and created are in the 7-day window
