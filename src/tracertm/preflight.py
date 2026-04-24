"""Preflight resource checks for TraceRTM services with wait+retry."""

from __future__ import annotations

import logging
import os
import socket
import time
from dataclasses import dataclass
from typing import TYPE_CHECKING
from urllib.parse import urlparse

if TYPE_CHECKING:
    from collections.abc import Iterable

logger = logging.getLogger(__name__)

# Retry config for preflight checks (give services time to start)
PREFLIGHT_MAX_ATTEMPTS = 3
PREFLIGHT_INITIAL_DELAY = 1.0
PREFLIGHT_BACKOFF = 2.0
PREFLIGHT_BACKOFF_MAX_SECONDS = 30.0  # Cap wait between retries (indefinite retry)

# HTTP status range for success
HTTP_OK_MIN = 200
HTTP_OK_MAX = 300


@dataclass(frozen=True)
class PreflightCheck:
    """PreflightCheck."""

    name: str
    url: str | None
    required: bool = True
    kind: str = "tcp"  # tcp, http, or env
    path: str = "/health"
    timeout: float = 2.0


@dataclass(frozen=True)
class PreflightResult:
    """PreflightResult."""

    name: str
    ok: bool
    message: str
    required: bool


def _parse_host_port(url: str, default_port: int | None) -> tuple[str, int | None]:
    parsed = urlparse(url)
    host = parsed.hostname or ""
    port = parsed.port
    if not host and parsed.scheme and ":" in parsed.scheme and not parsed.netloc:
        # Handle host:port without scheme (urlparse treats host as scheme)
        host_part, port_part = parsed.scheme.split(":", 1)
        host = host_part
        try:
            port = int(port_part)
        except ValueError:
            port = None
    if not host and parsed.scheme and parsed.netloc and not parsed.path:
        # Handle host:port when urlparse puts host in scheme and port in netloc (e.g. 127.0.0.1:7233)
        try:
            port = int(parsed.netloc)
            host = parsed.scheme
        except ValueError:
            port = None
    if not host and parsed.scheme and parsed.path and not parsed.netloc:
        # Handle host:port when urlparse puts host in scheme and port in path (e.g. localhost:7233)
        try:
            port = int(parsed.path)
            host = parsed.scheme
        except ValueError:
            port = None
    if port is None:
        port = default_port
    return host, port


def _tcp_check(url: str, default_port: int | None, timeout: float) -> PreflightResult:
    host, port = _parse_host_port(url, default_port)
    if not host or not port:
        return PreflightResult(url, False, "missing host/port", True)

    # Prefer IPv4 for "localhost" so we reach services that only listen on 127.0.0.1 (e.g. Temporal)
    connect_host = "127.0.0.1" if host.lower() == "localhost" else host

    try:
        with socket.create_connection((connect_host, port), timeout=timeout):
            return PreflightResult(url, True, "ok", True)
    except OSError as exc:
        return PreflightResult(url, False, str(exc), True)


def _env_check(name: str, value: str | None) -> PreflightResult:
    if value and value.strip():
        return PreflightResult(name, True, "ok", True)
    return PreflightResult(name, False, "missing", True)


def _http_check(url: str, path: str, timeout: float) -> PreflightResult:
    import urllib.error
    import urllib.request

    base = url.rstrip("/")
    full_url = f"{base}{path}"
    parsed = urlparse(full_url)
    scheme = (parsed.scheme or "").lower()
    if scheme not in {"http", "https"}:
        return PreflightResult(full_url, False, "only http/https URLs allowed", True)
    try:
        req = urllib.request.Request(full_url, method="GET")
        with urllib.request.urlopen(req, timeout=timeout) as resp:  # nosec B310 -- URL scheme validated above
            if HTTP_OK_MIN <= resp.status < HTTP_OK_MAX:
                return PreflightResult(full_url, True, "ok", True)
            return PreflightResult(full_url, False, f"status {resp.status}", True)
    except (OSError, TimeoutError, urllib.error.URLError, ValueError) as exc:
        return PreflightResult(full_url, False, str(exc), True)


