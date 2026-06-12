"""Traceability matrix construction helpers."""

from __future__ import annotations

import csv
import importlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterable

MATRIX_EXPORT_FIELDS = ("source_id", "target_id", "relationship")
PARQUET_DEPENDENCY_ERROR = "Parquet export requires pyarrow to be installed"


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

    def to_records(self) -> list[dict[str, str]]:
        """Return matrix cells as deterministic row dictionaries."""
        return [
            {
                "source_id": cell.source_id,
                "target_id": cell.target_id,
                "relationship": cell.relationship,
            }
            for cell in self.cells
        ]

    def export_json(self, path: str | Path) -> None:
        """Write matrix cells to a JSON array of records."""
        Path(path).write_text(
            json.dumps(self.to_records(), indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

    def export_csv(self, path: str | Path) -> None:
        """Write matrix cells to CSV with a stable header."""
        with Path(path).open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=MATRIX_EXPORT_FIELDS)
            writer.writeheader()
            writer.writerows(self.to_records())

    def export_parquet(self, path: str | Path) -> None:
        """Write matrix cells to Parquet using pyarrow."""
        try:
            pa = importlib.import_module("pyarrow")
            pq = importlib.import_module("pyarrow.parquet")
        except ModuleNotFoundError as exc:
            raise RuntimeError(PARQUET_DEPENDENCY_ERROR) from exc

        columns: dict[str, list[str]] = {field: [] for field in MATRIX_EXPORT_FIELDS}
        for cell in self.cells:
            columns["source_id"].append(cell.source_id)
            columns["target_id"].append(cell.target_id)
            columns["relationship"].append(cell.relationship)

        pq.write_table(pa.table(columns), path)


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
