"""Bulk ingestion helpers for GitHub issues."""

from __future__ import annotations

import json
import logging
import uuid
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from tracertm.models.trace_link import ArtifactKind, Requirement, TraceLink, TraceLinkType

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


@dataclass
class BulkIngestionResult:
    """Summary of a bulk ingestion run."""

    total_processed: int
    requirements_created: int
    trace_links_created: int
    errors: list[str] = field(default_factory=list)


class GitHubImportService:
    """Import GitHub issues into canonical TraceRTM trace-link objects."""

    STATUS_MAP: dict[str, str] = {
        "open": "todo",
        "in_progress": "in_progress",
        "in review": "in_progress",
        "closed": "complete",
        "done": "complete",
    }
    TYPE_MAP: dict[str, str] = {
        "issue": "task",
        "pull_request": "task",
        "discussion": "task",
    }

    _DEFAULT_CONFIDENCE: float = 0.70
    _LABELED_CONFIDENCE: float = 0.85

    def __init__(self, session: AsyncSession | None = None, http_client: Any | None = None) -> None:
        self.session = session
        self.http_client = http_client
        self.last_requirements: list[Requirement] = []
        self.last_trace_links: list[TraceLink] = []

        # Legacy compatibility: keep repository attributes available when a DB session is supplied.
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
    def _project_id_for_repo(repo: str) -> uuid.UUID:
        return uuid.uuid5(uuid.NAMESPACE_URL, f"tracertm:github:repo:{repo}")

    @staticmethod
    def _external_id(issue: dict[str, Any]) -> str:
        number = issue.get("number")
        issue_id = issue.get("id")
        if number is not None:
            return str(number)
        if issue_id is not None:
            return str(issue_id)
        raise ValueError("GitHub issue is missing both 'number' and 'id'")

    @staticmethod
    def _has_labels(issue: dict[str, Any]) -> bool:
        labels = issue.get("labels", [])
        if isinstance(labels, list):
            return len(labels) > 0
        return bool(labels)

    @staticmethod
    def _issue_label(issue: dict[str, Any], index: int) -> str:
        for key in ("number", "id", "title", "name"):
            value = issue.get(key)
            if value not in (None, ""):
                return str(value)
        return f"#{index + 1}"

    def _requirement_id(self, repo: str, external_id: str) -> uuid.UUID:
        return uuid.uuid5(uuid.NAMESPACE_URL, f"tracertm:github:req:{repo}:{external_id}")

    def _source_artifact_id(self, repo: str, external_id: str) -> uuid.UUID:
        return uuid.uuid5(uuid.NAMESPACE_URL, f"tracertm:github:src:{repo}:{external_id}")

    def _build_requirement(self, repo: str, issue: dict[str, Any]) -> Requirement:
        title = issue.get("title")
        if not isinstance(title, str) or not title.strip():
            raise ValueError("GitHub issue is missing required 'title'")

        external_id = self._external_id(issue)
        project_id = self._project_id_for_repo(repo)

        return Requirement(
            id=self._requirement_id(repo, external_id),
            project_id=project_id,
            kind=ArtifactKind.REQUIREMENT,
            title=title.strip(),
            description=issue.get("body") if isinstance(issue.get("body"), str) else None,
            external_id=external_id,
            metadata={
                "source": "github",
                "repo": repo,
                "issue_id": issue.get("id"),
                "issue_number": issue.get("number"),
                "labels": issue.get("labels", []),
            },
        )

    def _build_trace_link(self, repo: str, requirement: Requirement, issue: dict[str, Any]) -> TraceLink:
        external_id = requirement.external_id or self._external_id(issue)
        confidence = self._LABELED_CONFIDENCE if self._has_labels(issue) else self._DEFAULT_CONFIDENCE
        return TraceLink(
            id=uuid.uuid5(uuid.NAMESPACE_URL, f"tracertm:github:link:{repo}:{external_id}"),
            project_id=requirement.project_id,
            source_artifact_id=self._source_artifact_id(repo, external_id),
            target_artifact_id=requirement.id,
            link_type=TraceLinkType.IMPLEMENTS,
            confidence=confidence,
            rationale="Imported from GitHub issue",
            metadata={
                "source": "github",
                "repo": repo,
                "external_id": external_id,
            },
        )

    def import_issues(self, repo: str, issues: list[dict[str, Any]]) -> BulkIngestionResult:
        """Map GitHub issues to Requirements + IMPLEMENTS links."""

        self.last_requirements = []
        self.last_trace_links = []

        errors: list[str] = []
        for index, issue in enumerate(issues):
            try:
                requirement = self._build_requirement(repo, issue)
                trace_link = self._build_trace_link(repo, requirement, issue)
            except Exception as exc:  # pragma: no cover - exercised via tests
                errors.append(f"GitHub issue {self._issue_label(issue, index)}: {exc}")
                continue

            self.last_requirements.append(requirement)
            self.last_trace_links.append(trace_link)

        return BulkIngestionResult(
            total_processed=len(issues),
            requirements_created=len(self.last_requirements),
            trace_links_created=len(self.last_trace_links),
            errors=errors,
        )

    async def validate_github_export(self, json_data: str) -> list[str]:
        """Validate a GitHub export payload."""

        try:
            data = json.loads(json_data)
        except json.JSONDecodeError as exc:
            return [f"Invalid JSON: {exc!s}"]

        if "items" not in data and "issues" not in data:
            return ["Missing 'items' or 'issues' field"]
        if not isinstance(data.get("items", data.get("issues", [])), list):
            return ["'items' or 'issues' must be a list"]
        return []

    async def import_github_project(
        self,
        project_name: str,
        json_data: str,
        agent_id: str = "system",
    ) -> dict[str, Any]:
        """Legacy wrapper around the pure bulk-ingestion path."""

        errors = await self.validate_github_export(json_data)
        if errors:
            return {"success": False, "errors": errors}

        try:
            data = json.loads(json_data)
            issues = data.get("items", data.get("issues", []))
            result = self.import_issues(project_name, list(issues))
        except Exception as exc:  # pragma: no cover - compatibility wrapper
            logger.exception("GitHub import failed")
            return {"success": False, "errors": [f"Import failed: {exc!s}"]}

        return {
            "success": len(result.errors) == 0,
            "project_id": str(self._project_id_for_repo(project_name)),
            "items_imported": result.requirements_created,
            "links_imported": result.trace_links_created,
            "errors": result.errors,
            "agent_id": agent_id,
        }
