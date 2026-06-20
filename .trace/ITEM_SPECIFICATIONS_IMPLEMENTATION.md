# Item Specifications Implementation Guide

How to create SQLAlchemy models and repositories for the new specification tables.

---

## SQLAlchemy Model Template

### Base Model Pattern

```python
from datetime import datetime
from sqlalchemy import String, ForeignKey, DateTime, Float, Integer, Boolean, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from tracertm.models.base import Base, TimestampMixin

class SpecificationBase(Base, TimestampMixin):
    """Base class for all specification tables."""

    __abstract__ = True

    id: Mapped[str] = mapped_column(String(255), primary_key=True)
    item_id: Mapped[str] = mapped_column(
        String(255),
        ForeignKey("items.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True
    )
    spec_metadata: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        default={},
        server_default="{}"
    )
```

---

## 1. RequirementSpec Model

```python
from tracertm.models.base import SpecificationBase

class RequirementSpec(SpecificationBase):
    """Specification table for requirement-type items."""

    __tablename__ = "requirement_specs"

    # EARS Classification
    requirement_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="ubiquitous",
        server_default="ubiquitous"
    )
    ears_trigger: Mapped[str | None] = mapped_column(Text, nullable=True)
    ears_precondition: Mapped[str | None] = mapped_column(Text, nullable=True)
    ears_postcondition: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Constraint Classification
    constraint_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="hard",
        server_default="hard"
    )
    constraint_target: Mapped[float | None] = mapped_column(Float, nullable=True)
    constraint_tolerance: Mapped[float | None] = mapped_column(Float, nullable=True)
    constraint_unit: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # Verification
    verification_status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="unverified",
        server_default="unverified"
    )
    verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    verified_by: Mapped[str | None] = mapped_column(String(255), nullable=True)
    verification_evidence: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        default={},
        server_default="{}"
    )

    # Formal Specification
    formal_spec: Mapped[str | None] = mapped_column(Text, nullable=True)
    invariants: Mapped[list] = mapped_column(
        JSONB,
        nullable=False,
        default=[],
        server_default="[]"
    )
    preconditions: Mapped[list] = mapped_column(
        JSONB,
        nullable=False,
        default=[],
        server_default="[]"
    )
    postconditions: Mapped[list] = mapped_column(
        JSONB,
        nullable=False,
        default=[],
        server_default="[]"
    )

    # Quality Metrics
    quality_scores: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        default={},
        server_default="{}"
    )
    ambiguity_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    completeness_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    testability_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    overall_quality_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    quality_issues: Mapped[list] = mapped_column(
        JSONB,
        nullable=False,
        default=[],
        server_default="[]"
    )

    # Change Tracking
    volatility_index: Mapped[float | None] = mapped_column(Float, nullable=True)
    change_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default="0"
    )
    last_changed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    change_history: Mapped[list] = mapped_column(
        JSONB,
        nullable=False,
        default=[],
        server_default="[]"
    )

    # Impact Analysis
    change_propagation_index: Mapped[float | None] = mapped_column(Float, nullable=True)
    downstream_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default="0"
    )
    upstream_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default="0"
    )
    impact_assessment: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        default={},
        server_default="{}"
    )

    # Risk & Priority
    risk_level: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="medium",
        server_default="medium"
    )
    risk_factors: Mapped[list] = mapped_column(
        JSONB,
        nullable=False,
        default=[],
        server_default="[]"
    )
    wsjf_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    business_value: Mapped[int | None] = mapped_column(Integer, nullable=True)
    time_criticality: Mapped[int | None] = mapped_column(Integer, nullable=True)
    risk_reduction: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Semantic Analysis
    embeddings_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)
    similar_items: Mapped[list] = mapped_column(
        JSONB,
        nullable=False,
        default=[],
        server_default="[]"
    )
    auto_tags: Mapped[list] = mapped_column(
        JSONB,
        nullable=False,
        default=[],
        server_default="[]"
    )
    complexity_estimate: Mapped[str | None] = mapped_column(String(20), nullable=True)

    # Traceability
    source_reference: Mapped[str | None] = mapped_column(Text, nullable=True)
    rationale: Mapped[str | None] = mapped_column(Text, nullable=True)
    stakeholders: Mapped[list] = mapped_column(
        JSONB,
        nullable=False,
        default=[],
        server_default="[]"
    )
```

