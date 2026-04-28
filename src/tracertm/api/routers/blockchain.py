"""API Router for blockchain-style features: baselines, version chains, and embeddings.

Provides REST endpoints for:
- Baseline management (create, list, delete, verify)
- Embedding generation and similarity search
- Version chain management
"""

from datetime import datetime
from typing import Annotated, Any

from fastapi import APIRouter, Body, Depends, HTTPException, Path, Query
from pydantic import BaseModel, Field
from sqlalchemy import Integer
from sqlalchemy.ext.asyncio import AsyncSession

from tracertm.api.deps import auth_guard, get_db
from tracertm.repositories import (
    BaselineRepository,
    SpecEmbeddingRepository,
    VersionBlockRepository,
)

router = APIRouter(prefix="/blockchain", tags=["blockchain"])

# Create repository singletons
version_block_repo = VersionBlockRepository()
baseline_repo = BaselineRepository()
embedding_repo = SpecEmbeddingRepository()


# =============================================================================
# Request/Response Models
# =============================================================================


class CreateBaselineRequest(BaseModel):
    """Request to create a new baseline."""

    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    baseline_type: str = Field(default="snapshot", pattern="^(snapshot|release|freeze|audit)$")
    spec_type: str | None = Field(default=None, description="Filter by spec type, or null for all")
    items: list[dict[str, str]] = Field(
        ...,
        description="List of items: [{item_id, item_type, content_hash}]",
        min_length=1,
    )


class BaselineResponse(BaseModel):
    """Response for a baseline."""

    id: str
    baseline_id: str
    project_id: str
    spec_type: str | None
    merkle_root: str
    items_count: int
    baseline_type: str
    name: str | None
    description: str | None
    tags: list[str]
    created_by: str | None
    created_at: datetime
    expires_at: datetime | None

    model_config = {"from_attributes": True}


class BaselineListResponse(BaseModel):
    """Response for baseline list."""

    baselines: list[BaselineResponse]
    total: int


class BaselineItemResponse(BaseModel):
    """Response for a baseline item."""

    item_id: str
    item_type: str
    content_hash: str
    leaf_hash: str
    leaf_index: int
    version_at_baseline: int | None


class BaselineDetailResponse(BaseModel):
    """Detailed baseline response with items."""

    baseline: BaselineResponse
    items: list[BaselineItemResponse]


class GenerateEmbeddingsRequest(BaseModel):
    """Request to generate embeddings for specs."""

    spec_ids: list[str] = Field(..., min_length=1, max_length=100)
    spec_type: str = Field(..., pattern="^(requirements|tests|epics|stories|tasks|defects)$")
    model_name: str = Field(default="sentence-transformers/all-MiniLM-L6-v2")
    force_refresh: bool = Field(default=False, description="Regenerate even if exists")


class EmbeddingStatusResponse(BaseModel):
    """Response for embedding generation status."""

    total_requested: int
    generated: int
    skipped: int
    failed: int
    model_used: str
    details: list[dict[str, Any]]


class VersionChainStatsResponse(BaseModel):
    """Statistics for version chains in a project."""

    total_chains: int
    total_blocks: int
    valid_chains: int
    invalid_chains: int
    chains_by_type: dict[str, int]


# =============================================================================
# Baseline Endpoints
# =============================================================================


