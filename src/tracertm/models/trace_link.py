"""Trace-link domain model for SOTA research P0.

This module is the *canonical* domain layer for the requirements-traceability
spine. It sits on top of the existing generic ``Item``/``Link`` SQL models
(``tracertm.models.item.Item`` and ``tracertm.models.link.Link``) and adds:

* A canonical :class:`TraceLinkType` enum (SATISFIES, VERIFIES, IMPLEMENTS,
  DERIVES_FROM, REFINES, CONFLICTS_WITH, DUPLICATES) used by both the SQL
  ``links.link_type`` column and the Neo4j relationship label.
* A canonical :class:`ArtifactKind` enum partitioning Items into the
  traceability roles relevant for ISO 29148 / DO-178C / IEC 62304 style
  traces (REQUIREMENT, DESIGN, CODE, TEST, EVIDENCE, RISK, RATIONALE).
* Lightweight Pydantic value objects (:class:`TraceLink`,
  :class:`Requirement`, :class:`Artifact`) used at API and RAG boundaries.
  These are *not* ORM models — the SQL persistence already lives in
  :mod:`tracertm.models.link` and :mod:`tracertm.models.item`. The
  dataclasses here are the wire-format / pipeline-format the upcoming
  RAG, miner and query layers (later PRs) will operate on.
* :class:`Neo4jSchema`: declarative Cypher schema (constraints, indexes,
  relationship labels) for the graph projection.

Persistence note: the existing ``links`` table already covers source/target
ids and a free-form ``link_metadata`` JSONB. The two new SOTA-research
fields — ``confidence`` (float 0..1) and ``rationale`` (text) — are added
as first-class columns by alembic revision ``062_add_trace_link_fields`` so
they can be indexed and filtered without JSON-path queries.

Functional Requirements: FR-TRACE-001 (canonical link types),
FR-TRACE-002 (confidence-scored trace links), FR-TRACE-003 (Neo4j
projection of the traceability graph).
"""

from __future__ import annotations

import uuid
from datetime import datetime  # noqa: TC003 — Pydantic needs datetime at runtime
from enum import StrEnum
from typing import Any, Final

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

__all__ = [
    "NEO4J_NODE_LABELS",
    "NEO4J_RELATIONSHIP_TYPES",
    "Artifact",
    "ArtifactKind",
    "Neo4jSchema",
    "Requirement",
    "RequirementStatus",
    "TraceLink",
    "TraceLinkType",
    "VerificationMethod",
]


# ---------------------------------------------------------------------------
# Enums (canonical vocabulary shared by SQL, Neo4j and API layers)
# ---------------------------------------------------------------------------


class TraceLinkType(StrEnum):
    """Canonical trace-link relationship vocabulary.

    Values are the *exact* strings used as both the SQL ``links.link_type``
    column value and the Neo4j relationship label. Keep them SCREAMING_SNAKE
    so they round-trip cleanly through Cypher.

    Semantic mapping (ISO 29148 § 5.2.6 + DO-178C Table A-3):

    * ``SATISFIES``     — implementation/design artifact satisfies a requirement
    * ``VERIFIES``      — test/evidence verifies a requirement (forward V-model)
    * ``IMPLEMENTS``    — code artifact implements a design/spec element
    * ``DERIVES_FROM``  — derived requirement (parent → child decomposition)
    * ``REFINES``       — peer refinement at the same abstraction level
    * ``CONFLICTS_WITH``— mutually exclusive / contradictory requirements
    * ``DUPLICATES``    — semantic-equivalence link found by the miner
    """

    SATISFIES = "SATISFIES"
    VERIFIES = "VERIFIES"
    IMPLEMENTS = "IMPLEMENTS"
    DERIVES_FROM = "DERIVES_FROM"
    REFINES = "REFINES"
    CONFLICTS_WITH = "CONFLICTS_WITH"
    DUPLICATES = "DUPLICATES"


