"""
Supabase schema synchronisation utilities.
"""

from __future__ import annotations

import argparse
import json
import os
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any

from dotenv import load_dotenv

if TYPE_CHECKING:
    from collections.abc import Iterable

load_dotenv()


@dataclass
class TableColumn:
    name: str
    data_type: str
    is_nullable: bool
    default: str | None = None
    udt_name: str | None = None

    @classmethod
    def from_row(cls, row: Iterable[Any]) -> TableColumn:
        column_name, data_type, is_nullable, default, udt_name = row
        return cls(
            name=str(column_name),
            data_type=str(data_type),
            is_nullable=str(is_nullable) == "YES",
            default=None if default in {None, "NULL"} else str(default),
            udt_name=str(udt_name) if udt_name else None,
        )

    def as_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "data_type": self.data_type,
            "is_nullable": self.is_nullable,
            "default": self.default,
            "udt_name": self.udt_name,
        }


@dataclass
class SchemaSnapshot:
    tables: dict[str, list[TableColumn]] = field(default_factory=dict)
    enums: dict[str, list[str]] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> SchemaSnapshot:
        tables = {
            name: [TableColumn(**col) for col in columns]
            for name, columns in payload.get("tables", {}).items()
        }
        enums = {name: list(values) for name, values in payload.get("enums", {}).items()}
        return cls(tables=tables, enums=enums)

    def to_dict(self) -> dict[str, Any]:
        return {
            "tables": {
                name: [col.as_dict() for col in columns] for name, columns in self.tables.items()
            },
            "enums": self.enums,
        }

    def hash(self) -> str:
        import hashlib

        packed = json.dumps(self.to_dict(), sort_keys=True, separators=(",", ":")).encode()
        return hashlib.sha256(packed).hexdigest()


@dataclass
class SchemaDiff:
    added_tables: set[str] = field(default_factory=set)
    removed_tables: set[str] = field(default_factory=set)
    changed_tables: dict[str, dict[str, set[str]]] = field(default_factory=dict)
    added_enums: set[str] = field(default_factory=set)
    removed_enums: set[str] = field(default_factory=set)
    changed_enums: dict[str, dict[str, set[str]]] = field(default_factory=dict)

    def is_empty(self) -> bool:
        return not any(
            [
                self.added_tables,
                self.removed_tables,
                self.changed_tables,
                self.added_enums,
                self.removed_enums,
                self.changed_enums,
            ],
        )

    def render(self) -> str:
        lines: list[str] = []
        if self.added_tables:
            lines.append("## Added tables")
            lines.extend(f"- {name}" for name in sorted(self.added_tables))
        if self.removed_tables:
            lines.append("## Removed tables")
            lines.extend(f"- {name}" for name in sorted(self.removed_tables))
        for table, changes in sorted(self.changed_tables.items()):
            lines.append(f"## Table changes: {table}")
            for key, values in changes.items():
                if values:
                    lines.append(f"- {key}: {', '.join(sorted(values))}")
        if self.added_enums:
            lines.append("## Added enums")
            lines.extend(f"- {name}" for name in sorted(self.added_enums))
        if self.removed_enums:
            lines.append("## Removed enums")
            lines.extend(f"- {name}" for name in sorted(self.removed_enums))
        for enum, changes in sorted(self.changed_enums.items()):
            lines.append(f"## Enum changes: {enum}")
            for key, values in changes.items():
                if values:
                    lines.append(f"- {key}: {', '.join(sorted(values))}")
        return "\n".join(lines) if lines else "No differences detected."


class SchemaSync:
    """
    Synchronise Supabase metadata with generated schema snapshots.
    """

    def __init__(self, project_id: str | None = None, root_dir: Path | None = None) -> None:
        self.root = root_dir or Path.cwd()
        self.project_id = project_id or os.getenv("SUPABASE_PROJECT_ID", "")
        self.snapshot_path = self.root / "schemas" / "generated" / "schema_snapshot.json"
        self.metadata_path = self.root / "schemas" / "schema_version.json"

    def fetch_remote_snapshot(self) -> SchemaSnapshot:
        import psycopg2

        db_url = os.getenv("DB_URL")
        if not db_url:
            db_password = os.getenv("SUPABASE_DB_PASSWORD")
            if not db_password:
                raise RuntimeError("Provide DB_URL or SUPABASE_DB_PASSWORD for schema sync")
            db_url = (
                "postgresql://postgres:"
                + db_password
                + "@aws-0-us-west-1.pooler.supabase.com:6543/postgres"
            )

        with psycopg2.connect(db_url) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT table_name
                    FROM information_schema.tables
                    WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
                    ORDER BY table_name
                    """,
                )
                tables = [row[0] for row in cur.fetchall()]

                table_map: dict[str, list[TableColumn]] = {}
                for table in tables:
                    cur.execute(
                        """
                        SELECT column_name, data_type, is_nullable, column_default, udt_name
                        FROM information_schema.columns
                        WHERE table_schema = 'public' AND table_name = %s
                        ORDER BY ordinal_position
                        """,
                        (table,),
                    )
                    table_map[table] = [TableColumn.from_row(row) for row in cur.fetchall()]

                cur.execute(
                    """
                    SELECT t.typname, array_agg(e.enumlabel ORDER BY e.enumsortorder)
                    FROM pg_type t
                    JOIN pg_enum e ON t.oid = e.enumtypid
                    WHERE t.typtype = 'e'
                    GROUP BY t.typname
                    ORDER BY t.typname
                    """,
                )
                enums = {row[0]: list(row[1]) for row in cur.fetchall()}

        return SchemaSnapshot(tables=table_map, enums=enums)

    def load_local_snapshot(self) -> SchemaSnapshot:
        if not self.snapshot_path.exists():
            return SchemaSnapshot()
        payload = json.loads(self.snapshot_path.read_text())
        return SchemaSnapshot.from_dict(payload)

    def save_snapshot(self, snapshot: SchemaSnapshot) -> None:
        self.snapshot_path.parent.mkdir(parents=True, exist_ok=True)
        self.snapshot_path.write_text(json.dumps(snapshot.to_dict(), indent=2, sort_keys=True))
        meta = {
            "hash": snapshot.hash(),
            "generated_at": datetime.now(UTC).isoformat(),
            "project_id": self.project_id,
        }
        self.metadata_path.write_text(json.dumps(meta, indent=2, sort_keys=True))

    @staticmethod
    def diff_snapshots(current: SchemaSnapshot, candidate: SchemaSnapshot) -> SchemaDiff:
        diff = SchemaDiff()

        current_tables = set(current.tables)
        candidate_tables = set(candidate.tables)
        diff.added_tables = candidate_tables - current_tables
        diff.removed_tables = current_tables - candidate_tables

        for table in sorted(current_tables & candidate_tables):
            current_cols = {col.name: col for col in current.tables[table]}
            new_cols = {col.name: col for col in candidate.tables[table]}
            added = set(new_cols) - set(current_cols)
            removed = set(current_cols) - set(new_cols)
            changed = {
                name
                for name in current_cols
                if name in new_cols and current_cols[name].as_dict() != new_cols[name].as_dict()
            }
            if added or removed or changed:
                diff.changed_tables[table] = {
                    "added_columns": added,
                    "removed_columns": removed,
                    "modified_columns": changed,
                }

        current_enums = set(current.enums)
        candidate_enums = set(candidate.enums)
        diff.added_enums = candidate_enums - current_enums
        diff.removed_enums = current_enums - candidate_enums

        for enum in sorted(current_enums & candidate_enums):
            current_vals = set(current.enums[enum])
            new_vals = set(candidate.enums[enum])
            added = new_vals - current_vals
            removed = current_vals - new_vals
            if added or removed:
                diff.changed_enums[enum] = {"added_values": added, "removed_values": removed}

        return diff

    # Public API -----------------------------------------------------------
    def check(self) -> SchemaDiff:
        local = self.load_local_snapshot()
        remote = self.fetch_remote_snapshot()
        return self.diff_snapshots(local, remote)

    def update(self) -> SchemaSnapshot:
        remote = self.fetch_remote_snapshot()
        self.save_snapshot(remote)
        return remote

    def report(self, output: Path | None = None) -> Path:
        diff = self.check()
        target = output or (
            self.root / "reports" / f"schema_diff_{datetime.now(UTC).strftime('%Y%m%d_%H%M%S')}.md"
        )
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(diff.render())
        return target


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Supabase schema helper")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("check", help="Fetch remote schema and show drift summary")
    sub.add_parser("diff", help="Alias for check (prints diff output)")
    sub.add_parser("update", help="Persist the latest snapshot to disk")
    report_parser = sub.add_parser("report", help="Generate a Markdown diff report")
    report_parser.add_argument("--out", type=Path, help="Path for the report file")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    sync = SchemaSync()

    if args.command in {"check", "diff"}:
        diff = sync.check()
        if diff.is_empty():
            print("✅ Schema is up to date.")
            return 0
        print(diff.render())
        return 1

    if args.command == "update":
        snapshot = sync.update()
        print(
            f"✅ Schema snapshot updated ({len(snapshot.tables)} tables, {len(snapshot.enums)} enums).",
        )
        return 0

    if args.command == "report":
        path = sync.report(output=args.out)
        print(f"📄 Report written to {path}")
        return 0

    parser.print_help()
    return 2


__all__ = ["SchemaDiff", "SchemaSnapshot", "SchemaSync", "TableColumn", "main"]
