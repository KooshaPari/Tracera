# Project Management Data Model Implementations

## Table of Contents
1. SQLAlchemy Model Definitions
2. Pydantic Schema Definitions
3. Calculation Engine Patterns
4. State Machine Implementations
5. Query Optimization Strategies
6. Integration Patterns

---

## 1. SQLAlchemy Model Definitions

### 1.1 Enhanced Task Model with PM Attributes

```python
"""
Enhanced Task model integrating all PM domains.
Location: src/tracertm/models/task.py
"""

import uuid
from datetime import datetime, date
from typing import Any, Optional, List
from decimal import Decimal
from enum import Enum

from sqlalchemy import (
    DateTime, ForeignKey, Index, Integer, String, Text, Boolean, Float, Date,
    Numeric, Table, Column
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from tracertm.models.base import Base, TimestampMixin
from tracertm.models.types import JSONType


def generate_task_uuid() -> str:
    return str(uuid.uuid4())


# ============================================================================
# Enumerations
# ============================================================================

class TaskStatus(str, Enum):
    """Kanban-style task statuses"""
    NOT_STARTED = "not_started"
    PLANNING = "planning"
    READY = "ready"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    UNDER_REVIEW = "under_review"
    TESTING = "testing"
    COMPLETED = "completed"
    ARCHIVED = "archived"
    CANCELLED = "cancelled"


class DependencyType(str, Enum):
    """IEEE 1490 WBS Standard dependency types"""
    FINISH_START = "fs"
    START_START = "ss"
    FINISH_FINISH = "ff"
    START_FINISH = "sf"


class DependencyStrength(str, Enum):
    """Dependency binding strength"""
    HARD = "hard"
    SOFT = "soft"
    EXTERNAL = "external"


class TaskType(str, Enum):
    """Task classification"""
    FEATURE = "feature"
    BUG = "bug"
    TASK = "task"
    SUBTASK = "subtask"
    EPIC = "epic"
    STORY = "story"
    SPIKE = "spike"


class EstimationSource(str, Enum):
    """Source of effort estimation"""
    HISTORICAL = "historical"
    EXPERT_OPINION = "expert_opinion"
    SIMULATION = "simulation"
    STATISTICAL = "statistical"


class RiskLevel(str, Enum):
    """Task risk severity"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    MINIMAL = "minimal"


class DoRStatus(str, Enum):
    """Definition of Ready assessment status"""
    NOT_READY = "not_ready"
    PARTIALLY_READY = "partially_ready"
    READY = "ready"
    OVER_READY = "over_ready"


class DoDStatus(str, Enum):
    """Definition of Done verification status"""
    NOT_DONE = "not_done"
    PARTIALLY_DONE = "partially_done"
    DONE = "done"
    OVER_DONE = "over_done"


class ScheduleStatus(str, Enum):
    """Current schedule performance"""
    ON_SCHEDULE = "on_schedule"
    AHEAD = "ahead"
    BEHIND = "behind"
    COMPLETED = "completed"


# ============================================================================
# Association Tables
# ============================================================================

task_predecessor_association = Table(
    "task_predecessors",
    Base.metadata,
    Column("from_task_id", String(255), ForeignKey("tasks.id", ondelete="CASCADE")),
    Column("to_task_id", String(255), ForeignKey("tasks.id", ondelete="CASCADE")),
    Column("dependency_type", String(10), nullable=False),
    Column("lag_days", Integer, default=0),
    Index("idx_task_dep_from_to", "from_task_id", "to_task_id"),
)

task_blockers_association = Table(
    "task_blockers",
    Base.metadata,
    Column("task_id", String(255), ForeignKey("tasks.id", ondelete="CASCADE")),
    Column("blocker_id", String(255), ForeignKey("blockers.id", ondelete="CASCADE")),
    Index("idx_task_blockers_assoc", "task_id", "blocker_id"),
)

task_risk_association = Table(
    "task_risks",
    Base.metadata,
    Column("task_id", String(255), ForeignKey("tasks.id", ondelete="CASCADE")),
    Column("risk_id", String(255), ForeignKey("risks.id", ondelete="CASCADE")),
    Column("probability", Float),
    Column("impact_value", Float),
    Index("idx_task_risk_assoc", "task_id", "risk_id"),
)


# ============================================================================
# Main Task Model
# ============================================================================

class Task(Base, TimestampMixin):
    """
    Comprehensive project task model integrating:
    - Kanban workflow (status machine)
    - CPM scheduling (ES, EF, LS, LF, float calculation)
    - PERT estimation (3-point estimation)
    - WBS decomposition (work packages)
    - Resource allocation and tracking
    - Risk management and mitigation
    - Earned Value Management (EVM)
    - Definition of Ready/Done
    """

    __tablename__ = "tasks"

    __table_args__ = (
        Index("idx_tasks_project_status", "project_id", "status"),
        Index("idx_tasks_project_type", "project_id", "task_type"),
        Index("idx_tasks_owner", "owner"),
        Index("idx_tasks_assigned_to", "assigned_to"),
        Index("idx_tasks_parent", "parent_task_id"),
        Index("idx_tasks_wbs", "wbs_code"),
        Index("idx_tasks_planned_dates", "planned_start", "planned_finish"),
        Index("idx_tasks_epic", "epic_id"),
        {"extend_existing": True},
    )

    # ========== IDENTIFICATION ==========
    id: Mapped[str] = mapped_column(String(255), primary_key=True, default=generate_task_uuid)
    task_number: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    project_id: Mapped[str] = mapped_column(
        String(255), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    task_type: Mapped[str] = mapped_column(
        String(50), nullable=False, default=TaskType.TASK.value, index=True
    )

    # ========== HIERARCHY ==========
    parent_task_id: Mapped[str | None] = mapped_column(
        String(255), ForeignKey("tasks.id", ondelete="SET NULL"), nullable=True, index=True
    )
    epic_id: Mapped[str | None] = mapped_column(
        String(255), ForeignKey("tasks.id", ondelete="SET NULL"), nullable=True, index=True
    )
    wbs_code: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    control_account_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    work_package_id: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # ========== OWNERSHIP & ASSIGNMENT ==========
    owner: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    assigned_to: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    secondary_owner: Mapped[str | None] = mapped_column(String(255), nullable=True)
    team_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_by: Mapped[str | None] = mapped_column(String(255), nullable=True)
    modified_by: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # ========== STATUS & WORKFLOW ==========
    status: Mapped[str] = mapped_column(
        String(50), nullable=False, default=TaskStatus.NOT_STARTED.value, index=True
    )
    priority: Mapped[str] = mapped_column(
        String(50), nullable=False, default="medium", index=True
    )
    is_blocked: Mapped[bool] = mapped_column(Boolean, default=False, index=True)

    # ========== TRADITIONAL PM SCHEDULE (CPM) ==========
    planned_start: Mapped[date | None] = mapped_column(Date, nullable=True, index=True)
    planned_finish: Mapped[date | None] = mapped_column(Date, nullable=True, index=True)
    planned_duration_days: Mapped[int | None] = mapped_column(Integer, nullable=True)

    actual_start: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    actual_finish: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    actual_duration_days: Mapped[int | None] = mapped_column(Integer, nullable=True)
    remaining_duration_days: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # CPM Calculated Fields
    early_start: Mapped[date | None] = mapped_column(Date, nullable=True)
    early_finish: Mapped[date | None] = mapped_column(Date, nullable=True)
    late_start: Mapped[date | None] = mapped_column(Date, nullable=True)
    late_finish: Mapped[date | None] = mapped_column(Date, nullable=True)

    total_float_days: Mapped[float | None] = mapped_column(Float, nullable=True)
    free_float_days: Mapped[float | None] = mapped_column(Float, nullable=True)
    is_critical_task: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    criticality_percent: Mapped[float] = mapped_column(Float, default=0.0)

    schedule_variance_days: Mapped[float | None] = mapped_column(Float, nullable=True)
    schedule_variance_percent: Mapped[float | None] = mapped_column(Float, nullable=True)
    schedule_status: Mapped[str] = mapped_column(
        String(50), default=ScheduleStatus.ON_SCHEDULE.value
    )

    # ========== AGILE ESTIMATION (PERT) ==========
    story_points: Mapped[int | None] = mapped_column(Integer, nullable=True)
    optimistic_estimate_days: Mapped[int | None] = mapped_column(Integer, nullable=True)
    most_likely_estimate_days: Mapped[int | None] = mapped_column(Integer, nullable=True)
    pessimistic_estimate_days: Mapped[int | None] = mapped_column(Integer, nullable=True)
    expected_duration_days: Mapped[float | None] = mapped_column(Float, nullable=True)
    duration_standard_deviation: Mapped[float | None] = mapped_column(Float, nullable=True)
    estimation_confidence: Mapped[str | None] = mapped_column(String(50), nullable=True)
    estimation_source: Mapped[str | None] = mapped_column(
        String(50), nullable=True, default=EstimationSource.EXPERT_OPINION.value
    )

    # ========== EFFORT TRACKING ==========
    estimated_hours: Mapped[float | None] = mapped_column(Float, nullable=True)
    estimated_days: Mapped[int | None] = mapped_column(Integer, nullable=True)
    total_effort_hours: Mapped[float | None] = mapped_column(Float, nullable=True)
    total_logged_hours: Mapped[float | None] = mapped_column(Float, nullable=True)
    billable_hours: Mapped[float | None] = mapped_column(Float, nullable=True)
    non_billable_hours: Mapped[float | None] = mapped_column(Float, nullable=True)

    # ========== PROGRESS TRACKING ==========
    percent_complete_physical: Mapped[float] = mapped_column(Float, default=0.0)
    percent_complete_evm: Mapped[float | None] = mapped_column(Float, nullable=True)
    progress_status: Mapped[str] = mapped_column(String(50), default="on_track")
    last_status_update: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status_update_notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # ========== COST MANAGEMENT ==========
    estimated_cost: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    actual_cost_to_date: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    cost_variance: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    budget_category: Mapped[str | None] = mapped_column(String(100), nullable=True)
    is_billable: Mapped[bool] = mapped_column(Boolean, default=False)
    billing_rate: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)

    # ========== EVM METRICS ==========
    planned_value: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    earned_value: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    actual_cost: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    budget_at_completion: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    estimate_at_completion: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    estimate_to_complete: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    variance_at_completion: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)

    cost_performance_index: Mapped[float | None] = mapped_column(Float, nullable=True)
    schedule_performance_index: Mapped[float | None] = mapped_column(Float, nullable=True)

    # ========== QUALITY & ACCEPTANCE ==========
    dor_status: Mapped[str] = mapped_column(
        String(50), default=DoRStatus.NOT_READY.value, index=True
    )
    dor_score: Mapped[float] = mapped_column(Float, default=0.0)

    dod_status: Mapped[str] = mapped_column(
        String(50), default=DoDStatus.NOT_DONE.value, index=True
    )
    dod_score: Mapped[float] = mapped_column(Float, default=0.0)

    acceptance_criteria_count: Mapped[int] = mapped_column(Integer, default=0)
    acceptance_criteria_met: Mapped[int] = mapped_column(Integer, default=0)
    all_criteria_met: Mapped[bool] = mapped_column(Boolean, default=False)
    is_shippable: Mapped[bool] = mapped_column(Boolean, default=False)

    # ========== TESTING & VERIFICATION ==========
    test_cases_passing: Mapped[int] = mapped_column(Integer, default=0)
    test_cases_failing: Mapped[int] = mapped_column(Integer, default=0)
    test_cases_skipped: Mapped[int] = mapped_column(Integer, default=0)
    overall_test_status: Mapped[str] = mapped_column(String(50), default="not_tested")
    code_coverage_percent: Mapped[float | None] = mapped_column(Float, nullable=True)
    minimum_coverage_required: Mapped[float] = mapped_column(Float, default=80.0)

    code_review_status: Mapped[str] = mapped_column(String(50), default="not_started")
    code_review_by: Mapped[str | None] = mapped_column(String(255), nullable=True)
    code_review_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # ========== RISK MANAGEMENT ==========
    risk_level: Mapped[str] = mapped_column(
        String(50), default=RiskLevel.MEDIUM.value, index=True
    )
    risk_probability: Mapped[float] = mapped_column(Float, default=0.0)
    risk_impact_value: Mapped[float] = mapped_column(Float, default=0.0)
    risk_exposure_score: Mapped[float] = mapped_column(Float, default=0.0)
    risk_impact_days: Mapped[int | None] = mapped_column(Integer, nullable=True)
    risk_impact_cost: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)

    contingency_schedule_days: Mapped[int] = mapped_column(Integer, default=0)
    contingency_budget: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)

    # ========== FLEXIBLE METADATA ==========
    task_metadata: Mapped[dict[str, object]] = mapped_column(
        JSONType, nullable=False, default=dict
    )

    # ========== OPTIMISTIC LOCKING ==========
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    # ========== SOFT DELETE ==========
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, index=True
    )

    # ========== RELATIONSHIPS ==========
    parent_task = relationship(
        "Task",
        remote_side=[id],
        backref="child_tasks",
        foreign_keys=[parent_task_id],
    )
    epic = relationship(
        "Task",
        remote_side=[id],
        backref="epic_tasks",
        foreign_keys=[epic_id],
    )
    predecessors = relationship(
        "Task",
        secondary=task_predecessor_association,
        primaryjoin=id == task_predecessor_association.c.from_task_id,
        secondaryjoin=id == task_predecessor_association.c.to_task_id,
        backref="successors",
        foreign_keys=[task_predecessor_association.c.from_task_id, task_predecessor_association.c.to_task_id],
    )
    risks = relationship(
        "Risk",
        secondary=task_risk_association,
        backref="tasks",
    )
    blockers = relationship(
        "Blocker",
        secondary=task_blockers_association,
        backref="tasks",
    )
    time_entries = relationship(
        "TimeEntry",
        backref="task",
        cascade="all, delete-orphan",
    )
    state_history = relationship(
        "TaskStateHistory",
        backref="task",
        cascade="all, delete-orphan",
        lazy="select",
    )
    acceptance_criteria = relationship(
        "TaskAcceptanceCriterion",
        backref="task",
        cascade="all, delete-orphan",
    )

    __mapper_args__: dict[str, Any] = {
        "version_id_col": version,
    }

    def __init__(self, **kwargs: object) -> None:
        if "metadata" in kwargs and "task_metadata" not in kwargs:
            kwargs["task_metadata"] = kwargs.pop("metadata")
        super().__init__(**kwargs)

    def __getattribute__(self, name: str) -> object:
        if name == "metadata":
            return object.__getattribute__(self, "task_metadata")
        return super().__getattribute__(name)

    def __setattr__(self, name: str, value: object) -> None:
        if name == "metadata":
            name = "task_metadata"
        super().__setattr__(name, value)

    def __repr__(self) -> str:
        return f"<Task(id={self.id!r}, number={self.task_number!r}, title={self.title!r})>"

    # ========== COMPUTED PROPERTIES ==========
    @property
    def is_overdue(self) -> bool:
        """Task is overdue if not completed and past finish date"""
        if self.status == TaskStatus.COMPLETED.value:
            return False
        return self.planned_finish and date.today() > self.planned_finish

    @property
    def days_until_start(self) -> int | None:
        """Days until planned start"""
        if not self.planned_start:
            return None
        delta = self.planned_start - date.today()
        return delta.days

    @property
    def days_until_finish(self) -> int | None:
        """Days until planned finish"""
        if not self.planned_finish:
            return None
        delta = self.planned_finish - date.today()
        return delta.days

    @property
    def utilization_percent(self) -> float:
        """Effort utilization percentage"""
        if not self.estimated_hours or self.estimated_hours == 0:
            return 0.0
        return min((self.total_logged_hours or 0) / self.estimated_hours * 100, 100.0)

    @property
    def schedule_health(self) -> str:
        """Health status based on progress and schedule"""
        if self.percent_complete_physical >= 100 and self.status == TaskStatus.COMPLETED.value:
            return "healthy"
        if self.days_until_finish and self.days_until_finish < 0 and self.percent_complete_physical < 100:
            return "critical"
        if self.percent_complete_physical < (100 - (self.days_until_finish or 100)) / 2:
            return "at_risk"
        return "on_track"
```