---

## Repository Pattern

### Base Repository

```python
from typing import Generic, TypeVar, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select

T = TypeVar("T", bound="SpecificationBase")

class SpecificationRepository(Generic[T]):
    """Base repository for specification tables."""

    def __init__(self, db: Session, model_class: type[T]):
        self.db = db
        self.model_class = model_class

    def create(self, item_id: str, data: dict) -> T:
        """Create new specification."""
        spec = self.model_class(item_id=item_id, **data)
        self.db.add(spec)
        self.db.commit()
        return spec

    def get_by_item(self, item_id: str) -> Optional[T]:
        """Get specification by item_id (unique constraint)."""
        stmt = select(self.model_class).where(
            self.model_class.item_id == item_id
        )
        return self.db.scalar(stmt)

    def update(self, item_id: str, data: dict) -> Optional[T]:
        """Update specification."""
        spec = self.get_by_item(item_id)
        if not spec:
            return None

        for key, value in data.items():
            if hasattr(spec, key):
                setattr(spec, key, value)

        self.db.commit()
        return spec

    def delete(self, item_id: str) -> bool:
        """Delete specification."""
        spec = self.get_by_item(item_id)
        if not spec:
            return False

        self.db.delete(spec)
        self.db.commit()
        return True
```

### Requirement Specification Repository

```python
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import select, func

class RequirementSpecRepository(SpecificationRepository[RequirementSpec]):
    """Repository for requirement specifications."""

    def __init__(self, db: Session):
        super().__init__(db, RequirementSpec)

    def find_by_risk_level(self, risk_level: str) -> list[RequirementSpec]:
        """Find requirements by risk level."""
        stmt = select(self.model_class).where(
            self.model_class.risk_level == risk_level
        ).order_by(self.model_class.wsjf_score.desc())
        return self.db.scalars(stmt).all()

    def find_high_quality_issues(self) -> list[RequirementSpec]:
        """Find requirements with quality issues."""
        stmt = select(self.model_class).where(
            func.jsonb_array_length(self.model_class.quality_issues) > 0
        )
        return self.db.scalars(stmt).all()

    def find_unverified(self) -> list[RequirementSpec]:
        """Find unverified requirements."""
        stmt = select(self.model_class).where(
            self.model_class.verification_status == "unverified"
        ).order_by(self.model_class.risk_level.desc())
        return self.db.scalars(stmt).all()

    def calculate_wsjf_score(
        self,
        business_value: int,
        time_criticality: int,
        risk_reduction: int,
        effort_estimate: int
    ) -> float:
        """Calculate WSJF score."""
        if effort_estimate <= 0:
            return 0.0
        return (business_value + time_criticality + risk_reduction) / effort_estimate

    def update_volatility(self, item_id: str) -> Optional[RequirementSpec]:
        """Update volatility index based on change history."""
        spec = self.get_by_item(item_id)
        if not spec:
            return None

        change_count = spec.change_count
        if change_count == 0:
            spec.volatility_index = 0.0
        else:
            # Calculate based on frequency and recency
            recent_changes = len([
                c for c in spec.change_history
                if c.get("timestamp")  # Recent changes within last 30 days
            ])
            spec.volatility_index = min(1.0, recent_changes / 30.0)

        self.db.commit()
        return spec
```

### Test Specification Repository

