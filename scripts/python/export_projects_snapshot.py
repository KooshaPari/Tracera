#!/usr/bin/env python3
"""export_projects_snapshot module."""

import json
import os
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import psycopg2
from psycopg2.extras import RealDictCursor

POSTGRES_URL = os.environ.get(
    "TRACERTM_DATABASE_URL",
    "postgresql://kooshapari@localhost:5432/agent_api",
)

EXPORT_ROOT = (Path(__file__).parent / ".." / "exports").resolve()

TABLES = [
    "projects",
    "views",
    "node_kinds",
    "items",
    "item_views",
    "graphs",
    "graph_nodes",
    "links",
    "link_types",
    "graph_types",
    "edge_types",
    "node_kind_rules",
    "external_links",
]


def fetch_all(conn: Any, query: Any, params: Any = None) -> None:
    """Fetch all."""
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(query, params or {})
        return cur.fetchall()


def export_project(conn: Any, project_id: Any, out_dir: Any) -> None:
    """Export project."""
    data = {}
    for table in TABLES:
        if table == "projects":
            rows = fetch_all(conn, f"select * from {table} where id = %(pid)s", {"pid": project_id})
        elif (
            table in {"views", "node_kinds"}
            or table in {"items", "graphs"}
            or table in {"item_views", "graph_nodes", "links", "external_links"}
        ):
            rows = fetch_all(conn, f"select * from {table} where project_id = %(pid)s", {"pid": project_id})
        elif table in {"graph_types", "edge_types", "link_types", "node_kind_rules"}:
            rows = fetch_all(conn, f"select * from {table}")
        else:
            rows = fetch_all(conn, f"select * from {table}")
        data[table] = rows

    file_path = out_dir / f"{project_id}.json"
    with file_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2, sort_keys=True, default=default_json)


def default_json(value: Any) -> None:
    """Default json."""
    if isinstance(value, datetime):
        return value.isoformat()
    return str(value)


def main() -> None:
    """Main."""
    Path(EXPORT_ROOT).mkdir(exist_ok=True, parents=True)
    timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
    out_dir = Path(EXPORT_ROOT) / f"post_cleanup_snapshot_{timestamp}"
    out_dir.mkdir(exist_ok=True, parents=True)

    conn = psycopg2.connect(POSTGRES_URL)
    try:
        projects = fetch_all(conn, "select id, name from projects order by created_at asc")
        index = {
            "exported_at_utc": timestamp,
            "project_count": len(projects),
            "projects": projects,
        }
        index_file = out_dir / "index.json"
        with index_file.open("w", encoding="utf-8") as f:
            json.dump(index, f, ensure_ascii=False, indent=2, sort_keys=True, default=default_json)

        for project in projects:
            export_project(conn, project["id"], out_dir)
    finally:
        conn.close()


if __name__ == "__main__":
    main()