#: Core P0 subset called out in the SOTA research brief.
#: The miner / RAG layer (next PR) only needs to score these four.
CORE_TRACE_LINK_TYPES: Final[frozenset[TraceLinkType]] = frozenset({
    TraceLinkType.SATISFIES,
    TraceLinkType.VERIFIES,
    TraceLinkType.IMPLEMENTS,
    TraceLinkType.DERIVES_FROM,
})


class ArtifactKind(StrEnum):
    """Role of an :class:`Artifact` inside the traceability graph.

    Maps to the ``items.type`` discriminator on the SQL side and to the
    Neo4j node label (``:Requirement``, ``:Test``, …) on the graph side.
    """

    REQUIREMENT = "requirement"
    DESIGN = "design"
    CODE = "code"
    TEST = "test"
    EVIDENCE = "evidence"
    RISK = "risk"
    RATIONALE = "rationale"


class RequirementStatus(StrEnum):
    """Lifecycle states for a :class:`Requirement` (ISO 29148 § 5.2.8)."""

    DRAFT = "draft"
    PROPOSED = "proposed"
    APPROVED = "approved"
    IMPLEMENTED = "implemented"
    VERIFIED = "verified"
    DEPRECATED = "deprecated"
    REJECTED = "rejected"


class VerificationMethod(StrEnum):
    """DO-178C / IEEE 1012 verification methods used on VERIFIES links."""

    TEST = "test"
    ANALYSIS = "analysis"
    INSPECTION = "inspection"
    DEMONSTRATION = "demonstration"
    REVIEW = "review"


# ---------------------------------------------------------------------------
# Value objects (Pydantic, used at API / RAG / mining boundaries)
# ---------------------------------------------------------------------------


class Artifact(BaseModel):
    """Any node in the traceability graph (super-type of Requirement).

    Mirrors :class:`tracertm.models.item.Item` for the subset of fields the
    trace-link layer needs. ``id`` is the same UUID as ``items.id``.
    """

    model_config = ConfigDict(from_attributes=True, frozen=True)

    id: uuid.UUID
    project_id: uuid.UUID
    kind: ArtifactKind
    title: str = Field(min_length=1, max_length=500)
    description: str | None = None
    external_id: str | None = Field(default=None, max_length=255)
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime | None = None
    updated_at: datetime | None = None


class Requirement(Artifact):
    """A traceable requirement.

    Specialisation of :class:`Artifact` with ``kind`` pinned to
    :attr:`ArtifactKind.REQUIREMENT` and the ISO 29148 lifecycle fields the
    quality analyser (:mod:`tracertm.models.requirement_quality`) reads.
    """

    kind: ArtifactKind = ArtifactKind.REQUIREMENT
    status: RequirementStatus = RequirementStatus.DRAFT
    priority: int | None = Field(default=None, ge=0, le=5)
    rationale: str | None = None
    acceptance_criteria: list[str] = Field(default_factory=list)
    verification_method: VerificationMethod | None = None

    @field_validator("kind")
    @classmethod
    def _kind_must_be_requirement(cls, v: ArtifactKind) -> ArtifactKind:
        if v is not ArtifactKind.REQUIREMENT:
            msg = f"Requirement.kind must be REQUIREMENT, got {v!r}"
            raise ValueError(msg)
        return v


class TraceLink(BaseModel):
    """A confidence-scored directed edge in the traceability graph.

    Direction is ``source_artifact_id ──link_type──▶ target_artifact_id``.
    For example, a SATISFIES link runs *from* the implementing artifact
    *to* the requirement it satisfies::

        CodeFile ──SATISFIES──▶ Requirement
        TestCase ──VERIFIES──▶ Requirement
        ChildReq ──DERIVES_FROM──▶ ParentReq

    ``confidence`` is the miner's posterior probability that the link is
    correct (``1.0`` for human-curated links). ``rationale`` is a short
    natural-language justification, used both for explainability and as
    grounding context for the RAG layer.
    """

    model_config = ConfigDict(from_attributes=True, frozen=True)

    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    project_id: uuid.UUID
    source_artifact_id: uuid.UUID
    target_artifact_id: uuid.UUID
    link_type: TraceLinkType
    confidence: float = Field(ge=0.0, le=1.0, default=1.0)
    rationale: str | None = Field(default=None, max_length=4000)
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime | None = None
    updated_at: datetime | None = None

    @model_validator(mode="after")
    def _no_self_loops(self) -> TraceLink:
        if self.source_artifact_id == self.target_artifact_id:
            msg = "TraceLink source_artifact_id and target_artifact_id must differ"
            raise ValueError(msg)
        return self

    @property
    def is_core(self) -> bool:
        """True if this link uses one of the P0 SOTA link types."""
        return self.link_type in CORE_TRACE_LINK_TYPES


