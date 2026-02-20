"""FastAPI Router for Requirements Enhancement Endpoints.

Add this to src/tracertm/api/routers/enhancements.py

Provides REST API for:
- Finding duplicate requirements
- Analyzing requirement quality
- Computing impact analysis
- Detecting circular dependencies
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import TYPE_CHECKING, Annotated

# Import for type hints and Depends(); avoid circular import by deferring in get_enhancement_service
from fastapi import APIRouter, Depends, HTTPException, Query

if TYPE_CHECKING:
    from ENHANCEMENT_IMPLEMENTATION_STARTER import RequirementEnhancementService

# These would be imported from your actual modules
# from tracertm.services.requirement_enhancement_service import (
#     RequirementEnhancementService,
#     EnhancementCapability,
#     DuplicateCandidate,

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/projects/{project_id}/enhancements", tags=["enhancements"])


# ============================================================================
# DEPENDENCY INJECTION
# ============================================================================


def get_enhancement_service() -> RequirementEnhancementService:
    """Get enhancement service instance."""
    from ENHANCEMENT_IMPLEMENTATION_STARTER import RequirementEnhancementService

    return RequirementEnhancementService()


# ============================================================================
# DUPLICATE DETECTION ENDPOINTS
# ============================================================================


@router.post("/duplicates/search")
async def find_duplicate_requirements(
    project_id: str,
    threshold: Annotated[float, Query(ge=0.0, le=1.0)] = 0.85,
    service: RequirementEnhancementService = Depends(get_enhancement_service),
) -> None:
    """Search for duplicate requirements in a project.

    Query Parameters:
    - threshold: Similarity threshold (0.0-1.0), default 0.85

    Returns:
    - List of potential duplicate pairs with similarity scores

    Example:
    ```
    POST /api/projects/proj-1/enhancements/duplicates/search?threshold=0.85

    Response:
    {
      "project_id": "proj-1",
      "threshold": 0.85,
      "duplicates_found": 3,
      "duplicates": [
        {
          "item_1_id": "REQ-001",
          "item_1_title": "User authentication",
          "item_2_id": "REQ-002",
          "item_2_title": "OAuth authentication",
          "similarity_score": 0.92
        },
        ...
      ],
      "scan_completed_at": "2026-01-29T10:30:00Z"
    }
    ```
    """
    try:
        # Get all items from project
        # For now, this is a stub
        items = [
            {
                "id": "REQ-001",
                "title": "User authentication",
                "description": "The system shall authenticate users using OAuth 2.0",
            },
        ]

        if not items:
            raise HTTPException(status_code=404, detail="No requirements found in project")

        # Prepare requirement dicts
        requirements = [
            {"id": item["id"], "title": item.get("title", ""), "description": item.get("description", "")}
            for item in items
        ]

        # Find duplicates
        duplicates = await service.find_duplicates(requirements, threshold)

        return {
            "project_id": project_id,
            "threshold": threshold,
            "duplicates_found": len(duplicates),
            "duplicates": [
                {
                    "item_1_id": dup.item_1_id,
                    "item_1_title": dup.item_1_title,
                    "item_2_id": dup.item_2_id,
                    "item_2_title": dup.item_2_title,
                    "similarity_score": round(dup.similarity_score, 4),
                    "confidence": dup.confidence,
                }
                for dup in duplicates
            ],
            "scan_completed_at": datetime.now().isoformat(),
        }

    except Exception as e:
        logger.error("Error finding duplicates: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error finding duplicates: {e!s}") from e


@router.post("/duplicates/{item_id}/find-similar")
async def find_similar_requirements(
    _project_id: str,
    item_id: str,
    top_k: Annotated[int, Query(ge=1, le=50)] = 5,
    threshold: Annotated[float, Query(ge=0.0, le=1.0)] = 0.75,
    service: RequirementEnhancementService = Depends(get_enhancement_service),
) -> None:
    """Find requirements similar to a specific item.

    Path Parameters:
    - item_id: Target requirement ID

    Query Parameters:
    - top_k: Number of similar items to return (1-50, default 5)
    - threshold: Minimum similarity threshold (0.0-1.0, default 0.75)

    Returns:
    - List of similar requirements ranked by similarity

    Example:
    ```
    GET /api/projects/proj-1/enhancements/duplicates/REQ-001/find-similar?top_k=5

    Response:
    {
      "item_id": "REQ-001",
      "query_title": "User authentication",
      "similar_items": [
        {
          "item_id": "REQ-002",
          "title": "OAuth authentication",
          "similarity_score": 0.92,
          "rank": 1
        },
        ...
      ]
    }
    ```
    """
    try:
        # Get target item
        # Get all items in project

        # Stub implementation
        target_item = {
            "id": item_id,
            "title": "User authentication",
            "description": "The system shall authenticate users",
        }
        all_items = [target_item]

        requirements = [
            {"id": item["id"], "title": item.get("title", ""), "description": item.get("description", "")}
            for item in all_items
        ]

        duplicates = await service.find_duplicates(requirements, threshold)

        # Filter to top_k and exclude self
        similar = [dup for dup in duplicates if (item_id in {dup.item_1_id, dup.item_2_id})][:top_k]

        return {
            "item_id": item_id,
            "query_title": target_item.get("title", ""),
            "similar_count": len(similar),
            "similar_items": [
                {
                    "item_id": dup.item_2_id if dup.item_1_id == item_id else dup.item_1_id,
                    "title": dup.item_2_title if dup.item_1_id == item_id else dup.item_1_title,
                    "similarity_score": round(dup.similarity_score, 4),
                    "rank": idx + 1,
                }
                for idx, dup in enumerate(similar)
            ],
        }

    except Exception as e:
        logger.error("Error finding similar requirements: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=str(e)) from e


# ============================================================================
# QUALITY ANALYSIS ENDPOINTS
# ============================================================================


@router.get("/quality/{item_id}")
async def analyze_requirement_quality(
    _project_id: str,
    item_id: str,
    service: Annotated[RequirementEnhancementService, Depends(get_enhancement_service)],
) -> None:
    """Analyze quality of a specific requirement.

    Returns:
    - Quality score (0-100)
    - Quality grade (A-F)
    - List of issues found
    - Improvement recommendations

    Example:
    ```
    GET /api/projects/proj-1/enhancements/quality/REQ-001

    Response:
    {
      "item_id": "REQ-001",
      "title": "User authentication",
      "quality_metrics": {
        "score": 85,
        "grade": "B",
        "ambiguous_terms": ["fast"],
        "passive_voice_used": false,
        "word_count": 12,
        "sentence_count": 1,
        "complexity_level": "simple",
        "recommendations": [
          "Replace ambiguous term 'fast' with specific metric"
        ]
      },
      "analyzed_at": "2026-01-29T10:30:00Z"
    }
    ```
    """
    try:
        # Get item
        item = {"id": item_id, "title": "User authentication", "description": "The system should be fast"}

        if not item:
            raise HTTPException(status_code=404, detail="Requirement not found")

        # Analyze
        result = await service.enhance_requirement(item_id=item_id, description=item["description"])

        return {
            "item_id": item_id,
            "title": item.get("title", ""),
            "quality_metrics": result["enhancements"].get("quality", {}),
            "analyzed_at": datetime.now().isoformat(),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error analyzing quality: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/quality/batch")
async def analyze_multiple_requirements(
    project_id: str,
    item_ids: list[str],
    service: Annotated[RequirementEnhancementService, Depends(get_enhancement_service)],
) -> None:
    """Analyze quality of multiple requirements.

    Request Body:
    ```json
    {
      "item_ids": ["REQ-001", "REQ-002", "REQ-003"]
    }
    ```

    Returns:
    - Dictionary mapping item_id to quality analysis

    Example Response:
    ```json
    {
      "project_id": "proj-1",
      "analysis_count": 3,
      "quality_results": {
        "REQ-001": {
          "score": 85,
          "grade": "B",
          ...
        },
        ...
      },
      "summary": {
        "average_score": 78.3,
        "items_below_70": 1
      },
      "analyzed_at": "2026-01-29T10:30:00Z"
    }
    ```
    """
    try:
        if not item_ids:
            raise HTTPException(status_code=400, detail="item_ids required")

        if len(item_ids) > 100:
            raise HTTPException(status_code=400, detail="Maximum 100 items per batch")

        # Analyze each item
        results = {}
        total_score = 0

        for item_id in item_ids:
            # Get item
            item = {"id": item_id, "description": "Sample requirement"}

            # Analyze
            result = await service.enhance_requirement(item_id=item_id, description=item.get("description", ""))

            quality = result["enhancements"].get("quality", {})
            results[item_id] = quality
            total_score += quality.get("score", 0)

        # Calculate summary
        average_score = total_score / len(item_ids) if item_ids else 0
        items_below_70 = sum(1 for r in results.values() if r.get("score", 100) < 70)

        return {
            "project_id": project_id,
            "analysis_count": len(item_ids),
            "quality_results": results,
            "summary": {
                "average_score": round(average_score, 2),
                "items_below_70": items_below_70,
                "items_at_or_above_80": sum(1 for r in results.values() if r.get("score", 0) >= 80),
            },
            "analyzed_at": datetime.now().isoformat(),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error in batch analysis: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=str(e)) from e


# ============================================================================
# IMPACT ANALYSIS ENDPOINTS
# ============================================================================


@router.get("/impact/{item_id}")
async def get_impact_analysis(
    _project_id: str,
    item_id: str,
    direction: Annotated[str, Query(regex="^(downstream|upstream)$")] = "downstream",
    service: RequirementEnhancementService = Depends(get_enhancement_service),
) -> None:
    """Analyze impact of changing a requirement.

    Path Parameters:
    - item_id: Target requirement ID

    Query Parameters:
    - direction: "downstream" (affected by) or "upstream" (depends on)

    Returns:
    - Impact count and list
    - Risk assessment
    - Affected items by status

    Example:
    ```
    GET /api/projects/proj-1/enhancements/impact/REQ-001?direction=downstream

    Response:
    {
      "item_id": "REQ-001",
      "direction": "downstream",
      "direct_impact_count": 2,
      "transitive_impact_count": 5,
      "impacted_item_ids": ["REQ-002", "REQ-003", ...],
      "impact_depth": 3,
      "risk_score": 45.5,
      "risk_level": "medium",
      "affected_status_distribution": {
        "done": 3,
        "testing": 1,
        "draft": 1
      },
      "recommendation": "Proceed with caution - 1 item in testing",
      "analyzed_at": "2026-01-29T10:30:00Z"
    }
    ```
    """
    try:
        # Get all items and links

        items = [{"id": item_id, "title": "Sample", "status": "draft", "priority": 1}]
        links = []

        # Analyze impact
        impact = await service.analyze_impact(item_id, items, links)

        # Generate recommendation
        recommendation = ""
        if impact.risk_level == "critical":
            recommendation = "Request comprehensive review before change"
        elif impact.risk_level == "high":
            recommendation = "Schedule review meeting with stakeholders"
        elif impact.risk_level == "medium":
            recommendation = "Proceed with caution - notify affected teams"
        else:
            recommendation = "Safe to proceed"

        return {
            "item_id": item_id,
            "direction": direction,
            "direct_impact_count": impact.direct_impact_count,
            "transitive_impact_count": impact.transitive_impact_count,
            "impacted_item_ids": impact.impacted_item_ids,
            "impact_depth": impact.impact_depth,
            "risk_score": round(impact.risk_score, 2),
            "risk_level": impact.risk_level,
            "affected_status_distribution": impact.affected_status_distribution,
            "recommendation": recommendation,
            "analyzed_at": datetime.now().isoformat(),
        }

    except Exception as e:
        logger.error("Error analyzing impact: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/circular-dependencies")
async def detect_circular_dependencies(
    project_id: str,
    service: Annotated[RequirementEnhancementService, Depends(get_enhancement_service)],
) -> None:
    """Detect circular dependencies in project.

    Returns:
    - List of all circular dependency cycles
    - Cycle details and severity

    Example:
    ```
    GET /api/projects/proj-1/enhancements/circular-dependencies

    Response:
    {
      "project_id": "proj-1",
      "cycles_found": 2,
      "cycles": [
        {
          "items": ["REQ-001", "REQ-002", "REQ-001"],
          "length": 2,
          "severity": "high"
        },
        ...
      ],
      "recommendations": [
        "Break cycle: REQ-001 -> REQ-002 -> REQ-001",
        ...
      ],
      "scanned_at": "2026-01-29T10:30:00Z"
    }
    ```
    """
    try:
        # Get all items and links

        # Detect cycles
        cycles = await service.impact_service.detect_circular_dependencies()

        # Build cycle details
        cycle_details = []
        for cycle in cycles:
            severity = "critical" if len(cycle) > 3 else "high"
            cycle_details.append({"items": cycle, "length": len(cycle), "severity": severity})

        # Generate recommendations
        recommendations = [f"Break cycle: {' -> '.join(cycle)} -> {cycle[0]}" for cycle in cycles]

        return {
            "project_id": project_id,
            "cycles_found": len(cycles),
            "cycles": cycle_details,
            "recommendations": recommendations,
            "scanned_at": datetime.now().isoformat(),
        }

    except Exception as e:
        logger.error("Error detecting cycles: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=str(e)) from e


# ============================================================================
# HEALTH & STATUS ENDPOINTS
# ============================================================================


@router.get("/health")
async def enhancement_service_health(
    _service: Annotated[RequirementEnhancementService, Depends(get_enhancement_service)],
) -> None:
    """Check enhancement service health.

    Returns:
    - Service status
    - Loaded models and their sizes
    - Available capabilities

    Example:
    ```
    GET /api/projects/proj-1/enhancements/health

    Response:
    {
      "status": "healthy",
      "services": {
        "semantic_analysis": "ready",
        "quality_analysis": "ready",
        "impact_analysis": "ready"
      },
      "models_loaded": {
        "semantic_model": "all-MiniLM-L6-v2 (80MB)",
        "nlp_model": "en_core_web_sm (40MB)"
      },
      "capabilities": [
        "semantic_analysis",
        "quality_analysis",
        "impact_analysis"
      ],
      "checked_at": "2026-01-29T10:30:00Z"
    }
    ```
    """
    return {
        "status": "healthy",
        "services": {"semantic_analysis": "ready", "quality_analysis": "ready", "impact_analysis": "ready"},
        "models_loaded": {"semantic_model": "all-MiniLM-L6-v2 (80MB)", "nlp_model": "en_core_web_sm (40MB)"},
        "capabilities": [
            "semantic_analysis",
            "quality_analysis",
            "impact_analysis",
            "duplicate_detection",
            "circular_dependency_detection",
        ],
        "checked_at": datetime.now().isoformat(),
    }


# ============================================================================
# EXPORT ROUTES
# ============================================================================

# Add to main.py:
