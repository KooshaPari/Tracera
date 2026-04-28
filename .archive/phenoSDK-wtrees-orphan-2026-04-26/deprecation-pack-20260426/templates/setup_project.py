#!/usr/bin/env python3
"""Pheno-SDK Project Setup Script.

This script applies standardized CI/CD templates to pheno-sdk projects.
It creates a consistent development environment across all projects.

Usage:
    python setup_project.py --project-name my-project --project-dir /path/to/project
    python setup_project.py --help
"""

import argparse
import shutil
import sys
from pathlib import Path


class ProjectSetup:
    """
    Handles setup of standardized CI/CD for pheno-sdk projects.
    """

    def __init__(self, templates_dir: Path):
        self.templates_dir = templates_dir
        self.replacements: dict[str, str] = {}

    def set_replacements(
        self,
        project_name: str,
        project_version: str = "0.1.0",
        project_description: str = "",
        keywords: str = "",
    ):
        """
        Set template replacement variables.
        """
        self.replacements = {
            "{{PROJECT_NAME}}": project_name,
            "{{PROJECT_VERSION}}": project_version,
            "{{PROJECT_DESCRIPTION}}": project_description,
            "{{KEYWORDS}}": keywords,
        }

    def replace_placeholders(self, content: str) -> str:
        """
        Replace placeholder variables in template content.
        """
        for placeholder, value in self.replacements.items():
            content = content.replace(placeholder, value)
        return content

    def copy_template(
        self, template_path: Path, target_path: Path, replace_placeholders: bool = True,
    ) -> bool:
        """
        Copy a template file to target location with optional placeholder replacement.
        """
        try:
            # Create target directory if it doesn't exist
            target_path.parent.mkdir(parents=True, exist_ok=True)

            # Read template content
            with open(template_path, encoding="utf-8") as f:
                content = f.read()

            # Replace placeholders if requested
            if replace_placeholders:
                content = self.replace_placeholders(content)

            # Write to target
            with open(target_path, "w", encoding="utf-8") as f:
                f.write(content)

            print(f"✅ Created: {target_path}")
            return True

        except Exception as e:
            print(f"❌ Failed to create {target_path}: {e}")
            return False

    def setup_pyproject_toml(self, project_dir: Path) -> bool:
        """
        Setup pyproject.toml from template.
        """
        template = self.templates_dir / "pyproject.toml.template"
        target = project_dir / "pyproject.toml"

        # Backup existing pyproject.toml
        if target.exists():
            backup = project_dir / "pyproject.toml.bak"
            shutil.copy2(target, backup)
            print(f"📁 Backed up existing pyproject.toml to {backup}")

        return self.copy_template(template, target)

    def setup_github_workflow(self, project_dir: Path) -> bool:
        """
        Setup GitHub Actions workflow.
        """
        template = self.templates_dir / ".github" / "workflows" / "ci.yml.template"
        target = project_dir / ".github" / "workflows" / "ci.yml"
        return self.copy_template(template, target)

    def setup_precommit(self, project_dir: Path) -> bool:
        """
        Setup pre-commit configuration.
        """
        template = self.templates_dir / ".pre-commit-config.yaml.template"
        target = project_dir / ".pre-commit-config.yaml"
        return self.copy_template(template, target)

    def setup_makefile(self, project_dir: Path) -> bool:
        """
        Setup Makefile.
        """
        template = self.templates_dir / "Makefile.template"
        target = project_dir / "Makefile"
        return self.copy_template(template, target)

    def setup_gitignore(self, project_dir: Path) -> bool:
        """
        Create a comprehensive .gitignore file.
        """
        gitignore_content = """# Pheno-SDK Standard .gitignore

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
pip-wheel-metadata/
share/python-wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# Virtual environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/
.zen_venv/

# Testing
.coverage
.pytest_cache/
.tox/
.nox/
coverage.xml
*.cover
*.py,cover
.hypothesis/
htmlcov/
.coverage.*
test-results.xml

# MyPy
.mypy_cache/
.dmypy.json
dmypy.json

# Ruff
.ruff_cache/

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Logs
*.log
logs/

# Security
bandit-report.json
.env.local
.env.production
*.pem
*.key

# Documentation
docs/_build/
site/

# Project specific
temp/
tmp/
*.tmp
.cache/
"""

        target = project_dir / ".gitignore"
        try:
            with open(target, "w", encoding="utf-8") as f:
                f.write(gitignore_content)
            print(f"✅ Created: {target}")
            return True
        except Exception as e:
            print(f"❌ Failed to create .gitignore: {e}")
            return False

    def setup_full_project(
        self,
        project_name: str,
        project_dir: Path,
        project_version: str = "0.1.0",
        project_description: str = "",
        keywords: str = "",
    ) -> bool:
        """
        Setup complete standardized CI/CD for a project.
        """

        print(f"🚀 Setting up standardized CI/CD for {project_name}")
        print(f"📂 Target directory: {project_dir}")

        # Ensure project directory exists
        project_dir.mkdir(parents=True, exist_ok=True)

        # Set replacements
        self.set_replacements(project_name, project_version, project_description, keywords)

        # Track success
        success_count = 0
        total_tasks = 5

        # Setup each component
        tasks = [
            ("pyproject.toml", self.setup_pyproject_toml),
            ("GitHub workflow", self.setup_github_workflow),
            ("Pre-commit config", self.setup_precommit),
            ("Makefile", self.setup_makefile),
            (".gitignore", self.setup_gitignore),
        ]

        for task_name, task_func in tasks:
            print(f"\n📋 Setting up {task_name}...")
            if task_func(project_dir):
                success_count += 1
            else:
                print(f"⚠️  Failed to setup {task_name}")

        # Summary
        print(f"\n📊 Setup complete: {success_count}/{total_tasks} tasks successful")

        if success_count == total_tasks:
            print(f"🎉 All CI/CD components set up successfully for {project_name}!")
            print("\n📝 Next steps:")
            print(f"   1. cd {project_dir}")
            print("   2. make setup-dev")
            print("   3. Review and customize the generated files")
            print("   4. Initialize git repository if needed")
            return True
        print(f"⚠️  Setup completed with {total_tasks - success_count} warnings")
        return False


def main():
    parser = argparse.ArgumentParser(description="Setup standardized CI/CD for pheno-sdk projects")
    parser.add_argument(
        "--project-name", required=True, help="Name of the project (e.g., 'tui-kit', 'mcp-sdk-kit')",
    )
    parser.add_argument(
        "--project-dir", type=Path, help="Target project directory (default: current directory)",
    )
    parser.add_argument(
        "--project-version", default="0.1.0", help="Initial project version (default: 0.1.0)",
    )
    parser.add_argument("--description", default="", help="Project description")
    parser.add_argument("--keywords", default="", help="Comma-separated keywords for the project")
    parser.add_argument(
        "--templates-dir",
        type=Path,
        help="Path to templates directory (default: detect automatically)",
    )

    args = parser.parse_args()

    # Determine templates directory
    if args.templates_dir:
        templates_dir = args.templates_dir
    else:
        # Assume script is in templates directory
        templates_dir = Path(__file__).parent

    if not templates_dir.exists():
        print(f"❌ Templates directory not found: {templates_dir}")
        sys.exit(1)

    # Determine project directory
    project_dir = args.project_dir or Path.cwd()

    # Setup the project
    setup = ProjectSetup(templates_dir)
    success = setup.setup_full_project(
        project_name=args.project_name,
        project_dir=project_dir,
        project_version=args.project_version,
        project_description=args.description,
        keywords=args.keywords,
    )

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
