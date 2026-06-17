"""Unit tests for the SDLC-PM router.

Covers:
- GET /api/v1/sdlc-pm/health → 200 with pillar + status fields
- GET /api/v1/sdlc-pm/sprints → 200, list response (initially empty)
- GET /api/v1/sdlc-pm/stories → 200, list response (initially empty)
- POST /api/v1/sdlc-pm/sprints with valid body → 201 + persisted in list
- POST /api/v1/sdlc-pm/sprints with invalid body → 422
- POST /api/v1/sdlc-pm/sprints missing required fields → 422
- Created sprint appears in subsequent GET /sprints
- SprintResponse schema shape validation
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from tracertm.api.main import create_app
from tracertm.api.routers import sdlc_pm as sdlc_pm_module


@pytest.fixture(autouse=True)
def _reset_in_memory_store() -> None:
    """Clear the module-level in-memory stores before each test for isolation."""
    sdlc_pm_module._sprints.clear()
    sdlc_pm_module._stories.clear()
    yield
    sdlc_pm_module._sprints.clear()
    sdlc_pm_module._stories.clear()


@pytest.fixture
def client() -> TestClient:
    """Return a TestClient wrapping the full FastAPI app."""
    app = create_app()
    return TestClient(app)


_SPRINT_BASE_URL = "/api/v1/sdlc-pm"

_VALID_SPRINT_PAYLOAD = {
    "name": "Sprint 1",
    "goal": "Ship traceability pillar MVP",
    "start_date": "2026-06-01T00:00:00Z",
    "end_date": "2026-06-14T00:00:00Z",
}


class TestSdlcPmHealth:
    """GET /sdlc-pm/health endpoint."""

    def test_health_returns_200(self, client: TestClient) -> None:
        """Health endpoint must return HTTP 200."""
        response = client.get(f"{_SPRINT_BASE_URL}/health")
        assert response.status_code == 200

    def test_health_body_has_status_ok(self, client: TestClient) -> None:
        """Health body must contain status=ok."""
        response = client.get(f"{_SPRINT_BASE_URL}/health")
        data = response.json()
        assert data["status"] == "ok"

    def test_health_body_identifies_pillar(self, client: TestClient) -> None:
        """Health body must identify the sdlc_pm pillar."""
        response = client.get(f"{_SPRINT_BASE_URL}/health")
        data = response.json()
        assert data["pillar"] == "sdlc_pm"


class TestListSprints:
    """GET /sdlc-pm/sprints endpoint."""

    def test_list_sprints_returns_200(self, client: TestClient) -> None:
        """GET /sprints returns 200."""
        response = client.get(f"{_SPRINT_BASE_URL}/sprints")
        assert response.status_code == 200

    def test_list_sprints_initially_empty(self, client: TestClient) -> None:
        """GET /sprints returns an empty list when no sprints exist."""
        response = client.get(f"{_SPRINT_BASE_URL}/sprints")
        assert response.json() == []

    def test_list_sprints_returns_list_type(self, client: TestClient) -> None:
        """GET /sprints response body is a JSON array."""
        response = client.get(f"{_SPRINT_BASE_URL}/sprints")
        assert isinstance(response.json(), list)


class TestListStories:
    """GET /sdlc-pm/stories endpoint."""

    def test_list_stories_returns_200(self, client: TestClient) -> None:
        """GET /stories returns 200."""
        response = client.get(f"{_SPRINT_BASE_URL}/stories")
        assert response.status_code == 200

    def test_list_stories_initially_empty(self, client: TestClient) -> None:
        """GET /stories returns an empty list when no stories exist."""
        response = client.get(f"{_SPRINT_BASE_URL}/stories")
        assert response.json() == []

    def test_list_stories_returns_list_type(self, client: TestClient) -> None:
        """GET /stories response body is a JSON array."""
        response = client.get(f"{_SPRINT_BASE_URL}/stories")
        assert isinstance(response.json(), list)


class TestCreateSprint:
    """POST /sdlc-pm/sprints endpoint."""

    def test_create_sprint_valid_returns_201(self, client: TestClient) -> None:
        """POST /sprints with valid body returns 201."""
        response = client.post(f"{_SPRINT_BASE_URL}/sprints", json=_VALID_SPRINT_PAYLOAD)
        assert response.status_code == 201

    def test_create_sprint_response_contains_id(self, client: TestClient) -> None:
        """Created sprint response includes a non-empty id."""
        response = client.post(f"{_SPRINT_BASE_URL}/sprints", json=_VALID_SPRINT_PAYLOAD)
        data = response.json()
        assert "id" in data
        assert data["id"]

    def test_create_sprint_response_echoes_name(self, client: TestClient) -> None:
        """Created sprint response echoes the submitted name."""
        response = client.post(f"{_SPRINT_BASE_URL}/sprints", json=_VALID_SPRINT_PAYLOAD)
        data = response.json()
        assert data["name"] == _VALID_SPRINT_PAYLOAD["name"]

    def test_create_sprint_response_echoes_goal(self, client: TestClient) -> None:
        """Created sprint response echoes the submitted goal."""
        response = client.post(f"{_SPRINT_BASE_URL}/sprints", json=_VALID_SPRINT_PAYLOAD)
        data = response.json()
        assert data["goal"] == _VALID_SPRINT_PAYLOAD["goal"]

    def test_create_sprint_default_status_is_planned(self, client: TestClient) -> None:
        """Newly created sprint defaults to status=planned."""
        response = client.post(f"{_SPRINT_BASE_URL}/sprints", json=_VALID_SPRINT_PAYLOAD)
        data = response.json()
        assert data["status"] == "planned"

    def test_create_sprint_includes_timestamps(self, client: TestClient) -> None:
        """Created sprint response includes created_at and updated_at."""
        response = client.post(f"{_SPRINT_BASE_URL}/sprints", json=_VALID_SPRINT_PAYLOAD)
        data = response.json()
        assert "created_at" in data
        assert "updated_at" in data

    def test_create_sprint_appears_in_list(self, client: TestClient) -> None:
        """Sprint created via POST is returned in subsequent GET /sprints."""
        post_resp = client.post(
            f"{_SPRINT_BASE_URL}/sprints", json=_VALID_SPRINT_PAYLOAD
        )
        created_id = post_resp.json()["id"]

        get_resp = client.get(f"{_SPRINT_BASE_URL}/sprints")
        ids = [s["id"] for s in get_resp.json()]
        assert created_id in ids

    def test_create_sprint_missing_name_returns_422(self, client: TestClient) -> None:
        """POST /sprints without 'name' field returns 422 Unprocessable Entity."""
        payload = {k: v for k, v in _VALID_SPRINT_PAYLOAD.items() if k != "name"}
        response = client.post(f"{_SPRINT_BASE_URL}/sprints", json=payload)
        assert response.status_code == 422

    def test_create_sprint_missing_goal_returns_422(self, client: TestClient) -> None:
        """POST /sprints without 'goal' field returns 422 Unprocessable Entity."""
        payload = {k: v for k, v in _VALID_SPRINT_PAYLOAD.items() if k != "goal"}
        response = client.post(f"{_SPRINT_BASE_URL}/sprints", json=payload)
        assert response.status_code == 422

    def test_create_sprint_empty_name_returns_422(self, client: TestClient) -> None:
        """POST /sprints with empty-string 'name' returns 422 (min_length=1)."""
        payload = {**_VALID_SPRINT_PAYLOAD, "name": ""}
        response = client.post(f"{_SPRINT_BASE_URL}/sprints", json=payload)
        assert response.status_code == 422

    def test_create_sprint_missing_dates_returns_422(self, client: TestClient) -> None:
        """POST /sprints without date fields returns 422."""
        payload = {"name": "No Dates Sprint", "goal": "some goal"}
        response = client.post(f"{_SPRINT_BASE_URL}/sprints", json=payload)
        assert response.status_code == 422

    def test_create_multiple_sprints_all_appear_in_list(
        self, client: TestClient
    ) -> None:
        """Multiple POST /sprints calls each appear in GET /sprints."""
        ids = set()
        for i in range(3):
            payload = {**_VALID_SPRINT_PAYLOAD, "name": f"Sprint {i}"}
            resp = client.post(f"{_SPRINT_BASE_URL}/sprints", json=payload)
            assert resp.status_code == 201
            ids.add(resp.json()["id"])

        list_resp = client.get(f"{_SPRINT_BASE_URL}/sprints")
        listed_ids = {s["id"] for s in list_resp.json()}
        assert ids.issubset(listed_ids)
