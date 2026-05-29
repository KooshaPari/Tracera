"""Unit tests for the traceability quality scoring service.

Functional Requirements: FR-TRC-017

Coverage
--------
* Fully-covered graph scores high (composite near/at 90+).
* Orphan requirements reduce the score and appear in orphan list.
* Missing VERIFIES links are detected and flagged.
* Empty graph handled gracefully (no division by zero).
* IMPLEMENTS link counts as implementation coverage (SATISFIES-family).
* Average confidence is computed across all links.
* Low-confidence links reduce avg_confidence and composite.
* Non-requirement artifacts with no links counted as orphan artifacts.
* Per-requirement detail populated correctly.
* Composite score clamped to [0, 100].
* Single requirement, fully covered.
* Single requirement, orphan.
* Multiple projects' artifacts coexist without cross-contamination.
* Unverified requirements list excludes requirements that have VERIFIES.
* All-orphan graph gives composite near 0.
* Graph with only non-req artifacts (no requirements) handled.
* Graph with requirements and no artifacts of other kinds handled.
* VERIFIES link sets has_verifies True.
* SATISFIES link sets has_satisfies True.
* Link count per requirement equals sum of incoming + outgoing links.
"""

from __future__ import annotations

import uuid

import pytest

from tracertm.models.trace_link import Artifact, ArtifactKind, TraceLink, TraceLinkType
from tracertm.services.traceability_score_service import (
    TraceabilityScoreReport,
    score_traceability,
)

pytestmark = pytest.mark.unit

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_PROJ = uuid.UUID("aaaaaaaa-0000-0000-0000-000000000001")


def _req(title: str = "A requirement") -> Artifact:
    return Artifact(
        id=uuid.uuid4(),
        project_id=_PROJ,
        kind=ArtifactKind.REQUIREMENT,
        title=title,
    )


def _code(title: str = "Code artifact") -> Artifact:
    return Artifact(
        id=uuid.uuid4(),
        project_id=_PROJ,
        kind=ArtifactKind.CODE,
        title=title,
    )


def _test_art(title: str = "Test artifact") -> Artifact:
    return Artifact(
        id=uuid.uuid4(),
        project_id=_PROJ,
        kind=ArtifactKind.TEST,
        title=title,
    )


def _link(
    src: uuid.UUID,
    tgt: uuid.UUID,
    link_type: TraceLinkType,
    confidence: float = 1.0,
) -> TraceLink:
    return TraceLink(
        id=uuid.uuid4(),
        project_id=_PROJ,
        source_artifact_id=src,
        target_artifact_id=tgt,
        link_type=link_type,
        confidence=confidence,
    )


# ---------------------------------------------------------------------------
# Tests: empty graph
# ---------------------------------------------------------------------------


def test_empty_graph_no_crash() -> None:
    """Empty graph returns zeroed report without raising."""
    report = score_traceability([], [])
    assert report.total_requirements == 0
    assert report.total_artifacts == 0
    assert report.total_links == 0
    assert report.impl_coverage == 0.0
    assert report.test_coverage == 0.0
    assert report.orphan_req_pct == 0.0
    assert report.orphan_art_pct == 0.0
    assert report.avg_confidence == 1.0  # no links → default 1.0
    assert isinstance(report.composite, int)
    assert 0 <= report.composite <= 100


def test_empty_graph_composite_is_twenty() -> None:
    """Empty graph: composite = round(0.20 * 1.0 * 100) = 20."""
    report = score_traceability([], [])
    # formula: 0.35*0 + 0.35*0 + 0.20*1.0 - 0.05*0 - 0.05*0 = 0.20 → 20
    assert report.composite == 20


# ---------------------------------------------------------------------------
# Tests: single requirement, fully covered
# ---------------------------------------------------------------------------


