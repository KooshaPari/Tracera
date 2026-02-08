"""Integration sync processor for queue-driven sync tasks."""

from __future__ import annotations

import time
from typing import TYPE_CHECKING, Any

from tracertm.clients.github_client import GitHubClient, IssueListParams, IssueUpdateParams
from tracertm.clients.linear_client import LinearClient
from tracertm.repositories.integration_repository import (
    IntegrationCredentialRepository,
    IntegrationMappingRepository,
    IntegrationSyncLogRepository,
    IntegrationSyncQueueRepository,
)
from tracertm.repositories.item_repository import ItemRepository
from tracertm.services.encryption_service import EncryptionService

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


class IntegrationSyncProcessor:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        encryption_key = __import__("os").environ.get("ENCRYPTION_KEY", "")
        encryption_service = EncryptionService(encryption_key) if encryption_key else None
        self.credentials = IntegrationCredentialRepository(session, encryption_service)
        self.mappings = IntegrationMappingRepository(session)
        self.queue = IntegrationSyncQueueRepository(session)
        self.logs = IntegrationSyncLogRepository(session)

    async def process_queue_item(self, queue_item: Any) -> dict[str, Any]:
        started = time.monotonic()
        await self.queue.mark_processing(queue_item.id)

        mapping = await self.mappings.get_by_id(queue_item.mapping_id)
        credential = await self.credentials.get_by_id(queue_item.integration_credential_id)
        if not mapping or not credential:
            await self.queue.mark_failed(queue_item.id, "mapping_or_credential_missing")
            return {"status": "failed", "error": "mapping_or_credential_missing"}

        token = self.credentials.decrypt_token(credential)
        payload = queue_item.payload or {}
        provider = credential.provider
        direction = self._normalize_direction(queue_item.direction)

        try:
            result = await self._sync_provider(provider, token, mapping, payload, direction)
            await self.logs.create(
                mapping_id=mapping.id,
                operation=queue_item.event_type,
                direction=direction,
                source_system=provider,
                source_id=str(mapping.external_id),
                target_system="tracertm",
                target_id=str(mapping.tracertm_item_id),
                success=True,
                changes=result or {},
                sync_queue_id=queue_item.id,
            )
            await self.mappings.update_sync_status(mapping.id, success=True, direction=direction)
            await self.queue.mark_completed(queue_item.id, int((time.monotonic() - started) * 1000))
            return {"status": "completed", "result": result}
        except Exception as exc:
            await self.logs.create(
                mapping_id=mapping.id,
                operation=queue_item.event_type,
                direction=direction,
                source_system=provider,
                source_id=str(mapping.external_id),
                target_system="tracertm",
                target_id=str(mapping.tracertm_item_id),
                success=False,
                error_message=str(exc),
                sync_queue_id=queue_item.id,
            )
            await self.mappings.update_sync_status(mapping.id, success=False, direction=direction, error=str(exc))
            await self.queue.mark_failed(queue_item.id, str(exc))
            return {"status": "failed", "error": str(exc)}

    async def process_pending(self, limit: int = 50) -> dict[str, Any]:
        pending = await self.queue.get_pending(limit=limit)
        results = [await self.process_queue_item(item) for item in pending]
        return {"processed": len(results), "results": results}

    async def process_retryable(self, limit: int = 50) -> dict[str, Any]:
        retryable = await self.queue.get_retryable()
        results = [await self.process_queue_item(item) for item in retryable[:limit]]
        return {"processed": len(results), "results": results}

    async def _do_sync_github(
        self,
        client: GitHubClient,
        provider: str,
        mapping: Any,
        payload: dict[str, Any],
        direction: str,
    ) -> dict[str, Any]:
        """Handle github provider sync; caller must close client."""
        repo_name = mapping.mapping_metadata.get("repo_full_name") or mapping.external_id
        if direction in {"external_to_tracertm", "bidirectional"} and repo_name and "/" in repo_name:
            owner, repo = repo_name.split("/", 1)
            return await self._sync_github_repo_issues(client=client, mapping=mapping, owner=owner, repo=repo)
        if direction in {"tracertm_to_external", "bidirectional"}:
            return await self._push_github_issue_update(client=client, mapping=mapping, payload=payload)
        user = await client.get_authenticated_user()
        return {"provider": provider, "user": user.get("login")}

    async def _do_sync_github_projects(
        self,
        client: GitHubClient,
        provider: str,
        mapping: Any,
        direction: str,
    ) -> dict[str, Any]:
        """Handle github_projects provider sync; caller must close client."""
        project_id = mapping.mapping_metadata.get("project_id") or mapping.external_id
        if direction in {"external_to_tracertm", "bidirectional"} and project_id:
            return await self._sync_github_project_items(client=client, mapping=mapping, project_id=project_id)
        user = await client.get_authenticated_user()
        return {"provider": provider, "user": user.get("login")}

    async def _do_sync_linear(
        self,
        client: LinearClient,
        provider: str,
        mapping: Any,
        payload: dict[str, Any],
        direction: str,
    ) -> dict[str, Any]:
        """Handle linear provider sync; caller must close client."""
        team_id = mapping.mapping_metadata.get("team_id")
        project_id = mapping.mapping_metadata.get("project_id") or mapping.external_id
        if direction in {"external_to_tracertm", "bidirectional"}:
            if team_id:
                return await self._sync_linear_team_issues(client=client, mapping=mapping, team_id=team_id)
            if project_id:
                return await self._sync_linear_project_issues(client=client, mapping=mapping, project_id=project_id)
        if direction in {"tracertm_to_external", "bidirectional"}:
            return await self._push_linear_issue_update(client=client, mapping=mapping, payload=payload)
        viewer = await client.get_viewer()
        return {"provider": provider, "viewer": viewer.get("name")}

    async def _sync_provider(
        self,
        provider: str,
        token: str,
        mapping: Any,
        payload: dict[str, Any],
        direction: str,
    ) -> dict[str, Any]:
        if provider == "github":
            client = GitHubClient(token)
            try:
                return await self._do_sync_github(client, provider, mapping, payload, direction)
            finally:
                await client.close()
        if provider == "github_projects":
            client = GitHubClient(token)
            try:
                return await self._do_sync_github_projects(client, provider, mapping, direction)
            finally:
                await client.close()
        if provider == "linear":
            client = LinearClient(token)
            try:
                return await self._do_sync_linear(client, provider, mapping, payload, direction)
            finally:
                await client.close()
        return {
            "provider": provider,
            "status": "noop",
            "direction": direction,
            "payload": payload,
        }

    def _normalize_direction(self, direction: str) -> str:
        if direction in {"pull", "external_to_tracertm"}:
            return "external_to_tracertm"
        if direction in {"push", "tracertm_to_external"}:
            return "tracertm_to_external"
        return direction

    async def _sync_github_repo_issues(
        self,
        client: GitHubClient,
        mapping: Any,
        owner: str,
        repo: str,
    ) -> dict[str, Any]:
        items_repo = ItemRepository(self.session)
        mapping_repo = IntegrationMappingRepository(self.session)
        repo_full_name = f"{owner}/{repo}"
        issues = await client.list_issues(
            owner,
            repo,
            params=IssueListParams(state="all", per_page=50, page=1),
        )
        created = 0
        updated = 0
        for issue in issues:
            if issue.get("pull_request"):
                continue
            external_id = str(issue.get("id"))
            title = issue.get("title") or "Untitled Issue"
            description = issue.get("body")
            state = issue.get("state") or "open"
            status = "done" if state == "closed" else "todo"
            assignee = issue.get("assignee") or {}
            owner_name = assignee.get("login")
            labels = [label.get("name") for label in issue.get("labels", []) if isinstance(label, dict)]
            item_metadata = {
                "external_system": "github",
                "repo_full_name": repo_full_name,
                "issue_number": issue.get("number"),
                "state": state,
                "labels": labels,
                "url": issue.get("html_url"),
                "external_id": external_id,
                "external_key": f"{repo_full_name}#{issue.get('number')}",
            }
            existing = await mapping_repo.get_by_external_id(mapping.project_id, external_id)
            if existing:
                item = await items_repo.get_by_id(existing.tracertm_item_id, mapping.project_id)
                if item:
                    await items_repo.update(
                        str(item.id),
                        item.version,
                        title=title,
                        description=description,
                        status=status,
                        owner=owner_name,
                        item_metadata=item_metadata,
                    )
                    updated += 1
                continue

            new_item = await items_repo.create(
                project_id=mapping.project_id,
                title=title,
                view="integrations",
                item_type="issue",
                description=description,
                status=status,
                parent_id=mapping.tracertm_item_id,
                metadata=item_metadata,
                owner=owner_name,
                priority="medium",
            )
            await mapping_repo.create(
                project_id=mapping.project_id,
                credential_id=mapping.integration_credential_id,
                tracertm_item_id=str(new_item.id),
                tracertm_item_type="issue",
                external_system="github",
                external_id=external_id,
                external_url=issue.get("html_url") or "",
                direction=mapping.direction,
                auto_sync=mapping.auto_sync,
                mapping_metadata={
                    "repo_full_name": repo_full_name,
                    "issue_number": issue.get("number"),
                    "external_key": item_metadata["external_key"],
                },
            )
            created += 1

        return {"provider": "github", "repo": repo_full_name, "created": created, "updated": updated}

    async def _sync_github_project_items(
        self,
        client: GitHubClient,
        mapping: Any,
        project_id: str,
    ) -> dict[str, Any]:
        items_repo = ItemRepository(self.session)
        mapping_repo = IntegrationMappingRepository(self.session)
        items = await client.get_project_items(project_id, first=100)
        created = 0
        updated = 0
        for item in items:
            content = item.get("content") or {}
            if content.get("id") is None:
                continue
            external_id = str(content.get("id"))
            title = content.get("title") or "Untitled Item"
            description = None
            status = "todo"
            item_metadata = {
                "external_system": "github_projects",
                "project_id": project_id,
                "external_id": external_id,
                "external_key": content.get("number") or content.get("id"),
                "url": content.get("url"),
                "type": content.get("__typename") or content.get("type"),
            }
            existing = await mapping_repo.get_by_external_id(mapping.project_id, external_id)
            if existing:
                item_row = await items_repo.get_by_id(existing.tracertm_item_id, mapping.project_id)
                if item_row:
                    await items_repo.update(
                        str(item_row.id),
                        item_row.version,
                        title=title,
                        description=description,
                        status=status,
                        item_metadata=item_metadata,
                    )
                    updated += 1
                continue

            new_item = await items_repo.create(
                project_id=mapping.project_id,
                title=title,
                view="integrations",
                item_type="issue",
                description=description,
                status=status,
                parent_id=mapping.tracertm_item_id,
                metadata=item_metadata,
                priority="medium",
            )
            await mapping_repo.create(
                project_id=mapping.project_id,
                credential_id=mapping.integration_credential_id,
                tracertm_item_id=str(new_item.id),
                tracertm_item_type="issue",
                external_system="github_projects",
                external_id=external_id,
                external_url=content.get("url") or "",
                direction=mapping.direction,
                auto_sync=mapping.auto_sync,
                mapping_metadata={
                    "project_id": project_id,
                    "external_key": item_metadata["external_key"],
                },
            )
            created += 1
        return {"provider": "github_projects", "project_id": project_id, "created": created, "updated": updated}

    async def _sync_linear_team_issues(
        self,
        client: LinearClient,
        mapping: Any,
        team_id: str,
    ) -> dict[str, Any]:
        items_repo = ItemRepository(self.session)
        mapping_repo = IntegrationMappingRepository(self.session)
        result = await client.list_issues(team_id=team_id, first=50)
        issues = result.get("issues", {}).get("nodes", [])
        created = 0
        updated = 0
        for issue in issues:
            external_id = str(issue.get("id"))
            title = issue.get("title") or "Untitled Issue"
            description = issue.get("description")
            state = (issue.get("state") or {}).get("type") or "open"
            status = "done" if state in {"completed", "canceled"} else "todo"
            assignee = issue.get("assignee") or {}
            owner_name = assignee.get("name")
            item_metadata = {
                "external_system": "linear",
                "team_id": team_id,
                "identifier": issue.get("identifier"),
                "state": state,
                "url": issue.get("url"),
                "external_id": external_id,
                "external_key": issue.get("identifier"),
            }
            existing = await mapping_repo.get_by_external_id(mapping.project_id, external_id)
            if existing:
                item_row = await items_repo.get_by_id(existing.tracertm_item_id, mapping.project_id)
                if item_row:
                    await items_repo.update(
                        str(item_row.id),
                        item_row.version,
                        title=title,
                        description=description,
                        status=status,
                        owner=owner_name,
                        item_metadata=item_metadata,
                    )
                    updated += 1
                continue

            new_item = await items_repo.create(
                project_id=mapping.project_id,
                title=title,
                view="integrations",
                item_type="issue",
                description=description,
                status=status,
                parent_id=mapping.tracertm_item_id,
                metadata=item_metadata,
                owner=owner_name,
                priority="medium",
            )
            await mapping_repo.create(
                project_id=mapping.project_id,
                credential_id=mapping.integration_credential_id,
                tracertm_item_id=str(new_item.id),
                tracertm_item_type="issue",
                external_system="linear",
                external_id=external_id,
                external_url=issue.get("url") or "",
                direction=mapping.direction,
                auto_sync=mapping.auto_sync,
                mapping_metadata={
                    "team_id": team_id,
                    "external_key": issue.get("identifier"),
                },
            )
            created += 1

        return {"provider": "linear", "team_id": team_id, "created": created, "updated": updated}

    async def _sync_linear_project_issues(
        self,
        client: LinearClient,
        mapping: Any,
        project_id: str,
    ) -> dict[str, Any]:
        items_repo = ItemRepository(self.session)
        mapping_repo = IntegrationMappingRepository(self.session)
        project = await client.get_project(project_id)
        issues = (project.get("issues") or {}).get("nodes", [])
        created = 0
        updated = 0
        for issue in issues:
            external_id = str(issue.get("id"))
            title = issue.get("title") or "Untitled Issue"
            state = (issue.get("state") or {}).get("type") or "open"
            status = "done" if state in {"completed", "canceled"} else "todo"
            item_metadata = {
                "external_system": "linear",
                "project_id": project_id,
                "identifier": issue.get("identifier"),
                "state": state,
                "external_id": external_id,
                "external_key": issue.get("identifier"),
            }
            existing = await mapping_repo.get_by_external_id(mapping.project_id, external_id)
            if existing:
                item_row = await items_repo.get_by_id(existing.tracertm_item_id, mapping.project_id)
                if item_row:
                    await items_repo.update(
                        str(item_row.id),
                        item_row.version,
                        title=title,
                        status=status,
                        item_metadata=item_metadata,
                    )
                    updated += 1
                continue

            new_item = await items_repo.create(
                project_id=mapping.project_id,
                title=title,
                view="integrations",
                item_type="issue",
                description=None,
                status=status,
                parent_id=mapping.tracertm_item_id,
                metadata=item_metadata,
                priority="medium",
            )
            await mapping_repo.create(
                project_id=mapping.project_id,
                credential_id=mapping.integration_credential_id,
                tracertm_item_id=str(new_item.id),
                tracertm_item_type="issue",
                external_system="linear",
                external_id=external_id,
                external_url=issue.get("url") or "",
                direction=mapping.direction,
                auto_sync=mapping.auto_sync,
                mapping_metadata={
                    "project_id": project_id,
                    "external_key": issue.get("identifier"),
                },
            )
            created += 1

        return {"provider": "linear", "project_id": project_id, "created": created, "updated": updated}

    async def _push_github_issue_update(
        self,
        client: GitHubClient,
        mapping: Any,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        repo_name = mapping.mapping_metadata.get("repo_full_name")
        issue_number = mapping.mapping_metadata.get("issue_number")
        if not repo_name or not issue_number:
            return {"provider": "github", "status": "skipped", "reason": "missing_repo_or_issue_number"}
        owner, repo = repo_name.split("/", 1)

        title = payload.get("title")
        body = payload.get("description")
        state = payload.get("state")
        if title is None and body is None and state is None:
            items_repo = ItemRepository(self.session)
            item = await items_repo.get_by_id(mapping.tracertm_item_id, mapping.project_id)
            if item:
                title = item.title
                body = item.description
        updated = await client.update_issue(
            owner,
            repo,
            int(issue_number),
            params=IssueUpdateParams(title=title, body=body, state=state),
        )
        return {"provider": "github", "issue": updated.get("html_url")}

    async def _push_linear_issue_update(
        self,
        client: LinearClient,
        mapping: Any,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        issue_id = mapping.external_id
        if not issue_id:
            return {"provider": "linear", "status": "skipped", "reason": "missing_issue_id"}
        title = payload.get("title")
        description = payload.get("description")
        if title is None and description is None:
            items_repo = ItemRepository(self.session)
            item = await items_repo.get_by_id(mapping.tracertm_item_id, mapping.project_id)
            if item:
                title = item.title
                description = item.description
        updated = await client.update_issue(issue_id, title=title, description=description)
        return {"provider": "linear", "issue": updated.get("id")}
