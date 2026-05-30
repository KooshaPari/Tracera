from __future__ import annotations

import json
import uuid
from typing import Any

import httpx
import pytest

from tracertm.adapters.agileplus_adapter import AgilePlusAdapter
from tracertm.models.trace_link import Requirement, RequirementStatus, TraceLink, TraceLinkType

pytestmark = pytest.mark.unit

PROJECT_ID = uuid.UUID("11111111-1111-1111-1111-111111111111")
OTHER_PROJECT_ID = uuid.UUID("22222222-2222-2222-2222-222222222222")


def _requirement(
    title: str = "Requirement 1",
    *,
    requirement_id: uuid.UUID | None = None,
    project_id: uuid.UUID = PROJECT_ID,
) -> Requirement:
    return Requirement(
        id=requirement_id or uuid.uuid4(),
        project_id=project_id,
        title=title,
        description="A traced requirement",
        status=RequirementStatus.APPROVED,
        priority=3,
        rationale="Business need",
        acceptance_criteria=["works"],
    )


def _trace_link(
    *,
    source_artifact_id: uuid.UUID | None = None,
    target_artifact_id: uuid.UUID | None = None,
    link_type: TraceLinkType = TraceLinkType.SATISFIES,
    project_id: uuid.UUID = PROJECT_ID,
) -> TraceLink:
    source_id = source_artifact_id or uuid.uuid4()
    target_id = target_artifact_id or uuid.uuid4()
    return TraceLink(
        id=uuid.uuid4(),
        project_id=project_id,
        source_artifact_id=source_id,
        target_artifact_id=target_id,
        link_type=link_type,
        confidence=0.85,
        rationale="Trace evidence",
    )


class _Handler:
    def __init__(self, callback: Any) -> None:
        self.callback = callback
        self.requests: list[httpx.Request] = []

    def __call__(self, request: httpx.Request) -> httpx.Response:
        self.requests.append(request)
        return self.callback(request)


def _adapter_with(callback: Any, *, base_url: str = "https://agileplus.example") -> tuple[AgilePlusAdapter, _Handler]:
    handler = _Handler(callback)
    transport = httpx.MockTransport(handler)
    client = httpx.AsyncClient(transport=transport, base_url=base_url)
    return AgilePlusAdapter(base_url=base_url, api_key="secret-key", http_client=client), handler


@pytest.mark.asyncio
async def test_adapter_uses_authorization_header() -> None:
    def callback(request: httpx.Request) -> httpx.Response:
        assert request.headers["authorization"] == "Bearer secret-key"
        return httpx.Response(200, json={"id": "ap-1"})

    adapter, _handler = _adapter_with(callback)
    await adapter.push_requirement(_requirement())


