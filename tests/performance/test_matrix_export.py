"""Tests for traceability matrix export helpers."""

from __future__ import annotations

import csv
import json

import pytest

from tracertm.performance.matrix import TraceabilityMatrix, build_traceability_matrix


def _matrix() -> TraceabilityMatrix:
    return build_traceability_matrix(
        (
            ("REQ-1", "TC-1", "verifies"),
            ("REQ-1", "TC-2", "covers"),
            ("REQ-2", "TC-2", "depends_on"),
        )
    )


def test_matrix_to_records_preserves_cell_order() -> None:
    assert _matrix().to_records() == [
        {"source_id": "REQ-1", "target_id": "TC-1", "relationship": "verifies"},
        {"source_id": "REQ-1", "target_id": "TC-2", "relationship": "covers"},
        {"source_id": "REQ-2", "target_id": "TC-2", "relationship": "depends_on"},
    ]


def test_matrix_exports_json_records(tmp_path) -> None:
    export_path = tmp_path / "matrix.json"

    _matrix().export_json(export_path)

    assert json.loads(export_path.read_text(encoding="utf-8")) == _matrix().to_records()


def test_matrix_exports_csv_records(tmp_path) -> None:
    export_path = tmp_path / "matrix.csv"

    _matrix().export_csv(export_path)

    with export_path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    assert rows == _matrix().to_records()


def test_matrix_exports_parquet_records(tmp_path) -> None:
    export_path = tmp_path / "matrix.parquet"
    try:
        import pyarrow.parquet as pq
    except ModuleNotFoundError:
        with pytest.raises(RuntimeError, match="requires pyarrow"):
            _matrix().export_parquet(export_path)
        return

    _matrix().export_parquet(export_path)

    assert pq.read_table(export_path).to_pylist() == _matrix().to_records()
