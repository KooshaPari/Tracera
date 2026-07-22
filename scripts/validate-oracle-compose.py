#!/usr/bin/env python3
"""Validate a disposable rich-dashboard oracle checkout before Compose launch.

This is intentionally dependency-free and read-only.  It does not invoke Docker
or parse/modify a Compose file; it gates the two hazards found during recovery:
missing nginx assets and accidental publication on Grapheon's port 8080.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

RESERVED_HOST_PORT = 8080
PORT_RE = re.compile(r"(?:^|[\"'\s-])(?:127\.0\.0\.1:)?(\d{2,5}):\d{1,5}(?:[\"'\s]|$)")
CONTAINER_NAME_RE = re.compile(r"^\s*container_name:\s*([^#\s]+)", re.MULTILINE)


def validate_checkout(root: Path, compose: Path) -> tuple[list[str], list[str]]:
    """Return (errors, observations) for *root* and its Compose text."""
    errors: list[str] = []
    observations: list[str] = []

    nginx_conf = root / "nginx" / "nginx.conf"
    nginx_conf_d = root / "nginx" / "conf.d"
    if not nginx_conf.is_file():
        errors.append(f"missing required nginx config: {nginx_conf}")
    if not nginx_conf_d.is_dir():
        errors.append(f"missing required nginx include directory: {nginx_conf_d}")

    if not compose.is_file():
        errors.append(f"Compose file not found: {compose}")
        return errors, observations

    text = compose.read_text(encoding="utf-8")
    host_ports = [int(match.group(1)) for match in PORT_RE.finditer(text)]
    if RESERVED_HOST_PORT in host_ports:
        errors.append("host port 8080 is reserved for Grapheon and must not be published")
    observations.append(
        "host ports: " + (", ".join(map(str, host_ports)) if host_ports else "none published")
    )

    names = CONTAINER_NAME_RE.findall(text)
    if names:
        observations.append("fixed container_name values: " + ", ".join(names))
        observations.append("fixed container names require an isolated project/container prefix")
    else:
        observations.append("fixed container_name values: none")
    return errors, observations


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("checkout", type=Path, help="oracle checkout to inspect")
    parser.add_argument(
        "--compose",
        type=Path,
        default=None,
        help="Compose file relative to checkout (default: docker-compose.yml)",
    )
    args = parser.parse_args()
    root = args.checkout.resolve()
    compose = (args.compose or (root / "docker-compose.yml")).resolve()
    errors, observations = validate_checkout(root, compose)
    for observation in observations:
        print(f"INFO: {observation}")
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 2
    print("OK: oracle checkout passes Compose safety gate")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
