from __future__ import annotations

from typing import Any
from uuid import UUID

import pytest
from fastapi.testclient import TestClient


def _github_issue(
    issue_id: int,
    title: str = "Issue title",
    *,
    labels: list[str] | None = None,
    body: str = "Issue body",
) -> dict[str, Any]:
    return {
        "id": issue_id,
        "number": issue_id,
        "title": title,
        "body": body,
        "labels": labels or [],
    }


def _jira_issue(
    key: str,
    issue_id: str,
    *,
    summary: str = "Issue summary",
    description: str = "Issue description",
    issuetype: str = "Task",
) -> dict[str, Any]:
    return {
        "key": key,
        "id": issue_id,
        "fields": {
            "summary": summary,
            "description": description,
            "issuetype": {"name": issuetype},
        },
    }


def _github_service() -> Any:
    from tracertm.services.github_import_service import GitHubImportService

    return GitHubImportService()


def _jira_service() -> Any:
    from tracertm.services.jira_import_service import JiraImportService

    return JiraImportService()


def test_bulk_ingestion_result_shape() -> None:
    from tracertm.services.github_import_service import BulkIngestionResult

    result = BulkIngestionResult(
        total_processed=2,
        requirements_created=2,
        trace_links_created=2,
        errors=["warn"],
    )

    assert result.total_processed == 2
    assert result.requirements_created == 2
    assert result.trace_links_created == 2
    assert result.errors == ["warn"]


def test_import_issues_exports_github_service() -> None:
    from tracertm.services.github_import_service import GitHubImportService

    assert GitHubImportService is not None


def test_github_import_result_counts_single_labeled_issue() -> None:
    service = _github_service()
    result = service.import_issues("octo/repo", [_github_issue(1, labels=["needs-traceability"])])

    assert result.total_processed == 1
    assert result.requirements_created == 1
    assert result.trace_links_created == 1
    assert result.errors == []


def test_labeled_github_issue_uses_high_confidence() -> None:
    service = _github_service()
    service.import_issues("octo/repo", [_github_issue(1, labels=["priority:high"])])

    assert service.last_trace_links[0].confidence == pytest.approx(0.85)


def test_unlabeled_github_issue_uses_default_confidence() -> None:
    service = _github_service()
    service.import_issues("octo/repo", [_github_issue(1)])

    assert service.last_trace_links[0].confidence == pytest.approx(0.70)


def test_github_requirement_kind_is_requirement() -> None:
    from tracertm.models.trace_link import ArtifactKind

    service = _github_service()
    service.import_issues("octo/repo", [_github_issue(1)])

    assert service.last_requirements[0].kind == ArtifactKind.REQUIREMENT


def test_github_trace_link_type_is_implements() -> None:
    from tracertm.models.trace_link import TraceLinkType

    service = _github_service()
    service.import_issues("octo/repo", [_github_issue(1)])

    assert service.last_trace_links[0].link_type == TraceLinkType.IMPLEMENTS


def test_github_requirement_title_and_description_are_mapped() -> None:
    service = _github_service()
    service.import_issues("octo/repo", [_github_issue(1, title="Refactor API", body="Body text")])

    req = service.last_requirements[0]
    assert req.title == "Refactor API"
    assert req.description == "Body text"


def test_github_issues_with_errors_are_reported_but_non_blocking() -> None:
    service = _github_service()
    result = service.import_issues(
        "octo/repo",
        [_github_issue(1), {"number": 2, "body": "missing title"}],
    )

    assert result.total_processed == 2
    assert result.requirements_created == 1
    assert result.trace_links_created == 1
    assert len(result.errors) == 1
    assert "2" in result.errors[0]


def test_github_empty_input_returns_zero_counts() -> None:
    service = _github_service()
    result = service.import_issues("octo/repo", [])

    assert result.total_processed == 0
    assert result.requirements_created == 0
    assert result.trace_links_created == 0
    assert result.errors == []


def test_github_source_and_target_ids_differ() -> None:
    service = _github_service()
    service.import_issues("octo/repo", [_github_issue(1)])

    link = service.last_trace_links[0]
    assert link.source_artifact_id != link.target_artifact_id


def test_github_project_id_is_stable_for_same_repo() -> None:
    service = _github_service()
    service.import_issues("octo/repo", [_github_issue(1)])
    first = service.last_requirements[0].project_id
    service.import_issues("octo/repo", [_github_issue(2)])
    second = service.last_requirements[0].project_id

    assert first == second
    assert isinstance(first, UUID)


def test_github_distinct_repos_get_distinct_project_ids() -> None:
    service = _github_service()
    service.import_issues("octo/repo", [_github_issue(1)])
    repo_a = service.last_requirements[0].project_id
    service.import_issues("other/repo", [_github_issue(1)])
    repo_b = service.last_requirements[0].project_id

    assert repo_a != repo_b


