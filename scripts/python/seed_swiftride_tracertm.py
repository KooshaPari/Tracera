#!/usr/bin/env python3
"""Seed SwiftRide mock data into TraceRTM schema.

Reads:
  - scripts/mock_data_rideshare.sql (project + items)
  - scripts/add_swiftride_links.sql (links)

Produces tracertm-ready SQL:
  - Projects: UUID id, account_id (set via ACCOUNT_ID env or --account-id), name, metadata
  - Items: UUID id, project_id (UUID), title, description, type (from item_type), status,
    priority (integer), parent_id (UUID from map), metadata (item_metadata + view + owner)
  - Links: UUID id, source_id/target_id (item UUIDs), link_type, metadata (no project_id)

Usage:
  ACCOUNT_ID=your-account-uuid python scripts/seed_swiftride_tracertm.py [--account-id UUID] [--output FILE]
  # Extend existing project (items/links only; no project INSERT):
  PROJECT_ID=cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e python scripts/seed_swiftride_tracertm.py -o scripts/seed_swiftride_tracertm.sql
  # Or pipe to psql: python scripts/seed_swiftride_tracertm.py | psql $DATABASE_URL
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import uuid
from contextlib import nullcontext
from pathlib import Path


def handle_string_char(c: str, i: int, line: str, in_string: bool, escape: bool) -> tuple[bool, bool, int]:
    """Handle a character while inside a string. Returns (in_string, escape, new_position)."""
    if escape:
        return in_string, False, i + 1

    if c == "'" and i + 1 < len(line) and line[i + 1] == "'":
        return in_string, True, i + 2

    if c == "'":
        return False, False, i + 1

    return in_string, False, i + 1


def find_matching_paren(line: str) -> int:
    """Find the matching closing parenthesis, handling strings correctly."""
    depth = 0
    i = 0
    in_string = False
    escape = False

    while i < len(line):
        c = line[i]

        if in_string:
            in_string, escape, i = handle_string_char(c, i, line, in_string, escape)
            continue

        if c == "'":
            in_string = True
            i += 1
            continue

        if c == "(":
            depth += 1
        elif c == ")":
            depth -= 1
            if depth == 0:
                return i

        i += 1

    return -1


def parse_quoted_string(inner: str, start: int) -> tuple[str, int]:
    """Parse a quoted string starting at position start. Returns (value, new_position)."""
    j = start + 1
    buf = []

    while j < len(inner):
        if inner[j] == "'":
            if j + 1 < len(inner) and inner[j + 1] == "'":
                buf.append("'")
                j += 2
                continue
            break
        buf.append(inner[j])
        j += 1

    return "".join(buf), j + 1


def parse_number(inner: str, start: int) -> tuple[int, int]:
    """Parse an integer starting at position start. Returns (value, new_position)."""
    j = start + 1 if inner[start] == "-" else start
    while j < len(inner) and inner[j].isdigit():
        j += 1
    return int(inner[start:j]), j


def skip_to_comma(inner: str, start: int) -> int:
    """Skip to next comma from start position."""
    j = start
    while j < len(inner) and inner[j] != ",":
        j += 1
    return j


def parse_value_at_position(inner: str, i: int) -> tuple[str | int | None, int] | None:
    """Parse a single value starting at position i. Returns (value, new_position) or None."""
    # Quoted string
    if inner[i] == "'":
        value, new_i = parse_quoted_string(inner, i)
        return value, new_i

    # NULL
    if inner[i : i + 4] == "NULL":
        return None, i + 4

    # Number (including negative)
    if inner[i].isdigit() or (inner[i] == "-" and i + 1 < len(inner) and inner[i + 1].isdigit()):
        value, new_i = parse_number(inner, i)
        return value, new_i

    # NOW() function
    if inner[i] == "N" and inner[i : i + 3] == "NOW":
        new_i = skip_to_comma(inner, i)
        return None, new_i  # placeholder for timestamp

    return None


def parse_sql_values_line(line: str) -> list[str | int | None]:
    """Parse a single VALUES row: ('a', 'b', NULL, 1, ...). Handles quoted strings with ''."""
    line = line.strip().rstrip(",").strip()

    if not line.startswith("("):
        return []

    end = find_matching_paren(line)
    if end == -1:
        return []

    inner = line[1:end].strip()
    parts: list[str | int | None] = []
    i = 0

    while i < len(inner):
        # Skip leading comma/space
        while i < len(inner) and inner[i] in " \t,":
            i += 1

        if i >= len(inner):
            break

        result = parse_value_at_position(inner, i)
        if result:
            value, i = result
            parts.append(value)
        else:
            i += 1

    return parts


def extract_project_from_mock(mock_path: Path) -> dict | None:
    """Extract single project from mock_data_rideshare.sql."""
    text = mock_path.read_text(encoding="utf-8")
    # INSERT INTO projects (id, name, project_metadata, created_at, updated_at) VALUES (...);
    m = re.search(
        r"INSERT INTO projects\s*\([^)]+\)\s*VALUES\s*\(([^;]+)\);",
        text,
        re.DOTALL | re.IGNORECASE,
    )
    if not m:
        return None
    row = parse_sql_values_line("(" + m.group(1).strip() + ")")
    if len(row) < 3:
        return None
    return {
        "id": str(row[0]) if row[0] is not None else None,
        "name": str(row[1]) if row[1] is not None else None,
        "project_metadata": str(row[2]) if row[2] is not None else "{}",
    }


def extract_items_from_mock(mock_path: Path) -> list[dict]:
    """Extract all item rows from mock_data_rideshare.sql."""
    text = mock_path.read_text(encoding="utf-8")
    items: list[dict] = []
    # Match each line that looks like ('id', 'proj_...', ...)
    for m in re.finditer(
        r"^\s*\('([^']+)',\s*'([^']+)',\s*",
        text,
        re.MULTILINE,
    ):
        line_start = text.rfind("\n", 0, m.start()) + 1
        line_end = text.find("\n", m.end())
        if line_end == -1:
            line_end = len(text)
        line = text[line_start:line_end]
        if "NOW()" not in line and ")," not in line and ");" not in line:
            continue
        row = parse_sql_values_line(line)
        # id, project_id, title, description, view, item_type, status, priority, owner, parent_id, item_metadata, version, ...
        if len(row) < 12:
            continue
        items.append({
            "id": str(row[0]) if row[0] is not None else None,
            "project_id": str(row[1]) if row[1] is not None else None,
            "title": str(row[2]) if row[2] is not None else None,
            "description": str(row[3]) if row[3] is not None else None,
            "view": str(row[4]) if row[4] is not None else None,
            "item_type": str(row[5]) if row[5] is not None else None,
            "status": str(row[6]) if row[6] is not None else "todo",
            "priority": row[7],
            "owner": str(row[8]) if row[8] is not None else None,
            "parent_id": str(row[9]) if row[9] is not None else None,
            "item_metadata": str(row[10]) if row[10] is not None else "{}",
            "version": int(row[11]) if isinstance(row[11], int) else 1,
        })
    return items


def extract_links_from_add_links(links_path: Path) -> list[dict]:
    """Extract link rows from add_swiftride_links.sql. Columns: id, project_id, source_item_id, target_item_id, link_type, link_metadata, created_at, updated_at."""
    text = links_path.read_text(encoding="utf-8")
    links: list[dict] = []
    for line in text.splitlines():
        line = line.strip()
        if not re.match(r"^\s*\('link_", line):
            continue
        row = parse_sql_values_line(line)
        if len(row) < 6:
            continue
        links.append({
            "id": str(row[0]) if row[0] is not None else None,
            "project_id": str(row[1]) if row[1] is not None else None,
            "source_item_id": str(row[2]) if row[2] is not None else None,
            "target_item_id": str(row[3]) if row[3] is not None else None,
            "link_type": str(row[4]) if row[4] is not None else None,
            "link_metadata": str(row[5]) if row[5] is not None else "{}",
        })
    return links


def priority_to_int(p: str | int) -> int:
    """Priority to int."""
    if isinstance(p, int):
        return max(0, min(3, p))
    return {"low": 0, "medium": 1, "high": 2}.get(str(p).lower(), 1)


def sql_quote(s: str | None) -> str:
    """Sql quote."""
    if s is None:
        return "NULL"
    return "'" + str(s).replace("'", "''") + "'"


def main() -> int:
    """Main."""
    script_dir = Path(__file__).resolve().parent
    mock_path = script_dir / "mock_data_rideshare.sql"
    links_path = script_dir / "add_swiftride_links.sql"

    ap = argparse.ArgumentParser(description="Emit TraceRTM-ready SQL for SwiftRide mock data")
    ap.add_argument(
        "--account-id",
        default=os.environ.get("ACCOUNT_ID"),
        help="Account UUID for projects (or set ACCOUNT_ID)",
    )
    ap.add_argument(
        "--project-id",
        default=os.environ.get("PROJECT_ID"),
        help="Existing project UUID to extend (items/links only; no project INSERT). Set PROJECT_ID=uuid or --project-id",
    )
    ap.add_argument("--output", "-o", type=Path, help="Write SQL to file (default: stdout)")
    args = ap.parse_args()

    account_id = args.account_id
    extend_existing = bool(args.project_id)
    if extend_existing:
        project_uuid = args.project_id.strip()
        try:
            uuid.UUID(project_uuid)
        except ValueError:
            return 1
    else:
        project_uuid = str(uuid.uuid4())

    if not extend_existing and not account_id:
        account_id = "00000000-0000-0000-0000-000000000001"  # placeholder; user should set ACCOUNT_ID

    if not mock_path.exists():
        return 1
    if not links_path.exists():
        return 1

    project = extract_project_from_mock(mock_path)
    if not project:
        return 1

    items = extract_items_from_mock(mock_path)
    links_raw = extract_links_from_add_links(links_path)

    # Build UUIDs and mapping (project_uuid already set above when --project-id used)
    logical_to_uuid: dict[str, str] = {project["id"]: project_uuid}
    for it in items:
        logical_to_uuid[it["id"]] = str(uuid.uuid4())

    with Path(args.output).open("w", encoding="utf-8") if args.output is not None else nullcontext(sys.stdout) as out:
        # Project metadata: keep description from project_metadata JSON if present
        try:
            meta = json.loads(project["project_metadata"])
        except Exception:
            meta = {}
        if "description" not in meta and project.get("project_metadata"):
            try:
                meta = json.loads(project["project_metadata"])
            except Exception:
                meta = {}
        meta_str = json.dumps(meta).replace("'", "''")

        # Validate UUID to avoid SQL injection when writing to script (S608)
        try:
            safe_project_uuid = str(uuid.UUID(project_uuid))
        except (ValueError, TypeError) as err:
            msg = f"Invalid project UUID: {project_uuid!r}"
            raise ValueError(msg) from err

        # TraceRTM projects (tracertm schema): id, account_id, name, description, metadata, created_at, updated_at.
        desc_from_meta = meta.get("description", "") if isinstance(meta, dict) else ""
        out.write("-- SwiftRide seeded for TraceRTM (projects, items, graphs, links)\n")
        out.write("-- Generated by scripts/seed_swiftride_tracertm.py\n")
        if extend_existing:
            out.write("-- Target project (extend only): " + safe_project_uuid + "\n")
        out.write("SET search_path TO tracertm;\n\n")
        out.write("-- Delete in order: links reference items and graph; items reference project\n")
        out.write("DELETE FROM links WHERE project_id = '" + safe_project_uuid + "'::uuid;\n")
        out.write("DELETE FROM graph_nodes WHERE project_id = '" + safe_project_uuid + "'::uuid;\n")
        out.write("DELETE FROM items WHERE project_id = '" + safe_project_uuid + "'::uuid;\n")
        out.write("DELETE FROM graphs WHERE project_id = '" + safe_project_uuid + "'::uuid;\n")
        if not extend_existing:
            out.write("DELETE FROM projects WHERE id = '" + safe_project_uuid + "'::uuid;\n\n")
            if account_id:
                out.write(
                    "INSERT INTO projects (id, account_id, name, description, metadata, created_at, updated_at)\n",
                )
                out.write(
                    "VALUES ("
                    + sql_quote(safe_project_uuid)
                    + "::uuid, "
                    + sql_quote(account_id)
                    + ", "
                    + sql_quote(project["name"])
                    + ", "
                    + (sql_quote(desc_from_meta) if desc_from_meta else "NULL")
                    + ", '"
                    + meta_str
                    + "'::jsonb, NOW(), NOW());\n\n",
                )
            else:
                out.write("INSERT INTO projects (id, name, description, metadata, created_at, updated_at)\n")
                out.write(
                    "VALUES ("
                    + sql_quote(safe_project_uuid)
                    + "::uuid, "
                    + sql_quote(project["name"])
                    + ", "
                    + (sql_quote(desc_from_meta) if desc_from_meta else "NULL")
                    + ", '"
                    + meta_str
                    + "'::jsonb, NOW(), NOW());\n\n",
                )
        else:
            out.write("\n")

        # Items: id, project_id, title, description, type, status, priority, parent_id, metadata, created_at, updated_at
        # Merge item_metadata + view + owner into metadata
        out.write(
            "INSERT INTO items (id, project_id, title, description, type, status, priority, parent_id, metadata, created_at, updated_at)\nVALUES\n",
        )
        for i, it in enumerate(items):
            u = logical_to_uuid[it["id"]]
            parent_uuid = "NULL"
            if it.get("parent_id"):
                parent_uuid = sql_quote(logical_to_uuid.get(it["parent_id"], it["parent_id"]))
            try:
                item_meta = json.loads(it["item_metadata"])
            except Exception:
                item_meta = {}
            if it.get("view"):
                item_meta["view"] = it["view"]
            if it.get("owner"):
                item_meta["owner"] = it["owner"]
            if it.get("version") is not None:
                item_meta["version"] = it["version"]
            meta_str = json.dumps(item_meta).replace("'", "''")
            pri = priority_to_int(it["priority"])
            comma = "," if i < len(items) - 1 else ""
            out.write(
                "  ("
                + sql_quote(u)
                + ", "
                + sql_quote(safe_project_uuid)
                + ", "
                + sql_quote(it["title"])
                + ", "
                + sql_quote(it["description"])
                + ", "
                + sql_quote(it["item_type"])
                + ", "
                + sql_quote(it["status"])
                + ", "
                + str(pri)
                + ", "
                + parent_uuid
                + ", '"
                + meta_str
                + "'::jsonb, NOW(), NOW())"
                + comma
                + "\n",
            )
        out.write(";\n\n")

        # Default graph for the project (required for links.graph_id)
        graph_id = str(uuid.uuid4())
        out.write(
            "INSERT INTO graphs (id, project_id, name, graph_type, description, root_item_id, graph_metadata, created_at, updated_at)\n",
        )
        out.write(
            "VALUES ("
            + sql_quote(graph_id)
            + ", "
            + sql_quote(safe_project_uuid)
            + "::uuid, 'Trace graph', 'trace', NULL, NULL, '{}'::jsonb, NOW(), NOW());\n\n",
        )

        # Links: id, project_id, graph_id, source_item_id, target_item_id, link_type, link_metadata, created_at, updated_at
        valid_links = []
        for ln in links_raw:
            src = logical_to_uuid.get(ln["source_item_id"])
            tgt = logical_to_uuid.get(ln["target_item_id"])
            if not src or not tgt:
                continue
            meta = ln.get("link_metadata") or "{}"
            try:
                json.loads(meta)
            except Exception:
                meta = "{}"
            valid_links.append((str(uuid.uuid4()), src, tgt, ln["link_type"], meta))
        out.write(
            "INSERT INTO links (id, project_id, graph_id, source_item_id, target_item_id, link_type, link_metadata, created_at, updated_at)\nVALUES\n",
        )
        for i, (link_uuid, src, tgt, link_type, meta) in enumerate(valid_links):
            meta_esc = meta.replace("'", "''")
            comma = "," if i < len(valid_links) - 1 else ""
            out.write(
                "  ("
                + sql_quote(link_uuid)
                + ", "
                + sql_quote(safe_project_uuid)
                + "::uuid, "
                + sql_quote(graph_id)
                + ", "
                + sql_quote(src)
                + ", "
                + sql_quote(tgt)
                + ", "
                + sql_quote(link_type)
                + ", '"
                + meta_esc
                + "'::jsonb, NOW(), NOW())"
                + comma
                + "\n",
            )
        out.write(";\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
