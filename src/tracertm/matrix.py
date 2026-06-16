"""TraceabilityMatrix: requirement-to-artifact coverage matrix with export methods."""

from dataclasses import dataclass, field
from typing import List, Dict
import json
import csv
import io


@dataclass
class TraceabilityMatrix:
    """Requirement-to-artifact coverage matrix.

    Mirrors the Rust ``CoverageMatrix`` concept from ``crates/tracera-core/src/matrix.rs``
    at a simpler, export-oriented level.
    """

    requirements: List[str] = field(default_factory=list)
    artifacts: List[str] = field(default_factory=list)
    links: Dict[str, List[str]] = field(default_factory=dict)  # req_id -> [artifact_ids]

    def coverage_ratio(self) -> float:
        """Fraction of requirements that have at least one linked artifact."""
        if not self.requirements:
            return 0.0
        covered = sum(1 for r in self.requirements if self.links.get(r))
        return covered / len(self.requirements)

    def to_json(self) -> str:
        """Serialize the matrix to a JSON string."""
        return json.dumps(
            {
                "requirements": self.requirements,
                "artifacts": self.artifacts,
                "links": self.links,
                "coverage_ratio": self.coverage_ratio(),
            },
            indent=2,
        )

    def to_csv(self) -> str:
        """Serialize the matrix to a CSV string (requirements as rows, artifacts as columns)."""
        buf = io.StringIO()
        writer = csv.writer(buf)
        writer.writerow(["requirement_id"] + self.artifacts)
        for req in self.requirements:
            linked = self.links.get(req, [])
            row = [req] + ["X" if a in linked else "" for a in self.artifacts]
            writer.writerow(row)
        return buf.getvalue()

    def uncovered_requirements(self) -> List[str]:
        """Return requirement IDs that have no linked artifacts."""
        return [r for r in self.requirements if not self.links.get(r)]
