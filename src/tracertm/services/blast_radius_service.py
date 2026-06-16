"""Blast-radius / risk-weighted path scoring for TraceRTM.

Pure function over in-memory TraceLink graphs; no DB access required.
"""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from typing import Literal

from tracertm.models.trace_link import ArtifactKind, Artifact, TraceLink

# Risk-weighted scoring by ArtifactKind
_KIND_WEIGHT: dict[ArtifactKind, float] = {
    ArtifactKind.REQUIREMENT: 1.0,
    ArtifactKind.TEST: 0.9,
    ArtifactKind.CODE: 0.8,
    ArtifactKind.DESIGN: 0.7,
    ArtifactKind.RISK: 0.6,
    ArtifactKind.EVIDENCE: 0.5,
    ArtifactKind.RATIONALE: 0.4,
}

_DEFAULT_WEIGHT = 0.5


def _kind_weight(kind: ArtifactKind | None) -> float:
    if kind is None:
        return _DEFAULT_WEIGHT
    return _KIND_WEIGHT.get(kind, _DEFAULT_WEIGHT)


RiskLevel = Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]


@dataclass
class BlastRadiusResult:
    """Result of blast-radius computation for a single artifact."""

    artifact_id: str
    blast_radius_score: float  # 0.0 – 100.0
    affected_artifacts: list[str] = field(default_factory=list)
    critical_path: list[str] = field(default_factory=list)
    risk_level: RiskLevel = "LOW"


def _risk_level(score: float) -> RiskLevel:
    if score < 25.0:
        return "LOW"
    if score < 50.0:
        return "MEDIUM"
    if score < 75.0:
        return "HIGH"
    return "CRITICAL"


def compute_blast_radius(
    artifact_id: str,
    graph: dict[str, list[TraceLink]],
    artifacts: dict[str, Artifact],
    depth: int = 5,
) -> BlastRadiusResult:
    """Compute risk-weighted blast radius for *artifact_id*.

    Parameters
    ----------
    artifact_id:
        Source artifact whose downstream impact is assessed.
    graph:
        Adjacency list: source_id -> list[TraceLink].  Directed edges represent
        downstream dependencies (source → affects → target).
    artifacts:
        Flat map of id -> Artifact for weight lookup.
    depth:
        Maximum BFS depth to traverse.

    Returns
    -------
    BlastRadiusResult
        Affected artifacts, weighted score (0-100), critical path, risk level.
    """
    visited: set[str] = set()
    queue: deque[tuple[str, int]] = deque()
    queue.append((artifact_id, 0))
    visited.add(artifact_id)

    weighted_sum = 0.0
    # Track edge confidence along every path for critical-path selection
    # best_confidence[node] = (max accumulated confidence, predecessor)
    best_conf: dict[str, tuple[float, str | None]] = {artifact_id: (1.0, None)}

    while queue:
        current_id, current_depth = queue.popleft()
        if current_depth >= depth:
            continue
        for link in graph.get(current_id, []):
            target_id = str(link.target_artifact_id) if hasattr(link, "target_artifact_id") else str(getattr(link, "target_id", ""))
            if not target_id or target_id == artifact_id:
                continue
            artifact = artifacts.get(target_id)
            kind = artifact.kind if artifact is not None else None
            weight = _kind_weight(kind)
            edge_conf = float(getattr(link, "confidence", 1.0))

            if target_id not in visited:
                visited.add(target_id)
                queue.append((target_id, current_depth + 1))

            # Accumulate: add this edge's contribution to the score
            weighted_sum += edge_conf * weight

            # Track path with highest confidence
            parent_conf, _ = best_conf.get(current_id, (1.0, None))
            path_conf = parent_conf * edge_conf
            existing = best_conf.get(target_id, (0.0, None))[0]
            if path_conf > existing:
                best_conf[target_id] = (path_conf, current_id)

    affected = [aid for aid in visited if aid != artifact_id]

    # Normalise to 0-100: cap at 100
    score = min(weighted_sum * 10.0, 100.0) if affected else 0.0

    # Reconstruct critical path: find leaf with highest confidence, trace back
    if best_conf:
        leaf = max(
            (aid for aid in visited if aid != artifact_id),
            key=lambda aid: best_conf.get(aid, (0.0, None))[0],
            default=None,
        )
        path: list[str] = []
        node = leaf
        while node is not None:
            path.append(node)
            node = best_conf.get(node, (0.0, None))[1]
        critical_path = list(reversed(path))
    else:
        critical_path = []

    return BlastRadiusResult(
        artifact_id=artifact_id,
        blast_radius_score=round(score, 2),
        affected_artifacts=affected,
        critical_path=critical_path,
        risk_level=_risk_level(score),
    )