@router.post(
    "/projects/{project_id}/baselines",
    response_model=BaselineResponse,
    status_code=201,
)
async def create_baseline(
    project_id: Annotated[str, Path(description="Project ID")],
    request: Annotated[CreateBaselineRequest, Body()],
    claims: Annotated[dict[str, Any], Depends(auth_guard)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, Any]:
    """Create a new baseline snapshot.

    Creates a Merkle tree from the provided items and stores
    the baseline with pre-computed proofs for each item.

    Args:
        project_id: The project identifier
        request: Baseline creation parameters
        claims: Authentication claims from JWT
        db: Database session

    Returns:
        BaselineResponse: Created baseline details
    """
    try:
        user_id = claims.get("sub") or claims.get("user_id")

        # Convert items to tuple format
        items_tuples = [(item["item_id"], item["item_type"], item["content_hash"]) for item in request.items]

        baseline = await baseline_repo.create_baseline(
            db=db,
            project_id=project_id,
            baseline_type=request.baseline_type,
            name=request.name,
            items=items_tuples,
            created_by=user_id,
            description=request.description,
            spec_type=request.spec_type,
        )

        await db.commit()

        return BaselineResponse(
            id=str(baseline.id),
            baseline_id=baseline.baseline_id,
            project_id=baseline.project_id,
            spec_type=baseline.spec_type,
            merkle_root=baseline.merkle_root,
            items_count=baseline.items_count,
            baseline_type=baseline.baseline_type,
            name=baseline.name,
            description=baseline.description,
            tags=baseline.tags or [],
            created_by=baseline.created_by,
            created_at=baseline.created_at,
            expires_at=baseline.expires_at,
        )
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get(
    "/projects/{project_id}/baselines",
    response_model=BaselineListResponse,
)
async def list_baselines(
    project_id: Annotated[str, Path(description="Project ID")],
    baseline_type: Annotated[str | None, Query(description="Filter by type")] = None,
    spec_type: Annotated[str | None, Query(description="Filter by spec type")] = None,
    limit: Annotated[int, Query(ge=1, le=200)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
    _claims: dict[str, Any] = Depends(auth_guard),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """List baselines for a project.

    Args:
        project_id: The project identifier
        baseline_type: Optional filter by baseline type
        spec_type: Optional filter by spec type
        limit: Maximum results to return
        offset: Pagination offset
        claims: Authentication claims from JWT
        db: Database session

    Returns:
        BaselineListResponse: List of baselines
    """
    try:
        from sqlalchemy import func, select

        from tracertm.models.blockchain import Baseline

        # Build query
        query = select(Baseline).where(Baseline.project_id == project_id)

        if baseline_type:
            query = query.where(Baseline.baseline_type == baseline_type)
        if spec_type:
            query = query.where(Baseline.spec_type == spec_type)

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0

        # Get paginated results
        query = query.order_by(Baseline.created_at.desc()).offset(offset).limit(limit)
        result = await db.execute(query)
        baselines = list(result.scalars().all())

        return BaselineListResponse(
            baselines=[
                BaselineResponse(
                    id=str(b.id),
                    baseline_id=b.baseline_id,
                    project_id=b.project_id,
                    spec_type=b.spec_type,
                    merkle_root=b.merkle_root,
                    items_count=b.items_count,
                    baseline_type=b.baseline_type,
                    name=b.name,
                    description=b.description,
                    tags=b.tags or [],
                    created_by=b.created_by,
                    created_at=b.created_at,
                    expires_at=b.expires_at,
                )
                for b in baselines
            ],
            total=total,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get(
    "/projects/{project_id}/baselines/{baseline_id}",
    response_model=BaselineDetailResponse,
)
async def get_baseline(
    project_id: Annotated[str, Path(description="Project ID")],
    baseline_id: Annotated[str, Path(description="Baseline ID")],
    _claims: Annotated[dict[str, Any], Depends(auth_guard)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, Any]:
    """Get baseline details with items.

    Args:
        project_id: The project identifier
        baseline_id: The baseline identifier
        claims: Authentication claims from JWT
        db: Database session

    Returns:
        BaselineDetailResponse: Baseline with all items
    """
    try:
        from sqlalchemy import select
        from sqlalchemy.orm import selectinload

        from tracertm.models.blockchain import Baseline

        result = await db.execute(
            select(Baseline)
            .options(selectinload(Baseline.items))
            .where(Baseline.baseline_id == baseline_id)
            .where(Baseline.project_id == project_id),
        )
        baseline = result.scalar_one_or_none()

        if not baseline:
            raise HTTPException(status_code=404, detail=f"Baseline {baseline_id} not found")

        return BaselineDetailResponse(
            baseline=BaselineResponse(
                id=str(baseline.id),
                baseline_id=baseline.baseline_id,
                project_id=baseline.project_id,
                spec_type=baseline.spec_type,
                merkle_root=baseline.merkle_root,
                items_count=baseline.items_count,
                baseline_type=baseline.baseline_type,
                name=baseline.name,
                description=baseline.description,
                tags=baseline.tags or [],
                created_by=baseline.created_by,
                created_at=baseline.created_at,
                expires_at=baseline.expires_at,
            ),
            items=[
                BaselineItemResponse(
                    item_id=item.item_id,
                    item_type=item.item_type,
                    content_hash=item.content_hash,
                    leaf_hash=item.leaf_hash,
                    leaf_index=item.leaf_index,
                    version_at_baseline=item.version_at_baseline,
                )
                for item in sorted(baseline.items, key=lambda x: x.leaf_index)
            ],
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.delete(
    "/projects/{project_id}/baselines/{baseline_id}",
    status_code=204,
)
async def delete_baseline(
    project_id: Annotated[str, Path(description="Project ID")],
    baseline_id: Annotated[str, Path(description="Baseline ID")],
    _claims: Annotated[dict[str, Any], Depends(auth_guard)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    """Delete a baseline.

    Args:
        project_id: The project identifier
        baseline_id: The baseline identifier
        claims: Authentication claims from JWT
        db: Database session
    """
    try:
        from sqlalchemy import delete, select

        from tracertm.models.blockchain import Baseline

        # Verify exists
        result = await db.execute(
            select(Baseline).where(Baseline.baseline_id == baseline_id).where(Baseline.project_id == project_id),
        )
        baseline = result.scalar_one_or_none()

        if not baseline:
            raise HTTPException(status_code=404, detail=f"Baseline {baseline_id} not found")

        # Delete (cascade will handle items and proofs)
        await db.execute(delete(Baseline).where(Baseline.id == baseline.id))
        await db.commit()

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e)) from e


# =============================================================================
# Embedding Endpoints
# =============================================================================


@router.post(
    "/projects/{project_id}/embeddings/generate",
    response_model=EmbeddingStatusResponse,
)
async def generate_embeddings(
    project_id: Annotated[str, Path(description="Project ID")],
    request: Annotated[GenerateEmbeddingsRequest, Body()],
    _claims: Annotated[dict[str, Any], Depends(auth_guard)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, Any]:
    """Generate embeddings for specifications.

    Uses sentence-transformers to generate vector embeddings
    for semantic similarity search.

    Args:
        project_id: The project identifier
        request: Embedding generation parameters
        claims: Authentication claims from JWT
        db: Database session

    Returns:
        EmbeddingStatusResponse: Generation results
    """
    try:
        generated = 0
        skipped = 0
        failed = 0
        details = []

        # Check if sentence-transformers is available (optional deps)
        try:
            import numpy as np
            from sentence_transformers import SentenceTransformer

            model = SentenceTransformer(request.model_name)
        except ImportError:
            raise HTTPException(
                status_code=501,
                detail="sentence-transformers not installed. Install with: pip install 'tracertm[ml]'",
            ) from None

        for spec_id in request.spec_ids:
            try:
                # Check if embedding already exists
                existing = await embedding_repo.get_embedding(db, spec_id, request.spec_type, request.model_name)

                if existing and not request.force_refresh:
                    skipped += 1
                    details.append({
                        "spec_id": spec_id,
                        "status": "skipped",
                        "reason": "embedding exists",
                    })
                    continue

                # For now, use spec_id as placeholder text
                # In real implementation, fetch spec content from DB
                text = f"{request.spec_type}:{spec_id}"

                # Generate embedding
                embedding_vec = model.encode(text, convert_to_numpy=True)
                embedding_bytes = embedding_vec.astype(np.float32).tobytes()
                content_hash = version_block_repo.compute_content_hash({"text": text})

                # Store embedding
                await embedding_repo.store_embedding(
                    db=db,
                    spec_id=spec_id,
                    spec_type=request.spec_type,
                    project_id=project_id,
                    embedding=embedding_bytes,
                    embedding_dimension=len(embedding_vec),
                    embedding_model=request.model_name,
                    content_hash=content_hash,
                    source_text_length=len(text),
                )

                generated += 1
                details.append({
                    "spec_id": spec_id,
                    "status": "generated",
                    "dimension": str(len(embedding_vec)),
                })

            except Exception as e:
                failed += 1
                details.append({
                    "spec_id": spec_id,
                    "status": "failed",
                    "error": str(e),
                })

        await db.commit()

        return EmbeddingStatusResponse(
            total_requested=len(request.spec_ids),
            generated=generated,
            skipped=skipped,
            failed=failed,
            model_used=request.model_name,
            details=details,
        )

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get(
    "/projects/{project_id}/embeddings/stats",
    response_model=dict,
)
async def get_embedding_stats(
    project_id: Annotated[str, Path(description="Project ID")],
    _claims: Annotated[dict[str, Any], Depends(auth_guard)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, Any]:
    """Get embedding statistics for a project.

    Args:
        project_id: The project identifier
        claims: Authentication claims from JWT
        db: Database session

    Returns:
        Statistics about embeddings in the project
    """
    try:
        from sqlalchemy import func, select

        from tracertm.models.blockchain import SpecEmbedding

        # Count by spec type
        result = await db.execute(
            select(
                SpecEmbedding.spec_type,
                SpecEmbedding.embedding_model,
                func.count(SpecEmbedding.id).label("count"),
            )
            .where(SpecEmbedding.project_id == project_id)
            .group_by(SpecEmbedding.spec_type, SpecEmbedding.embedding_model),
        )
        rows = result.all()

        by_type: dict[str, int] = {}
        by_model: dict[str, int] = {}
        total = 0

        for row in rows:
            spec_type, model, count = row
            by_type[spec_type] = by_type.get(spec_type, 0) + count
            by_model[model] = by_model.get(model, 0) + count
            total += count
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
    else:
        return {
            "project_id": project_id,
            "total_embeddings": total,
            "by_spec_type": by_type,
            "by_model": by_model,
        }


@router.delete(
    "/projects/{project_id}/embeddings",
    status_code=204,
)
async def delete_embeddings(
    project_id: Annotated[str, Path(description="Project ID")],
    spec_type: Annotated[str | None, Query(description="Filter by spec type")] = None,
    model_name: Annotated[str | None, Query(description="Filter by model")] = None,
    _claims: dict[str, Any] = Depends(auth_guard),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete embeddings for a project.

    Args:
        project_id: The project identifier
        spec_type: Optional filter by spec type
        model_name: Optional filter by model
        claims: Authentication claims from JWT
        db: Database session
    """
    try:
        from sqlalchemy import and_, delete

        from tracertm.models.blockchain import SpecEmbedding

        conditions = [SpecEmbedding.project_id == project_id]

        if spec_type:
            conditions.append(SpecEmbedding.spec_type == spec_type)
        if model_name:
            conditions.append(SpecEmbedding.embedding_model == model_name)

        await db.execute(delete(SpecEmbedding).where(and_(*conditions)))
        await db.commit()

    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e)) from e


# =============================================================================
# Version Chain Stats Endpoint
# =============================================================================


@router.get(
    "/projects/{project_id}/version-chains/stats",
    response_model=VersionChainStatsResponse,
)
async def get_version_chain_stats(
    project_id: Annotated[str, Path(description="Project ID")],
    _claims: Annotated[dict[str, Any], Depends(auth_guard)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, Any]:
    """Get version chain statistics for a project.

    Args:
        project_id: The project identifier
        claims: Authentication claims from JWT
        db: Database session

    Returns:
        VersionChainStatsResponse: Chain statistics
    """
    try:
        from sqlalchemy import func, select

        from tracertm.models.blockchain import VersionBlock, VersionChainIndex

        # Count chains
        chains_result = await db.execute(
            select(
                func.count(VersionChainIndex.id).label("total"),
                func.sum(func.cast(VersionChainIndex.is_valid, Integer)).label("valid"),
            ).where(VersionChainIndex.project_id == project_id),
        )
        chains_row = chains_result.one()
        total_chains = chains_row.total or 0
        valid_chains = chains_row.valid or 0

        # Count blocks
        blocks_result = await db.execute(
            select(func.count(VersionBlock.id)).where(VersionBlock.project_id == project_id),
        )
        total_blocks = blocks_result.scalar() or 0

        # Count by spec type
        by_type_result = await db.execute(
            select(
                VersionChainIndex.spec_type,
                func.count(VersionChainIndex.id).label("count"),
            )
            .where(VersionChainIndex.project_id == project_id)
            .group_by(VersionChainIndex.spec_type),
        )
        chains_by_type: dict[str, int] = {row.spec_type: row.count for row in by_type_result.all()}

        return VersionChainStatsResponse(
            total_chains=total_chains,
            total_blocks=total_blocks,
            valid_chains=valid_chains,
            invalid_chains=total_chains - valid_chains,
            chains_by_type=chains_by_type,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
