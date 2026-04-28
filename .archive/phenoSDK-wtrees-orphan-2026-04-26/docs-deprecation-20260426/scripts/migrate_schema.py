#!/usr/bin/env python3
"""
Database schema synchronization and drift detection helper.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

ROOT_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from pheno.tools.schema_sync import SchemaDiff, SchemaSync  # noqa: E402

DEFAULT_PROJECT_ROOT = ROOT_DIR
DEFAULT_SCHEMA_DIR = ROOT_DIR / "schemas"
DEFAULT_MIGRATIONS_DIR = ROOT_DIR / "scripts" / "migrations"


@dataclass
class SchemaHealth:
    """
    Simple container for schema health details.
    """

    status: str
    schema_version: str
    tables_count: int
    drift_detected: bool
    validation_passed: bool
    diff_summary: str | None = None

    @classmethod
    def healthy(cls) -> SchemaHealth:
        """
        Return a baseline healthy status placeholder.
        """
        return cls(
            status="healthy",
            schema_version="v1.0.0",
            tables_count=0,
            drift_detected=False,
            validation_passed=True,
            diff_summary=None,
        )


def _read_metadata(sync: SchemaSync) -> dict[str, Any] | None:
    if not sync.metadata_path.exists():
        return None
    try:
        return json.loads(sync.metadata_path.read_text())
    except json.JSONDecodeError:
        return None


def check_schema_health(
    project_root: Path,
    *,
    offline: bool = False,
) -> tuple[SchemaHealth, SchemaDiff | None]:
    """
    Check schema drift status using SchemaSync utilities.
    """

    sync = SchemaSync(root_dir=project_root)
    metadata = _read_metadata(sync)

    if offline:
        snapshot = sync.load_local_snapshot()
        version = metadata.get("hash") if metadata else "unknown"
        return (
            SchemaHealth(
                status="offline",
                schema_version=str(version),
                tables_count=len(snapshot.tables),
                drift_detected=False,
                validation_passed=True,
                diff_summary=None,
            ),
            None,
        )

    try:
        remote_snapshot = sync.fetch_remote_snapshot()
        local_snapshot = sync.load_local_snapshot()
        diff = SchemaSync.diff_snapshots(local_snapshot, remote_snapshot)
        version = metadata.get("hash") if metadata else remote_snapshot.hash()
        summary = diff.render() if not diff.is_empty() else None
        health = SchemaHealth(
            status="healthy" if diff.is_empty() else "drift_detected",
            schema_version=str(version),
            tables_count=len(remote_snapshot.tables),
            drift_detected=not diff.is_empty(),
            validation_passed=diff.is_empty(),
            diff_summary=summary,
        )
        return health, diff
    except Exception as exc:  # pragma: no cover - defensive path when DB is unavailable
        return (
            SchemaHealth(
                status="error",
                schema_version="unknown",
                tables_count=0,
                drift_detected=True,
                validation_passed=False,
                diff_summary=str(exc),
            ),
            None,
        )


def sync_schema(project_root: Path, migrations_dir: Path, force: bool, offline: bool) -> bool:
    """
    Synchronize schema snapshot with the remote database.
    """

    if offline:
        print("Offline mode: skipping remote synchronization.")
        return False

    sync = SchemaSync(root_dir=project_root)
    snapshot = sync.update()
    print(f"Snapshot updated ({len(snapshot.tables)} tables, {len(snapshot.enums)} enums).")
    if migrations_dir.exists():
        print(f"Migrations directory: {migrations_dir}")
    if force:
        print("Force flag set – ensure migrations are applied manually if required.")
    return True


def validate_deployment_config(env: dict[str, Any], *, offline: bool = False) -> bool:
    """
    Validate deployment configuration environment variables.
    """

    if offline:
        return True

    required_keys = ("DATABASE_URL", "SCHEMA_SEARCH_PATH")
    missing = [key for key in required_keys if not env.get(key)]
    if missing:
        print(f"Missing required configuration keys: {', '.join(missing)}", file=sys.stderr)
        return False
    print("Deployment configuration validated.")
    return True


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Database schema management utility.")
    parser.add_argument(
        "--project-root",
        type=Path,
        default=DEFAULT_PROJECT_ROOT,
        help="Repository root containing schema assets (default: project root).",
    )
    parser.add_argument(
        "--migrations-dir",
        type=Path,
        default=DEFAULT_MIGRATIONS_DIR,
        help="Path to migration scripts (default: scripts/migrations/).",
    )
    parser.add_argument(
        "--check-only",
        action="store_true",
        help="Check schema health without performing synchronization.",
    )
    parser.add_argument(
        "--force-sync",
        action="store_true",
        help="Force schema synchronization even if drift is not detected.",
    )
    parser.add_argument(
        "--skip-config-validation",
        action="store_true",
        help="Skip environment configuration validation.",
    )
    parser.add_argument(
        "--offline",
        action="store_true",
        help="Skip remote snapshot fetches (use local snapshots only).",
    )
    return parser.parse_args(args=argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    if not args.skip_config_validation and not validate_deployment_config(
        os.environ, offline=args.offline,
    ):
        return 1

    project_root = args.project_root.resolve()
    migrations_dir = args.migrations_dir.resolve()

    health, diff = check_schema_health(project_root, offline=args.offline)
    print(f"Schema status: {health.status}")
    print(f"Schema version: {health.schema_version}")
    print(f"Tables count: {health.tables_count}")
    if health.diff_summary:
        print("\nDiff summary:\n" + health.diff_summary)

    if args.check_only:
        if health.drift_detected and not args.offline:
            print(
                "Schema drift detected. Run without --check-only to synchronize.", file=sys.stderr,
            )
            return 1
        return 0 if health.validation_passed else 1

    if diff and not diff.is_empty() and not args.force_sync:
        print(
            "Schema drift detected. Re-run with --force-sync to apply migrations.",
            file=sys.stderr,
        )
        return 1

    success = sync_schema(project_root, migrations_dir, args.force_sync, args.offline)
    return 0 if success else 1


if __name__ == "__main__":
    raise SystemExit(main())
