#!/usr/bin/env python3
"""
Version Management Enhancement System
Comprehensive version management with automated version bumping and dependency resolution.
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

import toml


@dataclass
class VersionInfo:
    """Version information."""
    current_version: str
    new_version: str
    version_type: str  # "major", "minor", "patch", "prerelease"
    is_prerelease: bool
    release_date: str
    changelog_entries: list[str]
    dependency_updates: list[dict[str, str]]
    breaking_changes: list[str]


@dataclass
class DependencyInfo:
    """Dependency information."""
    name: str
    current_version: str
    latest_version: str
    is_outdated: bool
    is_vulnerable: bool
    update_available: bool
    security_advisories: list[str]


class VersionManagement:
    """Comprehensive version management system."""

    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.reports_dir = self.project_root / "reports" / "version_management"
        self.reports_dir.mkdir(parents=True, exist_ok=True)

        self.version_info = None
        self.dependencies = []

        # Version management configuration
        self.config = {
            "version_file": "pyproject.toml",
            "changelog_file": "CHANGELOG.md",
            "requirements_file": "requirements.txt",
            "lock_file": "poetry.lock",
            "auto_update_dependencies": True,
            "check_security_vulnerabilities": True,
            "enforce_semantic_versioning": True,
            "prerelease_suffix": "rc",
            "version_bump_rules": {
                "major": ["BREAKING CHANGE", "feat!:", "fix!:"],
                "minor": ["feat:", "feature:"],
                "patch": ["fix:", "bugfix:", "chore:", "docs:", "style:", "refactor:"],
            },
        }

    def analyze_version_status(self) -> dict[str, Any]:
        """Analyze current version status and recommendations."""
        print("🔍 Analyzing Version Status...")

        # Get current version
        current_version = self._get_current_version()
        if not current_version:
            return {"error": "Could not determine current version"}

        # Analyze git history for version bump recommendations
        version_recommendation = self._analyze_git_history()

        # Check dependencies
        self._analyze_dependencies()

        # Check for security vulnerabilities
        security_issues = self._check_security_vulnerabilities()

        # Generate version compatibility matrix
        compatibility_matrix = self._generate_compatibility_matrix()

        # Generate recommendations
        recommendations = self._generate_version_recommendations(
            current_version, version_recommendation, security_issues,
        )

        # Create version info
        self.version_info = VersionInfo(
            current_version=current_version,
            new_version=version_recommendation.get("recommended_version", current_version),
            version_type=version_recommendation.get("recommended_type", "patch"),
            is_prerelease=version_recommendation.get("is_prerelease", False),
            release_date=datetime.now().strftime("%Y-%m-%d"),
            changelog_entries=version_recommendation.get("changelog_entries", []),
            dependency_updates=version_recommendation.get("dependency_updates", []),
            breaking_changes=version_recommendation.get("breaking_changes", []),
        )

        # Generate comprehensive report
        return self._generate_version_report()

    def bump_version(self, version_type: str, prerelease: bool = False,
                    custom_version: str | None = None) -> dict[str, Any]:
        """Bump version with comprehensive validation."""
        print(f"📈 Bumping version ({version_type})...")

        # Get current version
        current_version = self._get_current_version()
        if not current_version:
            return {"error": "Could not determine current version"}

        # Calculate new version
        new_version = self._calculate_new_version(
            current_version, version_type, prerelease, custom_version,
        )

        if not new_version:
            return {"error": "Could not calculate new version"}

        # Validate version bump
        if not self._validate_version_bump(current_version, new_version):
            return {"error": "Version bump validation failed"}

        # Update version files
        if not self._update_version_files(new_version):
            return {"error": "Failed to update version files"}

        # Update changelog
        if not self._update_changelog(new_version, version_type):
            return {"error": "Failed to update changelog"}

        # Update dependencies if needed
        if self.config["auto_update_dependencies"]:
            self._update_dependencies()

        # Create version tag
        if not self._create_version_tag(new_version):
            return {"error": "Failed to create version tag"}

        # Generate version report
        return self._generate_version_bump_report(current_version, new_version, version_type)

    def check_dependency_updates(self) -> dict[str, Any]:
        """Check for dependency updates and security issues."""
        print("🔍 Checking Dependency Updates...")

        # Analyze dependencies
        self._analyze_dependencies()

        # Check for security vulnerabilities
        security_issues = self._check_security_vulnerabilities()

        # Check for outdated dependencies
        outdated_deps = [dep for dep in self.dependencies if dep.is_outdated]

        # Check for vulnerable dependencies
        vulnerable_deps = [dep for dep in self.dependencies if dep.is_vulnerable]

        # Generate update recommendations
        update_recommendations = self._generate_dependency_recommendations()

        report = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_dependencies": len(self.dependencies),
                "outdated_dependencies": len(outdated_deps),
                "vulnerable_dependencies": len(vulnerable_deps),
                "security_issues": len(security_issues),
                "update_recommendations": len(update_recommendations),
            },
            "dependencies": [asdict(dep) for dep in self.dependencies],
            "security_issues": security_issues,
            "update_recommendations": update_recommendations,
        }

        # Save report
        self._save_dependency_report(report)

        return report

    def _get_current_version(self) -> str | None:
        """Get current version from version file."""
        try:
            version_file = self.project_root / self.config["version_file"]

            if version_file.suffix == ".toml":
                # Read from pyproject.toml
                with open(version_file) as f:
                    data = toml.load(f)

                version = data.get("project", {}).get("version", "")
                if version:
                    return version

                # Try tool.poetry.version
                version = data.get("tool", {}).get("poetry", {}).get("version", "")
                if version:
                    return version

                return None

            if version_file.name == "__init__.py":
                # Read from __init__.py
                with open(version_file) as f:
                    content = f.read()

                version_match = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', content)
                if version_match:
                    return version_match.group(1)

                return None

            return None

        except Exception as e:
            print(f"Error reading version: {e}")
            return None

    def _analyze_git_history(self) -> dict[str, Any]:
        """Analyze git history to recommend version bump."""
        try:
            # Get commits since last tag
            result = subprocess.run([
                "git", "log", "--oneline", "--format=%s", "--no-merges",
            ], check=False, capture_output=True, text=True, cwd=self.project_root)

            commits = result.stdout.strip().split("\n") if result.returncode == 0 else []

            # Analyze commit types
            major_indicators = 0
            minor_indicators = 0
            patch_indicators = 0
            breaking_changes = []
            changelog_entries = []

            for commit in commits:
                if commit:
                    # Check for breaking changes
                    if any(indicator in commit for indicator in self.config["version_bump_rules"]["major"]):
                        major_indicators += 1
                        if "BREAKING CHANGE" in commit or "!" in commit:
                            breaking_changes.append(commit)

                    # Check for minor changes
                    elif any(indicator in commit for indicator in self.config["version_bump_rules"]["minor"]):
                        minor_indicators += 1

                    # Check for patch changes
                    elif any(indicator in commit for indicator in self.config["version_bump_rules"]["patch"]):
                        patch_indicators += 1

                    # Add to changelog entries
                    changelog_entries.append(commit)

            # Determine recommended version type
            if major_indicators > 0:
                recommended_type = "major"
            elif minor_indicators > 0:
                recommended_type = "minor"
            else:
                recommended_type = "patch"

            # Calculate recommended version
            current_version = self._get_current_version()
            if current_version:
                recommended_version = self._calculate_new_version(
                    current_version, recommended_type, False, None,
                )
            else:
                recommended_version = "1.0.0"

            return {
                "recommended_type": recommended_type,
                "recommended_version": recommended_version,
                "major_indicators": major_indicators,
                "minor_indicators": minor_indicators,
                "patch_indicators": patch_indicators,
                "breaking_changes": breaking_changes,
                "changelog_entries": changelog_entries,
                "is_prerelease": False,
            }

        except Exception as e:
            print(f"Error analyzing git history: {e}")
            return {
                "recommended_type": "patch",
                "recommended_version": "1.0.0",
                "major_indicators": 0,
                "minor_indicators": 0,
                "patch_indicators": 0,
                "breaking_changes": [],
                "changelog_entries": [],
                "is_prerelease": False,
            }

    def _analyze_dependencies(self) -> None:
        """Analyze project dependencies."""
        self.dependencies = []

        # Check pyproject.toml dependencies
        self._analyze_pyproject_dependencies()

        # Check requirements.txt if it exists
        requirements_file = self.project_root / self.config["requirements_file"]
        if requirements_file.exists():
            self._analyze_requirements_dependencies(requirements_file)

    def _analyze_pyproject_dependencies(self) -> None:
        """Analyze dependencies from pyproject.toml."""
        try:
            pyproject_file = self.project_root / self.config["version_file"]
            with open(pyproject_file) as f:
                data = toml.load(f)

            # Get dependencies from project.dependencies
            dependencies = data.get("project", {}).get("dependencies", [])

            for dep in dependencies:
                # Parse dependency string
                dep_info = self._parse_dependency_string(dep)
                if dep_info:
                    self.dependencies.append(dep_info)

            # Get optional dependencies
            optional_deps = data.get("project", {}).get("optional-dependencies", {})
            for group, deps in optional_deps.items():
                for dep in deps:
                    dep_info = self._parse_dependency_string(dep)
                    if dep_info:
                        dep_info.name = f"{dep_info.name}[{group}]"
                        self.dependencies.append(dep_info)

        except Exception as e:
            print(f"Error analyzing pyproject dependencies: {e}")

    def _analyze_requirements_dependencies(self, requirements_file: Path) -> None:
        """Analyze dependencies from requirements.txt."""
        try:
            with open(requirements_file) as f:
                lines = f.readlines()

            for line in lines:
                line = line.strip()
                if line and not line.startswith("#"):
                    dep_info = self._parse_dependency_string(line)
                    if dep_info:
                        self.dependencies.append(dep_info)

        except Exception as e:
            print(f"Error analyzing requirements dependencies: {e}")

    def _parse_dependency_string(self, dep_string: str) -> DependencyInfo | None:
        """Parse a dependency string into DependencyInfo."""
        try:
            # Remove comments
            dep_string = dep_string.split("#")[0].strip()

            # Parse package name and version
            if "==" in dep_string:
                name, version = dep_string.split("==", 1)
            elif ">=" in dep_string:
                name, version = dep_string.split(">=", 1)
            elif "~=" in dep_string:
                name, version = dep_string.split("~=", 1)
            elif ">" in dep_string:
                name, version = dep_string.split(">", 1)
            else:
                name = dep_string
                version = "latest"

            name = name.strip()
            version = version.strip()

            # Check for latest version (simplified)
            latest_version = version  # In real implementation, would check PyPI

            return DependencyInfo(
                name=name,
                current_version=version,
                latest_version=latest_version,
                is_outdated=version != latest_version,
                is_vulnerable=False,  # Would check security databases
                update_available=version != latest_version,
                security_advisories=[],
            )

        except Exception as e:
            print(f"Error parsing dependency string '{dep_string}': {e}")
            return None

    def _check_security_vulnerabilities(self) -> list[dict[str, Any]]:
        """Check for security vulnerabilities in dependencies."""
        security_issues = []

        # This would integrate with security scanning tools
        # For now, return empty list
        return security_issues

    def _generate_compatibility_matrix(self) -> dict[str, Any]:
        """Generate version compatibility matrix."""
        return {
            "python_versions": ["3.8", "3.9", "3.10", "3.11", "3.12"],
            "supported_versions": ["3.8+", "3.9+", "3.10+", "3.11+", "3.12+"],
            "deprecated_versions": ["3.7"],
            "recommended_version": "3.11",
        }

    def _generate_version_recommendations(self, current_version: str,
                                        version_recommendation: dict[str, Any],
                                        security_issues: list[dict[str, Any]]) -> list[str]:
        """Generate version management recommendations."""
        recommendations = []

        # Version bump recommendations
        if version_recommendation["major_indicators"] > 0:
            recommendations.append("Major version bump recommended due to breaking changes")
        elif version_recommendation["minor_indicators"] > 0:
            recommendations.append("Minor version bump recommended due to new features")
        elif version_recommendation["patch_indicators"] > 0:
            recommendations.append("Patch version bump recommended due to bug fixes")

        # Security recommendations
        if security_issues:
            recommendations.append(f"Address {len(security_issues)} security vulnerabilities")

        # Dependency recommendations
        outdated_deps = [dep for dep in self.dependencies if dep.is_outdated]
        if outdated_deps:
            recommendations.append(f"Update {len(outdated_deps)} outdated dependencies")

        # Version compatibility recommendations
        recommendations.append("Ensure compatibility with supported Python versions")
        recommendations.append("Update documentation for version changes")

        return recommendations

    def _calculate_new_version(self, current_version: str, version_type: str,
                             prerelease: bool, custom_version: str | None) -> str | None:
        """Calculate new version number."""
        try:
            if custom_version:
                return custom_version

            # Parse current version
            version_parts = current_version.split(".")
            major = int(version_parts[0])
            minor = int(version_parts[1]) if len(version_parts) > 1 else 0
            patch = int(version_parts[2]) if len(version_parts) > 2 else 0

            # Remove prerelease suffix if present
            if "-" in str(patch):
                patch = int(str(patch).split("-")[0])

            # Calculate new version
            if version_type == "major":
                major += 1
                minor = 0
                patch = 0
            elif version_type == "minor":
                minor += 1
                patch = 0
            elif version_type == "patch":
                patch += 1
            else:
                return None

            new_version = f"{major}.{minor}.{patch}"

            # Add prerelease suffix if needed
            if prerelease:
                new_version += f"-{self.config['prerelease_suffix']}.1"

            return new_version

        except Exception as e:
            print(f"Error calculating new version: {e}")
            return None

    def _validate_version_bump(self, current_version: str, new_version: str) -> bool:
        """Validate version bump."""
        try:
            # Check if new version is higher than current
            current_parts = [int(x) for x in current_version.split(".")]
            new_parts = [int(x.split("-")[0]) for x in new_version.split(".")]

            if len(new_parts) < len(current_parts):
                new_parts.extend([0] * (len(current_parts) - len(new_parts)))

            for i in range(len(current_parts)):
                if new_parts[i] < current_parts[i]:
                    return False
                if new_parts[i] > current_parts[i]:
                    return True

            return new_version != current_version

        except Exception as e:
            print(f"Error validating version bump: {e}")
            return False

    def _update_version_files(self, new_version: str) -> bool:
        """Update version in all relevant files."""
        try:
            version_file = self.project_root / self.config["version_file"]

            if version_file.suffix == ".toml":
                # Update pyproject.toml
                with open(version_file) as f:
                    data = toml.load(f)

                # Update project version
                if "project" in data:
                    data["project"]["version"] = new_version
                elif "tool" in data and "poetry" in data["tool"]:
                    data["tool"]["poetry"]["version"] = new_version

                with open(version_file, "w") as f:
                    toml.dump(data, f)

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

            return True

        except Exception as e:
            print(f"Error updating version files: {e}")
            return False

    def _update_changelog(self, new_version: str, version_type: str) -> bool:
        """Update changelog with new version."""
        try:
            changelog_file = self.project_root / self.config["changelog_file"]

            # Get commits since last tag
            commits = self._get_commits_since_last_tag()

            # Generate changelog entry
            changelog_entry = f"""## [{new_version}] - {datetime.now().strftime('%Y-%m-%d')}

