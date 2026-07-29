#!/usr/bin/env python3
"""Regression checks for the disposable oracle's host-boundary overlay.

This test is intentionally dependency-free and does not contact Docker.  The
overlay is the security boundary: every published dependency port must be
loopback-only, while the backend network remains internal in Compose.
"""

from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[1]
OVERLAY = ROOT / "deploy" / "oracle-isolated" / "docker-compose.override.yml"
EXPECTED = {
    "127.0.0.1:18000:80",
    "127.0.0.1:18081:8080",
    "127.0.0.1:18080:8000",
    "127.0.0.1:15432:5432",
    "127.0.0.1:16379:6379",
    "127.0.0.1:14222:4222",
}


def main() -> int:
    text = OVERLAY.read_text(encoding="utf-8")
    published = set(re.findall(r'"([^"\n]+:[^"\n]+:[^"\n]+)"', text))
    if published != EXPECTED:
        missing = sorted(EXPECTED - published)
        unexpected = sorted(published - EXPECTED)
        print(f"FAIL: missing={missing} unexpected={unexpected}", file=sys.stderr)
        return 1
    if any(not binding.startswith("127.0.0.1:") for binding in published):
        print("FAIL: non-loopback host publication detected", file=sys.stderr)
        return 1
    print(f"OK: {len(published)} oracle publications are loopback-only")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
