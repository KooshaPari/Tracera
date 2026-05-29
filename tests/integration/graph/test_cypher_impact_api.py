"""Integration tests for Cypher-based impact analysis API.

Tests both handler-level Cypher execution and the HTTP layer for the two
impact endpoints.

Markers
-------
* ``integration`` — requires a live Neo4j instance (set NEO4J_URI env var)
* ``slow``        — full end-to-end graph traversal; excluded from fast CI

"""

from __future__ import annotations

import uuid
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient

pytestmark = [pytest.mark.integration, pytest.mark.slow]


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def artifact_ids() -> dict[str, str]:
    """Return a small set of stable UUIDs for graph fixtures."""
    return {
        "req": str(uuid.UUID("aaaaaaaa-0000-0000-0000-000000000001")),
        "design": str(uuid.UUID("aaaaaaaa-0000-0000-0000-000000000002")),
        "code": str(uuid.UUID("aaaaaaaa-0000-0000-0000-000000000003")),
        "test": str(uuid.UUID("aaaaaaaa-0000-0000-0000-000000000004")),
    }


def _make_record(artifact_id: str, kind: str, title: str, link_types: list[str]) -> dict[str, Any]:
    """Build a fake Neo4j record dict matching ``_row_to_artifact`` expectations."""
    return {
        "id": artifact_id,
        "project_id": str(uuid.UUID("bbbbbbbb-0000-0000-0000-000000000001")),
        "kind": kind,
        "title": title,
        "external_id": None,
        "link_types": link_types,
    }


# ---------------------------------------------------------------------------
# Unit-style: handler functions (mocked driver)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_query_forward_impact_returns_affected_artifacts(
    artifact_ids: dict[str, str],
) -> None:
    """Forward impact query returns downstream artifacts from Neo4j records.

    Uses a mocked AsyncDriver so no live Neo4j is required for this assertion.
    """
    from tracertm.api.handlers.impact import query_forward_impact

    design_record = _make_record(
        artifact_ids["design"],
        "design",
        "System Design Doc",
        ["SATISFIES"],
    )
    code_record = _make_record(
        artifact_ids["code"],
        "code",
        "auth.py",
        ["SATISFIES", "IMPLEMENTS"],
    )

    # Build a mock session whose .run().data() returns two records
    mock_result = AsyncMock()
    mock_result.data = AsyncMock(return_value=[design_record, code_record])
    mock_session = AsyncMock()
    mock_session.run = AsyncMock(return_value=mock_result)
    mock_session.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session.__aexit__ = AsyncMock(return_value=False)

    mock_driver = MagicMock()
    mock_driver.session = MagicMock(return_value=mock_session)

    result = await query_forward_impact(mock_driver, artifact_ids["req"])

    assert len(result) == 2
    ids = {r["id"] for r in result}
    assert artifact_ids["design"] in ids
    assert artifact_ids["code"] in ids
    # Check shape of one item
    design_item = next(r for r in result if r["id"] == artifact_ids["design"])
    assert design_item["kind"] == "design"
    assert "SATISFIES" in design_item["via_link_types"]


@pytest.mark.asyncio
async def test_query_reverse_impact_returns_upstream_artifacts(
    artifact_ids: dict[str, str],
) -> None:
    """Reverse impact query returns upstream artifacts from Neo4j records.

    Uses a mocked AsyncDriver — no live Neo4j required.
    """
    from tracertm.api.handlers.impact import query_reverse_impact

    req_record = _make_record(
        artifact_ids["req"],
        "requirement",
        "FR-001 Auth",
        ["SATISFIES"],
    )

    mock_result = AsyncMock()
    mock_result.data = AsyncMock(return_value=[req_record])
    mock_session = AsyncMock()
    mock_session.run = AsyncMock(return_value=mock_result)
    mock_session.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session.__aexit__ = AsyncMock(return_value=False)

    mock_driver = MagicMock()
    mock_driver.session = MagicMock(return_value=mock_session)

    result = await query_reverse_impact(mock_driver, artifact_ids["code"])

    assert len(result) == 1
    assert result[0]["id"] == artifact_ids["req"]
    assert result[0]["kind"] == "requirement"


# ---------------------------------------------------------------------------
# HTTP layer: FastAPI TestClient (mocked Neo4j + auth)
# ---------------------------------------------------------------------------


@pytest.fixture
def app_client() -> TestClient:
    """Return a TestClient with auth and Neo4j driver mocked out."""
    from fastapi import FastAPI

    # Import the exact function objects used inside the router's Depends() calls
    from tracertm.api.deps import auth_guard
    from tracertm.api.handlers.impact import get_neo4j_driver
    from tracertm.api.routers.impact import router

    test_app = FastAPI()
    test_app.include_router(router, prefix="/api/v1")

    # Override the exact function objects referenced by Depends() in the router
    test_app.dependency_overrides[auth_guard] = lambda: {"sub": "test-user"}

    # Stub Neo4j driver — returns empty lists by default
    async def _stub_driver() -> None:  # type: ignore[return]
        mock_result = AsyncMock()
        mock_result.data = AsyncMock(return_value=[])
        mock_session = AsyncMock()
        mock_session.run = AsyncMock(return_value=mock_result)
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=False)

        mock_driver = MagicMock()
        mock_driver.session = MagicMock(return_value=mock_session)
        yield mock_driver

    test_app.dependency_overrides[get_neo4j_driver] = _stub_driver

    return TestClient(test_app)


