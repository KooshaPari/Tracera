"""Specification tools for MCP.

Functional Requirements: FR-MCP-002, FR-DISC-003
"""

from fastmcp.exceptions import ToolError

from tracertm.api.http_client import TraceRTMHttpClient, TraceRTMHttpError
from tracertm.mcp.api_client import get_api_client
from tracertm.mcp.core import mcp


def _api_client() -> TraceRTMHttpClient:
    return get_api_client()


# =============================================================================
# ADR Tools
# =============================================================================


@mcp.tool(description="Create a new Architecture Decision Record (ADR)")
def create_adr(
    project_id: str,
    title: str,
    context: str,
    decision: str,
    consequences: str,
    status: str = "proposed",
    decision_drivers: list[str] | None = None,
    tags: list[str] | None = None,
) -> dict[str, object]:
    """Create adr."""
    decision_drivers = decision_drivers if decision_drivers is not None else []
    tags = tags if tags is not None else []
    client = _api_client()
    try:
        adr = client.post(
            "/api/v1/adrs",
            json={
                "project_id": project_id,
                "title": title,
                "context": context,
                "decision": decision,
                "consequences": consequences,
                "status": status,
                "decision_drivers": decision_drivers,
                "tags": tags,
            },
        )
    except TraceRTMHttpError as exc:
        raise ToolError(str(exc)) from exc

    return {
        "id": adr.get("id"),
        "adr_number": adr.get("adr_number"),
        "title": adr.get("title", title),
        "status": adr.get("status", status),
    }


@mcp.tool(description="List ADRs for a project")
def list_adrs(
    project_id: str,
    status: str | None = None,
) -> list[dict]:
    """List adrs."""
    client = _api_client()
    try:
        adrs = client.get(
            "/api/v1/adrs",
            params={"project_id": project_id, "status": status},
        )
    except TraceRTMHttpError as exc:
        raise ToolError(str(exc)) from exc

    return [
        {
            "id": a.get("id"),
            "adr_number": a.get("adr_number"),
            "title": a.get("title"),
            "status": a.get("status"),
            "date": a.get("date"),
        }
        for a in adrs
    ]


# =============================================================================
# Contract Tools
# =============================================================================


@mcp.tool(description="Create a new Contract (Design by Contract)")
def create_contract(
    project_id: str,
    item_id: str,
    title: str,
    contract_type: str,
    status: str = "draft",
) -> dict[str, object]:
    """Create contract."""
    client = _api_client()
    try:
        contract = client.post(
            "/api/v1/contracts",
            json={
                "project_id": project_id,
                "item_id": item_id,
                "title": title,
                "contract_type": contract_type,
                "status": status,
            },
        )
    except TraceRTMHttpError as exc:
        raise ToolError(str(exc)) from exc

    return {
        "id": contract.get("id"),
        "contract_number": contract.get("contract_number"),
        "title": contract.get("title", title),
    }


# =============================================================================
# Feature & Scenario Tools
# =============================================================================


@mcp.tool(description="Create a new BDD Feature")
def create_feature(
    project_id: str,
    name: str,
    description: str | None = None,
    as_a: str | None = None,
    i_want: str | None = None,
    so_that: str | None = None,
) -> dict[str, object]:
    """Create feature."""
    client = _api_client()
    try:
        feature = client.post(
            "/api/v1/features",
            json={
                "project_id": project_id,
                "name": name,
                "description": description,
                "as_a": as_a,
                "i_want": i_want,
                "so_that": so_that,
            },
        )
    except TraceRTMHttpError as exc:
        raise ToolError(str(exc)) from exc

    return {
        "id": feature.get("id"),
        "feature_number": feature.get("feature_number"),
        "name": feature.get("name", name),
    }


@mcp.tool(description="Create a new BDD Scenario for a Feature")
def create_scenario(
    feature_id: str,
    title: str,
    gherkin_text: str,
) -> dict[str, object]:
    """Create scenario."""
    client = _api_client()
    try:
        scenario = client.post(
            f"/api/v1/features/{feature_id}/scenarios",
            json={"title": title, "gherkin_text": gherkin_text},
        )
    except TraceRTMHttpError as exc:
        raise ToolError(str(exc)) from exc

    return {
        "id": scenario.get("id"),
        "scenario_number": scenario.get("scenario_number"),
        "title": scenario.get("title", title),
    }


# =============================================================================
# Quality Tools
# =============================================================================


@mcp.tool(description="Analyze requirements quality (smells, ambiguity)")
def analyze_quality(
    item_id: str,
) -> dict[str, object]:
    """Analyze quality."""
    client = _api_client()
    try:
        quality = client.post(f"/api/v1/quality/items/{item_id}/analyze")
    except TraceRTMHttpError as exc:
        raise ToolError(str(exc)) from exc

    return {
        "id": quality.get("id"),
        "item_id": quality.get("item_id", item_id),
        "smells": quality.get("smells"),
        "ambiguity_score": quality.get("ambiguity_score"),
        "completeness_score": quality.get("completeness_score"),
        "suggestions": quality.get("suggestions"),
    }
