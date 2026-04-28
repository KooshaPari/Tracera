#!/usr/bin/env python3
"""
Test Ruff Integration
====================

Test script to verify the ruff-centric approach works correctly.
"""

import sys
from pathlib import Path

# Add pheno-sdk to path
pheno_sdk_path = Path(__file__).parent
sys.path.insert(0, str(pheno_sdk_path))

from src.pheno.mcp.entry_points.enhanced_framework import create_enhanced_framework


def test_ruff_integration():
    """
    Test ruff integration in the enhanced framework.
    """
    print("🧪 Testing Ruff Integration")
    print("=" * 50)

    # Create enhanced framework
    framework = create_enhanced_framework(
        project_name="test_project",
        project_root=Path(__file__).parent,
        enable_basic=False,
        enable_advanced=False,
        enable_maintenance=True,
    )

    print(f"Available commands: {framework.get_available_commands()}")

    # Test ruff-only check
    print("\n🔍 Testing ruff-only check...")

    class MockArgs:
        def __init__(self):
            pass

    args = MockArgs()

    try:
        result = framework.execute_command("check_ruff", args)
        print(f"Ruff-only check result: {result}")
    except Exception as e:
        print(f"Error running ruff-only check: {e}")

    # Test comprehensive check
    print("\n🔍 Testing comprehensive check...")
    try:
        result = framework.execute_command("check", args)
        print(f"Comprehensive check result: {result}")
    except Exception as e:
        print(f"Error running comprehensive check: {e}")

    # Test lint command
    print("\n🔍 Testing lint command...")
    try:
        result = framework.execute_command("lint", args)
        print(f"Lint result: {result}")
    except Exception as e:
        print(f"Error running lint: {e}")

    # Test format command
    print("\n🔍 Testing format command...")
    try:
        result = framework.execute_command("format", args)
        print(f"Format result: {result}")
    except Exception as e:
        print(f"Error running format: {e}")

    print("\n✅ Ruff integration test completed!")


if __name__ == "__main__":
    test_ruff_integration()
