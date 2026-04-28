from __future__ import annotations

import asyncio
import time
from typing import TYPE_CHECKING

from pheno.logging.core.logger import get_logger
from pheno.security.scanners.detectors import (
    run_detect_secrets,
    run_trufflehog,
    scan_entropy,
)
from pheno.security.scanners.models import (
    ScanSummary,
    SecretFinding,
    SuppressionRules,
    apply_suppressions,
)

if TYPE_CHECKING:
    from collections.abc import Iterable, Sequence
    from pathlib import Path

logger = get_logger("pheno.security.pipeline")


async def scan_paths(
    paths: Iterable[Path],
    *,
    include_patterns: Sequence[str] | None = None,
    exclude_patterns: Sequence[str] | None = None,
    suppression_rules: SuppressionRules | None = None,
    entropy_threshold: float = 4.5,
) -> ScanSummary:
    """Run secret scanning over the provided paths.

    Args:
        paths: Paths to scan (files or directories).
        include_patterns: Optional glob patterns to include.
        exclude_patterns: Optional glob patterns to exclude.
        suppression_rules: Optional suppression configuration.
        entropy_threshold: Minimum entropy required for heuristic matches.
    """
    start = time.perf_counter()
    include_patterns = include_patterns or ("*.py", "*.env", "*.txt")
    exclude_patterns = exclude_patterns or ()

    target_files = _collect_files(paths, include_patterns, exclude_patterns)
    findings: list[SecretFinding] = []

    logger.debug("secret_scan_start", file_count=len(target_files))

    tasks = [
        asyncio.create_task(_scan_file(file_path, entropy_threshold=entropy_threshold))
        for file_path in target_files
    ]

    for task in asyncio.as_completed(tasks):
        findings.extend(await task)

    kept, suppressed = apply_suppressions(findings, suppression_rules)

    duration_ms = int((time.perf_counter() - start) * 1000)
    logger.debug(
        "secret_scan_complete",
        findings=len(kept),
        suppressed=len(suppressed),
        duration_ms=duration_ms,
    )

    return ScanSummary(findings=kept, suppressed=suppressed, duration_ms=duration_ms)


async def _scan_file(file_path: Path, *, entropy_threshold: float) -> list[SecretFinding]:
    lines = _read_lines(file_path)
    loop = asyncio.get_running_loop()
    from functools import partial

    detect_secrets_task = loop.run_in_executor(
        None, partial(run_detect_secrets, file_path=file_path, lines=lines),
    )
    trufflehog_task = loop.run_in_executor(
        None, partial(run_trufflehog, file_path=file_path, lines=lines),
    )
    entropy_findings = scan_entropy(file_path=file_path, lines=lines, threshold=entropy_threshold)

    detect_findings, trufflehog_findings = await asyncio.gather(
        detect_secrets_task,
        trufflehog_task,
        return_exceptions=False,
    )
    return [*detect_findings, *trufflehog_findings, *entropy_findings]


def _collect_files(
    paths: Iterable[Path],
    include_patterns: Sequence[str],
    exclude_patterns: Sequence[str],
) -> list[Path]:
    collected: list[Path] = []
    for path in paths:
        if path.is_file():
            if _matches(path, include_patterns, exclude_patterns):
                collected.append(path)
            continue
        for candidate in path.rglob("*"):
            if candidate.is_file() and _matches(candidate, include_patterns, exclude_patterns):
                collected.append(candidate)
    return collected


def _matches(path: Path, include_patterns: Sequence[str], exclude_patterns: Sequence[str]) -> bool:
    from fnmatch import fnmatch

    if not any(fnmatch(path.name, pattern) for pattern in include_patterns):
        return False
    return not any(fnmatch(path.name, pattern) for pattern in exclude_patterns)


def _read_lines(path: Path) -> list[tuple[int, str]]:
    lines: list[tuple[int, str]] = []
    try:
        with path.open("r", encoding="utf-8", errors="ignore") as fh:
            for idx, line in enumerate(fh, start=1):
                lines.append((idx, line.rstrip("\n")))
    except OSError:
        logger.debug("secret_scan_read_error", file=str(path))
    return lines
