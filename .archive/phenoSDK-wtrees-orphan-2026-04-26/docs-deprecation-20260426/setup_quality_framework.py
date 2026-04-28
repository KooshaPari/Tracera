#!/usr/bin/env python3
"""
Setup script for Pheno Quality Framework.
"""

import argparse
import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from pheno.quality.config import list_configs
from pheno.quality.integration import (
    export_framework_for_project,
    integrate_quality_framework,
)


def main():
    parser = argparse.ArgumentParser(description="Setup Pheno Quality Framework")
    parser.add_argument(
        "action", choices=["integrate", "export", "list-configs"], help="Action to perform",
    )
    parser.add_argument("--project-path", default=".", help="Project path for integration")
    parser.add_argument(
        "--project-type",
        choices=["pheno-sdk", "zen-mcp", "atoms-mcp"],
        default="pheno-sdk",
        help="Project type",
    )
    parser.add_argument("--output-path", help="Output path for export")

    args = parser.parse_args()

    if args.action == "integrate":
        print(f"🔧 Integrating quality framework into {args.project_path}...")
        success = integrate_quality_framework(args.project_path, args.project_type)
        if success:
            print("✅ Quality framework integrated successfully!")
            print(f"📁 Framework files added to {args.project_path}/quality/")
            print("🚀 You can now run: python quality/analyze.py .")
        else:
            print("❌ Failed to integrate quality framework")
            return 1

    elif args.action == "export":
        output_path = args.output_path or f"./exports/{args.project_type}-quality"
        print(f"📦 Exporting quality framework for {args.project_type}...")
        success = export_framework_for_project(args.project_type, output_path)
        if success:
            print(f"✅ Quality framework exported to {output_path}")
            print("📁 You can now copy this to other projects")
        else:
            print("❌ Failed to export quality framework")
            return 1

    elif args.action == "list-configs":
        print("📋 Available configuration presets:")
        for config_name in list_configs():
            print(f"  - {config_name}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