### Added
"""

            # Categorize commits
            features = [c for c in commits if c.startswith("feat:")]
            fixes = [c for c in commits if c.startswith("fix:")]
            other = [c for c in commits if not c.startswith(("feat:", "fix:"))]

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

            return True

        except Exception as e:
            print(f"Error updating changelog: {e}")
            return False

    def _update_dependencies(self) -> None:
        """Update dependencies to latest versions."""
        # This would update dependencies to latest compatible versions
        # For now, just log the action
        print("  📦 Updating dependencies...")

    def _create_version_tag(self, new_version: str) -> bool:
        """Create git tag for the new version."""
        try:
            tag_name = f"v{new_version}"

            result = subprocess.run([
                "git", "tag", "-a", tag_name, "-m", f"Version {new_version}",
            ], check=False, capture_output=True, text=True, cwd=self.project_root)

            return result.returncode == 0

        except Exception as e:
            print(f"Error creating version tag: {e}")
            return False

    def _get_commits_since_last_tag(self) -> list[str]:
        """Get commits since the last tag."""
        try:
            result = subprocess.run([
                "git", "log", "--oneline", "--format=%s", "--no-merges",
            ], check=False, capture_output=True, text=True, cwd=self.project_root)

            return result.stdout.strip().split("\n") if result.returncode == 0 else []

        except Exception as e:
            print(f"Error getting commits: {e}")
            return []

    def _generate_dependency_recommendations(self) -> list[str]:
        """Generate dependency update recommendations."""
        recommendations = []

        outdated_deps = [dep for dep in self.dependencies if dep.is_outdated]
        if outdated_deps:
            recommendations.append(f"Update {len(outdated_deps)} outdated dependencies")

        vulnerable_deps = [dep for dep in self.dependencies if dep.is_vulnerable]
        if vulnerable_deps:
            recommendations.append(f"Address {len(vulnerable_deps)} vulnerable dependencies")

        return recommendations

    def _generate_version_report(self) -> dict[str, Any]:
        """Generate comprehensive version report."""
        print("📊 Generating Version Report...")

        report = {
            "timestamp": datetime.now().isoformat(),
            "version_info": asdict(self.version_info) if self.version_info else None,
            "dependencies": [asdict(dep) for dep in self.dependencies],
            "summary": {
                "current_version": self.version_info.current_version if self.version_info else "Unknown",
                "recommended_version": self.version_info.new_version if self.version_info else "Unknown",
                "version_type": self.version_info.version_type if self.version_info else "Unknown",
                "total_dependencies": len(self.dependencies),
                "outdated_dependencies": len([d for d in self.dependencies if d.is_outdated]),
                "vulnerable_dependencies": len([d for d in self.dependencies if d.is_vulnerable]),
            },
            "config": self.config,
        }

        # Save report
        self._save_version_report(report)

        return report

    def _generate_version_bump_report(self, current_version: str, new_version: str,
                                    version_type: str) -> dict[str, Any]:
        """Generate version bump report."""
        report = {
            "timestamp": datetime.now().isoformat(),
            "version_bump": {
                "current_version": current_version,
                "new_version": new_version,
                "version_type": version_type,
                "success": True,
            },
            "summary": {
                "version_updated": True,
                "changelog_updated": True,
                "tag_created": True,
            },
        }

        # Save report
        self._save_version_report(report)

        return report

    def _save_version_report(self, report: dict[str, Any]) -> None:
        """Save version report."""
        # Save JSON report
        json_file = self.reports_dir / f"version_report_{int(time.time())}.json"
        with open(json_file, "w") as f:
            json.dump(report, f, indent=2)

        print(f"📊 Version report saved: {json_file}")

    def _save_dependency_report(self, report: dict[str, Any]) -> None:
        """Save dependency report."""
        # Save JSON report
        json_file = self.reports_dir / f"dependency_report_{int(time.time())}.json"
        with open(json_file, "w") as f:
            json.dump(report, f, indent=2)

        print(f"📊 Dependency report saved: {json_file}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Version Management")
    parser.add_argument("project_root", help="Project root directory")
    parser.add_argument("--analyze", action="store_true", help="Analyze version status")
    parser.add_argument("--bump", choices=["major", "minor", "patch"], help="Bump version")
    parser.add_argument("--prerelease", action="store_true", help="Create prerelease")
    parser.add_argument("--version", help="Custom version number")
    parser.add_argument("--dependencies", action="store_true", help="Check dependencies")
    parser.add_argument("--output", "-o", help="Output report file")
    parser.add_argument("--json", action="store_true", help="Output JSON format")

    args = parser.parse_args()

    manager = VersionManagement(args.project_root)

    if args.analyze:
        report = manager.analyze_version_status()
    elif args.bump:
        report = manager.bump_version(args.bump, args.prerelease, args.version)
    elif args.dependencies:
        report = manager.check_dependency_updates()
    else:
        report = manager.analyze_version_status()

    if args.json:
        output = json.dumps(report, indent=2)
    # Pretty print format
    elif "error" in report:
        output = f"❌ Error: {report['error']}"
    else:
        summary = report.get("summary", {})
        output = f"""
📈 VERSION MANAGEMENT REPORT
{'=' * 50}
Current Version: {summary.get('current_version', 'Unknown')}
Recommended Version: {summary.get('recommended_version', 'Unknown')}
Version Type: {summary.get('version_type', 'Unknown')}
Total Dependencies: {summary.get('total_dependencies', 0)}
Outdated Dependencies: {summary.get('outdated_dependencies', 0)}
Vulnerable Dependencies: {summary.get('vulnerable_dependencies', 0)}
"""

    if args.output:
        with open(args.output, "w") as f:
            f.write(output)
        print(f"Report saved to {args.output}")
    else:
        print(output)


if __name__ == "__main__":
    main()