### 1.2 Supporting Models

```python
# src/tracertm/models/task_related.py

class TaskStateHistory(Base, TimestampMixin):
    """Task status transition audit trail"""
    __tablename__ = "task_state_history"

    id: Mapped[str] = mapped_column(String(255), primary_key=True, default=generate_task_uuid)
    task_id: Mapped[str] = mapped_column(
        String(255), ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False, index=True
    )
    from_state: Mapped[str] = mapped_column(String(50))
    to_state: Mapped[str] = mapped_column(String(50))
    transitioned_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    transitioned_by: Mapped[str] = mapped_column(String(255), nullable=True)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    approval_required: Mapped[bool] = mapped_column(Boolean, default=False)
    approved_by: Mapped[str | None] = mapped_column(String(255), nullable=True)
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        Index("idx_task_state_history_task_id", "task_id"),
        Index("idx_task_state_history_date", "transitioned_at"),
        {"extend_existing": True},
    )


class TaskAcceptanceCriterion(Base, TimestampMixin):
    """Individual acceptance criteria for a task"""
    __tablename__ = "task_acceptance_criteria"

    id: Mapped[str] = mapped_column(String(255), primary_key=True, default=generate_task_uuid)
    task_id: Mapped[str] = mapped_column(
        String(255), ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False, index=True
    )
    criterion_number: Mapped[int] = mapped_column(Integer)
    description: Mapped[str] = mapped_column(Text)
    is_met: Mapped[bool] = mapped_column(Boolean, default=False)
    verified_by: Mapped[str | None] = mapped_column(String(255), nullable=True)
    verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    verification_notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    __table_args__ = (
        Index("idx_task_acceptance_task_id", "task_id"),
        {"extend_existing": True},
    )


class Blocker(Base, TimestampMixin):
    """Task blocker/impediment tracking"""
    __tablename__ = "blockers"

    id: Mapped[str] = mapped_column(String(255), primary_key=True, default=generate_task_uuid)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str] = mapped_column(Text)
    blocker_type: Mapped[str] = mapped_column(
        String(50), nullable=False  # dependency, resource, technical, approval
    )
    status: Mapped[str] = mapped_column(
        String(50), nullable=False, default="open", index=True
    )
    severity: Mapped[str] = mapped_column(String(50), default="medium")
    created_by: Mapped[str] = mapped_column(String(255))
    assigned_to: Mapped[str | None] = mapped_column(String(255), nullable=True)
    target_resolution_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    resolved_by: Mapped[str | None] = mapped_column(String(255), nullable=True)
    resolution: Mapped[str | None] = mapped_column(Text, nullable=True)
    impact_schedule_days: Mapped[int] = mapped_column(Integer, default=0)
    impact_cost: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)

    __table_args__ = (
        Index("idx_blockers_status", "status"),
        Index("idx_blockers_created", "created_at"),
        {"extend_existing": True},
    )


class TimeEntry(Base, TimestampMixin):
    """Task time tracking"""
    __tablename__ = "time_entries"

    id: Mapped[str] = mapped_column(String(255), primary_key=True, default=generate_task_uuid)
    task_id: Mapped[str] = mapped_column(
        String(255), ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False, index=True
    )
    resource_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    entry_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    hours_worked: Mapped[float] = mapped_column(Float, nullable=False)
    work_type: Mapped[str] = mapped_column(String(50))  # development, testing, documentation, etc.
    activity_description: Mapped[str] = mapped_column(Text, nullable=True)
    billable: Mapped[bool] = mapped_column(Boolean, default=True)
    status: Mapped[str] = mapped_column(
        String(50), default="submitted"  # draft, submitted, approved, rejected, billed
    )
    submitted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    approved_by: Mapped[str | None] = mapped_column(String(255), nullable=True)
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        Index("idx_time_entry_task_date", "task_id", "entry_date"),
        Index("idx_time_entry_resource", "resource_id"),
        {"extend_existing": True},
    )


class Risk(Base, TimestampMixin):
    """Risk register entry"""
    __tablename__ = "risks"

    id: Mapped[str] = mapped_column(String(255), primary_key=True, default=generate_task_uuid)
    project_id: Mapped[str] = mapped_column(
        String(255), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str] = mapped_column(Text)
    category: Mapped[str] = mapped_column(
        String(50)  # technical, schedule, resource, cost, external
    )
    probability: Mapped[float] = mapped_column(Float)  # 0.0-1.0
    impact_value: Mapped[float] = mapped_column(Float)  # 0.0-100.0
    exposure_score: Mapped[float] = mapped_column(Float)  # probability * impact
    status: Mapped[str] = mapped_column(
        String(50), default="identified"  # identified, assessed, mitigated, monitored, closed
    )
    mitigation_strategy: Mapped[str] = mapped_column(String(50))  # avoid, mitigate, transfer, accept
    mitigation_plan: Mapped[str | None] = mapped_column(Text, nullable=True)
    contingency_budget: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)

    __table_args__ = (
        Index("idx_risks_project_status", "project_id", "status"),
        {"extend_existing": True},
    )
```

