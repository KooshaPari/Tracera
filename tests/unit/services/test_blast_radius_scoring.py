"""Unit tests for blast_radius_service — FR-TRC-015.

All tests are pure-function; no DB or graph-DB required.
"""
from __future__ import annotations

import uuid

import pytest

from tracertm.models.trace_link import ArtifactKind, Artifact, TraceLink, TraceLinkType
from tracertm.services.blast_radius_service import BlastRadiusResult, _kind_weight, _risk_level, compute_blast_radius

_PROJECT_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")

# Stable artifact IDs for tests
_IDS: dict[str, uuid.UUID] = {
    label: uuid.UUID(f"00000000-0000-0000-0000-{i:012d}")
    for i, label in enumerate(["A", "B", "C", "D", "src"] + [str(i) for i in range(1000)], start=1)
}


def _aid(label: str) -> str:
    """Return a stable string UUID for the given label."""
    return str(_IDS[label])


def _artifact(label: str, kind: ArtifactKind = ArtifactKind.CODE) -> Artifact:
    return Artifact(
        id=_IDS[label],
        project_id=_PROJECT_ID,
        kind=kind,
        title=f"Artifact {label}",
        external_id=label,
    )


def _link(source_label: str, target_label: str, confidence: float = 1.0) -> TraceLink:
    return TraceLink(
        id=uuid.uuid4(),
        project_id=_PROJECT_ID,
        source_artifact_id=_IDS[source_label],
        target_artifact_id=_IDS[target_label],
        link_type=TraceLinkType.IMPLEMENTS,
        confidence=confidence,
    )


def _graph(*edges: tuple[str, str, float | None]) -> dict[str, list[TraceLink]]:
    """Build adjacency dict keyed by string UUID."""
    g: dict[str, list[TraceLink]] = {}
    for edge in edges:
        src, tgt = edge[0], edge[1]
        conf = edge[2] if len(edge) > 2 and edge[2] is not None else 1.0  # type: ignore[misc]
        link = _link(src, tgt, conf)
        g.setdefault(_aid(src), []).append(link)
    return g


def _artifacts(*labels: str, **kind_overrides: ArtifactKind) -> dict[str, Artifact]:
    return {_aid(lbl): _artifact(lbl, kind_overrides.get(lbl, ArtifactKind.CODE)) for lbl in labels}


# --- _kind_weight ------------------------------------------------------------------


def test_kind_weight_requirement_is_highest() -> None:
    assert _kind_weight(ArtifactKind.REQUIREMENT) == 1.0


def test_kind_weight_rationale_is_lowest() -> None:
    assert _kind_weight(ArtifactKind.RATIONALE) == 0.4


def test_kind_weight_none_returns_default() -> None:
    assert _kind_weight(None) == 0.5


# --- _risk_level -------------------------------------------------------------------


def test_risk_level_low_below_25() -> None:
    assert _risk_level(0.0) == "LOW"
    assert _risk_level(24.9) == "LOW"


def test_risk_level_medium_25_to_50() -> None:
    assert _risk_level(25.0) == "MEDIUM"
    assert _risk_level(49.9) == "MEDIUM"


def test_risk_level_high_50_to_75() -> None:
    assert _risk_level(50.0) == "HIGH"
    assert _risk_level(74.9) == "HIGH"


def test_risk_level_critical_75_and_above() -> None:
    assert _risk_level(75.0) == "CRITICAL"
    assert _risk_level(100.0) == "CRITICAL"


# --- compute_blast_radius ----------------------------------------------------------


def test_isolated_artifact_returns_zero_score() -> None:
    result = compute_blast_radius(_aid("A"), {}, {})
    assert result.blast_radius_score == 0.0
    assert result.affected_artifacts == []
    assert result.risk_level == "LOW"


def test_single_edge_produces_affected_artifact() -> None:
    g = _graph(("A", "B"))
    arts = _artifacts("A", "B")
    result = compute_blast_radius(_aid("A"), g, arts)
    assert _aid("B") in result.affected_artifacts
    assert result.blast_radius_score > 0.0


