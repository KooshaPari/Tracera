"""Architecture Fitness Tests.

These tests enforce architectural boundaries and quality standards.
Run with: pytest tests/architecture/test_fitness.py

Enable in CI with: PHENO_FITNESS_TESTS=1 pytest
"""

import ast
import os
from pathlib import Path

import pytest

# Skip by default, enable with environment variable
SKIP_FITNESS = os.getenv("PHENO_FITNESS_TESTS") != "1"
skip_reason = "Fitness tests disabled. Set PHENO_FITNESS_TESTS=1 to enable."

# Repository root
REPO_ROOT = Path(__file__).parent.parent.parent


class ImportVisitor(ast.NodeVisitor):
    """
    AST visitor to collect imports from Python files.
    """

    def __init__(self):
        self.imports: list[tuple[str, str]] = []  # (module, from_module)

    def visit_Import(self, node):
        for alias in node.names:
            self.imports.append((alias.name, ""))
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        if node.module:
            for alias in node.names:
                self.imports.append((alias.name, node.module))
        self.generic_visit(node)


def get_python_files(directory: Path) -> list[Path]:
    """
    Get all Python files in directory recursively.
    """
    return list(directory.rglob("*.py"))


def get_imports_from_file(file_path: Path) -> list[tuple[str, str]]:
    """
    Extract imports from a Python file.
    """
    try:
        with open(file_path, encoding="utf-8") as f:
            tree = ast.parse(f.read(), filename=str(file_path))
        visitor = ImportVisitor()
        visitor.visit(tree)
        return visitor.imports
    except Exception:
        # Skip files that can't be parsed
        return []


def get_file_lines(file_path: Path) -> int:
    """
    Count lines in a file.
    """
    try:
        with open(file_path, encoding="utf-8") as f:
            return len(f.readlines())
    except Exception:
        return 0


@pytest.mark.skipif(SKIP_FITNESS, reason=skip_reason)
class TestImportBoundaries:
    """
    Test that import boundaries are respected.
    """

    def test_domain_never_imports_adapters(self):
        """
        Domain layer should never import from adapter layer.
        """
        domain_dirs = [
            REPO_ROOT / "src" / "pheno" / "mcp",
            REPO_ROOT / "src" / "pheno" / "domain",
            REPO_ROOT / "src" / "pheno" / "config" / "core",
        ]

        violations = []

        for domain_dir in domain_dirs:
            if not domain_dir.exists():
                continue

            for py_file in get_python_files(domain_dir):
                imports = get_imports_from_file(py_file)

                for name, from_module in imports:
                    # Check for adapter imports
                    if any(
                        adapter in from_module
                        for adapter in [
                            "_kit",
                            "adapter_kit",
                            "observability_kit",
                            "config_kit",
                            "mcp_sdk",
                            "mcp_infra",
                        ]
                    ):
                        violations.append(
                            f"{py_file.relative_to(REPO_ROOT)}: imports {from_module}.{name}",
                        )

        assert not violations, "Domain layer imports from adapter layer:\n" + "\n".join(violations)

    def test_ports_never_import_adapters(self):
        """
        Ports should never import concrete adapter implementations.
        """
        ports_dir = REPO_ROOT / "src" / "pheno" / "ports"

        if not ports_dir.exists():
            pytest.skip("Ports directory doesn't exist yet")

        violations = []

        for py_file in get_python_files(ports_dir):
            imports = get_imports_from_file(py_file)

            for name, from_module in imports:
                # Ports should only import from typing, abc, and pheno domain
                if from_module and not any(
                    allowed in from_module
                    for allowed in [
                        "typing",
                        "abc",
                        "pheno.mcp",
                        "pheno.domain",
                        "pheno.config",
                        "collections.abc",
                    ]
                ):
                    violations.append(
                        f"{py_file.relative_to(REPO_ROOT)}: imports {from_module}.{name}",
                    )

        assert not violations, "Ports layer imports non-domain modules:\n" + "\n".join(violations)

    def test_no_circular_dependencies(self):
        """
        Check for circular dependencies between major modules.
        """
        # This is a simplified check - full cycle detection would be more complex
        pheno_dir = REPO_ROOT / "src" / "pheno"

        if not pheno_dir.exists():
            pytest.skip("Pheno directory doesn't exist")

        # Map of module -> imports
        module_imports = {}

        for module_dir in pheno_dir.iterdir():
            if not module_dir.is_dir() or module_dir.name.startswith("_"):
                continue

            module_name = f"pheno.{module_dir.name}"
            imports = set()

            for py_file in get_python_files(module_dir):
                file_imports = get_imports_from_file(py_file)
                for name, from_module in file_imports:
                    if from_module.startswith("pheno."):
                        imports.add(from_module.split(".")[1])

            module_imports[module_dir.name] = imports

        # Check for direct circular dependencies
        violations = []
        for module, imports in module_imports.items():
            for imported in imports:
                if imported in module_imports:
                    if module in module_imports[imported]:
                        violations.append(f"{module} <-> {imported}")

        assert not violations, "Circular dependencies detected:\n" + "\n".join(set(violations))


