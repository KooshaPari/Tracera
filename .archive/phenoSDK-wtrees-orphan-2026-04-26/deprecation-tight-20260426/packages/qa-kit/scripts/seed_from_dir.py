#!/usr/bin/env python3
"""Seed the QA DB from a directory of SQLite DB artifacts by merging them into the
destination DB.

Usage:
  python scripts/qa_seed_from_dir.py --seed-dir /mnt/qa_artifacts --dest-db /data/qa/qa.db
  # If --dest-db omitted, uses $QA_DB_PATH or qa_data/qa.db
"""

from __future__ import annotations

import argparse
from pathlib import Path

from scripts.qa_merge_db import ensure_out_db, merge_one
from src.shared.logging import get_logger

logger = get_logger(__name__)


def main() -> int:
    ap = argparse.ArgumentParser(description="Seed QA DB by merging DBs from a directory")
    ap.add_argument("--seed-dir", required=True, help="Directory containing *.db files to merge")
    ap.add_argument("--dest-db", help="Destination DB path (default $QA_DB_PATH or qa_data/qa.db)")
    args = ap.parse_args()

    dest = Path(args.dest_db or (Path.cwd() / "dashboard" / "qa_data" / "qa.db"))
    dest.parent.mkdir(parents=True, exist_ok=True)
    conn = ensure_out_db(dest)

    total = 0
    for db in Path(args.seed_dir).glob("*.db"):
        total += merge_one(conn, db)
    conn.close()
    logger.info(f"Merged {total} runs into {dest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
