#!/usr/bin/env python3
"""
Manage benchmark metadata and optional dataset downloads.
"""

from __future__ import annotations

import argparse
import json
import os
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from urllib.request import urlretrieve

ROOT_DIR = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = ROOT_DIR / "data" / "benchmarks" / "manifest.json"
MANIFEST_ENV_KEY = "PHENO_BENCHMARK_MANIFEST"


@dataclass
class BenchmarkEntry:
    dataset: str
    source: str
    split: str
    samples: int | None
    checksum: str | None
    registered_at: str
    notes: str | None = None
    local_path: str | None = None

    @classmethod
    def create(
        cls,
        dataset: str,
        source: str,
        split: str,
        samples: int | None,
        checksum: str | None,
        notes: str | None,
        local_path: str | None,
    ) -> BenchmarkEntry:
        return cls(
            dataset=dataset,
            source=source,
            split=split,
            samples=samples,
            checksum=checksum,
            notes=notes,
            local_path=local_path,
            registered_at=datetime.now(tz=UTC).isoformat(),
        )


def manifest_path() -> Path:
    override = os.getenv(MANIFEST_ENV_KEY)
    if override:
        return Path(override).expanduser().resolve()
    return DEFAULT_MANIFEST


def load_manifest(path: Path) -> dict[str, dict[str, object]]:
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        return {}
    with path.open("r", encoding="utf-8") as handle:
        try:
            return json.load(handle)
        except json.JSONDecodeError:
            return {}


def save_manifest(path: Path, payload: dict[str, dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True))


def download_dataset(source: str, target_dir: Path) -> Path | None:
    target_dir.mkdir(parents=True, exist_ok=True)
    filename = source.split("/")[-1] or "dataset.bin"
    destination = target_dir / filename
    try:
        urlretrieve(source, destination)
        return destination
    except Exception as exc:  # pragma: no cover - network dependent
        print(f"⚠️  Failed to download dataset ({exc}).")
        return None


def register_dataset(args: argparse.Namespace) -> None:
    local_path = None
    if args.download:
        if not args.destination:
            raise SystemExit("Provide --destination when using --download.")
        downloaded = download_dataset(args.source, args.destination)
        if downloaded:
            local_path = str(downloaded)

    entry = BenchmarkEntry.create(
        dataset=args.dataset,
        source=args.source,
        split=args.split,
        samples=args.samples,
        checksum=args.checksum,
        notes=args.notes,
        local_path=local_path,
    )
    manifest_file = manifest_path()
    manifest = load_manifest(manifest_file)
    manifest[entry.dataset] = asdict(entry)
    save_manifest(manifest_file, manifest)
    print(f"Registered dataset '{entry.dataset}' in {manifest_file}")
    if local_path:
        print(f" 👉 Downloaded to {local_path}")


def list_datasets(_: argparse.Namespace) -> None:
    manifest_file = manifest_path()
    manifest = load_manifest(manifest_file)
    if not manifest:
        print("No benchmark datasets registered yet.")
        return
    for dataset, payload in manifest.items():
        location = payload.get("local_path") or payload.get("source")
        print(f"- {dataset} ({payload.get('split')}) :: {location}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Manage benchmark metadata for Pheno-SDK.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    register_parser = sub.add_parser(
        "register",
        help="Register or update a dataset entry.",
    )
    register_parser.add_argument(
        "--dataset",
        required=True,
        help="Dataset name (e.g., SWE-bench-lite).",
    )
    register_parser.add_argument(
        "--source",
        required=True,
        help="Source URL or local path.",
    )
    register_parser.add_argument(
        "--split",
        default="default",
        help="Dataset split identifier.",
    )
    register_parser.add_argument(
        "--samples",
        type=int,
        help="Number of samples/examples.",
    )
    register_parser.add_argument(
        "--checksum",
        help="Optional checksum for verification.",
    )
    register_parser.add_argument("--notes", help="Additional notes or context.")
    register_parser.add_argument(
        "--download",
        action="store_true",
        help="Download the dataset immediately.",
    )
    register_parser.add_argument(
        "--destination",
        type=Path,
        help="Directory for downloaded assets.",
    )
    register_parser.set_defaults(func=register_dataset)

    list_parser = sub.add_parser("list", help="List registered datasets.")
    list_parser.set_defaults(func=list_datasets)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    args.func(args)
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    raise SystemExit(main())