---

## 2. Pydantic Schema Definitions

### 2.1 Task Schemas

```python
# src/tracertm/schemas/task.py

from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List, Any
from pydantic import BaseModel, Field


class TaskCreate(BaseModel):
    """Create a new task"""
    title: str = Field(..., min_length=1, max_length=500)
    description: Optional[str] = None
    project_id: str
    task_type: str = "task"
    parent_task_id: Optional[str] = None
    owner: Optional[str] = None
    assigned_to: Optional[str] = None
    priority: str = "medium"
    planned_start: Optional[date] = None
    planned_finish: Optional[date] = None
    planned_duration_days: Optional[int] = None
    story_points: Optional[int] = None
    estimated_hours: Optional[float] = None


class TaskUpdate(BaseModel):
    """Update task fields"""
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    description: Optional[str] = None
    status: Optional[str] = None
    assigned_to: Optional[str] = None
    priority: Optional[str] = None
    percent_complete_physical: Optional[float] = Field(None, ge=0, le=100)
    planned_finish: Optional[date] = None
    remaining_duration_days: Optional[int] = None


class TaskScheduleUpdate(BaseModel):
    """Update CPM schedule attributes"""
    planned_start: Optional[date] = None
    planned_finish: Optional[date] = None
    planned_duration_days: Optional[int] = None
    early_start: Optional[date] = None
    early_finish: Optional[date] = None
    late_start: Optional[date] = None
    late_finish: Optional[date] = None


class PERTEstimate(BaseModel):
    """PERT three-point estimation"""
    optimistic_days: int
    most_likely_days: int
    pessimistic_days: int
    confidence_level: str = "medium"
    estimation_source: str = "expert_opinion"


class EVMData(BaseModel):
    """Earned Value Management data"""
    planned_value: Decimal
    earned_value: Decimal
    actual_cost: Decimal
    budget_at_completion: Decimal


class TaskResponse(BaseModel):
    """Task response schema"""
    id: str
    task_number: str
    project_id: str
    title: str
    description: Optional[str]
    task_type: str
    status: str
    priority: str
    owner: Optional[str]
    assigned_to: Optional[str]

    # Schedule
    planned_start: Optional[date]
    planned_finish: Optional[date]
    actual_start: Optional[datetime]
    actual_finish: Optional[datetime]
    percent_complete_physical: float

    # Estimation
    story_points: Optional[int]
    estimated_hours: Optional[float]
    total_logged_hours: Optional[float]

    # Quality
    dor_status: str
    dod_status: str
    acceptance_criteria_met: int

    # Risk
    risk_level: str

    # Metadata
    version: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TaskDetailedResponse(TaskResponse):
    """Detailed task response with all fields"""
    # CPM
    early_start: Optional[date]
    early_finish: Optional[date]
    late_start: Optional[date]
    late_finish: Optional[date]
    total_float_days: Optional[float]
    is_critical_task: bool
    schedule_status: str

    # PERT
    optimistic_estimate_days: Optional[int]
    most_likely_estimate_days: Optional[int]
    pessimistic_estimate_days: Optional[int]
    expected_duration_days: Optional[float]

    # EVM
    planned_value: Optional[Decimal]
    earned_value: Optional[Decimal]
    actual_cost: Optional[Decimal]
    cost_performance_index: Optional[float]
    schedule_performance_index: Optional[float]

    # Cost
    estimated_cost: Optional[Decimal]
    actual_cost_to_date: Optional[Decimal]
    budget_at_completion: Optional[Decimal]

    # Testing
    test_cases_passing: int
    test_cases_failing: int
    code_coverage_percent: Optional[float]

    # WBS
    wbs_code: Optional[str]
    work_package_id: Optional[str]

    # Relationships
    predecessor_count: int
    successor_count: int
    blocker_count: int
```

