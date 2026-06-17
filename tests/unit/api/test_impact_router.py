"""Unit tests for GET /impact/forward/{id} and GET /impact/reverse/{id} endpoints.

Functional Requirements: FR-TRACE-003
"""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from tracertm.api.deps import auth_guard
from tracertm.api.handlers.impact import get_neo4j_driver
from tracertm.api.main import create_app


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

KNOWN_ARTIFACT_ID = "art-1111-aaaa"
UNKNOWN_ARTIFACT_ID = "art-9999-zzzz"

_SAMPLE_AFFECTED = [
    {
        "id": "art-2222-bbbb",
        "project_id": "proj-001",
        "kind": "test",
        "title": "Test Suite A",
        "external_id": "T-42",
        "via_link_types": ["IMPLEMENTS"],
    },
    {
        "id": "art-3333-cccc",
        "project_id": "proj-001",
        "kind": "documentation",
        "title": "Doc Page",
        "external_id": "D-7",
        "via_link_types": ["IMPLEMENTS", "VERIFIES"],
    },
]

_SAMPLE_UPSTREAM = [
    {
        "id": "art-0000-root",
        "project_id": "proj-001",
        "kind": "requirement",
        "title": "Root Requirement",
        "external_id": "FR-1",
        "via_link_types": ["SATISFIES"],
    },
]


def _make_client(
    forward_return: list[dict[str, Any]] | None = None,
    reverse_return: list[dict[str, Any]] | None = None,
) -> TestClient:
    """Build a TestClient with auth and Neo4j driver overridden."""
    app = create_app()

    async def _mock_auth(*_args: Any, **_kwargs: Any) -> dict[str, Any]:
        return {"sub": "test-user", "scope": "read:traces"}

    async def _mock_driver() -> AsyncMock:  # type: ignore[misc]
        yield AsyncMock()

    app.dependency_overrides[auth_guard] = _mock_auth
    app.dependency_overrides[get_neo4j_driver] = _mock_driver

    return TestClient(app)


# ---------------------------------------------------------------------------
# Tests: GET /api/v1/impact/forward/{artifact_id}
# ---------------------------------------------------------------------------


def test_forward_impact_200_response_structure() -> None:
    """GET /forward/{id} returns 200 with required top-level fields."""
    client = _make_client()

    with patch(
        "tracertm.api.routers.impact.query_forward_impact",
        new=AsyncMock(return_value=_SAMPLE_AFFECTED),
    ):
        response = client.get(f"/api/v1/impact/forward/{KNOWN_ARTIFACT_ID}")

    assert response.status_code == 200
    data = response.json()
    assert data["artifact_id"] == KNOWN_ARTIFACT_ID
    assert data["direction"] == "forward"
    assert "total" in data
    assert "affected" in data


def test_forward_impact_total_matches_list_length() -> None:
    """GET /forward/{id} total equals len(affected)."""
    client = _make_client()

    with patch(
        "tracertm.api.routers.impact.query_forward_impact",
        new=AsyncMock(return_value=_SAMPLE_AFFECTED),
    ):
        response = client.get(f"/api/v1/impact/forward/{KNOWN_ARTIFACT_ID}")

    data = response.json()
    assert data["total"] == len(_SAMPLE_AFFECTED)
    assert len(data["affected"]) == data["total"]


def test_forward_impact_affected_item_fields() -> None:
    """Each item in affected list contains expected artifact fields."""
    client = _make_client()

    with patch(
        "tracertm.api.routers.impact.query_forward_impact",
        new=AsyncMock(return_value=_SAMPLE_AFFECTED),
    ):
        response = client.get(f"/api/v1/impact/forward/{KNOWN_ARTIFACT_ID}")

    first = response.json()["affected"][0]
    for field in ("id", "project_id", "kind", "title", "external_id", "via_link_types"):
        assert field in first, f"Missing field: {field}"


def test_forward_impact_empty_graph() -> None:
    """GET /forward/{id} returns total=0 and empty affected when no downstream."""
    client = _make_client()

    with patch(
        "tracertm.api.routers.impact.query_forward_impact",
        new=AsyncMock(return_value=[]),
    ):
        response = client.get(f"/api/v1/impact/forward/{KNOWN_ARTIFACT_ID}")

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0
    assert data["affected"] == []


