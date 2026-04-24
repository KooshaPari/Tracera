#!/usr/bin/env python3
"""Introspect a TraceRTM project: items, links, graphs counts and optional JSON dump.

Usage:
  DATABASE_URL=postgresql://... python scripts/introspect_project.py cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e
  DATABASE_URL=... python scripts/introspect_project.py cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e --output project_snapshot.json
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path


def main() -> int:
    """Main."""
    ap = argparse.ArgumentParser(
        description="Introspect TraceRTM project items, links, and graphs",
    )
    ap.add_argument(
        "project_id",
        help="Project UUID (e.g. cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e)",
    )
    ap.add_argument(
        "--output",
        "-o",
        type=Path,
        help="Write full snapshot to JSON file",
    )
    ap.add_argument(
        "--limit",
        type=int,
        default=0,
        help="Limit items/links in snapshot (0 = no limit)",
    )
    args = ap.parse_args()

    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        return 1

    try:
        import psycopg
    except ImportError:
        return 1

    project_id = args.project_id.strip()

    with psycopg.connect(database_url) as conn, conn.cursor() as cur:
        # Project
        cur.execute(
            "SELECT id, account_id, name, description, metadata FROM tracertm.projects WHERE id = %s::uuid",
            (project_id,),
        )
        row = cur.fetchone()
        if not row:
            return 1
        project = {
            "id": str(row[0]),
            "account_id": str(row[1]) if row[1] else None,
            "name": row[2],
            "description": row[3],
            "metadata": row[4],
        }

        # Counts
        cur.execute(
            "SELECT COUNT(*) FROM tracertm.items WHERE project_id = %s::uuid",
            (project_id,),
        )
        items_count = cur.fetchone()[0]
        try:
            cur.execute(
                "SELECT COUNT(*) FROM tracertm.links WHERE project_id = %s::uuid",
                (project_id,),
            )
            links_count = cur.fetchone()[0]
        except Exception:
            # Links table may not have project_id; count via join with items
            cur.execute(
                """
                SELECT COUNT(DISTINCT l.id) FROM tracertm.links l
                INNER JOIN tracertm.items i1 ON l.source_id = i1.id
                INNER JOIN tracertm.items i2 ON l.target_id = i2.id
                WHERE (i1.project_id = %s::uuid OR i2.project_id = %s::uuid)
                  AND i1.deleted_at IS NULL AND i2.deleted_at IS NULL
                """,
                (project_id, project_id),
            )
            links_count = cur.fetchone()[0]
        cur.execute(
            "SELECT COUNT(*) FROM tracertm.graphs WHERE project_id = %s::uuid",
            (project_id,),
        )
        graphs_count = cur.fetchone()[0]
        cur.execute(
            "SELECT COUNT(*) FROM tracertm.graph_nodes WHERE project_id = %s::uuid",
            (project_id,),
        )
        graph_nodes_count = cur.fetchone()[0]

    if args.output:
        limit = args.limit or None
        with psycopg.connect(database_url) as conn, conn.cursor() as cur:
            params = (project_id,) + ((limit,) if limit else ())
            cur.execute(
                """
                SELECT id, project_id, title, type, status, priority, parent_id, metadata
                FROM tracertm.items WHERE project_id = %s::uuid
                ORDER BY created_at
                """
                + (" LIMIT %s" if limit else ""),
                params,
            )
            cols = [d.name for d in cur.description]
            items = [
                {c: str(v) if hasattr(v, "hex") else v for c, v in zip(cols, r, strict=True)} for r in cur.fetchall()
            ]
            cur.execute(
                """
                SELECT id, project_id, graph_id, source_item_id, target_item_id, link_type, link_metadata
                FROM tracertm.links WHERE project_id = %s::uuid
                ORDER BY created_at
                """
                + (" LIMIT %s" if limit else ""),
                params,
            )
            cols = [d.name for d in cur.description]
            links = [
                {c: str(v) if hasattr(v, "hex") else v for c, v in zip(cols, r, strict=True)} for r in cur.fetchall()
            ]
            cur.execute(
                "SELECT id, project_id, name, graph_type FROM tracertm.graphs WHERE project_id = %s::uuid",
                (project_id,),
            )
            cols = [d.name for d in cur.description]
            graphs = [
                {c: str(v) if hasattr(v, "hex") else v for c, v in zip(cols, r, strict=True)} for r in cur.fetchall()
            ]
        snapshot = {
            "project": project,
            "summary": {
                "items": items_count,
                "links": links_count,
                "graphs": graphs_count,
                "graph_nodes": graph_nodes_count,
            },
            "items": items,
            "links": links,
            "graphs": graphs,
        }
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("w") as f:
            json.dump(snapshot, f, indent=2)

    return 0


if __name__ == "__main__":
    sys.exit(main())
