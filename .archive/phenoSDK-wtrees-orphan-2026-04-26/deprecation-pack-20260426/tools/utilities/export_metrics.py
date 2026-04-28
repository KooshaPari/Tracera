#!/usr/bin/env python3
"""
Export aggregated runtime metrics data.
"""

from __future__ import annotations

import argparse
import json
import sqlite3
from pathlib import Path
from typing import Any

ROOT_DIR = Path(__file__).resolve().parents[1]
DEFAULT_DB = ROOT_DIR / "data" / "metrics" / "krouter_metrics.db"
DEFAULT_DB.parent.mkdir(parents=True, exist_ok=True)


def fetch_model_summary(conn: sqlite3.Connection) -> dict[str, dict[str, Any]]:
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        """
        SELECT
            model_used AS model,
            COUNT(*) AS request_count,
            AVG(latency_ms) AS avg_latency_ms,
            AVG(total_cost_usd) AS avg_cost_usd,
            AVG(quality_score) AS avg_quality,
            SUM(CASE WHEN was_successful = 1 THEN 1 ELSE 0 END) AS success_count
        FROM metrics_records
        WHERE model_used IS NOT NULL
        GROUP BY model_used
        ORDER BY request_count DESC
        """,
    ).fetchall()

    summary: dict[str, dict[str, Any]] = {}
    for row in rows:
        total_requests = row["request_count"] or 0
        success_rate = (
            (row["success_count"] / total_requests) if total_requests else 0.0
        )
        summary[row["model"]] = {
            "request_count": int(total_requests),
            "avg_latency_ms": row["avg_latency_ms"],
            "avg_cost_usd": row["avg_cost_usd"],
            "avg_quality": row["avg_quality"],
            "success_rate": success_rate,
        }
    return summary


def fetch_recent_records(conn: sqlite3.Connection, limit: int) -> list[dict[str, Any]]:
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        """
        SELECT request_id, timestamp, model_used, latency_ms, total_cost_usd, quality_score
        FROM metrics_records
        ORDER BY timestamp DESC
        LIMIT ?
        """,
        (limit,),
    ).fetchall()
    return [dict(row) for row in rows]


def export_metrics(database: Path, limit: int) -> dict[str, Any]:
    if not database.exists():
        raise FileNotFoundError(f"Metrics database not found at {database}")

    with sqlite3.connect(database) as conn:
        summary = fetch_model_summary(conn)
        recent = fetch_recent_records(conn, limit)

    return {
        "database": str(database),
        "summary": summary,
        "recent_records": recent,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Export runtime metrics aggregates.")
    parser.add_argument(
        "--db",
        type=Path,
        default=DEFAULT_DB,
        help="Path to metrics SQLite database",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=25,
        help="Number of recent records to include",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Optional path to write JSON output",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    data = export_metrics(args.db, args.limit)
    json_payload = json.dumps(data, indent=2, sort_keys=True)

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json_payload, encoding="utf-8")
        print(f"Wrote metrics export to {args.output}")
    else:
        print(json_payload)
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    raise SystemExit(main())