```python
class TestSpecRepository(SpecificationRepository[TestSpec]):
    """Repository for test specifications."""

    def __init__(self, db: Session):
        super().__init__(db, TestSpec)

    def find_flaky_tests(self) -> list[TestSpec]:
        """Find flaky tests."""
        stmt = select(self.model_class).where(
            self.model_class.is_flaky == True
        ).order_by(self.model_class.flakiness_index.desc())
        return self.db.scalars(stmt).all()

    def calculate_flakiness(self, item_id: str) -> float:
        """Calculate flakiness from execution history."""
        spec = self.get_by_item(item_id)
        if not spec or spec.execution_count == 0:
            return 0.0

        if spec.failed_count == 0:
            return 0.0

        # Flakiness = occasional failures / total runs
        return min(1.0, spec.failed_count / spec.execution_count * 0.5)

    def find_by_coverage_gap(self, min_coverage: float) -> list[TestSpec]:
        """Find tests below coverage threshold."""
        stmt = select(self.model_class).where(
            self.model_class.coverage_percent < min_coverage
        ).order_by(self.model_class.coverage_percent)
        return self.db.scalars(stmt).all()

    def update_execution_stats(
        self,
        item_id: str,
        status: str,
        duration_ms: float
    ) -> Optional[TestSpec]:
        """Record test execution."""
        spec = self.get_by_item(item_id)
        if not spec:
            return None

        spec.execution_count += 1
        spec.last_executed_at = func.now()
        spec.last_execution_status = status

        if status == "passed":
            spec.passed_count += 1
        elif status == "failed":
            spec.failed_count += 1
        elif status == "skipped":
            spec.skipped_count += 1

        # Update execution history
        if not spec.execution_history:
            spec.execution_history = []

        spec.execution_history.append({
            "timestamp": datetime.now().isoformat(),
            "status": status,
            "duration_ms": duration_ms
        })

        # Keep only last 100 executions
        if len(spec.execution_history) > 100:
            spec.execution_history = spec.execution_history[-100:]

        self.db.commit()
        return spec
```

---

## Service Layer Pattern

### Quality Analyzer Service

```python
from tracertm.repositories.requirement_spec_repository import RequirementSpecRepository

class RequirementQualityService:
    """Service for analyzing requirement quality."""

    def __init__(self, repo: RequirementSpecRepository):
        self.repo = repo

    def analyze_quality(self, item_id: str) -> dict:
        """Comprehensive quality analysis."""
        spec = self.repo.get_by_item(item_id)
        if not spec:
            return {}

        analysis = {
            "overall_score": spec.overall_quality_score or 0.0,
            "dimensions": {
                "ambiguity": spec.ambiguity_score or 0.0,
                "completeness": spec.completeness_score or 0.0,
                "testability": spec.testability_score or 0.0,
            },
            "issues": spec.quality_issues or [],
            "risk_level": spec.risk_level,
            "recommendation": self._get_recommendation(spec)
        }
        return analysis

    def _get_recommendation(self, spec: RequirementSpec) -> str:
        """Generate improvement recommendation."""
        if spec.overall_quality_score is None or spec.overall_quality_score >= 0.8:
            return "Ready for implementation"
        elif spec.overall_quality_score >= 0.6:
            return "Review and address quality issues"
        else:
            return "Major rework needed before proceeding"

    def calculate_all_metrics(self, item_id: str) -> RequirementSpec:
        """Calculate all quality metrics."""
        spec = self.repo.get_by_item(item_id)
        if not spec:
            return None

        # Calculate individual scores (0-1 scale)
        ambiguity = self._calculate_ambiguity(spec)
        completeness = self._calculate_completeness(spec)
        testability = self._calculate_testability(spec)

        spec.ambiguity_score = ambiguity
        spec.completeness_score = completeness
        spec.testability_score = testability

        # Composite score
        spec.overall_quality_score = (ambiguity + completeness + testability) / 3

        # Update quality_scores dict
        spec.quality_scores = {
            "ambiguity": ambiguity,
            "completeness": completeness,
            "testability": testability,
            "overall": spec.overall_quality_score
        }

        return self.repo.db.commit()

    def _calculate_ambiguity(self, spec: RequirementSpec) -> float:
        """Calculate ambiguity score (0=clear, 1=ambiguous)."""
        if not spec.ears_trigger or not spec.ears_postcondition:
            return 1.0  # Missing critical EARS parts = ambiguous
        if spec.formal_spec:
            return 0.1  # Formal spec reduces ambiguity
        return 0.3  # Natural language only

    def _calculate_completeness(self, spec: RequirementSpec) -> float:
        """Calculate completeness (0=incomplete, 1=complete)."""
        requirements = [
            bool(spec.ears_trigger),
            bool(spec.ears_postcondition),
            bool(spec.acceptance_criteria),  # If available
            len(spec.preconditions) > 0,
            len(spec.postconditions) > 0,
        ]
        return sum(requirements) / len(requirements)

    def _calculate_testability(self, spec: RequirementSpec) -> float:
        """Calculate testability (0=untestable, 1=easily testable)."""
        if spec.ears_postcondition and spec.verification_status != "unverified":
            return 0.9
        elif spec.ears_postcondition:
            return 0.7
        return 0.2
```

