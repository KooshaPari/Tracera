"""Unit tests for impact scoring router endpoints."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from tracertm.api.main import create_app
from tracertm.models.trace_link import Artifact, TraceLink


@pytest.fixture
def client() -> TestClient:
    """Create a test client with mock auth."""
    app = create_app()

    # Override auth_guard to allow test requests through
    async def mock_auth(*args, **kwargs):
        return {"sub": "test-user", "scope": "read:traces"}

    app.dependency_overrides[
        __import__('tracertm.api.deps', fromlist=['auth_guard']).auth_guard
    ] = mock_auth

    return TestClient(app)


def test_blast_radius_happy_path(client: TestClient) -> None:
    """Test successful blast radius computation."""
    payload = {
        "artifact_id": "FR-1",
        "artifacts": [
            {"id": "FR-1", "kind": "requirement", "title": "Feature 1"},
            {"id": "IMPL-1", "kind": "implementation", "title": "Implementation 1"},
            {"id": "TEST-1", "kind": "test", "title": "Test 1"},
        ],
        "links": [
            {
                "source_artifact_id": "FR-1",
                "target_artifact_id": "IMPL-1",
                "relationship": "implements",
                "confidence": 0.95,
            },
            {
                "source_artifact_id": "IMPL-1",
                "target_artifact_id": "TEST-1",
                "relationship": "verifies",
                "confidence": 0.88,
            },
        ],
        "depth": 5,
    }

    response = client.post("/api/v1/impact/blast-radius", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert "artifact_id" in data
    assert "affected_count" in data or "affected" in data


def test_blast_radius_empty_graph(client: TestClient) -> None:
    """Test blast radius with empty artifact graph."""
    payload = {
        "artifact_id": "FR-1",
        "artifacts": [{"id": "FR-1", "kind": "requirement", "title": "Feature 1"}],
        "links": [],
        "depth": 5,
    }

    response = client.post("/api/v1/impact/blast-radius", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["artifact_id"] == "FR-1"


def test_blast_radius_invalid_depth(client: TestClient) -> None:
    """Test blast radius with invalid depth parameter."""
    payload = {
        "artifact_id": "FR-1",
        "artifacts": [{"id": "FR-1", "kind": "requirement", "title": "Feature 1"}],
        "links": [],
        "depth": 21,  # Exceeds max of 20
    }

    response = client.post("/api/v1/impact/blast-radius", json=payload)

    # Should validate depth constraint
    assert response.status_code == 422


def test_blast_radius_missing_artifact_id(client: TestClient) -> None:
    """Test blast radius with missing artifact_id."""
    payload = {
        "artifacts": [{"id": "FR-1", "kind": "requirement", "title": "Feature 1"}],
        "links": [],
        "depth": 5,
    }

    response = client.post("/api/v1/impact/blast-radius", json=payload)

    assert response.status_code == 422


def test_blast_radius_empty_artifact_id(client: TestClient) -> None:
    """Test blast radius with empty artifact_id string."""
    payload = {
        "artifact_id": "",  # Empty string
        "artifacts": [{"id": "FR-1", "kind": "requirement", "title": "Feature 1"}],
        "links": [],
        "depth": 5,
    }

    response = client.post("/api/v1/impact/blast-radius", json=payload)

    assert response.status_code == 422


def test_blast_radius_multiple_levels(client: TestClient) -> None:
    """Test blast radius with multi-level dependency chain."""
    payload = {
        "artifact_id": "FR-1",
        "artifacts": [
            {"id": "FR-1", "kind": "requirement", "title": "Feature 1"},
            {"id": "IMPL-1", "kind": "implementation", "title": "Implementation 1"},
            {"id": "TEST-1", "kind": "test", "title": "Test 1"},
            {"id": "DOC-1", "kind": "documentation", "title": "Documentation 1"},
        ],
        "links": [
            {
                "source_artifact_id": "FR-1",
                "target_artifact_id": "IMPL-1",
                "relationship": "implements",
                "confidence": 1.0,
            },
            {
                "source_artifact_id": "IMPL-1",
                "target_artifact_id": "TEST-1",
                "relationship": "verifies",
                "confidence": 0.95,
            },
            {
                "source_artifact_id": "TEST-1",
                "target_artifact_id": "DOC-1",
                "relationship": "documents",
                "confidence": 0.85,
            },
        ],
        "depth": 5,
    }

    response = client.post("/api/v1/impact/blast-radius", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["artifact_id"] == "FR-1"


def test_blast_radius_zero_depth(client: TestClient) -> None:
    """Test blast radius with zero depth (should be invalid)."""
    payload = {
        "artifact_id": "FR-1",
        "artifacts": [{"id": "FR-1", "kind": "requirement", "title": "Feature 1"}],
        "links": [],
        "depth": 0,  # Below minimum of 1
    }

    response = client.post("/api/v1/impact/blast-radius", json=payload)

    assert response.status_code == 422
