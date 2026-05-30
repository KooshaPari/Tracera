"""Coverage matrix export service for Tracera.

Implements FR-TRC-014: Traceability coverage matrix export (CSV/JSON).

Produces a matrix where:
- Rows    = Requirement artifacts
- Columns = Coverage dimensions: ``impl`` (SATISFIES/IMPLEMENTS links)
             and ``test`` (VERIFIES links), plus ``ArtifactKind`` buckets
             for linked non-requirement artifacts.
- Cells   = linked artifact IDs / titles, or empty when uncovered.

The module is a **pure function** (no DB access). Feed it in-memory lists
of :class:`~tracertm.models.trace_link.Artifact` and
:class:`~tracertm.models.trace_link.TraceLink` — the same signature used
by :func:`~tracertm.services.traceability_score_service.score_traceability`
(DRY: reuses the same graph snapshot pattern).

Formats
-------
* **CSV**  — RFC 4180-compliant; header row + one row per requirement.
* **JSON** — Structured dict with ``meta`` summary + ``rows`` list.
* **PDF**  — *Future work* (heavy dependency on reportlab/WeasyPrint;
              excluded from v1 to avoid adding a build-time dep).

Functional Requirements: FR-TRC-014
"""

from __future__ import annotations

import csv
import io
import json
import uuid
from dataclasses import dataclass, field
from typing import Sequence

from tracertm.models.trace_link import Artifact, ArtifactKind, TraceLink, TraceLinkType
from tracertm.services.traceability_score_service import (
    _SATISFIES_TYPES,  # noqa: PLC2701  # shared constant, same module family
    _VERIFIES_TYPES,
)

__all__ = [
    "CoverageMatrixRow",
    "CoverageMatrixReport",
    "build_coverage_matrix",
    "export_csv",
    "export_json",
]

# ---------------------------------------------------------------------------
# Column identifiers
# ---------------------------------------------------------------------------

_COL_IMPL = "impl_artifacts"
_COL_TEST = "test_artifacts"

# Non-requirement ArtifactKind columns (one per kind, excluding REQUIREMENT)
_KIND_COLUMNS: list[ArtifactKind] = [
    ArtifactKind.DESIGN,
    ArtifactKind.CODE,
    ArtifactKind.TEST,
    ArtifactKind.EVIDENCE,
    ArtifactKind.RISK,
    ArtifactKind.RATIONALE,
]


# ---------------------------------------------------------------------------
# Result types
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class CoverageMatrixRow:
    """Coverage data for a single requirement."""

    requirement_id: uuid.UUID
    requirement_title: str
    # Coverage dimensions
    impl_artifact_ids: list[uuid.UUID]      # SATISFIES / IMPLEMENTS sources
    impl_artifact_titles: list[str]
    test_artifact_ids: list[uuid.UUID]      # VERIFIES sources
    test_artifact_titles: list[str]
    # Per-ArtifactKind linked artifact titles (keyed by kind.value)
    kind_artifacts: dict[str, list[str]]
    # Derived booleans
    is_impl_covered: bool
    is_test_covered: bool
    is_fully_covered: bool                  # both impl + test


@dataclass(frozen=True, slots=True)
class CoverageMatrixReport:
    """Coverage matrix for a Requirement/Artifact/TraceLink graph snapshot."""

    total_requirements: int
    total_artifacts: int
    total_links: int
    impl_covered_count: int
    test_covered_count: int
    fully_covered_count: int
    impl_coverage_pct: float    # [0.0, 1.0]
    test_coverage_pct: float    # [0.0, 1.0]
    rows: list[CoverageMatrixRow] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Core builder — pure function
# ---------------------------------------------------------------------------


