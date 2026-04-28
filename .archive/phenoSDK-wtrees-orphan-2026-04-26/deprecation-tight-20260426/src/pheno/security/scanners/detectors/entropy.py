from __future__ import annotations

import math
from typing import TYPE_CHECKING

from pheno.security.scanners.models import SecretFinding

if TYPE_CHECKING:
    from collections.abc import Iterable
    from pathlib import Path


def calculate_entropy(data: str) -> float:
    if not data:
        return 0.0
    occurrences = {char: data.count(char) for char in set(data)}
    length = len(data)
    return -sum((count / length) * math.log2(count / length) for count in occurrences.values())


def scan_entropy(
    *,
    file_path: Path,
    lines: Iterable[tuple[int, str]],
    threshold: float,
) -> list[SecretFinding]:
    findings: list[SecretFinding] = []
    for line_no, text in lines:
        candidates = [segment for segment in text.split() if len(segment) >= 20]
        for candidate in candidates:
            entropy = calculate_entropy(candidate)
            if entropy >= threshold:
                findings.append(
                    SecretFinding(
                        detector="entropy",
                        file_path=file_path,
                        line=line_no,
                        context=text.strip(),
                        severity="medium" if entropy < threshold + 0.5 else "high",
                        fingerprint=f"entropy:{file_path}:{line_no}:{hash(candidate)}",
                        entropy=entropy,
                        tags=("heuristic",),
                    ),
                )
    return findings