---

## 3. Calculation Engine Patterns

### 3.1 CPM Calculation Service

```python
# src/tracertm/services/cpm_service.py

from datetime import datetime, timedelta, date
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

@dataclass
class Node:
    """Task node in CPM network"""
    task_id: str
    duration: int  # days
    es: int = 0    # Early Start
    ef: int = 0    # Early Finish
    ls: int = 0    # Late Start
    lf: int = 0    # Late Finish
    predecessors: List[str] = None
    successors: List[str] = None

    def __post_init__(self):
        if self.predecessors is None:
            self.predecessors = []
        if self.successors is None:
            self.successors = []

    @property
    def slack(self) -> int:
        return self.lf - self.ef

    @property
    def is_critical(self) -> bool:
        return self.slack == 0


class CPMCalculationService:
    """Calculate Critical Path Method metrics"""

    def __init__(self):
        self.nodes: Dict[str, Node] = {}
        self.critical_path: List[str] = []

    def build_network(self, tasks: List[Dict]) -> None:
        """Build task network from task list"""
        self.nodes = {}
        for task in tasks:
            self.nodes[task['id']] = Node(
                task_id=task['id'],
                duration=task['duration_days'],
                predecessors=task.get('predecessor_ids', []),
                successors=task.get('successor_ids', [])
            )

    def forward_pass(self) -> None:
        """Calculate Early Start and Early Finish"""
        visited = set()

        def calculate_node(node_id: str) -> None:
            if node_id in visited:
                return

            node = self.nodes[node_id]

            # Calculate ES (maximum EF of predecessors + lag)
            if not node.predecessors:
                node.es = 0
            else:
                max_ef = 0
                for pred_id in node.predecessors:
                    calculate_node(pred_id)
                    pred_node = self.nodes[pred_id]
                    max_ef = max(max_ef, pred_node.ef)
                node.es = max_ef

            node.ef = node.es + node.duration
            visited.add(node_id)

        # Start from all tasks
        for task_id in self.nodes:
            if task_id not in visited:
                calculate_node(task_id)

    def backward_pass(self) -> None:
        """Calculate Late Start and Late Finish"""
        # Find project finish (max EF)
        project_finish = max(node.ef for node in self.nodes.values())

        visited = set()

        def calculate_node(node_id: str) -> None:
            if node_id in visited:
                return

            node = self.nodes[node_id]

            # Calculate LF (minimum LS of successors - lag)
            if not node.successors:
                node.lf = project_finish
            else:
                min_ls = float('inf')
                for succ_id in node.successors:
                    calculate_node(succ_id)
                    succ_node = self.nodes[succ_id]
                    min_ls = min(min_ls, succ_node.ls)
                node.lf = min_ls

            node.ls = node.lf - node.duration
            visited.add(node_id)

        # Start from all tasks
        for task_id in self.nodes:
            if task_id not in visited:
                calculate_node(task_id)

    def identify_critical_path(self) -> List[str]:
        """Identify tasks on critical path (slack = 0)"""
        self.critical_path = [
            node_id for node_id, node in self.nodes.items()
            if node.is_critical
        ]
        return self.critical_path

    def calculate_project_metrics(self) -> Dict:
        """Calculate overall project metrics"""
        self.forward_pass()
        self.backward_pass()
        self.identify_critical_path()

        project_finish = max(node.ef for node in self.nodes.values())

        return {
            'project_finish_days': project_finish,
            'critical_path_length': len(self.critical_path),
            'critical_tasks': self.critical_path,
            'total_slack_available': sum(
                node.slack for node in self.nodes.values()
            ),
        }

    def calculate_slack_hierarchy(self) -> Dict[str, float]:
        """Calculate total and free float for each task"""
        slack = {}

        for node_id, node in self.nodes.items():
            # Total Float
            total_float = node.slack

            # Free Float (minimum LS of successors - EF)
            if not node.successors:
                free_float = node.slack
            else:
                min_succ_es = min(
                    self.nodes[succ_id].es for succ_id in node.successors
                )
                free_float = min_succ_es - node.ef

            slack[node_id] = {
                'total_float': total_float,
                'free_float': free_float,
                'is_critical': total_float == 0
            }

        return slack
```

