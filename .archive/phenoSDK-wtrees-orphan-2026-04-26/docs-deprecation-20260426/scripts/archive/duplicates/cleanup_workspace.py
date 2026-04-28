#!/usr/bin/env python3
"""
Workspace cleanup placeholder used by Makefile targets.
"""

from __future__ import annotations

import pathlib


def main() -> int:
    workspace = pathlib.Path.cwd()
    print(f"[cleanup] workspace={workspace}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
