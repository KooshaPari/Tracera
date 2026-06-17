"""Pytest plugin for automated evidence emission during test execution (NFR-TRC-012).

This plugin integrates with pytest to automatically emit traceability evidence
as tests execute, creating records that link specifications to code to tests
to commits. It allows tests to be marked with spec references and automatically
collects evidence during test runs.
"""

from __future__ import annotations

from typing import Any

import pytest

from tracertm.self_tracing.evidence_emitter import EvidenceEmitter


class TraceabilityPlugin:
    """Pytest plugin for NFR-TRC-012 self-tracing evidence collection.

    This plugin hooks into pytest's test execution lifecycle to:
    1. Capture spec references from test markers (e.g., @pytest.mark.spec("NFR-TRC-012"))
    2. Record test results (pass/fail)
    3. Emit evidence records linking tests to specs and commits
    4. Generate coverage and impact analysis reports

    Usage:
        # Register in pytest.ini or conftest.py:
        # pytest_plugins = ["tracertm.self_tracing.pytest_plugin"]

        # Mark tests with spec references:
        @pytest.mark.spec("NFR-TRC-012")
        @pytest.mark.spec_type("requirement")
        def test_my_feature():
            assert True

        # Evidence is automatically emitted to a JSON file or database
    """

    def __init__(self) -> None:
        """Initialize the traceability plugin."""
        self.emitter = EvidenceEmitter()
        self.evidence_records: list[dict[str, Any]] = []
        self.coverage_records: list[dict[str, Any]] = []
        self.test_specs: dict[str, list[str]] = {}

    def pytest_configure(self, config: Any) -> None:
        """Configure the plugin at session start.

        Args:
            config: pytest config object.
        """
        config.addinivalue_line(
            "markers",
            "spec(spec_id): Mark test as verifying a requirement (e.g., 'NFR-TRC-012')",
        )
        config.addinivalue_line(
            "markers",
            "spec_type(type): Mark the specification type (requirement/design/architecture)",
        )
        config.addinivalue_line(
            "markers",
            "code_artifact(path): Mark the code file being tested (e.g., 'src/foo.py')",
        )

    def pytest_runtest_setup(self, item: Any) -> None:
        """Hook called before each test runs.

        Args:
            item: pytest Item (test function).
        """
        # Extract spec references from markers
        test_id = f"{item.fspath.basename}::{item.name}"
        spec_markers = [mark.args[0] for mark in item.iter_markers("spec")]

        if spec_markers:
            self.test_specs[test_id] = spec_markers

    def pytest_runtest_logreport(self, report: Any) -> None:
        """Hook called after each test phase (setup/call/teardown).

        Args:
            report: pytest TestReport with test outcome.
        """
        if report.when != "call":
            return

        test_id = f"{report.fspath}::{report.nodeid.split('::')[-1]}" if report.fspath else report.nodeid
        passed = report.outcome == "passed"

        # Emit evidence for tests with spec references
        if test_id in self.test_specs:
            for spec_ref in self.test_specs[test_id]:
                evidence = self.emitter.emit_test_evidence(
                    test_id=test_id,
                    spec_ref=spec_ref,
                    result=passed,
                    details={"duration": report.duration if hasattr(report, "duration") else None},
                )
                self.evidence_records.append(evidence)

                # Emit coverage record if passed
                if passed:
                    coverage = self.emitter.emit_coverage_record(
                        spec_id=spec_ref,
                        code_artifact_id=test_id,
                        relationship="verifies",
                        confidence=1.0 if passed else 0.0,
                    )
                    self.coverage_records.append(coverage)

    def pytest_sessionfinish(self, session: Any, exitstatus: int) -> None:
        """Hook called at end of test session.

        Args:
            session: pytest Session.
            exitstatus: Exit status code.
        """
        # Could save evidence records to a file or database here
        pass

    def get_evidence_records(self) -> list[dict[str, Any]]:
        """Retrieve all emitted evidence records.

        Returns:
            List of evidence record dicts.
        """
        return self.evidence_records

    def get_coverage_records(self) -> list[dict[str, Any]]:
        """Retrieve all coverage records.

        Returns:
            List of coverage record dicts.
        """
        return self.coverage_records


def pytest_plugins() -> list[str]:
    """Pytest hook to register this plugin.

    Returns:
        List of plugin modules to load.
    """
    return ["tracertm.self_tracing.pytest_plugin"]
