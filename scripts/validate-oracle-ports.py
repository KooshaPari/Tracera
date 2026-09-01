#!/usr/bin/env python3
"""Validate isolated Python-oracle host ports without touching the runtime."""

from __future__ import annotations

import argparse
import sys

RESERVED = {8080: "Grapheon"}


def validate(ports: list[int]) -> list[str]:
    errors: list[str] = []
    if len(set(ports)) != len(ports):
        errors.append("selected ports must be unique")
    for port in ports:
        if not 1024 <= port <= 65535:
            errors.append(f"port {port} must be between 1024 and 65535")
        if port in RESERVED:
            errors.append(f"port {port} is reserved for {RESERVED[port]}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("ports", nargs="+", type=int, help="host ports to reserve")
    args = parser.parse_args()
    errors = validate(args.ports)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 2
    print("OK: isolated oracle ports are valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
