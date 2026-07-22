#!/usr/bin/env python3
"""Compare rich frontend route templates with a materialized Python oracle.

This is intentionally conservative: parameter names are normalized only for
comparison, while the report retains the original templates. A normalized
match is evidence of a candidate contract overlap, not proof of runtime parity.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROUTE_RE = re.compile(r"[\"'](/api/v1[^\"']+)[\"']")
DECORATOR_RE = re.compile(
    r"@(?:\w+\.)?(?:get|post|put|patch|delete)\([\"']([^\"']+)"
)
PREFIX_RE = re.compile(r"router\s*=\s*APIRouter\(prefix=[\"']([^\"']+)")
ROUTER_NAMES = {
    "auth": "/auth",
    "comments": "/items/{item_id}/comments",
    "evidence": "/evidence",
    "impact": "/impact",
    "impact_scoring": "/impact",
    "ingest": "/ingest",
    "org_intel": "/org-intel",
    "sdlc_pm": "/sdlc-pm",
    "code_trace": "",
    "traceability": "",
}


def normalize(route: str) -> str:
    return re.sub(r"\{[^}]+\}", "{}", route).rstrip("/") or "/"


def frontend_routes(root: Path) -> set[str]:
    routes: set[str] = set()
    for file in (root / "frontend/apps/web/src/api").glob("*.ts"):
        routes.update(ROUTE_RE.findall(file.read_text(errors="replace")))
    return routes


def oracle_routes(root: Path) -> set[str]:
    routes: set[str] = set()
    router_root = root / "src/tracertm/api/routers"
    for file in router_root.glob("*.py"):
        prefix_match = PREFIX_RE.search(file.read_text(errors="replace"))
        prefix = prefix_match.group(1) if prefix_match else ROUTER_NAMES.get(file.stem)
        if prefix is None:
            continue
        for path in DECORATOR_RE.findall(file.read_text(errors="replace")):
            if path.startswith("/"):
                suffix = "" if path == "/" else path
                routes.add(f"/api/v1{prefix}{suffix}")
    return routes


def go_routes(file: Path) -> set[str]:
    """Extract Echo registrations from a gateway routes.go file."""
    routes: set[str] = set()
    pattern = re.compile(
        r'(?:api|protected|oauth|s\.echo)\.(?:GET|POST|PUT|PATCH|DELETE)\("([^\"]+)'
    )
    for path in pattern.findall(file.read_text(errors="replace")):
        if path.startswith("/api/"):
            routes.add(path)
        elif path.startswith("/") and file.name == "routes.go":
            routes.add("/api/v1" + path)
    return routes


def rust_routes(file: Path) -> set[str]:
    """Extract Axum route literals from the native Tracera server."""
    pattern = re.compile(r'\.route\("([^"]+)"')
    return set(pattern.findall(file.read_text(errors="replace")))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("frontend_checkout", type=Path)
    parser.add_argument("oracle_checkout", type=Path)
    parser.add_argument("--go-routes", type=Path)
    parser.add_argument("--rust-main", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    rich = frontend_routes(args.frontend_checkout)
    oracle = oracle_routes(args.oracle_checkout)
    gateway = go_routes(args.go_routes) if args.go_routes else set()
    native = rust_routes(args.rust_main) if args.rust_main else set()
    rich_normalized = {normalize(route): route for route in rich}
    oracle_normalized = {normalize(route): route for route in oracle}
    overlap = sorted(set(rich_normalized) & set(oracle_normalized))
    report = {
        "rich_routes": len(rich),
        "oracle_routes": len(oracle),
        "normalized_matches": len(overlap),
        "matches": [
            {"rich": rich_normalized[route], "oracle": oracle_normalized[route]}
            for route in overlap
        ],
        "frontend_only": sorted(set(rich_normalized) - set(oracle_normalized)),
        "oracle_only": sorted(set(oracle_normalized) - set(rich_normalized)),
        "gateway_routes": len(gateway),
        "gateway_normalized_matches": len(
            set(normalize(route) for route in rich) & {normalize(route) for route in gateway}
        ),
        "rust_routes": len(native),
        "rust_normalized_matches": len(
            {normalize(route) for route in rich} & {normalize(route) for route in native}
        ),
        "normalization": "all {param} segments collapse to {} for comparison only",
    }
    rendered = json.dumps(report, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
