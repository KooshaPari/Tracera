#!/usr/bin/env python3
"""Ingest Lighthouse CI (LHCI) JSON reports into the QA SQLite DB.

Default discovery: .lighthouseci/*.json
Usage:
  python scripts/qa_ingest_lhci.py --project Dashboard --db qa_data/qa.db \
    --input .lighthouseci/*.json
"""

import argparse
import json
import sqlite3
from pathlib import Path

from src.shared.logging import get_logger

logger = get_logger(__name__)


def ensure_lh_schema(conn: sqlite3.Connection) -> None:
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS lh_runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            url TEXT,
            created_at TEXT,
            perf REAL,
            a11y REAL,
            bp REAL,
            seo REAL,
            pwa REAL,
            raw_json TEXT,
            FOREIGN KEY(project_id) REFERENCES projects(id)
        );
        """,
    )
    cur.execute(
        "CREATE INDEX IF NOT EXISTS idx_lh_project_created ON lh_runs(project_id, created_at);",
    )
    conn.commit()


def upsert_project(conn: sqlite3.Connection, name: str) -> int:
    cur = conn.cursor()
    cur.execute("INSERT OR IGNORE INTO projects(name) VALUES(?)", (name,))
    row = cur.execute("SELECT id FROM projects WHERE name=?", (name,)).fetchone()
    return int(row[0])


def parse_lhci_report(path: Path):
    data = json.loads(path.read_text())
    cats = data.get("categories", {})

    def score(key):
        v = cats.get(key, {}).get("score")
        return float(v) * 100 if isinstance(v, int | float) else None

    data.get("fetchTime") or data.get("requestedUrl")
    return {
        "url": data.get("finalUrl") or data.get("requestedUrl"),
        "created_at": data.get("fetchTime"),
        "perf": score("performance"),
        "a11y": score("accessibility"),
        "bp": score("best-practices"),
        "seo": score("seo"),
        "pwa": score("pwa"),
        "raw": json.dumps(data)[:200000],
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Ingest LHCI JSON into QA DB")
    ap.add_argument("--project", required=True)
    ap.add_argument("--db", required=True)
    ap.add_argument("--input", nargs="+", required=True)
    args = ap.parse_args()

    conn = sqlite3.connect(args.db)
    conn.row_factory = sqlite3.Row
    ensure_lh_schema(conn)
    proj = upsert_project(conn, args.project)
    cur = conn.cursor()
    inserted = 0
    for p in args.input:
        path = Path(p)
        if not path.exists():
            continue
        try:
            rep = parse_lhci_report(path)
            cur.execute(
                """
                INSERT INTO lh_runs(project_id, url, created_at, perf, a11y, bp, seo, pwa, raw_json)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    proj,
                    rep["url"],
                    rep["created_at"],
                    rep["perf"],
                    rep["a11y"],
                    rep["bp"],
                    rep["seo"],
                    rep["pwa"],
                    rep["raw"],
                ),
            )
            inserted += 1
        except Exception:
            continue
    conn.commit()
    logger.info(f"Inserted {inserted} LHCI runs into {args.db}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
