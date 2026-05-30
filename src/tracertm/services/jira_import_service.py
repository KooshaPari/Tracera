"""Bulk ingestion helpers for Jira issues."""

from __future__ import annotations

import json
import logging
import uuid
from typing import TYPE_CHECKING, Any

from tracertm.models.trace_link import ArtifactKind, Requirement, TraceLink, TraceLinkType
from tracertm.services.github_import_service import BulkIngestionResult

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


class JiraImportService:
    """Import Jira issues into canonical TraceRTM trace-link objects."""

    STATUS_MAP: dict[str, str] = {
        "To Do": "todo",
        "In Progress": "in_progress",
        "In Review": "in_progress",
        "Done": "complete",
        "Closed": "complete",
    }
    TYPE_MAP: dict[str, str] = {
        "Epic": "epic",
        "Story": "story",
        "Task": "task",
        "Bug": "bug",
        "Sub-task": "subtask",
    }
    LINK_TYPE_MAP: dict[str, str] = {
        "relates to": "relates_to",
        "blocks": "blocks",
        "is blocked by": "blocked_by",
        "duplicates": "duplicates",
        "is duplicated by": "duplicated_by",
        "implements": "implements",
        "is implemented by": "implemented_by",
    }

    _DEFAULT_CONFIDENCE: float = 0.75
    _HIGH_CONFIDENCE: float = 0.90

    def __init__(self, session: AsyncSession | None = None, http_client: Any | None = None) -> None:
        self.session = session
        self.http_client = http_client
        self.last_requirements: list[Requirement] = []
        self.last_trace_links: list[TraceLink] = []

        self.projects = None
        self.items = None
        self.links = None
        self.events = None
        if session is not None:
            from tracertm.repositories.event_repository import EventRepository
            from tracertm.repositories.item_repository import ItemRepository
            from tracertm.repositories.link_repository import LinkRepository
            from tracertm.repositories.project_repository import ProjectRepository

            self.projects = ProjectRepository(session)
            self.items = ItemRepository(session)
            self.links = LinkRepository(session)
            self.events = EventRepository(session)

    @staticmethod
    def _project_id() -> uuid.UUID:
        return uuid.uuid5(uuid.NAMESPACE_URL, "tracertm:jira:project")

    @staticmethod
    def _external_id(issue: dict[str, Any]) -> str:
        key = issue.get("key")
        if not isinstance(key, str) or not key.strip():
            raise ValueError("Jira issue is missing required 'key'")
        return key.strip()

    @staticmethod
    def _issue_label(issue: dict[str, Any], index: int) -> str:
        key = issue.get("key")
        if isinstance(key, str) and key.strip():
            return key.strip()
        return f"#{index + 1}"

    @staticmethod
    def _issuetype_name(issue: dict[str, Any]) -> str:
        fields = issue.get("fields")
        if not isinstance(fields, dict):
            raise ValueError("Jira issue is missing required 'fields'")
        issuetype = fields.get("issuetype")
        if not isinstance(issuetype, dict):
            return "Task"
        name = issuetype.get("name")
        return name if isinstance(name, str) and name.strip() else "Task"

    def _requirement_id(self, external_id: str) -> uuid.UUID:
        return uuid.uuid5(uuid.NAMESPACE_URL, f"tracertm:jira:req:{external_id}")

    def _source_artifact_id(self, external_id: str) -> uuid.UUID:
        return uuid.uuid5(uuid.NAMESPACE_URL, f"tracertm:jira:src:{external_id}")

    def _build_requirement(self, issue: dict[str, Any]) -> Requirement:
        fields = issue.get("fields")
        if not isinstance(fields, dict):
            raise ValueError("Jira issue is missing required 'fields'")

        summary = fields.get("summary")
        if not isinstance(summary, str) or not summary.strip():
            raise ValueError("Jira issue is missing required 'summary'")

        external_id = self._external_id(issue)
        issuetype = self._issuetype_name(issue)

        description = fields.get("description")
        if not isinstance(description, str):
            description = None

        return Requirement(
            id=self._requirement_id(external_id),
            project_id=self._project_id(),
            kind=ArtifactKind.REQUIREMENT,
            title=summary.strip(),
            description=description,
            external_id=external_id,
            metadata={
                "source": "jira",
                "jira_key": external_id,
                "jira_id": issue.get("id"),
                "issuetype": issuetype,
            },
        )

    def _build_trace_link(self, requirement: Requirement, issue: dict[str, Any]) -> TraceLink:
        external_id = requirement.external_id or self._external_id(issue)
        issuetype = self._issuetype_name(issue).casefold()
        confidence = self._HIGH_CONFIDENCE if issuetype in {"bug", "story"} else self._DEFAULT_CONFIDENCE
        return TraceLink(
            id=uuid.uuid5(uuid.NAMESPACE_URL, f"tracertm:jira:link:{external_id}"),
            project_id=requirement.project_id,
            source_artifact_id=self._source_artifact_id(external_id),
            target_artifact_id=requirement.id,
            link_type=TraceLinkType.IMPLEMENTS,
            confidence=confidence,
            rationale="Imported from Jira issue",
            metadata={
                "source": "jira",
                "jira_key": external_id,
                "issuetype": self._issuetype_name(issue),
            },
        )

    def import_issues(self, issues: list[dict[str, Any]]) -> BulkIngestionResult:
        """Map Jira issues to Requirements + IMPLEMENTS links."""

        self.last_requirements = []
        self.last_trace_links = []

        errors: list[str] = []
        for index, issue in enumerate(issues):
            try:
                requirement = self._build_requirement(issue)
                trace_link = self._build_trace_link(requirement, issue)
            except Exception as exc:  # pragma: no cover - exercised via tests
                errors.append(f"Jira issue {self._issue_label(issue, index)}: {exc}")
                continue

            self.last_requirements.append(requirement)
            self.last_trace_links.append(trace_link)

        return BulkIngestionResult(
            total_processed=len(issues),
            requirements_created=len(self.last_requirements),
            trace_links_created=len(self.last_trace_links),
            errors=errors,
        )

    async def validate_jira_export(self, json_data: str) -> list[str]:
        """Validate a Jira export payload."""

        try:
            data = json.loads(json_data)
        except json.JSONDecodeError as exc:
            return [f"Invalid JSON: {exc!s}"]

        issues = data.get("issues")
        if "issues" not in data:
            return ["Missing 'issues' field"]
        if not isinstance(issues, list):
            return ["'issues' must be a list"]
        return []

    async def import_jira_project(
        self,
        project_name: str,
        json_data: str,
        agent_id: str = "system",
    ) -> dict[str, Any]:
        """Legacy wrapper around the pure bulk-ingestion path."""

        errors = await self.validate_jira_export(json_data)
        if errors:
            return {"success": False, "errors": errors}

        try:
            data = json.loads(json_data)
            result = self.import_issues(list(data.get("issues", [])))
        except Exception as exc:  # pragma: no cover - compatibility wrapper
            logger.exception("Jira import failed")
            return {"success": False, "errors": [f"Import failed: {exc!s}"]}

        return {
            "success": len(result.errors) == 0,
            "project_id": str(self._project_id()),
            "items_imported": result.requirements_created,
            "links_imported": result.trace_links_created,
            "errors": result.errors,
            "agent_id": agent_id,
        }
