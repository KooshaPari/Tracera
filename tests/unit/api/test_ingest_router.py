"""Unit tests for ingest router endpoints (POST /ingest/github, POST /ingest/jira).

All service and DB calls are mocked — no real connections required.
"""

from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock, patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from tracertm.api.deps import auth_guard
from tracertm.api.routers.ingest import router as ingest_router

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_FAKE_RESULT = {
    "imported": 2,
    "skipped": 0,
    "errors": [],
}


def _make_app() -> FastAPI:
    """Build a minimal FastAPI app that mounts only the ingest router."""
    app = FastAPI()
    # The ingest router declares prefix="/ingest" itself; mount at root.
    app.include_router(ingest_router)

    async def _mock_auth(*args: Any, **kwargs: Any) -> dict[str, Any]:
        return {"sub": "test-user", "scope": "write:ingest"}

    app.dependency_overrides[auth_guard] = _mock_auth
    return app


@pytest.fixture()
def client() -> TestClient:
    """TestClient with mocked auth and mocked import services."""
    app = _make_app()
    return TestClient(app)


# ---------------------------------------------------------------------------
# POST /ingest/github — happy path
# ---------------------------------------------------------------------------


def test_ingest_github_valid_payload_returns_200(client: TestClient) -> None:
    """POST /ingest/github with a valid repo + issues list returns 200/201."""
    payload = {
        "repo": "org/repo",
        "issues": [
            {"number": 1, "title": "Fix login bug", "body": "Steps to reproduce…"},
            {"number": 2, "title": "Add dark mode", "body": ""},
        ],
    }

    with patch(
        "tracertm.api.routers.ingest.GitHubImportService"
    ) as MockSvc:
        mock_instance = MagicMock()
        mock_instance.import_issues.return_value = _FAKE_RESULT
        MockSvc.return_value = mock_instance

        response = client.post("/ingest/github", json=payload)

    assert response.status_code in {200, 201}
    mock_instance.import_issues.assert_called_once_with(
        "org/repo",
        payload["issues"],
    )


def test_ingest_github_empty_issues_list_returns_200(client: TestClient) -> None:
    """POST /ingest/github with an empty issues list is a valid request."""
    payload = {"repo": "org/empty-repo", "issues": []}

    empty_result = {"imported": 0, "skipped": 0, "errors": []}

    with patch(
        "tracertm.api.routers.ingest.GitHubImportService"
    ) as MockSvc:
        mock_instance = MagicMock()
        mock_instance.import_issues.return_value = empty_result
        MockSvc.return_value = mock_instance

        response = client.post("/ingest/github", json=payload)

    assert response.status_code in {200, 201}


def test_ingest_github_response_structure(client: TestClient) -> None:
    """Response body for POST /ingest/github contains expected keys."""
    payload = {"repo": "org/repo", "issues": [{"number": 3, "title": "Bug"}]}

    expected = {"imported": 1, "skipped": 0, "errors": []}

    with patch(
        "tracertm.api.routers.ingest.GitHubImportService"
    ) as MockSvc:
        mock_instance = MagicMock()
        mock_instance.import_issues.return_value = expected
        MockSvc.return_value = mock_instance

        response = client.post("/ingest/github", json=payload)

    assert response.status_code in {200, 201}
    data = response.json()
    assert "imported" in data
    assert "skipped" in data
    assert "errors" in data
    assert data["imported"] == 1


# ---------------------------------------------------------------------------
# POST /ingest/github — validation errors
# ---------------------------------------------------------------------------


def test_ingest_github_missing_repo_returns_422(client: TestClient) -> None:
    """POST /ingest/github without 'repo' field must return 422."""
    payload = {"issues": [{"number": 1, "title": "Bug"}]}

    response = client.post("/ingest/github", json=payload)

    assert response.status_code == 422


def test_ingest_github_empty_repo_string_returns_422(client: TestClient) -> None:
    """POST /ingest/github with empty string repo must return 422 (min_length=1)."""
    payload = {"repo": "", "issues": []}

    response = client.post("/ingest/github", json=payload)

    assert response.status_code == 422


def test_ingest_github_malformed_body_returns_422(client: TestClient) -> None:
    """POST /ingest/github with non-JSON body must return 422."""
    response = client.post(
        "/ingest/github",
        content=b"not-json-at-all",
        headers={"Content-Type": "application/json"},
    )

    assert response.status_code == 422


# ---------------------------------------------------------------------------
# POST /ingest/jira — happy path
# ---------------------------------------------------------------------------


def test_ingest_jira_valid_payload_returns_200(client: TestClient) -> None:
    """POST /ingest/jira with a valid issues list returns 200/201."""
    payload = {
        "issues": [
            {"key": "PROJ-1", "summary": "Login fails", "status": "Open"},
            {"key": "PROJ-2", "summary": "API timeout", "status": "In Progress"},
        ]
    }

    with patch(
        "tracertm.api.routers.ingest.JiraImportService"
    ) as MockSvc:
        mock_instance = MagicMock()
        mock_instance.import_issues.return_value = _FAKE_RESULT
        MockSvc.return_value = mock_instance

        response = client.post("/ingest/jira", json=payload)

    assert response.status_code in {200, 201}
    mock_instance.import_issues.assert_called_once_with(payload["issues"])


def test_ingest_jira_empty_issues_list_returns_200(client: TestClient) -> None:
    """POST /ingest/jira with an empty issues list is a valid request."""
    payload = {"issues": []}

    empty_result = {"imported": 0, "skipped": 0, "errors": []}

    with patch(
        "tracertm.api.routers.ingest.JiraImportService"
    ) as MockSvc:
        mock_instance = MagicMock()
        mock_instance.import_issues.return_value = empty_result
        MockSvc.return_value = mock_instance

        response = client.post("/ingest/jira", json=payload)

    assert response.status_code in {200, 201}


def test_ingest_jira_response_structure(client: TestClient) -> None:
    """Response body for POST /ingest/jira contains expected keys."""
    payload = {"issues": [{"key": "PROJ-3", "summary": "Dark mode"}]}

    expected = {"imported": 1, "skipped": 0, "errors": []}

    with patch(
        "tracertm.api.routers.ingest.JiraImportService"
    ) as MockSvc:
        mock_instance = MagicMock()
        mock_instance.import_issues.return_value = expected
        MockSvc.return_value = mock_instance

        response = client.post("/ingest/jira", json=payload)

    assert response.status_code in {200, 201}
    data = response.json()
    assert "imported" in data
    assert "skipped" in data
    assert "errors" in data
    assert data["imported"] == 1


# ---------------------------------------------------------------------------
# POST /ingest/jira — validation errors
# ---------------------------------------------------------------------------


def test_ingest_jira_missing_issues_field_uses_default(client: TestClient) -> None:
    """POST /ingest/jira without 'issues' field should succeed (default_factory=list)."""
    with patch(
        "tracertm.api.routers.ingest.JiraImportService"
    ) as MockSvc:
        mock_instance = MagicMock()
        mock_instance.import_issues.return_value = {"imported": 0, "skipped": 0, "errors": []}
        MockSvc.return_value = mock_instance

        response = client.post("/ingest/jira", json={})

    # 'issues' has default_factory=list so missing key is valid
    assert response.status_code in {200, 201}
    mock_instance.import_issues.assert_called_once_with([])


def test_ingest_jira_malformed_body_returns_422(client: TestClient) -> None:
    """POST /ingest/jira with non-JSON body must return 422."""
    response = client.post(
        "/ingest/jira",
        content=b"{{bad json",
        headers={"Content-Type": "application/json"},
    )

    assert response.status_code == 422
