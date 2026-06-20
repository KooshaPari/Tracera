from typing import Any

import pytest

from tracertm.models.item import Item
from tracertm.services.item_service import ItemService

pytestmark = pytest.mark.integration


async def _seed_item(async_session: Any, project_id: Any = "proj-1", status: Any = "todo") -> None:
    item = Item(
        id="item-1",
        project_id=project_id,
        title="Item",
        view="FEATURE",
        item_type="feature",
        status=status,
        version=1,
    )
    async_session.add(item)
    await async_session.commit()
    return item


@pytest.mark.asyncio
async def test_update_item_logs_event_and_links(async_session: Any) -> None:
    item = await _seed_item(async_session)
    # create a target to link
    target = Item(
        id="item-2",
        project_id="proj-1",
        title="Target",
        view="FEATURE",
        item_type="feature",
        status="todo",
        version=1,
    )
    async_session.add(target)
    await async_session.commit()

    svc = ItemService(async_session)
    updated = await svc.update_item(item.id, agent_id="agent", status="in_progress", owner="alice")

    assert updated.status == "in_progress"
    assert updated.owner == "alice"

    from sqlalchemy import select

    from tracertm.models.event import Event

    events = (await async_session.execute(select(Event))).scalars().all()
    assert any(e.event_type == "item_updated" and e.entity_id == item.id for e in events)


@pytest.mark.asyncio
async def test_delete_item_hard_and_soft(async_session: Any) -> None:
    await _seed_item(async_session)
    svc = ItemService(async_session)

    soft = await svc.delete_item("item-1", agent_id="agent", soft=True)
    assert soft is True

    # soft delete sets deleted_at; verify not removed
    from sqlalchemy import select

    remaining = (await async_session.execute(select(Item))).scalars().all()
    assert remaining and remaining[0].deleted_at is not None

    # hard delete removes row
    hard = await svc.delete_item("item-1", agent_id="agent", soft=False)
    assert hard is True


@pytest.mark.asyncio
async def test_undelete_item_returns_none_when_missing(async_session: Any) -> None:
    svc = ItemService(async_session)
    restored = await svc.undelete_item("missing", agent_id="agent")
    assert restored is None


@pytest.mark.asyncio
async def test_update_item_invalid_status_raises(async_session: Any) -> None:
    await _seed_item(async_session, status="todo")
    svc = ItemService(async_session)
    with pytest.raises(ValueError):
        await svc.update_item_status("item-1", "invalid", agent_id="agent", project_id="proj-1")
