"""Bulk ingestion endpoints for external issue sources."""

from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from tracertm.api.deps import auth_guard
from tracertm.services.github_import_service import BulkIngestionResult, GitHubImportService
from tracertm.services.jira_import_service import JiraImportService

router = APIRouter(prefix="/ingest", tags=["ingest"])


class GitHubIssueIngestRequest(BaseModel):
    repo: str = Field(min_length=1)
    issues: list[dict[str, Any]] = Field(default_factory=list)


class JiraIssueIngestRequest(BaseModel):
    issues: list[dict[str, Any]] = Field(default_factory=list)


@router.post("/github")
async def ingest_github_issues(
    body: GitHubIssueIngestRequest,
    _claims: Annotated[dict[str, Any], Depends(auth_guard)],
) -> BulkIngestionResult:
    """Bulk-ingest GitHub issues into Requirements + TraceLinks."""

    service = GitHubImportService()
    return service.import_issues(body.repo, body.issues)


@router.post("/jira")
async def ingest_jira_issues(
    body: JiraIssueIngestRequest,
    _claims: Annotated[dict[str, Any], Depends(auth_guard)],
) -> BulkIngestionResult:
    """Bulk-ingest Jira issues into Requirements + TraceLinks."""

    service = JiraImportService()
    return service.import_issues(body.issues)

