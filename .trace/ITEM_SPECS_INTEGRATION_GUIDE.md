# Item Specs API - Integration Guide

## Overview

This guide walks through integrating the new Item Specifications API router into the existing TraceRTM backend.

## File Locations

| Component | Location |
|-----------|----------|
| **Router** | `src/tracertm/api/routers/item_specs.py` (2,122 lines) |
| **Schemas** | `src/tracertm/schemas/item_spec.py` (to create) |
| **Models** | `src/tracertm/models/item_spec*.py` (to create) |
| **Services** | `src/tracertm/services/item_spec_*.py` (to create) |
| **Repositories** | `src/tracertm/repositories/item_spec_*.py` (to create) |
| **Migrations** | `alembic/versions/XXX_add_item_specs.py` (to create) |

## Step 1: Register Router in Main API

### File: `src/tracertm/api/main.py`

Add the import at the top with other router imports:

```python
from tracertm.api.routers import (
    adrs,
    quality,
    features,
    contracts,
    specifications,
    item_specs,  # Add this line
)
```

Include the router in the app setup:

```python
app.include_router(adrs.router)
app.include_router(quality.router)
app.include_router(features.router)
app.include_router(contracts.router)
app.include_router(specifications.router)
app.include_router(item_specs.router)  # Add this line
```

This makes all endpoints available at `/item-specs/` prefix.

## Step 2: Create Database Models

### File: `src/tracertm/models/item_spec.py`

Create models for the database schema:

```python
"""Database models for item specifications."""

from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, Text, Float, Boolean, JSON
from sqlalchemy.orm import Mapped, mapped_column
from tracertm.models.base import Base, TimestampMixin
from tracertm.models.types import JSONType

class RequirementSpec(Base, TimestampMixin):
    """Requirement specification model."""

    __tablename__ = "requirement_specs"
    __table_args__ = (
        Index("idx_requirement_specs_item_id", "item_id"),
        Index("idx_requirement_specs_project_id", "project_id"),
        Index("idx_requirement_specs_risk_level", "risk_level"),
        Index("idx_requirement_specs_verification_status", "verification_status"),
    )

    id: Mapped[str] = mapped_column(String(255), primary_key=True)
    item_id: Mapped[str] = mapped_column(String(255), ForeignKey("items.id"), nullable=False)
    project_id: Mapped[str] = mapped_column(String(255), ForeignKey("projects.id"), nullable=False)

    requirement_type: Mapped[str] = mapped_column(String(50), nullable=False)  # functional, non_functional, constraint
    risk_level: Mapped[str] = mapped_column(String(50), nullable=False)  # low, medium, high, critical
    verification_status: Mapped[str] = mapped_column(String(50), nullable=False, default="unverified")

    quality_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    impact_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    traceability_index: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    acceptance_criteria: Mapped[str] = mapped_column(Text, nullable=False)
    verification_evidence: Mapped[list] = mapped_column(JSONType, nullable=False, default=list)

    metadata: Mapped[dict] = mapped_column(JSONType, nullable=False, default=dict)

    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class TestSpec(Base, TimestampMixin):
    """Test specification model."""

    __tablename__ = "test_specs"
    __table_args__ = (
        Index("idx_test_specs_item_id", "item_id"),
        Index("idx_test_specs_project_id", "project_id"),
        Index("idx_test_specs_test_type", "test_type"),
        Index("idx_test_specs_is_quarantined", "is_quarantined"),
    )

    id: Mapped[str] = mapped_column(String(255), primary_key=True)
    item_id: Mapped[str] = mapped_column(String(255), ForeignKey("items.id"), nullable=False)
    project_id: Mapped[str] = mapped_column(String(255), ForeignKey("projects.id"), nullable=False)

    test_type: Mapped[str] = mapped_column(String(50), nullable=False)  # unit, integration, e2e, performance, security
    coverage_percentage: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    pass_rate: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    flakiness_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    is_quarantined: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    quarantine_reason: Mapped[str | None] = mapped_column(String(255), nullable=True)

    last_run: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    average_duration_ms: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    total_runs: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    metadata: Mapped[dict] = mapped_column(JSONType, nullable=False, default=dict)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


# Similar models for EpicSpec, UserStorySpec, TaskSpec, DefectSpec
# Each following the same pattern with appropriate fields
```

## Step 3: Create Pydantic Schemas

### File: `src/tracertm/schemas/item_spec.py`

