#!/usr/bin/env python3
"""Validate kit boundaries to ensure proper separation of concerns.

Prevents circular dependencies and maintains clean architecture.
"""

import ast
import sys
from pathlib import Path


class KitBoundaryValidator(ast.NodeVisitor):
    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.current_kit = self._extract_kit_from_path(file_path)
        self.imports: set[tuple[str, str]] = set()  # (module, alias)
        self.violations: list = []

    def _extract_kit_from_path(self, path: Path) -> str:
        """
        Extract kit name from file path.
        """
        parts = path.parts
        if "src" in parts:
            src_idx = parts.index("src")
            if src_idx + 2 < len(parts):
                return parts[src_idx + 2]  # src/pheno/<kit>
        return "unknown"

    def visit_Import(self, node):
        """
        Handle regular imports.
        """
        for alias in node.names:
            self.imports.add((alias.name, alias.asname))
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        """
        Handle from imports.
        """
        if node.module:
            self.imports.add((node.module, None))
            # Check for cross-kit imports
            if self._is_cross_kit_import(node.module):
                self.violations.append(
                    f"Cross-kit import detected in {self.file_path}: "
                    f"from {node.module} (kit: {self.current_kit})",
                )
                # Check for allowed exceptions
                if not self._is_allowed_cross_kit_import(node.module):
                    self.violations.append(
                        f"  -> Invalid cross-kit import: {node.module} not in allowed list",
                    )
        self.generic_visit(node)

    def _is_cross_kit_import(self, module: str) -> bool:
        """
        Check if import is from another kit.
        """
        if not module.startswith("pheno."):
            return False

        parts = module.split(".")
        if len(parts) < 3:
            return False

        imported_kit = parts[2]  # pheno.<kit>.*
        return imported_kit != self.current_kit

    def _is_allowed_cross_kit_import(self, module: str) -> bool:
        """
        Check if cross-kit import is explicitly allowed.
        """
        # These kits are allowed to import from each other
        allowed_pairs = {
            "auth": ["core"],
            "core": ["auth", "adapters", "auth"],
            "adapters": ["core", "auth"],
        }

        parts = module.split(".")
        if len(parts) < 3:
            return True

        source_kit = self.current_kit
        target_kit = parts[2]

        return target_kit in allowed_pairs.get(source_kit, [])

    def validate(self) -> list:
        """
        Return list of violations.
        """
        return self.violations


def check_file(file_path: Path) -> list:
    """
    Check a single Python file for boundary violations.
    """
    try:
        with open(file_path, encoding="utf-8") as f:
            tree = ast.parse(f.read())
    except (SyntaxError, UnicodeDecodeError) as e:
        return [f"Error parsing {file_path}: {e}"]

    validator = KitBoundaryValidator(file_path)
    validator.visit(tree)
    return validator.validate()


def main():
    if len(sys.argv) < 2:
        print("No files provided for kit boundary validation")
        return 0

    files = [Path(f) for f in sys.argv[1:]]
    all_violations = []

    for file_path in files:
        if not file_path.exists() or not file_path.suffix == ".py":
            continue

        violations = check_file(file_path)
        all_violations.extend(violations)

    if all_violations:
        print("❌ Kit boundary violations found:")
        for violation in all_violations:
            print(f"  - {violation}")
        return 1
    print("✅ No kit boundary violations detected")
    return 0


if __name__ == "__main__":
    sys.exit(main())
