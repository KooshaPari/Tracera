from typing import Any

import pytest

from tests.test_constants import COUNT_TWO
from tracertm.models.project import Project
from tracertm.repositories.link_repository import LinkRepository

pytestmark = pytest.mark.integration


@pytest.mark.asyncio
async def test_link_create_and_fetch(async_session: Any) -> None:
    async_session.add(Project(id="proj-1", name="Proj"))
    await async_session.commit()

    repo = LinkRepository(async_session)
    link = await repo.create("proj-1", "a", "b", "implements")

    by_id = await repo.get_by_id(str(link.id))
    assert by_id is not None
    assert by_id.source_item_id == "a"

    by_project = await repo.get_by_project("proj-1")
    assert len(by_project) == 1


@pytest.mark.asyncio
async def test_delete_and_delete_by_item(async_session: Any) -> None:
    async_session.add(Project(id="proj-1", name="Proj"))
    await async_session.commit()

    repo = LinkRepository(async_session)
    await repo.create("proj-1", "a", "b", "implements")
    await repo.create("proj-1", "a", "c", "tests")

    removed_count = await repo.delete_by_item("a")
    assert removed_count == COUNT_TWO

    remaining = await repo.get_by_project("proj-1")
    assert remaining == []
