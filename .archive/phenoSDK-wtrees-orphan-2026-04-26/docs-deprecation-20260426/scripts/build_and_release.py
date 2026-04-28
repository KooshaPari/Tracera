#!/usr/bin/env python3
"""
Build and Release Automation for pheno-sdk
Handles wheel building, testing, and publishing
"""

import shutil
import subprocess
import sys
import tempfile
import venv
from pathlib import Path


def run_command(cmd, cwd=None, check=True):
    """Run a command and return the result."""
    result = subprocess.run(cmd, check=False, shell=True, cwd=cwd, capture_output=True, text=True)
    if check and result.returncode != 0:
        print(f"Command failed: {cmd}")
        print(f"stdout: {result.stdout}")
        print(f"stderr: {result.stderr}")
        sys.exit(1)
    return result


def build_wheel():
    """Build the wheel distribution."""
    print("Building wheel distribution...")
    run_command("python -m build")
    print("✓ Wheel built successfully")


def run_tests():
    """Run tests to ensure package is working."""
    print("Running tests...")
    run_command("pytest tests/ -v --tb=short")
    print("✓ Tests passed")


def test_install_in_fresh_venv():
    """Test installing the wheel in a fresh virtual environment."""
    print("Testing install in fresh virtual environment...")

    with tempfile.TemporaryDirectory() as temp_dir:
        # Create virtual environment
        venv_path = Path(temp_dir) / "test_venv"
        venv.create(venv_path, with_pip=True)

        # Get paths
        if sys.platform == "win32":
            python_exe = venv_path / "Scripts" / "python.exe"
            pip_exe = venv_path / "Scripts" / "pip.exe"
        else:
            python_exe = venv_path / "bin" / "python"
            pip_exe = venv_path / "bin" / "pip"

        # Install the wheel
        dist_dir = Path(__file__).parent.parent / "dist"
        wheel_files = list(dist_dir.glob("*.whl"))

        if not wheel_files:
            print("No wheel file found in dist/")
            sys.exit(1)

        wheel_file = wheel_files[0]  # Use the first wheel found

        print(f"Installing {wheel_file}...")
        run_command(f"{pip_exe} install {wheel_file}")

        # Test import
        print("Testing import...")
        result = run_command(f"{python_exe} -c \"import pheno; print('✓ Import successful')\"", check=False)
        if result.returncode != 0:
            print("Import test failed")
            sys.exit(1)

        print("✓ Fresh install test passed")


def publish_to_private_repo(repo_url=None):
    """Publish to private repository."""
    if repo_url:
        print(f"Publishing to private repository: {repo_url}")
        run_command(f"twine upload --repository-url {repo_url} dist/*")
    else:
        print("Publishing to PyPI (use --repository-url for private repo)")
        run_command("twine upload dist/*")
    print("✓ Published successfully")


def main():
    """Main build and release process."""
    import argparse

    parser = argparse.ArgumentParser(description="Build and release pheno-sdk")
    parser.add_argument("--skip-tests", action="store_true", help="Skip running tests")
    parser.add_argument("--skip-install-test", action="store_true", help="Skip fresh install test")
    parser.add_argument("--repository-url", help="Private repository URL")
    parser.add_argument("--dry-run", action="store_true", help="Build and test but don't publish")

    args = parser.parse_args()

    project_root = Path(__file__).parent.parent

    # Ensure we're in the project directory
    import os
    os.chdir(project_root)

    try:
        # Clean previous builds
        if Path("dist").exists():
            shutil.rmtree("dist")
        if Path("build").exists():
            shutil.rmtree("build")

        # Build wheel
        build_wheel()

        # Run tests
        if not args.skip_tests:
            run_tests()

        # Test fresh install
        if not args.skip_install_test:
            test_install_in_fresh_venv()

        # Publish
        if not args.dry_run:
            publish_to_private_repo(args.repository_url)
        else:
            print("Dry run - skipping publish")

        print("\n🎉 Build and release process completed successfully!")

    except Exception as e:
        print(f"\n❌ Build and release failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
