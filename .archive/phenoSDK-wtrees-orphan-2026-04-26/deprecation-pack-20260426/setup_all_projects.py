#!/usr/bin/env python3
"""
Setup All Pheno-SDK Projects
=============================

Applies standardized CI/CD configuration to all pheno-sdk kit projects.
Uses the templates in /templates directory.

Usage:
    python setup_all_projects.py [--dry-run] [--skip-existing]
"""

import argparse
import sys
from pathlib import Path

# Import the setup script
sys.path.insert(0, str(Path(__file__).parent / "templates"))
from setup_project import ProjectSetup

# List of pheno-sdk projects (kits) to setup
PHENO_SDK_PROJECTS = [
    {
        "name": "adapter-kit",
        "description": "Adapter patterns and base classes for pheno-sdk",
        "keywords": "adapters,patterns,factory,pheno-sdk",
    },
    {
        "name": "api-gateway-kit",
        "description": "API gateway components for pheno-sdk",
        "keywords": "api,gateway,routing,pheno-sdk",
    },
    {
        "name": "authkit-client",
        "description": "Authentication client for pheno-sdk",
        "keywords": "auth,authentication,client,pheno-sdk",
    },
    {
        "name": "build-analyzer-kit",
        "description": "Build analysis tools for pheno-sdk",
        "keywords": "build,analysis,tools,pheno-sdk",
    },
    {
        "name": "cli-builder-kit",
        "description": "CLI builder with TUI integration for pheno-sdk",
        "keywords": "cli,tui,builder,terminal,pheno-sdk",
    },
    {
        "name": "config-kit",
        "description": "Configuration management with interactive wizards for pheno-sdk",
        "keywords": "config,configuration,wizard,pheno-sdk",
    },
    {
        "name": "db-kit",
        "description": "Database utilities for pheno-sdk",
        "keywords": "database,db,utilities,pheno-sdk",
    },
    {
        "name": "deploy-kit",
        "description": "Deployment orchestration with TUI for pheno-sdk",
        "keywords": "deployment,orchestration,tui,pheno-sdk",
    },
    {
        "name": "domain-kit",
        "description": "Domain modeling utilities for pheno-sdk",
        "keywords": "domain,modeling,ddd,pheno-sdk",
    },
    {
        "name": "event-kit",
        "description": "Event handling and pub/sub for pheno-sdk",
        "keywords": "events,pubsub,messaging,pheno-sdk",
    },
    {
        "name": "filewatch-kit",
        "description": "File watching utilities for pheno-sdk",
        "keywords": "filewatch,watcher,files,pheno-sdk",
    },
    {
        "name": "mcp-infra-sdk",
        "description": "MCP infrastructure SDK for pheno-sdk",
        "keywords": "mcp,infrastructure,sdk,pheno-sdk",
    },
    {
        "name": "mcp-sdk-kit",
        "description": "MCP SDK components for pheno-sdk",
        "keywords": "mcp,sdk,components,pheno-sdk",
    },
    {
        "name": "multi-cloud-deploy-kit",
        "description": "Multi-cloud deployment tools for pheno-sdk",
        "keywords": "cloud,deployment,multi-cloud,pheno-sdk",
    },
    {
        "name": "observability-kit",
        "description": "Observability and monitoring for pheno-sdk",
        "keywords": "observability,monitoring,metrics,pheno-sdk",
    },
    {
        "name": "orchestrator-kit",
        "description": "Orchestration utilities for pheno-sdk",
        "keywords": "orchestration,workflow,pheno-sdk",
    },
    {
        "name": "process-monitor-sdk",
        "description": "Process monitoring SDK for pheno-sdk",
        "keywords": "process,monitoring,sdk,pheno-sdk",
    },
    {
        "name": "pydevkit",
        "description": "Python development kit for pheno-sdk",
        "keywords": "python,development,devkit,pheno-sdk",
    },
    {
        "name": "resource-management-kit",
        "description": "Resource management utilities for pheno-sdk",
        "keywords": "resources,management,pheno-sdk",
    },
    {
        "name": "storage-kit",
        "description": "Storage utilities for pheno-sdk",
        "keywords": "storage,files,s3,pheno-sdk",
    },
    {
        "name": "stream-kit",
        "description": "Stream processing utilities for pheno-sdk",
        "keywords": "streams,processing,async,pheno-sdk",
    },
    {
        "name": "tui_kit",
        "description": "Terminal UI toolkit with context-aware components for pheno-sdk",
        "keywords": "tui,terminal,ui,components,pheno-sdk",
    },
    {
        "name": "vector-kit",
        "description": "Vector operations and embeddings for pheno-sdk",
        "keywords": "vectors,embeddings,ml,pheno-sdk",
    },
    {
        "name": "workflow-kit",
        "description": "Workflow management for pheno-sdk",
        "keywords": "workflow,automation,pheno-sdk",
    },
]