def build_coverage_matrix(
    artifacts: Sequence[Artifact],
    links: Sequence[TraceLink],
) -> CoverageMatrixReport:
    """Build a coverage matrix from an in-memory graph snapshot.

    Parameters
    ----------
    artifacts:
        All artifact nodes (requirements + non-requirements).
    links:
        All trace links in the snapshot.

    Returns
    -------
    :class:`CoverageMatrixReport` with one :class:`CoverageMatrixRow` per
    requirement.
    """
    requirements = [a for a in artifacts if a.kind == ArtifactKind.REQUIREMENT]
    artifact_by_id: dict[uuid.UUID, Artifact] = {a.id: a for a in artifacts}

    # Index links by target (impl / test pointing AT requirements)
    impl_sources_by_req: dict[uuid.UUID, list[Artifact]] = {}
    test_sources_by_req: dict[uuid.UUID, list[Artifact]] = {}
    kind_sources_by_req: dict[uuid.UUID, dict[ArtifactKind, list[Artifact]]] = {}

    for lnk in links:
        src = artifact_by_id.get(lnk.source_artifact_id)
        tgt_id = lnk.target_artifact_id
        if src is None:
            continue

        if lnk.link_type in _SATISFIES_TYPES:
            impl_sources_by_req.setdefault(tgt_id, []).append(src)
        if lnk.link_type in _VERIFIES_TYPES:
            test_sources_by_req.setdefault(tgt_id, []).append(src)

        # Bucket by kind for any link touching a requirement as target
        if tgt_id in {r.id for r in requirements}:
            kind_map = kind_sources_by_req.setdefault(tgt_id, {})
            kind_map.setdefault(src.kind, []).append(src)

    rows: list[CoverageMatrixRow] = []
    impl_covered_count = 0
    test_covered_count = 0
    fully_covered_count = 0

    for req in requirements:
        impl_arts = impl_sources_by_req.get(req.id, [])
        test_arts = test_sources_by_req.get(req.id, [])
        kind_map = kind_sources_by_req.get(req.id, {})

        is_impl = bool(impl_arts)
        is_test = bool(test_arts)
        is_full = is_impl and is_test

        kind_artifacts: dict[str, list[str]] = {
            k.value: [a.title for a in kind_map.get(k, [])]
            for k in _KIND_COLUMNS
        }

        row = CoverageMatrixRow(
            requirement_id=req.id,
            requirement_title=req.title,
            impl_artifact_ids=[a.id for a in impl_arts],
            impl_artifact_titles=[a.title for a in impl_arts],
            test_artifact_ids=[a.id for a in test_arts],
            test_artifact_titles=[a.title for a in test_arts],
            kind_artifacts=kind_artifacts,
            is_impl_covered=is_impl,
            is_test_covered=is_test,
            is_fully_covered=is_full,
        )
        rows.append(row)

        if is_impl:
            impl_covered_count += 1
        if is_test:
            test_covered_count += 1
        if is_full:
            fully_covered_count += 1

    n_req = len(requirements)
    return CoverageMatrixReport(
        total_requirements=n_req,
        total_artifacts=len(artifacts),
        total_links=len(links),
        impl_covered_count=impl_covered_count,
        test_covered_count=test_covered_count,
        fully_covered_count=fully_covered_count,
        impl_coverage_pct=impl_covered_count / n_req if n_req else 0.0,
        test_coverage_pct=test_covered_count / n_req if n_req else 0.0,
        rows=rows,
    )


# ---------------------------------------------------------------------------
# Export helpers
# ---------------------------------------------------------------------------

_CSV_COLUMNS = [
    "requirement_id",
    "requirement_title",
    "impl_covered",
    "impl_artifacts",
    "test_covered",
    "test_artifacts",
] + [f"kind_{k.value}" for k in _KIND_COLUMNS]


def export_csv(report: CoverageMatrixReport) -> str:
    """Serialise *report* to an RFC 4180-compliant CSV string.

    Columns::

        requirement_id, requirement_title,
        impl_covered, impl_artifacts,
        test_covered, test_artifacts,
        kind_design, kind_code, kind_test,
        kind_evidence, kind_risk, kind_rationale

    Multi-valued cells (multiple linked artifacts) are pipe-separated within
    the cell (e.g. ``"ArtA|ArtB"``).

    Returns
    -------
    str
        UTF-8 CSV text with CRLF line endings per RFC 4180.
    """
    buf = io.StringIO()
    writer = csv.writer(buf, lineterminator="\r\n")
    writer.writerow(_CSV_COLUMNS)

    for row in report.rows:
        writer.writerow([
            str(row.requirement_id),
            row.requirement_title,
            "covered" if row.is_impl_covered else "uncovered",
            "|".join(row.impl_artifact_titles),
            "covered" if row.is_test_covered else "uncovered",
            "|".join(row.test_artifact_titles),
            *[
                "|".join(row.kind_artifacts.get(k.value, []))
                for k in _KIND_COLUMNS
            ],
        ])

    return buf.getvalue()


def export_json(report: CoverageMatrixReport) -> str:
    """Serialise *report* to a JSON string.

    Structure::

        {
          "meta": {
            "total_requirements": int,
            "total_artifacts":    int,
            "total_links":        int,
            "impl_covered":       int,
            "test_covered":       int,
            "fully_covered":      int,
            "impl_coverage_pct":  float,
            "test_coverage_pct":  float
          },
          "columns": ["requirement_id", "requirement_title", ...],
          "rows": [
            {
              "requirement_id":      str,
              "requirement_title":   str,
              "impl_covered":        bool,
              "impl_artifacts":      [str, ...],
              "test_covered":        bool,
              "test_artifacts":      [str, ...],
              "kind_design":         [str, ...],
              ...
            },
            ...
          ]
        }

    Returns
    -------
    str
        JSON text (UTF-8, 2-space indent).
    """
    payload: dict = {
        "meta": {
            "total_requirements": report.total_requirements,
            "total_artifacts": report.total_artifacts,
            "total_links": report.total_links,
            "impl_covered": report.impl_covered_count,
            "test_covered": report.test_covered_count,
            "fully_covered": report.fully_covered_count,
            "impl_coverage_pct": round(report.impl_coverage_pct, 4),
            "test_coverage_pct": round(report.test_coverage_pct, 4),
        },
        "columns": _CSV_COLUMNS,
        "rows": [
            {
                "requirement_id": str(row.requirement_id),
                "requirement_title": row.requirement_title,
                "impl_covered": row.is_impl_covered,
                "impl_artifacts": row.impl_artifact_titles,
                "test_covered": row.is_test_covered,
                "test_artifacts": row.test_artifact_titles,
                **{
                    f"kind_{k.value}": row.kind_artifacts.get(k.value, [])
                    for k in _KIND_COLUMNS
                },
            }
            for row in report.rows
        ],
    }
    return json.dumps(payload, indent=2, ensure_ascii=False)
