"""Unit tests for the coverage matrix export service.

Functional Requirements: FR-TRC-014

Coverage
--------
* Empty graph → empty matrix with correct headers in CSV and JSON.
* Single covered requirement → appears in matrix, is_impl_covered True.
* Single uncovered requirement → appears in matrix, is_impl_covered False.
* SATISFIES link counts as impl coverage.
* IMPLEMENTS link counts as impl coverage (SATISFIES-family, DRY with scorer).
* VERIFIES link counts as test coverage.
* Both impl + test → is_fully_covered True.
* Only impl → is_fully_covered False.
* Only test → is_fully_covered False.
* Multiple requirements → correct row count and coverage counts.
* Coverage percentages computed correctly (covered / total).
* CSV header row matches _CSV_COLUMNS spec.
* CSV rows: correct field count; impl/test cells contain artifact titles.
* CSV cells with multiple linked artifacts are pipe-separated.
* CSV escaping: titles containing commas/quotes are RFC 4180-escaped.
* JSON meta block has all required keys.
* JSON rows have correct keys per requirement.
* JSON impl_covered / test_covered booleans match domain logic.
* Kind-bucket columns populated for linked non-req artifacts.
* Non-requirement artifacts without links don't appear in matrix rows.
* Graph with requirements and no non-req artifacts → kind columns empty.
* Non-requirement artifacts not in any req's target links → kind columns empty.
* Coverage pct = 0.0 when all requirements uncovered.
* Coverage pct = 1.0 when all requirements covered.
"""

from __future__ import annotations

import csv
import io
import json
import uuid

import pytest

from tracertm.models.trace_link import Artifact, ArtifactKind, TraceLink, TraceLinkType
from tracertm.services.coverage_matrix_service import (
    _CSV_COLUMNS,
    _KIND_COLUMNS,
    build_coverage_matrix,
    export_csv,
    export_json,
)

pytestmark = pytest.mark.unit

# ---------------------------------------------------------------------------
# Helpers / fixtures
# ---------------------------------------------------------------------------

_PROJ = uuid.UUID("bbbbbbbb-0000-0000-0000-000000000001")


def _req(title: str = "Requirement A") -> Artifact:
    return Artifact(
        id=uuid.uuid4(), project_id=_PROJ, kind=ArtifactKind.REQUIREMENT, title=title
    )


def _code(title: str = "Code A") -> Artifact:
    return Artifact(
        id=uuid.uuid4(), project_id=_PROJ, kind=ArtifactKind.CODE, title=title
    )


def _test_art(title: str = "Test A") -> Artifact:
    return Artifact(
        id=uuid.uuid4(), project_id=_PROJ, kind=ArtifactKind.TEST, title=title
    )


def _design(title: str = "Design A") -> Artifact:
    return Artifact(
        id=uuid.uuid4(), project_id=_PROJ, kind=ArtifactKind.DESIGN, title=title
    )


def _link(
    src_id: uuid.UUID,
    tgt_id: uuid.UUID,
    link_type: TraceLinkType,
    confidence: float = 1.0,
) -> TraceLink:
    return TraceLink(
        id=uuid.uuid4(),
        project_id=_PROJ,
        source_artifact_id=src_id,
        target_artifact_id=tgt_id,
        link_type=link_type,
        confidence=confidence,
    )


# ---------------------------------------------------------------------------
# Empty graph
# ---------------------------------------------------------------------------


def test_empty_graph_returns_empty_rows() -> None:
    report = build_coverage_matrix([], [])
    assert report.total_requirements == 0
    assert report.total_artifacts == 0
    assert report.total_links == 0
    assert report.rows == []
    assert report.impl_coverage_pct == 0.0
    assert report.test_coverage_pct == 0.0


def test_empty_graph_csv_has_header_only() -> None:
    report = build_coverage_matrix([], [])
    csv_text = export_csv(report)
    reader = csv.reader(io.StringIO(csv_text))
    rows = list(reader)
    # Only header row (empty body rows are stripped by csv module from empty input)
    assert len(rows) == 1
    assert rows[0] == _CSV_COLUMNS


def test_empty_graph_json_has_expected_keys() -> None:
    report = build_coverage_matrix([], [])
    data = json.loads(export_json(report))
    assert "meta" in data
    assert "columns" in data
    assert "rows" in data
    assert data["rows"] == []
    assert data["meta"]["total_requirements"] == 0


# ---------------------------------------------------------------------------
# Single requirement — uncovered
# ---------------------------------------------------------------------------


