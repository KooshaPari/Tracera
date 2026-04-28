#!/usr/bin/env python3
"""
Pheno-SDK Vendor Management System
==================================

Automated local package vendoring with setup/cleanup capabilities.
This script manages external dependencies by copying them into the vendor directory
for offline development and consistent dependency management.

Usage:
    python scripts/vendor_manager.py setup
    python scripts/vendor_manager.py clean
    python scripts/vendor_manager.py list
"""

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path


class VendorManager:
    """
    Manages vendoring of external packages for pheno-sdk.
    """

    def __init__(self, vendor_dir: str = "vendor"):
        self.vendor_dir = Path(vendor_dir)
        self.project_root = Path(__file__).parent.parent
        self.config_file = self.project_root / ".vendor.config"

    def setup_vendor_directory(self) -> None:
        """
        Set up the vendor directory with specified packages.
        """
        print("Setting up vendor directory...")

        # Create vendor directory if it doesn't exist
        self.vendor_dir.mkdir(exist_ok=True)

        # Get list of packages to vendor
        packages = self._get_packages_to_vendor()

        # Vendor each package
        for package in packages:
            self._vendor_package(package)

        # Save configuration
        self._save_vendor_config(packages)

        print("✅ Vendor directory setup complete")

    def _get_packages_to_vendor(self) -> list[str]:
        """
        Get list of packages that should be vendored.
        """
        # These are example packages that might be vendored
        # In practice, this would be configurable
        return [
            "requests",
            "click",
            "colorama",
            "tqdm",
        ]

    def _vendor_package(self, package_name: str) -> None:
        """
        Vendor a specific package.
        """
        print(f"  Vendoring {package_name}...")

        # Create package directory
        package_dir = self.vendor_dir / package_name
        if package_dir.exists():
            shutil.rmtree(package_dir)

        package_dir.mkdir(exist_ok=True)

        # Try to copy package from site-packages
        try:
            # Get package location
            result = subprocess.run(
                [sys.executable, "-c", f"import {package_name}; print({package_name}.__file__)"],
                capture_output=True,
                text=True,
                check=True,
            )

            package_path = Path(result.stdout.strip())
            if package_path.is_file():
                package_path = package_path.parent

            # Copy package files
            if package_path.exists():
                shutil.copytree(package_path, package_dir / package_name)
                print(f"    ✓ Copied {package_name} from {package_path}")
            else:
                print(f"    ✗ Could not find {package_name}")

        except subprocess.CalledProcessError:
            print(f"    ✗ Failed to vendor {package_name}")

    def _save_vendor_config(self, packages: list[str]) -> None:
        """
        Save vendor configuration to file.
        """
        config = {
            "packages": packages,
            "vendor_dir": str(self.vendor_dir),
            "timestamp": str(Path().stat().st_mtime if Path().exists() else "N/A"),
        }

        with open(self.config_file, "w") as f:
            json.dump(config, f, indent=2)

    def clean_vendor_directory(self) -> None:
        """
        Clean the vendor directory.
        """
        print("Cleaning vendor directory...")

        if self.vendor_dir.exists():
            shutil.rmtree(self.vendor_dir)
            print("  ✅ Vendor directory cleaned")
        else:
            print("  Vendor directory does not exist")

    def list_vendored_packages(self) -> None:
        """
        List all vendored packages.
        """
        if not self.vendor_dir.exists():
            print("Vendor directory does not exist")
            return

        packages = list(self.vendor_dir.iterdir())
        if not packages:
            print("No vendored packages found")
            return

        print("Vendored packages:")
        for package in packages:
            if package.is_dir():
                print(f"  - {package.name}")


def main():
    """
    Main entry point.
    """
    parser = argparse.ArgumentParser(
        description="Pheno-SDK Vendor Management System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Commands:
  setup    Vendor specified packages
  clean    Remove all vendored packages
  list     List all vendored packages
        """,
    )

    parser.add_argument(
        "command", choices=["setup", "clean", "list"], help="Vendor management command",
    )

    args = parser.parse_args()

    vendor_manager = VendorManager()

    if args.command == "setup":
        vendor_manager.setup_vendor_directory()
    elif args.command == "clean":
        vendor_manager.clean_vendor_directory()
    elif args.command == "list":
        vendor_manager.list_vendored_packages()


if __name__ == "__main__":
    main()
