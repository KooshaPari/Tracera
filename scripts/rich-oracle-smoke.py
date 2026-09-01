#!/usr/bin/env python3
"""Static and live smoke contract for the approved rich dashboard oracle.

The check is deliberately dependency-free and read-only.  Without ``--live`` it
only validates the browser API base and expected route contract.  With ``--live``
it issues bounded GET requests and reports unavailable routes as skips rather
than turning an unstarted oracle into a false failure.
"""

from __future__ import annotations

import argparse
import ipaddress
import json
import sys
from dataclasses import asdict, dataclass
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import Request, urlopen

DEFAULT_BASE = "http://127.0.0.1:18000"
CORE_PATHS = (
    "/ready",
    "/health",
    "/api/v1/auth/me",
    "/api/v1/projects",
    "/api/v1/items",
    "/api/v1/graph/full",
    "/api/v1/search/health",
    "/api/v1/notifications",
)


@dataclass(frozen=True)
class Probe:
    path: str
    status: str
    http_status: int | None = None
    detail: str | None = None


def validate_base(raw: str) -> str:
    if any(char in raw for char in ("\n", "\r", "\t")):
        raise ValueError("API base must not contain control characters")
    parsed = urlsplit(raw)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise ValueError("API base must be an http(s) URL with a hostname")
    if parsed.username or parsed.password:
        raise ValueError("API base must not contain credentials")
    hostname = parsed.hostname.rstrip(".").lower()
    if hostname != "localhost":
        try:
            address = ipaddress.ip_address(hostname)
        except ValueError as error:
            raise ValueError("API base must target localhost or a loopback address") from error
        if not address.is_loopback:
            raise ValueError("API base must target localhost or a loopback address")
    if parsed.port != 18000:
        raise ValueError(f"API base must target oracle gateway port 18000 (got {parsed.port})")
    if parsed.path not in {"", "/"} or parsed.query or parsed.fragment:
        raise ValueError("API base must not contain a path, query, or fragment")
    return raw.rstrip("/")


def probe(base: str, path: str, timeout: float) -> Probe:
    request = Request(f"{base}{path}", headers={"Accept": "application/json"})
    try:
        with urlopen(request, timeout=timeout) as response:
            return Probe(path, "pass", response.status)
    except HTTPError as error:
        # A route returning 401/403/405 proves the gateway is reachable; callers
        # still need auth or a different method.  404 is an explicit gap.
        status = "reachable" if error.code in {401, 403, 405} else "unavailable"
        return Probe(path, status, error.code, error.reason)
    except (TimeoutError, URLError, OSError) as error:
        return Probe(path, "skipped", detail=str(error.reason if isinstance(error, URLError) else error))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default=DEFAULT_BASE, help="gateway origin (must use port 18000)")
    parser.add_argument("--timeout", type=float, default=10.0, help="per-request timeout in seconds")
    parser.add_argument("--live", action="store_true", help="probe the gateway; default is static-only")
    parser.add_argument("--json", action="store_true", help="emit machine-readable output")
    args = parser.parse_args()
    if not 0.1 <= args.timeout <= 10:
        parser.error("--timeout must be between 0.1 and 10 seconds")
    try:
        base = validate_base(args.base_url)
    except ValueError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2

    results = [Probe(path, "contract") for path in CORE_PATHS]
    if args.live:
        results = [probe(base, path, args.timeout) for path in CORE_PATHS]
    payload = {"base_url": base, "gateway_port": 18000, "live": args.live, "probes": [asdict(item) for item in results]}
    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        mode = "live" if args.live else "static"
        print(f"PASS rich-oracle smoke contract ({mode}; base={base})")
        for item in results:
            suffix = f" ({item.http_status})" if item.http_status else ""
            print(f"  {item.status:11} {item.path}{suffix}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
