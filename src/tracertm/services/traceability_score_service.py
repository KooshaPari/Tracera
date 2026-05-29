"""Traceability quality scoring service for Tracera.

Implements FR-TRC-017: Requirement quality scoring — computes per-requirement
and overall coverage metrics over the Requirement / Artifact / TraceLink graph.

Metrics
-------
* ``impl_coverage``   — % requirements with ≥1 SATISFIES link (implementation).
* ``test_coverage``   — % requirements with ≥1 VERIFIES link (test coverage).
* ``orphan_req_pct``  — % requirements with zero outgoing or incoming links.
* ``orphan_art_pct``  — % non-requirement artifacts with zero links.
* ``avg_confidence``  — mean confidence across all links (1.0 if no links).
* ``composite``       — 0-100 health score (weighted average, orphan penalty).

Composite formula
-----------------
  composite = round(
      0.35 * impl_coverage
    + 0.35 * test_coverage
    + 0.20 * avg_confidence
    - 0.05 * orphan_req_pct
    - 0.05 * orphan_art_pct
  ) * 100

All inputs are in [0, 1]; output clamped to [0, 100].

This module is a **pure function** (no DB access); feed it in-memory lists.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Sequence

from tracertm.models.trace_link import Artifact, ArtifactKind, TraceLink, TraceLinkType

__all__ = [
    "TraceabilityScoreReport",
    "PerRequirementScore",
    "score_traceability",
]

# ---------------------------------------------------------------------------
# Result types
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class PerRequirementScore:
    """Quality metrics for a single requirement node."""

    requirement_id: uuid.UUID
    title: str
    has_satisfies: bool
    has_verifies: bool
    is_orphan: bool
    link_count: int


@dataclass(frozen=True, slots=True)
class TraceabilityScoreReport:
    """Overall traceability health report for the supplied graph snapshot."""

    total_requirements: int
    total_artifacts: int
    total_links: int

    # Coverage ratios in [0.0, 1.0]
    impl_coverage: float        # % requirements with ≥1 SATISFIES
    test_coverage: float        # % requirements with ≥1 VERIFIES
    orphan_req_pct: float       # % requirements with zero links
    orphan_art_pct: float       # % non-requirement artifacts with zero links
    avg_confidence: float       # mean link confidence (1.0 when no links)

    # Composite 0-100 health score
    composite: int

    # Detail lists
    orphan_requirements: list[PerRequirementScore] = field(default_factory=list)
    unverified_requirements: list[PerRequirementScore] = field(default_factory=list)
    per_requirement: list[PerRequirementScore] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Scoring logic
# ---------------------------------------------------------------------------

_SATISFIES_TYPES: frozenset[TraceLinkType] = frozenset({
    TraceLinkType.SATISFIES,
    TraceLinkType.IMPLEMENTS,
})
_VERIFIES_TYPES: frozenset[TraceLinkType] = frozenset({
    TraceLinkType.VERIFIES,
})


def score_traceability(
    artifacts: Sequence[Artifact],
    links: Sequence[TraceLink],
) -> TraceabilityScoreReport:
    """Compute traceability health metrics over an in-memory graph snapshot.

    Parameters
    ----------
    artifacts:
        All artifact nodes in the project snapshot (requirements + non-req).
    links:
        All trace links.  Only ``source_artifact_id``, ``target_artifact_id``,
        ``link_type``, and ``confidence`` are used.

    Returns
    -------
    :class:`TraceabilityScoreReport` with per-requirement detail and composite score.
    """
    requirements = [a for a in artifacts if a.kind == ArtifactKind.REQUIREMENT]
    non_req = [a for a in artifacts if a.kind != ArtifactKind.REQUIREMENT]

    req_ids: set[uuid.UUID] = {r.id for r in requirements}
    art_ids: set[uuid.UUID] = {a.id for a in artifacts}

    # Index links by target (for SATISFIES/VERIFIES pointing *at* requirements)
    # and by source (for links originating from requirements)
    satisfies_by_target: dict[uuid.UUID, list[TraceLink]] = {}
    verifies_by_target: dict[uuid.UUID, list[TraceLink]] = {}
    links_by_participant: dict[uuid.UUID, list[TraceLink]] = {}

    for lnk in links:
        links_by_participant.setdefault(lnk.source_artifact_id, []).append(lnk)
        links_by_participant.setdefault(lnk.target_artifact_id, []).append(lnk)

        if lnk.link_type in _SATISFIES_TYPES:
            satisfies_by_target.setdefault(lnk.target_artifact_id, []).append(lnk)
        if lnk.link_type in _VERIFIES_TYPES:
            verifies_by_target.setdefault(lnk.target_artifact_id, []).append(lnk)

    # Per-requirement scores
    per_req: list[PerRequirementScore] = []
    impl_count = 0
    test_count = 0
    orphan_reqs: list[PerRequirementScore] = []
    unverified_reqs: list[PerRequirementScore] = []

    for req in requirements:
        has_satisfies = bool(satisfies_by_target.get(req.id))
        has_verifies = bool(verifies_by_target.get(req.id))
        req_links = links_by_participant.get(req.id, [])
        is_orphan = len(req_links) == 0

        score = PerRequirementScore(
            requirement_id=req.id,
            title=req.title,
            has_satisfies=has_satisfies,
            has_verifies=has_verifies,
            is_orphan=is_orphan,
            link_count=len(req_links),
        )
        per_req.append(score)

        if has_satisfies:
            impl_count += 1
        if has_verifies:
            test_count += 1
        if is_orphan:
            orphan_reqs.append(score)
        if not has_verifies:
            unverified_reqs.append(score)

    # Orphan non-requirement artifacts
    orphan_art_count = sum(
        1 for a in non_req if not links_by_participant.get(a.id)
    )

    n_req = len(requirements)
    n_art_non_req = len(non_req)

    impl_cov = impl_count / n_req if n_req else 0.0
    test_cov = test_count / n_req if n_req else 0.0
    orphan_req_pct = len(orphan_reqs) / n_req if n_req else 0.0
    orphan_art_pct = orphan_art_count / n_art_non_req if n_art_non_req else 0.0

    # Average confidence across all links
    if links:
        avg_conf = sum(lnk.confidence for lnk in links) / len(links)
    else:
        avg_conf = 1.0

    # Composite score (clamped 0–100)
    raw = (
        0.35 * impl_cov
        + 0.35 * test_cov
        + 0.20 * avg_conf
        - 0.05 * orphan_req_pct
        - 0.05 * orphan_art_pct
    )
    composite = max(0, min(100, round(raw * 100)))

    return TraceabilityScoreReport(
        total_requirements=n_req,
        total_artifacts=len(artifacts),
        total_links=len(links),
        impl_coverage=impl_cov,
        test_coverage=test_cov,
        orphan_req_pct=orphan_req_pct,
        orphan_art_pct=orphan_art_pct,
        avg_confidence=avg_conf,
        composite=composite,
        orphan_requirements=orphan_reqs,
        unverified_requirements=unverified_reqs,
        per_requirement=per_req,
    )
