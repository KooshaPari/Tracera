from __future__ import annotations

import json
import shutil
import subprocess
from typing import TYPE_CHECKING

from pheno.logging.core.logger import get_logger
from pheno.security.scanners.models import SecretFinding

if TYPE_CHECKING:
    from collections.abc import Iterable
    from pathlib import Path

logger = get_logger("pheno.security.trufflehog")


def run_trufflehog(
    *,
    file_path: Path,
    lines: Iterable[tuple[int, str]],
) -> list[SecretFinding]:
    executable = shutil.which("trufflehog")
    if executable is None:
        return []

    try:
        process = subprocess.run(
            [executable, "filesystem", str(file_path), "--json"],
            check=False,
            capture_output=True,
            text=True,
        )
    except OSError as exc:  # pragma: no cover
        logger.warning("trufflehog_failed_launch", file=str(file_path), error=str(exc))
        return []

    if process.returncode not in {0, 183}:  # 183 indicates findings detected
        if process.stderr:
            logger.warning(
                "trufflehog_nonzero", code=process.returncode, stderr=process.stderr.strip(),
            )
        return []

    findings: list[SecretFinding] = []
    line_lookup = dict(lines)

    for raw_line in process.stdout.splitlines():
        raw_line = raw_line.strip()
        if not raw_line:
            continue
        try:
            payload = json.loads(raw_line)
        except json.JSONDecodeError:
            logger.debug("trufflehog_skip_line", line=raw_line[:80])
            continue
        source = payload.get("SourceMetadata", {}).get("Data", {})
        line_no = int(source.get("Line", 0)) or 0
        context = line_lookup.get(line_no, "")
        detector = payload.get("DetectorName", "trufflehog")
        fingerprint = payload.get("Fingerprint", "")
        findings.append(
            SecretFinding(
                detector=detector,
                file_path=file_path,
                line=line_no,
                context=context.strip(),
                severity="high",
                fingerprint=f"trufflehog:{fingerprint}",
                entropy=None,
                tags=(payload.get("DetectorType", "trufflehog"),),
            ),
        )
    return findings
