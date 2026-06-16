"""Unit tests for TraceabilityMatrix."""
import json
import pytest
from tracertm.matrix import TraceabilityMatrix


def make_matrix() -> TraceabilityMatrix:
    m = TraceabilityMatrix()
    m.requirements = ["req-1", "req-2", "req-3"]
    m.artifacts = ["art-1", "art-2"]
    m.links = {"req-1": ["art-1"], "req-2": ["art-1", "art-2"]}
    return m


def test_coverage_ratio_partial():
    m = make_matrix()
    assert m.coverage_ratio() == pytest.approx(2 / 3)


def test_coverage_ratio_all_covered():
    m = TraceabilityMatrix()
    m.requirements = ["r1", "r2"]
    m.artifacts = ["a1"]
    m.links = {"r1": ["a1"], "r2": ["a1"]}
    assert m.coverage_ratio() == pytest.approx(1.0)


def test_coverage_ratio_none_covered():
    m = TraceabilityMatrix()
    m.requirements = ["r1", "r2"]
    m.artifacts = ["a1"]
    m.links = {}
    assert m.coverage_ratio() == pytest.approx(0.0)


def test_coverage_ratio_empty_requirements():
    m = TraceabilityMatrix()
    assert m.coverage_ratio() == 0.0


def test_uncovered_requirements():
    m = make_matrix()
    uncovered = m.uncovered_requirements()
    assert "req-3" in uncovered
    assert "req-1" not in uncovered
    assert "req-2" not in uncovered


def test_uncovered_requirements_all_linked():
    m = TraceabilityMatrix()
    m.requirements = ["r1"]
    m.artifacts = ["a1"]
    m.links = {"r1": ["a1"]}
    assert m.uncovered_requirements() == []


def test_uncovered_requirements_none_linked():
    m = TraceabilityMatrix()
    m.requirements = ["r1", "r2"]
    m.links = {}
    assert set(m.uncovered_requirements()) == {"r1", "r2"}


def test_to_json_round_trip():
    m = make_matrix()
    data = json.loads(m.to_json())
    assert data["requirements"] == m.requirements
    assert data["artifacts"] == m.artifacts
    assert data["links"] == m.links
    assert data["coverage_ratio"] == pytest.approx(m.coverage_ratio())


def test_to_csv_headers():
    m = make_matrix()
    csv_str = m.to_csv()
    lines = csv_str.strip().splitlines()
    header = lines[0]
    assert "requirement_id" in header
    assert "art-1" in header
    assert "art-2" in header


def test_to_csv_marks_linked():
    m = make_matrix()
    csv_str = m.to_csv()
    lines = csv_str.strip().splitlines()
    # req-1 row: linked to art-1 only
    req1_row = next(l for l in lines if l.startswith("req-1"))
    assert "X" in req1_row
    # req-3 row: no links
    req3_row = next(l for l in lines if l.startswith("req-3"))
    assert "X" not in req3_row


def test_to_csv_row_count():
    m = make_matrix()
    csv_str = m.to_csv()
    lines = [l for l in csv_str.strip().splitlines() if l]
    # 1 header + 3 requirements
    assert len(lines) == 4