### 3.2 PERT Estimation Service

```python
# src/tracertm/services/pert_service.py

import math
from dataclasses import dataclass

@dataclass
class PERTResult:
    """Result of PERT calculation"""
    expected_duration: float
    standard_deviation: float
    variance: float
    coefficient_of_variation: float
    confidence_68_percent: Tuple[float, float]  # ±1σ
    confidence_95_percent: Tuple[float, float]  # ±2σ
    confidence_99_percent: Tuple[float, float]  # ±3σ


class PERTCalculationService:
    """Program Evaluation Review Technique calculations"""

    @staticmethod
    def calculate_expected_duration(
        optimistic: float, most_likely: float, pessimistic: float
    ) -> float:
        """
        Calculate expected duration using PERT formula:
        E = (O + 4M + P) / 6
        """
        return (optimistic + 4 * most_likely + pessimistic) / 6

    @staticmethod
    def calculate_standard_deviation(
        optimistic: float, pessimistic: float
    ) -> float:
        """
        Calculate standard deviation:
        σ = (P - O) / 6
        """
        return (pessimistic - optimistic) / 6

    @staticmethod
    def calculate_variance(
        optimistic: float, pessimistic: float
    ) -> float:
        """Calculate variance: σ²"""
        std_dev = PERTCalculationService.calculate_standard_deviation(
            optimistic, pessimistic
        )
        return std_dev ** 2

    @classmethod
    def calculate_metrics(
        cls, optimistic: float, most_likely: float, pessimistic: float
    ) -> PERTResult:
        """Calculate all PERT metrics"""
        expected_duration = cls.calculate_expected_duration(
            optimistic, most_likely, pessimistic
        )
        standard_deviation = cls.calculate_standard_deviation(
            optimistic, pessimistic
        )
        variance = standard_deviation ** 2
        coefficient_of_variation = (
            standard_deviation / expected_duration
            if expected_duration > 0
            else 0
        )

        # Confidence intervals
        confidence_68 = (
            expected_duration - 1 * standard_deviation,
            expected_duration + 1 * standard_deviation,
        )
        confidence_95 = (
            expected_duration - 1.96 * standard_deviation,
            expected_duration + 1.96 * standard_deviation,
        )
        confidence_99 = (
            expected_duration - 2.576 * standard_deviation,
            expected_duration + 2.576 * standard_deviation,
        )

        return PERTResult(
            expected_duration=expected_duration,
            standard_deviation=standard_deviation,
            variance=variance,
            coefficient_of_variation=coefficient_of_variation,
            confidence_68_percent=confidence_68,
            confidence_95_percent=confidence_95,
            confidence_99_percent=confidence_99,
        )

    @staticmethod
    def calculate_success_probability(
        target_duration: float,
        expected_duration: float,
        standard_deviation: float,
    ) -> float:
        """
        Calculate probability of completing by target date.
        Uses normal distribution cumulative function.
        """
        if standard_deviation == 0:
            return 1.0 if target_duration >= expected_duration else 0.0

        z_score = (target_duration - expected_duration) / standard_deviation
        # Approximate normal CDF
        probability = 0.5 * (1 + math.erf(z_score / math.sqrt(2)))
        return min(probability, 1.0)
```

