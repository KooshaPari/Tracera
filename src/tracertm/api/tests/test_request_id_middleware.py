"""Smoke tests for the phenotype_request_id FastAPI middleware.

These tests verify that the middleware is correctly wired into the
Tracera API: it reads the inbound ``X-Request-Id`` header, generates one
when missing, and echoes it back on the response.
"""

from __future__ import annotations

from fastapi.testclient import TestClient

from tracertm.api.main import app

client = TestClient(app)


def test_middleware_runs_on_404_endpoints() -> None:
    """Even a 404 response goes through the middleware and gets a generated ID."""
    response = client.get("/api/v1/this-route-does-not-exist")
    # 404 from FastAPI, but middleware still ran.
    assert response.status_code == 404
    rid = response.headers.get("X-Request-Id")
    assert rid is not None
    assert len(rid) >= 16


def test_middleware_propagates_inbound_request_id() -> None:
    """If the client sends X-Request-Id, the middleware echoes it back unchanged."""
    inbound_id = "test-req-id-abc-123"
    response = client.post(
        "/api/v1/coverage-matrix",
        json={"links": []},
        headers={"X-Request-Id": inbound_id},
    )
    assert response.headers.get("X-Request-Id") == inbound_id


def test_middleware_generates_uuid_when_no_inbound_header() -> None:
    """When the client omits X-Request-Id, the middleware generates a uuid4 fallback."""
    response = client.post(
        "/api/v1/coverage-matrix",
        json={"links": []},
    )
    rid = response.headers.get("X-Request-Id")
    assert rid is not None
    # uuid4 hex form is 32 hex chars (no dashes here per the v0.1.0 middleware).
    assert len(rid) >= 16  # tolerate uuid4 with or without dashes
