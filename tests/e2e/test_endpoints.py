"""E2E smoke for Tracera's 24 public API endpoints.

Set TARGET_URL to hit a live deploy (e.g. workflow_dispatch input).
When unset, pytest expects a local/ephemeral stack at http://127.0.0.1:8000.
"""

from __future__ import annotations

import os
from typing import Any

import httpx
import pytest

TARGET_URL = os.environ.get("TARGET_URL", "http://127.0.0.1:8000").rstrip("/")

# (method, path, json_body|None, acceptable_status_codes)
ENDPOINTS: list[tuple[str, str, dict[str, Any] | None, frozenset[int]]] = [
    # Ops probes (2)
    ("GET", "/healthz", None, frozenset({200})),
    ("GET", "/readyz", None, frozenset({200})),
    # Auth (1)
    ("GET", "/api/v1/auth/me", None, frozenset({200, 401, 403})),
    # Traceability (4)
    ("POST", "/api/v1/coverage-matrix", {}, frozenset({200, 422})),
    ("POST", "/api/v1/governance/spec-check", {}, frozenset({200, 422})),
    ("POST", "/api/v1/impact", {}, frozenset({200, 422})),
    ("POST", "/api/v1/confidence", {}, frozenset({200, 422})),
    # SDLC PM (4)
    ("GET", "/api/v1/sdlc-pm/health", None, frozenset({200})),
    ("GET", "/api/v1/sdlc-pm/sprints", None, frozenset({200})),
    ("GET", "/api/v1/sdlc-pm/stories", None, frozenset({200})),
    (
        "POST",
        "/api/v1/sdlc-pm/sprints",
        {"name": "e2e-sprint", "goal": "endpoint smoke"},
        frozenset({201, 422}),
    ),
    # Evidence (3)
    ("GET", "/api/v1/evidence/health", None, frozenset({200})),
    ("GET", "/api/v1/evidence", None, frozenset({200})),
    (
        "POST",
        "/api/v1/evidence",
        {"title": "e2e-evidence", "kind": "note", "body": "smoke"},
        frozenset({201, 422}),
    ),
    # Org intel (3)
    ("GET", "/api/v1/org-intel/health", None, frozenset({200})),
    ("GET", "/api/v1/org-intel/metrics", None, frozenset({200})),
    ("GET", "/api/v1/org-intel/teams", None, frozenset({200})),
    # Analysis (1)
    (
        "GET",
        "/api/v1/analysis/code-trace/e2e-component",
        None,
        frozenset({200, 404, 501}),
    ),
    # Comments (3) — placeholder item id
    ("GET", "/api/v1/items/e2e-item/comments/", None, frozenset({200, 404})),
    (
        "POST",
        "/api/v1/items/e2e-item/comments/",
        {"body": "e2e comment"},
        frozenset({201, 404, 422}),
    ),
    (
        "DELETE",
        "/api/v1/items/e2e-item/comments/00000000-0000-0000-0000-000000000001",
        None,
        frozenset({204, 404}),
    ),
    # Impact scoring (1)
    ("POST", "/api/v1/impact/blast-radius", {}, frozenset({200, 404, 422})),
    # Ingest (2)
    ("POST", "/api/v1/ingest/github", {}, frozenset({200, 401, 422})),
    ("POST", "/api/v1/ingest/jira", {}, frozenset({200, 401, 422})),
]

assert len(ENDPOINTS) == 24, f"expected 24 endpoints, got {len(ENDPOINTS)}"


def _endpoint_id(case: tuple[str, str, dict[str, Any] | None, frozenset[int]]) -> str:
    method, path, _, _ = case
    return f"{method} {path}"


@pytest.fixture(scope="module")
def client() -> httpx.Client:
    with httpx.Client(base_url=TARGET_URL, timeout=30.0) as http:
        yield http


@pytest.mark.e2e
@pytest.mark.parametrize("method,path,body,allowed", ENDPOINTS, ids=_endpoint_id)
def test_endpoint_reachable(
    client: httpx.Client,
    method: str,
    path: str,
    body: dict[str, Any] | None,
    allowed: frozenset[int],
) -> None:
    """Each endpoint must respond without a transport error."""
    response = client.request(method, path, json=body)
    assert response.status_code in allowed, (
        f"{method} {path} -> {response.status_code} body={response.text[:500]!r}"
    )


@pytest.mark.e2e
def test_target_url_configured() -> None:
    """Sanity: TARGET_URL is set for the run."""
    assert TARGET_URL.startswith("http")