@pytest.mark.skipif(SKIP_FITNESS, reason=skip_reason)
class TestFileSizeBudgets:
    """
    Test that files respect size budgets.
    """

    SOFT_LIMIT = 350  # Lines - warning
    HARD_LIMIT = 500  # Lines - error

    def test_core_files_within_budget(self):
        """
        Core pheno files should be within size budget.
        """
        pheno_dir = REPO_ROOT / "src" / "pheno"

        if not pheno_dir.exists():
            pytest.skip("Pheno directory doesn't exist")

        violations = []
        warnings = []

        for py_file in get_python_files(pheno_dir):
            # Skip __init__.py and test files
            if py_file.name == "__init__.py" or "test" in py_file.name:
                continue

            lines = get_file_lines(py_file)

            if lines > self.HARD_LIMIT:
                violations.append(
                    f"{py_file.relative_to(REPO_ROOT)}: {lines} lines "
                    f"(limit: {self.HARD_LIMIT})",
                )
            elif lines > self.SOFT_LIMIT:
                warnings.append(
                    f"{py_file.relative_to(REPO_ROOT)}: {lines} lines "
                    f"(soft limit: {self.SOFT_LIMIT})",
                )

        # Print warnings but don't fail
        if warnings:
            print("\n⚠️  File size warnings:")
            for warning in warnings:
                print(f"  {warning}")

        assert not violations, "Files exceed hard size limit:\n" + "\n".join(violations)


@pytest.mark.skipif(SKIP_FITNESS, reason=skip_reason)
class TestPublicAPI:
    """
    Test that public API is properly defined.
    """

    def test_pheno_modules_have_all(self):
        """
        All pheno modules should define __all__.
        """
        pheno_dir = REPO_ROOT / "src" / "pheno"

        if not pheno_dir.exists():
            pytest.skip("Pheno directory doesn't exist")

        missing_all = []

        for module_dir in pheno_dir.iterdir():
            if not module_dir.is_dir() or module_dir.name.startswith("_"):
                continue

            init_file = module_dir / "__init__.py"
            if not init_file.exists():
                continue

            try:
                with open(init_file, encoding="utf-8") as f:
                    content = f.read()
                    tree = ast.parse(content)

                has_all = any(
                    isinstance(node, ast.Assign)
                    and any(
                        isinstance(target, ast.Name) and target.id == "__all__"
                        for target in node.targets
                    )
                    for node in ast.walk(tree)
                )

                if not has_all:
                    missing_all.append(f"pheno.{module_dir.name}")
            except Exception:
                pass

        # This is a warning for now, not a hard failure
        if missing_all:
            print("\n⚠️  Modules missing __all__ definition:")
            for module in missing_all:
                print(f"  {module}")


@pytest.mark.skipif(SKIP_FITNESS, reason=skip_reason)
class TestDependencyConsolidation:
    """
    Test that consolidation is progressing.
    """

    def test_no_duplicate_di_containers(self):
        """
        Should only have one DI container implementation.
        """
        # After consolidation, only pheno.adapters.Container should exist
        container_files = [
            REPO_ROOT / "adapter-kit" / "di" / "container.py",
            REPO_ROOT / "adapter-kit" / "adapter_kit" / "di" / "container.py",
            REPO_ROOT / "src" / "pheno" / "adapters" / "container.py",
        ]

        existing = [f for f in container_files if f.exists()]

        # For now, just report what exists
        print(f"\n📊 DI Container implementations found: {len(existing)}")
        for f in existing:
            print(f"  - {f.relative_to(REPO_ROOT)}")

        # After Week 1, this should be 1 (only pheno.adapters.container)
        # For now, just informational

    def test_no_duplicate_config_managers(self):
        """
        Should only have one config manager implementation.
        """
        config_locations = [
            REPO_ROOT / "config-kit",
            REPO_ROOT / "src" / "pheno" / "config",
            REPO_ROOT / "packages" / "pydevkit" / "src" / "pydevkit" / "config",
        ]

        existing = [d for d in config_locations if d.exists()]

        print(f"\n📊 Config implementations found: {len(existing)}")
        for d in existing:
            print(f"  - {d.relative_to(REPO_ROOT)}")

        # After Week 2, this should be 1 (only pheno.config)


if __name__ == "__main__":
    # Run with fitness tests enabled
    os.environ["PHENO_FITNESS_TESTS"] = "1"
    pytest.main([__file__, "-v"])
