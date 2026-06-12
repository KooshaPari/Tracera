"""Traceability matrix construction helpers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterable


@dataclass(frozen=True, slots=True)
class MatrixCell:
    """One source-to-target relationship in a traceability matrix."""

    source_id: str
    target_id: str
    relationship: str


@dataclass(frozen=True, slots=True)
class TraceabilityMatrix:
    """Sparse traceability matrix optimized for fast construction."""

    source_ids: tuple[str, ...]
    target_ids: tuple[str, ...]
    cells: tuple[MatrixCell, ...]


def build_traceability_matrix(links: Iterable[tuple[str, str, str]]) -> TraceabilityMatrix:
    """Build a deterministic sparse matrix from source, target, relationship links."""
    source_seen: set[str] = set()
    target_seen: set[str] = set()
    source_ids: list[str] = []
    target_ids: list[str] = []
    cells: list[MatrixCell] = []

    for source_id, target_id, relationship in links:
        if source_id not in source_seen:
            source_seen.add(source_id)
            source_ids.append(source_id)
        if target_id not in target_seen:
            target_seen.add(target_id)
            target_ids.append(target_id)
        cells.append(MatrixCell(source_id, target_id, relationship))

    return TraceabilityMatrix(tuple(source_ids), tuple(target_ids), tuple(cells))