def run_single_check(check: PreflightCheck) -> PreflightResult:
    """Run one preflight check and return the result."""
    if not check.url:
        return PreflightResult(check.name, False, "missing url", check.required)
    if check.kind == "env":
        return _env_check(check.name, check.url)
    if check.kind == "http":
        return _http_check(check.url, check.path, check.timeout)
    default_port = _default_port_for_url(check.url)
    return _tcp_check(check.url, default_port, check.timeout)


def run_single_check_with_retry(
    check: PreflightCheck,
    max_attempts: int | None = PREFLIGHT_MAX_ATTEMPTS,
    initial_delay: float = PREFLIGHT_INITIAL_DELAY,
    backoff: float = PREFLIGHT_BACKOFF,
    backoff_max: float = PREFLIGHT_BACKOFF_MAX_SECONDS,
) -> PreflightResult:
    """Run one preflight check with wait+retry. Progressive backoff (cap at backoff_max).

    If max_attempts is None, retry indefinitely until success.
    """
    result = run_single_check(check)
    if result.ok:
        return result
    delay = initial_delay
    attempt = 0
    while True:
        attempt += 1
        if max_attempts is not None and attempt >= max_attempts:
            return result
        logger.info(
            "[preflight] %s failed (attempt %s), retrying in %.1fs%s",
            check.name,
            attempt,
            delay,
            "" if max_attempts is None else f"/{max_attempts}",
        )
        time.sleep(delay)
        result = run_single_check(check)
        if result.ok:
            return result
        delay = min(delay * backoff, backoff_max)


def run_preflight(
    service_name: str,
    checks: Iterable[PreflightCheck],
    strict: bool,
    exclude_names: Iterable[str] | None = None,
) -> None:
    """Run preflight checks. If exclude_names is set, skip those (caller runs them with retry)."""
    exclude = set(exclude_names or ())
    failures: list[PreflightResult] = []

    for check in checks:
        if check.name in exclude:
            continue
        if not check.url:
            if check.required:
                failures.append(PreflightResult(check.name, False, "missing url", check.required))
            else:
                logger.debug("[%s] optional check '%s' missing URL", service_name, check.name)
            continue

        if check.kind == "env":
            result = _env_check(check.name, check.url)
        elif check.kind == "http":
            result = run_single_check_with_retry(
                check,
                max_attempts=None,
                initial_delay=PREFLIGHT_INITIAL_DELAY,
                backoff=PREFLIGHT_BACKOFF,
                backoff_max=PREFLIGHT_BACKOFF_MAX_SECONDS,
            )
        else:
            result = run_single_check_with_retry(
                check,
                max_attempts=None,
                initial_delay=PREFLIGHT_INITIAL_DELAY,
                backoff=PREFLIGHT_BACKOFF,
                backoff_max=PREFLIGHT_BACKOFF_MAX_SECONDS,
            )

        if not result.ok:
            msg = f"{check.name} failed: {result.message} ({check.url})"
            if check.required:
                failures.append(PreflightResult(check.name, False, msg, True))
            else:
                logger.debug("[%s] %s", service_name, msg)
        else:
            logger.info("[%s] %s ok", service_name, check.name)

    if failures and strict:
        messages = ", ".join(f.name for f in failures)
        msg = f"Preflight failed for: {messages}"
        raise RuntimeError(msg)


def run_preflight_with_results(
    service_name: str,
    checks: Iterable[PreflightCheck],
    strict: bool = False,
    exclude_names: Iterable[str] | None = None,
    max_attempts: int | None = PREFLIGHT_MAX_ATTEMPTS,
) -> tuple[bool, list[PreflightResult]]:
    """Run preflight checks and return (all_passed, list of results).

    Does not raise; callers can format failures with format_preflight_failures().
    max_attempts: retries per check (default 3); use None for indefinite retry.
    """
    exclude = set(exclude_names or ())
    all_results: list[PreflightResult] = []
    failures: list[PreflightResult] = []

    for check in checks:
        if check.name in exclude:
            continue
        if not check.url:
            res = PreflightResult(check.name, False, "missing url", check.required)
            all_results.append(res)
            if check.required:
                failures.append(res)
            else:
                logger.debug("[%s] optional check '%s' missing URL", service_name, check.name)
            continue

        if check.kind == "env":
            result = _env_check(check.name, check.url)
        elif check.kind == "http":
            result = run_single_check_with_retry(
                check,
                max_attempts=max_attempts,
                initial_delay=PREFLIGHT_INITIAL_DELAY,
                backoff=PREFLIGHT_BACKOFF,
                backoff_max=PREFLIGHT_BACKOFF_MAX_SECONDS,
            )
        else:
            result = run_single_check_with_retry(
                check,
                max_attempts=max_attempts,
                initial_delay=PREFLIGHT_INITIAL_DELAY,
                backoff=PREFLIGHT_BACKOFF,
                backoff_max=PREFLIGHT_BACKOFF_MAX_SECONDS,
            )

        # Normalize result name to check.name so callers get "neo4j" not "neo4j://localhost:7687"
        normalized = PreflightResult(check.name, result.ok, result.message, result.required)
        all_results.append(normalized)
        if not normalized.ok:
            if check.required:
                failures.append(normalized)
            else:
                logger.debug("[%s] %s failed: %s", service_name, check.name, result.message)
        else:
            logger.info("[%s] %s ok", service_name, check.name)

    passed = len(failures) == 0
    if failures and strict:
        # Caller asked for strict: still return so they can print details
        pass
    return passed, all_results