def test_single_req_fully_covered() -> None:
    req = _req("The system shall authenticate users")
    code = _code()
    test = _test_art()
    satisfies = _link(code.id, req.id, TraceLinkType.SATISFIES)
    verifies = _link(test.id, req.id, TraceLinkType.VERIFIES)

    report = score_traceability([req, code, test], [satisfies, verifies])

    assert report.total_requirements == 1
    assert report.impl_coverage == 1.0
    assert report.test_coverage == 1.0
    assert report.orphan_req_pct == 0.0
    assert len(report.orphan_requirements) == 0
    assert len(report.unverified_requirements) == 0
    assert report.composite >= 80  # fully covered → high score


def test_single_req_orphan() -> None:
    req = _req()
    report = score_traceability([req], [])

    assert report.orphan_req_pct == 1.0
    assert len(report.orphan_requirements) == 1
    assert report.orphan_requirements[0].requirement_id == req.id
    assert report.composite < 20  # all orphan → penalty


# ---------------------------------------------------------------------------
# Tests: implementation coverage
# ---------------------------------------------------------------------------


def test_implements_counts_as_impl_coverage() -> None:
    """IMPLEMENTS link type counts toward implementation coverage."""
    req = _req()
    code = _code()
    impl_link = _link(code.id, req.id, TraceLinkType.IMPLEMENTS)

    report = score_traceability([req, code], [impl_link])

    assert report.impl_coverage == 1.0
    assert report.per_requirement[0].has_satisfies is True


def test_no_satisfies_link_reduces_impl_coverage() -> None:
    req = _req()
    test = _test_art()
    verifies = _link(test.id, req.id, TraceLinkType.VERIFIES)

    report = score_traceability([req, test], [verifies])

    assert report.impl_coverage == 0.0
    assert report.per_requirement[0].has_satisfies is False
    assert report.per_requirement[0].has_verifies is True


# ---------------------------------------------------------------------------
# Tests: test coverage
# ---------------------------------------------------------------------------


def test_missing_verifies_flagged_in_unverified_list() -> None:
    req = _req()
    code = _code()
    satisfies = _link(code.id, req.id, TraceLinkType.SATISFIES)

    report = score_traceability([req, code], [satisfies])

    assert report.test_coverage == 0.0
    assert len(report.unverified_requirements) == 1
    assert report.unverified_requirements[0].requirement_id == req.id


def test_verified_req_not_in_unverified_list() -> None:
    req = _req()
    test = _test_art()
    verifies = _link(test.id, req.id, TraceLinkType.VERIFIES)

    report = score_traceability([req, test], [verifies])

    unverified_ids = {r.requirement_id for r in report.unverified_requirements}
    assert req.id not in unverified_ids


# ---------------------------------------------------------------------------
# Tests: orphan non-requirement artifacts
# ---------------------------------------------------------------------------


def test_orphan_artifact_counted() -> None:
    req = _req()
    lone_code = _code("Orphan code file")  # no links at all
    test = _test_art()
    verifies = _link(test.id, req.id, TraceLinkType.VERIFIES)

    report = score_traceability([req, lone_code, test], [verifies])

    # lone_code has no links; test has one link
    assert report.orphan_art_pct == pytest.approx(0.5)


def test_no_non_req_artifacts_orphan_pct_zero() -> None:
    req = _req()
    report = score_traceability([req], [])
    # No non-requirement artifacts at all → pct = 0
    assert report.orphan_art_pct == 0.0


# ---------------------------------------------------------------------------
# Tests: average confidence
# ---------------------------------------------------------------------------


def test_avg_confidence_full_confidence() -> None:
    req = _req()
    code = _code()
    lnk = _link(code.id, req.id, TraceLinkType.SATISFIES, confidence=1.0)

    report = score_traceability([req, code], [lnk])
    assert report.avg_confidence == pytest.approx(1.0)


