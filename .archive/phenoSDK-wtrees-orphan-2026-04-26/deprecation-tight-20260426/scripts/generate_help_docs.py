#!/usr/bin/env python3
"""Help System Enhancement Script.

Auto-generated help comments and CLI documentation.
"""

import argparse
import json
import os
import re
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]


def extract_cli_commands() -> dict[str, Any]:
    """
    Extract CLI commands from the codebase.
    """
    commands = {}

    # Scan for CLI command files
    cli_dirs = [
        REPO_ROOT / "pheno-sdk" / "cli",
        REPO_ROOT / "zen-mcp-server" / "cli",
        REPO_ROOT / "atoms_mcp-old" / "cli",
    ]

    for cli_dir in cli_dirs:
        if cli_dir.exists():
            for root, dirs, files in os.walk(cli_dir):
                for file in files:
                    if file.endswith(".py") and not file.startswith("__"):
                        file_path = os.path.join(root, file)
                        commands.update(extract_commands_from_file(file_path))

    return commands


def extract_commands_from_file(file_path: str) -> dict[str, Any]:
    """
    Extract commands from a single Python file.
    """
    commands = {}

    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        # Look for Typer commands and functions
        command_patterns = [
            r"@app\.command\(\)\s*def\s+(\w+)\([^)]*\):",
            r"@typer\.Typer\(\)\s*def\s+(\w+)\([^)]*\):",
            r'def\s+(\w+)\([^)]*\):\s*"""[^"]*"""',
            r'def\s+(\w+)\([^)]*\):\s*"""[^"]*"""',
        ]

        for pattern in command_patterns:
            matches = re.finditer(pattern, content, re.MULTILINE | re.DOTALL)
            for match in matches:
                command_name = match.group(1)
                if command_name not in ["main", "app", "cli"]:
                    commands[command_name] = {
                        "file": file_path,
                        "name": command_name,
                        "description": extract_command_description(content, command_name),
                        "parameters": extract_command_parameters(content, command_name),
                    }

    except Exception as e:
        print(f"Error processing {file_path}: {e}")

    return commands


def extract_command_description(content: str, command_name: str) -> str:
    """
    Extract command description from docstring.
    """
    # Look for function definition and its docstring
    pattern = rf'def\s+{command_name}\([^)]*\):\s*"""(.*?)"""'
    match = re.search(pattern, content, re.DOTALL)

    if match:
        docstring = match.group(1).strip()
        # Clean up the docstring
        docstring = re.sub(r"\s+", " ", docstring)
        return docstring

    return f"Command: {command_name}"


def extract_command_parameters(content: str, command_name: str) -> list[dict[str, str]]:
    """
    Extract command parameters.
    """
    parameters = []

    # Look for function signature
    pattern = rf"def\s+{command_name}\(([^)]*)\):"
    match = re.search(pattern, content)

    if match:
        params_str = match.group(1)
        # Parse parameters (simplified)
        for param in params_str.split(","):
            param = param.strip()
            if param and not param.startswith("*"):
                param_name = param.split(":")[0].strip()
                param_type = param.split(":")[1].strip() if ":" in param else "str"
                parameters.append(
                    {
                        "name": param_name,
                        "type": param_type,
                        "description": f"Parameter: {param_name}",
                    },
                )

    return parameters


