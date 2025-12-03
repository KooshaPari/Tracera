import pytest

from tracertm.models.item import Item
from tracertm.models.link import Link
from tracertm.repositories.item_repository import ItemRepository
from tracertm.repositories.link_repository import LinkRepository
from tracertm.services.impact_analysis_service import ImpactAnalysisService
from tracertm.services.cycle_detection_service import CycleDetectionService
from tracertm.services.shortest_path_service import ShortestPathService

pytestmark = pytest.mark.integration


async def _seed_items_and_links(session, edges, project_id="proj-1"):
    items = {}
    for node in {n for edge in edges for n in edge[:2]}:
        item = Item(id=node, project_id=project_id, title=node, view="FEATURE", item_type="feature", status="todo")
        session.add(item)
        items[node] = item
    await session.commit()

    for src, tgt, ltype in edges:
        session.add(Link(id=f"{src}->{tgt}", project_id=project_id, source_item_id=src, target_item_id=tgt, link_type=ltype, metadata={}))
    await session.commit()
    return items


@pytest.mark.asyncio
async def test_impact_analysis_counts_children(async_session):
    edges = [("root", "child1", "DEPENDS_ON"), ("root", "child2", "DEPENDS_ON"), ("child1", "leaf", "DEPENDS_ON")]
    await _seed_items_and_links(async_session, edges)

    svc = ImpactAnalysisService(async_session)
    result = await svc.analyze_impact("root", max_depth=5)

    assert result.total_affected == 3
    assert result.max_depth_reached == 2
    assert result.affected_by_depth[1] == 2
    assert result.affected_by_depth[2] == 1


@pytest.mark.asyncio
async def test_cycle_detection_async_detects_cycle(async_session):
    edges = [("a", "b", "depends_on"), ("b", "a", "depends_on")]
    await _seed_items_and_links(async_session, edges)

    svc = CycleDetectionService(async_session)
    result = await svc.detect_cycles_async("proj-1")

    assert result.has_cycles is True
    assert result.total_cycles >= 1


@pytest.mark.asyncio
async def test_cycle_detection_async_respects_link_types(async_session):
    edges = [("a", "b", "tests"), ("b", "c", "implements")]
    await _seed_items_and_links(async_session, edges)

    svc = CycleDetectionService(async_session)
    result = await svc.detect_cycles_async("proj-1", link_types=["depends_on"])

    assert result.has_cycles is False


@pytest.mark.asyncio
async def test_shortest_path_service_finds_path(async_session):
    edges = [("a", "b", "depends_on"), ("b", "c", "depends_on"), ("a", "d", "depends_on")]
    await _seed_items_and_links(async_session, edges)

    svc = ShortestPathService(async_session)
    path = await svc.find_shortest_path("proj-1", "a", "c")

    assert path.exists is True
    assert path.path == ["a", "b", "c"]
    assert path.distance == 2


@pytest.mark.asyncio
async def test_shortest_path_service_no_path(async_session):
    edges = [("a", "b", "depends_on"), ("c", "d", "depends_on")]
    await _seed_items_and_links(async_session, edges)

    svc = ShortestPathService(async_session)
    path = await svc.find_shortest_path("proj-1", "a", "d")

    assert path.exists is False
    assert path.path == []