def format_preflight_failures(results: list[PreflightResult]) -> str:
    """Format failed preflight results for display (no need to run 'rtm dev check')."""
    failed = [r for r in results if not r.ok]
    if not failed:
        return ""
    lines = ["Service preflight failed:", ""]
    lines.extend(f"  • {r.name}: {r.message}" for r in failed)
    lines.extend(("", "Fix the service issues above and try again."))
    return "\n".join(lines)


def _default_port_for_url(url: str) -> int | None:
    parsed = urlparse(url)
    scheme = (parsed.scheme or "").lower()

    if scheme in {"postgres", "postgresql", "postgresql+asyncpg"}:
        return 5432
    if scheme in {"redis", "rediss"}:
        return 6379
    if scheme == "nats":
        return 4222
    if scheme in {"neo4j", "bolt"}:
        return 7687
    if scheme == "http":
        return 80
    if scheme == "https":
        return 443
    return None


def build_api_checks() -> list[PreflightCheck]:
    """Build API checks for the current cache, database, messaging, and storage runtime."""
    return [
        PreflightCheck("database", os.getenv("DATABASE_URL"), required=True, kind="tcp"),
        PreflightCheck("cache", os.getenv("REDIS_URL"), required=True, kind="tcp"),
        PreflightCheck("nats", os.getenv("NATS_URL"), required=True, kind="tcp"),
        PreflightCheck("neo4j", os.getenv("NEO4J_URI"), required=True, kind="tcp"),
        PreflightCheck("go-backend", os.getenv("GO_BACKEND_URL"), required=False, kind="http"),
        PreflightCheck("s3-endpoint", os.getenv("S3_ENDPOINT"), required=True, kind="tcp"),
        PreflightCheck("s3-access-key", os.getenv("S3_ACCESS_KEY_ID"), required=True, kind="env"),
        PreflightCheck("s3-secret", os.getenv("S3_SECRET_ACCESS_KEY"), required=True, kind="env"),
        PreflightCheck("s3-bucket", os.getenv("S3_BUCKET"), required=True, kind="env"),
        PreflightCheck("temporal-host", os.getenv("TEMPORAL_HOST"), required=True, kind="tcp"),
        PreflightCheck("temporal-namespace", os.getenv("TEMPORAL_NAMESPACE"), required=True, kind="env"),
        PreflightCheck(
            "workos-api",
            os.getenv("WORKOS_API_BASE_URL", "https://api.workos.com"),
            required=True,
            kind="tcp",
        ),
        PreflightCheck("workos-client-id", os.getenv("WORKOS_CLIENT_ID"), required=True, kind="env"),
        PreflightCheck("workos-api-key", os.getenv("WORKOS_API_KEY"), required=True, kind="env"),
        PreflightCheck("workos-domain", os.getenv("WORKOS_AUTHKIT_DOMAIN"), required=True, kind="env"),
    ]


