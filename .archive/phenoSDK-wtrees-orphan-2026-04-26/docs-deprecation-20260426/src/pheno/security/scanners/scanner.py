"""High-level secret scanner with Morph-compatible API.

Provides unified interface for secret scanning across files and repositories.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from pheno.logging.core.logger import get_logger
from pheno.security.scanners.models import ScanSummary, SecretFinding, SuppressionRules
from pheno.security.scanners.pipeline import scan_paths

if TYPE_CHECKING:
    from pathlib import Path

logger = get_logger("pheno.security.scanner")


@dataclass
class ScanResult:
    """
    Complete scan result (Morph-compatible).
    """

    total_files_scanned: int
    secrets_found: int
    high_severity_count: int
    medium_severity_count: int
    low_severity_count: int
    findings_by_type: dict[str, int]
    findings_by_file: dict[str, list[SecretFinding]]
    all_findings: list[SecretFinding]
    scan_duration_ms: int


class SecretScanner:
    """Unified secret scanner for files and repositories.

    Provides Morph-compatible API for secret scanning.
    """

    def __init__(
        self,
        *,
        entropy_threshold: float = 4.5,
        suppression_rules: SuppressionRules | None = None,
    ):
        """Initialize scanner.

        Args:
            entropy_threshold: Minimum entropy for heuristic detection
            suppression_rules: Optional suppression configuration
        """
        self.entropy_threshold = entropy_threshold
        self.suppression_rules = suppression_rules

    async def scan_directory(
        self,
        directory: Path,
        *,
        include_patterns: list[str] | None = None,
        exclude_patterns: list[str] | None = None,
    ) -> ScanResult:
        """Scan a directory for secrets.

        Args:
            directory: Directory to scan
            include_patterns: File patterns to include
            exclude_patterns: File patterns to exclude

        Returns:
            ScanResult with complete findings
        """
        if not directory.is_dir():
            raise ValueError(f"Not a directory: {directory}")

        summary = await scan_paths(
            [directory],
            include_patterns=include_patterns,
            exclude_patterns=exclude_patterns,
            suppression_rules=self.suppression_rules,
            entropy_threshold=self.entropy_threshold,
        )

        return self._create_result(summary)

    async def scan_file(self, file_path: Path) -> ScanResult:
        """Scan a single file for secrets.

        Args:
            file_path: File to scan

        Returns:
            ScanResult with findings
        """
        if not file_path.is_file():
            raise ValueError(f"Not a file: {file_path}")

        summary = await scan_paths(
            [file_path],
            suppression_rules=self.suppression_rules,
            entropy_threshold=self.entropy_threshold,
        )

        return self._create_result(summary)

    async def scan_files(
        self,
        file_paths: list[Path],
        *,
        include_patterns: list[str] | None = None,
        exclude_patterns: list[str] | None = None,
    ) -> ScanResult:
        """Scan multiple files for secrets.

        Args:
            file_paths: Files to scan
            include_patterns: File patterns to include
            exclude_patterns: File patterns to exclude

        Returns:
            ScanResult with findings
        """
        summary = await scan_paths(
            file_paths,
            include_patterns=include_patterns,
            exclude_patterns=exclude_patterns,
            suppression_rules=self.suppression_rules,
            entropy_threshold=self.entropy_threshold,
        )

        return self._create_result(summary)

    def _create_result(self, summary: ScanSummary) -> ScanResult:
        """
        Convert ScanSummary to ScanResult.
        """
        findings = list(summary.findings)

        # Count by severity
        high_count = sum(1 for f in findings if f.severity == "high")
        medium_count = sum(1 for f in findings if f.severity == "medium")
        low_count = sum(1 for f in findings if f.severity == "low")

        # Count by detector type
        findings_by_type: dict[str, int] = {}
        for finding in findings:
            findings_by_type[finding.detector] = findings_by_type.get(finding.detector, 0) + 1

        # Group by file
        findings_by_file: dict[str, list[SecretFinding]] = {}
        files_scanned: set[Path] = set()

        for finding in findings:
            file_str = str(finding.file_path)
            files_scanned.add(finding.file_path)

            if file_str not in findings_by_file:
                findings_by_file[file_str] = []
            findings_by_file[file_str].append(finding)

        return ScanResult(
            total_files_scanned=len(files_scanned),
            secrets_found=len(findings),
            high_severity_count=high_count,
            medium_severity_count=medium_count,
            low_severity_count=low_count,
            findings_by_type=findings_by_type,
            findings_by_file=findings_by_file,
            all_findings=findings,
            scan_duration_ms=summary.duration_ms,
        )

    def create_baseline(self, findings: list[SecretFinding]) -> SuppressionRules:
        """Create suppression rules from current findings (baseline).

        Args:
            findings: Findings to baseline

        Returns:
            SuppressionRules that will suppress these findings
        """
        fingerprints = tuple(f.fingerprint for f in findings)
        return SuppressionRules(allowed_fingerprints=fingerprints)


class GitSecretScanner:
    """Scanner for Git repositories (including history).

    Note: This is a simplified implementation. For full Git history scanning,
    consider using trufflehog directly via CLI.
    """

    def __init__(
        self,
        *,
        entropy_threshold: float = 4.5,
        suppression_rules: SuppressionRules | None = None,
    ):
        """Initialize Git scanner.

        Args:
            entropy_threshold: Minimum entropy for heuristic detection
            suppression_rules: Optional suppression configuration
        """
        self.scanner = SecretScanner(
            entropy_threshold=entropy_threshold,
            suppression_rules=suppression_rules,
        )

    async def scan_repository(
        self,
        repo_path: Path,
        *,
        include_patterns: list[str] | None = None,
        exclude_patterns: list[str] | None = None,
    ) -> ScanResult:
        """Scan a Git repository (working directory).

        Args:
            repo_path: Path to Git repository
            include_patterns: File patterns to include
            exclude_patterns: File patterns to exclude

        Returns:
            ScanResult with findings
        """
        # Add .git to exclude patterns
        exclude_patterns = list(exclude_patterns or [])
        if ".git/*" not in exclude_patterns:
            exclude_patterns.append(".git/*")

        return await self.scanner.scan_directory(
            repo_path,
            include_patterns=include_patterns,
            exclude_patterns=exclude_patterns,
        )

    async def scan_commits(
        self,
        repo_path: Path,
        commits: list[str] | None = None,
    ) -> ScanResult:
        """Scan specific Git commits.

        Note: This is a placeholder. For full implementation, use trufflehog CLI.

        Args:
            repo_path: Path to Git repository
            commits: Commit SHAs to scan (None = all commits)

        Returns:
            ScanResult with findings
        """
        logger.warning(
            "git_commit_scan_not_implemented",
            message="Git commit scanning not fully implemented. Use trufflehog CLI for full history scanning.",
        )

        # For now, just scan the working directory
        return await self.scan_repository(repo_path)

    async def scan_branches(
        self,
        repo_path: Path,
        branches: list[str] | None = None,
    ) -> ScanResult:
        """Scan specific Git branches.

        Note: This is a placeholder. For full implementation, use trufflehog CLI.

        Args:
            repo_path: Path to Git repository
            branches: Branch names to scan (None = current branch)

        Returns:
            ScanResult with findings
        """
        logger.warning(
            "git_branch_scan_not_implemented",
            message="Git branch scanning not fully implemented. Use trufflehog CLI for full history scanning.",
        )

        # For now, just scan the working directory
        return await self.scan_repository(repo_path)
