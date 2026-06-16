"""Neo4j trace-link writer with guarded driver import and in-memory fallback."""
from __future__ import annotations

from typing import TYPE_CHECKING, Any
from uuid import UUID

from tracertm.models.trace_link import (
    Artifact,
    ArtifactKind,
    Requirement,
    TraceLink,
    TraceLinkType,
)

if TYPE_CHECKING:
    from neo4j import Driver

# Guarded import of neo4j -------------------------------------------------
try:
    import neo4j  # noqa: F401
    _NEO4J_AVAILABLE = True
except Exception:  # pragma: no cover
    _NEO4J_AVAILABLE = False

# In-memory fallback store --------------------------------------------------
_MEMORY_STORE: dict[str, Any] = {
    "artifacts": {},
    "requirements": {},
    "links": {},
}


def _artifact_to_record(artifact: Artifact) -> dict[str, Any]:
    return {
        "id": str(artifact.id),
        "project_id": str(artifact.project_id),
        "kind": artifact.kind.value,
        "title": artifact.title,
        "description": artifact.description,
        "external_id": artifact.external_id,
        "metadata": artifact.metadata,
        "created_at": artifact.created_at,
        "updated_at": artifact.updated_at,
    }


def _requirement_to_record(req: Requirement) -> dict[str, Any]:
    rec = _artifact_to_record(req)
    rec.update({
        "status": req.status.value,
        "priority": req.priority,
        "rationale": req.rationale,
        "acceptance_criteria": req.acceptance_criteria,
        "verification_method": req.verification_method,
    })
    return rec


def _link_to_record(link: TraceLink) -> dict[str, Any]:
    return {
        "link_id": str(link.id) if link.id else str(link.project_id) + "::link",
        "project_id": str(link.project_id),
        "source_id": str(link.source_artifact_id),
        "target_id": str(link.target_artifact_id),
        "rel_type": link.link_type.value,
        "confidence": link.confidence,
        "rationale": link.rationale,
        "metadata": link.metadata,
        "created_at": link.created_at,
        "updated_at": link.updated_at,
    }


def write_artifact(driver: Any, artifact: Artifact) -> None:
    """Upsert an Artifact node in Neo4j (or in-memory fallback)."""
    if not _NEO4J_AVAILABLE or driver is None:
        _MEMORY_STORE["artifacts"][str(artifact.id)] = artifact
        return
    cypher = """
MERGE (a:Artifact {id: $id})
SET a.project_id = $project_id,
    a.kind = $kind,
    a.title = $title,
    a.description = $description,
    a.external_id = $external_id,
    a.metadata = $metadata,
    a.created_at = $created_at,
    a.updated_at = $updated_at
"""
    with driver.session() as session:
        session.run(cypher, **_artifact_to_record(artifact))


def write_requirement(driver: Any, requirement: Requirement) -> None:
    """Upsert a Requirement node (labelled Artifact:Requirement) in Neo4j."""
    if not _NEO4J_AVAILABLE or driver is None:
        _MEMORY_STORE["requirements"][str(requirement.id)] = requirement
        return
    cypher = """
MERGE (a:Artifact:Requirement {id: $id})
SET a.project_id = $project_id,
    a.kind = $kind,
    a.title = $title,
    a.description = $description,
    a.external_id = $external_id,
    a.metadata = $metadata,
    a.created_at = $created_at,
    a.updated_at = $updated_at,
    a.status = $status,
    a.priority = $priority,
    a.rationale = $rationale,
    a.acceptance_criteria = $acceptance_criteria,
    a.verification_method = $verification_method
"""
    with driver.session() as session:
        session.run(cypher, **_requirement_to_record(requirement))


def write_link(driver: Any, link: TraceLink) -> None:
    """Upsert a TraceLink relationship between two Artifacts in Neo4j."""
    if not _NEO4J_AVAILABLE or driver is None:
        _MEMORY_STORE["links"][str(link.id or link.project_id) + "::link"] = link
        return
    cypher = f"""
MATCH (src:Artifact {{id: $source_id}})
MATCH (dst:Artifact {{id: $target_id}})
MERGE (src)-[r:{link.link_type.value}]->(dst)
SET r.confidence = $confidence,
    r.rationale = $rationale,
    r.metadata = $metadata,
    r.created_at = $created_at,
    r.updated_at = $updated_at
"""
    rec = _link_to_record(link)
    with driver.session() as session:
        session.run(cypher, **rec)


class Neo4jTraceLinkWriter:
    """Writer class with upsert_node / upsert_edge / neighbours (fallback aware)."""

    def __init__(self, driver: Any) -> None:
        self._driver = driver

    def upsert_node(self, artifact: Artifact) -> None:
        if isinstance(artifact, Requirement):
            write_requirement(self._driver, artifact)
        else:
            write_artifact(self._driver, artifact)

    def upsert_edge(self, link: TraceLink) -> None:
        write_link(self._driver, link)

    def neighbors(
        self,
        node_id: UUID,
        *,
        rel_type: TraceLinkType | None = None,
        direction: str = "out",
    ) -> list[TraceLink]:
        """Return incident trace links for a node (in-memory fallback if no driver)."""
        if not _NEO4J_AVAILABLE or self._driver is None:
            results = []
            for link in _MEMORY_STORE["links"].values():
                if link.source_artifact_id == node_id or link.target_artifact_id == node_id:
                    if rel_type is None or link.link_type == rel_type:
                        results.append(link)
            return results
        if direction not in ("out", "in", "both"):
            raise ValueError(f"direction must be out|in|both, got {direction!r}")
        rel_filter = ""
        params: dict[str, Any] = {"node_id": str(node_id)}
        if rel_type is not None:
            rel_filter = "AND type(r) = $rel_type"
            params["rel_type"] = rel_type.value
        if direction == "out":
            pattern = "(n:Artifact {id: $node_id})-[r]->(m:Artifact)"
        elif direction == "in":
            pattern = "(n:Artifact {id: $node_id})<-[r]-(m:Artifact)"
        else:
            pattern = "(n:Artifact {id: $node_id})-[r]-(m:Artifact)"
        cypher = (
            f"MATCH {pattern} WHERE true {rel_filter} "
            "RETURN type(r) AS rel_type, n.id AS src_id, m.id AS dst_id, "
            "r.confidence AS confidence, r.rationale AS rationale"
        )
        edges = []
        with self._driver.session() as session:
            for record in session.run(cypher, **params):
                edges.append(
                    TraceLink(
                        project_id=UUID(record["src_id"]),
                        source_artifact_id=UUID(record["src_id"]),
                        target_artifact_id=UUID(record["dst_id"]),
                        link_type=TraceLinkType(record["rel_type"]),
                        confidence=record.get("confidence", 1.0),
                        rationale=record.get("rationale"),
                    )
                )
        return edges
