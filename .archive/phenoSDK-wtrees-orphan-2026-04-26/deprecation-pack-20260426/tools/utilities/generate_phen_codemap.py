"""Utility to audit `pheno` namespace references while reorganising packages into their
layered homes.

Run from the repo root:

    python tools/generate_phen_codemap.py

It emits three sections:
1. Packaging/config files referencing `src/pheno`.
2. Python modules importing `pheno.*` (grouped by package).
3. Suggested `sed`/`python` commands for bulk replacement.
"""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
DOCS_ROOT = REPO_ROOT / "docs"


def _load_manifest() -> dict:
    manifest_path = REPO_ROOT / "tools" / "phen_namespace_manifest.json"
    with manifest_path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def _find_python_imports() -> tuple[Counter, dict[str, list[str]]]:
    per_top_level = Counter()
    samples: dict[str, list[str]] = defaultdict(list)

    for path in SRC_ROOT.rglob("*.py"):
        if not path.is_file():
            continue
        rel = path.relative_to(REPO_ROOT)
        text = path.read_text(encoding="utf-8", errors="ignore")
        if "from pheno" not in text and "import pheno" not in text:
            continue
        top_level = rel.parts[1] if len(rel.parts) > 1 else rel.parts[0]
        per_top_level[top_level] += 1
        if len(samples[top_level]) < 5:
            for line in text.splitlines():
                if "from pheno" in line or "import pheno" in line:
                    samples[top_level].append(f"{rel}:{line.strip()}")
                    if len(samples[top_level]) >= 5:
                        break
    return per_top_level, samples


def _find_docs_references() -> list[str]:
    matches: list[str] = []
    for path in DOCS_ROOT.rglob("*"):
        if not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if "src/pheno" in text:
            matches.append(str(path.relative_to(REPO_ROOT)))
    return matches


def main() -> None:
    manifest = _load_manifest()
    pkg_counts, samples = _find_python_imports()
    doc_paths = _find_docs_references()

    print("=== Packaging Manifest Targets ===")
    for file_name, sections in manifest.items():
        print(f"{file_name}:")
        if isinstance(sections, dict):
            for section, value in sections.items():
                if isinstance(value, list):
                    for entry in value:
                        print(
                            f"  - [{section}] {entry['line']} -> "
                            f"{entry['replace_with']}",
                        )
                elif isinstance(value, dict):
                    info = ", ".join(f"{k}={v}" for k, v in value.items())
                    print(f"  - [{section}] {info}")
        else:
            print(f"  - raw: {sections}")
    print()

    print("=== Python Import Counts (pheno.*) ===")
    for top, count in pkg_counts.most_common():
        print(f"{top}: {count} files")
        for sample in samples.get(top, []):
            print(f"    · {sample}")
    print()

    print("=== Documentation References to src/pheno ===")
    for doc in sorted(doc_paths):
        print(f"  - {doc}")
    print()

    print("Next steps:")
    print(
        "  1. Migrate code into the layered `pheno.*` modules per "
        "PHEN_HEXAGONAL_MIGRATION_PLAN.md.",
    )
    print(
        "  2. Use this manifest to update packaging files and run a codemod "
        "for imports.",
    )
    print(
        "  3. Verify with `python tools/generate_phen_codemap.py` after each batch "
        "to ensure counts drop.",
    )


if __name__ == "__main__":
    main()