def test_forward_impact_unknown_artifact_404() -> None:
    """GET /forward/{id} with unknown artifact_id returns 404."""
    client = _make_client()

    from fastapi import HTTPException

    async def _raise_404(driver: Any, artifact_id: str) -> list[dict[str, Any]]:
        raise HTTPException(status_code=404, detail="Artifact not found")

    with patch(
        "tracertm.api.routers.impact.query_forward_impact",
        new=_raise_404,
    ):
        response = client.get(f"/api/v1/impact/forward/{UNKNOWN_ARTIFACT_ID}")

    assert response.status_code == 404


def test_forward_impact_with_mocked_graph_port_returns_known_data() -> None:
    """Forward impact with fully-mocked Neo4j session returns exact known payload."""
    app = create_app()

    async def _mock_auth(*_args: Any, **_kwargs: Any) -> dict[str, Any]:
        return {"sub": "test-user", "scope": "read:traces"}

    # Build a mock driver whose session().run().data() returns known rows
    mock_record = {
        "id": "art-2222-bbbb",
        "project_id": "proj-001",
        "kind": "test",
        "title": "Test Suite A",
        "external_id": "T-42",
        "link_types": ["IMPLEMENTS"],
    }
    mock_result = AsyncMock()
    mock_result.data = AsyncMock(return_value=[mock_record])

    mock_session = AsyncMock()
    mock_session.run = AsyncMock(return_value=mock_result)
    mock_session.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session.__aexit__ = AsyncMock(return_value=False)

    mock_driver = MagicMock()
    mock_driver.session = MagicMock(return_value=mock_session)

    async def _mock_driver_dep() -> Any:  # type: ignore[misc]
        yield mock_driver

    app.dependency_overrides[auth_guard] = _mock_auth
    app.dependency_overrides[get_neo4j_driver] = _mock_driver_dep

    client = TestClient(app)
    response = client.get(f"/api/v1/impact/forward/{KNOWN_ARTIFACT_ID}")

    assert response.status_code == 200
    data = response.json()
    assert data["artifact_id"] == KNOWN_ARTIFACT_ID
    assert data["total"] == 1
    assert data["affected"][0]["id"] == "art-2222-bbbb"
    assert data["affected"][0]["via_link_types"] == ["IMPLEMENTS"]


# ---------------------------------------------------------------------------
# Tests: GET /api/v1/impact/reverse/{artifact_id}
# ---------------------------------------------------------------------------


def test_reverse_impact_200_response_structure() -> None:
    """GET /reverse/{id} returns 200 with required top-level fields."""
    client = _make_client()

    with patch(
        "tracertm.api.routers.impact.query_reverse_impact",
        new=AsyncMock(return_value=_SAMPLE_UPSTREAM),
    ):
        response = client.get(f"/api/v1/impact/reverse/{KNOWN_ARTIFACT_ID}")

    assert response.status_code == 200
    data = response.json()
    assert data["artifact_id"] == KNOWN_ARTIFACT_ID
    assert data["direction"] == "reverse"
    assert "total" in data
    assert "upstream" in data


def test_reverse_impact_total_matches_list_length() -> None:
    """GET /reverse/{id} total equals len(upstream)."""
    client = _make_client()

    with patch(
        "tracertm.api.routers.impact.query_reverse_impact",
        new=AsyncMock(return_value=_SAMPLE_UPSTREAM),
    ):
        response = client.get(f"/api/v1/impact/reverse/{KNOWN_ARTIFACT_ID}")

    data = response.json()
    assert data["total"] == len(_SAMPLE_UPSTREAM)
    assert len(data["upstream"]) == data["total"]


def test_reverse_impact_unknown_artifact_404() -> None:
    """GET /reverse/{id} with unknown artifact_id returns 404."""
    client = _make_client()

    from fastapi import HTTPException

    async def _raise_404(driver: Any, artifact_id: str) -> list[dict[str, Any]]:
        raise HTTPException(status_code=404, detail="Artifact not found")

    with patch(
        "tracertm.api.routers.impact.query_reverse_impact",
        new=_raise_404,
    ):
        response = client.get(f"/api/v1/impact/reverse/{UNKNOWN_ARTIFACT_ID}")

    assert response.status_code == 404
