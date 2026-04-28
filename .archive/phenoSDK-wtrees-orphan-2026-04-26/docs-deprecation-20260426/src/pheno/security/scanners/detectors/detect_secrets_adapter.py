from __future__ import annotations

from typing import TYPE_CHECKING

from pheno.logging.core.logger import get_logger
from pheno.security.scanners.models import SecretFinding

if TYPE_CHECKING:
    from collections.abc import Iterable
    from pathlib import Path

logger = get_logger("pheno.security.detect_secrets")

try:  # pragma: no cover - optional dependency
    from detect_secrets.core.scan import scan_file  # type: ignore
    from detect_secrets.settings import default_settings  # type: ignore
except ImportError:  # pragma: no cover - optional dependency
    scan_file = None
    default_settings = None


def run_detect_secrets(
    *,
    file_path: Path,
    lines: Iterable[tuple[int, str]],
) -> list[SecretFinding]:
    if scan_file is None or default_settings is None:
        return []

    line_lookup = dict(lines)
    findings: list[SecretFinding] = []

    try:
        with default_settings():
            secrets = list(scan_file(str(file_path)))
    except Exception as exc:  # pragma: no cover - defensive low-probability path
        logger.warning("detect_secrets_failed", file=str(file_path), error=str(exc))
        return []

    for secret in secrets:
        line_no = getattr(secret, "line_number", None) or getattr(secret, "line", 0)
        secret_type = getattr(secret, "type", getattr(secret, "secret_type", "unknown"))
        fingerprint = getattr(secret, "hashed_secret", getattr(secret, "secret_hash", ""))
        line_text = line_lookup.get(line_no, "")
        findings.append(
            SecretFinding(
                detector="detect-secrets",
                file_path=file_path,
                line=line_no,
                context=line_text.strip(),
                severity="high",
                fingerprint=f"detect-secrets:{fingerprint}",
                entropy=None,
                tags=(secret_type,),
            ),
        )

    return findings
