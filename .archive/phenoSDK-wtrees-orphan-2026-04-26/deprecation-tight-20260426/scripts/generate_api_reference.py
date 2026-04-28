#!/usr/bin/env python3
"""Generate API reference documentation from cross-link database.

Automatically generates comprehensive API documentation from module metadata,
including state, specs, examples, and cross-references.

State: STABLE
Since: 0.3.0
Specs: SPEC-DOC-001 (Documentation System)
Tests: scripts/test_generate_api_reference.py
Docs: docs/EXTENDED_CROSS_LINKING.md
Depends_On: scripts/extract_cross_links.py
"""

import ast
import json
from pathlib import Path
from typing import Dict, List, Optional
import re


PROJECT_ROOT = Path(__file__).parent.parent


class APIReferenceGenerator:
    """Generate API reference documentation from codebase."""

    def __init__(self, db_path: Path):
        """Initialize with cross-link database."""
        with open(db_path) as f:
            self.db = json.load(f)

    def extract_module_api(self, module_path: Path) -> Dict:
        """Extract public API from Python module."""
        try:
            with open(module_path) as f:
                content = f.read()

            tree = ast.parse(content)

            api = {
                "classes": [],
                "functions": [],
                "constants": [],
                "exports": [],
            }

            for node in ast.walk(tree):
                # Extract classes
                if isinstance(node, ast.ClassDef) and not node.name.startswith("_"):
                    class_info = {
                        "name": node.name,
                        "docstring": ast.get_docstring(node) or "",
                        "methods": [],
                        "bases": [self._get_name(base) for base in node.bases],
                    }

                    # Extract methods
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef) and not item.name.startswith("_"):
                            method_info = {
                                "name": item.name,
                                "docstring": ast.get_docstring(item) or "",
                                "args": [arg.arg for arg in item.args.args if arg.arg != "self"],
                                "returns": self._get_return_annotation(item),
                            }
                            class_info["methods"].append(method_info)

                    api["classes"].append(class_info)

                # Extract functions
                elif isinstance(node, ast.FunctionDef) and not node.name.startswith("_"):
                    # Skip if it's a method (inside a class)
                    if not any(isinstance(parent, ast.ClassDef) for parent in ast.walk(tree)):
                        func_info = {
                            "name": node.name,
                            "docstring": ast.get_docstring(node) or "",
                            "args": [arg.arg for arg in node.args.args],
                            "returns": self._get_return_annotation(node),
                        }
                        api["functions"].append(func_info)

                # Extract constants (module-level assignments)
                elif isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name) and target.id.isupper():
                            api["constants"].append({
                                "name": target.id,
                                "value": ast.unparse(node.value) if hasattr(ast, "unparse") else str(node.value),
                            })

            # Extract __all__ exports
            for node in tree.body:
                if isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name) and target.id == "__all__":
                            if isinstance(node.value, ast.List):
                                api["exports"] = [
                                    elt.s if isinstance(elt, ast.Str) else elt.value
                                    for elt in node.value.elts
                                    if isinstance(elt, (ast.Str, ast.Constant))
                                ]

            return api

        except Exception as e:
            print(f"Error extracting API from {module_path}: {e}")
            return {"classes": [], "functions": [], "constants": [], "exports": []}

    def _get_name(self, node):
        """Get name from AST node."""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self._get_name(node.value)}.{node.attr}"
        else:
            return ""

    def _get_return_annotation(self, func_node):
        """Get return type annotation."""
        if func_node.returns:
            return ast.unparse(func_node.returns) if hasattr(ast, "unparse") else ""
        return None

    def generate_module_reference(self, module_id: str, module_meta: Dict) -> str:
        """Generate API reference for a single module."""
        lines = []

        # Module header
        module_name = module_id.replace("src/pheno/", "pheno.").replace("/__init__.py", "").replace("/", ".")
        lines.extend([
            f"## `{module_name}`",
            "",
        ])

        # Metadata
        links = module_meta.get("links", {})
        state = links.get("state", "UNKNOWN")
        since = links.get("since", "N/A")

        state_emoji = {
            "STABLE": "✅",
            "IN_PROGRESS": "🔵",
            "EXPERIMENTAL": "🧪",
            "DEPRECATED": "⚠️",
            "ARCHIVED": "📦",
        }.get(state, "❓")

        lines.extend([
            f"**State**: {state_emoji} {state}",
            f"**Since**: v{since}",
            "",
        ])

        # Description from docstring
        module_path = PROJECT_ROOT / module_id
        if module_path.exists():
            with open(module_path) as f:
                content = f.read()
            tree = ast.parse(content)
            docstring = ast.get_docstring(tree)
            if docstring:
                # Extract first paragraph (before metadata)
                first_para = docstring.split("\n\n")[0].strip()
                # Remove metadata lines
                desc_lines = [line for line in first_para.split("\n") if not line.startswith(("State:", "Since:", "Specs:", "Stories:", "Tests:", "Docs:"))]
                if desc_lines:
                    lines.extend([
                        " ".join(desc_lines),
                        "",
                    ])

        # Cross-references
        if links.get("specs"):
            lines.append(f"**Specifications**: {', '.join(links['specs'])}")
        if links.get("stories"):
            lines.append(f"**User Stories**: {', '.join(links['stories'])}")
        if links.get("tests"):
            test_refs = links["tests"] if isinstance(links["tests"], list) else [links["tests"]]
            lines.append(f"**Tests**: {', '.join(test_refs)}")
        if links.get("docs"):
            doc_refs = links["docs"] if isinstance(links["docs"], list) else [links["docs"]]
            lines.append(f"**Documentation**: {', '.join(doc_refs)}")

        lines.append("")

        # Extract API
        if module_path.exists():
            api = self.extract_module_api(module_path)

            # Classes
            if api["classes"]:
                lines.extend(["### Classes", ""])
                for cls in api["classes"]:
                    lines.extend([
                        f"#### `{cls['name']}`",
                        "",
                    ])

                    if cls["bases"]:
                        lines.append(f"**Inherits**: {', '.join(cls['bases'])}")
                        lines.append("")

                    if cls["docstring"]:
                        first_line = cls["docstring"].split("\n")[0]
                        lines.append(first_line)
                        lines.append("")

                    if cls["methods"]:
                        lines.append("**Methods**:")
                        lines.append("")
                        for method in cls["methods"]:
                            args_str = ", ".join(method["args"])
                            returns_str = f" -> {method['returns']}" if method["returns"] else ""
                            lines.append(f"- `{method['name']}({args_str}){returns_str}`")
                            if method["docstring"]:
                                first_line = method["docstring"].split("\n")[0]
                                lines.append(f"  - {first_line}")
                        lines.append("")

            # Functions
            if api["functions"]:
                lines.extend(["### Functions", ""])
                for func in api["functions"]:
                    args_str = ", ".join(func["args"])
                    returns_str = f" -> {func['returns']}" if func["returns"] else ""
                    lines.append(f"#### `{func['name']}({args_str}){returns_str}`")
                    lines.append("")

                    if func["docstring"]:
                        first_para = func["docstring"].split("\n\n")[0]
                        lines.append(first_para)
                        lines.append("")

            # Constants
            if api["constants"]:
                lines.extend(["### Constants", ""])
                for const in api["constants"]:
                    lines.append(f"- `{const['name']}` = `{const['value']}`")
                lines.append("")

            # Exports
            if api["exports"]:
                lines.extend([
                    "### Exported Names",
                    "",
                    f"`__all__` = `{api['exports']}`",
                    "",
                ])

        lines.append("---")
        lines.append("")

        return "\n".join(lines)

    def generate_api_reference_doc(self, output_path: Path):
        """Generate complete API reference documentation."""
        lines = [
            "# API Reference",
            "",
            "**Auto-generated** from module metadata and cross-links.",
            "",
            "---",
            "",
            "## Table of Contents",
            "",
        ]

        # Build TOC by top-level module
        modules_by_package = {}
        for module_id in sorted(self.db["modules"].keys()):
            package = module_id.split("/")[2]  # Extract pheno.XXX
            if package not in modules_by_package:
                modules_by_package[package] = []
            modules_by_package[package].append(module_id)

        for package in sorted(modules_by_package.keys()):
            lines.append(f"- [{package}](#{package})")

        lines.extend(["", "---", ""])

        # Generate reference for each module
        for package in sorted(modules_by_package.keys()):
            lines.extend([
                f"# {package}",
                "",
            ])

            for module_id in sorted(modules_by_package[package]):
                module_meta = self.db["modules"][module_id]
                lines.append(self.generate_module_reference(module_id, module_meta))

        # Write documentation
        with open(output_path, "w") as f:
            f.write("\n".join(lines))

        print(f"  ✓ API reference saved to: {output_path}")


def main():
    """Generate API reference documentation."""
    print("=" * 70)
    print("Generating API Reference Documentation")
    print("=" * 70)
    print()

    # Load cross-link database
    db_path = PROJECT_ROOT / "docs" / "cross_links.json"
    if not db_path.exists():
        print(f"❌ Cross-link database not found: {db_path}")
        print("   Run: python scripts/extract_cross_links.py")
        return

    generator = APIReferenceGenerator(db_path)

    # Generate documentation
    print("Generating API reference...")
    output = PROJECT_ROOT / "docs" / "API_REFERENCE.md"
    generator.generate_api_reference_doc(output)

    print()
    print("=" * 70)
    print("Summary")
    print("=" * 70)
    print(f"  Output: {output}")
    print(f"  Modules documented: {len(generator.db['modules'])}")
    print()
    print("✅ API reference generation complete!")
    print()
    print("Next steps:")
    print("  1. Review: cat docs/API_REFERENCE.md")
    print("  2. Publish: Copy to apps/docs/content/docs/api/")
    print("  3. Update: Add to navigation")


if __name__ == "__main__":
    main()
