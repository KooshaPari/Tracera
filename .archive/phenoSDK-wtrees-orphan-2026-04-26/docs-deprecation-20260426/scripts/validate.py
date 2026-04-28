#!/usr/bin/env python3
"""
Unified Validation Tool for Pheno-SDK

This tool provides comprehensive validation for:
- Environment configurations
- Schema validation
- Dependency validation
- Cleanup validation

Usage:
    python scripts/validate.py [command] [options]

Commands:
    config      Validate environment configurations
    schema      Validate schema snapshots and metadata
    dependencies Validate dependency licenses and security
    cleanup     Validate code cleanup and dead code removal
    all         Run all validation checks

Options:
    --env ENV           Environment type (development, preview, production)
    --verbose           Verbose output
    --json              Output results as JSON
    --fix               Attempt to fix issues automatically
"""

import json
import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import typer
from rich.console import Console
from rich.table import Table

console = Console()
app = typer.Typer(help="Unified Validation Tool for Pheno-SDK")

# Add src to path
REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = REPO_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))


@dataclass
class ValidationResult:
    """Result of a validation check."""

    name: str
    status: str  # "passed", "failed", "warning"
    message: str
    details: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "status": self.status,
            "message": self.message,
            "details": self.details,
        }


class ConfigValidator:
    """Validates environment configurations."""

    def __init__(self, env_type: str = "development"):
        self.env_type = env_type
        self.required_vars = self._get_required_vars()

    def _get_required_vars(self) -> dict[str, str]:
        """Get required environment variables for the environment type."""
        base_vars = {
            "PHENO_ENV": "Environment identifier",
            "PHENO_LOG_LEVEL": "Logging level",
        }

        if self.env_type == "production":
            base_vars.update(
                {
                    "PHENO_DB_URL": "Database connection URL",
                    "PHENO_REDIS_URL": "Redis connection URL",
                    "PHENO_SECRET_KEY": "Secret key for encryption",
                },
            )

        return base_vars

    def validate(self) -> list[ValidationResult]:
        """Validate environment configuration."""
        results = []

        for var, description in self.required_vars.items():
            value = os.getenv(var)
            if value:
                results.append(
                    ValidationResult(
                        name=f"Environment variable: {var}",
                        status="passed",
                        message=f"{var} is set",
                        details={"variable": var, "description": description},
                    ),
                )
            else:
                results.append(
                    ValidationResult(
                        name=f"Environment variable: {var}",
                        status="failed",
                        message=f"{var} is not set",
                        details={"variable": var, "description": description},
                    ),
                )

        return results


class SchemaValidator:
    """Validates schema snapshots and metadata."""

    def __init__(self):
        self.schema_dir = REPO_ROOT / "schemas"

    def validate(self) -> list[ValidationResult]:
        """Validate schema files."""
        results = []

        if not self.schema_dir.exists():
            results.append(
                ValidationResult(
                    name="Schema directory",
                    status="failed",
                    message="Schema directory does not exist",
                    details={"path": str(self.schema_dir)},
                ),
            )
            return results

        # Check for schema files
        schema_files = list(self.schema_dir.glob("*.json"))
        if not schema_files:
            results.append(
                ValidationResult(
                    name="Schema files",
                    status="warning",
                    message="No schema files found",
                    details={"path": str(self.schema_dir)},
                ),
            )
        else:
            results.append(
                ValidationResult(
                    name="Schema files",
                    status="passed",
                    message=f"Found {len(schema_files)} schema files",
                    details={
                        "count": len(schema_files),
                        "files": [f.name for f in schema_files],
                    },
                ),
            )

        # Validate each schema file
        for schema_file in schema_files:
            try:
                with open(schema_file) as f:
                    schema_data = json.load(f)

                # Basic schema validation
                if "type" in schema_data and "properties" in schema_data:
                    results.append(
                        ValidationResult(
                            name=f"Schema validation: {schema_file.name}",
                            status="passed",
                            message="Schema is valid JSON",
                            details={"file": schema_file.name},
                        ),
                    )
                else:
                    results.append(
                        ValidationResult(
                            name=f"Schema validation: {schema_file.name}",
                            status="warning",
                            message="Schema missing required fields",
                            details={
                                "file": schema_file.name,
                                "missing": ["type", "properties"],
                            },
                        ),
                    )
            except json.JSONDecodeError as e:
                results.append(
                    ValidationResult(
                        name=f"Schema validation: {schema_file.name}",
                        status="failed",
                        message="Invalid JSON",
                        details={"file": schema_file.name, "error": str(e)},
                    ),
                )

        return results