```python
"""Pydantic schemas for item specifications."""

from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel, Field, ConfigDict


class RequirementSpecCreate(BaseModel):
    """Schema for creating requirement spec."""

    item_id: str = Field(..., min_length=1)
    requirement_type: str = Field(..., pattern="^(functional|non_functional|constraint)$")
    risk_level: str = Field(..., pattern="^(low|medium|high|critical)$")
    acceptance_criteria: str = Field(..., min_length=1)
    metadata: Optional[dict[str, Any]] = None

    model_config = ConfigDict(protected_namespaces=())


class RequirementSpecResponse(BaseModel):
    """Schema for requirement spec response."""

    id: str
    item_id: str
    project_id: str
    requirement_type: str
    risk_level: str
    verification_status: str
    quality_score: float
    impact_score: Optional[float] = None
    traceability_index: float
    acceptance_criteria: str
    verification_evidence: Optional[list[dict[str, Any]]] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True, protected_namespaces=())


# Similar schemas for all other spec types
# Follow the Create, Update, Response pattern
```

## Step 4: Create Service Layer

### File: `src/tracertm/services/item_spec_service.py`

```python
"""Services for item specifications."""

from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from tracertm.models.item_spec import RequirementSpec
from tracertm.repositories.item_spec import RequirementSpecRepository


class RequirementSpecService:
    """Service for requirement specifications."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = RequirementSpecRepository(db)

    async def create_spec(
        self,
        item_id: str,
        requirement_type: str,
        risk_level: str,
        acceptance_criteria: str,
        **kwargs
    ) -> RequirementSpec:
        """Create a new requirement specification."""
        data = {
            "item_id": item_id,
            "requirement_type": requirement_type,
            "risk_level": risk_level,
            "acceptance_criteria": acceptance_criteria,
            **kwargs
        }
        return await self.repo.create(data)

    async def analyze_quality(self, spec_id: str) -> RequirementSpec:
        """Analyze quality of a requirement."""
        spec = await self.repo.get_by_id(spec_id)
        if not spec:
            raise ValueError("Requirement spec not found")

        # TODO: Implement quality analysis logic
        # - Check clarity and completeness
        # - Verify traceability
        # - Validate acceptance criteria

        quality_score = self._calculate_quality_score(spec)
        return await self.repo.update(spec_id, quality_score=quality_score)

    async def analyze_impact(self, spec_id: str) -> RequirementSpec:
        """Analyze impact of a requirement."""
        spec = await self.repo.get_by_id(spec_id)
        if not spec:
            raise ValueError("Requirement spec not found")

        # TODO: Implement impact analysis logic
        # - Identify affected components
        # - Analyze dependency chain
        # - Calculate risk propagation

        impact_score = self._calculate_impact_score(spec)
        return await self.repo.update(spec_id, impact_score=impact_score)

    async def verify_requirement(
        self,
        spec_id: str,
        user_id: str,
        evidence_type: str,
        evidence_reference: str,
        description: str
    ) -> RequirementSpec:
        """Record verification for a requirement."""
        spec = await self.repo.get_by_id(spec_id)
        if not spec:
            raise ValueError("Requirement spec not found")

        # Add evidence
        evidence = {
            "type": evidence_type,
            "reference": evidence_reference,
            "description": description,
            "verified_by": user_id,
            "verified_at": datetime.utcnow().isoformat()
        }

        verification_evidence = spec.verification_evidence or []
        verification_evidence.append(evidence)

        return await self.repo.update(
            spec_id,
            verification_status="verified",
            verification_evidence=verification_evidence
        )

    def _calculate_quality_score(self, spec: RequirementSpec) -> float:
        """Calculate quality score for a requirement."""
        # TODO: Implement scoring logic
        score = 0.0

        # Check acceptance criteria clarity
        if len(spec.acceptance_criteria) > 50:
            score += 25

        # Check for verification evidence
        if spec.verification_evidence:
            score += 25

        # Check traceability
        # score += calculate_traceability(spec)

        return min(score, 100.0)

    def _calculate_impact_score(self, spec: RequirementSpec) -> float:
        """Calculate impact score for a requirement."""
        # TODO: Implement impact scoring
        # Based on risk level and dependencies
        risk_multiplier = {"low": 0.2, "medium": 0.5, "high": 0.8, "critical": 1.0}
        return 50.0 * risk_multiplier.get(spec.risk_level, 0.5)


# Similar service classes for other spec types
class TestSpecService:
    """Service for test specifications."""
    # TODO: Implement similar pattern


class EpicSpecService:
    """Service for epic specifications."""
    # TODO: Implement similar pattern


class UserStorySpecService:
    """Service for user story specifications."""
    # TODO: Implement similar pattern


class TaskSpecService:
    """Service for task specifications."""
    # TODO: Implement similar pattern


class DefectSpecService:
    """Service for defect specifications."""
    # TODO: Implement similar pattern
```

