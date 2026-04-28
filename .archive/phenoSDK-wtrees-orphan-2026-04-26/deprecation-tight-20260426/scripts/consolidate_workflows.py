#!/usr/bin/env python3
"""
Workflow Consolidation Script
Analyzes existing workflows and provides migration guidance.
"""

import argparse
from collections import defaultdict
from pathlib import Path
from typing import Any

import yaml


class WorkflowConsolidator:
    """Consolidate GitHub Actions workflows."""

    def __init__(self, workflows_dir: str):
        self.workflows_dir = Path(workflows_dir)
        self.workflows = {}
        self.consolidation_map = {}

    def analyze_workflows(self) -> dict[str, Any]:
        """Analyze all workflows and create consolidation plan."""
        print("🔍 Analyzing existing workflows...")

        # Load all workflow files
        for workflow_file in self.workflows_dir.glob("*.yml"):
            if workflow_file.name == "consolidated-ci.yml":
                continue

            try:
                with open(workflow_file) as f:
                    workflow_data = yaml.safe_load(f)
                    self.workflows[workflow_file.name] = workflow_data
            except Exception as e:
                print(f"Warning: Could not parse {workflow_file}: {e}")

        # Categorize workflows
        categories = self._categorize_workflows()

        # Create consolidation plan
        consolidation_plan = self._create_consolidation_plan(categories)

        return {
            "total_workflows": len(self.workflows),
            "categories": categories,
            "consolidation_plan": consolidation_plan,
            "migration_steps": self._generate_migration_steps(consolidation_plan),
        }

    def _categorize_workflows(self) -> dict[str, list[str]]:
        """Categorize workflows by their purpose."""
        categories = defaultdict(list)

        for workflow_name, workflow_data in self.workflows.items():
            # Determine category based on workflow name and content
            if "quality" in workflow_name.lower() or "lint" in workflow_name.lower():
                categories["code_quality"].append(workflow_name)
            elif "test" in workflow_name.lower():
                categories["testing"].append(workflow_name)
            elif "security" in workflow_name.lower():
                categories["security"].append(workflow_name)
            elif "architect" in workflow_name.lower():
                categories["architecture"].append(workflow_name)
            elif "doc" in workflow_name.lower():
                categories["documentation"].append(workflow_name)
            elif "build" in workflow_name.lower() or "ci" in workflow_name.lower():
                categories["build_ci"].append(workflow_name)
            elif "deploy" in workflow_name.lower():
                categories["deployment"].append(workflow_name)
            elif "release" in workflow_name.lower() or "version" in workflow_name.lower():
                categories["release"].append(workflow_name)
            elif "monitor" in workflow_name.lower():
                categories["monitoring"].append(workflow_name)
            elif "performance" in workflow_name.lower():
                categories["performance"].append(workflow_name)
            else:
                categories["other"].append(workflow_name)

        return dict(categories)

    def _create_consolidation_plan(self, categories: dict[str, list[str]]) -> dict[str, Any]:
        """Create a consolidation plan."""
        plan = {
            "consolidated_workflows": {
                "consolidated-ci.yml": {
                    "purpose": "Main CI/CD pipeline",
                    "includes": [],
                    "replaces": [],
                },
            },
            "workflows_to_remove": [],
            "workflows_to_keep": [],
            "workflows_to_modify": [],
        }

        # Map old workflows to new consolidated workflow
        main_workflow = plan["consolidated_workflows"]["consolidated-ci.yml"]

        # Add workflows that should be consolidated
        for category, workflows in categories.items():
            if category in ["code_quality", "testing", "security", "architecture", "build_ci"]:
                main_workflow["includes"].extend(workflows)
                main_workflow["replaces"].extend(workflows)
                plan["workflows_to_remove"].extend(workflows)
            elif category in ["deployment", "release"]:
                # Keep these as separate workflows for now
                plan["workflows_to_keep"].extend(workflows)
            elif category in ["monitoring", "performance"]:
                # These can be integrated into main workflow conditionally
                main_workflow["includes"].extend(workflows)
                plan["workflows_to_modify"].extend(workflows)

        return plan

    def _generate_migration_steps(self, consolidation_plan: dict[str, Any]) -> list[str]:
        """Generate step-by-step migration instructions."""
        steps = [
            "1. Backup existing workflows directory",
            "2. Test the new consolidated-ci.yml workflow",
            "3. Gradually disable old workflows by adding 'if: false' to their triggers",
            "4. Monitor the consolidated workflow for a few days",
            "5. Remove disabled workflows once confirmed working",
        ]

        # Add specific steps for each category
        if consolidation_plan["workflows_to_remove"]:
            steps.append(f"6. Remove {len(consolidation_plan['workflows_to_remove'])} workflows: {', '.join(consolidation_plan['workflows_to_remove'])}")

        if consolidation_plan["workflows_to_keep"]:
            steps.append(f"7. Keep {len(consolidation_plan['workflows_to_keep'])} workflows: {', '.join(consolidation_plan['workflows_to_keep'])}")

        return steps

    def generate_migration_report(self, analysis: dict[str, Any]) -> str:
        """Generate a detailed migration report."""
        report = f"""
# Workflow Consolidation Report

## Summary
- **Total workflows analyzed**: {analysis['total_workflows']}
- **Workflows to consolidate**: {len(analysis['consolidation_plan']['workflows_to_remove'])}
- **Workflows to keep**: {len(analysis['consolidation_plan']['workflows_to_keep'])}

## Workflow Categories

"""

        for category, workflows in analysis["categories"].items():
            report += f"### {category.replace('_', ' ').title()}\n"
            for workflow in workflows:
                report += f"- {workflow}\n"
            report += "\n"

        report += """
## Consolidation Plan

### New Consolidated Workflow: `consolidated-ci.yml`
This workflow combines multiple existing workflows into a single, efficient pipeline:

**Phases:**
1. **Preparation**: Environment setup and change detection
2. **Code Quality**: Linting, formatting, type checking
3. **Architecture**: Design pattern validation, complexity analysis
4. **Security**: Vulnerability scanning, dependency checks
5. **Testing**: Unit tests, integration tests
6. **Documentation**: Markdown validation, doc generation
7. **Performance**: Benchmarking (conditional)
8. **Quality Gates**: Final validation and scoring
9. **Deployment**: Build and deploy (main branch only)

### Migration Steps

"""

        for step in analysis["migration_steps"]:
            report += f"{step}\n"

        report += """
## Benefits of Consolidation

1. **Reduced Complexity**: Single workflow instead of 36 separate ones
2. **Better Performance**: Parallel execution where possible
3. **Conditional Execution**: Only run what's needed based on changes
4. **Unified Reporting**: Single quality score and comprehensive reports
5. **Easier Maintenance**: One workflow to maintain instead of many
6. **Cost Optimization**: Reduced GitHub Actions minutes usage

## Risk Mitigation

1. **Gradual Migration**: Disable old workflows gradually
2. **Monitoring**: Watch for any issues during transition
3. **Rollback Plan**: Keep old workflows as backup initially
4. **Testing**: Thoroughly test consolidated workflow before full migration

"""

        return report

    def create_workflow_archive(self) -> None:
        """Create an archive of old workflows before consolidation."""
        archive_dir = self.workflows_dir / "archive"
        archive_dir.mkdir(exist_ok=True)

        print(f"📁 Creating workflow archive in {archive_dir}")

        for workflow_file in self.workflows_dir.glob("*.yml"):
            if workflow_file.name != "consolidated-ci.yml":
                # Copy to archive
                import shutil
                shutil.copy2(workflow_file, archive_dir / workflow_file.name)
                print(f"  Archived: {workflow_file.name}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Consolidate GitHub Actions workflows")
    parser.add_argument("workflows_dir", help="Path to workflows directory")
    parser.add_argument("--analyze-only", action="store_true", help="Only analyze, don't create archive")
    parser.add_argument("--output", "-o", help="Output report file")

    args = parser.parse_args()

    consolidator = WorkflowConsolidator(args.workflows_dir)

    # Analyze workflows
    analysis = consolidator.analyze_workflows()

    # Generate report
    report = consolidator.generate_migration_report(analysis)

    # Output report
    if args.output:
        with open(args.output, "w") as f:
            f.write(report)
        print(f"📄 Report saved to {args.output}")
    else:
        print(report)

    # Create archive if not analyze-only
    if not args.analyze_only:
        consolidator.create_workflow_archive()
        print("✅ Workflow archive created")

    # Print summary
    print("\n📊 Consolidation Summary:")
    print(f"  Total workflows: {analysis['total_workflows']}")
    print(f"  To consolidate: {len(analysis['consolidation_plan']['workflows_to_remove'])}")
    print(f"  To keep: {len(analysis['consolidation_plan']['workflows_to_keep'])}")
    print(f"  To modify: {len(analysis['consolidation_plan']['workflows_to_modify'])}")


if __name__ == "__main__":
    main()