### 3.3 EVM Calculation Service

```python
# src/tracertm/services/evm_service.py

from decimal import Decimal
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class EVMMetrics:
    """Earned Value Management metrics"""
    reporting_date: datetime
    planned_value: Decimal      # Budgeted Cost of Work Scheduled (BCWS)
    earned_value: Decimal       # Budgeted Cost of Work Performed (BCWP)
    actual_cost: Decimal        # Actual Cost of Work Performed (ACWP)
    budget_at_completion: Decimal

    # Variance metrics
    cost_variance: Decimal       # EV - AC
    schedule_variance: Decimal   # EV - PV

    # Performance indices
    cost_performance_index: float  # EV / AC
    schedule_performance_index: float  # EV / PV

    # Projections
    estimate_at_completion: Decimal
    estimate_to_complete: Decimal
    variance_at_completion: Decimal

    # Status
    percent_complete: float
    schedule_health: str  # ahead, on_schedule, behind


class EVMCalculationService:
    """Earned Value Management calculations"""

    @staticmethod
    def calculate_cost_variance(earned_value: Decimal, actual_cost: Decimal) -> Decimal:
        """CV = EV - AC"""
        return earned_value - actual_cost

    @staticmethod
    def calculate_schedule_variance(earned_value: Decimal, planned_value: Decimal) -> Decimal:
        """SV = EV - PV"""
        return earned_value - planned_value

    @staticmethod
    def calculate_cost_performance_index(
        earned_value: Decimal, actual_cost: Decimal
    ) -> float:
        """CPI = EV / AC"""
        if actual_cost == 0:
            return 0.0
        return float(earned_value / actual_cost)

    @staticmethod
    def calculate_schedule_performance_index(
        earned_value: Decimal, planned_value: Decimal
    ) -> float:
        """SPI = EV / PV"""
        if planned_value == 0:
            return 0.0
        return float(earned_value / planned_value)

    @staticmethod
    def calculate_estimate_at_completion(
        budget_at_completion: Decimal, cost_performance_index: float
    ) -> Decimal:
        """EAC = BAC / CPI"""
        if cost_performance_index == 0:
            return budget_at_completion
        return budget_at_completion / Decimal(str(cost_performance_index))

    @staticmethod
    def calculate_estimate_to_complete(
        estimate_at_completion: Decimal, actual_cost: Decimal
    ) -> Decimal:
        """ETC = EAC - AC"""
        return estimate_at_completion - actual_cost

    @staticmethod
    def calculate_variance_at_completion(
        budget_at_completion: Decimal, estimate_at_completion: Decimal
    ) -> Decimal:
        """VAC = BAC - EAC"""
        return budget_at_completion - estimate_at_completion

    @classmethod
    def calculate_all_metrics(
        cls,
        planned_value: Decimal,
        earned_value: Decimal,
        actual_cost: Decimal,
        budget_at_completion: Decimal,
        reporting_date: Optional[datetime] = None,
    ) -> EVMMetrics:
        """Calculate all EVM metrics"""
        if reporting_date is None:
            reporting_date = datetime.now()

        cv = cls.calculate_cost_variance(earned_value, actual_cost)
        sv = cls.calculate_schedule_variance(earned_value, planned_value)
        cpi = cls.calculate_cost_performance_index(earned_value, actual_cost)
        spi = cls.calculate_schedule_performance_index(earned_value, planned_value)
        eac = cls.calculate_estimate_at_completion(budget_at_completion, cpi)
        etc = cls.calculate_estimate_to_complete(eac, actual_cost)
        vac = cls.calculate_variance_at_completion(budget_at_completion, eac)

        percent_complete = (
            float(earned_value / budget_at_completion * 100)
            if budget_at_completion > 0
            else 0.0
        )

        # Determine schedule health
        if spi >= 1.0:
            schedule_health = "ahead"
        elif spi >= 0.95:
            schedule_health = "on_schedule"
        else:
            schedule_health = "behind"

        return EVMMetrics(
            reporting_date=reporting_date,
            planned_value=planned_value,
            earned_value=earned_value,
            actual_cost=actual_cost,
            budget_at_completion=budget_at_completion,
            cost_variance=cv,
            schedule_variance=sv,
            cost_performance_index=cpi,
            schedule_performance_index=spi,
            estimate_at_completion=eac,
            estimate_to_complete=etc,
            variance_at_completion=vac,
            percent_complete=percent_complete,
            schedule_health=schedule_health,
        )
```

