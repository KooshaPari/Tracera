#!/usr/bin/env python3
"""Schema Validation Script for Pheno-SDK.

Validates local schema snapshots, metadata, and optional definition modules.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = REPO_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from pheno.tools.schema_sync import SchemaSnapshot  # noqa: E402


@dataclass
class ValidationReport:
    status: str
    details: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        payload = {"status": self.status}
        payload.update(self.details)
        return payload


def _load_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text())
    except json.JSONDecodeError as exc:
        raise ValueError(f"{path} is not valid JSON: {exc}") from exc


def validate_snapshot(schemas_dir: Path) -> ValidationReport:
    snapshot_path = schemas_dir / "generated" / "schema_snapshot.json"
    metadata_path = schemas_dir / "schema_version.json"

    if not snapshot_path.exists():
        return ValidationReport(
            status="missing_snapshot",
            details={"snapshot_path": str(snapshot_path)},
        )

    payload = _load_json(snapshot_path)
    snapshot = SchemaSnapshot.from_dict(payload)
    table_count = len(snapshot.tables)
    enum_count = len(snapshot.enums)
    snapshot_hash = snapshot.hash()

    metadata_status = "missing"
    stored_hash = None
    if metadata_path.exists():
        metadata = _load_json(metadata_path)
        stored_hash = metadata.get("hash")
        metadata_status = "valid" if stored_hash == snapshot_hash else "hash_mismatch"

    return ValidationReport(
        status="ok" if metadata_status == "valid" else metadata_status,
        details={
            "tables": table_count,
            "enums": enum_count,
            "snapshot_path": str(snapshot_path),
            "metadata_path": str(metadata_path),
            "snapshot_hash": snapshot_hash,
            "stored_hash": stored_hash,
        },
    )


def validate_definition_modules(schemas_dir: Path) -> ValidationReport:
    definitions_dir = schemas_dir / "definitions"
    if not definitions_dir.exists():
        return ValidationReport(
            status="missing_definitions",
            details={"definitions_path": str(definitions_dir)},
        )

    python_files = list(definitions_dir.rglob("*.py"))
    parsed = 0
    issues: list[dict[str, str]] = []

    for file_path in python_files:
        try:
            file_path.read_text()
            parsed += 1
        except UnicodeDecodeError as exc:
            issues.append({"file": str(file_path), "reason": f"Encoding error: {exc}"})
        except OSError as exc:
            issues.append({"file": str(file_path), "reason": f"I/O error: {exc}"})

    status = "ok" if not issues else "invalid"
    return ValidationReport(
        status=status,
        details={
            "definitions_path": str(definitions_dir),
            "files_discovered": len(python_files),
            "files_parsed": parsed,
            "issues": issues[:10],
        },
    )


def validate_schema_assets(schemas_dir: Path) -> dict[str, Any]:
    snapshot_report = validate_snapshot(schemas_dir)
    definitions_report = validate_definition_modules(schemas_dir)

    status_priority = [
        "ok",
        "hash_mismatch",
        "missing",
        "missing_snapshot",
        "missing_definitions",
        "invalid",
    ]

    combined_status = "ok"
    for candidate in (snapshot_report.status, definitions_report.status):
        if status_priority.index(candidate) > status_priority.index(combined_status):
            combined_status = candidate

    return {
        "status": combined_status,
        "snapshot": snapshot_report.to_dict(),
        "definitions": definitions_report.to_dict(),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate schema assets for pheno-sdk.")
    parser.add_argument(
        "--schemas-dir",
        type=Path,
        default=REPO_ROOT / "schemas",
        help="Directory containing schema assets (default: ./schemas).",
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON output.")
    parser.add_argument(
        "--output",
        type=Path,
        help="Optional path to write the JSON report.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    schemas_dir = args.schemas_dir.resolve()

    report = validate_schema_assets(schemas_dir)

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, indent=2))

    if args.json or args.output:
        print(json.dumps(report, indent=2))
    else:
        print("Schema Validation Summary")
        print("========================")
        print(f"Overall status: {report['status']}")
        snapshot = report["snapshot"]
        print(
            f"Snapshot status: {snapshot['status']} "
            f"(tables={snapshot.get('tables', 0)}, enums={snapshot.get('enums', 0)})",
        )
        definitions = report["definitions"]
        print(
            f"Definitions status: {definitions['status']} "
            f"(files={definitions.get('files_discovered', 0)})",
        )
        if definitions.get("issues"):
            print("Definition issues:")
            for issue in definitions["issues"]:
                print(f"  - {issue['file']}: {issue['reason']}")

    return 0 if report["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
