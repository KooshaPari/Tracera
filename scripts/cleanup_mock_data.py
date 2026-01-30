#!/usr/bin/env python3
import os
import re
import sqlite3
from typing import Iterable

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))

SKIP_DIRS = {
    '.git', '.venv', '.venv_test', 'node_modules', '.mypy_cache', '.ruff_cache',
    '.pytest_cache', '.uv-cache', '.playwright-mcp', '.sessions', '.trace',
    '__pycache__', '.hypothesis'
}

BAD_PROJECT_NAMES = {
    'Mobile Banking App',
    'E-Commerce Platform',
    'Healthcare Management System',
    'Real-Time Analytics Dashboard',
    'DevOps Automation Platform',
    'New Project',
    '<script>alert(\'XSS\')</script>',
}

BAD_TITLE_PREFIX_RE = re.compile(
    r'^(req|requirement|test|story|feature|task|epic|bug|issue|node|item|ticket|case)[\-_ ]*[0-9]+',
    re.IGNORECASE,
)

BAD_PHRASE_RE = re.compile(
    r'(test requirement|sample requirement|dummy requirement|placeholder|lorem ipsum|tbd|todo)',
    re.IGNORECASE,
)

SCRIPT_TAG_RE = re.compile(r'<script', re.IGNORECASE)


def iter_db_files(root: str) -> Iterable[str]:
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for filename in filenames:
            if filename.endswith('.db'):
                yield os.path.join(dirpath, filename)


def has_table(conn: sqlite3.Connection, table: str) -> bool:
    cur = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,))
    return cur.fetchone() is not None


def clean_sqlite_db(db_path: str) -> dict:
    result = {
        'db': db_path,
        'projects_deleted': 0,
        'items_deleted': 0,
        'skipped': False,
        'reason': '',
    }

    try:
        conn = sqlite3.connect(db_path)
    except sqlite3.Error as exc:
        result['skipped'] = True
        result['reason'] = f'connect_error:{exc}'
        return result

    try:
        if not has_table(conn, 'projects') or not has_table(conn, 'items'):
            result['skipped'] = True
            result['reason'] = 'missing_tables'
            return result

        # Delete generic items
        cur = conn.execute("SELECT id, title, COALESCE(description, '') FROM items")
        item_ids = []
        for item_id, title, description in cur.fetchall():
            title_l = title or ''
            desc_l = description or ''
            if SCRIPT_TAG_RE.search(title_l) or SCRIPT_TAG_RE.search(desc_l):
                item_ids.append(item_id)
                continue
            if BAD_TITLE_PREFIX_RE.search(title_l):
                item_ids.append(item_id)
                continue
            if BAD_PHRASE_RE.search(title_l) or BAD_PHRASE_RE.search(desc_l):
                item_ids.append(item_id)
                continue
        if item_ids:
            conn.executemany("DELETE FROM items WHERE id = ?", [(i,) for i in item_ids])
            result['items_deleted'] = len(item_ids)

        # Delete generic projects
        cur = conn.execute("SELECT id, name FROM projects")
        project_ids = []
        for project_id, name in cur.fetchall():
            if name in BAD_PROJECT_NAMES or SCRIPT_TAG_RE.search(name or ''):
                project_ids.append(project_id)
        if project_ids:
            conn.executemany("DELETE FROM projects WHERE id = ?", [(p,) for p in project_ids])
            result['projects_deleted'] = len(project_ids)

        conn.commit()
        try:
            conn.execute('VACUUM')
        except sqlite3.Error:
            pass
    finally:
        conn.close()

    return result


def main() -> None:
    db_files = sorted(set(iter_db_files(REPO_ROOT)))
    results = []
    for db_path in db_files:
        results.append(clean_sqlite_db(db_path))

    # Output summary for operator
    for result in results:
        if result['skipped']:
            print(f"SKIP {result['db']} ({result['reason']})")
        else:
            print(
                f"CLEAN {result['db']} items_deleted={result['items_deleted']} "
                f"projects_deleted={result['projects_deleted']}"
            )


if __name__ == '__main__':
    main()