---

## 4. State Machine Implementation

### 4.1 State Transition Engine

```python
# src/tracertm/services/state_machine_service.py

from enum import Enum
from typing import Callable, Dict, Set, Optional, Tuple
from datetime import datetime

class TaskState(str, Enum):
    NOT_STARTED = "not_started"
    PLANNING = "planning"
    READY = "ready"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    UNDER_REVIEW = "under_review"
    TESTING = "testing"
    COMPLETED = "completed"
    ARCHIVED = "archived"
    CANCELLED = "cancelled"


class StateTransitionRule:
    """Defines allowed transitions from one state to another"""

    def __init__(
        self,
        from_state: TaskState,
        to_state: TaskState,
        requires_approval: bool = False,
        condition: Optional[Callable] = None,
        allowed_roles: Optional[Set[str]] = None,
    ):
        self.from_state = from_state
        self.to_state = to_state
        self.requires_approval = requires_approval
        self.condition = condition
        self.allowed_roles = allowed_roles or {"any"}

    def can_transition(self, task, user_role: str = None) -> Tuple[bool, str]:
        """Check if transition is allowed"""
        # Check role permission
        if self.allowed_roles and "any" not in self.allowed_roles:
            if user_role not in self.allowed_roles:
                return False, f"Role '{user_role}' not allowed for this transition"

        # Check condition
        if self.condition and not self.condition(task):
            return False, "Transition condition not met"

        return True, ""


class TaskStateMachine:
    """Task workflow state machine"""

    TRANSITIONS: Dict[TaskState, Set[TaskState]] = {
        TaskState.NOT_STARTED: {TaskState.PLANNING, TaskState.CANCELLED},
        TaskState.PLANNING: {TaskState.READY, TaskState.CANCELLED},
        TaskState.READY: {TaskState.IN_PROGRESS, TaskState.BLOCKED, TaskState.CANCELLED},
        TaskState.IN_PROGRESS: {
            TaskState.BLOCKED,
            TaskState.UNDER_REVIEW,
            TaskState.CANCELLED,
        },
        TaskState.BLOCKED: {TaskState.IN_PROGRESS, TaskState.CANCELLED},
        TaskState.UNDER_REVIEW: {
            TaskState.IN_PROGRESS,
            TaskState.TESTING,
            TaskState.CANCELLED,
        },
        TaskState.TESTING: {
            TaskState.IN_PROGRESS,
            TaskState.COMPLETED,
            TaskState.CANCELLED,
        },
        TaskState.COMPLETED: {TaskState.ARCHIVED},
        TaskState.ARCHIVED: set(),
        TaskState.CANCELLED: set(),
    }

    APPROVAL_REQUIRED = {
        (TaskState.UNDER_REVIEW, TaskState.COMPLETED),
        (TaskState.PLANNING, TaskState.READY),
    }

    def __init__(self):
        self.rules: Dict[Tuple[TaskState, TaskState], StateTransitionRule] = {}
        self._setup_default_rules()

    def _setup_default_rules(self) -> None:
        """Setup default transition rules"""
        for from_state, to_states in self.TRANSITIONS.items():
            for to_state in to_states:
                requires_approval = (from_state, to_state) in self.APPROVAL_REQUIRED
                self.add_rule(
                    StateTransitionRule(
                        from_state=from_state,
                        to_state=to_state,
                        requires_approval=requires_approval,
                    )
                )

    def add_rule(self, rule: StateTransitionRule) -> None:
        """Add custom transition rule"""
        key = (rule.from_state, rule.to_state)
        self.rules[key] = rule

    def can_transition(
        self, current_state: TaskState, to_state: TaskState, user_role: str = None
    ) -> Tuple[bool, str]:
        """Check if transition is allowed"""
        if to_state not in self.TRANSITIONS.get(current_state, set()):
            return False, f"No transition from {current_state} to {to_state}"

        rule = self.rules.get((current_state, to_state))
        if rule:
            return rule.can_transition(None, user_role)

        return True, ""

    def get_allowed_transitions(
        self, current_state: TaskState, user_role: str = None
    ) -> Set[TaskState]:
        """Get all allowed transitions from current state"""
        allowed = set()
        for to_state in self.TRANSITIONS.get(current_state, set()):
            can_transition, _ = self.can_transition(
                current_state, to_state, user_role
            )
            if can_transition:
                allowed.add(to_state)
        return allowed

    def transition(
        self,
        task,
        to_state: TaskState,
        user_id: str,
        user_role: str = None,
        reason: str = None,
    ) -> Tuple[bool, str]:
        """Execute state transition"""
        current_state = TaskState(task.status)

        # Check if transition is allowed
        allowed, error = self.can_transition(current_state, to_state, user_role)
        if not allowed:
            return False, error

        # Check if approval is required
        rule = self.rules.get((current_state, to_state))
        if rule and rule.requires_approval:
            task.status_requires_approval = True
            task.approval_pending_user = user_id
            return True, "Transition requires approval"

        # Apply transition
        task.previous_status = current_state.value
        task.status = to_state.value
        task.last_status_change = datetime.now()
        task.last_status_change_by = user_id
        task.status_change_reason = reason

        return True, ""
```

---

## 5. Conclusion

This implementation guide provides:

1. **Comprehensive SQLAlchemy models** supporting all PM domains
2. **Pydantic schemas** for API validation
3. **Calculation engines** for CPM, PERT, and EVM
4. **State machine** for workflow enforcement
5. **Modular, extensible architecture** for future enhancements

All components follow SOLID principles and are designed for production use in enterprise PM systems supporting both agile and traditional methodologies.

