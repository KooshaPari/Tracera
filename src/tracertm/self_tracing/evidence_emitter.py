"""Evidence emission for NFR-TRC-012: spec→code→test→commit traceability chain.

This module implements the EvidenceEmitter class which emits traceability evidence
records linking specifications, code artifacts, tests, and commits together,
enabling Tracera to trace itself through its own traceability system.
"""

from __future__ import annotations

import subprocess
import uuid
from datetime import UTC, datetime
from typing import Any


class EvidenceEmitter:
    """Emits traceability evidence linking spec→code→test→commit (NFR-TRC-012).

    The EvidenceEmitter creates structured evidence records that demonstrate
    how specifications are implemented in code, verified by tests, and committed
    to version control. This enables end-to-end traceability of the system's own
    requirements through its own specification system.
    """

    def __init__(self) -> None:
        """Initialize the evidence emitter."""
        self._current_commit = self._get_current_commit()

    def emit_test_evidence(
        self, test_id: str, spec_ref: str, result: bool, details: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Emit evidence record for a test execution.

        Args:
            test_id: Unique identifier for the test (file::function or UUID).
            spec_ref: Reference to the specification requirement (e.g., NFR-TRC-012, FR-TRC-001).
            result: Test result (True for PASS, False for FAIL).
            details: Optional additional test metadata (duration, assertion count, etc.).

        Returns:
            Evidence record dict with keys:
                - evidence_id: UUID for this evidence record
                - test_id: test identifier
                - spec_ref: requirement reference
                - result: "PASS" or "FAIL"
                - timestamp: ISO-8601 UTC timestamp
                - commit: current git commit SHA (short)
                - details: additional metadata
        """
        return {
            "evidence_id": str(uuid.uuid4()),
            "test_id": test_id,
            "spec_ref": spec_ref,
            "result": "PASS" if result else "FAIL",
            "timestamp": datetime.now(UTC).isoformat(),
            "commit": self._current_commit,
            "details": details or {},
        }

    def chain_evidence(
        self,
        spec_ref: str,
        code_path: str,
        test_id: str,
        commit: str | None = None,
    ) -> dict[str, Any]:
        """Build full spec→code→test→commit evidence chain.

        This method constructs a complete traceability chain showing how a specification
        requirement flows through code implementation, test verification, and version control.

        Args:
            spec_ref: Specification requirement identifier (e.g., NFR-TRC-012).
            code_path: File path to the code artifact implementing the spec.
            test_id: Test identifier verifying the implementation.
            commit: Optional git commit SHA. If None, uses current commit.

        Returns:
            Chained evidence dict with structure:
                - spec_ref: requirement identifier
                - code_path: file path of implementation
                - test_id: test verifying the code
                - commit: git commit containing the test
                - chain_id: UUID linking all elements together
                - chain_type: "spec→code→test→commit"
                - timestamp: ISO-8601 UTC timestamp
                - links: list of individual link evidence records
        """
        commit_sha = commit or self._current_commit
        chain_id = str(uuid.uuid4())

        links = [
            {
                "source": "spec",
                "source_id": spec_ref,
                "target": "code",
                "target_id": code_path,
                "relationship": "satisfies",
                "evidence_id": str(uuid.uuid4()),
            },
            {
                "source": "code",
                "source_id": code_path,
                "target": "test",
                "target_id": test_id,
                "relationship": "verifies",
                "evidence_id": str(uuid.uuid4()),
            },
            {
                "source": "test",
                "source_id": test_id,
                "target": "commit",
                "target_id": commit_sha,
                "relationship": "contains",
                "evidence_id": str(uuid.uuid4()),
            },
        ]

        return {
            "spec_ref": spec_ref,
            "code_path": code_path,
            "test_id": test_id,
            "commit": commit_sha,
            "chain_id": chain_id,
            "chain_type": "spec→code→test→commit",
            "timestamp": datetime.now(UTC).isoformat(),
            "links": links,
        }

    def _get_current_commit(self) -> str:
        """Get the current git commit SHA (short form).

        Returns:
            Short commit SHA (7 chars) or "unknown" if git fails.
        """
        try:
            result = subprocess.check_output(
                ["git", "rev-parse", "--short", "HEAD"],
                stderr=subprocess.DEVNULL,
                text=True,
            )
            return result.strip()
        except (subprocess.CalledProcessError, FileNotFoundError, OSError):
            return "unknown"

    def emit_coverage_record(
        self,
        spec_id: str,
        code_artifact_id: str,
        relationship: str,
        confidence: float = 0.95,
    ) -> dict[str, Any]:
        """Emit a coverage record for a spec-to-code relationship.

        Args:
            spec_id: Specification artifact identifier.
            code_artifact_id: Code artifact identifier.
            relationship: Type of relationship (e.g., "satisfies", "implements").
            confidence: Confidence score [0.0, 1.0] for the link.

        Returns:
            Coverage record dict with keys:
                - coverage_id: UUID for this coverage record
                - spec_id: specification identifier
                - code_artifact_id: code artifact identifier
                - relationship: relationship type
                - confidence: confidence score
                - timestamp: ISO-8601 UTC timestamp
                - status: "covered" or "partial" based on confidence
        """
        status = "covered" if confidence >= 0.9 else "partial"
        return {
            "coverage_id": str(uuid.uuid4()),
            "spec_id": spec_id,
            "code_artifact_id": code_artifact_id,
            "relationship": relationship,
            "confidence": confidence,
            "timestamp": datetime.now(UTC).isoformat(),
            "status": status,
        }

    def impact_analysis_record(
        self,
        changed_artifact_id: str,
        affected_artifacts: list[dict[str, Any]],
        total_score: float,
    ) -> dict[str, Any]:
        """Emit an impact analysis record for blast radius calculation.

        Args:
            changed_artifact_id: ID of the artifact that changed.
            affected_artifacts: List of affected artifact dicts with keys:
                - artifact_id: identifier
                - depth: distance from changed artifact
                - score: impact score
                - via: list of intermediate artifact IDs
            total_score: Sum of all impact scores.

        Returns:
            Impact analysis record dict with keys:
                - analysis_id: UUID for this analysis
                - changed_artifact_id: artifact that changed
                - affected_count: number of affected artifacts
                - total_score: total impact score
                - timestamp: ISO-8601 UTC timestamp
                - affected: list of affected artifact records
        """
        return {
            "analysis_id": str(uuid.uuid4()),
            "changed_artifact_id": changed_artifact_id,
            "affected_count": len(affected_artifacts),
            "total_score": total_score,
            "timestamp": datetime.now(UTC).isoformat(),
            "affected": affected_artifacts,
        }
