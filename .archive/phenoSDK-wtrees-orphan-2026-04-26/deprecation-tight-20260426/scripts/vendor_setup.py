#!/usr/bin/env python3
"""
Vendor Setup Script for Pheno-SDK Automated setup and configuration of vendored
dependencies.
"""

import argparse
import sys
from pathlib import Path


class VendorSetup:
    """
    Automated vendor setup and management.
    """

    def __init__(self, project_dir: str = None):
        self.project_dir = Path(project_dir) if project_dir else Path.cwd()
        self.vendor_dir = self.project_dir / "vendor"
        self.config_file = self.project_dir / "vendor_config.json"

        # Default packages to vendor (critical dependencies)
        self.default_packages = [
            {"name": "typer", "reason": "CLI framework - critical for project", "required": True},
            {"name": "rich", "reason": "Rich console output - essential for CLI", "required": True},
            {"name": "click", "reason": "Click CLI library - optional fallback", "required": False},
            {
                "name": "pydantic",
                "reason": "Data validation - core functionality",
                "required": True,
            },
        ]

    def setup_vendor_system(self, force: bool = False) -> bool:
        """
        Setup complete vendor system.
        """
        print("🚀 Setting up vendor management system...")

        try:
            # Create vendor directory
            self.vendor_dir.mkdir(exist_ok=True)
            print("✓ Vendor directory created")

            # Create .gitignore for vendor directory
            gitignore_path = self.vendor_dir / ".gitignore"
            if not gitignore_path.exists():
                gitignore_path.write_text("*\n!.gitignore\n!vendor.lock.json\n!metadata.json\n")
                print("✓ Vendor .gitignore created")

            # Initialize vendor lock file
            lock_file = self.vendor_dir / "vendor.lock.json"
            if not lock_file.exists() or force:
                lock_file.write_text("{}\n")
                print("✓ Vendor lock file initialized")

            # Create metadata file
            metadata_file = self.vendor_dir / "metadata.json"
            if not metadata_file.exists():
                metadata_file.write_text(
                    '{"setup_version": "1.0", "project": "' + str(self.project_dir.name) + '"}\n',
                )
                print("✓ Metadata file created")

            # Create vendor README
            self._create_vendor_readme()

            print("✅ Vendor system setup complete!")
            return True

        except Exception as e:
            print(f"❌ Setup failed: {e}")
            return False

    def vendor_default_packages(self, force: bool = False) -> bool:
        """
        Vendor default critical packages.
        """
        print("📦 Vendoring critical dependencies...")

        from lib.vendor_manager import VendorManager

        vendor_manager = VendorManager(str(self.vendor_dir))
        success = True

        for pkg in self.default_packages:
            try:
                print(f"  • Adding {pkg['name']}...")

                # Try to add package
                result = vendor_manager.add_package(pkg["name"], force=force)

                if result:
                    print(f"    ✅ {pkg['name']} vendored")
                elif pkg["required"]:
                    print(f"    ❌ Failed to vendor required package {pkg['name']}")
                    success = False
                else:
                    print(f"    ⚠️  Failed to vendor optional package {pkg['name']}")

            except Exception as e:
                print(f"    ❌ Error vendoring {pkg['name']}: {e}")
                if pkg["required"]:
                    success = False

        if success:
            print("✅ Package vendoring complete!")
        else:
            print("⚠️  Some packages failed to vendor")

        return success

    def create_bundle_requirements(self) -> bool:
        """
        Create bundled requirements file.
        """
        print("📄 Creating bundled requirements...")

        try:
            vendor_manager = VendorManager(str(self.vendor_dir))
            packages = vendor_manager.list_packages()

            bundle_requirements = self.project_dir / "requirements-bundled.txt"

            with open(bundle_requirements, "w") as f:
                f.write("# Bundled requirements for Pheno-SDK\n")
                f.write("# These packages are vendored in the vendor/ directory\n\n")

                for pkg in packages:
                    f.write(f"# {pkg['name']} - See vendor/{pkg['name']}\n")
                    # Add commented out original requirement for reference
                    f.write(f"# {pkg['name']}>={pkg['version']}\n\n")

            print(f"✓ Created {bundle_requirements}")
            return True

        except Exception as e:
            print(f"❌ Failed to create bundle requirements: {e}")
            return False

    def update_python_path(self) -> bool:
        """
        Update Python path configuration.
        """
        print("🐍 Updating Python path configuration...")

        try:
            sitecustomize_path = self.project_dir / "sitecustomize.py"

            if sitecustomize_path.exists():
                content = sitecustomize_path.read_text()
            else:
                content = ""

            vendor_path_addition = """
# Add vendor directory to Python path for Pheno-SDK
import os
from pathlib import Path

pheno_vendor_path = Path(__file__).parent / "vendor"
if pheno_vendor_path.exists():
    if str(pheno_vendor_path) not in sys.path:
        sys.path.insert(0, str(pheno_vendor_path))
"""

            if "pheno_vendor_path" not in content:
                with open(sitecustomize_path, "a") as f:
                    f.write(vendor_path_addition)
                print("✓ Updated sitecustomize.py")
            else:
                print("✓ sitecustomize.py already configured")

            return True

        except Exception as e:
            print(f"❌ Failed to update Python path: {e}")
            return False

    def create_vendor_tests(self) -> bool:
        """
        Create vendor-related tests.
        """
        print("🧪 Creating vendor tests...")

        try:
            test_dir = self.project_dir / "tests" / "vendor"
            test_dir.mkdir(parents=True, exist_ok=True)

            # Test vendor manager
            manager_test = test_dir / "test_vendor_manager.py"
            manager_test.write_text(
                '''
"""Test vendor manager functionality"""

import pytest
import tempfile
import shutil
from pathlib import Path
import sys

# Add project root to path for testing
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from lib.vendor_manager import VendorManager


class TestVendorManager:
    """Test vendor manager operations"""

    @pytest.fixture
    def temp_vendor_dir(self):
        """Create temporary vendor directory"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def vendor_manager(self, temp_vendor_dir):
        """Create vendor manager instance"""
        return VendorManager(temp_vendor_dir)

    def test_vendor_manager_initialization(self, vendor_manager):
        """Test vendor manager initialization"""
        assert vendor_manager.vendor_dir.exists()
        assert vendor_manager.packages == {}

    def test_list_packages_empty(self, vendor_manager):
        """Test listing packages when empty"""
        packages = vendor_manager.list_packages()
        assert packages == []

    def test_verify_packages_empty(self, vendor_manager):
        """Test verifying packages when empty"""
        results = vendor_manager.verify_packages()
        assert results == {}

    def test_clean_vendor_dir_empty(self, vendor_manager):
        """Test cleaning empty vendor directory"""
        removed = vendor_manager.clean_vendor_dir()
        assert removed == []
''',
            )

            print("✓ Created vendor tests")
            return True

        except Exception as e:
            print(f"❌ Failed to create vendor tests: {e}")
            return False

    def _create_vendor_readme(self):
        """
        Create README for vendor directory.
        """
        readme_path = self.vendor_dir / "README.md"

        if not readme_path.exists():
            readme_content = """# Vendor Directory

This directory contains vendored (bundled) dependencies for the Pheno-SDK project.

## Purpose

Vendoring ensures that critical dependencies are always available, even when:
- Network connectivity is limited
- Package repositories are unavailable
- Specific dependency versions are required

## Structure

```
vendor/
├── package-name/          # Vendored package directory
├── vendor.lock.json       # Package lock file with checksums
├── metadata.json          # Vendor metadata
└── .gitignore            # Git ignore rules
```

## Management

Use the vendor manager to manage vendored packages:

```bash
# List vendored packages
python scripts/vendor_setup.py list

# Add a package to vendor
python scripts/vendor_setup.py add package-name

# Remove a vendored package
python scripts/vendor_setup.py remove package-name

# Sync packages with sources
python scripts/vendor_setup.py sync

# Verify vendored packages
python scripts/vendor_setup.py verify

# Clean vendor directory
python scripts/vendor_setup.py clean
```

## Guidelines

- Vendor only critical dependencies that affect project functionality
- Keep vendor directory size minimal
- Update vendored packages regularly
- Verify checksums after updates
- Document reasons for vendoring each package
"""

            readme_path.write_text(readme_content)

    def complete_setup(self, force: bool = False) -> bool:
        """
        Complete vendor system setup.
        """
        print("🏗️  Setting up complete vendor system...")

        success = True

        # Setup vendor system
        if not self.setup_vendor_system(force):
            success = False

        # Vendor critical packages
        if not self.vendor_default_packages(force):
            success = False

        # Create bundle requirements
        if not self.create_bundle_requirements():
            success = False

        # Update Python path
        if not self.update_python_path():
            success = False

        # Create tests
        if not self.create_vendor_tests():
            # This is not critical for overall success
            print("⚠️  Vendor tests creation failed (non-critical)")

        if success:
            print("\n🎉 Vendor system setup complete!")
            print("\nNext steps:")
            print("  1. Review vendored packages: python scripts/vendor_setup.py list")
            print("  2. Verify package integrity: python scripts/vendor_setup.py verify")
            print("  3. Test imports: python -c 'import typer, rich'")
        else:
            print("\n❌ Vendor system setup completed with issues")

        return success


def main():
    """
    Main entry point.
    """
    parser = argparse.ArgumentParser(description="Setup Pheno-SDK vendor system")
    parser.add_argument("--force", action="store_true", help="Force overwrite existing files")
    parser.add_argument("--project-dir", help="Project directory path")
    parser.add_argument(
        "--setup-only", action="store_true", help="Only setup vendor system, don't add packages",
    )

    args = parser.parse_args()

    vendor_setup = VendorSetup(args.project_dir)

    if args.setup_only:
        success = vendor_setup.setup_vendor_system(args.force)
    else:
        success = vendor_setup.complete_setup(args.force)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
