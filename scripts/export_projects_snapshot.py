#!/usr/bin/env python3
import json
import os
from datetime import datetime, timezone
import psycopg2
from psycopg2.extras import RealDictCursor

POSTGRES_URL = os.environ.get(
    'TRACERTM_DATABASE_URL',
    'postgresql://kooshapari@localhost:5432/agent_api',
)

EXPORT_ROOT = os.path.join(os.path.dirname(__file__), os.pardir, 'exports')

TABLES = [
    'projects',
    'views',
    'node_kinds',
    'items',
    'item_views',
    'graphs',
    'graph_nodes',
    'links',
    'link_types',
    'graph_types',
    'edge_types',
    'node_kind_rules',
    'external_links',
]


def fetch_all(conn, query, params=None):
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(query, params or {})
        return cur.fetchall()


def export_project(conn, project_id, out_dir):
    data = {}
    for table in TABLES:
        if table == 'projects':
            rows = fetch_all(conn, f"select * from {table} where id = %(pid)s", {'pid': project_id})
        elif table in {'views', 'node_kinds'}:
            rows = fetch_all(conn, f"select * from {table} where project_id = %(pid)s", {'pid': project_id})
        elif table in {'items', 'graphs'}:
            rows = fetch_all(conn, f"select * from {table} where project_id = %(pid)s", {'pid': project_id})
        elif table in {'item_views', 'graph_nodes', 'links', 'external_links'}:
            rows = fetch_all(conn, f"select * from {table} where project_id = %(pid)s", {'pid': project_id})
        elif table in {'graph_types', 'edge_types', 'link_types', 'node_kind_rules'}:
            rows = fetch_all(conn, f"select * from {table}")
        else:
            rows = fetch_all(conn, f"select * from {table}")
        data[table] = rows

    file_path = os.path.join(out_dir, f"{project_id}.json")
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2, sort_keys=True, default=default_json)


def default_json(value):
    if isinstance(value, datetime):
        return value.isoformat()
    return str(value)


def main():
    os.makedirs(EXPORT_ROOT, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')
    out_dir = os.path.join(EXPORT_ROOT, f"post_cleanup_snapshot_{timestamp}")
    os.makedirs(out_dir, exist_ok=True)

    conn = psycopg2.connect(POSTGRES_URL)
    try:
        projects = fetch_all(conn, "select id, name from projects order by created_at asc")
        index = {
            'exported_at_utc': timestamp,
            'project_count': len(projects),
            'projects': projects,
        }
        with open(os.path.join(out_dir, 'index.json'), 'w', encoding='utf-8') as f:
            json.dump(index, f, ensure_ascii=False, indent=2, sort_keys=True, default=default_json)

        for project in projects:
            export_project(conn, project['id'], out_dir)
    finally:
        conn.close()

    print(f"EXPORT_DIR {out_dir}")


if __name__ == '__main__':
    main()
