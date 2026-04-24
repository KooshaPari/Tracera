from datetime import UTC, datetime, timedelta
from typing import Any

import pytest

from tracertm.models.event import Event
from tracertm.models.item import Item
from tracertm.services.conflict_resolution_service import ConflictResolutionService

pytestmark = pytest.mark.integration


def _seed_item(session: Any, project_id: Any = "proj-1", item_id: Any = "item-1") -> None:
    item = Item(
        id=item_id,
        project_id=project_id,
        title="Item",
        view="FEATURE",
        item_type="feature",
        status="todo",
        version=1,
    )
    session.add(item)
    session.commit()
    return item


def _event(session: Any, project_id: Any, entity_id: Any, agent: Any, minutes_ago: Any = 0) -> None:
    event = Event(
        project_id=project_id,
        event_type="item_updated",
        entity_type="item",
        entity_id=entity_id,
        agent_id=agent,
        created_at=datetime.now(UTC) - timedelta(minutes=minutes_ago),
    )
    session.add(event)
    session.commit()
    return event


def test_detect_conflicts_finds_multiple_agents(sync_session: Any) -> None:
    _seed_item(sync_session, item_id="item-1")
    _event(sync_session, "proj-1", "item-1", "agent-a", minutes_ago=1)
    _event(sync_session, "proj-1", "item-1", "agent-b", minutes_ago=0)

    svc = ConflictResolutionService(sync_session)
    conflicts = svc.detect_conflicts("proj-1", item_id="item-1", time_window_seconds=300)

    assert len(conflicts) == 1
    conflict = conflicts[0]
    assert conflict["entity_id"] == "item-1"
    assert set(conflict["conflicting_agents"]) == {"agent-a", "agent-b"}


def test_detect_conflicts_empty_when_single_agent(sync_session: Any) -> None:
    _seed_item(sync_session, item_id="item-2")
    _event(sync_session, "proj-1", "item-2", "agent-a")

    svc = ConflictResolutionService(sync_session)
    conflicts = svc.detect_conflicts("proj-1", item_id="item-2")

    assert conflicts == []


def test_resolve_conflict_last_write_and_merge(sync_session: Any) -> None:
    _seed_item(sync_session, item_id="item-3")
    # Create two events to trigger conflict path
    _event(sync_session, "proj-1", "item-3", "agent-a", minutes_ago=10)
    _event(sync_session, "proj-1", "item-3", "agent-b", minutes_ago=1)

    svc = ConflictResolutionService(sync_session)
    result = svc.resolve_conflict("proj-1", "item-3", strategy="last_write_wins")
    assert result["resolved"] is True
    assert result["strategy"] == "last_write_wins"
    assert result["winner_agent"] == "agent-b"

    merge = svc.resolve_conflict("proj-1", "item-3", strategy="merge")
    assert merge["resolved"] is True
    assert merge["strategy"] == "merge"


def test_resolve_conflict_errors(sync_session: Any) -> None:
    svc = ConflictResolutionService(sync_session)
    with pytest.raises(ValueError):
        svc.resolve_conflict("proj-1", "missing-item")

    with pytest.raises(ValueError):
        svc.resolve_conflict("proj-1", "missing-item", strategy="unknown")
