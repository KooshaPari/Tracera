#!/usr/bin/env python3
"""Merge multiple QA SQLite databases into a single output DB.

Usage:
  python scripts/qa_merge_db.py --output merged.db --inputs path/to/db1.db path/to/db2.db

Notes:
  - Assumes all input DBs share the schema created by scripts/qa_ingest.py
  - Upserts projects by name, remaps run/test_case foreign keys accordingly
  - Safe to run repeatedly; will append runs and test cases
"""

from __future__ import annotations

import argparse
import sqlite3
from collections.abc import Iterable
from pathlib import Path

from src.shared.logging import get_logger

logger = get_logger(__name__)


SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    framework TEXT NOT NULL,
    commit_sha TEXT,
    branch TEXT,
    ci_provider TEXT,
    triggered_by TEXT,
    created_at TEXT NOT NULL,
    started_at TEXT,
    duration_ms INTEGER,
    total INTEGER,
    passed INTEGER,
    failed INTEGER,
    skipped INTEGER,
    errors INTEGER,
    coverage_lines REAL,
    coverage_branches REAL,
    meta_json TEXT,
    FOREIGN KEY(project_id) REFERENCES projects(id)
);

CREATE TABLE IF NOT EXISTS test_cases (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id INTEGER NOT NULL,
    file TEXT,
    suite TEXT,
    name TEXT,
    status TEXT,
    duration_ms INTEGER,
    error_message TEXT,
    retry_count INTEGER,
    extra_json TEXT,
    FOREIGN KEY(run_id) REFERENCES runs(id)
);

CREATE INDEX IF NOT EXISTS idx_runs_project_created ON runs(project_id, created_at);
CREATE INDEX IF NOT EXISTS idx_cases_run_status ON test_cases(run_id, status);
"""


def ensure_out_db(path: Path) -> sqlite3.Connection:
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path))
    conn.executescript(SCHEMA_SQL)
    conn.row_factory = sqlite3.Row
    return conn


def merge_one(conn: sqlite3.Connection, src_path: Path) -> int:
    """Merge a single source DB into destination.

    Returns number of runs merged.
    """
    cur = conn.cursor()
    cur.execute("ATTACH DATABASE ? AS s", (str(src_path),))
    runs_merged = 0
    try:
        conn.execute("BEGIN")

        # Upsert projects by name
        cur.execute("INSERT OR IGNORE INTO projects(name) SELECT name FROM s.projects")

        # Build project ID mapping src->dest
        mapping: dict[int, int] = {}
        for row in cur.execute(
            "SELECT sp.id AS src_id, dp.id AS dest_id FROM s.projects sp JOIN projects dp ON dp.name = sp.name",
        ):
            mapping[int(row["src_id"])] = int(row["dest_id"])

        # Copy runs with remapped project_id, track run_id mapping
        run_id_map: dict[int, int] = {}
        run_rows = list(
            cur.execute(
                """
                SELECT id, project_id, framework, commit_sha, branch, ci_provider, triggered_by,
                       created_at, started_at, duration_ms, total, passed, failed, skipped, errors,
                       coverage_lines, coverage_branches, meta_json
                FROM s.runs
                ORDER BY datetime(created_at)
                """,
            ),
        )
        for r in run_rows:
            dest_project_id = mapping[int(r["project_id"])]
            cur.execute(
                """
                INSERT INTO runs(project_id, framework, commit_sha, branch, ci_provider, triggered_by,
                                 created_at, started_at, duration_ms, total, passed, failed, skipped, errors,
                                 coverage_lines, coverage_branches, meta_json)
                VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                """,
                (
                    dest_project_id,
                    r["framework"],
                    r["commit_sha"],
                    r["branch"],
                    r["ci_provider"],
                    r["triggered_by"],
                    r["created_at"],
                    r["started_at"],
                    r["duration_ms"],
                    r["total"],
                    r["passed"],
                    r["failed"],
                    r["skipped"],
                    r["errors"],
                    r["coverage_lines"],
                    r["coverage_branches"],
                    r["meta_json"],
                ),
            )
            new_id = int(cur.lastrowid)
            run_id_map[int(r["id"])] = new_id
            runs_merged += 1

        # Copy test_cases with remapped run_id
        case_rows = list(
            cur.execute(
                "SELECT run_id, file, suite, name, status, duration_ms, error_message, retry_count, extra_json FROM s.test_cases",
            ),
        )
        batch: Iterable[tuple] = []
        batch = [
            (
                run_id_map.get(int(c["run_id"])),
                c["file"],
                c["suite"],
                c["name"],
                c["status"],
                c["duration_ms"],
                c["error_message"],
                c["retry_count"],
                c["extra_json"],
            )
            for c in case_rows
            if int(c["run_id"]) in run_id_map
        ]
        cur.executemany(
            """
            INSERT INTO test_cases(run_id, file, suite, name, status, duration_ms, error_message, retry_count, extra_json)
            VALUES(?,?,?,?,?,?,?,?,?)
            """,
            batch,
        )

        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.execute("DETACH DATABASE s")
    return runs_merged


def main() -> int:
    ap = argparse.ArgumentParser(description="Merge QA SQLite DBs")
    ap.add_argument("--output", required=True, help="Output DB path")
    ap.add_argument("--inputs", nargs="+", required=True, help="Input DB paths to merge")
    args = ap.parse_args()

    out = Path(args.output)
    conn = ensure_out_db(out)
    total_runs = 0
    for inp in args.inputs:
        src = Path(inp)
        if not src.exists():
            logger.info(f"WARN: skipping missing DB: {src}")
            continue
        merged = merge_one(conn, src)
        logger.info(f"Merged {merged} runs from {src}")
        total_runs += merged
    conn.close()
    logger.info(f"Done. Wrote {out} with {total_runs} runs merged.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