def generate_help_documentation(commands: dict[str, Any]) -> str:
    """
    Generate comprehensive help documentation.
    """
    doc = []
    doc.append("# ATOMS-PHENO CLI Help Documentation")
    doc.append("=" * 50)
    doc.append("")
    doc.append(
        "This document provides comprehensive help for all CLI commands available in the ATOMS-PHENO infrastructure.",
    )
    doc.append("")

    # Group commands by category
    categories = {
        "Core Commands": [],
        "Development Commands": [],
        "Testing Commands": [],
        "Monitoring Commands": [],
        "Deployment Commands": [],
        "Package Management Commands": [],
    }

    for cmd_name, cmd_info in commands.items():
        if any(keyword in cmd_name.lower() for keyword in ["test", "pytest", "coverage"]):
            categories["Testing Commands"].append((cmd_name, cmd_info))
        elif any(
            keyword in cmd_name.lower()
            for keyword in ["monitor", "analyze", "complexity", "duplication"]
        ):
            categories["Monitoring Commands"].append((cmd_name, cmd_info))
        elif any(keyword in cmd_name.lower() for keyword in ["deploy", "vercel", "deployment"]):
            categories["Deployment Commands"].append((cmd_name, cmd_info))
        elif any(keyword in cmd_name.lower() for keyword in ["vendor", "package", "dependency"]):
            categories["Package Management Commands"].append((cmd_name, cmd_info))
        elif any(keyword in cmd_name.lower() for keyword in ["dev", "build", "setup"]):
            categories["Development Commands"].append((cmd_name, cmd_info))
        else:
            categories["Core Commands"].append((cmd_name, cmd_info))

    # Generate documentation for each category
    for category, cmd_list in categories.items():
        if cmd_list:
            doc.append(f"## {category}")
            doc.append("")

            for cmd_name, cmd_info in cmd_list:
                doc.append(f"### `{cmd_name}`")
                doc.append("")
                doc.append(f"**Description:** {cmd_info['description']}")
                doc.append("")
                doc.append(f"**File:** `{cmd_info['file']}`")
                doc.append("")

                if cmd_info["parameters"]:
                    doc.append("**Parameters:**")
                    for param in cmd_info["parameters"]:
                        doc.append(f"- `{param['name']}` ({param['type']}): {param['description']}")
                    doc.append("")

                doc.append("**Usage:**")
                doc.append("```bash")
                doc.append(f"pheno {cmd_name} [options]")
                doc.append("```")
                doc.append("")

    return "\n".join(doc)


def generate_makefile_help() -> str:
    """
    Generate help documentation for Makefile targets.
    """
    help_doc = []
    help_doc.append("# Makefile Help Documentation")
    help_doc.append("=" * 40)
    help_doc.append("")
    help_doc.append(
        "This document provides help for all Makefile targets available in the ATOMS-PHENO infrastructure.",
    )
    help_doc.append("")

    # Common Makefile targets
    targets = {
        "Development": [
            ("install", "Install development dependencies"),
            ("install-prod", "Install production dependencies"),
            ("setup", "Set up development environment"),
            ("clean", "Clean build artifacts and temporary files"),
            ("clean-all", "Clean all artifacts including vendor packages"),
        ],
        "Testing": [
            ("test", "Run all tests"),
            ("test-parallel", "Run tests in parallel"),
            ("test-coverage", "Run tests with coverage analysis"),
            ("test-duration", "Run tests with duration tracking"),
            ("test-fast", "Run only fast tests"),
            ("test-slow", "Run only slow tests"),
        ],
        "Code Quality": [
            ("lint", "Run linting checks"),
            ("lint-fix", "Fix linting issues automatically"),
            ("format", "Format code with Black"),
            ("imports", "Sort imports with isort"),
            ("docs-format", "Format docstrings with docformatter"),
            ("quality", "Run comprehensive quality checks"),
            ("quality-full", "Run full quality analysis"),
        ],
        "Security": [
            ("security", "Run security scans"),
            ("bandit", "Run Bandit security analysis"),
            ("safety", "Run Safety vulnerability check"),
            ("audit", "Run comprehensive security audit"),
        ],
        "Monitoring": [
            ("monitor-complexity", "Analyze code complexity"),
            ("monitor-dead-code", "Detect dead code"),
            ("monitor-duplication", "Analyze code duplication"),
            ("monitor-docs", "Check documentation coverage"),
            ("monitor-deps", "Analyze dependencies"),
            ("monitor-all", "Run all monitoring checks"),
        ],
        "Performance": [
            ("benchmark", "Run performance benchmarks"),
            ("profile", "Run memory profiling"),
            ("load-test", "Run load tests"),
            ("perf-all", "Run all performance tests"),
        ],
        "Deployment": [
            ("deploy-validate", "Validate deployment readiness"),
            ("deploy-check", "Check deployment configuration"),
            ("vercel-deploy", "Deploy to Vercel"),
            ("health-check", "Check system health"),
        ],
        "Package Management": [
            ("vendor-status", "Check vendor package status"),
            ("vendor-sync", "Sync vendor packages"),
            ("vendor-verify", "Verify vendor packages"),
            ("vendor-clean", "Clean vendor packages"),
            ("deps-analyze", "Analyze dependencies"),
            ("deps-validate", "Validate dependencies"),
        ],
    }

    for category, target_list in targets.items():
        help_doc.append(f"## {category}")
        help_doc.append("")

        for target, description in target_list:
            help_doc.append(f"### `make {target}`")
            help_doc.append(f"**Description:** {description}")
            help_doc.append("")
            help_doc.append("**Usage:**")
            help_doc.append("```bash")
            help_doc.append(f"make {target}")
            help_doc.append("```")
            help_doc.append("")

    return "\n".join(help_doc)


