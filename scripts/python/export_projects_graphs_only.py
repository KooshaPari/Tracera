#!/usr/bin/env python3
"""export_projects_graphs_only module."""

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


def fetch_all(conn: Any, query: Any, params: Any = None) -> None:
    """Fetch all."""
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(query, params or {})
        return cur.fetchall()


def default_json(value: Any) -> None:
    """Default json."""
    if isinstance(value, datetime):
        return value.isoformat()
    return str(value)


def export_project(conn: Any, project_id: Any, out_dir: Any) -> None:
    """Export project."""
    project = fetch_all(
        conn,
        "select id, name, description, project_metadata from projects where id = %(pid)s",
        {"pid": project_id},
    )
    if not project:
        return
    project = project[0]

    graphs = fetch_all(
        conn,
        """
        select id, name, graph_type, root_item_id, graph_version, graph_rules, created_at, updated_at
        from graphs
        where project_id = %(pid)s
        order by created_at asc
    """,
        {"pid": project_id},
    )

    graph_nodes = fetch_all(
        conn,
        """
        select graph_id, item_id
        from graph_nodes
        where project_id = %(pid)s
    """,
        {"pid": project_id},
    )

    links = fetch_all(
        conn,
        """
        select id, graph_id, link_type, source_item_id, target_item_id, link_metadata, created_at, updated_at
        from links
        where project_id = %(pid)s
    """,
        {"pid": project_id},
    )

    link_types = fetch_all(conn, "select * from link_types where project_id = %(pid)s", {"pid": project_id})

    item_ids = list({row["item_id"] for row in graph_nodes})
    items = []
    if item_ids:
        items = fetch_all(
            conn,
            """
            select id, title, description, status, priority, owner, parent_id, item_metadata, node_kind_id
            from items
            where id = any(%(ids)s)
        """,
            {"ids": item_ids},
        )

    node_kind_ids = list({row["node_kind_id"] for row in items if row["node_kind_id"]})
    node_kinds = []
    if node_kind_ids:
        node_kinds = fetch_all(
            conn,
            "select id, name, description, kind_metadata, project_id from node_kinds where id = any(%(ids)s)",
            {"ids": node_kind_ids},
        )

    items_by_id = {item["id"]: item for item in items}
    kinds_by_id = {kind["id"]: kind for kind in node_kinds}

    # Denormalized edge list per graph for LLM-friendly consumption
    edges_by_graph = {g["id"]: [] for g in graphs}
    for link in links:
        src = items_by_id.get(link["source_item_id"])
        dst = items_by_id.get(link["target_item_id"])
        edge = {
            "id": link["id"],
            "graph_id": link["graph_id"],
            "type": link["link_type"],
            "source_item_id": link["source_item_id"],
            "target_item_id": link["target_item_id"],
            "source_title": src["title"] if src else None,
            "target_title": dst["title"] if dst else None,
            "source_kind": kinds_by_id.get(src["node_kind_id"], {}).get("name") if src else None,
            "target_kind": kinds_by_id.get(dst["node_kind_id"], {}).get("name") if dst else None,
            "metadata": link.get("link_metadata", {}),
        }
        edges_by_graph.setdefault(link["graph_id"], []).append(edge)

    data = {
        "schema_version": "2026-01",
        "project": project,
        "graphs": graphs,
        "graph_nodes": graph_nodes,
        "links": links,
        "link_types": link_types,
        "items": items,
        "node_kinds": node_kinds,
        "graph_edges": edges_by_graph,
    }

    file_path = out_dir / f"{project_id}.graphs.json"
    with file_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2, sort_keys=True, default=default_json)


def main() -> None:
    """Main."""
    Path(EXPORT_ROOT).mkdir(exist_ok=True, parents=True)
    timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
    out_dir = Path(EXPORT_ROOT) / f"graphs_only_snapshot_{timestamp}"
    out_dir.mkdir(exist_ok=True, parents=True)

    conn = psycopg2.connect(POSTGRES_URL)
    try:
        projects = fetch_all(conn, "select id, name from projects order by created_at asc")
        index = {
            "exported_at_utc": timestamp,
            "project_count": len(projects),
            "projects": projects,
            "format": "graphs_only",
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
