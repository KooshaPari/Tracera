from datetime import UTC, datetime
from types import SimpleNamespace
from typing import Any, cast
from uuid import uuid4

import pytest
import pytest_asyncio
from fastapi import HTTPException
from httpx import ASGITransport, AsyncClient

from tests.test_constants import COUNT_THREE, COUNT_TWO, HTTP_INTERNAL_SERVER_ERROR, HTTP_NOT_FOUND, HTTP_OK
from tracertm.api import main


class _FakeItem:
    def __init__(self, item_id: str, title: str, view: str = "FEATURE", status: str = "OPEN") -> None:
        self.id = item_id
        self.title = title
        self.view = view
        self.status = status
        now = datetime.now(UTC)
        self.created_at = now
        self.updated_at = now
        self.description = f"{title} description"


class _FakeLink:
    def __init__(self, link_id: str, source: str, target: str, link_type: str = "DEPENDS_ON") -> None:
        self.id = link_id
        self.source_item_id = source
        self.target_item_id = target
        self.link_type = link_type


class _FakeItemRepository:
    _seeded_ids = ["item-a", "item-b", "item-c"]

    def __init__(self, _db: Any) -> None:
        self._items = [
            _FakeItem(self._seeded_ids[0], "Item A"),
            _FakeItem(self._seeded_ids[1], "Item B"),
            _FakeItem(self._seeded_ids[2], "Item C"),
        ]

    async def get_by_project(self, _project_id: str) -> None:
        return self._items

    async def get_by_id(self, item_id: str) -> None:
        return next((item for item in self._items if item.id == item_id), None)


class _FakeLinkRepository:
    def __init__(self, _db: Any) -> None:
        self._links = [
            _FakeLink(str(uuid4()), "source-1", "target-1"),
            _FakeLink(str(uuid4()), "source-2", "target-2"),
        ]

    async def get_by_project(self, _project_id: str) -> None:
        return self._links


class _FakeImpactService:
    def __init__(self, _db: Any) -> None:
        pass

    async def analyze_impact(self, item_id: str) -> None:
        return SimpleNamespace(
            root_item_id=item_id,
            total_affected=2,
            max_depth_reached=3,
            affected_items=["a1", "a2"],
        )


class _FakeCycleService:
    def __init__(self, _db: Any) -> None:
        pass

    async def detect_cycles(self, _project_id: str) -> None:
        return SimpleNamespace(has_cycles=True, total_cycles=1, severity="medium", affected_items={"n1", "n2"})


class _FakeShortestPathService:
    def __init__(self, _db: Any) -> None:
        pass

    async def find_shortest_path(self, project_id: str, source_id: str, _target_id: str) -> None:
        return SimpleNamespace(exists=True, distance=2, path=[source_id, "mid", target_id], link_types=["DEPENDS_ON"])


@pytest.fixture(autouse=True)
def reset_overrides() -> None:
    main.app.dependency_overrides.clear()
    yield
    main.app.dependency_overrides.clear()


@pytest.fixture(autouse=True)
def patch_repositories(monkeypatch: Any) -> None:
    monkeypatch.setattr("tracertm.repositories.item_repository.ItemRepository", _FakeItemRepository)
    monkeypatch.setattr("tracertm.repositories.link_repository.LinkRepository", _FakeLinkRepository)
    monkeypatch.setattr("tracertm.services.impact_analysis_service.ImpactAnalysisService", _FakeImpactService)
    monkeypatch.setattr("tracertm.services.cycle_detection_service.CycleDetectionService", _FakeCycleService)
    monkeypatch.setattr("tracertm.services.shortest_path_service.ShortestPathService", _FakeShortestPathService)


@pytest_asyncio.fixture
async def client() -> None:
    async def fake_db() -> None:
        yield object()

    main.app.dependency_overrides[main.get_db] = fake_db
    transport = ASGITransport(app=main.app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient) -> None:
    response = await client.get("/health")
    assert response.status_code == HTTP_OK
    payload = response.json()
    assert payload["status"] == "healthy"
    assert payload["service"] == "TraceRTM API"


@pytest.mark.asyncio
async def test_list_items_returns_paginated_subset(client: AsyncClient) -> None:
    response = await client.get("/api/v1/items", params={"project_id": "p1", "skip": 1, "limit": 1})
    assert response.status_code == HTTP_OK
    payload = response.json()
    assert payload["total"] == COUNT_THREE
    assert len(payload["items"]) == 1
    assert {"id", "title", "view", "status"}.issubset(payload["items"][0].keys())


@pytest.mark.asyncio
async def test_get_item_returns_data(client: AsyncClient) -> None:
    target_id = _FakeItemRepository._seeded_ids[0]
    response = await client.get(f"/api/v1/items/{target_id}")
    assert response.status_code == HTTP_OK
    payload = response.json()
    assert payload["id"] == target_id
    assert payload["title"]
    assert payload["status"]


@pytest.mark.asyncio
async def test_get_item_not_found_returns_404(client: AsyncClient) -> None:
    response = await client.get("/api/v1/items/missing-id")
    assert response.status_code == HTTP_NOT_FOUND


@pytest.mark.asyncio
async def test_list_links(client: AsyncClient) -> None:
    response = await client.get("/api/v1/links", params={"project_id": "p1"})
    assert response.status_code == HTTP_OK
    payload = response.json()
    assert payload["total"] == COUNT_TWO
    assert len(payload["links"]) == COUNT_TWO
    assert {"id", "source_id", "target_id", "type"}.issubset(payload["links"][0].keys())


@pytest.mark.asyncio
async def test_get_impact_analysis(client: AsyncClient) -> None:
    response = await client.get("/api/v1/analysis/impact/item-1", params={"project_id": "p1"})
    assert response.status_code == HTTP_OK
    payload = response.json()
    assert payload["root_item_id"] == "item-1"
    assert payload["total_affected"] == COUNT_TWO
    assert payload["max_depth"] == COUNT_THREE
    assert payload["affected_items"] == ["a1", "a2"]


@pytest.mark.asyncio
async def test_detect_cycles(client: AsyncClient) -> None:
    response = await client.get("/api/v1/analysis/cycles/p1")
    assert response.status_code == HTTP_OK
    payload = response.json()
    assert payload["has_cycles"] is True
    assert payload["total_cycles"] == 1
    assert payload["severity"] == "medium"
    assert set(payload["affected_items"]) == {"n1", "n2"}


@pytest.mark.asyncio
async def test_find_shortest_path(client: AsyncClient) -> None:
    response = await client.get(
        "/api/v1/analysis/shortest-path",
        params={"project_id": "p1", "source_id": "a", "target_id": "b"},
    )
    assert response.status_code == HTTP_OK
    payload = response.json()
    assert payload["exists"] is True
    assert payload["distance"] == COUNT_TWO
    assert payload["path"] == ["a", "mid", "b"]
    assert payload["link_types"] == ["DEPENDS_ON"]


@pytest.mark.asyncio
async def test_get_db_raises_when_missing_database_url(monkeypatch: Any) -> None:
    monkeypatch.setattr("tracertm.config.manager.ConfigManager.get", lambda self, _key: None)
    with pytest.raises(HTTPException) as exc_info:
        await anext(main.get_db())
    exc = cast("HTTPException", exc_info.value)
    assert exc.status_code == HTTP_INTERNAL_SERVER_ERROR
