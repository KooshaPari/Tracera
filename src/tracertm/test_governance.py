"""Tests for spec-first governance tooling."""

# ruff: noqa: D103, S101

from __future__ import annotations

from fastapi.testclient import TestClient

from tracertm.api.main import create_app
from tracertm.governance import (
    GovernanceSpec,
    GovernanceTrace,
    evaluate_spec_first_governance,
)

HTTP_OK = 200


def test_spec_first_governance_passes_for_approved_traced_spec() -> None:
    report = evaluate_spec_first_governance(
        specs=[
            GovernanceSpec(
                spec_id="SPEC-1",
                title="Governance gate",
                owner="platform",
                acceptance_criteria=["Reject implementation without a spec"],
                evidence_links=["docs/specs/governance.md"],
                status="approved",
            )
        ],
        traces=[
            GovernanceTrace(spec_id="SPEC-1", target_id="src/tool.py", kind="implementation"),
            GovernanceTrace(spec_id="SPEC-1", target_id="tests/test_tool.py", kind="test"),
        ],
    )

    assert report.status == "pass"
    assert report.violations == []


def test_spec_first_governance_reports_missing_requirements_and_orphans() -> None:
    report = evaluate_spec_first_governance(
        specs=[
            GovernanceSpec(
                spec_id="SPEC-1",
                title="Unapproved work",
                owner="platform",
            )
        ],
        traces=[GovernanceTrace(spec_id="SPEC-2", target_id="src/tool.py", kind="implementation")],
    )

    assert report.status == "fail"
    assert {violation.code for violation in report.violations} == {
        "not_approved",
        "missing_acceptance",
        "missing_evidence",
        "missing_implementation",
        "missing_test",
        "orphan_trace",
    }


def test_governance_spec_check_api() -> None:
    client = TestClient(create_app())

    response = client.post(
        "/api/v1/governance/spec-check",
        json={
            "specs": [
                {
                    "spec_id": "SPEC-1",
                    "title": "Governance gate",
                    "owner": "platform",
                    "acceptance_criteria": ["Gate planned work"],
                    "evidence_links": ["docs/specs/governance.md"],
                    "status": "approved",
                }
            ],
            "traces": [
                {"spec_id": "SPEC-1", "target_id": "src/tool.py", "kind": "implementation"},
                {"spec_id": "SPEC-1", "target_id": "tests/test_tool.py", "kind": "test"},
            ],
        },
    )

    assert response.status_code == HTTP_OK
    assert response.json()["status"] == "pass"
