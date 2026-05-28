"""Integration tests for :mod:`tracertm.storage.neo4j_trace_link_writer`.

These tests spin up a real Neo4j 5 instance via ``testcontainers-neo4j``
and exercise the writer end-to-end. They are gated behind the
``integration`` pytest marker and skipped when Docker (and therefore
testcontainers) is not available on the host — matching the policy used
by the rest of the integration suite.

Functional Requirements: FR-TRACE-003 (Neo4j projection of the
traceability graph).
"""

from __future__ import annotations

import uuid
from collections.abc import Iterator
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from neo4j import Driver

# testcontainers + neo4j are optional at test-collection time; skip the
# whole module if either is missing so the unit-only CI tier keeps green.
testcontainers_neo4j = pytest.importorskip(
    "testcontainers.neo4j",
    reason="testcontainers-neo4j is required for Neo4j projection tests",
)
neo4j_pkg = pytest.importorskip(
    "neo4j",
    reason="neo4j driver is required for Neo4j projection tests",
)

from tracertm.models.trace_link import (  # noqa: E402  (after importorskip)
    Artifact,
    ArtifactKind,
    Requirement,
    RequirementStatus,
    TraceLink,
    TraceLinkType,
    VerificationMethod,
)
from tracertm.storage.neo4j_trace_link_writer import (  # noqa: E402
    apply_schema,
    write_artifact,
    write_link,
    write_requirement,
)

pytestmark = [pytest.mark.integration, pytest.mark.slow]


@pytest.fixture(scope="module")
def neo4j_driver() -> Iterator[Driver]:
    """Start a Neo4j 5 testcontainer and yield an open driver.

    Scoped per-module so the (relatively expensive) container start cost
    is amortised across all three tests. Each test uses a unique
    ``project_id`` so they don't see each other's data despite sharing
    the database.
    """
    Neo4jContainer = testcontainers_neo4j.Neo4jContainer  # noqa: N806
    GraphDatabase = neo4j_pkg.GraphDatabase  # noqa: N806

    container = Neo4jContainer("neo4j:5-community")
    container.start()
    try:
        driver = GraphDatabase.driver(
            container.get_connection_url(),
            auth=("neo4j", container.password),  # type: ignore[attr-defined]
        )
        try:
            apply_schema(driver)
            yield driver
        finally:
            driver.close()
    finally:
        container.stop()


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_apply_schema_is_idempotent(neo4j_driver: Driver) -> None:
    """Re-applying the schema must not raise (all DDL uses IF NOT EXISTS).

    Also verifies that the artifact node-key constraint and the artifact
    fulltext index are both visible to ``SHOW CONSTRAINTS`` /
    ``SHOW INDEXES`` after the first apply.
    """
    # Second apply — first apply happened in the fixture.
    apply_schema(neo4j_driver)

    with neo4j_driver.session() as session:
        constraint_names = {
            record["name"] for record in session.run("SHOW CONSTRAINTS YIELD name")
        }
        index_names = {
            record["name"] for record in session.run("SHOW INDEXES YIELD name")
        }

    assert "artifact_node_key" in constraint_names
    assert "requirement_id_unique" in constraint_names
    assert "artifact_text" in index_names


def test_write_requirement_and_artifact_are_idempotent(
    neo4j_driver: Driver,
) -> None:
    """write_requirement + write_artifact MERGE on (project_id, id).

    Calling each writer twice for the same value object must produce
    exactly one node with the latest property values.
    """
    project_id = uuid.uuid4()
    req = Requirement(
        id=uuid.uuid4(),
        project_id=project_id,
        title="REQ-1: System shall authenticate users",
        description="Initial wording",
        status=RequirementStatus.DRAFT,
        priority=3,
        acceptance_criteria=["Given valid creds, when login, then 200"],
        verification_method=VerificationMethod.TEST,
    )
    artifact = Artifact(
        id=uuid.uuid4(),
        project_id=project_id,
        kind=ArtifactKind.TEST,
        title="test_login_happy_path",
        external_id="tests/auth/test_login.py::test_happy_path",
    )

    # First write.
    write_requirement(neo4j_driver, req)
    write_artifact(neo4j_driver, artifact)

    # Second write — same ids, mutated title on the requirement.
    updated_req = req.model_copy(update={"title": "REQ-1: SSO required"})
    write_requirement(neo4j_driver, updated_req)
    write_artifact(neo4j_driver, artifact)

    with neo4j_driver.session() as session:
        req_count = session.run(
            "MATCH (r:Requirement {project_id: $pid, id: $id}) RETURN count(r) AS c",
            pid=str(project_id),
            id=str(req.id),
        ).single()["c"]
        req_title = session.run(
            "MATCH (r:Requirement {project_id: $pid, id: $id}) RETURN r.title AS t",
            pid=str(project_id),
            id=str(req.id),
        ).single()["t"]
        artifact_labels = session.run(
            "MATCH (a:Artifact {project_id: $pid, id: $id}) RETURN labels(a) AS l",
            pid=str(project_id),
            id=str(artifact.id),
        ).single()["l"]

    assert req_count == 1, "Requirement MERGE must be idempotent"
    assert req_title == "REQ-1: SSO required", "second write should update title"
    assert "Artifact" in artifact_labels
    assert "Test" in artifact_labels, "kind-specific label must be set"


def test_write_link_creates_typed_relationship_and_is_idempotent(
    neo4j_driver: Driver,
) -> None:
    """write_link creates exactly one typed edge per (src,tgt,link_type).

    Calling write_link twice for the same TraceLink id must result in a
    single SATISFIES relationship whose confidence reflects the most
    recent write.
    """
    project_id = uuid.uuid4()
    req = Requirement(
        id=uuid.uuid4(),
        project_id=project_id,
        title="REQ-2: Encrypted at rest",
    )
    code = Artifact(
        id=uuid.uuid4(),
        project_id=project_id,
        kind=ArtifactKind.CODE,
        title="storage/encryption.py",
    )
    write_requirement(neo4j_driver, req)
    write_artifact(neo4j_driver, code)

    link = TraceLink(
        project_id=project_id,
        source_artifact_id=code.id,
        target_artifact_id=req.id,
        link_type=TraceLinkType.SATISFIES,
        confidence=0.72,
        rationale="cosine(code, req) = 0.81",
    )

    write_link(neo4j_driver, link)
    # Second write of the SAME link id, but with a higher confidence —
    # idempotent MERGE must update in place, not insert a duplicate edge.
    write_link(
        neo4j_driver,
        link.model_copy(update={"confidence": 0.95}),
    )

    with neo4j_driver.session() as session:
        result = session.run(
            "MATCH (c:Artifact {id: $cid})-[l:SATISFIES]->(r:Artifact {id: $rid}) "
            "RETURN count(l) AS c, collect(l.confidence) AS confs, "
            "collect(l.rationale) AS rationales",
            cid=str(code.id),
            rid=str(req.id),
        ).single()

    assert result["c"] == 1, "SATISFIES edge MERGE must be idempotent"
    assert result["confs"] == [pytest.approx(0.95)]
    assert result["rationales"] == ["cosine(code, req) = 0.81"]
