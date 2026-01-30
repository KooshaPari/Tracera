"""
Specification tools for MCP.
"""

from typing import List, Optional
from fastmcp import Context

from tracertm.mcp.core import mcp
from tracertm.api.deps import get_db
from tracertm.services.adr_service import ADRService
from tracertm.services.contract_service import ContractService
from tracertm.services.feature_service import FeatureService
from tracertm.services.scenario_service import ScenarioService
from tracertm.services.requirement_quality_service import RequirementQualityService

# =============================================================================
# ADR Tools
# =============================================================================

@mcp.tool(description="Create a new Architecture Decision Record (ADR)")
async def create_adr(
    project_id: str,
    title: str,
    context: str,
    decision: str,
    consequences: str,
    status: str = "proposed",
    decision_drivers: List[str] = [],
    tags: List[str] = [],
) -> dict:
    async for session in get_db():
        service = ADRService(session)
        adr = await service.create_adr(
            project_id=project_id,
            title=title,
            context=context,
            decision=decision,
            consequences=consequences,
            status=status,
            decision_drivers=decision_drivers,
            tags=tags,
        )
        return {
            "id": adr.id,
            "adr_number": adr.adr_number,
            "title": adr.title,
            "status": adr.status
        }

@mcp.tool(description="List ADRs for a project")
async def list_adrs(
    project_id: str,
    status: Optional[str] = None,
) -> List[dict]:
    async for session in get_db():
        service = ADRService(session)
        adrs = await service.list_adrs(project_id, status)
        return [
            {
                "id": a.id,
                "adr_number": a.adr_number,
                "title": a.title,
                "status": a.status,
                "date": a.date.isoformat() if a.date else None
            }
            for a in adrs
        ]

# =============================================================================
# Contract Tools
# =============================================================================

@mcp.tool(description="Create a new Contract (Design by Contract)")
async def create_contract(
    project_id: str,
    item_id: str,
    title: str,
    contract_type: str,
    status: str = "draft",
) -> dict:
    async for session in get_db():
        service = ContractService(session)
        contract = await service.create_contract(
            project_id=project_id,
            item_id=item_id,
            title=title,
            contract_type=contract_type,
            status=status,
        )
        return {
            "id": contract.id,
            "contract_number": contract.contract_number,
            "title": contract.title
        }

# =============================================================================
# Feature & Scenario Tools
# =============================================================================

@mcp.tool(description="Create a new BDD Feature")
async def create_feature(
    project_id: str,
    name: str,
    description: str = None,
    as_a: str = None,
    i_want: str = None,
    so_that: str = None,
) -> dict:
    async for session in get_db():
        service = FeatureService(session)
        feature = await service.create_feature(
            project_id=project_id,
            name=name,
            description=description,
            as_a=as_a,
            i_want=i_want,
            so_that=so_that,
        )
        return {
            "id": feature.id,
            "feature_number": feature.feature_number,
            "name": feature.name
        }

@mcp.tool(description="Create a new BDD Scenario for a Feature")
async def create_scenario(
    feature_id: str,
    title: str,
    gherkin_text: str,
) -> dict:
    async for session in get_db():
        service = ScenarioService(session)
        scenario = await service.create_scenario(
            feature_id=feature_id,
            title=title,
            gherkin_text=gherkin_text,
        )
        return {
            "id": scenario.id,
            "scenario_number": scenario.scenario_number,
            "title": scenario.title
        }

# =============================================================================
# Quality Tools
# =============================================================================

@mcp.tool(description="Analyze requirements quality (smells, ambiguity)")
async def analyze_quality(
    item_id: str,
) -> dict:
    async for session in get_db():
        service = RequirementQualityService(session)
        quality = await service.analyze_quality(item_id)
        return {
            "id": quality.id,
            "item_id": quality.item_id,
            "smells": quality.smells,
            "ambiguity_score": quality.ambiguity_score,
            "completeness_score": quality.completeness_score,
            "suggestions": quality.suggestions,
        }
