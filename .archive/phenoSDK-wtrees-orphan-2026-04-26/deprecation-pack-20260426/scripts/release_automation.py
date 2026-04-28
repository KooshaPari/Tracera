#!/usr/bin/env python3
"""
Release Automation System
Comprehensive release automation with semantic versioning.
"""

import argparse
import json
import re
import subprocess
import time
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


@dataclass
class ReleaseInfo:
    """Release information."""
    version: str
    release_type: str  # "major", "minor", "patch", "prerelease"
    changelog: str
    release_notes: str
    git_tag: str
    timestamp: float
    author: str
    commit_hash: str


@dataclass
class ReleaseStep:
    """Release step information."""
    name: str
    status: str  # "pending", "running", "completed", "failed"
    duration: float
    output: str
    error: str | None = None


class ReleaseAutomation:
    """Comprehensive release automation system."""

    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.reports_dir = self.project_root / "reports" / "releases"
        self.reports_dir.mkdir(parents=True, exist_ok=True)

        self.release_steps = []
        self.current_release = None

        # Release configuration
        self.config = {
            "version_file": "pyproject.toml",
            "changelog_file": "CHANGELOG.md",
            "release_branch": "main",
            "prerelease_branch": "develop",
            "tag_prefix": "v",
            "build_artifacts": True,
            "run_tests": True,
            "create_github_release": False,  # Would need GitHub API
            "notify_team": False,  # Would need notification system
        }

    def create_release(self, release_type: str, prerelease: bool = False,
                      custom_version: str | None = None) -> dict[str, Any]:
        """Create a new release."""
        print(f"🚀 Creating {release_type} release...")

        # Step 1: Validate environment
        self._add_step("validate_environment", "Validate release environment")
        if not self._validate_environment():
            return self._generate_release_report()

        # Step 2: Get current version
        self._add_step("get_current_version", "Get current version")
        current_version = self._get_current_version()
        if not current_version:
            return self._generate_release_report()

        # Step 3: Calculate new version
        self._add_step("calculate_version", "Calculate new version")
        new_version = self._calculate_new_version(current_version, release_type, prerelease, custom_version)
        if not new_version:
            return self._generate_release_report()

        # Step 4: Update version files
        self._add_step("update_version", "Update version files")
        if not self._update_version_files(new_version):
            return self._generate_release_report()

        # Step 5: Generate changelog
        self._add_step("generate_changelog", "Generate changelog")
        changelog = self._generate_changelog(new_version, release_type)
        if not changelog:
            return self._generate_release_report()

        # Step 6: Generate release notes
        self._add_step("generate_release_notes", "Generate release notes")
        release_notes = self._generate_release_notes(new_version, changelog)

        # Step 7: Run tests
        if self.config["run_tests"]:
            self._add_step("run_tests", "Run test suite")
            if not self._run_tests():
                return self._generate_release_report()

        # Step 8: Build artifacts
        if self.config["build_artifacts"]:
            self._add_step("build_artifacts", "Build release artifacts")
            if not self._build_artifacts():
                return self._generate_release_report()

        # Step 9: Create git tag
        self._add_step("create_git_tag", "Create git tag")
        if not self._create_git_tag(new_version):
            return self._generate_release_report()

        # Step 10: Push changes
        self._add_step("push_changes", "Push changes to remote")
        if not self._push_changes():
            return self._generate_release_report()

        # Step 11: Create GitHub release (if enabled)
        if self.config["create_github_release"]:
            self._add_step("create_github_release", "Create GitHub release")
            self._create_github_release(new_version, release_notes)

        # Step 12: Notify team (if enabled)
        if self.config["notify_team"]:
            self._add_step("notify_team", "Notify team")
            self._notify_team(new_version, release_notes)

        # Create release info
        self.current_release = ReleaseInfo(
            version=new_version,
            release_type=release_type,
            changelog=changelog,
            release_notes=release_notes,
            git_tag=f"{self.config['tag_prefix']}{new_version}",
            timestamp=time.time(),
            author=self._get_git_author(),
            commit_hash=self._get_current_commit(),
        )

        # Generate final report
        return self._generate_release_report()

    def _add_step(self, name: str, description: str) -> None:
        """Add a release step."""
        step = ReleaseStep(
            name=name,
            status="running",
            duration=0.0,
            output="",
            error=None,
        )
        self.release_steps.append(step)
        print(f"  📋 {description}...")

    def _complete_step(self, success: bool, output: str = "", error: str = "") -> None:
        """Complete the current step."""
        if self.release_steps:
            current_step = self.release_steps[-1]
            current_step.status = "completed" if success else "failed"
            current_step.output = output
            current_step.error = error if not success else None
            current_step.duration = time.time() - current_step.duration  # This is a bit hacky

    def _validate_environment(self) -> bool:
        """Validate the release environment."""
        try:
            # Check if we're in a git repository
            result = subprocess.run(["git", "status"], check=False, capture_output=True, text=True, cwd=self.project_root)
            if result.returncode != 0:
                self._complete_step(False, "", "Not in a git repository")
                return False

            # Check if working directory is clean
            result = subprocess.run(["git", "diff", "--quiet"], check=False, capture_output=True, text=True, cwd=self.project_root)
            if result.returncode != 0:
                self._complete_step(False, "", "Working directory is not clean")
                return False

            # Check if we're on the correct branch
            result = subprocess.run(["git", "branch", "--show-current"], check=False, capture_output=True, text=True, cwd=self.project_root)
            current_branch = result.stdout.strip()
            if current_branch != self.config["release_branch"]:
                self._complete_step(False, "", f"Not on release branch ({self.config['release_branch']})")
                return False

            # Check if version file exists
            version_file = self.project_root / self.config["version_file"]
            if not version_file.exists():
                self._complete_step(False, "", f"Version file not found: {self.config['version_file']}")
                return False

            self._complete_step(True, "Environment validation passed")
            return True

        except Exception as e:
            self._complete_step(False, "", f"Environment validation failed: {e}")
            return False

    def _get_current_version(self) -> str | None:
        """Get the current version from version file."""
        try:
            version_file = self.project_root / self.config["version_file"]

            if version_file.suffix == ".toml":
                # Read from pyproject.toml
                with open(version_file) as f:
                    content = f.read()

                # Simple regex to find version
                version_match = re.search(r'version\s*=\s*["\']([^"\']+)["\']', content)
                if version_match:
                    version = version_match.group(1)
                    self._complete_step(True, f"Current version: {version}")
                    return version
                self._complete_step(False, "", "Version not found in pyproject.toml")
                return None

            if version_file.name == "__init__.py":
                # Read from __init__.py
                with open(version_file) as f:
                    content = f.read()

                version_match = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', content)
                if version_match:
                    version = version_match.group(1)
                    self._complete_step(True, f"Current version: {version}")
                    return version
                self._complete_step(False, "", "Version not found in __init__.py")
                return None

            self._complete_step(False, "", f"Unsupported version file format: {version_file.suffix}")
            return None

        except Exception as e:
            self._complete_step(False, "", f"Error reading version: {e}")
            return None

    def _calculate_new_version(self, current_version: str, release_type: str,
                             prerelease: bool, custom_version: str | None) -> str | None:
        """Calculate the new version number."""
        try:
            if custom_version:
                new_version = custom_version
            else:
                # Parse current version
                version_parts = current_version.split(".")
                major = int(version_parts[0])
                minor = int(version_parts[1]) if len(version_parts) > 1 else 0
                patch = int(version_parts[2]) if len(version_parts) > 2 else 0

                # Calculate new version
                if release_type == "major":
                    major += 1
                    minor = 0
                    patch = 0
                elif release_type == "minor":
                    minor += 1
                    patch = 0
                elif release_type == "patch":
                    patch += 1
                else:
                    self._complete_step(False, "", f"Invalid release type: {release_type}")
                    return None

                new_version = f"{major}.{minor}.{patch}"

                # Add prerelease suffix if needed
                if prerelease:
                    new_version += "-rc.1"

            self._complete_step(True, f"New version: {new_version}")
            return new_version

        except Exception as e:
            self._complete_step(False, "", f"Error calculating version: {e}")
            return None

    def _update_version_files(self, new_version: str) -> bool:
        """Update version in all relevant files."""
        try:
            version_file = self.project_root / self.config["version_file"]

            if version_file.suffix == ".toml":
                # Update pyproject.toml
                with open(version_file) as f:
                    content = f.read()

                # Replace version
                new_content = re.sub(
                    r'version\s*=\s*["\'][^"\']+["\']',
                    f'version = "{new_version}"',
                    content,
                )

                with open(version_file, "w") as f:
                    f.write(new_content)

            # Also update __init__.py if it exists
            init_file = self.project_root / "src" / "pheno" / "__init__.py"
            if init_file.exists():
                with open(init_file) as f:
                    content = f.read()

                new_content = re.sub(
                    r'__version__\s*=\s*["\'][^"\']+["\']',
                    f'__version__ = "{new_version}"',
                    content,
                )

                with open(init_file, "w") as f:
                    f.write(new_content)

            self._complete_step(True, f"Updated version to {new_version}")
            return True

        except Exception as e:
            self._complete_step(False, "", f"Error updating version files: {e}")
            return False

    def _generate_changelog(self, new_version: str, release_type: str) -> str | None:
        """Generate changelog for the new version."""
        try:
            changelog_file = self.project_root / self.config["changelog_file"]

            # Get git commits since last tag
            commits = self._get_commits_since_last_tag()

            # Categorize commits
            features = []
            fixes = []
            breaking = []
            other = []

            for commit in commits:
                message = commit.get("message", "")
                if message.startswith("feat:"):
                    features.append(message)
                elif message.startswith("fix:"):
                    fixes.append(message)
                elif message.startswith("BREAKING CHANGE:") or "!" in message:
                    breaking.append(message)
                else:
                    other.append(message)

            # Generate changelog entry
            changelog_entry = f"""## [{new_version}] - {datetime.now().strftime('%Y-%m-%d')}

### Added
"""

            if features:
                for feature in features:
                    changelog_entry += f"- {feature}\n"
            else:
                changelog_entry += "- No new features\n"

            changelog_entry += "\n### Changed\n"
            if other:
                for change in other:
                    changelog_entry += f"- {change}\n"
            else:
                changelog_entry += "- No changes\n"

            changelog_entry += "\n### Fixed\n"
            if fixes:
                for fix in fixes:
                    changelog_entry += f"- {fix}\n"
            else:
                changelog_entry += "- No fixes\n"

            if breaking:
                changelog_entry += "\n### Breaking Changes\n"
                for breaking_change in breaking:
                    changelog_entry += f"- {breaking_change}\n"

            changelog_entry += "\n"

            # Update changelog file
            if changelog_file.exists():
                with open(changelog_file) as f:
                    content = f.read()

                # Insert new entry after the first heading
                lines = content.split("\n")
                insert_index = 1
                for i, line in enumerate(lines):
                    if line.startswith("## [") and i > 0:
                        insert_index = i
                        break

                lines.insert(insert_index, changelog_entry)
                new_content = "\n".join(lines)
            else:
                new_content = f"# Changelog\n\n{changelog_entry}"

            with open(changelog_file, "w") as f:
                f.write(new_content)

            self._complete_step(True, f"Generated changelog for {new_version}")
            return changelog_entry

        except Exception as e:
            self._complete_step(False, "", f"Error generating changelog: {e}")
            return None

    def _generate_release_notes(self, new_version: str, changelog: str) -> str:
        """Generate release notes for the new version."""
        try:
            # Extract key information from changelog
            lines = changelog.split("\n")

            features = []
            fixes = []
            breaking = []

            current_section = None
            for line in lines:
                if line.startswith("### Added"):
                    current_section = "features"
                elif line.startswith("### Fixed"):
                    current_section = "fixes"
                elif line.startswith("### Breaking Changes"):
                    current_section = "breaking"
                elif line.startswith("###") or line.startswith("##"):
                    current_section = None
                elif line.startswith("- ") and current_section:
                    item = line[2:].strip()
                    if current_section == "features":
                        features.append(item)
                    elif current_section == "fixes":
                        fixes.append(item)
                    elif current_section == "breaking":
                        breaking.append(item)

            # Generate release notes
            release_notes = f"""# Release {new_version}

## What's New

"""

            if features:
                release_notes += "### ✨ New Features\n\n"
                for feature in features:
                    release_notes += f"- {feature}\n"
                release_notes += "\n"

            if fixes:
                release_notes += "### 🐛 Bug Fixes\n\n"
                for fix in fixes:
                    release_notes += f"- {fix}\n"
                release_notes += "\n"

            if breaking:
                release_notes += "### ⚠️ Breaking Changes\n\n"
                for breaking_change in breaking:
                    release_notes += f"- {breaking_change}\n"
                release_notes += "\n"

            release_notes += f"""## Installation

```bash
pip install pheno-sdk=={new_version}
```

## Full Changelog

See [CHANGELOG.md](CHANGELOG.md) for the complete list of changes.

---

*This release was automatically generated.*
"""

            self._complete_step(True, f"Generated release notes for {new_version}")
            return release_notes

        except Exception as e:
            self._complete_step(False, "", f"Error generating release notes: {e}")
            return ""

    def _run_tests(self) -> bool:
        """Run the test suite."""
        try:
            result = subprocess.run([
                "python", "-m", "pytest", "tests/", "-v", "--tb=short",
            ], check=False, capture_output=True, text=True, cwd=self.project_root, timeout=300)

            if result.returncode == 0:
                self._complete_step(True, "All tests passed")
                return True
            self._complete_step(False, "", f"Tests failed: {result.stderr}")
            return False

        except subprocess.TimeoutExpired:
            self._complete_step(False, "", "Tests timed out")
            return False
        except Exception as e:
            self._complete_step(False, "", f"Error running tests: {e}")
            return False

    def _build_artifacts(self) -> bool:
        """Build release artifacts."""
        try:
            # Build wheel
            result = subprocess.run([
                "python", "-m", "build",
            ], check=False, capture_output=True, text=True, cwd=self.project_root, timeout=300)

            if result.returncode == 0:
                self._complete_step(True, "Build artifacts created successfully")
                return True
            self._complete_step(False, "", f"Build failed: {result.stderr}")
            return False

        except subprocess.TimeoutExpired:
            self._complete_step(False, "", "Build timed out")
            return False
        except Exception as e:
            self._complete_step(False, "", f"Error building artifacts: {e}")
            return False

    def _create_git_tag(self, new_version: str) -> bool:
        """Create a git tag for the release."""
        try:
            tag_name = f"{self.config['tag_prefix']}{new_version}"

            # Create tag
            result = subprocess.run([
                "git", "tag", "-a", tag_name, "-m", f"Release {new_version}",
            ], check=False, capture_output=True, text=True, cwd=self.project_root)

            if result.returncode == 0:
                self._complete_step(True, f"Created tag: {tag_name}")
                return True
            self._complete_step(False, "", f"Failed to create tag: {result.stderr}")
            return False

        except Exception as e:
            self._complete_step(False, "", f"Error creating git tag: {e}")
            return False

    def _push_changes(self) -> bool:
        """Push changes to remote repository."""
        try:
            # Add all changes
            subprocess.run(["git", "add", "."], check=False, cwd=self.project_root)

            # Commit changes
            result = subprocess.run([
                "git", "commit", "-m", f"Release {self.current_release.version if self.current_release else 'unknown'}",
            ], check=False, capture_output=True, text=True, cwd=self.project_root)

            if result.returncode != 0:
                self._complete_step(False, "", f"Failed to commit changes: {result.stderr}")
                return False

            # Push changes
            result = subprocess.run([
                "git", "push", "origin", self.config["release_branch"],
            ], check=False, capture_output=True, text=True, cwd=self.project_root)

            if result.returncode != 0:
                self._complete_step(False, "", f"Failed to push changes: {result.stderr}")
                return False

            # Push tags
            result = subprocess.run([
                "git", "push", "origin", "--tags",
            ], check=False, capture_output=True, text=True, cwd=self.project_root)

            if result.returncode != 0:
                self._complete_step(False, "", f"Failed to push tags: {result.stderr}")
                return False

            self._complete_step(True, "Changes pushed successfully")
            return True

        except Exception as e:
            self._complete_step(False, "", f"Error pushing changes: {e}")
            return False

    def _create_github_release(self, new_version: str, release_notes: str) -> None:
        """Create GitHub release (placeholder)."""
        # This would use GitHub API to create a release
        # For now, just log the action
        print(f"  📝 Would create GitHub release for {new_version}")
        self._complete_step(True, "GitHub release creation (simulated)")

    def _notify_team(self, new_version: str, release_notes: str) -> None:
        """Notify team about release (placeholder)."""
        # This would send notifications to team
        # For now, just log the action
        print(f"  📧 Would notify team about release {new_version}")
        self._complete_step(True, "Team notification (simulated)")

    def _get_commits_since_last_tag(self) -> list[dict[str, str]]:
        """Get commits since the last tag."""
        try:
            result = subprocess.run([
                "git", "log", "--oneline", "--format=%H|%s|%an|%ae", "--no-merges",
            ], check=False, capture_output=True, text=True, cwd=self.project_root)

            commits = []
            for line in result.stdout.strip().split("\n"):
                if line:
                    parts = line.split("|", 3)
                    if len(parts) >= 4:
                        commits.append({
                            "hash": parts[0],
                            "message": parts[1],
                            "author": parts[2],
                            "email": parts[3],
                        })

            return commits

        except Exception as e:
            print(f"Error getting commits: {e}")
            return []

    def _get_git_author(self) -> str:
        """Get git author information."""
        try:
            result = subprocess.run([
                "git", "config", "user.name",
            ], check=False, capture_output=True, text=True, cwd=self.project_root)

            return result.stdout.strip() if result.returncode == 0 else "Unknown"

        except Exception:
            return "Unknown"

    def _get_current_commit(self) -> str:
        """Get current commit hash."""
        try:
            result = subprocess.run([
                "git", "rev-parse", "HEAD",
            ], check=False, capture_output=True, text=True, cwd=self.project_root)

            return result.stdout.strip() if result.returncode == 0 else "Unknown"

        except Exception:
            return "Unknown"

    def _generate_release_report(self) -> dict[str, Any]:
        """Generate comprehensive release report."""
        print("📊 Generating Release Report...")

        # Calculate statistics
        total_steps = len(self.release_steps)
        completed_steps = len([s for s in self.release_steps if s.status == "completed"])
        failed_steps = len([s for s in self.release_steps if s.status == "failed"])

        # Calculate total duration
        total_duration = sum(s.duration for s in self.release_steps)

        # Determine overall status
        overall_status = "success" if failed_steps == 0 else "failed"

        report = {
            "timestamp": datetime.now().isoformat(),
            "release_info": asdict(self.current_release) if self.current_release else None,
            "summary": {
                "total_steps": total_steps,
                "completed_steps": completed_steps,
                "failed_steps": failed_steps,
                "total_duration": round(total_duration, 2),
                "overall_status": overall_status,
            },
            "steps": [asdict(step) for step in self.release_steps],
            "config": self.config,
        }

        # Save report
        self._save_release_report(report)

        return report

    def _save_release_report(self, report: dict[str, Any]) -> None:
        """Save release report."""
        # Save JSON report
        json_file = self.reports_dir / f"release_report_{int(time.time())}.json"
        with open(json_file, "w") as f:
            json.dump(report, f, indent=2)

        # Save summary report
        summary_file = self.reports_dir / f"release_summary_{int(time.time())}.md"
        self._save_release_summary(report, summary_file)

        print("📊 Release reports saved:")
        print(f"  JSON: {json_file}")
        print(f"  Summary: {summary_file}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Release Automation")
    parser.add_argument("project_root", help="Project root directory")
    parser.add_argument("--type", choices=["major", "minor", "patch"], default="patch", help="Release type")
    parser.add_argument("--prerelease", action="store_true", help="Create prerelease")
    parser.add_argument("--version", help="Custom version number")
    parser.add_argument("--output", "-o", help="Output report file")
    parser.add_argument("--json", action="store_true", help="Output JSON format")

    args = parser.parse_args()

    automation = ReleaseAutomation(args.project_root)
    report = automation.create_release(
        release_type=args.type,
        prerelease=args.prerelease,
        custom_version=args.version,
    )

    if args.json:
        output = json.dumps(report, indent=2)
    else:
        # Pretty print format
        summary = report["summary"]
        output = f"""
🚀 RELEASE AUTOMATION REPORT
{'=' * 50}
Overall Status: {summary['overall_status'].upper()}
Total Steps: {summary['total_steps']}
Completed: {summary['completed_steps']}
Failed: {summary['failed_steps']}
Duration: {summary['total_duration']}s

Steps:
"""
        for step in report["steps"]:
            status_emoji = "✅" if step["status"] == "completed" else "❌" if step["status"] == "failed" else "⏳"
            output += f"  {status_emoji} {step['name']}: {step['status']}\n"

    if args.output:
        with open(args.output, "w") as f:
            f.write(output)
        print(f"Report saved to {args.output}")
    else:
        print(output)


if __name__ == "__main__":
    main()
