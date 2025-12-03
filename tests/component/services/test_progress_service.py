from datetime import datetime, timedelta

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from tracertm.models.item import Item
from tracertm.services.progress_service import ProgressService


def _session():
    engine = create_engine("sqlite:///:memory:")
    from tracertm.models.base import Base

    Base.metadata.create_all(engine)
    return Session(bind=engine)


def _seed_items(session, project_id="proj-1"):
    parent = Item(id="p1", project_id=project_id, title="Parent", status="in_progress")
    child_done = Item(id="c1", project_id=project_id, title="Done", status="complete", parent_id="p1")
    child_todo = Item(id="c2", project_id=project_id, title="Todo", status="todo", parent_id="p1")
    session.add_all([parent, child_done, child_todo])
    session.commit()
    return parent, child_done, child_todo


def test_calculate_completion_leaf():
    session = _session()
    item = Item(id="i1", project_id="proj", title="Leaf", status="complete")
    session.add(item)
    session.commit()

    svc = ProgressService(session)
    assert svc.calculate_completion("i1") == 100.0


def test_calculate_completion_parent_average():
    session = _session()
    parent, child_done, child_todo = _seed_items(session)
    svc = ProgressService(session)
    pct = svc.calculate_completion(parent.id)
    assert pct == (100.0 + 0.0) / 2


def test_get_blocked_items_returns_blockers():
    session = _session()
    blocked = Item(id="b1", project_id="proj", title="Blocked", status="in_progress")
    blocker = Item(id="blk1", project_id="proj", title="Blocker", status="todo")
    from tracertm.models.link import Link

    session.add_all([blocked, blocker, Link(id="l1", project_id="proj", source_item_id="blk1", target_item_id="b1", link_type="blocks")])
    session.commit()

    svc = ProgressService(session)
    results = svc.get_blocked_items("proj")
    assert results[0]["item_id"] == "b1"
    assert results[0]["blockers"][0]["id"] == "blk1"


def test_get_stalled_items_filters_by_threshold():
    session = _session()
    old = Item(id="old", project_id="proj", title="Old", status="in_progress", updated_at=datetime.utcnow() - timedelta(days=10))
    fresh = Item(id="fresh", project_id="proj", title="Fresh", status="in_progress", updated_at=datetime.utcnow())
    session.add_all([old, fresh])
    session.commit()

    svc = ProgressService(session)
    stalled = svc.get_stalled_items("proj", days_threshold=7)
    ids = [s["item_id"] for s in stalled]
    assert "old" in ids and "fresh" not in ids


def test_calculate_velocity_counts_created_and_completed():
    session = _session()
    now = datetime.utcnow()
    done = Item(id="done", project_id="proj", title="Done", status="complete", updated_at=now)
    created = Item(id="new", project_id="proj", title="New", status="todo", created_at=now)
    session.add_all([done, created])
    session.commit()

    svc = ProgressService(session)
    v = svc.calculate_velocity("proj", days=7)
    assert v["items_completed"] == 1
    assert v["items_created"] == 1