def setup_project(
    project_info: dict, pheno_sdk_root: Path, dry_run: bool = False, skip_existing: bool = False,
) -> bool:
    """Setup a single project with CI/CD templates.

    Args:
        project_info: Project information dictionary
        pheno_sdk_root: Root directory of pheno-sdk
        dry_run: If True, only show what would be done
        skip_existing: If True, skip projects that already have pyproject.toml

    Returns:
        True if successful, False otherwise
    """
    project_name = project_info["name"]
    project_dir = pheno_sdk_root / project_name

    if not project_dir.exists():
        print(f"⚠️  Skipping {project_name}: directory not found")
        return False

    # Check if already setup
    if skip_existing and (project_dir / "pyproject.toml").exists():
        print(f"⏭️  Skipping {project_name}: already has pyproject.toml")
        return True

    print(f"\n{'[DRY RUN] ' if dry_run else ''}🔧 Setting up {project_name}...")
    print(f"   Location: {project_dir}")

    if dry_run:
        print("   Would create:")
        print("     - pyproject.toml")
        print("     - Makefile")
        print("     - .pre-commit-config.yaml")
        print("     - .github/workflows/ci.yml")
        print("     - .gitignore")
        return True

    # Initialize setup
    templates_dir = pheno_sdk_root / "templates"
    setup = ProjectSetup(templates_dir)

    # Set project-specific replacements
    setup.set_replacements(
        project_name=project_name,
        project_version="0.1.0",
        project_description=project_info["description"],
        keywords=project_info["keywords"],
    )

    # Apply templates
    success = True
    success &= setup.setup_pyproject_toml(project_dir)
    success &= setup.setup_makefile(project_dir)
    success &= setup.setup_precommit(project_dir)
    success &= setup.setup_github_workflow(project_dir)
    success &= setup.setup_gitignore(project_dir)

    if success:
        print(f"✅ Successfully setup {project_name}")
    else:
        print(f"⚠️  Some errors occurred setting up {project_name}")

    return success


def main():
    """
    Main entry point.
    """
    parser = argparse.ArgumentParser(description="Setup CI/CD for all pheno-sdk projects")
    parser.add_argument(
        "--dry-run", action="store_true", help="Show what would be done without making changes",
    )
    parser.add_argument(
        "--skip-existing",
        action="store_true",
        help="Skip projects that already have pyproject.toml",
    )
    parser.add_argument(
        "--projects", nargs="+", help="Only setup specific projects (space-separated names)",
    )

    args = parser.parse_args()

    # Find pheno-sdk root
    pheno_sdk_root = Path(__file__).parent.resolve()
    print(f"📁 Pheno-SDK root: {pheno_sdk_root}")
    print(f"📦 Projects to setup: {len(PHENO_SDK_PROJECTS)}")

    if args.dry_run:
        print("\n🔍 DRY RUN MODE - No changes will be made\n")

    # Filter projects if specific ones requested
    projects_to_setup = PHENO_SDK_PROJECTS
    if args.projects:
        projects_to_setup = [p for p in PHENO_SDK_PROJECTS if p["name"] in args.projects]
        print(f"🎯 Filtering to {len(projects_to_setup)} specific projects")

    # Setup each project
    results = []
    for project_info in projects_to_setup:
        result = setup_project(
            project_info, pheno_sdk_root, dry_run=args.dry_run, skip_existing=args.skip_existing,
        )
        results.append((project_info["name"], result))

    # Summary
    print("\n" + "=" * 60)
    print("SETUP SUMMARY")
    print("=" * 60)

    successful = [name for name, result in results if result]
    failed = [name for name, result in results if not result]

    print(f"✅ Successful: {len(successful)}")
    print(f"❌ Failed: {len(failed)}")

    if failed:
        print(f"\nFailed projects: {', '.join(failed)}")

    print("\n" + "=" * 60)
    print("NEXT STEPS")
    print("=" * 60)
    print("1. Review generated files in each project")
    print("2. Run 'make install' in each project to setup development environment")
    print("3. Run 'make test' to ensure tests pass")
    print("4. Commit the changes to git")

    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main())
