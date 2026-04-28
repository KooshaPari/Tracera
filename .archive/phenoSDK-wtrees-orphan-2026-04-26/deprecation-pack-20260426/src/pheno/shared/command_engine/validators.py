"""Project Validators.

Provides validation capabilities for project structure, dependencies, and configuration
to ensure commands can execute successfully.
"""

import logging
import subprocess
from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class ValidationStatus(Enum):
    """
    Status of validation.
    """

    PASSED = "passed"
    FAILED = "failed"
    WARNING = "warning"
    SKIPPED = "skipped"


@dataclass
class ValidationResult:
    """
    Result of a validation check.
    """

    name: str
    status: ValidationStatus
    message: str
    details: dict[str, Any] | None = None
    fix_suggestion: str | None = None

    @property
    def is_valid(self) -> bool:
        """
        Check if validation passed.
        """
        return self.status == ValidationStatus.PASSED


class ProjectValidator:
    """Validates project structure and configuration.

    Provides comprehensive validation for different project types to ensure commands can
    execute successfully.
    """

    def __init__(self):
        self._validators: dict[str, Callable[[Path], ValidationResult]] = {}

    def register_validator(self, name: str, validator: Callable[[Path], ValidationResult]) -> None:
        """
        Register a custom validator.
        """
        self._validators[name] = validator

    async def validate_project(
        self, project_path: Path, project_type: str, validators: list[str] | None = None,
    ) -> list[ValidationResult]:
        """Validate a project.

        Args:
            project_path: Path to project directory
            project_type: Type of project (python, node, etc.)
            validators: List of validator names to run (default: all)

        Returns:
            List of validation results
        """
        results = []

        # Get validators to run
        validators_to_run = validators or list(self._validators.keys())

        # Add type-specific validators
        type_validators = self._get_type_validators(project_type)
        validators_to_run.extend(type_validators)

        # Run validators
        for validator_name in validators_to_run:
            try:
                if validator_name in self._validators:
                    result = self._validators[validator_name](project_path)
                else:
                    result = self._run_builtin_validator(validator_name, project_path, project_type)

                results.append(result)

            except Exception as e:
                logger.exception(f"Validator '{validator_name}' failed: {e}")
                results.append(
                    ValidationResult(
                        name=validator_name,
                        status=ValidationStatus.FAILED,
                        message=f"Validator failed: {e}",
                        details={"error": str(e)},
                    ),
                )

        return results

    def _get_type_validators(self, project_type: str) -> list[str]:
        """
        Get validators specific to project type.
        """
        type_validators = {
            "python": [
                "python_structure",
                "python_dependencies",
                "python_imports",
            ],
            "node": [
                "node_structure",
                "node_dependencies",
                "node_scripts",
            ],
            "rust": [
                "rust_structure",
                "rust_dependencies",
            ],
            "go": [
                "go_structure",
                "go_modules",
            ],
        }

        return type_validators.get(project_type, [])

    def _run_builtin_validator(
        self, name: str, project_path: Path, project_type: str,
    ) -> ValidationResult:
        """
        Run a built-in validator.
        """
        validator_map = self._get_validator_map()

        if name in validator_map:
            return validator_map[name](project_path)
        return self._create_unknown_validator_result(name)

    def _get_validator_map(self) -> dict[str, callable]:
        """
        Get mapping of validator names to their methods.
        """
        return {
            "python_structure": self._validate_python_structure,
            "python_dependencies": self._validate_python_dependencies,
            "python_imports": self._validate_python_imports,
            "node_structure": self._validate_node_structure,
            "node_dependencies": self._validate_node_dependencies,
            "node_scripts": self._validate_node_scripts,
            "rust_structure": self._validate_rust_structure,
            "rust_dependencies": self._validate_rust_dependencies,
            "go_structure": self._validate_go_structure,
            "go_modules": self._validate_go_modules,
        }

    def _create_unknown_validator_result(self, name: str) -> ValidationResult:
        """
        Create a result for unknown validators.
        """
        return ValidationResult(
            name=name, status=ValidationStatus.SKIPPED, message=f"Unknown validator: {name}",
        )

    def _validate_python_structure(self, project_path: Path) -> ValidationResult:
        """
        Validate Python project structure.
        """
        required_files = ["pyproject.toml", "setup.py", "setup.cfg"]
        has_required = any((project_path / f).exists() for f in required_files)

        if not has_required:
            return ValidationResult(
                name="python_structure",
                status=ValidationStatus.FAILED,
                message="No Python project configuration found",
                fix_suggestion="Create pyproject.toml, setup.py, or setup.cfg",
            )

        # Check for source directory
        src_dirs = ["src", "lib", project_path.name]
        has_src = any((project_path / d).is_dir() for d in src_dirs)

        if not has_src:
            return ValidationResult(
                name="python_structure",
                status=ValidationStatus.WARNING,
                message="No source directory found",
                fix_suggestion="Create a src/ directory or place modules in project root",
            )

        return ValidationResult(
            name="python_structure",
            status=ValidationStatus.PASSED,
            message="Python project structure is valid",
        )

    def _validate_python_dependencies(self, project_path: Path) -> ValidationResult:
        """
        Validate Python dependencies.
        """
        try:
            # Check if pip is available
            subprocess.run(["pip", "--version"], check=True, capture_output=True)

            # Check if requirements.txt exists
            req_file = project_path / "requirements.txt"
            if req_file.exists():
                return ValidationResult(
                    name="python_dependencies",
                    status=ValidationStatus.PASSED,
                    message="Python dependencies configuration found",
                )
            return ValidationResult(
                name="python_dependencies",
                status=ValidationStatus.WARNING,
                message="No requirements.txt found",
                fix_suggestion="Create requirements.txt or use pyproject.toml for dependencies",
            )

        except (subprocess.CalledProcessError, FileNotFoundError):
            return ValidationResult(
                name="python_dependencies",
                status=ValidationStatus.FAILED,
                message="pip not available",
                fix_suggestion="Install pip or use a Python environment with pip",
            )

    def _validate_python_imports(self, project_path: Path) -> ValidationResult:
        """
        Validate Python imports.
        """
        try:
            # Find Python files
            python_files = list(project_path.rglob("*.py"))

            if not python_files:
                return ValidationResult(
                    name="python_imports",
                    status=ValidationStatus.WARNING,
                    message="No Python files found",
                )

            # Check for common import issues
            import_errors = []
            for py_file in python_files:
                try:
                    with open(py_file, encoding="utf-8") as f:
                        content = f.read()

                    # Basic syntax check
                    compile(content, str(py_file), "exec")

                except SyntaxError as e:
                    import_errors.append(f"{py_file}: {e}")
                except Exception as e:
                    import_errors.append(f"{py_file}: {e}")

            if import_errors:
                return ValidationResult(
                    name="python_imports",
                    status=ValidationStatus.FAILED,
                    message=f"Import/syntax errors found: {len(import_errors)}",
                    details={"errors": import_errors[:5]},  # Show first 5 errors
                )

            return ValidationResult(
                name="python_imports",
                status=ValidationStatus.PASSED,
                message=f"All {len(python_files)} Python files have valid syntax",
            )

        except Exception as e:
            return ValidationResult(
                name="python_imports",
                status=ValidationStatus.FAILED,
                message=f"Failed to validate imports: {e}",
            )

    def _validate_node_structure(self, project_path: Path) -> ValidationResult:
        """
        Validate Node.js project structure.
        """
        package_json = project_path / "package.json"

        if not package_json.exists():
            return ValidationResult(
                name="node_structure",
                status=ValidationStatus.FAILED,
                message="No package.json found",
                fix_suggestion="Run 'npm init' to create package.json",
            )

        return ValidationResult(
            name="node_structure",
            status=ValidationStatus.PASSED,
            message="Node.js project structure is valid",
        )

    def _validate_node_dependencies(self, project_path: Path) -> ValidationResult:
        """
        Validate Node.js dependencies.
        """
        try:
            # Check if npm is available
            subprocess.run(["npm", "--version"], check=True, capture_output=True)

            package_json = project_path / "package.json"
            if package_json.exists():
                return ValidationResult(
                    name="node_dependencies",
                    status=ValidationStatus.PASSED,
                    message="Node.js dependencies configuration found",
                )
            return ValidationResult(
                name="node_dependencies",
                status=ValidationStatus.FAILED,
                message="No package.json found",
            )

        except (subprocess.CalledProcessError, FileNotFoundError):
            return ValidationResult(
                name="node_dependencies",
                status=ValidationStatus.FAILED,
                message="npm not available",
                fix_suggestion="Install Node.js and npm",
            )

    def _validate_node_scripts(self, project_path: Path) -> ValidationResult:
        """
        Validate Node.js scripts.
        """
        package_json = project_path / "package.json"

        if not package_json.exists():
            return ValidationResult(
                name="node_scripts",
                status=ValidationStatus.SKIPPED,
                message="No package.json found",
            )

        try:
            import json

            with open(package_json) as f:
                config = json.load(f)

            scripts = config.get("scripts", {})
            if not scripts:
                return ValidationResult(
                    name="node_scripts",
                    status=ValidationStatus.WARNING,
                    message="No scripts defined in package.json",
                    fix_suggestion="Add scripts section to package.json",
                )

            return ValidationResult(
                name="node_scripts",
                status=ValidationStatus.PASSED,
                message=f"Found {len(scripts)} scripts in package.json",
            )

        except Exception as e:
            return ValidationResult(
                name="node_scripts",
                status=ValidationStatus.FAILED,
                message=f"Failed to validate scripts: {e}",
            )

    def _validate_rust_structure(self, project_path: Path) -> ValidationResult:
        """
        Validate Rust project structure.
        """
        cargo_toml = project_path / "Cargo.toml"

        if not cargo_toml.exists():
            return ValidationResult(
                name="rust_structure",
                status=ValidationStatus.FAILED,
                message="No Cargo.toml found",
                fix_suggestion="Run 'cargo init' to create a Rust project",
            )

        return ValidationResult(
            name="rust_structure",
            status=ValidationStatus.PASSED,
            message="Rust project structure is valid",
        )

    def _validate_rust_dependencies(self, project_path: Path) -> ValidationResult:
        """
        Validate Rust dependencies.
        """
        try:
            # Check if cargo is available
            subprocess.run(["cargo", "--version"], check=True, capture_output=True)

            return ValidationResult(
                name="rust_dependencies",
                status=ValidationStatus.PASSED,
                message="Cargo is available",
            )

        except (subprocess.CalledProcessError, FileNotFoundError):
            return ValidationResult(
                name="rust_dependencies",
                status=ValidationStatus.FAILED,
                message="Cargo not available",
                fix_suggestion="Install Rust toolchain",
            )

    def _validate_go_structure(self, project_path: Path) -> ValidationResult:
        """
        Validate Go project structure.
        """
        go_mod = project_path / "go.mod"

        if not go_mod.exists():
            return ValidationResult(
                name="go_structure",
                status=ValidationStatus.FAILED,
                message="No go.mod found",
                fix_suggestion="Run 'go mod init <module>' to create a Go module",
            )

        return ValidationResult(
            name="go_structure",
            status=ValidationStatus.PASSED,
            message="Go project structure is valid",
        )

    def _validate_go_modules(self, project_path: Path) -> ValidationResult:
        """
        Validate Go modules.
        """
        try:
            # Check if go is available
            subprocess.run(["go", "version"], check=True, capture_output=True)

            return ValidationResult(
                name="go_modules",
                status=ValidationStatus.PASSED,
                message="Go toolchain is available",
            )

        except (subprocess.CalledProcessError, FileNotFoundError):
            return ValidationResult(
                name="go_modules",
                status=ValidationStatus.FAILED,
                message="Go toolchain not available",
                fix_suggestion="Install Go toolchain",
            )
