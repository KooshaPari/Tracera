#!/usr/bin/env python3
"""Fail-closed verification of an isolated oracle source tuple in Git."""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

REQUIRED = (
    "docker-compose.yml",
    "Dockerfile",
    "backend/Dockerfile",
    "pyproject.toml",
    "deploy/nginx/nginx.conf",
)


def exists(repo: Path, ref: str, path: str) -> bool:
    result = subprocess.run(
        ["git", "-C", str(repo), "cat-file", "-e", f"{ref}:{path}"],
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return result.returncode == 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("ref", help="Git ref containing the candidate runtime")
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    args = parser.parse_args()
    result = subprocess.run(
        ["git", "-C", str(args.repo), "rev-parse", "--verify", args.ref],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode:
        print(json.dumps({"ref": args.ref, "error": "unknown_git_ref"}, indent=2))
        return 2
    checks = {path: exists(args.repo, args.ref, path) for path in REQUIRED}
    report = {
        "ref": args.ref,
        "commit": result.stdout.strip(),
        "required": checks,
        "complete": all(checks.values()),
    }
    print(json.dumps(report, indent=2))
    return 0 if report["complete"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