def build_mcp_checks() -> list[PreflightCheck]:
    """Build mcp checks."""
    return [
        PreflightCheck("database", os.getenv("DATABASE_URL"), required=True, kind="tcp"),
        PreflightCheck("cache", os.getenv("REDIS_URL"), required=True, kind="tcp"),
        PreflightCheck("nats", os.getenv("NATS_URL"), required=True, kind="tcp"),
        PreflightCheck("neo4j", os.getenv("NEO4J_URI"), required=True, kind="tcp"),
        PreflightCheck("go-backend", os.getenv("GO_BACKEND_URL"), required=False, kind="http"),
        PreflightCheck("s3-endpoint", os.getenv("S3_ENDPOINT"), required=True, kind="tcp"),
        PreflightCheck("s3-access-key", os.getenv("S3_ACCESS_KEY_ID"), required=True, kind="env"),
        PreflightCheck("s3-secret", os.getenv("S3_SECRET_ACCESS_KEY"), required=True, kind="env"),
        PreflightCheck("s3-bucket", os.getenv("S3_BUCKET"), required=True, kind="env"),
        PreflightCheck("temporal-host", os.getenv("TEMPORAL_HOST"), required=True, kind="tcp"),
        PreflightCheck("temporal-namespace", os.getenv("TEMPORAL_NAMESPACE"), required=True, kind="env"),
        PreflightCheck(
            "workos-api",
            os.getenv("WORKOS_API_BASE_URL", "https://api.workos.com"),
            required=True,
            kind="tcp",
        ),
        PreflightCheck("workos-client-id", os.getenv("WORKOS_CLIENT_ID"), required=True, kind="env"),
        PreflightCheck("workos-api-key", os.getenv("WORKOS_API_KEY"), required=True, kind="env"),
        PreflightCheck("workos-domain", os.getenv("WORKOS_AUTHKIT_DOMAIN"), required=True, kind="env"),
    ]


def check_cli_available() -> bool:
    """Check cli available."""
    return True


def build_dev_start_checks() -> list[PreflightCheck]:
    """Preflight for 'rtm dev start' / 'rtm dev restart': only infra we don't start.

    These commands start Go backend, Python API, etc. So we only check that
    PostgreSQL, the cache runtime, NATS, and Neo4j are reachable (typically via brew/docker).
    """
    return [
        PreflightCheck("database", os.getenv("DATABASE_URL"), required=True, kind="tcp"),
        PreflightCheck("cache", os.getenv("REDIS_URL"), required=True, kind="tcp"),
        PreflightCheck("nats", os.getenv("NATS_URL"), required=True, kind="tcp"),
        PreflightCheck("neo4j", os.getenv("NEO4J_URI"), required=True, kind="tcp"),
    ]


def build_cli_checks() -> list[PreflightCheck]:
    """Full CLI preflight for commands that assume backends are already running."""
    return [
        PreflightCheck("database", os.getenv("DATABASE_URL"), required=True, kind="tcp"),
        PreflightCheck("cache", os.getenv("REDIS_URL"), required=True, kind="tcp"),
        PreflightCheck("nats", os.getenv("NATS_URL"), required=True, kind="tcp"),
        PreflightCheck("neo4j", os.getenv("NEO4J_URI"), required=True, kind="tcp"),
        PreflightCheck("go-backend", os.getenv("GO_BACKEND_URL"), required=False, kind="http"),
        PreflightCheck("s3-endpoint", os.getenv("S3_ENDPOINT"), required=True, kind="tcp"),
        PreflightCheck("s3-access-key", os.getenv("S3_ACCESS_KEY_ID"), required=True, kind="env"),
        PreflightCheck("s3-secret", os.getenv("S3_SECRET_ACCESS_KEY"), required=True, kind="env"),
        PreflightCheck("s3-bucket", os.getenv("S3_BUCKET"), required=True, kind="env"),
        PreflightCheck("temporal-host", os.getenv("TEMPORAL_HOST"), required=True, kind="tcp"),
        PreflightCheck("temporal-namespace", os.getenv("TEMPORAL_NAMESPACE"), required=True, kind="env"),
        PreflightCheck(
            "workos-api",
            os.getenv("WORKOS_API_BASE_URL", "https://api.workos.com"),
            required=True,
            kind="tcp",
        ),
        PreflightCheck("workos-client-id", os.getenv("WORKOS_CLIENT_ID"), required=True, kind="env"),
        PreflightCheck("workos-api-key", os.getenv("WORKOS_API_KEY"), required=True, kind="env"),
        PreflightCheck("workos-domain", os.getenv("WORKOS_AUTHKIT_DOMAIN"), required=True, kind="env"),
    ]
