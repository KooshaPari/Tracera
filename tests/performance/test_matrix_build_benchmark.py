"""Benchmarks for traceability matrix construction."""

from __future__ import annotations

from itertools import starmap
from time import perf_counter

import pytest

from tracertm.performance.matrix import MatrixCell, TraceabilityMatrix, build_traceability_matrix

LINK_COUNT = 10_000
REGRESSION_TOLERANCE = 1.05


def _links(count: int = LINK_COUNT) -> tuple[tuple[str, str, str], ...]:
    return tuple(
        (f"REQ-{index % 2500:04d}", f"TC-{index:05d}", "verifies")
        for index in range(count)
    )


def _reference_matrix(links: tuple[tuple[str, str, str], ...]) -> TraceabilityMatrix:
    source_ids = tuple(sorted({source_id for source_id, _, _ in links}))
    target_ids = tuple(sorted({target_id for _, target_id, _ in links}))
    cells = tuple(starmap(MatrixCell, links))
    return TraceabilityMatrix(source_ids, target_ids, cells)


def _timed_reference(links: tuple[tuple[str, str, str], ...]) -> float:
    start = perf_counter()
    _reference_matrix(links)
    return perf_counter() - start


@pytest.mark.benchmark(group="matrix-build")
@pytest.mark.performance
def test_matrix_build_10k_links_regression_gate(benchmark: pytest.FixtureRequest) -> None:
    links = _links()
    expected = _reference_matrix(links)

    result = benchmark(build_traceability_matrix, links)

    assert result == expected
    assert len(result.cells) == LINK_COUNT
    assert benchmark.stats.stats.mean <= _timed_reference(links) * REGRESSION_TOLERANCE