def test_github_result_serializes_to_json_ready_fields() -> None:
    service = _github_service()
    result = service.import_issues("octo/repo", [_github_issue(1)])

    assert result.__dict__["total_processed"] == 1
    assert "errors" in result.__dict__


def test_import_issues_exports_jira_service() -> None:
    from tracertm.services.jira_import_service import JiraImportService

    assert JiraImportService is not None


def test_jira_import_result_counts_single_story() -> None:
    service = _jira_service()
    result = service.import_issues([_jira_issue("TRC-1", "1001", issuetype="Story")])

    assert result.total_processed == 1
    assert result.requirements_created == 1
    assert result.trace_links_created == 1
    assert result.errors == []


def test_story_issue_uses_high_confidence() -> None:
    service = _jira_service()
    service.import_issues([_jira_issue("TRC-1", "1001", issuetype="Story")])

    assert service.last_trace_links[0].confidence == pytest.approx(0.90)


def test_bug_issue_uses_high_confidence() -> None:
    service = _jira_service()
    service.import_issues([_jira_issue("TRC-1", "1001", issuetype="Bug")])

    assert service.last_trace_links[0].confidence == pytest.approx(0.90)


def test_default_jira_confidence_is_lower() -> None:
    service = _jira_service()
    service.import_issues([_jira_issue("TRC-1", "1001", issuetype="Task")])

    assert service.last_trace_links[0].confidence == pytest.approx(0.75)


def test_jira_requirement_fields_are_mapped() -> None:
    service = _jira_service()
    service.import_issues(
        [_jira_issue("TRC-1", "1001", summary="Fix login", description="Problem statement", issuetype="Bug")],
    )

    req = service.last_requirements[0]
    assert req.title == "Fix login"
    assert req.description == "Problem statement"
    assert req.external_id == "TRC-1"


def test_jira_trace_link_type_is_implements() -> None:
    from tracertm.models.trace_link import TraceLinkType

    service = _jira_service()
    service.import_issues([_jira_issue("TRC-1", "1001")])

    assert service.last_trace_links[0].link_type == TraceLinkType.IMPLEMENTS


def test_jira_issues_with_errors_are_reported_but_non_blocking() -> None:
    service = _jira_service()
    result = service.import_issues([_jira_issue("TRC-1", "1001"), {"key": "TRC-2"}])

    assert result.total_processed == 2
    assert result.requirements_created == 1
    assert result.trace_links_created == 1
    assert len(result.errors) == 1
    assert "TRC-2" in result.errors[0]


def test_jira_empty_input_returns_zero_counts() -> None:
    service = _jira_service()
    result = service.import_issues([])

    assert result.total_processed == 0
    assert result.requirements_created == 0
    assert result.trace_links_created == 0
    assert result.errors == []


def test_jira_source_and_target_ids_differ() -> None:
    service = _jira_service()
    service.import_issues([_jira_issue("TRC-1", "1001")])

    link = service.last_trace_links[0]
    assert link.source_artifact_id != link.target_artifact_id


def test_jira_project_id_is_stable_for_same_source() -> None:
    service = _jira_service()
    service.import_issues([_jira_issue("TRC-1", "1001")])
    first = service.last_requirements[0].project_id
    service.import_issues([_jira_issue("TRC-2", "1002")])
    second = service.last_requirements[0].project_id

    assert first == second


def test_jira_result_serializes_to_json_ready_fields() -> None:
    service = _jira_service()
    result = service.import_issues([_jira_issue("TRC-1", "1001")])

    assert result.__dict__["requirements_created"] == 1
    assert "trace_links_created" in result.__dict__


def test_github_ingest_endpoint_returns_bulk_ingestion_result() -> None:
    from tracertm.api.deps import auth_guard
    from tracertm.api.main import app

    app.dependency_overrides[auth_guard] = lambda: {"sub": "test-user"}
    try:
        client = TestClient(app)
        response = client.post(
            "/api/v1/ingest/github",
            json={"repo": "octo/repo", "issues": [_github_issue(1, labels=["needs-traceability"])]},
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    payload = response.json()
    assert payload["total_processed"] == 1
    assert payload["requirements_created"] == 1
    assert payload["trace_links_created"] == 1


def test_jira_ingest_endpoint_returns_bulk_ingestion_result() -> None:
    from tracertm.api.deps import auth_guard
    from tracertm.api.main import app

    app.dependency_overrides[auth_guard] = lambda: {"sub": "test-user"}
    try:
        client = TestClient(app)
        response = client.post(
            "/api/v1/ingest/jira",
            json={"issues": [_jira_issue("TRC-1", "1001", issuetype="Bug")]},
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    payload = response.json()
    assert payload["total_processed"] == 1
    assert payload["requirements_created"] == 1
    assert payload["trace_links_created"] == 1