---

## Usage Examples

### Creating a Requirement Spec

```python
from tracertm.repositories.requirement_spec_repository import RequirementSpecRepository

# In your endpoint/service
def create_requirement(item_id: str, data: dict, db: Session):
    repo = RequirementSpecRepository(db)

    spec = repo.create(
        item_id=item_id,
        data={
            "requirement_type": "ubiquitous",
            "ears_trigger": "When user submits form",
            "ears_precondition": "User is logged in",
            "ears_postcondition": "Data is saved and confirmation shown",
            "constraint_type": "hard",
            "verification_status": "pending",
            "risk_level": "medium"
        }
    )

    # Calculate quality metrics
    quality_service = RequirementQualityService(repo)
    quality_service.calculate_all_metrics(item_id)

    return spec
```

### Querying with Filters

```python
def find_high_priority_requirements(db: Session):
    repo = RequirementSpecRepository(db)

    # Find high-risk requirements
    specs = repo.find_by_risk_level("high")

    # Find with quality issues
    problematic = repo.find_high_quality_issues()

    # Find unverified
    unverified = repo.find_unverified()

    return {
        "high_risk": specs,
        "quality_issues": problematic,
        "unverified": unverified
    }
```

### Recording Test Execution

```python
def execute_test(item_id: str, status: str, duration_ms: float, db: Session):
    repo = TestSpecRepository(db)

    spec = repo.update_execution_stats(
        item_id=item_id,
        status=status,
        duration_ms=duration_ms
    )

    # Check if flaky
    flakiness = repo.calculate_flakiness(item_id)
    if flakiness > 0.3:
        spec.is_flaky = True
        db.commit()

    return spec
```

---

## Database Transactions

### Atomic Updates

```python
from sqlalchemy.orm import Session
from contextlib import contextmanager

@contextmanager
def transaction(db: Session):
    """Context manager for transactions."""
    try:
        yield db
        db.commit()
    except Exception as e:
        db.rollback()
        raise e

# Usage
with transaction(db) as session:
    req_repo = RequirementSpecRepository(session)
    spec = req_repo.get_by_item(item_id)
    spec.verification_status = "verified"
    spec.verified_at = datetime.now()
    spec.verified_by = user_id
```

---

## Performance Considerations

### Indexing for Queries

The migration creates these indexes for optimal performance:

**RequirementSpec:**
- `idx_req_spec_item` - One-to-one lookup
- `idx_req_spec_type` - Type filtering
- `idx_req_spec_risk` - Risk-based queries
- `idx_req_spec_verification` - Status filtering

**TestSpec:**
- `idx_test_spec_flaky` - Quick flaky test lookup
- `idx_test_spec_last_executed` - Recent execution queries
- Combined type/level for test categorization

### Batch Operations

```python
def bulk_update_quality_scores(item_ids: list[str], db: Session):
    """Update quality scores for multiple items."""
    repo = RequirementSpecRepository(db)
    service = RequirementQualityService(repo)

    for item_id in item_ids:
        try:
            service.calculate_all_metrics(item_id)
        except Exception as e:
            print(f"Error processing {item_id}: {e}")

    db.commit()
```

---

**Last Updated:** 2026-01-29
**File:** `/alembic/versions/028_add_item_specifications.py`
