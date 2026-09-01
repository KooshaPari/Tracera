"""Jira issue bulk import into TraceRTM trace-link objects."""

from __future__ import annotations

from typing import Any
from uuid import NAMESPACE_DNS, UUID, uuid5

from tracertm.models.trace_link import (
    ArtifactKind,
    Requirement,
    TraceLink,
    TraceLinkType,
)

from tracertm.services.github_import_service import BulkIngestionResult


class JiraImportService:
    """Map Jira issues to Requirements + IMPLEMENTS links."""

    _DEFAULT_CONFIDENCE: float = 0.75
    _HIGH_CONFIDENCE: float = 0.90
    _HIGH_CONFIDENCE_TYPES = {"story", "bug"}

    def __init__(self, session: Any | None = None) -> None:
        self.session = session
        self.last_requirements: list[Requirement] = []
        self.last_trace_links: list[TraceLink] = []

    @staticmethod
    def _project_id() -> UUID:
        return uuid5(NAMESPACE_DNS, "tracertm:jira")

    @staticmethod
    def _issue_key(issue: dict[str, Any]) -> str:
        key = issue.get("key")
        if isinstance(key, str) and key.strip():
            return key.strip()
        return "unknown"

    @staticmethod
    def _issue_type(issue: dict[str, Any]) -> str:
        fields = issue.get("fields")
        if not isinstance(fields, dict):
            return "task"
        issuetype = fields.get("issuetype")
        if isinstance(issuetype, dict):
            name = issuetype.get("name")
            if isinstance(name, str):
                return name.lower()
        return "task"

    def _confidence_for(self, issue: dict[str, Any]) -> float:
        if self._issue_type(issue) in self._HIGH_CONFIDENCE_TYPES:
            return self._HIGH_CONFIDENCE
        return self._DEFAULT_CONFIDENCE

    def _map_issue(
        self,
        project_id: UUID,
        issue: dict[str, Any],
    ) -> tuple[Requirement, TraceLink]:
        fields = issue.get("fields")
        if not isinstance(fields, dict):
            raise ValueError("missing fields")

        summary = fields.get("summary")
        if not isinstance(summary, str) or not summary.strip():
            raise ValueError("missing summary")

        key = self._issue_key(issue)
        description = fields.get("description")
        description_text = description if isinstance(description, str) else None
        issue_id = str(issue.get("id") or key)

        requirement_id = uuid5(project_id, f"requirement:{key}")
        source_id = uuid5(project_id, f"jira-issue:{issue_id}")

        requirement = Requirement(
            id=requirement_id,
            project_id=project_id,
            kind=ArtifactKind.REQUIREMENT,
            title=summary.strip(),
            description=description_text,
            external_id=key,
            metadata={"issuetype": self._issue_type(issue)},
        )
        trace_link = TraceLink(
            project_id=project_id,
            source_artifact_id=source_id,
            target_artifact_id=requirement_id,
            link_type=TraceLinkType.IMPLEMENTS,
            confidence=self._confidence_for(issue),
            rationale=f"Imported from Jira issue {key}",
        )
        return requirement, trace_link

    def import_issues(self, issues: list[dict[str, Any]]) -> BulkIngestionResult:
        project_id = self._project_id()
        requirements: list[Requirement] = []
        trace_links: list[TraceLink] = []
        errors: list[str] = []

        for issue in issues:
            try:
                requirement, trace_link = self._map_issue(project_id, issue)
            except ValueError as exc:
                errors.append(f"Issue {self._issue_key(issue)}: {exc}")
                continue
            requirements.append(requirement)
            trace_links.append(trace_link)

        self.last_requirements = requirements
        self.last_trace_links = trace_links
        return BulkIngestionResult(
            total_processed=len(issues),
            requirements_created=len(requirements),
            trace_links_created=len(trace_links),
            errors=errors,
        )