@pytest.mark.asyncio
async def test_push_requirement_success_parses_id() -> None:
    def callback(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(201, json={"id": "req-123"})

    adapter, _handler = _adapter_with(callback)
    result = await adapter.push_requirement(_requirement())

    assert result.success is True
    assert result.agileplus_id == "req-123"
    assert result.error is None


@pytest.mark.asyncio
async def test_push_requirement_sends_expected_payload() -> None:
    requirement = _requirement(title="Payload check")

    def callback(request: httpx.Request) -> httpx.Response:
        body = json.loads(request.content)
        assert request.method == "POST"
        assert request.url.path == "/api/stories"
        assert body["title"] == "Payload check"
        assert body["body"] == "A traced requirement"
        assert body["metadata"]["external_id"] == str(requirement.id)
        assert body["metadata"]["project_id"] == str(requirement.project_id)
        assert body["metadata"]["status"] == RequirementStatus.APPROVED.value
        return httpx.Response(200, json={"agileplus_id": "req-456"})

    adapter, _handler = _adapter_with(callback)
    result = await adapter.push_requirement(requirement)

    assert result.success is True
    assert result.agileplus_id == "req-456"


@pytest.mark.asyncio
async def test_push_requirement_handles_non_success_status() -> None:
    def callback(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(400, json={"error": "bad request"})

    adapter, _handler = _adapter_with(callback)
    result = await adapter.push_requirement(_requirement())

    assert result.success is False
    assert result.agileplus_id is None
    assert result.error == "HTTP 400"


@pytest.mark.asyncio
async def test_push_requirement_handles_network_error() -> None:
    def callback(_request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("boom", request=httpx.Request("POST", "https://agileplus.example/api/stories"))

    adapter, _handler = _adapter_with(callback)
    result = await adapter.push_requirement(_requirement())

    assert result.success is False
    assert result.agileplus_id is None
    assert "boom" in (result.error or "")


@pytest.mark.asyncio
async def test_push_requirement_parses_nested_identifier() -> None:
    def callback(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"data": {"requirement": {"agileplus_id": "nested-1"}}})

    adapter, _handler = _adapter_with(callback)
    result = await adapter.push_requirement(_requirement())

    assert result.success is True
    assert result.agileplus_id == "nested-1"


@pytest.mark.asyncio
async def test_push_requirement_uses_other_project_id() -> None:
    requirement = _requirement(project_id=OTHER_PROJECT_ID)

    def callback(request: httpx.Request) -> httpx.Response:
        body = json.loads(request.content)
        assert body["metadata"]["project_id"] == str(OTHER_PROJECT_ID)
        return httpx.Response(200, json={"id": "req-999"})

    adapter, _handler = _adapter_with(callback)
    result = await adapter.push_requirement(requirement)

    assert result.success is True
    assert result.agileplus_id == "req-999"


@pytest.mark.asyncio
async def test_push_trace_link_success() -> None:
    def callback(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"id": "link-123"})

    adapter, _handler = _adapter_with(callback)
    result = await adapter.push_trace_link(_trace_link())

    assert result.success is True
    assert result.agileplus_id == "link-123"


@pytest.mark.asyncio
async def test_push_trace_link_sends_expected_payload() -> None:
    link = _trace_link()

    def callback(request: httpx.Request) -> httpx.Response:
        body = json.loads(request.content)
        assert request.method == "POST"
        assert request.url.path == f"/api/stories/{link.target_artifact_id}/tags"
        assert body["tags"] == [
            f"trace-link:{link.link_type.value.lower()}",
            f"trace-link:{link.id}",
        ]
        trace_link = body["metadata"]["trace_link"]
        assert trace_link["id"] == str(link.id)
        assert trace_link["project_id"] == str(link.project_id)
        assert trace_link["source_artifact_id"] == str(link.source_artifact_id)
        assert trace_link["target_artifact_id"] == str(link.target_artifact_id)
        assert trace_link["link_type"] == TraceLinkType.SATISFIES.value
        assert trace_link["confidence"] == pytest.approx(0.85)
        assert trace_link["rationale"] == "Trace evidence"
        return httpx.Response(201, json={"agileplus_id": "link-456"})

    adapter, _handler = _adapter_with(callback)
    result = await adapter.push_trace_link(link)

    assert result.success is True
    assert result.agileplus_id == "link-456"


@pytest.mark.asyncio
async def test_push_trace_link_handles_error_status() -> None:
    def callback(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(502, json={"error": "upstream"})

    adapter, _handler = _adapter_with(callback)
    result = await adapter.push_trace_link(_trace_link())

    assert result.success is False
    assert result.agileplus_id is None
    assert result.error == "HTTP 502"


@pytest.mark.asyncio
async def test_push_project_requirements_success_counts_all_items() -> None:
    req1 = _requirement(title="Req 1")
    req2 = _requirement(title="Req 2")
    link1 = _trace_link(source_artifact_id=uuid.uuid4(), target_artifact_id=req1.id)
    link2 = _trace_link(source_artifact_id=uuid.uuid4(), target_artifact_id=req2.id)

    def callback(request: httpx.Request) -> httpx.Response:
        payload = json.loads(request.content)
        if request.url.path == "/api/stories":
            return httpx.Response(200, json={"id": f"req-{payload['title'].lower().replace(' ', '-')}"})
        if request.url.path.endswith("/tags"):
            return httpx.Response(200, json={"id": f"link-{payload['metadata']['trace_link']['target_artifact_id'][-4:]}"})
        pytest.fail(f"unexpected path: {request.url.path}")

    adapter, _handler = _adapter_with(callback)
    result = await adapter.push_project_requirements(PROJECT_ID, [req1, req2], [link1, link2])

    assert result.total == 4
    assert result.succeeded == 4
    assert result.failed == 0
    assert result.errors == []


@pytest.mark.asyncio
async def test_push_project_requirements_partially_fails() -> None:
    req1 = _requirement(title="Req ok")
    req2 = _requirement(title="Req fail")
    link = _trace_link(source_artifact_id=uuid.uuid4(), target_artifact_id=req1.id)
    call_count = {"count": 0}

    def callback(request: httpx.Request) -> httpx.Response:
        call_count["count"] += 1
        if call_count["count"] == 2:
            return httpx.Response(500, json={"error": "nope"})
        return httpx.Response(200, json={"id": f"ok-{call_count['count']}"})

    adapter, _handler = _adapter_with(callback)
    result = await adapter.push_project_requirements(PROJECT_ID, [req1, req2], [link])

    assert result.total == 3
    assert result.succeeded == 2
    assert result.failed == 1
    assert len(result.errors) == 1
    assert "Req fail" in result.errors[0]


@pytest.mark.asyncio
async def test_push_project_requirements_handles_empty_inputs() -> None:
    def callback(_request: httpx.Request) -> httpx.Response:
        pytest.fail("no request expected")

    adapter, _handler = _adapter_with(callback)
    result = await adapter.push_project_requirements(PROJECT_ID, [], [])

    assert result.total == 0
    assert result.succeeded == 0
    assert result.failed == 0
    assert result.errors == []


@pytest.mark.asyncio
async def test_push_project_requirements_preserves_order() -> None:
    req = _requirement(title="Ordering")
    link = _trace_link(source_artifact_id=uuid.uuid4(), target_artifact_id=req.id)
    paths: list[str] = []

    def callback(request: httpx.Request) -> httpx.Response:
        paths.append(request.url.path)
        return httpx.Response(200, json={"id": f"{len(paths)}"})

    adapter, _handler = _adapter_with(callback)
    await adapter.push_project_requirements(PROJECT_ID, [req], [link])

    assert paths == ["/api/stories", f"/api/stories/{req.id}/tags"]


@pytest.mark.asyncio
async def test_push_project_requirements_error_messages_include_context() -> None:
    req = _requirement(title="Contextual failure")

    def callback(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(404, json={"error": "missing"})

    adapter, _handler = _adapter_with(callback)
    result = await adapter.push_project_requirements(PROJECT_ID, [req], [])

    assert result.total == 1
    assert result.succeeded == 0
    assert result.failed == 1
    assert any("requirement" in err.lower() for err in result.errors)
    assert any("Contextual failure" in err for err in result.errors)


@pytest.mark.asyncio
async def test_push_trace_link_handles_missing_id_field() -> None:
    def callback(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"data": {"unexpected": True}})

    adapter, _handler = _adapter_with(callback)
    result = await adapter.push_trace_link(_trace_link())

    assert result.success is False
    assert result.agileplus_id is None
    assert result.error is not None


@pytest.mark.asyncio
async def test_push_requirement_handles_text_response() -> None:
    def callback(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, text='{"agileplus_id":"text-1"}', headers={"content-type": "application/json"})

    adapter, _handler = _adapter_with(callback)
    result = await adapter.push_requirement(_requirement())

    assert result.success is True
    assert result.agileplus_id == "text-1"