def generate_script_help() -> str:
    """
    Generate help documentation for scripts.
    """
    help_doc = []
    help_doc.append("# Scripts Help Documentation")
    help_doc.append("=" * 40)
    help_doc.append("")
    help_doc.append(
        "This document provides help for all scripts available in the ATOMS-PHENO infrastructure.",
    )
    help_doc.append("")

    # Script categories
    script_categories = {
        "Analysis Scripts": [
            ("analyze_complexity.py", "Analyze code complexity using Radon"),
            ("analyze_duplication.py", "Analyze code duplication using Pylint"),
            ("analyze_dependencies.py", "Analyze dependencies using pipdeptree"),
            ("analyze_response_times.py", "Analyze API response times"),
            ("analyze_churn.py", "Analyze code churn using Git"),
        ],
        "Validation Scripts": [
            ("validate_dependencies.py", "Validate dependency security and licenses"),
            ("validate_schema.py", "Validate database schema"),
            ("validate_cleanup.py", "Validate code cleanup status"),
            ("validate_config.py", "Validate environment configuration"),
        ],
        "Monitoring Scripts": [
            ("coverage_analysis.py", "Analyze test coverage"),
            ("test_duration_tracker.py", "Track test execution duration"),
            ("profile_memory.py", "Profile memory usage"),
        ],
        "Utility Scripts": [
            ("vendor_setup.py", "Set up vendor package management"),
            ("check_deployment.py", "Check deployment readiness"),
            ("check_health.py", "Check system health"),
            ("backfill_embeddings.py", "Backfill embedding data"),
            ("check_embedding_status.py", "Check embedding generation status"),
        ],
    }

    for category, script_list in script_categories.items():
        help_doc.append(f"## {category}")
        help_doc.append("")

        for script_name, description in script_list:
            help_doc.append(f"### `{script_name}`")
            help_doc.append(f"**Description:** {description}")
            help_doc.append("")
            help_doc.append("**Usage:**")
            help_doc.append("```bash")
            help_doc.append(f"python scripts/{script_name} [options]")
            help_doc.append("```")
            help_doc.append("")
            help_doc.append("**Options:**")
            help_doc.append("- `--help`: Show help message")
            help_doc.append("- `--json`: Output in JSON format")
            help_doc.append("- `--report`: Generate detailed report")
            help_doc.append("")

    return "\n".join(help_doc)


def main():
    """
    Main help generation function.
    """
    parser = argparse.ArgumentParser(description="Generate help documentation")
    default_output_dir = REPO_ROOT / "pheno-sdk" / "docs"
    parser.add_argument(
        "--output-dir",
        default=str(default_output_dir),
        help="Output directory for documentation",
    )
    parser.add_argument(
        "--format", choices=["markdown", "html", "json"], default="markdown", help="Output format",
    )

    args = parser.parse_args()

    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(exist_ok=True)

    # Extract CLI commands
    commands = extract_cli_commands()

    # Generate documentation
    cli_doc = generate_help_documentation(commands)
    makefile_doc = generate_makefile_help()
    script_doc = generate_script_help()

    # Write documentation files
    if args.format == "markdown":
        with open(output_dir / "cli-help.md", "w") as f:
            f.write(cli_doc)

        with open(output_dir / "makefile-help.md", "w") as f:
            f.write(makefile_doc)

        with open(output_dir / "scripts-help.md", "w") as f:
            f.write(script_doc)

        # Combined documentation
        combined_doc = f"{cli_doc}\n\n{makefile_doc}\n\n{script_doc}"
        with open(output_dir / "complete-help.md", "w") as f:
            f.write(combined_doc)

    elif args.format == "json":
        help_data = {
            "cli_commands": commands,
            "makefile_targets": {},  # Would be populated from Makefile parsing
            "scripts": {},  # Would be populated from script analysis
        }

        with open(output_dir / "help-data.json", "w") as f:
            json.dump(help_data, f, indent=2)

    print(f"Help documentation generated in {output_dir}")
    print(f"Format: {args.format}")
    print(f"CLI Commands: {len(commands)}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