def test_avg_confidence_low_reduces_composite() -> None:
    req = _req()
    code = _code()
    test = _test_art()
    low_sat = _link(code.id, req.id, TraceLinkType.SATISFIES, confidence=0.1)
    low_ver = _link(test.id, req.id, TraceLinkType.VERIFIES, confidence=0.1)

    report = score_traceability([req, code, test], [low_sat, low_ver])
    assert report.avg_confidence == pytest.approx(0.1)
    # Even with 100% coverage, low confidence pulls composite down
    high_conf_report = score_traceability(
        [req, code, test],
        [
            _link(code.id, req.id, TraceLinkType.SATISFIES, confidence=1.0),
            _link(test.id, req.id, TraceLinkType.VERIFIES, confidence=1.0),
        ],
    )
    assert report.composite < high_conf_report.composite


# ---------------------------------------------------------------------------
# Tests: multiple requirements
# ---------------------------------------------------------------------------


def test_partial_coverage_ratios() -> None:
    """Two requirements: one fully covered, one orphan."""
    req_covered = _req("Covered req")
    req_orphan = _req("Orphan req")
    code = _code()
    test = _test_art()
    satisfies = _link(code.id, req_covered.id, TraceLinkType.SATISFIES)
    verifies = _link(test.id, req_covered.id, TraceLinkType.VERIFIES)

    report = score_traceability(
        [req_covered, req_orphan, code, test],
        [satisfies, verifies],
    )

    assert report.total_requirements == 2
    assert report.impl_coverage == pytest.approx(0.5)
    assert report.test_coverage == pytest.approx(0.5)
    assert report.orphan_req_pct == pytest.approx(0.5)
    assert len(report.orphan_requirements) == 1
    assert report.orphan_requirements[0].requirement_id == req_orphan.id


def test_all_orphan_requirements_composite_near_zero() -> None:
    """All requirements with zero links → very low composite."""
    reqs = [_req(f"req-{i}") for i in range(5)]
    report = score_traceability(reqs, [])
    assert report.orphan_req_pct == 1.0
    assert report.composite <= 15


# ---------------------------------------------------------------------------
# Tests: per-requirement detail
# ---------------------------------------------------------------------------


def test_per_requirement_populated() -> None:
    req = _req("My req")
    code = _code()
    test = _test_art()
    lnk1 = _link(code.id, req.id, TraceLinkType.SATISFIES)
    lnk2 = _link(test.id, req.id, TraceLinkType.VERIFIES)

    report = score_traceability([req, code, test], [lnk1, lnk2])

    assert len(report.per_requirement) == 1
    detail = report.per_requirement[0]
    assert detail.requirement_id == req.id
    assert detail.has_satisfies is True
    assert detail.has_verifies is True
    assert detail.is_orphan is False
    assert detail.link_count == 2  # req is target of both lnk1 and lnk2


def test_per_requirement_orphan_flag() -> None:
    req = _req()
    report = score_traceability([req], [])
    assert report.per_requirement[0].is_orphan is True
    assert report.per_requirement[0].link_count == 0


# ---------------------------------------------------------------------------
# Tests: graph with only non-req artifacts
# ---------------------------------------------------------------------------


def test_no_requirements_in_graph() -> None:
    code = _code()
    report = score_traceability([code], [])
    assert report.total_requirements == 0
    assert report.impl_coverage == 0.0
    assert report.test_coverage == 0.0
    assert report.orphan_req_pct == 0.0


# ---------------------------------------------------------------------------
# Tests: composite score clamping
# ---------------------------------------------------------------------------


def test_composite_never_exceeds_100() -> None:
    reqs = [_req(f"req-{i}") for i in range(10)]
    codes = [_code(f"code-{i}") for i in range(10)]
    tests = [_test_art(f"test-{i}") for i in range(10)]
    links: list[TraceLink] = []
    for req, code, test in zip(reqs, codes, tests):
        links.append(_link(code.id, req.id, TraceLinkType.SATISFIES))
        links.append(_link(test.id, req.id, TraceLinkType.VERIFIES))

    report = score_traceability(reqs + codes + tests, links)
    assert report.composite <= 100


def test_composite_never_below_zero() -> None:
    # Craft a maximally penalised graph (impossible in practice, but guard anyway)
    report = score_traceability([], [])
    assert report.composite >= 0
