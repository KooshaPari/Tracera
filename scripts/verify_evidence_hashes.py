#!/usr/bin/env python3
"""Verify every sha256 attestation in the state-forward evidence corpus.

The corpus under ``docs/state/tracera-state-forward-20261017-q1`` is an
append-only record of observed state. Each observation directory carries its
own ``SHA256SUMS`` manifest, and two further manifests (``input-manifest.json``
and ``EVIDENCE-SHA256.json``) attest the inputs and the census evidence.

Those attestations are only meaningful if the artifacts keep the exact bytes
that were captured. Formatting tools must therefore never rewrite this tree:
``ruff.toml`` excludes ``docs/state`` and ``.prettierignore`` excludes the same
paths. This script proves the exclusion still holds.

Usage:
    python3 scripts/verify_evidence_hashes.py
    python3 scripts/verify_evidence_hashes.py --corpus docs/state/<name>

Exits 0 when every attested entry matches, 1 otherwise.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CORPUS = REPO_ROOT / "docs/state/tracera-state-forward-20261017-q1"


def sha256_of(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(64 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_sha256sums(corpus: Path) -> tuple[int, int, list[str]]:
    """Verify every ``SHA256SUMS`` manifest inside the corpus."""
    total = 0
    passing = 0
    failing: list[str] = []
    for manifest in sorted(corpus.rglob("SHA256SUMS")):
        for raw in manifest.read_text(encoding="utf-8").splitlines():
            line = raw.strip()
            if not line:
                continue
            parts = line.split(None, 1)
            if len(parts) != 2:
                failing.append(f"MALFORMED {manifest.relative_to(REPO_ROOT)}: {line}")
                continue
            expected, rel = parts[0], parts[1].lstrip("*")
            target = manifest.parent / rel
            total += 1
            if not target.is_file():
                failing.append(f"MISSING {target.relative_to(REPO_ROOT)}")
                continue
            actual = sha256_of(target)
            if actual == expected:
                passing += 1
            else:
                failing.append(
                    f"MISMATCH {target.relative_to(REPO_ROOT)} "
                    f"(expected {expected[:12]}, got {actual[:12]})"
                )
    return passing, total, failing


def verify_input_manifest(corpus: Path) -> tuple[int, int, list[str]]:
    """Verify the ``inputs`` entries of ``input-manifest.json``."""
    manifest = corpus / "input-manifest.json"
    if not manifest.is_file():
        return 0, 0, [f"MISSING {manifest.relative_to(REPO_ROOT)}"]
    entries = json.loads(manifest.read_text(encoding="utf-8"))["inputs"]
    passing = 0
    failing: list[str] = []
    for entry in entries:
        rel = entry["path"]
        expected = entry["sha256"]
        target = (corpus / rel).resolve()
        if not target.is_file():
            failing.append(f"MISSING {rel}")
            continue
        actual = sha256_of(target)
        if actual == expected:
            passing += 1
        else:
            failing.append(
                f"MISMATCH {rel} (expected {expected[:12]}, got {actual[:12]})"
            )
    return passing, len(entries), failing


def verify_evidence_sha(corpus: Path) -> tuple[int, int, list[str]]:
    """Verify every ``EVIDENCE-SHA256.json`` manifest inside the corpus."""
    total = 0
    passing = 0
    failing: list[str] = []
    for manifest in sorted(corpus.rglob("EVIDENCE-SHA256.json")):
        base = manifest.parent
        data = json.loads(manifest.read_text(encoding="utf-8"))
        for rel, expected in data.items():
            total += 1
            target = (base / rel).resolve()
            if not target.is_file():
                failing.append(f"MISSING {rel}")
                continue
            actual = sha256_of(target)
            if actual == expected:
                passing += 1
            else:
                failing.append(
                    f"MISMATCH {rel} (expected {expected[:12]}, got {actual[:12]})"
                )
    return passing, total, failing


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--corpus",
        default=str(DEFAULT_CORPUS),
        help="evidence corpus directory to verify (default: the state-forward corpus)",
    )
    args = parser.parse_args(argv)
    corpus = Path(args.corpus).resolve()

    checks = [
        ("SHA256SUMS", *verify_sha256sums(corpus)),
        ("input-manifest.json", *verify_input_manifest(corpus)),
        ("EVIDENCE-SHA256.json", *verify_evidence_sha(corpus)),
    ]

    print("=" * 70)
    print(f"EVIDENCE HASH VERIFICATION  (corpus: {corpus.name})")
    print("=" * 70)
    for name, passing, total, failing in checks:
        print(f"  {name:<22} {passing}/{total}")
        for message in failing:
            print(f"    - {message}")

    passing = sum(c[1] for c in checks)
    total = sum(c[2] for c in checks)
    failures = sum(len(c[3]) for c in checks)
    print()
    print(f"OVERALL: {passing}/{total} entries verified")
    if failures == 0:
        print("STATUS  : PASS")
        return 0
    print(f"STATUS  : FAIL ({failures} mismatches)")
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