## Step 5: Create Repository Layer

### File: `src/tracertm/repositories/item_spec.py`

```python
"""Repositories for item specifications."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from tracertm.models.item_spec import RequirementSpec, TestSpec


class RequirementSpecRepository:
    """Repository for requirement specifications."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, data: dict) -> RequirementSpec:
        """Create a new requirement spec."""
        spec = RequirementSpec(**data)
        self.db.add(spec)
        await self.db.flush()
        return spec

    async def get_by_id(self, spec_id: str) -> RequirementSpec | None:
        """Get requirement spec by ID."""
        stmt = select(RequirementSpec).where(RequirementSpec.id == spec_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_project(
        self,
        project_id: str,
        requirement_type: str | None = None,
        risk_level: str | None = None,
        verification_status: str | None = None,
        limit: int = 100,
        offset: int = 0
    ) -> list[RequirementSpec]:
        """List requirement specs with filters."""
        stmt = select(RequirementSpec).where(
            RequirementSpec.project_id == project_id
        )

        if requirement_type:
            stmt = stmt.where(RequirementSpec.requirement_type == requirement_type)
        if risk_level:
            stmt = stmt.where(RequirementSpec.risk_level == risk_level)
        if verification_status:
            stmt = stmt.where(RequirementSpec.verification_status == verification_status)

        stmt = stmt.limit(limit).offset(offset)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def update(self, spec_id: str, **data) -> RequirementSpec | None:
        """Update a requirement spec."""
        spec = await self.get_by_id(spec_id)
        if not spec:
            return None

        for key, value in data.items():
            setattr(spec, key, value)

        await self.db.flush()
        return spec

    async def delete(self, spec_id: str) -> bool:
        """Delete a requirement spec."""
        spec = await self.get_by_id(spec_id)
        if not spec:
            return False

        await self.db.delete(spec)
        await self.db.flush()
        return True

    async def get_unverified_by_project(
        self, project_id: str, limit: int = 100
    ) -> list[RequirementSpec]:
        """Get unverified requirements."""
        stmt = select(RequirementSpec).where(
            RequirementSpec.project_id == project_id,
            RequirementSpec.verification_status == "unverified"
        ).limit(limit)

        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_high_risk_by_project(
        self, project_id: str, limit: int = 100
    ) -> list[RequirementSpec]:
        """Get high/critical risk requirements."""
        stmt = select(RequirementSpec).where(
            RequirementSpec.project_id == project_id,
            RequirementSpec.risk_level.in_(["high", "critical"])
        ).limit(limit)

        result = await self.db.execute(stmt)
        return result.scalars().all()


# Similar repository classes for other spec types
```

## Step 6: Create Database Migration

### File: `alembic/versions/XXX_add_item_specs.py`

