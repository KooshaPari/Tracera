"""Traceability matrix construction helpers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterable

import csv
import json
from pathlib import Path


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
        """Return the matrix cells as a list of dict records."""
        return [
            {"source_id": cell.source_id, "target_id": cell.target_id, "relationship": cell.relationship}
            for cell in self.cells
        ]

    def export_json(self, path: Path | str) -> None:
        """Export the matrix records as a JSON file."""
        export_path = Path(path)
        export_path.write_text(json.dumps(self.to_records(), ensure_ascii=False), encoding="utf-8")

    def export_csv(self, path: Path | str) -> None:
        """Export the matrix records as a CSV file."""
        export_path = Path(path)
        fieldnames = ["source_id", "target_id", "relationship"]
        with export_path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.to_records())

    def export_parquet(self, path: Path | str) -> None:
        """Export the matrix records as a Parquet file."""
        try:
            import pyarrow as pa
            import pyarrow.parquet as pq
        except ModuleNotFoundError as exc:
            raise RuntimeError("export_parquet requires pyarrow") from exc
        export_path = Path(path)
        table = pa.Table.from_pylist(self.to_records())
        pq.write_table(table, str(export_path))


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
