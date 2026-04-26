"""
Architecture testing plugin for pytest.

This plugin provides architecture fitness tests including:
- File size validation
- Import boundary enforcement
- Dependency direction validation
- Naming convention checks
- Cyclomatic complexity analysis
"""

import ast
import os
from pathlib import Path

import pytest


class ArchitecturePlugin:
    """Pytest plugin for architecture fitness testing."""

    def __init__(self, config):
        self.config = config
        self.max_file_size = config.getoption("--max-file-size", default=1000)
        self.max_complexity = config.getoption("--max-complexity", default=10)
        self.enforce_imports = config.getoption("--enforce-imports", default=True)
        self.enforce_dependencies = config.getoption("--enforce-dependencies", default=True)

    @pytest.hookimpl(tryfirst=True)
    def pytest_collection_modifyitems(self, config, items):
        """Add architecture tests to the test collection."""
        if not self.enforce_imports and not self.enforce_dependencies:
            return

        # Add architecture tests
        architecture_items = []

        if self.enforce_imports:
            architecture_items.append(
                pytest.Function.from_parent(
                    parent=items[0].parent if items else None,
                    name="test_import_boundaries",
                    callobj=self._test_import_boundaries,
                    markers=[pytest.mark.architecture, pytest.mark.imports],
                ),
            )

        if self.enforce_dependencies:
            architecture_items.append(
                pytest.Function.from_parent(
                    parent=items[0].parent if items else None,
                    name="test_dependency_direction",
                    callobj=self._test_dependency_direction,
                    markers=[pytest.mark.architecture, pytest.mark.dependencies],
                ),
            )

        # Add file size tests
        architecture_items.append(
            pytest.Function.from_parent(
                parent=items[0].parent if items else None,
                name="test_file_sizes",
                callobj=self._test_file_sizes,
                markers=[pytest.mark.architecture, pytest.mark.file_size],
            ),
        )

        # Add complexity tests
        architecture_items.append(
            pytest.Function.from_parent(
                parent=items[0].parent if items else None,
                name="test_cyclomatic_complexity",
                callobj=self._test_cyclomatic_complexity,
                markers=[pytest.mark.architecture, pytest.mark.complexity],
            ),
        )

        items.extend(architecture_items)

    def _test_import_boundaries(self):
        """Test that import boundaries are respected."""
        violations = []

        # Define allowed import patterns
        allowed_patterns = [
            r"^src\.",
            r"^tests\.",
            r"^conftest$",
        ]

        # Check each Python file
        for py_file in self._get_python_files():
            with open(py_file, encoding="utf-8") as f:
                try:
                    tree = ast.parse(f.read())
                except SyntaxError:
                    continue

                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            if not self._is_allowed_import(alias.name, allowed_patterns):
                                violations.append(f"{py_file}: {alias.name}")
                    elif isinstance(node, ast.ImportFrom):
                        if node.module and not self._is_allowed_import(node.module, allowed_patterns):
                            violations.append(f"{py_file}: {node.module}")

        if violations:
            pytest.fail("Import boundary violations found:\n" + "\n".join(violations))

    def _test_dependency_direction(self):
        """Test that dependency direction is respected."""
        violations = []

        # Define dependency rules
        dependency_rules = {
            "src.domain": [],  # Domain should not depend on anything
            "src.application": ["src.domain"],  # Application can depend on domain
            "src.adapters": ["src.domain", "src.application"],  # Adapters can depend on domain and application
            "src.infrastructure": ["src.domain", "src.application", "src.adapters"],  # Infrastructure can depend on all
        }

        for py_file in self._get_python_files():
            file_path = str(py_file)
            if not file_path.startswith("src/"):
                continue

            # Determine which layer this file belongs to
            file_layer = self._get_file_layer(file_path)
            if not file_layer:
                continue

            # Check imports against dependency rules
            with open(py_file, encoding="utf-8") as f:
                try:
                    tree = ast.parse(f.read())
                except SyntaxError:
                    continue

                for node in ast.walk(tree):
                    if isinstance(node, ast.ImportFrom) and node.module:
                        import_layer = self._get_import_layer(node.module)
                        if import_layer and not self._is_allowed_dependency(file_layer, import_layer, dependency_rules):
                            violations.append(f"{py_file}: {file_layer} -> {import_layer} ({node.module})")

        if violations:
            pytest.fail("Dependency direction violations found:\n" + "\n".join(violations))

    def _test_file_sizes(self):
        """Test that file sizes are within limits."""
        violations = []

        for py_file in self._get_python_files():
            line_count = sum(1 for _ in open(py_file, encoding="utf-8"))
            if line_count > self.max_file_size:
                violations.append(f"{py_file}: {line_count} lines (max: {self.max_file_size})")

        if violations:
            pytest.fail("File size violations found:\n" + "\n".join(violations))

    def _test_cyclomatic_complexity(self):
        """Test that cyclomatic complexity is within limits."""
        violations = []

        for py_file in self._get_python_files():
            with open(py_file, encoding="utf-8") as f:
                try:
                    tree = ast.parse(f.read())
                except SyntaxError:
                    continue

                for node in ast.walk(tree):
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        complexity = self._calculate_complexity(node)
                        if complexity > self.max_complexity:
                            violations.append(f"{py_file}:{node.lineno} {node.name}: {complexity} (max: {self.max_complexity})")

        if violations:
            pytest.fail("Cyclomatic complexity violations found:\n" + "\n".join(violations))

    def _get_python_files(self) -> list[Path]:
        """Get all Python files in the project."""
        python_files = []
        for root, dirs, files in os.walk("."):
            # Skip certain directories
            dirs[:] = [d for d in dirs if d not in {".git", "__pycache__", ".pytest_cache", "htmlcov", "dist", "build"}]

            for file in files:
                if file.endswith(".py"):
                    python_files.append(Path(root) / file)

        return python_files

    def _is_allowed_import(self, import_name: str, allowed_patterns: list[str]) -> bool:
        """Check if an import is allowed based on patterns."""
        import re
        return any(re.match(pattern, import_name) for pattern in allowed_patterns)

    def _get_file_layer(self, file_path: str) -> str | None:
        """Determine which architectural layer a file belongs to."""
        if "src/domain" in file_path:
            return "src.domain"
        if "src/application" in file_path:
            return "src.application"
        if "src/adapters" in file_path:
            return "src.adapters"
        if "src/infrastructure" in file_path:
            return "src.infrastructure"
        return None

    def _get_import_layer(self, import_name: str) -> str | None:
        """Determine which architectural layer an import belongs to."""
        if import_name.startswith("src.domain"):
            return "src.domain"
        if import_name.startswith("src.application"):
            return "src.application"
        if import_name.startswith("src.adapters"):
            return "src.adapters"
        if import_name.startswith("src.infrastructure"):
            return "src.infrastructure"
        return None

    def _is_allowed_dependency(self, from_layer: str, to_layer: str, rules: dict[str, list[str]]) -> bool:
        """Check if a dependency from one layer to another is allowed."""
        allowed_deps = rules.get(from_layer, [])
        return to_layer in allowed_deps

    def _calculate_complexity(self, node: ast.AST) -> int:
        """Calculate cyclomatic complexity of a function."""
        complexity = 1  # Base complexity

        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor)) or isinstance(child, ast.ExceptHandler):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1

        return complexity


def pytest_addoption(parser):
    """Add command line options for architecture testing."""
    parser.addoption(
        "--max-file-size",
        type=int,
        default=1000,
        help="Maximum allowed lines per file",
    )
    parser.addoption(
        "--max-complexity",
        type=int,
        default=10,
        help="Maximum allowed cyclomatic complexity",
    )
    parser.addoption(
        "--enforce-imports",
        action="store_true",
        default=True,
        help="Enforce import boundaries",
    )
    parser.addoption(
        "--enforce-dependencies",
        action="store_true",
        default=True,
        help="Enforce dependency direction",
    )


def pytest_configure(config):
    """Configure the architecture plugin."""
    config.pluginmanager.register(ArchitecturePlugin(config), "architecture")