# ---------------------------------------------------------------------------
# Neo4j schema
# ---------------------------------------------------------------------------


#: Neo4j relationship labels. Kept in sync with :class:`TraceLinkType` so
#: the projection layer can do ``rel_type = link.link_type.value``.
NEO4J_RELATIONSHIP_TYPES: Final[tuple[str, ...]] = tuple(t.value for t in TraceLinkType)

#: Neo4j node labels (one per ArtifactKind, plus the umbrella ``Artifact``).
NEO4J_NODE_LABELS: Final[tuple[str, ...]] = (
    "Artifact",
    "Requirement",
    "Design",
    "Code",
    "Test",
    "Evidence",
    "Risk",
    "Rationale",
    "Project",
)


class Neo4jSchema:
    """Declarative Cypher schema for the trace-link graph projection.

    Apply once at startup (idempotent — all statements use IF NOT EXISTS).
    The schema deliberately uses *node-key* constraints on
    ``(project_id, id)`` so the same UUID can theoretically be reused
    across tenants without collisions.
    """

    #: Uniqueness / existence constraints.
    # Note: NODE KEY and relationship property constraints require Neo4j
    # Enterprise. Community edition supports node uniqueness only — we use
    # UNIQUE constraints to approximate the composite NODE KEY, and omit
    # the relationship property existence constraint (enforced at the
    # application layer by the TraceLink model validator instead).
    CONSTRAINTS: Final[tuple[str, ...]] = (
        # Artifact id unique globally (project scoping enforced by app layer).
        "CREATE CONSTRAINT artifact_id_unique IF NOT EXISTS FOR (a:Artifact) REQUIRE a.id IS UNIQUE",
        "CREATE CONSTRAINT requirement_id_unique IF NOT EXISTS FOR (r:Requirement) REQUIRE r.id IS UNIQUE",
        "CREATE CONSTRAINT project_id_unique IF NOT EXISTS FOR (p:Project) REQUIRE p.id IS UNIQUE",
    )

    #: Lookup / range indexes for the common RAG-side queries.
    INDEXES: Final[tuple[str, ...]] = (
        "CREATE INDEX artifact_project_kind IF NOT EXISTS FOR (a:Artifact) ON (a.project_id, a.kind)",
        "CREATE INDEX artifact_external_id IF NOT EXISTS FOR (a:Artifact) ON (a.external_id)",
        "CREATE INDEX requirement_status IF NOT EXISTS FOR (r:Requirement) ON (r.status)",
        "CREATE FULLTEXT INDEX artifact_text IF NOT EXISTS FOR (a:Artifact) ON EACH [a.title, a.description]",
    )

    @classmethod
    def all_statements(cls) -> tuple[str, ...]:
        """All DDL statements in apply order (constraints before indexes)."""
        return cls.CONSTRAINTS + cls.INDEXES

    @classmethod
    def relationship_label_for(cls, link_type: TraceLinkType) -> str:
        """Return the Neo4j relationship label for a given TraceLinkType."""
        return link_type.value

    @classmethod
    def node_label_for(cls, kind: ArtifactKind) -> str:
        """Return the primary Neo4j node label for a given ArtifactKind."""
        # Title-case mapping matches NEO4J_NODE_LABELS above.
        return kind.value.capitalize()
