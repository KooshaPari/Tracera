"""Specification management MCP tools."""

from __future__ import annotations

from typing import Any

from fastmcp.exceptions import ToolError

try:
    from tracertm.mcp.core import mcp
except ImportError:

    class _StubMCP:
        def tool(self, *_args: object, **_kwargs: object) -> object:
            def decorator(fn: object) -> object:
                return fn

            return decorator

    mcp: Any = _StubMCP()  # type: ignore[no-redef]

from .common import _call_tool, _maybe_select_project, _wrap

# Import spec tools with fallback
try:
    from tracertm.mcp.tools import specifications as spec_tools
except ImportError:

    class _SpecStub:
        async def create_adr(self, **_kwargs: object) -> None:
            msg = "Specification tools unavailable"
            raise ToolError(msg)

        async def list_adrs(self, **_kwargs: object) -> None:
            msg = "Specification tools unavailable"
            raise ToolError(msg)

        async def create_contract(self, **_kwargs: object) -> None:
            msg = "Specification tools unavailable"
            raise ToolError(msg)

        async def create_feature(self, **_kwargs: object) -> None:
            msg = "Specification tools unavailable"
            raise ToolError(msg)

        async def create_scenario(self, **_kwargs: object) -> None:
            msg = "Specification tools unavailable"
            raise ToolError(msg)

    spec_tools: object = _SpecStub()  # type: ignore[no-redef]


@mcp.tool(description="Unified specification operations")
async def specification_manage(
    kind: str,
    action: str,
    payload: dict[str, object] | None = None,
    ctx: object | None = None,
) -> dict[str, object]:
    """Unified specification management tool.

    Specification kinds and actions:
    - adr.create: Create Architecture Decision Record (requires: project_id, title, context, decision, consequences; optional: status, decision_drivers, tags)
    - adr.list: List ADRs (requires: project_id; optional: status)
    - contract.create: Create contract (requires: project_id, item_id, title, contract_type; optional: status)
    - feature.create: Create feature (requires: project_id, name, description, as_a, i_want, so_that)
    - scenario.create: Create scenario (requires: feature_id, title, gherkin_text)
    """
    payload = payload or {}
    kind = kind.lower()
    action = action.lower()

    await _maybe_select_project(payload, ctx)

    if kind == "adr":
        if action == "create":
            result = await _call_tool(
                spec_tools,
                "create_adr",
                project_id=payload.get("project_id"),
                title=payload.get("title"),
                context=payload.get("context"),
                decision=payload.get("decision"),
                consequences=payload.get("consequences"),
                status=payload.get("status", "proposed"),
                decision_drivers=payload.get("decision_drivers", []),
                tags=payload.get("tags", []),
            )
            return _wrap(result, ctx, f"{kind}.{action}")
        if action == "list":
            result = await _call_tool(
                spec_tools,
                "list_adrs",
                project_id=payload.get("project_id"),
                status=payload.get("status"),
            )
            return _wrap(result, ctx, f"{kind}.{action}")

    if kind == "contract" and action == "create":
        result = await _call_tool(
            spec_tools,
            "create_contract",
            project_id=payload.get("project_id"),
            item_id=payload.get("item_id"),
            title=payload.get("title"),
            contract_type=payload.get("contract_type"),
            status=payload.get("status", "draft"),
        )
        return _wrap(result, ctx, f"{kind}.{action}")

    if kind == "feature" and action == "create":
        result = await _call_tool(
            spec_tools,
            "create_feature",
            project_id=payload.get("project_id"),
            name=(payload.get("name") or ""),
            description=payload.get("description"),
            as_a=payload.get("as_a"),
            i_want=payload.get("i_want"),
            so_that=payload.get("so_that"),
        )
        return _wrap(result, ctx, f"{kind}.{action}")

    if kind == "scenario" and action == "create":
        result = await _call_tool(
            spec_tools,
            "create_scenario",
            feature_id=payload.get("feature_id"),
            title=payload.get("title"),
            gherkin_text=payload.get("gherkin_text"),
        )
        return _wrap(result, ctx, f"{kind}.{action}")

    msg = f"Unknown spec action: {kind}.{action}"
    raise ToolError(msg)
