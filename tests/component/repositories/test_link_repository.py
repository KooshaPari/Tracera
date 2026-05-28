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


@pytest.mark.asyncio
async def test_store_link_with_confidence(async_session: Any) -> None:
    """LinkRepository.create persists confidence + rationale fields."""
    async_session.add(Project(id="proj-1", name="Proj"))
    await async_session.commit()

    repo = LinkRepository(async_session)
    link = await repo.create(
        "proj-1",
        "a",
        "b",
        "implements",
        confidence=0.73,
        rationale="cosine(req,art)=0.81 above tau=0.7",
    )

    fetched = await repo.get_by_id(str(link.id))
    assert fetched is not None
    assert fetched.confidence == pytest.approx(0.73)
    assert fetched.rationale == "cosine(req,art)=0.81 above tau=0.7"


@pytest.mark.asyncio
async def test_query_high_confidence_only(async_session: Any) -> None:
    """list_with_confidence filters out links below the threshold and sorts desc."""
    async_session.add(Project(id="proj-1", name="Proj"))
    await async_session.commit()

    repo = LinkRepository(async_session)
    await repo.create("proj-1", "a", "b", "implements", confidence=0.2)
    await repo.create("proj-1", "a", "c", "implements", confidence=0.95)
    await repo.create("proj-1", "a", "d", "implements", confidence=0.6)

    high = await repo.list_with_confidence(0.5, project_id="proj-1")
    assert len(high) == COUNT_TWO
    confidences = [link.confidence for link in high]
    assert confidences == sorted(confidences, reverse=True)
    assert all(c >= 0.5 for c in confidences)


@pytest.mark.asyncio
async def test_default_confidence_is_1_0(async_session: Any) -> None:
    """Omitting confidence yields 1.0 (human-curated default)."""
    async_session.add(Project(id="proj-1", name="Proj"))
    await async_session.commit()

    repo = LinkRepository(async_session)
    link = await repo.create("proj-1", "a", "b", "implements")

    fetched = await repo.get_by_id(str(link.id))
    assert fetched is not None
    assert fetched.confidence == pytest.approx(1.0)
    assert fetched.rationale is None
