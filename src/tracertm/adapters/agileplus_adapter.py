"""Async adapter for pushing traceability data to AgilePlus."""

from __future__ import annotations

import contextlib
import json
from typing import TYPE_CHECKING, Any

import httpx
from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from tracertm.models.trace_link import Requirement, TraceLink

_DEFAULT_TIMEOUT = 30.0
_STATUS_BAD_REQUEST = 400


class AgilePlusPushResult(BaseModel):
    """Result from pushing a single requirement or trace link."""

    success: bool
    agileplus_id: str | None = None
    error: str | None = None


class BulkPushResult(BaseModel):
    """Result from a bulk project push."""

    total: int
    succeeded: int
    failed: int
    errors: list[str] = Field(default_factory=list)


class AgilePlusAdapter:
    """Push requirements and trace links to AgilePlus over HTTP."""

    def __init__(
        self,
        base_url: str,
        api_key: str,
        http_client: httpx.AsyncClient | None = None,
        timeout: float = _DEFAULT_TIMEOUT,
    ) -> None:
        """Initialize the adapter."""
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout
        self._client = http_client
        self._owns_client = http_client is None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=self.timeout,
            )
        return self._client

    async def close(self) -> None:
        """Close the owned HTTP client, if any."""
        if self._client is not None and self._owns_client:
            await self._client.aclose()
            self._client = None

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

    @staticmethod
    def _response_json(response: httpx.Response) -> dict[str, Any] | list[Any] | None:
        with contextlib.suppress(ValueError, json.JSONDecodeError):
            data = response.json()
            if isinstance(data, (dict, list, type(None))):
                return data
        return None

    @classmethod
    def _extract_identifier(cls, payload: Any) -> str | None:
        if isinstance(payload, dict):
            return cls._extract_identifier_from_dict(payload)
        if isinstance(payload, list):
            return cls._extract_identifier_from_list(payload)
        return None

    @classmethod
    def _extract_identifier_from_dict(cls, payload: dict[str, Any]) -> str | None:
        for key in ("agileplus_id", "id", "external_id"):
            value = payload.get(key)
            if isinstance(value, str) and value.strip():
                return value

        for key in ("data", "requirement", "link", "result"):
            identifier = cls._extract_identifier(payload.get(key))
            if identifier:
                return identifier

        for value in payload.values():
            identifier = cls._extract_identifier(value)
            if identifier:
                return identifier
        return None

    @classmethod
    def _extract_identifier_from_list(cls, payload: list[Any]) -> str | None:
        for item in payload:
            identifier = cls._extract_identifier(item)
            if identifier:
                return identifier
        return None

    @staticmethod
    def _stringify_failure(response: httpx.Response | None, error: Exception | str) -> str:
        if isinstance(error, str):
            return error
        if response is not None:
            return f"HTTP {response.status_code}"
        return str(error)

    def _requirement_payload(self, requirement: Requirement) -> dict[str, Any]:
        metadata: dict[str, Any] = {
            "external_id": str(requirement.id),
            "project_id": str(requirement.project_id),
            "kind": requirement.kind.value,
            "status": requirement.status.value,
        }
        if requirement.priority is not None:
            metadata["priority"] = requirement.priority
        if requirement.rationale is not None:
            metadata["rationale"] = requirement.rationale
        if requirement.acceptance_criteria:
            metadata["acceptance_criteria"] = requirement.acceptance_criteria
        if requirement.verification_method is not None:
            metadata["verification_method"] = requirement.verification_method.value
        if requirement.external_id is not None:
            metadata["source_external_id"] = requirement.external_id
        if requirement.metadata:
            metadata["source_metadata"] = requirement.metadata

        return {
            "title": requirement.title,
            "body": requirement.description,
            "metadata": metadata,
        }

    def _trace_link_payload(self, link: TraceLink) -> dict[str, Any]:
        trace_link = {
            "id": str(link.id),
            "project_id": str(link.project_id),
            "source_artifact_id": str(link.source_artifact_id),
            "target_artifact_id": str(link.target_artifact_id),
            "link_type": link.link_type.value,
            "confidence": link.confidence,
            "rationale": link.rationale,
            "metadata": link.metadata,
        }
        return {
            "tags": [
                f"trace-link:{link.link_type.value.lower()}",
                f"trace-link:{link.id}",
            ],
            "metadata": {
                "trace_link": trace_link,
            },
        }

    async def _post_json(self, path: str, payload: dict[str, Any]) -> AgilePlusPushResult:
        client = await self._get_client()
        try:
            response = await client.post(path, json=payload, headers=self._headers())
        except httpx.HTTPError as exc:
            return AgilePlusPushResult(success=False, error=self._stringify_failure(None, exc))

        if response.status_code >= _STATUS_BAD_REQUEST:
            return AgilePlusPushResult(success=False, error=f"HTTP {response.status_code}")

        parsed = self._response_json(response)
        if parsed is None:
            return AgilePlusPushResult(success=False, error="Invalid AgilePlus response")

        agileplus_id = self._extract_identifier(parsed)
        if not agileplus_id:
            return AgilePlusPushResult(success=False, error="Missing AgilePlus id in response")

        return AgilePlusPushResult(success=True, agileplus_id=agileplus_id)

    async def push_requirement(self, req: Requirement) -> AgilePlusPushResult:
        """Push one requirement to AgilePlus."""
        return await self._post_json("/api/stories", self._requirement_payload(req))

    async def push_trace_link(self, link: TraceLink) -> AgilePlusPushResult:
        """Push one trace link to AgilePlus."""
        return await self._post_json(
            f"/api/stories/{link.target_artifact_id}/tags",
            self._trace_link_payload(link),
        )

    async def push_project_requirements(
        self,
        project_id: str,
        requirements: list[Requirement],
        links: list[TraceLink],
    ) -> BulkPushResult:
        """Push a project's requirements and trace links to AgilePlus."""
        total = len(requirements) + len(links)
        succeeded = 0
        failed = 0
        errors: list[str] = []

        for requirement in requirements:
            if str(requirement.project_id) != str(project_id):
                failed += 1
                errors.append(
                    f"Requirement {requirement.title} ({requirement.id}) belongs to project {requirement.project_id}, not {project_id}",
                )
                continue
            result = await self.push_requirement(requirement)
            if result.success:
                succeeded += 1
                continue
            failed += 1
            errors.append(
                f"Requirement {requirement.title} ({requirement.id}) push failed: {result.error or 'unknown error'}",
            )

        for link in links:
            if str(link.project_id) != str(project_id):
                failed += 1
                errors.append(
                    f"Trace link {link.id} belongs to project {link.project_id}, not {project_id}",
                )
                continue
            result = await self.push_trace_link(link)
            if result.success:
                succeeded += 1
                continue
            failed += 1
            errors.append(f"Trace link {link.id} push failed: {result.error or 'unknown error'}")

        return BulkPushResult(total=total, succeeded=succeeded, failed=failed, errors=errors)