def test_forward_impact_endpoint_returns_200(
    app_client: TestClient,
    artifact_ids: dict[str, str],
) -> None:
    """GET /api/v1/impact/forward/{id} returns 200 with expected JSON shape."""
    resp = app_client.get(f"/api/v1/impact/forward/{artifact_ids['req']}")
    assert resp.status_code == 200
    body = resp.json()
    assert body["artifact_id"] == artifact_ids["req"]
    assert body["direction"] == "forward"
    assert isinstance(body["total"], int)
    assert isinstance(body["affected"], list)


def test_reverse_impact_endpoint_returns_200(
    app_client: TestClient,
    artifact_ids: dict[str, str],
) -> None:
    """GET /api/v1/impact/reverse/{id} returns 200 with expected JSON shape."""
    resp = app_client.get(f"/api/v1/impact/reverse/{artifact_ids['code']}")
    assert resp.status_code == 200
    body = resp.json()
    assert body["artifact_id"] == artifact_ids["code"]
    assert body["direction"] == "reverse"
    assert isinstance(body["total"], int)
    assert isinstance(body["upstream"], list)


# ---------------------------------------------------------------------------
# Live-gated spine verification: seed → store → query round-trip
# ---------------------------------------------------------------------------


@pytest.mark.integration
@pytest.mark.live_neo4j
def test_seed_forward_reverse_roundtrip_live() -> None:
    """Seed a minimal graph into live Neo4j and verify forward+reverse impact.

    Requires NEO4J_URI (default bolt://localhost:7687) to be reachable.
    Skips automatically when the driver cannot connect.

    Verifies the requirements-traceability spine end-to-end.
    """
    import os

    try:
        import neo4j
    except ImportError:
        pytest.skip("neo4j driver not installed")

    from tracertm.models.trace_link import (
        Artifact,
        ArtifactKind,
        Requirement,
        RequirementStatus,
        TraceLink,
        TraceLinkType,
    )
    from tracertm.storage.neo4j_trace_link_writer import (
        apply_schema,
        write_artifact,
        write_link,
        write_requirement,
    )

    uri = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
    user = os.environ.get("NEO4J_USER", "neo4j")
    password = os.environ.get("NEO4J_PASSWORD", "tracertm_password")

    try:
        driver = neo4j.GraphDatabase.driver(uri, auth=(user, password))
        driver.verify_connectivity()
    except Exception as exc:
        pytest.skip(f"Neo4j not reachable at {uri}: {exc}")

    # Use deterministic UUIDs isolated to this test.
    import uuid

    ns = uuid.UUID("12345678-1234-5678-1234-567812345678")
    proj_id = uuid.uuid5(ns, "test-spine-project")
    req_id = uuid.uuid5(ns, "req-FR-SPINE-001")
    pr_id = uuid.uuid5(ns, "artifact-PR#999")
    lnk_id = uuid.uuid5(ns, f"{pr_id}:{req_id}:SATISFIES")

    try:
        apply_schema(driver)

        req = Requirement(
            id=req_id,
            project_id=proj_id,
            title="FR-SPINE-001 Spine Verification",
            description="Spine integration test requirement",
            external_id="FR-SPINE-001",
            status=RequirementStatus.VERIFIED,
        )
        write_requirement(driver, req)

        pr = Artifact(
            id=pr_id,
            project_id=proj_id,
            kind=ArtifactKind.CODE,
            title="PR#999",
            external_id="PR#999",
        )
        write_artifact(driver, pr)

        link = TraceLink(
            id=lnk_id,
            project_id=proj_id,
            source_artifact_id=pr_id,
            target_artifact_id=req_id,
            link_type=TraceLinkType.SATISFIES,
            confidence=1.0,
            rationale="spine test",
        )
        write_link(driver, link)

        # Forward impact: what artifacts trace to FR-SPINE-001?
        with driver.session() as session:
            fwd = session.run(
                "MATCH (r:Requirement {external_id: $eid})<-[l]-(a:Artifact) "
                "RETURN type(l) AS ltype, a.external_id AS aid",
                eid="FR-SPINE-001",
            ).data()

        assert len(fwd) >= 1, f"Forward query returned no results: {fwd}"
        artifact_ids_fwd = {row["aid"] for row in fwd}
        assert "PR#999" in artifact_ids_fwd, f"PR#999 not in forward results: {artifact_ids_fwd}"
        assert any(row["ltype"] == "SATISFIES" for row in fwd)

        # Reverse impact: what requirement does PR#999 satisfy?
        with driver.session() as session:
            rev = session.run(
                "MATCH (a:Artifact {external_id: $eid})-[l]->(r:Requirement) "
                "RETURN type(l) AS ltype, r.external_id AS rid, r.status AS status",
                eid="PR#999",
            ).data()

        assert len(rev) >= 1, f"Reverse query returned no results: {rev}"
        req_ids_rev = {row["rid"] for row in rev}
        assert "FR-SPINE-001" in req_ids_rev, f"FR-SPINE-001 not in reverse results: {req_ids_rev}"
        assert rev[0]["status"] == "verified"

    finally:
        # Clean up only the test-isolated nodes.
        with driver.session() as session:
            session.run(
                "MATCH (n:Artifact {project_id: $pid}) DETACH DELETE n",
                pid=str(proj_id),
            )
        driver.close()