def test_single_uncovered_requirement() -> None:
    req = _req("REQ-001")
    report = build_coverage_matrix([req], [])
    assert report.total_requirements == 1
    assert report.impl_covered_count == 0
    assert report.test_covered_count == 0
    assert report.impl_coverage_pct == 0.0
    assert report.test_coverage_pct == 0.0
    row = report.rows[0]
    assert row.requirement_title == "REQ-001"
    assert row.is_impl_covered is False
    assert row.is_test_covered is False
    assert row.is_fully_covered is False
    assert row.impl_artifact_titles == []
    assert row.test_artifact_titles == []


# ---------------------------------------------------------------------------
# SATISFIES → impl coverage
# ---------------------------------------------------------------------------


def test_satisfies_link_counts_as_impl_covered() -> None:
    req = _req()
    code = _code()
    lnk = _link(code.id, req.id, TraceLinkType.SATISFIES)
    report = build_coverage_matrix([req, code], [lnk])
    row = report.rows[0]
    assert row.is_impl_covered is True
    assert code.title in row.impl_artifact_titles


def test_implements_link_counts_as_impl_covered() -> None:
    """IMPLEMENTS is in the SATISFIES-family — DRY with traceability scorer."""
    req = _req()
    code = _code()
    lnk = _link(code.id, req.id, TraceLinkType.IMPLEMENTS)
    report = build_coverage_matrix([req, code], [lnk])
    row = report.rows[0]
    assert row.is_impl_covered is True


# ---------------------------------------------------------------------------
# VERIFIES → test coverage
# ---------------------------------------------------------------------------


def test_verifies_link_counts_as_test_covered() -> None:
    req = _req()
    test = _test_art()
    lnk = _link(test.id, req.id, TraceLinkType.VERIFIES)
    report = build_coverage_matrix([req, test], [lnk])
    row = report.rows[0]
    assert row.is_test_covered is True
    assert test.title in row.test_artifact_titles


# ---------------------------------------------------------------------------
# Fully covered
# ---------------------------------------------------------------------------


def test_both_impl_and_test_is_fully_covered() -> None:
    req = _req()
    code = _code()
    test = _test_art()
    impl_lnk = _link(code.id, req.id, TraceLinkType.SATISFIES)
    test_lnk = _link(test.id, req.id, TraceLinkType.VERIFIES)
    report = build_coverage_matrix([req, code, test], [impl_lnk, test_lnk])
    assert report.fully_covered_count == 1
    assert report.rows[0].is_fully_covered is True


def test_impl_only_not_fully_covered() -> None:
    req = _req()
    code = _code()
    lnk = _link(code.id, req.id, TraceLinkType.SATISFIES)
    report = build_coverage_matrix([req, code], [lnk])
    assert report.rows[0].is_fully_covered is False


def test_test_only_not_fully_covered() -> None:
    req = _req()
    test = _test_art()
    lnk = _link(test.id, req.id, TraceLinkType.VERIFIES)
    report = build_coverage_matrix([req, test], [lnk])
    assert report.rows[0].is_fully_covered is False


# ---------------------------------------------------------------------------
# Multiple requirements
# ---------------------------------------------------------------------------


def test_multiple_requirements_correct_row_count() -> None:
    reqs = [_req(f"REQ-{i:03d}") for i in range(5)]
    codes = [_code(f"CODE-{i}") for i in range(3)]
    # Link first 3 requirements to code artifacts (impl only)
    links = [_link(codes[i].id, reqs[i].id, TraceLinkType.SATISFIES) for i in range(3)]
    report = build_coverage_matrix(reqs + codes, links)
    assert report.total_requirements == 5
    assert report.impl_covered_count == 3
    assert report.test_covered_count == 0
    assert report.fully_covered_count == 0
    assert len(report.rows) == 5


def test_coverage_pct_all_covered() -> None:
    reqs = [_req(f"R{i}") for i in range(4)]
    codes = [_code(f"C{i}") for i in range(4)]
    links = [_link(codes[i].id, reqs[i].id, TraceLinkType.SATISFIES) for i in range(4)]
    report = build_coverage_matrix(reqs + codes, links)
    assert report.impl_coverage_pct == 1.0


def test_coverage_pct_none_covered() -> None:
    reqs = [_req(f"R{i}") for i in range(3)]
    report = build_coverage_matrix(reqs, [])
    assert report.impl_coverage_pct == 0.0
    assert report.test_coverage_pct == 0.0


# ---------------------------------------------------------------------------
# Kind-bucket columns
# ---------------------------------------------------------------------------


def test_kind_column_populated_for_linked_design_artifact() -> None:
    req = _req()
    des = _design("DesignDoc")
    lnk = _link(des.id, req.id, TraceLinkType.SATISFIES)
    report = build_coverage_matrix([req, des], [lnk])
    row = report.rows[0]
    assert "DesignDoc" in row.kind_artifacts.get(ArtifactKind.DESIGN.value, [])