```python
"""Add item specifications tables.

Revision ID: add_item_specs
Revises: <previous_migration>
Create Date: 2025-01-29 10:00:00.000000
"""

from alembic import op
import sqlalchemy as sa
from tracertm.models.types import JSONType


def upgrade() -> None:
    """Create item specification tables."""

    # Requirement specs table
    op.create_table(
        'requirement_specs',
        sa.Column('id', sa.String(255), primary_key=True),
        sa.Column('item_id', sa.String(255), sa.ForeignKey('items.id'), nullable=False),
        sa.Column('project_id', sa.String(255), sa.ForeignKey('projects.id'), nullable=False),
        sa.Column('requirement_type', sa.String(50), nullable=False),
        sa.Column('risk_level', sa.String(50), nullable=False),
        sa.Column('verification_status', sa.String(50), nullable=False, server_default='unverified'),
        sa.Column('quality_score', sa.Float, nullable=False, server_default='0'),
        sa.Column('impact_score', sa.Float, nullable=True),
        sa.Column('traceability_index', sa.Float, nullable=False, server_default='0'),
        sa.Column('acceptance_criteria', sa.Text, nullable=False),
        sa.Column('verification_evidence', JSONType, nullable=False, server_default='[]'),
        sa.Column('metadata', JSONType, nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    )

    # Create indexes
    op.create_index('idx_requirement_specs_item_id', 'requirement_specs', ['item_id'])
    op.create_index('idx_requirement_specs_project_id', 'requirement_specs', ['project_id'])
    op.create_index('idx_requirement_specs_risk_level', 'requirement_specs', ['risk_level'])
    op.create_index('idx_requirement_specs_verification_status', 'requirement_specs', ['verification_status'])

    # Test specs table
    op.create_table(
        'test_specs',
        sa.Column('id', sa.String(255), primary_key=True),
        sa.Column('item_id', sa.String(255), sa.ForeignKey('items.id'), nullable=False),
        sa.Column('project_id', sa.String(255), sa.ForeignKey('projects.id'), nullable=False),
        sa.Column('test_type', sa.String(50), nullable=False),
        sa.Column('coverage_percentage', sa.Float, nullable=False, server_default='0'),
        sa.Column('pass_rate', sa.Float, nullable=False, server_default='0'),
        sa.Column('flakiness_score', sa.Float, nullable=False, server_default='0'),
        sa.Column('is_quarantined', sa.Boolean, nullable=False, server_default='false'),
        sa.Column('quarantine_reason', sa.String(255), nullable=True),
        sa.Column('last_run', sa.DateTime(timezone=True), nullable=True),
        sa.Column('average_duration_ms', sa.Float, nullable=False, server_default='0'),
        sa.Column('total_runs', sa.Integer, nullable=False, server_default='0'),
        sa.Column('metadata', JSONType, nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    )

    # Create indexes
    op.create_index('idx_test_specs_item_id', 'test_specs', ['item_id'])
    op.create_index('idx_test_specs_project_id', 'test_specs', ['project_id'])
    op.create_index('idx_test_specs_test_type', 'test_specs', ['test_type'])
    op.create_index('idx_test_specs_is_quarantined', 'test_specs', ['is_quarantined'])

    # Similar for other spec types...


def downgrade() -> None:
    """Drop item specification tables."""
    op.drop_table('test_specs')
    op.drop_table('requirement_specs')
    # Drop other spec tables...
```

## Step 7: Update Imports in Models __init__

### File: `src/tracertm/models/__init__.py`

Add imports for new models:

```python
from tracertm.models.item_spec import (
    RequirementSpec,
    TestSpec,
    EpicSpec,
    UserStorySpec,
    TaskSpec,
    DefectSpec,
)
```

## Step 8: Update Schemas __init__

### File: `src/tracertm/schemas/__init__.py`

Add imports for new schemas (if using central export):

```python
from tracertm.schemas.item_spec import (
    RequirementSpecCreate,
    RequirementSpecUpdate,
    RequirementSpecResponse,
    # ... etc
)
```

## Testing Integration

After integration, test the endpoints:

```bash
# Create a requirement
curl -X POST http://localhost:8000/item-specs/requirements \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "item_id": "item_123",
    "requirement_type": "functional",
    "risk_level": "high",
    "acceptance_criteria": "User can login"
  }'

# List requirements
curl -X GET http://localhost:8000/item-specs/requirements?risk_level=high \
  -H "Authorization: Bearer <token>"

# Get test health report
curl -X GET http://localhost:8000/item-specs/tests/health-report \
  -H "Authorization: Bearer <token>"
```

## Development Order

1. Create database models
2. Create migrations and run them
3. Create Pydantic schemas
4. Create repositories
5. Create services
6. Replace TODO markers in router with service calls
7. Write comprehensive tests
8. Register router in main API
9. Test all endpoints
10. Document API usage

## Key Considerations

### Security
- All endpoints require authentication via `auth_guard`
- Row-level security via RLS policies (PostgreSQL)
- Input validation via Pydantic
- SQL injection protection via SQLAlchemy ORM

### Performance
- Database indexes on frequently queried fields
- Pagination support on list endpoints
- Lazy loading to avoid N+1 queries
- Async implementation for concurrency

### Maintainability
- Consistent pattern across all spec types
- Clear separation of concerns (Router -> Service -> Repository)
- Comprehensive docstrings
- Type hints throughout

### Extensibility
- Easy to add new spec types
- Metadata field for custom data
- Flexible filtering on list endpoints
- Hook points for business logic

## Troubleshooting

### Import Errors
If you get import errors after adding the router, ensure:
- File exists at correct path
- All imports in router can be resolved
- Router is registered in main.py

### Database Errors
If migrations fail:
- Check migration syntax
- Ensure previous migrations have run
- Check foreign key references

### Service Not Implemented
If you get 501 errors:
- Services are not yet implemented
- Follow Step 4 to implement service layer
- Replace `TODO` comments with actual logic
