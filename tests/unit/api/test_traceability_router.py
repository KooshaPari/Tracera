"""Unit tests for traceability router endpoints."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from tracertm.api.main import create_app


@pytest.fixture
def client() -> TestClient:
    """Create a test client with mock auth."""
    app = create_app()

    # Override auth_guard to allow test requests through
    async def mock_auth(*args, **kwargs):
        return {"sub": "test-user", "scope": "read:traces write:traces"}

    app.dependency_overrides[
        __import__('tracertm.api.deps', fromlist=['auth_guard']).auth_guard
    ] = mock_auth

    return TestClient(app)


def test_create_trace_link_happy_path(client: TestClient) -> None:
    """Test successful creation of a trace link."""
    payload = {
        "source_artifact_id": "FR-1",
        "target_artifact_id": "IMPL-1",
        "relationship": "implements",
        "confidence": 0.95,
    }

    response = client.post("/api/v1/trace-links", json=payload)

    # API may return 201 Created or 200 OK depending on implementation
    assert response.status_code in [200, 201]
    data = response.json()
    assert data["source_artifact_id"] == "FR-1"
    assert data["target_artifact_id"] == "IMPL-1"
    assert data["relationship"] == "implements"


def test_create_trace_link_missing_fields(client: TestClient) -> None:
    """Test creation fails with missing required fields."""
    payload = {
        "source_artifact_id": "FR-1",
        # Missing target_artifact_id
        "relationship": "implements",
    }

    response = client.post("/api/v1/trace-links", json=payload)

    assert response.status_code == 422


def test_create_trace_link_invalid_confidence(client: TestClient) -> None:
    """Test creation fails with invalid confidence score."""
    payload = {
        "source_artifact_id": "FR-1",
        "target_artifact_id": "IMPL-1",
        "relationship": "implements",
        "confidence": 1.5,  # Out of range [0, 1]
    }

    response = client.post("/api/v1/trace-links", json=payload)

    assert response.status_code == 422


def test_get_trace_link_happy_path(client: TestClient) -> None:
    """Test successful retrieval of a trace link."""
    # First create one
    create_payload = {
        "source_artifact_id": "FR-1",
        "target_artifact_id": "IMPL-1",
        "relationship": "implements",
        "confidence": 0.95,
    }
    create_response = client.post("/api/v1/trace-links", json=create_payload)
    assert create_response.status_code in [200, 201]
    created_link = create_response.json()
    link_id = created_link.get("id")

    # Now retrieve it
    if link_id:
        response = client.get(f"/api/v1/trace-links/{link_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["source_artifact_id"] == "FR-1"


def test_get_trace_link_not_found(client: TestClient) -> None:
    """Test retrieval of non-existent trace link."""
    response = client.get("/api/v1/trace-links/nonexistent-id")

    assert response.status_code == 404


def test_list_trace_links_happy_path(client: TestClient) -> None:
    """Test successful listing of trace links."""
    response = client.get("/api/v1/trace-links")

    assert response.status_code == 200
    data = response.json()
    # Should return a list (possibly empty)
    assert isinstance(data, list)


def test_delete_trace_link_happy_path(client: TestClient) -> None:
    """Test successful deletion of a trace link."""
    # First create one
    create_payload = {
        "source_artifact_id": "FR-1",
        "target_artifact_id": "IMPL-1",
        "relationship": "implements",
        "confidence": 0.95,
    }
    create_response = client.post("/api/v1/trace-links", json=create_payload)
    assert create_response.status_code in [200, 201]
    created_link = create_response.json()
    link_id = created_link.get("id")

    # Now delete it
    if link_id:
        response = client.delete(f"/api/v1/trace-links/{link_id}")
        assert response.status_code == 204


def test_delete_trace_link_not_found(client: TestClient) -> None:
    """Test deletion of non-existent trace link."""
    response = client.delete("/api/v1/trace-links/nonexistent-id")

    assert response.status_code == 404


def test_create_trace_link_zero_confidence(client: TestClient) -> None:
    """Test trace link creation with zero confidence."""
    payload = {
        "source_artifact_id": "FR-1",
        "target_artifact_id": "IMPL-1",
        "relationship": "implements",
        "confidence": 0.0,  # Valid edge case
    }

    response = client.post("/api/v1/trace-links", json=payload)

    assert response.status_code in [200, 201]


def test_create_trace_link_max_confidence(client: TestClient) -> None:
    """Test trace link creation with maximum confidence."""
    payload = {
        "source_artifact_id": "FR-1",
        "target_artifact_id": "IMPL-1",
        "relationship": "implements",
        "confidence": 1.0,  # Valid maximum
    }

    response = client.post("/api/v1/trace-links", json=payload)

    assert response.status_code in [200, 201]


def test_update_trace_link_happy_path(client: TestClient) -> None:
    """Test successful update of a trace link."""
    # First create one
    create_payload = {
        "source_artifact_id": "FR-1",
        "target_artifact_id": "IMPL-1",
        "relationship": "implements",
        "confidence": 0.8,
    }
    create_response = client.post("/api/v1/trace-links", json=create_payload)
    assert create_response.status_code in [200, 201]
    created_link = create_response.json()
    link_id = created_link.get("id")

    # Update it
    if link_id:
        update_payload = {
            "source_artifact_id": "FR-1",
            "target_artifact_id": "IMPL-1",
            "relationship": "implements",
            "confidence": 0.95,  # Changed confidence
        }
        response = client.put(f"/api/v1/trace-links/{link_id}", json=update_payload)
        # Depending on API design, might be 200 or 204
        assert response.status_code in [200, 201, 204]
