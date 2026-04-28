from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from collections.abc import Iterable
    from pathlib import Path

Severity = Literal["low", "medium", "high"]


@dataclass(frozen=True, slots=True)
class SecretFinding:
    detector: str
    file_path: Path
    line: int
    context: str
    severity: Severity
    fingerprint: str
    entropy: float | None = None
    tags: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class ScanSummary:
    findings: tuple[SecretFinding, ...]
    suppressed: tuple[SecretFinding, ...]
    duration_ms: int


@dataclass(frozen=True, slots=True)
class SuppressionRules:
    allowed_paths: tuple[str, ...] = ()
    allowed_fingerprints: tuple[str, ...] = ()
    allowed_detectors: tuple[str, ...] = ()

    def allows(self, finding: SecretFinding) -> bool:
        if any(finding.file_path.match(pattern) for pattern in self.allowed_paths):
            return True
        if finding.fingerprint in self.allowed_fingerprints:
            return True
        return finding.detector in self.allowed_detectors


def apply_suppressions(
    findings: Iterable[SecretFinding],
    rules: SuppressionRules | None,
) -> tuple[tuple[SecretFinding, ...], tuple[SecretFinding, ...]]:
    if rules is None:
        collected = tuple(findings)
        return collected, ()

    kept: list[SecretFinding] = []
    suppressed: list[SecretFinding] = []
    for finding in findings:
        if rules.allows(finding):
            suppressed.append(finding)
        else:
            kept.append(finding)
    return tuple(kept), tuple(suppressed)
