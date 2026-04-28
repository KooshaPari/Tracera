#!/usr/bin/env python3
"""Ensure core Pheno-SDK documentation reflects the current SDK surface area.

The fingerprint captures the exported namespaces and optional dependency bundles. Docs
must embed matching markers so changes to pheno-sdk force docs to stay current. Run with
--update to refresh markers after editing documentation.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

try:
    import tomllib  # Python 3.11+
except ModuleNotFoundError:  # pragma: no cover
    import tomli as tomllib  # type: ignore


REPO_ROOT = Path(__file__).resolve().parents[2]

DOC_MARKERS = {
    REPO_ROOT / "PHENO.MD": "PHENO_MD_FINGERPRINT",
    REPO_ROOT / "docs" / "index.md": "DOCS_INDEX_FINGERPRINT",
    REPO_ROOT / "docs" / "kits" / "overview.md": "DOCS_KITS_OVERVIEW_FINGERPRINT",
}


def gather_fingerprint_data() -> dict:
    """
    Collect stable SDK metadata used to fingerprint docs.
    """
    pheno_pkg = REPO_ROOT / "src" / "pheno"
    if not pheno_pkg.exists():
        raise SystemExit(f"pheno namespace not found at {pheno_pkg}")

    namespaces = sorted(
        entry.name
        for entry in pheno_pkg.iterdir()
        if entry.is_dir() and not entry.name.startswith("__")
    )

    pyproject_path = REPO_ROOT / "pyproject.toml"
    if not pyproject_path.exists():
        raise SystemExit(f"pyproject.toml missing at {pyproject_path}")

    with pyproject_path.open("rb") as handle:
        pyproject = tomllib.load(handle)

    optional_deps = pyproject.get("project", {}).get("optional-dependencies", {})
    extras = {name: sorted(values) for name, values in optional_deps.items()}

    return {
        "namespaces": namespaces,
        "optional_dependencies": extras,
    }


def compute_fingerprint(data: dict) -> str:
    payload = json.dumps(data, sort_keys=True).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def update_marker(path: Path, marker: str, fingerprint: str) -> bool:
    marker_text = f"<!-- {marker}: {fingerprint} -->"
    lines = path.read_text(encoding="utf-8").splitlines()

    for idx, line in enumerate(lines):
        if line.strip().startswith(f"<!-- {marker}:"):
            if line.strip() == marker_text:
                return False
            lines[idx] = marker_text
            path.write_text("\n".join(lines) + "\n", encoding="utf-8")
            return True

    if lines and lines[-1].strip():
        lines.append("")
    lines.append(marker_text)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return True


def verify_marker(path: Path, marker: str, fingerprint: str) -> None:
    marker_text = f"<!-- {marker}: {fingerprint} -->"
    contents = path.read_text(encoding="utf-8")
    if marker_text not in contents:
        raise SystemExit(
            f"{path} is out of sync.\n"
            f"Expected marker: {marker_text}\n"
            "Run 'python scripts/checks/verify_pheno_docs.py --update' to refresh.",
        )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--update",
        action="store_true",
        help="Rewrite documentation markers with the current fingerprint.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    fingerprint = compute_fingerprint(gather_fingerprint_data())

    if args.update:
        changed = False
        for path, marker in DOC_MARKERS.items():
            if not path.exists():
                raise SystemExit(f"Documentation file missing: {path}")
            changed |= update_marker(path, marker, fingerprint)
        if changed:
            print("Updated Pheno-SDK documentation fingerprints.")
        else:
            print("Pheno-SDK documentation fingerprints already up to date.")
        return

    for path, marker in DOC_MARKERS.items():
        if not path.exists():
            raise SystemExit(f"Documentation file missing: {path}")
        verify_marker(path, marker, fingerprint)

    print("Pheno-SDK documentation fingerprints verified.")


if __name__ == "__main__":
    main()
