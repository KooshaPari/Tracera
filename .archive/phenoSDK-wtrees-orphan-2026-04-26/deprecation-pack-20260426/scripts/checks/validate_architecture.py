#!/usr/bin/env python3
"""Validate architecture compliance for Python files.

Ensures hexagonal architecture and modular design principles.
"""

import ast
import sys
from pathlib import Path


class ArchitectureValidator(ast.NodeVisitor):
    """
    Validates architectural patterns in Python code.
    """

    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.violations: list[str] = []
        self.current_class = None
        self.classes: dict[str, dict] = {}

    def visit_ClassDef(self, node):
        """
        Analyze class definitions.
        """
        self.current_class = node.name
        self.classes[node.name] = {
            "methods": [],
            "bases": [base.id for base in node.bases if isinstance(base, ast.Name)],
            "decorators": [
                d.id if isinstance(d, ast.Name) else str(d) for d in node.decorator_list
            ],
            "line": node.lineno,
        }
        self.generic_visit(node)
        self.current_class = None

    def visit_FunctionDef(self, node):
        """
        Analyze function definitions.
        """
        if self.current_class:
            self.classes[self.current_class]["methods"].append(node.name)

        # Check for architectural violations
        if self._has_direct_infrastructure_calls(node):
            self.violations.append(
                f"Direct infrastructure call in {node.name} "
                f"at line {node.lineno} - should use adapter pattern",
            )

        self.generic_visit(node)

    def _has_direct_infrastructure_calls(self, node) -> bool:
        """
        Check for direct database, HTTP, or infrastructure calls.
        """
        infrastructure_modules = {
            "sqlite3",
            "psycopg2",
            "asyncpg",
            "requests",
            "httpx",
            "urllib",
            "socket",
            "subprocess",
            "os.system",
        }

        for child in ast.walk(node):
            if isinstance(child, ast.Call) and isinstance(child.func, (ast.Attribute, ast.Name)):
                if isinstance(child.func, ast.Attribute):
                    if child.func.attr in ["connect", "execute", "query", "request"]:
                        return True
                elif isinstance(child.func, ast.Name):
                    if child.func.id in infrastructure_modules:
                        return True
        return False

    def validate_naming_conventions(self):
        """
        Validate naming conventions.
        """
        if not self.current_class:
            return

        class_name = self.current_class
        # Interface classes should start with 'I'
        if any(
            base in ["Interface", "ABC", "Protocol"] for base in self.classes[class_name]["bases"]
        ):
            if not class_name.startswith("I") and not class_name.endswith("Interface"):
                self.violations.append(
                    f"Interface class {class_name} should start with 'I' or end with 'Interface'",
                )

        # Implementation classes should not end with 'Interface'
        if class_name.endswith("Interface") and not any(
            base in ["Interface", "ABC", "Protocol"] for base in self.classes[class_name]["bases"]
        ):
            self.violations.append(
                f"Non-interface class {class_name} should not end with 'Interface'",
            )

    def validate_class_responsibility(self):
        """
        Validate Single Responsibility Principle.
        """
        if not self.current_class:
            return

        class_name = self.current_class
        methods = self.classes[class_name]["methods"]

        # Check for too many methods (potential god class)
        if len(methods) > 15:
            self.violations.append(
                f"Class {class_name} has {len(methods)} methods - consider splitting",
            )

        # Check for mixed responsibilities
        method_prefixes = [m.split("_")[0] for m in methods if "_" in m]
        unique_prefixes = set(method_prefixes)
        if len(unique_prefixes) > 5:
            self.violations.append(
                f"Class {class_name} may have mixed responsibilities "
                f"(found {len(unique_prefixes)} different method prefixes)",
            )


def check_file(file_path: Path) -> list[str]:
    """
    Check a single Python file for architectural violations.
    """
    try:
        with open(file_path, encoding="utf-8") as f:
            tree = ast.parse(f.read())
    except (SyntaxError, UnicodeDecodeError) as e:
        return [f"Error parsing {file_path}: {e}"]

    validator = ArchitectureValidator(file_path)
    validator.visit(tree)

    # Additional validations after AST traversal
    if validator.classes:
        for class_name in validator.classes:
            validator.current_class = class_name
            validator.validate_naming_conventions()
            validator.validate_class_responsibility()

    return validator.violations


def main():
    if len(sys.argv) < 2:
        print("No files provided for architecture validation")
        return 0

    files = [Path(f) for f in sys.argv[1:]]
    all_violations = []

    for file_path in files:
        if not file_path.exists() or not file_path.suffix == ".py":
            continue

        violations = check_file(file_path)
        if violations:
            all_violations.append((file_path, violations))

    if not all_violations:
        print("✅ No architecture violations detected")
        return 0

    print("❌ Architecture violations found:")
    for file_path, violations in all_violations:
        print(f"\n📄 {file_path}:")
        for violation in violations:
            print(f"  - {violation}")

    total_violations = sum(len(violations) for _, violations in all_violations)
    print(f"\n❌ Found {total_violations} architecture violation(s)")
    return 1


if __name__ == "__main__":
    sys.exit(main())
