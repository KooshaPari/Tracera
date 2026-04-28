#!/usr/bin/env python3
"""
Schema drift detection CLI for Pheno-SDK.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from pheno.tools.schema_sync import SchemaDiff, SchemaSync


def _render_diff(diff: SchemaDiff) -> list[str]:
    if diff.is_empty():
        return []
    payload = diff.render().splitlines()
    return [line for line in payload if line.strip()]


def check_schema_drift(*, offline: bool = False) -> dict[str, Any]:
    sync = SchemaSync(root_dir=ROOT_DIR)
    result: dict[str, Any] = {
        "status": "healthy",
        "drift_detected": False,
        "diff": [],
    }

    if offline:
        snapshot = sync.load_local_snapshot()
        result.update(
            {
                "status": "offline",
                "tables": len(snapshot.tables),
                "enums": len(snapshot.enums),
            },
        )
        return result

    try:
        remote = sync.fetch_remote_snapshot()
        local = sync.load_local_snapshot()
        diff = SchemaSync.diff_snapshots(local, remote)
        if not diff.is_empty():
            result["status"] = "drift_detected"
            result["drift_detected"] = True
            result["diff"] = _render_diff(diff)
        result["tables"] = len(remote.tables)
        result["enums"] = len(remote.enums)
        return result
    except Exception as exc:  # pragma: no cover - connection issues
        result.update({"status": "error", "drift_detected": True, "error": str(exc)})
        return result


def validate_schema_consistency(*, offline: bool = False) -> dict[str, Any]:
    sync = SchemaSync(root_dir=ROOT_DIR)
    metadata_path = sync.metadata_path
    snapshot = sync.load_local_snapshot()
    metadata: dict[str, Any] | None = None

    if metadata_path.exists():
        try:
            metadata = json.loads(metadata_path.read_text())
        except json.JSONDecodeError:
            metadata = None

    consistent = metadata is not None and metadata.get("hash") == snapshot.hash()
    status = "consistent" if consistent else "inconsistent"
    if offline:
        status = "offline"

    return {
        "status": status,
        "consistent": consistent,
        "metadata_present": metadata is not None,
        "snapshot_tables": len(snapshot.tables),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Check schema drift")
    parser.add_argument("--json", action="store_true", help="Output JSON format")
    parser.add_argument(
        "--offline",
        action="store_true",
        help="Skip remote snapshot fetches",
    )
    args = parser.parse_args()

    drift_result = check_schema_drift(offline=args.offline)
    consistency_result = validate_schema_consistency(offline=args.offline)

    overall_status = "healthy"
    if drift_result.get("drift_detected") or consistency_result.get("status") not in {
        "consistent",
        "offline",
    }:
        overall_status = "issues_detected"

    combined_result = {
        "drift_check": drift_result,
        "consistency_check": consistency_result,
        "overall_status": overall_status,
    }

    if args.json:
        print(json.dumps(combined_result, indent=2))
    else:
        print("Schema Drift Check Results:")
        print("=" * 40)
        print(f"\nDrift Check: {drift_result['status']}")
        if drift_result.get("diff"):
            print("  Diff summary:")
            for line in drift_result["diff"]:
                print(f"    {line}")
        print(f"\nConsistency Check: {consistency_result['status']}")
        print(f"  Snapshot tables: {consistency_result['snapshot_tables']}")
        print(f"\nOverall Status: {overall_status}")

    return 0 if overall_status == "healthy" or args.offline else 1


if __name__ == "__main__":
    raise SystemExit(main())