def test_chain_three_artifacts_all_affected() -> None:
    g = _graph(("A", "B"), ("B", "C"))
    arts = _artifacts("A", "B", "C")
    result = compute_blast_radius(_aid("A"), g, arts)
    assert set(result.affected_artifacts) == {_aid("B"), _aid("C")}


def test_depth_limit_truncates_traversal() -> None:
    g = _graph(("A", "B"), ("B", "C"), ("C", "D"))
    arts = _artifacts("A", "B", "C", "D")
    result = compute_blast_radius(_aid("A"), g, arts, depth=1)
    assert _aid("B") in result.affected_artifacts
    assert _aid("C") not in result.affected_artifacts
    assert _aid("D") not in result.affected_artifacts


def test_high_confidence_link_raises_score() -> None:
    g_high = _graph(("A", "B", 1.0))
    g_low = _graph(("A", "B", 0.1))
    arts = _artifacts("A", "B")
    result_high = compute_blast_radius(_aid("A"), g_high, arts)
    result_low = compute_blast_radius(_aid("A"), g_low, arts)
    assert result_high.blast_radius_score > result_low.blast_radius_score


def test_requirement_kind_heavier_than_code() -> None:
    """REQUIREMENT-typed artifact should produce higher score than CODE-typed."""
    g = _graph(("A", "B"))
    arts_req = {_aid("A"): _artifact("A"), _aid("B"): _artifact("B", ArtifactKind.REQUIREMENT)}
    arts_code = {_aid("A"): _artifact("A"), _aid("B"): _artifact("B", ArtifactKind.CODE)}
    score_req = compute_blast_radius(_aid("A"), g, arts_req).blast_radius_score
    score_code = compute_blast_radius(_aid("A"), g, arts_code).blast_radius_score
    assert score_req > score_code


def test_score_capped_at_100() -> None:
    """Very wide graphs should not produce score > 100."""
    targets = [str(i) for i in range(50)]
    g: dict[str, list[TraceLink]] = {
        _aid("src"): [_link("src", t) for t in targets]
    }
    arts: dict[str, Artifact] = {_aid("src"): _artifact("src")}
    arts.update({_aid(t): _artifact(t) for t in targets})
    result = compute_blast_radius(_aid("src"), g, arts)
    assert result.blast_radius_score <= 100.0


def test_critical_path_starts_at_source() -> None:
    g = _graph(("A", "B"), ("B", "C"))
    arts = _artifacts("A", "B", "C")
    result = compute_blast_radius(_aid("A"), g, arts)
    assert result.critical_path[0] == _aid("A")


def test_critical_path_ends_at_highest_confidence_leaf() -> None:
    # A->B (0.9), A->C (0.5) — critical path should end at B
    g = _graph(("A", "B", 0.9), ("A", "C", 0.5))
    arts = _artifacts("A", "B", "C")
    result = compute_blast_radius(_aid("A"), g, arts)
    assert result.critical_path[-1] == _aid("B")


def test_artifact_id_in_result() -> None:
    result = compute_blast_radius(_aid("A"), {}, {})
    assert result.artifact_id == _aid("A")


def test_empty_graph_critical_path_is_empty() -> None:
    result = compute_blast_radius(_aid("A"), {}, {})
    assert result.critical_path == []


def test_cyclic_links_do_not_loop_forever() -> None:
    """Cycle A->B->A must not infinite-loop."""
    g = _graph(("A", "B"), ("B", "A"))
    arts = _artifacts("A", "B")
    result = compute_blast_radius(_aid("A"), g, arts)
    assert isinstance(result.blast_radius_score, float)


def test_blast_radius_result_is_dataclass_with_expected_fields() -> None:
    r = BlastRadiusResult(artifact_id="x", blast_radius_score=42.0)
    assert r.artifact_id == "x"
    assert r.blast_radius_score == 42.0
    assert r.risk_level == "LOW"
    assert r.affected_artifacts == []
    assert r.critical_path == []