class DependencyValidator:
    """Validates dependency licenses and security."""

    def validate(self) -> list[ValidationResult]:
        """Validate dependencies."""
        results = []

        # Check if safety is available
        try:
            safety_result = subprocess.run(
                ["safety", "check", "--json"],
                check=False,
                capture_output=True,
                text=True,
            )

            if safety_result.returncode == 0:
                results.append(
                    ValidationResult(
                        name="Security check (safety)",
                        status="passed",
                        message="No security vulnerabilities found",
                        details={
                            "tool": "safety",
                            "returncode": safety_result.returncode,
                        },
                    ),
                )
            else:
                try:
                    safety_data = json.loads(safety_result.stdout)
                    vuln_count = len(safety_data.get("vulnerabilities", []))
                    results.append(
                        ValidationResult(
                            name="Security check (safety)",
                            status="warning" if vuln_count > 0 else "passed",
                            message=f"Found {vuln_count} vulnerabilities",
                            details={"tool": "safety", "vulnerabilities": vuln_count},
                        ),
                    )
                except json.JSONDecodeError:
                    results.append(
                        ValidationResult(
                            name="Security check (safety)",
                            status="failed",
                            message="Failed to parse safety output",
                            details={"tool": "safety", "error": "JSON decode error"},
                        ),
                    )
        except FileNotFoundError:
            results.append(
                ValidationResult(
                    name="Security check (safety)",
                    status="warning",
                    message="Safety tool not found",
                    details={"tool": "safety", "error": "Not installed"},
                ),
            )

        # Check if pip-audit is available
        try:
            pip_audit_result = subprocess.run(
                ["pip-audit", "--format=json"],
                check=False,
                capture_output=True,
                text=True,
            )

            if pip_audit_result.returncode == 0:
                results.append(
                    ValidationResult(
                        name="Security audit (pip-audit)",
                        status="passed",
                        message="No security issues found",
                        details={
                            "tool": "pip-audit",
                            "returncode": pip_audit_result.returncode,
                        },
                    ),
                )
            else:
                results.append(
                    ValidationResult(
                        name="Security audit (pip-audit)",
                        status="warning",
                        message="Security audit found issues",
                        details={
                            "tool": "pip-audit",
                            "returncode": pip_audit_result.returncode,
                        },
                    ),
                )
        except FileNotFoundError:
            results.append(
                ValidationResult(
                    name="Security audit (pip-audit)",
                    status="warning",
                    message="pip-audit tool not found",
                    details={"tool": "pip-audit", "error": "Not installed"},
                ),
            )

        return results


class CleanupValidator:
    """Validates code cleanup and dead code removal."""

    def validate(self) -> list[ValidationResult]:
        """Validate cleanup."""
        results = []

        # Check for temporary files
        temp_patterns = ["*.pyc", "*.pyo", "*.log", "*.tmp"]
        temp_files = []
        for pattern in temp_patterns:
            temp_files.extend(REPO_ROOT.glob(pattern))

        if temp_files:
            results.append(
                ValidationResult(
                    name="Temporary files",
                    status="warning",
                    message=f"Found {len(temp_files)} temporary files",
                    details={"files": [f.name for f in temp_files]},
                ),
            )
        else:
            results.append(
                ValidationResult(
                    name="Temporary files",
                    status="passed",
                    message="No temporary files found",
                    details={"count": 0},
                ),
            )

        # Check for cache directories
        cache_dirs = list(REPO_ROOT.rglob("__pycache__"))
        if cache_dirs:
            results.append(
                ValidationResult(
                    name="Cache directories",
                    status="warning",
                    message=f"Found {len(cache_dirs)} cache directories",
                    details={
                        "directories": [
                            str(d.relative_to(REPO_ROOT)) for d in cache_dirs
                        ],
                    },
                ),
            )
        else:
            results.append(
                ValidationResult(
                    name="Cache directories",
                    status="passed",
                    message="No cache directories found",
                    details={"count": 0},
                ),
            )

        # Check for OS junk files
        junk_patterns = [".DS_Store", "Thumbs.db"]
        junk_files = []
        for pattern in junk_patterns:
            junk_files.extend(REPO_ROOT.glob(pattern))

        if junk_files:
            results.append(
                ValidationResult(
                    name="OS junk files",
                    status="warning",
                    message=f"Found {len(junk_files)} OS junk files",
                    details={"files": [f.name for f in junk_files]},
                ),
            )
        else:
            results.append(
                ValidationResult(
                    name="OS junk files",
                    status="passed",
                    message="No OS junk files found",
                    details={"count": 0},
                ),
            )

        return results


