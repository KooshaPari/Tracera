from typing import Any

import pytest

from tracertm.core.concurrency import ConcurrencyError
from tracertm.models.item import Item
from tracertm.models.link import Link
from tracertm.models.project import Project
from tracertm.repositories.item_repository import ItemRepository
from tracertm.repositories.link_repository import LinkRepository

pytestmark = pytest.mark.integration


@pytest.mark.asyncio
async def test_create_and_get_item(async_session: Any) -> None:
    project = Project(id="proj-1", name="Proj")
    async_session.add(project)
    await async_session.commit()

    repo = ItemRepository(async_session)
    item = await repo.create("proj-1", "Title", "FEATURE", "feature")

    fetched = await repo.get_by_id(str(item.id), project_id="proj-1")
    assert fetched is not None
    assert fetched.title == "Title"
    assert fetched.version == 1


@pytest.mark.asyncio
async def test_update_optimistic_lock(async_session: Any) -> None:
    project = Project(id="proj-1", name="Proj")
    async_session.add(project)
    await async_session.commit()

    repo = ItemRepository(async_session)
    item = await repo.create("proj-1", "Title", "FEATURE", "feature")

    starting_version = item.version
    updated = await repo.update(str(item.id), expected_version=starting_version, status="done")
    assert updated.status == "done"
    assert updated.version == starting_version + 1

    with pytest.raises(ConcurrencyError):
        await repo.update(str(item.id), expected_version=1, status="todo")


@pytest.mark.asyncio
async def test_soft_delete_and_restore(async_session: Any) -> None:
    project = Project(id="proj-1", name="Proj")
    async_session.add(project)
    await async_session.commit()

    repo = ItemRepository(async_session)
    item = await repo.create("proj-1", "Title", "FEATURE", "feature")

    ok = await repo.delete(str(item.id), soft=True)
    assert ok is True
    # direct fetch without deleted filter
    result = await async_session.execute(__import__("sqlalchemy").select(Item).where(Item.id == item.id))
    deleted = result.scalar_one()
    assert deleted.deleted_at is not None

    restored = await repo.restore(str(item.id))
    assert restored is not None
    assert restored.deleted_at is None


@pytest.mark.asyncio
async def test_hard_delete_cascades_links(async_session: Any) -> None:
    project = Project(id="proj-1", name="Proj")
    async_session.add(project)
    await async_session.commit()

    item_repo = ItemRepository(async_session)
    link_repo = LinkRepository(async_session)

    a = await item_repo.create("proj-1", "A", "FEATURE", "feature")
    b = await item_repo.create("proj-1", "B", "FEATURE", "feature")
    link = Link(
        id="link-1",
        project_id="proj-1",
        source_item_id=a.id,
        target_item_id=b.id,
        link_type="implements",
        metadata={},
    )
    async_session.add(link)
    await async_session.commit()

    removed = await item_repo.delete(str(a.id), soft=False)
    assert removed is True
    # ensure link rows are gone
    links = await link_repo.get_by_project("proj-1")
    assert links == []
