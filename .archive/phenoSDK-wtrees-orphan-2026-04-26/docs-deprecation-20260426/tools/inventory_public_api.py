#!/usr/bin/env python3
"""Public API Inventory Tool for Pheno-SDK.

Scans kit __init__.py files and collects exported symbols to build a public API
inventory. This helps ensure we preserve API compatibility during consolidation.
"""

import ast
import json
from pathlib import Path
from typing import Any

ROOT = Path("/Users/kooshapari/temp-PRODVERCEL/485/kush/pheno-sdk")


def find_init_files(root: Path) -> list[Path]:
    inits: list[Path] = []
    for p in root.rglob("__init__.py"):
        # Skip virtual envs and build artifacts
        if any(
            seg in p.parts for seg in [".venv", "venv", "build", "dist", "__pycache__", ".egg-info"]
        ):
            continue
        # Only include paths that appear to be kits or their packages
        if any(
            seg.endswith("-kit") or seg.endswith("_kit") or seg in ("pydevkit", "authkit-client")
            for seg in p.parts
        ):
            inits.append(p)
    return inits


def extract_exports(init_path: Path) -> dict[str, Any]:
    data: dict[str, Any] = {
        "path": str(init_path),
        "module": ".".join(init_path.with_suffix("").parts[-4:]),
        "all": [],
        "imports": [],
        "names": [],
        "version": None,
    }
    try:
        src = init_path.read_text()
        tree = ast.parse(src)
        for node in tree.body:
            if isinstance(node, ast.Assign):
                # __all__ collection
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == "__all__":
                        if isinstance(node.value, (ast.List, ast.Tuple)):
                            data["all"] = [
                                elt.s for elt in node.value.elts if isinstance(elt, ast.Str)
                            ]
                # __version__ capture
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == "__version__":
                        if isinstance(node.value, ast.Str):
                            data["version"] = node.value.s
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                names = [alias.name for alias in node.names]
                data["imports"].append({"from": module, "names": names})
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                if not node.name.startswith("_"):
                    data["names"].append(node.name)
    except Exception as e:
        data["error"] = str(e)
    return data


def build_inventory() -> dict[str, Any]:
    result: dict[str, Any] = {
        "kits": {},
        "summary": {},
    }
    inits = find_init_files(ROOT)
    for init in inits:
        kit_dir = None
        for part in init.parts:
            if (
                part.endswith("-kit")
                or part.endswith("_kit")
                or part in ("pydevkit", "authkit-client")
            ):
                kit_dir = part
        kit_key = kit_dir or "unknown"
        result["kits"].setdefault(kit_key, []).append(extract_exports(init))

    # Summary counts
    total_symbols = 0
    per_kit_counts: dict[str, int] = {}
    for kit, entries in result["kits"].items():
        count = 0
        for entry in entries:
            count += len(entry.get("all", [])) or len(entry.get("names", []))
        per_kit_counts[kit] = count
        total_symbols += count

    result["summary"] = {
        "total_kits": len(result["kits"]),
        "total_symbols": total_symbols,
        "per_kit_export_counts": per_kit_counts,
    }
    return result


def main():
    inv = build_inventory()
    out = ROOT / "tools" / "public_api_inventory.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(inv, indent=2))
    print(f"✅ Public API inventory written to: {out}")
    print(f"📊 Kits indexed: {inv['summary']['total_kits']}")


if __name__ == "__main__":
    main()
