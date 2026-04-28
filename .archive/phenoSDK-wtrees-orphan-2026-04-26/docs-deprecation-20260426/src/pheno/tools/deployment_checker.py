"""
Deployment readiness checks.
"""

from __future__ import annotations

import os
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable


@dataclass
class DeploymentCheck:
    name: str
    check_fn: Callable[[], tuple[bool, str]]
    severity: str = "error"  # "error" or "warning"
    fix_hint: str | None = None


class DeploymentChecker:
    def __init__(self, project_root: Path | None = None):
        self.project_root = project_root or Path.cwd()
        self.errors = 0
        self.warnings = 0

    # Small helper checks ----------------------------------------------------
    def _file_exists(self, path: str) -> tuple[bool, str]:
        file_path = self.project_root / path
        return (True, f"{path} exists") if file_path.is_file() else (False, f"{path} not found")

    def _file_executable(self, path: str) -> tuple[bool, str]:
        file_path = self.project_root / path
        if not file_path.exists():
            return False, f"{path} not found"
        if os.access(file_path, os.X_OK):
            return True, f"{path} is executable"
        return False, f"{path} is not executable"

    def _file_contains(self, path: str, pattern: str) -> tuple[bool, str]:
        file_path = self.project_root / path
        if not file_path.exists():
            return False, f"{path} not found"
        content = (
            file_path.read_text(encoding="utf-8", errors="ignore") if file_path.is_file() else ""
        )
        return (
            (True, f"{path} contains {pattern}")
            if re.search(pattern, content, re.MULTILINE)
            else (False, f"{path} does not contain {pattern}")
        )

    def _no_uncommitted_changes(self) -> tuple[bool, str]:
        try:
            subprocess.run(
                ["git", "rev-parse", "--git-dir"],
                cwd=self.project_root,
                capture_output=True,
                check=True,
            )
            unstaged = subprocess.run(
                ["git", "diff", "--quiet"], check=False, cwd=self.project_root, capture_output=True,
            )
            staged = subprocess.run(
                ["git", "diff", "--cached", "--quiet"],
                check=False,
                cwd=self.project_root,
                capture_output=True,
            )
            return (
                (True, "No uncommitted changes")
                if unstaged.returncode == 0 and staged.returncode == 0
                else (
                    False,
                    "Uncommitted changes detected",
                )
            )
        except (FileNotFoundError, subprocess.CalledProcessError):
            return False, "Not a git repository"

    # Runner -----------------------------------------------------------------
    def run_check(self, check: DeploymentCheck) -> None:
        ok, message = check.check_fn()
        if ok:
            print(f"   ✅ {message}")
        else:
            icon = "❌" if check.severity == "error" else "⚠️"
            print(f"   {icon} {message}")
            if check.fix_hint:
                print(f"      {check.fix_hint}")
            if check.severity == "error":
                self.errors += 1
            else:
                self.warnings += 1

    def run_all(self, checks: list[DeploymentCheck]) -> tuple[int, int]:
        print("\n🔍 Deployment Readiness Check")
        print("=" * 70)
        print()
        for check in checks:
            self.run_check(check)
        print()
        print("=" * 70)
        print("📊 Summary")
        print("=" * 70)
        print()
        if self.errors == 0 and self.warnings == 0:
            print("✅ All checks passed!\n")
            return 0, 0
        if self.errors == 0:
            print(f"⚠️  {self.warnings} warning(s) found\n")
            print("You can deploy, but address warnings when possible.\n")
            return 0, self.warnings
        print(f"❌ {self.errors} error(s) and {self.warnings} warning(s) found\n")
        print("Fix errors before deploying.\n")
        return self.errors, self.warnings


def create_vercel_checks(project_root: Path | None = None) -> list[DeploymentCheck]:
    checker = DeploymentChecker(project_root)
    return [
        DeploymentCheck(
            "⚙️  Vercel: vercel.json exists", lambda: checker._file_exists("vercel.json"), "error",
        ),
        DeploymentCheck(
            "⚙️  Vercel: buildCommand configured",
            lambda: checker._file_contains("vercel.json", "buildCommand"),
            "warning",
        ),
        DeploymentCheck(
            "🔨 Build: build.sh exists", lambda: checker._file_exists("build.sh"), "error",
        ),
        DeploymentCheck(
            "🔨 Build: build.sh is executable",
            lambda: checker._file_executable("build.sh"),
            "warning",
            fix_hint="Run: chmod +x build.sh",
        ),
        DeploymentCheck(
            "📄 Requirements: requirements.txt exists",
            lambda: checker._file_exists("requirements.txt"),
            "error",
        ),
        DeploymentCheck(
            "🔐 Environment: .env.preview exists (optional)",
            lambda: checker._file_exists(".env.preview"),
            "warning",
            fix_hint="Create .env.preview for preview deployments (optional)",
        ),
        DeploymentCheck(
            "🔐 Environment: .env.production exists (optional)",
            lambda: checker._file_exists(".env.production"),
            "warning",
            fix_hint="Create .env.production for production deployments (optional)",
        ),
        DeploymentCheck(
            "📝 Git: No uncommitted changes",
            checker._no_uncommitted_changes,
            "warning",
            fix_hint="Commit changes before deploying",
        ),
    ]


__all__ = ["DeploymentCheck", "DeploymentChecker", "create_vercel_checks"]
