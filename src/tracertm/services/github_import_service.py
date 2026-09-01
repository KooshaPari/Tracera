"""GitHub issue bulk import into TraceRTM trace-link objects."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
from uuid import NAMESPACE_DNS, UUID, uuid5

from tracertm.models.trace_link import (
    ArtifactKind,
    Requirement,
    TraceLink,
    TraceLinkType,
)


@dataclass
class BulkIngestionResult:
    """Summary of a bulk ingestion run."""

    total_processed: int
    requirements_created: int
    trace_links_created: int
    errors: list[str] = field(default_factory=list)


class GitHubImportService:
    """Map GitHub issues to Requirements + IMPLEMENTS links."""

    _DEFAULT_CONFIDENCE: float = 0.70
    _LABELED_CONFIDENCE: float = 0.85

    def __init__(self, session: Any | None = None) -> None:
        self.session = session
        self.last_requirements: list[Requirement] = []
        self.last_trace_links: list[TraceLink] = []

    @staticmethod
    def _project_id_for_repo(repo: str) -> UUID:
        return uuid5(NAMESPACE_DNS, f"tracertm:github:{repo}")

    @staticmethod
    def _issue_ref(issue: dict[str, Any]) -> str:
        issue_id = issue.get("number") or issue.get("id")
        if issue_id is not None:
            return str(issue_id)
        return "unknown"

    @staticmethod
    def _label_names(issue: dict[str, Any]) -> list[str]:
        raw = issue.get("labels") or []
        names: list[str] = []
        for label in raw:
            if isinstance(label, str):
                names.append(label)
            elif isinstance(label, dict):
                name = label.get("name")
                if isinstance(name, str):
                    names.append(name)
        return names

    def _map_issue(
        self,
        repo: str,
        project_id: UUID,
        issue: dict[str, Any],
    ) -> tuple[Requirement, TraceLink]:
        title = issue.get("title")
        if not isinstance(title, str) or not title.strip():
            raise ValueError("missing title")

        issue_ref = self._issue_ref(issue)
        labels = self._label_names(issue)
        confidence = self._LABELED_CONFIDENCE if labels else self._DEFAULT_CONFIDENCE
        body = issue.get("body")
        description = body if isinstance(body, str) else None

        requirement_id = uuid5(project_id, f"requirement:{repo}:{issue_ref}")
        source_id = uuid5(project_id, f"github-issue:{repo}:{issue_ref}")

        requirement = Requirement(
            id=requirement_id,
            project_id=project_id,
            kind=ArtifactKind.REQUIREMENT,
            title=title.strip(),
            description=description,
            external_id=issue_ref,
            metadata={"repo": repo, "labels": labels},
        )
        trace_link = TraceLink(
            project_id=project_id,
            source_artifact_id=source_id,
            target_artifact_id=requirement_id,
            link_type=TraceLinkType.IMPLEMENTS,
            confidence=confidence,
            rationale=f"Imported from GitHub issue {issue_ref} in {repo}",
        )
        return requirement, trace_link

    def import_issues(self, repo: str, issues: list[dict[str, Any]]) -> BulkIngestionResult:
        project_id = self._project_id_for_repo(repo)
        requirements: list[Requirement] = []
        trace_links: list[TraceLink] = []
        errors: list[str] = []

        for issue in issues:
            try:
                requirement, trace_link = self._map_issue(repo, project_id, issue)
            except ValueError as exc:
                errors.append(f"Issue {self._issue_ref(issue)}: {exc}")
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
