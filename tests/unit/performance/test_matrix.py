"""Unit tests for tracertm.performance.matrix."""

import pytest

from tracertm.performance.matrix import MatrixCell, TraceabilityMatrix, build_traceability_matrix


def test_build_traceability_matrix_empty() -> None:
    """build_traceability_matrix returns empty matrix for empty input."""
    result = build_traceability_matrix([])
    assert result == TraceabilityMatrix((), (), ())


def test_build_traceability_matrix_preserves_order_and_dedupes_ids() -> None:
    """build_traceability_matrix preserves first-seen order and deduplicates source/target ids."""
    links = [
        ("REQ-1", "TC-1", "verified_by"),
        ("REQ-1", "TC-2", "verified_by"),  # duplicate source
        ("REQ-2", "TC-1", "traced_to"),    # duplicate target
        ("REQ-3", "TC-3", "related_to"),
    ]
    result = build_traceability_matrix(links)

    assert result.source_ids == ("REQ-1", "REQ-2", "REQ-3")
    assert result.target_ids == ("TC-1", "TC-2", "TC-3")
    assert result.cells == (
        MatrixCell("REQ-1", "TC-1", "verified_by"),
        MatrixCell("REQ-1", "TC-2", "verified_by"),
        MatrixCell("REQ-2", "TC-1", "traced_to"),
        MatrixCell("REQ-3", "TC-3", "related_to"),
    )