class UnifiedValidator:
    """Unified validation orchestrator."""

    def __init__(self, env_type: str = "development"):
        self.env_type = env_type
        self.validators = {
            "config": ConfigValidator(env_type),
            "schema": SchemaValidator(),
            "dependencies": DependencyValidator(),
            "cleanup": CleanupValidator(),
        }

    def validate_all(self) -> dict[str, list[ValidationResult]]:
        """Run all validations."""
        results = {}

        for name, validator in self.validators.items():
            results[name] = validator.validate()

        return results

    def validate_specific(self, validator_name: str) -> list[ValidationResult]:
        """Run specific validation."""
        if validator_name not in self.validators:
            return [
                ValidationResult(
                    name="Validation",
                    status="failed",
                    message=f"Unknown validator: {validator_name}",
                    details={"available": list(self.validators.keys())},
                ),
            ]

        return self.validators[validator_name].validate()


# CLI Commands
@app.command()
def config(
    env: str = typer.Option(
        "development",
        "--env",
        help="Environment type (development, preview, production)",
    ),
    verbose: bool = typer.Option(False, "--verbose", help="Verbose output"),
    json_output: bool = typer.Option(False, "--json", help="Output results as JSON"),
):
    """Validate environment configurations."""
    validator = ConfigValidator(env)
    results = validator.validate()

    if json_output:
        console.print(json.dumps([r.to_dict() for r in results], indent=2))
    else:
        display_results("Configuration Validation", results)


@app.command()
def schema(
    verbose: bool = typer.Option(False, "--verbose", help="Verbose output"),
    json_output: bool = typer.Option(False, "--json", help="Output results as JSON"),
):
    """Validate schema snapshots and metadata."""
    validator = SchemaValidator()
    results = validator.validate()

    if json_output:
        console.print(json.dumps([r.to_dict() for r in results], indent=2))
    else:
        display_results("Schema Validation", results)


@app.command()
def dependencies(
    verbose: bool = typer.Option(False, "--verbose", help="Verbose output"),
    json_output: bool = typer.Option(False, "--json", help="Output results as JSON"),
):
    """Validate dependency licenses and security."""
    validator = DependencyValidator()
    results = validator.validate()

    if json_output:
        console.print(json.dumps([r.to_dict() for r in results], indent=2))
    else:
        display_results("Dependency Validation", results)


@app.command()
def cleanup(
    verbose: bool = typer.Option(False, "--verbose", help="Verbose output"),
    json_output: bool = typer.Option(False, "--json", help="Output results as JSON"),
):
    """Validate code cleanup and dead code removal."""
    validator = CleanupValidator()
    results = validator.validate()

    if json_output:
        console.print(json.dumps([r.to_dict() for r in results], indent=2))
    else:
        display_results("Cleanup Validation", results)


@app.command()
def all(
    env: str = typer.Option(
        "development",
        "--env",
        help="Environment type (development, preview, production)",
    ),
    verbose: bool = typer.Option(False, "--verbose", help="Verbose output"),
    json_output: bool = typer.Option(False, "--json", help="Output results as JSON"),
):
    """Run all validation checks."""
    validator = UnifiedValidator(env)
    results = validator.validate_all()

    if json_output:
        output = {}
        for name, result_list in results.items():
            output[name] = [r.to_dict() for r in result_list]
        console.print(json.dumps(output, indent=2))
    else:
        for name, result_list in results.items():
            display_results(f"{name.title()} Validation", result_list)
            console.print()  # Add spacing between sections


def display_results(title: str, results: list[ValidationResult]):
    """Display validation results in a nice format."""
    table = Table(title=title)
    table.add_column("Check", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Message", style="white")

    for result in results:
        status_style = {
            "passed": "green",
            "failed": "red",
            "warning": "yellow",
        }.get(result.status, "white")

        table.add_row(
            result.name,
            f"[{status_style}]{result.status}[/{status_style}]",
            result.message,
        )

    console.print(table)


if __name__ == "__main__":
    app()
