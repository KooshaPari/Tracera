#!/usr/bin/env python3
"""
CLI Classes Consolidation Script.

This script consolidates all duplicate CLI classes into a unified system.

Actions performed:
1. Consolidate duplicate CLI classes
2. Remove duplicate CLI implementations
3. Create unified CLI system
4. Update imports across the codebase
"""

import shutil
from pathlib import Path


class CLIClassesConsolidator:
    """Consolidates CLI classes."""

    def __init__(self, base_path: str = "src/pheno"):
        """Initialize consolidator.

        Args:
            base_path: Base path for pheno modules
        """
        self.base_path = Path(base_path)
        self.removed_files: list[str] = []
        self.consolidated_cli_classes: dict[str, str] = {}

    def consolidate_cli_classes(self) -> None:
        """Consolidate CLI classes."""
        print("🔧 Consolidating CLI classes...")

        # Files to remove (duplicate CLI functionality)
        duplicate_cli_files = [
            "cli/cli_runner.py",  # Duplicate CLI runner
            "cli/simple.py",  # Duplicate simple CLI
            "cli/adapters.py",  # Move to adapters
            "cli/command.py",  # Move to ports
            "cli/registry.py",  # Move to ports
            "cli/main.py",  # Move to unified
        ]

        for file_path in duplicate_cli_files:
            full_path = self.base_path / file_path
            if full_path.exists():
                self._remove_file(full_path)
                print(f"  ❌ Removed: {file_path}")

        # Consolidate CLI functionality
        self._consolidate_cli_functionality()

    def consolidate_duplicate_cli_classes(self) -> None:
        """Consolidate duplicate CLI classes."""
        print("🔧 Consolidating duplicate CLI classes...")

        # Find and consolidate duplicate CLI classes
        duplicate_cli_classes = [
            "CLIAdapter",
            "Command",
            "CLIRunner",
            "SimpleCLI",
            "RichCLI",
            "HelloCommand",
            "Args",
        ]

        for cli_class in duplicate_cli_classes:
            self._consolidate_cli_class(cli_class)

    def create_unified_cli_system(self) -> None:
        """Create unified CLI system."""
        print("🏗️  Creating unified CLI system...")

        # Create the unified CLI system
        unified_cli_content = '''"""
Unified CLI System for Pheno SDK.

This module provides a comprehensive, unified CLI system consolidating
all CLI functionality across the pheno-sdk codebase.

CLI Components:
===============

UnifiedCLI (main)
├── Command (base)
├── CLIAdapter (base)
├── TyperCLI (adapter)
├── ClickCLI (adapter)
└── RichCLI (adapter)

CLI Features:
=============
- Command registration and discovery
- Option and argument handling
- Group management
- Help generation
- Error handling
- Multiple framework support (Typer, Click, Rich)
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable

from pheno.adapters.cli import TyperCLI
from pheno.ports.cli import ArgumentDefinition, CommandDefinition, OptionDefinition


class CommandCategory(Enum):
    """Command category enumeration."""

    CORE = "core"
    ATLAS = "atlas"
    QUALITY = "quality"
    CICD = "cicd"
    PROJECT = "project"
    DEPLOYMENT = "deployment"
    MONITORING = "monitoring"
    DEVELOPMENT = "development"


class ProjectType(Enum):
    """Project type enumeration."""

    PYTHON = "python"
    NODEJS = "nodejs"
    REACT = "react"
    NEXTJS = "nextjs"
    GO = "go"
    RUST = "rust"
    UNKNOWN = "unknown"


@dataclass
class CLIContext:
    """CLI execution context."""

    project_path: str
    project_type: ProjectType = ProjectType.UNKNOWN
    commands: dict[str, CommandDefinition] = None

    def __post_init__(self):
        if self.commands is None:
            self.commands = {}

    def get_available_commands(self) -> list[str]:
        """Get list of available commands."""
        return list(self.commands.keys())


class Command(ABC):
    """Base class for CLI commands."""

    def __init__(self, name: str, description: str = ""):
        """Initialize command.

        Args:
            name: Command name
            description: Command description
        """
        self.name = name
        self.description = description

    @abstractmethod
    async def execute(self, args: dict[str, Any]) -> int:
        """Execute the command.

        Args:
            args: Command arguments

        Returns:
            Exit code (0 for success)
        """
        pass

    def get_help(self) -> str:
        """Get command help text.

        Returns:
            Help text
        """
        return self.description


class CLIAdapter(ABC):
    """Base class for CLI adapters."""

    @abstractmethod
    def create_cli(self, project_type: ProjectType, commands: list[str]) -> Any:
        """Create CLI instance.

        Args:
            project_type: Project type
            commands: Available commands

        Returns:
            CLI instance
        """
        pass

    @abstractmethod
    def run_cli(self, cli: Any, args: list[str]) -> int:
        """Run CLI with arguments.

        Args:
            cli: CLI instance
            args: Command line arguments

        Returns:
            Exit code
        """
        pass


class UnifiedCLI:
    """Unified CLI that consolidates all CLI functionality."""

    def __init__(self, name: str = "pheno", description: str = ""):
        """Initialize unified CLI.

        Args:
            name: CLI application name
            description: CLI description
        """
        self.name = name
        self.description = description
        self.typer_cli = TyperCLI(name=name, description=description)
        self.commands: dict[str, CommandDefinition] = {}
        self.context = CLIContext(project_path=".")

    def command(self, name: str, **kwargs) -> Callable:
        """Decorator for command registration."""
        return self.typer_cli.command(name, **kwargs)

    def option(self, name: str, **kwargs) -> Callable:
        """Decorator for option registration."""
        return self.typer_cli.option(name, **kwargs)

    def argument(self, name: str, **kwargs) -> Callable:
        """Decorator for argument registration."""
        return self.typer_cli.argument(name, **kwargs)

    def group(self, name: str, **kwargs) -> Callable:
        """Decorator for group registration."""
        return self.typer_cli.group(name, **kwargs)

    async def run(self, args: list[str] | None = None) -> None:
        """Run CLI application."""
        await self.typer_cli.run(args)

    def get_command(self, name: str) -> CommandDefinition | None:
        """Get command definition by name."""
        return self.typer_cli.get_command(name)

    def list_commands(self) -> list[str]:
        """List all registered commands."""
        return self.typer_cli.list_commands()

    def add_command(self, command: CommandDefinition) -> None:
        """Add command definition."""
        self.typer_cli.add_command(command)
        self.commands[command.name] = command

    def register_command(
        self,
        name: str,
        command_class: type[Command],
        arg_specs: dict[str, Any] | None = None,
        help_text: str | None = None,
    ) -> None:
        """Register a command with the CLI.

        Args:
            name: Command name
            command_class: Command class
            arg_specs: Argument specifications
            help_text: Help text
        """
        # This would integrate with the command registry
        pass


# Re-export from adapters
from pheno.adapters.cli import TyperCLI, ClickCLI, RichCLI

__all__ = [
    "UnifiedCLI",
    "Command",
    "CLIAdapter",
    "CommandCategory",
    "ProjectType",
    "CLIContext",
    "TyperCLI",
    "ClickCLI",
    "RichCLI",
]
'''

        # Write unified CLI
        unified_file = self.base_path / "cli" / "unified_cli.py"
        unified_file.write_text(unified_cli_content)
        print(f"  ✅ Created unified CLI: {unified_file}")

        # Update main CLI init
        self._update_cli_init()

    def _consolidate_cli_functionality(self) -> None:
        """Consolidate CLI functionality."""
        print("  🔄 Consolidating CLI functionality...")

        # Keep the best CLI implementation
        unified_cli = self.base_path / "cli" / "unified" / "cli.py"
        if unified_cli.exists():
            print(f"    ✅ Keeping unified CLI: {unified_cli}")

        # Create unified CLI system
        self.create_unified_cli_system()

    def _consolidate_cli_class(self, cli_class: str) -> None:
        """Consolidate a specific CLI class."""
        print(f"  🔄 Consolidating {cli_class}...")

        # Find all files containing this CLI class
        files_with_cli_class = []
        for py_file in self.base_path.rglob("*.py"):
            try:
                content = py_file.read_text()
                if f"class {cli_class}" in content:
                    files_with_cli_class.append(py_file)
            except Exception:
                pass

        if len(files_with_cli_class) > 1:
            print(f"    ⚠️  Found {len(files_with_cli_class)} files with {cli_class}")
            # Keep the one in cli/unified/ directory, remove others
            for file_path in files_with_cli_class:
                if "cli/unified/" not in str(file_path):
                    # Remove duplicate definition
                    self._remove_duplicate_class_from_file(file_path, cli_class)
                    print(f"    ❌ Removed {cli_class} from {file_path}")

    def _remove_duplicate_class_from_file(
        self, file_path: Path, class_name: str,
    ) -> None:
        """Remove duplicate class definition from file."""
        try:
            content = file_path.read_text()
            lines = content.split("\n")

            # Find class definition
            class_start = None
            class_end = None
            indent_level = None

            for i, line in enumerate(lines):
                if f"class {class_name}" in line and ":" in line:
                    class_start = i
                    indent_level = len(line) - len(line.lstrip())
                    break

            if class_start is not None:
                # Find end of class
                for i in range(class_start + 1, len(lines)):
                    line = lines[i]
                    if line.strip() and not line.startswith(
                        " " * ((indent_level or 0) + 1),
                    ):
                        class_end = i
                        break

                if class_end is None:
                    class_end = len(lines)

                # Remove class definition
                new_lines = lines[:class_start] + lines[class_end:]
                file_path.write_text("\n".join(new_lines))

        except Exception as e:
            print(f"    ⚠️  Could not remove {class_name} from {file_path}: {e}")

    def _update_cli_init(self) -> None:
        """Update CLI __init__.py."""
        print("  🔄 Updating CLI __init__.py...")

        init_content = '''"""
Unified CLI System for Pheno SDK.

This module provides a comprehensive, unified CLI system consolidating
all CLI functionality across the pheno-sdk codebase.
"""

from __future__ import annotations

# Import everything from unified CLI
from .unified_cli import *

# Re-export from unified module
from .unified import *

__all__ = [
    # Unified CLI
    "UnifiedCLI",
    "Command",
    "CLIAdapter",
    "CommandCategory",
    "ProjectType",
    "CLIContext",
    # Adapters
    "TyperCLI",
    "ClickCLI",
    "RichCLI",
    # Decorators
    "command",
    "option",
    "argument",
    "group",
    # Builder
    "CLIBuilder",
]
'''

        init_file = self.base_path / "cli" / "__init__.py"
        init_file.write_text(init_content)
        print("    ✅ Updated CLI __init__.py")

    def generate_consolidation_report(self) -> None:
        """Generate consolidation report."""
        print("\n📊 CLI Classes Consolidation Report")
        print("=" * 60)
        print(f"Files removed: {len(self.removed_files)}")
        print(f"CLI classes consolidated: {len(self.consolidated_cli_classes)}")

        print("\nRemoved files:")
        for file_path in self.removed_files:
            print(f"  - {file_path}")

        print("\nConsolidated CLI classes:")
        for old_cli_class, new_cli_class in self.consolidated_cli_classes.items():
            print(f"  - {old_cli_class} → {new_cli_class}")

    def run_consolidation(self) -> None:
        """Run full CLI classes consolidation process."""
        print("🚀 Starting CLI classes consolidation...")
        print("=" * 60)

        # Step 1: Consolidate CLI classes
        self.consolidate_cli_classes()

        # Step 2: Consolidate duplicate CLI classes
        self.consolidate_duplicate_cli_classes()

        # Step 3: Generate report
        self.generate_consolidation_report()

        print("\n✅ CLI classes consolidation complete!")
        print("Next steps:")
        print("1. Update imports across the codebase")
        print("2. Run tests to ensure functionality is preserved")
        print("3. Update documentation")
        print("4. Continue with other duplicate class consolidation")

    def _remove_file(self, file_path: Path) -> None:
        """Remove a file and track it."""
        try:
            if file_path.is_file():
                file_path.unlink()
            elif file_path.is_dir():
                shutil.rmtree(file_path)
            self.removed_files.append(str(file_path))
        except Exception as e:
            print(f"    ⚠️  Could not remove {file_path}: {e}")


def main():
    """Main consolidation function."""
    consolidator = CLIClassesConsolidator()
    consolidator.run_consolidation()


if __name__ == "__main__":
    main()
