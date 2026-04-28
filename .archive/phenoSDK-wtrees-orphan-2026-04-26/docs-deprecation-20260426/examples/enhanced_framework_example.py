#!/usr/bin/env python3
"""
Enhanced Framework Usage Examples
=================================

This example demonstrates how to use the enhanced composable MCP framework
for various use cases, from simple to complex scenarios.
"""

import sys
from pathlib import Path

# Add pheno-sdk to path
pheno_sdk_path = Path(__file__).parent.parent
sys.path.insert(0, str(pheno_sdk_path))

from src.pheno.mcp.entry_points.enhanced_framework import (
    AdvancedCommandsMixin,
    BasicCommandsMixin,
    MaintenanceCommandsMixin,
    create_atoms_framework,
    create_enhanced_framework,
    create_simple_framework,
)


def example_1_simple_framework():
    """Example 1: Simple framework with only basic commands."""
    print("=== Example 1: Simple Framework ===")

    # Create a simple framework with only basic commands
    framework = create_simple_framework(
        project_name="my_simple_project", project_root=Path(__file__).parent,
    )

    print(f"Available commands: {framework.get_available_commands()}")

    # You can run commands programmatically
    class MockArgs:
        def __init__(self):
            self.port = 50002
            self.verbose = True
            self.no_tunnel = False

    args = MockArgs()

    # Execute commands
    print("Running start command...")
    result = framework.execute_command("start", args)
    print(f"Start result: {result}")

    print("Running status command...")
    result = framework.execute_command("status", args)
    print(f"Status result: {result}")


def example_2_advanced_framework():
    """Example 2: Advanced framework with all commands."""
    print("\n=== Example 2: Advanced Framework ===")

    # Create an advanced framework with all commands
    framework = create_enhanced_framework(
        project_name="my_advanced_project",
        project_root=Path(__file__).parent,
        enable_basic=True,
        enable_advanced=True,
        enable_maintenance=True,
    )

    print(f"Available commands: {framework.get_available_commands()}")

    # Run maintenance commands
    class MockArgs:
        def __init__(self):
            pass

    args = MockArgs()

    print("Running comprehensive check...")
    result = framework.execute_command("check", args)
    print(f"Check result: {result}")

    print("Running lint...")
    result = framework.execute_command("lint", args)
    print(f"Lint result: {result}")

    print("Running format...")
    result = framework.execute_command("format", args)
    print(f"Format result: {result}")


def example_3_custom_commands():
    """Example 3: Adding custom commands to the framework."""
    print("\n=== Example 3: Custom Commands ===")

    # Create a framework
    framework = create_enhanced_framework(
        project_name="my_custom_project", project_root=Path(__file__).parent,
    )

    # Add custom commands
    def custom_hello(args):
        print("Hello from custom command!")
        return 0

    def custom_goodbye(args):
        print("Goodbye from custom command!")
        return 0

    framework.add_custom_command("hello", custom_hello)
    framework.add_custom_command("goodbye", custom_goodbye)

    print(f"Available commands: {framework.get_available_commands()}")

    # Run custom commands
    class MockArgs:
        def __init__(self):
            pass

    args = MockArgs()

    print("Running custom hello command...")
    result = framework.execute_command("hello", args)
    print(f"Hello result: {result}")

    print("Running custom goodbye command...")
    result = framework.execute_command("goodbye", args)
    print(f"Goodbye result: {result}")


def example_4_mixins():
    """Example 4: Using individual mixins."""
    print("\n=== Example 4: Individual Mixins ===")

    # Create individual mixins
    basic_mixin = BasicCommandsMixin()
    advanced_mixin = AdvancedCommandsMixin()
    maintenance_mixin = MaintenanceCommandsMixin(Path(__file__).parent)

    print(f"Basic commands: {list(basic_mixin.get_commands().keys())}")
    print(f"Advanced commands: {list(advanced_mixin.get_commands().keys())}")
    print(f"Maintenance commands: {list(maintenance_mixin.get_commands().keys())}")

    # You can use mixins independently
    class MockArgs:
        def __init__(self):
            self.port = 50002
            self.verbose = True
            self.environment = "preview"
            self.test_type = "dry"

    args = MockArgs()

    # Run commands from different mixins
    print("Running basic start command...")
    result = basic_mixin.cmd_start(args)
    print(f"Start result: {result}")

    print("Running advanced test command...")
    result = advanced_mixin.cmd_test(args)
    print(f"Test result: {result}")


def example_5_cli_interface():
    """Example 5: Using the CLI interface."""
    print("\n=== Example 5: CLI Interface ===")

    # Create a framework
    framework = create_atoms_framework(project_root=Path(__file__).parent)

    # Create CLI parser
    parser = framework.create_cli_parser()

    # Show help
    print("CLI Help:")
    parser.print_help()

    # You can also run the CLI with arguments
    print("\nRunning CLI with 'start --help'...")
    result = framework.run_cli(["start", "--help"])
    print(f"CLI result: {result}")


def example_6_maintenance_commands():
    """Example 6: Detailed maintenance commands."""
    print("\n=== Example 6: Maintenance Commands ===")

    # Create a framework with maintenance commands
    framework = create_enhanced_framework(
        project_name="maintenance_demo",
        project_root=Path(__file__).parent,
        enable_basic=False,
        enable_advanced=False,
        enable_maintenance=True,
    )

    print(f"Maintenance commands: {framework.get_available_commands()}")

    # Run maintenance commands
    class MockArgs:
        def __init__(self):
            pass

    args = MockArgs()

    print("Running comprehensive check with parallel execution...")
    result = framework.execute_command("check", args)
    print(f"Check result: {result}")

    print("Running lint with autofix...")
    result = framework.execute_command("lint", args)
    print(f"Lint result: {result}")

    print("Running format...")
    result = framework.execute_command("format", args)
    print(f"Format result: {result}")


def main():
    """
    Run all examples.
    """
    print("Enhanced MCP Framework Examples")
    print("=" * 50)

    try:
        example_1_simple_framework()
        example_2_advanced_framework()
        example_3_custom_commands()
        example_4_mixins()
        example_5_cli_interface()
        example_6_maintenance_commands()

        print("\n" + "=" * 50)
        print("All examples completed successfully!")

    except Exception as e:
        print(f"\nError running examples: {e}")
        import traceback

        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
