#!/usr/bin/env python3
"""Ingest Axe accessibility JSON reports into QA SQLite DB.

Supports typical formats produced by axe-core/cli or playwright-axe output:
- Top-level { violations: [...], passes: [...], url?, timestamp? }
- Or an array of such result objects

Usage:
  python scripts/qa_ingest_axe.py --project Dashboard --db qa_data/qa.db --input reports/axe/*.json
"""

import argparse
import json
import sqlite3
from pathlib import Path

from src.shared.logging import get_logger

logger = get_logger(__name__)


def ensure_schema(conn: sqlite3.Connection) -> None:
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        );
        """,
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS axe_runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            created_at TEXT,
            url TEXT,
            critical INTEGER,
            serious INTEGER,
            moderate INTEGER,
            minor INTEGER,
            raw_json TEXT,
            FOREIGN KEY(project_id) REFERENCES projects(id)
        );
        """,
    )
    cur.execute(
        "CREATE INDEX IF NOT EXISTS idx_axe_project_created ON axe_runs(project_id, created_at);",
    )
    conn.commit()


def upsert_project(conn: sqlite3.Connection, name: str) -> int:
    cur = conn.cursor()
    cur.execute("INSERT OR IGNORE INTO projects(name) VALUES(?)", (name,))
    row = cur.execute("SELECT id FROM projects WHERE name=?", (name,)).fetchone()
    return int(row[0])


def count_severity(violations) -> dict:
    sev = {"critical": 0, "serious": 0, "moderate": 0, "minor": 0}
    for v in violations or []:
        impact = (v.get("impact") or "").lower()
        if impact in sev:
            sev[impact] += 1
    return sev


def parse_axe_json(path: Path) -> list[dict]:
    data = json.loads(path.read_text())
    results = []
    items = data if isinstance(data, list) else [data]
    for it in items:
        violations = it.get("violations") or []
        sev = count_severity(violations)
        results.append(
            {
                "created_at": it.get("timestamp") or it.get("generatedAt") or None,
                "url": it.get("url") or it.get("pageUrl") or None,
                **sev,
                "raw": json.dumps(it)[:200000],
            },
        )
    return results


def main() -> int:
    ap = argparse.ArgumentParser(description="Ingest Axe JSON into QA DB")
    ap.add_argument("--project", required=True)
    ap.add_argument("--db", required=True)
    ap.add_argument("--input", nargs="+", required=True)
    args = ap.parse_args()

    conn = sqlite3.connect(args.db)
    conn.row_factory = sqlite3.Row
    ensure_schema(conn)
    pid = upsert_project(conn, args.project)
    cur = conn.cursor()
    inserted = 0
    for p in args.input:
        path = Path(p)
        if not path.exists():
            continue
        try:
            for res in parse_axe_json(path):
                cur.execute(
                    """
                    INSERT INTO axe_runs(project_id, created_at, url, critical, serious, moderate, minor, raw_json)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        pid,
                        res.get("created_at"),
                        res.get("url"),
                        int(res.get("critical") or 0),
                        int(res.get("serious") or 0),
                        int(res.get("moderate") or 0),
                        int(res.get("minor") or 0),
                        res.get("raw"),
                    ),
                )
                inserted += 1
        except Exception:
            continue
    conn.commit()
    logger.info(f"Inserted {inserted} Axe results into {args.db}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