def test_kind_columns_empty_when_no_non_req_links() -> None:
    req = _req()
    report = build_coverage_matrix([req], [])
    row = report.rows[0]
    for k in _KIND_COLUMNS:
        assert row.kind_artifacts.get(k.value, []) == []


# ---------------------------------------------------------------------------
# CSV well-formedness
# ---------------------------------------------------------------------------


def test_csv_header_matches_spec() -> None:
    req = _req()
    report = build_coverage_matrix([req], [])
    reader = csv.reader(io.StringIO(export_csv(report)))
    header = next(reader)
    assert header == _CSV_COLUMNS


def test_csv_row_count_matches_requirements() -> None:
    reqs = [_req(f"R{i}") for i in range(3)]
    report = build_coverage_matrix(reqs, [])
    reader = csv.reader(io.StringIO(export_csv(report)))
    rows = list(reader)
    assert len(rows) == 4  # header + 3 data rows


def test_csv_covered_cell_contains_artifact_title() -> None:
    req = _req("My Requirement")
    code = _code("my_module.py")
    lnk = _link(code.id, req.id, TraceLinkType.SATISFIES)
    report = build_coverage_matrix([req, code], [lnk])
    reader = csv.reader(io.StringIO(export_csv(report)))
    _header = next(reader)
    data_row = next(reader)
    impl_artifacts_idx = _CSV_COLUMNS.index("impl_artifacts")
    assert "my_module.py" in data_row[impl_artifacts_idx]


def test_csv_multiple_artifacts_pipe_separated() -> None:
    req = _req()
    c1 = _code("CodeA")
    c2 = _code("CodeB")
    l1 = _link(c1.id, req.id, TraceLinkType.SATISFIES)
    l2 = _link(c2.id, req.id, TraceLinkType.SATISFIES)
    report = build_coverage_matrix([req, c1, c2], [l1, l2])
    reader = csv.reader(io.StringIO(export_csv(report)))
    _header = next(reader)
    data_row = next(reader)
    impl_artifacts_idx = _CSV_COLUMNS.index("impl_artifacts")
    cell = data_row[impl_artifacts_idx]
    parts = cell.split("|")
    assert len(parts) == 2
    assert "CodeA" in parts
    assert "CodeB" in parts


def test_csv_commas_and_quotes_in_title_escaped() -> None:
    """Titles with commas or quotes must be safely enclosed by csv.writer."""
    req = _req('Req with "quotes" and, commas')
    report = build_coverage_matrix([req], [])
    csv_text = export_csv(report)
    reader = csv.reader(io.StringIO(csv_text))
    _header = next(reader)
    data_row = next(reader)
    req_title_idx = _CSV_COLUMNS.index("requirement_title")
    assert data_row[req_title_idx] == 'Req with "quotes" and, commas'


# ---------------------------------------------------------------------------
# JSON structure
# ---------------------------------------------------------------------------


def test_json_meta_contains_required_keys() -> None:
    report = build_coverage_matrix([], [])
    data = json.loads(export_json(report))
    required_keys = {
        "total_requirements",
        "total_artifacts",
        "total_links",
        "impl_covered",
        "test_covered",
        "fully_covered",
        "impl_coverage_pct",
        "test_coverage_pct",
    }
    assert required_keys <= set(data["meta"].keys())


def test_json_row_contains_required_keys() -> None:
    req = _req("R1")
    report = build_coverage_matrix([req], [])
    data = json.loads(export_json(report))
    row = data["rows"][0]
    required = {
        "requirement_id",
        "requirement_title",
        "impl_covered",
        "impl_artifacts",
        "test_covered",
        "test_artifacts",
    }
    assert required <= set(row.keys())


def test_json_impl_covered_boolean_true_when_linked() -> None:
    req = _req()
    code = _code()
    lnk = _link(code.id, req.id, TraceLinkType.SATISFIES)
    report = build_coverage_matrix([req, code], [lnk])
    data = json.loads(export_json(report))
    assert data["rows"][0]["impl_covered"] is True


def test_json_impl_covered_boolean_false_when_not_linked() -> None:
    req = _req()
    report = build_coverage_matrix([req], [])
    data = json.loads(export_json(report))
    assert data["rows"][0]["impl_covered"] is False


def test_json_columns_field_matches_csv_columns() -> None:
    report = build_coverage_matrix([], [])
    data = json.loads(export_json(report))
    assert data["columns"] == _CSV_COLUMNS
