# TraceRTM: Problem and Process Modeling Implementation Plan

**Document Version:** 1.0
**Date:** January 2025
**Status:** Approved for Implementation

---

## Executive Summary

This document outlines a comprehensive, phased implementation plan for adding Problem and Process modeling capabilities to TraceRTM. The plan leverages existing architectural patterns (repository pattern, Item model extension, JSONB metadata) while introducing targeted new entities and workflows to handle complex problem lifecycle management and process definition/execution.

### Key Design Decision

**Recommended Approach: Hybrid Model Strategy**
- **Problems**: Dedicated `Problem` entity (complex state machine, RCA workflows, KEDB integration)
- **Processes**: Dedicated `Process` entity (lifecycle management, BPMN visualization)
- **Integration**: Both link to existing Items via new Link types and relationships

This approach preserves backward compatibility while enabling specialized workflows without overloading the Item model.

### Implementation Timeline

| Phase | Duration | Scope |
|-------|----------|-------|
| **MVP (Phase 1)** | Weeks 1-4 | Problem entity, basic CRUD, status transitions, list/detail views |
| **Enhanced (Phase 2)** | Weeks 5-8 | Process entity, swimlane diagrams, process-to-task relationships |
| **RCA & KEDB (Phase 3)** | Weeks 9-12 | Root Cause Analysis tools, Known Error Database, impact assessment |
| **Knowledge Integration (Phase 4)** | Weeks 13-16 | Learning system, problem resolution recommendations, analytics |

---

## Part 1: Data Model Design

### 1.1 Problem Entity

**Purpose:** Track reported problems with complex lifecycle, root cause analysis, and resolution workflows.

#### Database Schema

```python
# File: src/tracertm/models/problem.py

from datetime import datetime
from typing import Any, Literal

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from tracertm.models.base import Base, TimestampMixin
from tracertm.models.types import JSONType


class Problem(Base, TimestampMixin):
    """
    Problem model for issue/defect tracking with lifecycle management.

    Supports complex state machine transitions and RCA workflows.
    """

    __tablename__ = "problems"

    __table_args__ = (
        Index("idx_problems_project_status", "project_id", "status"),
        Index("idx_problems_project_category", "project_id", "category"),
        Index("idx_problems_severity", "project_id", "severity"),
        Index("idx_problems_owner", "project_id", "owner"),
        {"extend_existing": True},
    )

    id: Mapped[str] = mapped_column(
        String(255), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    project_id: Mapped[str] = mapped_column(
        String(255),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Core fields
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    problem_statement: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Status management
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="open",
        index=True,
    )
    # Enum values: open, in_investigation, pending_workaround, known_error, awaiting_fix, closed

    # Classification
    category: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    # Examples: performance, security, usability, data_integrity, integration, deployment

    severity: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="medium",
        index=True,
    )
    # Enum values: critical, high, medium, low

    impact_level: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="medium",
    )
    # Enum values: critical, high, medium, low

    # Relationships
    reported_by: Mapped[str | None] = mapped_column(String(255), nullable=True)
    owner: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    assignee: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Parent problem (for problem hierarchies)
    parent_problem_id: Mapped[str | None] = mapped_column(
        String(255),
        ForeignKey("problems.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Dates
    reported_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    first_occurrence: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    last_occurrence: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    resolved_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Impact assessment
    affected_systems: Mapped[list[str]] = mapped_column(
        JSONType,
        nullable=False,
        default=list,
    )
    affected_users_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    estimated_business_impact: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Root cause analysis
    root_cause: Mapped[str | None] = mapped_column(Text, nullable=True)
    root_cause_analysis: Mapped[dict[str, Any]] = mapped_column(
        JSONType,
        nullable=False,
        default=dict,
    )
    # Structure: {
    #   "method": "5_whys" | "fishbone" | "kepner_tregoe",
    #   "findings": [...],
    #   "contributing_factors": [...]
    # }

    # Resolution
    workaround: Mapped[str | None] = mapped_column(Text, nullable=True)
    permanent_fix: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Known Error Database reference
    kedb_reference: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Extensibility
    problem_metadata: Mapped[dict[str, Any]] = mapped_column(
        JSONType,
        nullable=False,
        default=dict,
    )

    # Optimistic locking
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    # Soft delete
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, index=True
    )

    __mapper_args__: dict[str, Any] = {
        "version_id_col": version,
    }
```

#### Problem Status State Machine

```
OPEN
  ↓
IN_INVESTIGATION
  ├→ PENDING_WORKAROUND (if workaround identified)
  │   └→ AWAITING_FIX (permanent solution in progress)
  │       └→ CLOSED (resolved)
  ├→ KNOWN_ERROR (documented in KEDB)
  │   └→ AWAITING_FIX
  │       └→ CLOSED
  └→ AWAITING_FIX (direct path if solution found)
      └→ CLOSED

CANCELLED (any state)
```

### 1.2 Process Entity

**Purpose:** Model business processes, workflows, and procedures with lifecycle stages and relationships to tasks/items.

#### Database Schema

```python
# File: src/tracertm/models/process.py

from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from tracertm.models.base import Base, TimestampMixin
from tracertm.models.types import JSONType


class Process(Base, TimestampMixin):
    """
    Process model for workflow and procedure definition.

    Supports BPMN-style visualization, swimlane diagrams, and lifecycle management.
    """

    __tablename__ = "processes"

    __table_args__ = (
        Index("idx_processes_project_status", "project_id", "status"),
        Index("idx_processes_project_category", "project_id", "category"),
        Index("idx_processes_owner", "project_id", "owner"),
        {"extend_existing": True},
    )

    id: Mapped[str] = mapped_column(
        String(255), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    project_id: Mapped[str] = mapped_column(
        String(255),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Core fields
    name: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Process classification
    category: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    # Examples: development, deployment, incident_response, change_management,
    #           quality_assurance, security, compliance, operations

    # Status management
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="draft",
        index=True,
    )
    # Enum values: draft, active, deprecated, retired, archived

    # Version control for process definitions
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    version_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_current_version: Mapped[bool] = mapped_column(
        nullable=False, default=True, index=True
    )

    parent_process_id: Mapped[str | None] = mapped_column(
        String(255),
        ForeignKey("processes.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Ownership and governance
    owner: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    stakeholders: Mapped[list[str]] = mapped_column(
        JSONType,
        nullable=False,
        default=list,
    )

    # Lifecycle definition
    stages: Mapped[list[dict[str, Any]]] = mapped_column(
        JSONType,
        nullable=False,
        default=list,
    )
    # Structure: [
    #   {
    #     "id": "stage_1",
    #     "name": "Planning",
    #     "description": "...",
    #     "sequence": 1,
    #     "entry_criteria": "...",
    #     "exit_criteria": "..."
    #   },
    #   ...
    # ]

    # BPMN visualization
    bpmn_definition: Mapped[dict[str, Any]] = mapped_column(
        JSONType,
        nullable=False,
        default=dict,
    )
    # Stores BPMN 2.0 XML or simplified JSON representation

    # Swimlanes for BPMN diagrams
    swimlanes: Mapped[list[dict[str, Any]]] = mapped_column(
        JSONType,
        nullable=False,
        default=list,
    )
    # Structure: [
    #   {
    #     "id": "swimlane_1",
    #     "name": "Development Team",
    #     "color": "#...",
    #     "responsibilities": ["..."]
    #   },
    #   ...
    # ]

    # Entry/exit criteria
    entry_criteria: Mapped[str | None] = mapped_column(Text, nullable=True)
    exit_criteria: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Performance metrics
    sla_duration_hours: Mapped[int | None] = mapped_column(Integer, nullable=True)
    target_cycle_time_minutes: Mapped[int | None] = mapped_column(
        Integer, nullable=True
    )

    # Documentation
    documentation_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    runbook: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Extensibility
    process_metadata: Mapped[dict[str, Any]] = mapped_column(
        JSONType,
        nullable=False,
        default=dict,
    )

    # Dates
    activated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    deprecated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Soft delete
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, index=True
    )

    __mapper_args__: dict[str, Any] = {
        "version_id_col": version,
    }
```

#### Process Status Lifecycle

```
DRAFT
  ↓
ACTIVE
  ├→ DEPRECATED (new version available)
  │   └→ RETIRED (older version, no longer supported)
  │       └→ ARCHIVED
  └→ ARCHIVED

ACTIVE can transition back to DRAFT for updates
```

### 1.3 New Link Types

Add these link types to the Link model's type enumeration:

```python
# New Link Types to support Problem and Process relationships

NEW_LINK_TYPES = {
    # Problem-to-Problem relationships
    "causes": "Problem A causes Problem B",
    "blocks": "Problem blocks other problem",

    # Item-to-Problem relationships
    "resolves": "Item resolves Problem",
    "triggers": "Item or event triggers Problem",
    "duplicate_of": "Problem is duplicate of another",

    # Process-to-Item relationships
    "executes": "Process executes Item/Task",
    "defines": "Process defines/documents Item",

    # Item-to-Process relationships
    "follows": "Item follows Process",
    "implements": "Item implements Process step",

    # Problem-to-Process relationships
    "prevented_by": "Problem prevented by Process",
    "resolved_by": "Problem resolved by Process",

    # Known Error Links
    "has_workaround": "Problem has known workaround",
    "documented_in": "Problem documented in KEDB",
}
```

### 1.4 Problem Activity Log

```python
# File: src/tracertm/models/problem_activity.py

from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from tracertm.models.base import Base, TimestampMixin
from tracertm.models.types import JSONType


class ProblemActivity(Base, TimestampMixin):
    """Activity log for problem lifecycle tracking."""

    __tablename__ = "problem_activities"

    __table_args__ = (
        Index("idx_problem_activities_problem", "problem_id"),
        Index("idx_problem_activities_type", "activity_type"),
    )

    id: Mapped[str] = mapped_column(
        String(255), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    problem_id: Mapped[str] = mapped_column(
        String(255),
        ForeignKey("problems.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    activity_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    # Values: status_changed, rca_added, workaround_identified, assigned,
    #         commented, linked_to_item, resolved

    actor: Mapped[str | None] = mapped_column(String(255), nullable=True)
    action_description: Mapped[str] = mapped_column(Text, nullable=False)

    # Previous and current state
    previous_state: Mapped[dict[str, Any]] = mapped_column(
        JSONType,
        nullable=False,
        default=dict,
    )
    new_state: Mapped[dict[str, Any]] = mapped_column(
        JSONType,
        nullable=False,
        default=dict,
    )

    metadata: Mapped[dict[str, Any]] = mapped_column(
        JSONType,
        nullable=False,
        default=dict,
    )
```

---

## Part 2: API Endpoints

### 2.1 Problem API Endpoints

#### Base URL: `/api/v1/projects/{project_id}/problems`

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/` | Create new problem |
| GET | `/` | List problems (with filters) |
| GET | `/{problem_id}` | Get problem details |
| PUT | `/{problem_id}` | Update problem |
| DELETE | `/{problem_id}` | Soft delete problem |
| POST | `/{problem_id}/status` | Transition problem status |
| POST | `/{problem_id}/rca` | Start/update RCA |
| POST | `/{problem_id}/rca/5-whys` | Perform 5 Whys analysis |
| POST | `/{problem_id}/rca/fishbone` | Perform Fishbone analysis |
| POST | `/{problem_id}/workaround` | Add workaround |
| GET | `/{problem_id}/activity` | Get activity log |
| POST | `/{problem_id}/link` | Link to item |
| GET | `/{problem_id}/impact` | Get impact analysis |

#### Problem Create Endpoint

```python
# File: src/tracertm/api/main.py - Add to FastAPI app

@app.post("/api/v1/projects/{project_id}/problems", tags=["problems"])
async def create_problem(
    project_id: str,
    problem_create: ProblemCreate,
    session: AsyncSession = Depends(get_db_session),
) -> ProblemResponse:
    """
    Create a new problem.

    Args:
        project_id: Project ID
        problem_create: Problem creation schema
        session: Database session

    Returns:
        Created problem

    Raises:
        404: Project not found
        422: Validation error
    """
    problem_service = ProblemService(session)
    problem = await problem_service.create_problem(
        project_id=project_id,
        title=problem_create.title,
        description=problem_create.description,
        category=problem_create.category,
        severity=problem_create.severity,
        reported_by=problem_create.reported_by,
        affected_systems=problem_create.affected_systems,
    )
    return ProblemResponse.from_orm(problem)


@app.put("/api/v1/projects/{project_id}/problems/{problem_id}", tags=["problems"])
async def update_problem(
    project_id: str,
    problem_id: str,
    problem_update: ProblemUpdate,
    session: AsyncSession = Depends(get_db_session),
) -> ProblemResponse:
    """Update an existing problem."""
    problem_service = ProblemService(session)
    problem = await problem_service.update_problem(
        problem_id=problem_id,
        project_id=project_id,
        **problem_update.dict(exclude_unset=True)
    )
    return ProblemResponse.from_orm(problem)


@app.post(
    "/api/v1/projects/{project_id}/problems/{problem_id}/status",
    tags=["problems"]
)
async def transition_problem_status(
    project_id: str,
    problem_id: str,
    status_transition: ProblemStatusTransition,
    session: AsyncSession = Depends(get_db_session),
) -> ProblemResponse:
    """
    Transition problem status with validation.

    Validates state machine rules before allowing transition.
    """
    problem_service = ProblemService(session)
    problem = await problem_service.transition_status(
        problem_id=problem_id,
        project_id=project_id,
        new_status=status_transition.new_status,
        reason=status_transition.reason,
    )
    return ProblemResponse.from_orm(problem)


@app.post(
    "/api/v1/projects/{project_id}/problems/{problem_id}/rca/5-whys",
    tags=["problems"]
)
async def perform_5_whys_analysis(
    project_id: str,
    problem_id: str,
    analysis: FiveWhysRequest,
    session: AsyncSession = Depends(get_db_session),
) -> RCAResponse:
    """
    Perform 5 Whys root cause analysis.

    Guides structured problem decomposition.
    """
    rca_service = RootCauseAnalysisService(session)
    result = await rca_service.perform_5_whys(
        problem_id=problem_id,
        project_id=project_id,
        initial_problem=analysis.initial_problem,
        questions_answers=analysis.questions_answers,
    )
    return RCAResponse.from_orm(result)


@app.post(
    "/api/v1/projects/{project_id}/problems/{problem_id}/rca/fishbone",
    tags=["problems"]
)
async def perform_fishbone_analysis(
    project_id: str,
    problem_id: str,
    analysis: FishboneRequest,
    session: AsyncSession = Depends(get_db_session),
) -> RCAResponse:
    """
    Perform Fishbone (Ishikawa) diagram analysis.

    Identifies contributing factors across categories.
    """
    rca_service = RootCauseAnalysisService(session)
    result = await rca_service.perform_fishbone(
        problem_id=problem_id,
        project_id=project_id,
        categories=analysis.categories,
        factors=analysis.factors,
    )
    return RCAResponse.from_orm(result)


@app.get(
    "/api/v1/projects/{project_id}/problems",
    tags=["problems"]
)
async def list_problems(
    project_id: str,
    status: str | None = None,
    category: str | None = None,
    severity: str | None = None,
    owner: str | None = None,
    skip: int = 0,
    limit: int = 50,
    session: AsyncSession = Depends(get_db_session),
) -> list[ProblemResponse]:
    """
    List problems with filtering.

    Query Parameters:
        status: Filter by problem status
        category: Filter by category
        severity: Filter by severity
        owner: Filter by owner
        skip: Skip N results
        limit: Limit results to N (max 100)
    """
    problem_service = ProblemService(session)
    problems = await problem_service.list_problems(
        project_id=project_id,
        status=status,
        category=category,
        severity=severity,
        owner=owner,
        skip=skip,
        limit=min(limit, 100),
    )
    return [ProblemResponse.from_orm(p) for p in problems]
```

### 2.2 Process API Endpoints

#### Base URL: `/api/v1/projects/{project_id}/processes`

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/` | Create new process |
| GET | `/` | List processes |
| GET | `/{process_id}` | Get process details |
| PUT | `/{process_id}` | Update process |
| DELETE | `/{process_id}` | Soft delete process |
| POST | `/{process_id}/version` | Create new version |
| POST | `/{process_id}/activate` | Activate process |
| POST | `/{process_id}/deprecate` | Deprecate process |
| GET | `/{process_id}/bpmn` | Get BPMN diagram |
| POST | `/{process_id}/bpmn` | Update BPMN diagram |
| GET | `/{process_id}/swimlanes` | Get swimlane definitions |
| POST | `/{process_id}/execute` | Execute process |
| GET | `/{process_id}/executions` | List process executions |

#### Process Create Endpoint

```python
# File: src/tracertm/api/main.py - Add to FastAPI app

@app.post("/api/v1/projects/{project_id}/processes", tags=["processes"])
async def create_process(
    project_id: str,
    process_create: ProcessCreate,
    session: AsyncSession = Depends(get_db_session),
) -> ProcessResponse:
    """
    Create a new process.

    Args:
        project_id: Project ID
        process_create: Process creation schema
        session: Database session

    Returns:
        Created process
    """
    process_service = ProcessService(session)
    process = await process_service.create_process(
        project_id=project_id,
        name=process_create.name,
        description=process_create.description,
        category=process_create.category,
        owner=process_create.owner,
        stages=process_create.stages,
        swimlanes=process_create.swimlanes,
    )
    return ProcessResponse.from_orm(process)


@app.post(
    "/api/v1/projects/{project_id}/processes/{process_id}/activate",
    tags=["processes"]
)
async def activate_process(
    project_id: str,
    process_id: str,
    session: AsyncSession = Depends(get_db_session),
) -> ProcessResponse:
    """
    Activate a process (transition from draft to active).

    Validates all required fields before activation.
    """
    process_service = ProcessService(session)
    process = await process_service.activate_process(
        process_id=process_id,
        project_id=project_id,
    )
    return ProcessResponse.from_orm(process)


@app.get(
    "/api/v1/projects/{project_id}/processes/{process_id}/bpmn",
    tags=["processes"]
)
async def get_process_bpmn(
    project_id: str,
    process_id: str,
    format: str = "json",  # "json" or "xml"
    session: AsyncSession = Depends(get_db_session),
) -> dict[str, Any]:
    """
    Get process BPMN definition.

    Query Parameters:
        format: Return format (json or xml)
    """
    process_service = ProcessService(session)
    bpmn = await process_service.get_bpmn_definition(
        process_id=process_id,
        project_id=project_id,
        format=format,
    )
    return bpmn


@app.post(
    "/api/v1/projects/{project_id}/processes/{process_id}/version",
    tags=["processes"]
)
async def create_process_version(
    project_id: str,
    process_id: str,
    version_request: ProcessVersionRequest,
    session: AsyncSession = Depends(get_db_session),
) -> ProcessResponse:
    """
    Create a new version of the process.

    Current active version becomes deprecated.
    New version can be activated when ready.
    """
    process_service = ProcessService(session)
    new_version = await process_service.create_version(
        process_id=process_id,
        project_id=project_id,
        changes=version_request.changes,
        notes=version_request.notes,
    )
    return ProcessResponse.from_orm(new_version)
```

---

## Part 3: Frontend Components

### 3.1 React Component Structure

```
src/
  components/
    problems/
      ProblemList.tsx              # Main problem list view
      ProblemDetail.tsx            # Problem detail/view
      ProblemModal.tsx             # Create/edit modal
      ProblemStatusBadge.tsx       # Status indicator
      ProblemSeverityBadge.tsx     # Severity indicator
      RCAModal.tsx                 # RCA tool modal
      FiveWhysForm.tsx             # 5 Whys analysis form
      FishboneForm.tsx             # Fishbone diagram form
      KnownErrorModal.tsx          # Known Error database entry
      ProblemActivityLog.tsx       # Activity timeline

    processes/
      ProcessList.tsx              # Main process list view
      ProcessDetail.tsx            # Process detail/view
      ProcessModal.tsx             # Create/edit modal
      ProcessActivationDialog.tsx  # Activation confirmation
      BPMNDiagram.tsx              # BPMN visualization
      SwimlaneEditor.tsx           # Swimlane diagram editor
      ProcessStageBuilder.tsx      # Stage definition UI
      ProcessVersionHistory.tsx    # Version management

  hooks/
    useProblem.ts                  # Problem CRUD operations
    useProcess.ts                  # Process CRUD operations
    useProblemFilters.ts           # Problem filtering logic
    useProcessFilters.ts           # Process filtering logic
    useRCA.ts                      # RCA workflow hooks

  services/
    api/
      problemsApi.ts               # Problem API client
      processesApi.ts              # Process API client
      rcaApi.ts                    # RCA API client
```

### 3.2 Problem List View

```typescript
// File: src/components/problems/ProblemList.tsx

import { FC, useState } from 'react';
import {
  Table,
  TableHeader,
  TableColumn,
  TableBody,
  TableRow,
  TableCell,
  Input,
  Button,
  Pagination,
  Chip,
  Modal,
} from '@tracertm/ui';
import { useProblem } from '@/hooks/useProblem';
import { ProblemModal } from './ProblemModal';
import { ProblemDetail } from './ProblemDetail';

export interface ProblemListProps {
  projectId: string;
}

export const ProblemList: FC<ProblemListProps> = ({ projectId }) => {
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState<string | null>(null);
  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const [selectedProblem, setSelectedProblem] = useState<string | null>(null);

  const { problems, isLoading, createProblem } = useProblem({
    projectId,
    status: statusFilter,
    search,
    page,
  });

  const statusColors = {
    open: 'bg-red-100',
    in_investigation: 'bg-yellow-100',
    pending_workaround: 'bg-orange-100',
    known_error: 'bg-purple-100',
    awaiting_fix: 'bg-blue-100',
    closed: 'bg-green-100',
  };

  const severityColors = {
    critical: 'text-red-600',
    high: 'text-orange-600',
    medium: 'text-yellow-600',
    low: 'text-green-600',
  };

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold">Problems</h2>
        <Button onClick={() => setIsCreateOpen(true)}>
          New Problem
        </Button>
      </div>

      <div className="flex gap-2">
        <Input
          placeholder="Search problems..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="flex-1"
        />
        <select
          value={statusFilter || ''}
          onChange={(e) => setStatusFilter(e.target.value || null)}
          className="px-3 py-2 border rounded"
        >
          <option value="">All Statuses</option>
          <option value="open">Open</option>
          <option value="in_investigation">In Investigation</option>
          <option value="pending_workaround">Pending Workaround</option>
          <option value="known_error">Known Error</option>
          <option value="awaiting_fix">Awaiting Fix</option>
          <option value="closed">Closed</option>
        </select>
      </div>

      <Table>
        <TableHeader>
          <TableColumn>Title</TableColumn>
          <TableColumn>Status</TableColumn>
          <TableColumn>Severity</TableColumn>
          <TableColumn>Owner</TableColumn>
          <TableColumn>Actions</TableColumn>
        </TableHeader>
        <TableBody>
          {problems.map((problem) => (
            <TableRow key={problem.id}>
              <TableCell>{problem.title}</TableCell>
              <TableCell>
                <Chip
                  className={statusColors[problem.status as keyof typeof statusColors]}
                >
                  {problem.status.replace(/_/g, ' ')}
                </Chip>
              </TableCell>
              <TableCell>
                <span className={severityColors[problem.severity as keyof typeof severityColors]}>
                  {problem.severity}
                </span>
              </TableCell>
              <TableCell>{problem.owner || '-'}</TableCell>
              <TableCell>
                <Button
                  size="sm"
                  onClick={() => setSelectedProblem(problem.id)}
                >
                  View
                </Button>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>

      <Pagination
        page={page}
        totalPages={Math.ceil(problems.length / 50)}
        onChange={setPage}
      />

      <ProblemModal
        isOpen={isCreateOpen}
        onClose={() => setIsCreateOpen(false)}
        projectId={projectId}
        onSuccess={() => setIsCreateOpen(false)}
      />

      {selectedProblem && (
        <Modal
          isOpen={true}
          onClose={() => setSelectedProblem(null)}
          size="xl"
        >
          <ProblemDetail
            projectId={projectId}
            problemId={selectedProblem}
            onClose={() => setSelectedProblem(null)}
          />
        </Modal>
      )}
    </div>
  );
};
```

### 3.3 Problem Detail View

```typescript
// File: src/components/problems/ProblemDetail.tsx

import { FC, useState } from 'react';
import { Tabs, Button, Card, Badge } from '@tracertm/ui';
import { useProblem } from '@/hooks/useProblem';
import { RCAModal } from './RCAModal';
import { FiveWhysForm } from './FiveWhysForm';
import { FishboneForm } from './FishboneForm';
import { ProblemActivityLog } from './ProblemActivityLog';

export interface ProblemDetailProps {
  projectId: string;
  problemId: string;
  onClose: () => void;
}

export const ProblemDetail: FC<ProblemDetailProps> = ({
  projectId,
  problemId,
  onClose,
}) => {
  const { problem, isLoading, transitionStatus } = useProblem({
    projectId,
    problemId,
  });

  const [activeTab, setActiveTab] = useState<'overview' | 'rca' | 'activity'>('overview');
  const [isRCAModalOpen, setIsRCAModalOpen] = useState(false);

  if (isLoading || !problem) {
    return <div>Loading...</div>;
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-start">
        <div>
          <h3 className="text-xl font-bold">{problem.title}</h3>
          <p className="text-gray-600">{problem.description}</p>
        </div>
        <div className="space-x-2">
          <Badge>{problem.severity}</Badge>
          <Badge>{problem.status}</Badge>
        </div>
      </div>

      <Tabs activeTab={activeTab} onChange={setActiveTab}>
        <Tab name="overview" label="Overview">
          <Card>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="font-semibold">Category</label>
                <p>{problem.category}</p>
              </div>
              <div>
                <label className="font-semibold">Owner</label>
                <p>{problem.owner || 'Unassigned'}</p>
              </div>
              <div>
                <label className="font-semibold">Reported By</label>
                <p>{problem.reported_by}</p>
              </div>
              <div>
                <label className="font-semibold">Impact Level</label>
                <p>{problem.impact_level}</p>
              </div>
              <div className="col-span-2">
                <label className="font-semibold">Affected Systems</label>
                <div className="flex gap-2 flex-wrap">
                  {problem.affected_systems?.map((sys) => (
                    <Badge key={sys}>{sys}</Badge>
                  ))}
                </div>
              </div>
              {problem.workaround && (
                <div className="col-span-2">
                  <label className="font-semibold">Workaround</label>
                  <p>{problem.workaround}</p>
                </div>
              )}
              {problem.root_cause && (
                <div className="col-span-2">
                  <label className="font-semibold">Root Cause</label>
                  <p>{problem.root_cause}</p>
                </div>
              )}
            </div>
          </Card>
        </Tab>

        <Tab name="rca" label="Root Cause Analysis">
          <Card className="space-y-4">
            <div className="flex justify-end">
              <Button onClick={() => setIsRCAModalOpen(true)}>
                Start RCA
              </Button>
            </div>

            {problem.root_cause_analysis?.method && (
              <div>
                <h4 className="font-semibold mb-2">
                  {problem.root_cause_analysis.method.replace(/_/g, ' ')}
                </h4>
                {/* Display RCA findings based on method */}
              </div>
            )}
          </Card>
        </Tab>

        <Tab name="activity" label="Activity Log">
          <ProblemActivityLog problemId={problemId} />
        </Tab>
      </Tabs>

      <RCAModal
        isOpen={isRCAModalOpen}
        onClose={() => setIsRCAModalOpen(false)}
        problemId={problemId}
        projectId={projectId}
      />
    </div>
  );
};
```

### 3.4 Custom Hooks

```typescript
// File: src/hooks/useProblem.ts

import { useQuery, useMutation } from '@tanstack/react-query';
import { problemsApi } from '@/services/api/problemsApi';
import { ProblemCreate, ProblemUpdate, Problem } from '@/types/problem';

export interface UseProblemOptions {
  projectId: string;
  problemId?: string;
  status?: string | null;
  search?: string;
  page?: number;
}

export const useProblem = ({
  projectId,
  problemId,
  status,
  search,
  page = 1,
}: UseProblemOptions) => {
  // Fetch list of problems
  const problemsQuery = useQuery({
    queryKey: ['problems', projectId, { status, search, page }],
    queryFn: () =>
      problemsApi.listProblems(projectId, {
        status,
        search,
        page,
      }),
    enabled: !problemId,
  });

  // Fetch single problem
  const problemQuery = useQuery({
    queryKey: ['problem', projectId, problemId],
    queryFn: () => problemsApi.getProblem(projectId, problemId!),
    enabled: !!problemId,
  });

  // Create problem mutation
  const createMutation = useMutation({
    mutationFn: (data: ProblemCreate) =>
      problemsApi.createProblem(projectId, data),
    onSuccess: () => {
      problemsQuery.refetch();
    },
  });

  // Update problem mutation
  const updateMutation = useMutation({
    mutationFn: (data: ProblemUpdate) =>
      problemsApi.updateProblem(projectId, problemId!, data),
    onSuccess: () => {
      problemQuery.refetch();
      problemsQuery.refetch();
    },
  });

  // Status transition mutation
  const statusMutation = useMutation({
    mutationFn: (newStatus: string) =>
      problemsApi.transitionStatus(projectId, problemId!, {
        new_status: newStatus,
      }),
    onSuccess: () => {
      problemQuery.refetch();
    },
  });

  return {
    problems: problemsQuery.data || [],
    problem: problemQuery.data,
    isLoading: problemsQuery.isLoading || problemQuery.isLoading,
    createProblem: createMutation.mutate,
    updateProblem: updateMutation.mutate,
    transitionStatus: statusMutation.mutate,
  };
};
```

---

## Part 4: State Management

### 4.1 Zustand Store for Problems

```typescript
// File: src/stores/problemStore.ts

import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';
import { Problem, ProblemFilter } from '@/types/problem';

interface ProblemStore {
  // State
  problems: Problem[];
  selectedProblem: Problem | null;
  filters: ProblemFilter;
  isLoading: boolean;
  error: string | null;

  // Actions
  setProblems: (problems: Problem[]) => void;
  setSelectedProblem: (problem: Problem | null) => void;
  setFilters: (filters: ProblemFilter) => void;
  addProblem: (problem: Problem) => void;
  updateProblem: (problem: Problem) => void;
  removeProblem: (problemId: string) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  reset: () => void;
}

const initialState = {
  problems: [],
  selectedProblem: null,
  filters: {},
  isLoading: false,
  error: null,
};

export const useProblemStore = create<ProblemStore>()(
  devtools(
    persist(
      (set) => ({
        ...initialState,
        setProblems: (problems) => set({ problems }),
        setSelectedProblem: (selectedProblem) =>
          set({ selectedProblem }),
        setFilters: (filters) =>
          set((state) => ({
            filters: { ...state.filters, ...filters },
          })),
        addProblem: (problem) =>
          set((state) => ({
            problems: [...state.problems, problem],
          })),
        updateProblem: (problem) =>
          set((state) => ({
            problems: state.problems.map((p) =>
              p.id === problem.id ? problem : p
            ),
          })),
        removeProblem: (problemId) =>
          set((state) => ({
            problems: state.problems.filter((p) => p.id !== problemId),
          })),
        setLoading: (isLoading) => set({ isLoading }),
        setError: (error) => set({ error }),
        reset: () => set(initialState),
      }),
      {
        name: 'problem-store',
      }
    )
  )
);
```

### 4.2 React Query Configuration

```typescript
// File: src/config/queryClient.ts

import { QueryClient, DefaultOptions } from '@tanstack/react-query';

const queryConfig: DefaultOptions = {
  queries: {
    staleTime: 1000 * 60 * 5, // 5 minutes
    gcTime: 1000 * 60 * 10, // 10 minutes
    retry: 1,
    refetchOnWindowFocus: true,
  },
  mutations: {
    retry: 1,
  },
};

export const queryClient = new QueryClient({
  defaultOptions: queryConfig,
});
```

---

## Part 5: Pydantic Schemas

### 5.1 Problem Schemas

```python
# File: src/tracertm/schemas/problem.py

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class ProblemCreate(BaseModel):
    """Schema for creating a problem."""

    title: str = Field(..., min_length=1, max_length=500)
    description: str | None = None
    problem_statement: str | None = None

    category: str = Field(..., min_length=1, max_length=100)
    severity: str = Field(default="medium", max_length=50)
    impact_level: str = Field(default="medium", max_length=50)

    reported_by: str | None = None
    owner: str | None = None
    affected_systems: list[str] = Field(default_factory=list)
    estimated_business_impact: str | None = None


class ProblemUpdate(BaseModel):
    """Schema for updating a problem."""

    title: str | None = Field(None, min_length=1, max_length=500)
    description: str | None = None
    problem_statement: str | None = None

    severity: str | None = None
    impact_level: str | None = None
    owner: str | None = None
    assignee: str | None = None

    affected_systems: list[str] | None = None
    affected_users_count: int | None = None
    estimated_business_impact: str | None = None


class ProblemStatusTransition(BaseModel):
    """Schema for problem status transitions."""

    new_status: str = Field(
        ...,
        description="Target status (open, in_investigation, pending_workaround, "
                   "known_error, awaiting_fix, closed)"
    )
    reason: str | None = None


class RootCauseAnalysis(BaseModel):
    """Schema for RCA data."""

    method: str  # "5_whys", "fishbone", "kepner_tregoe"
    findings: list[str] = Field(default_factory=list)
    contributing_factors: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class ProblemResponse(BaseModel):
    """Schema for problem response."""

    id: str
    project_id: str

    title: str
    description: str | None
    problem_statement: str | None

    status: str
    category: str
    severity: str
    impact_level: str

    reported_by: str | None
    owner: str | None
    assignee: str | None
    parent_problem_id: str | None

    reported_at: datetime | None
    first_occurrence: datetime | None
    last_occurrence: datetime | None
    resolved_at: datetime | None

    affected_systems: list[str]
    affected_users_count: int | None
    estimated_business_impact: str | None

    root_cause: str | None
    root_cause_analysis: dict[str, Any]
    workaround: str | None
    permanent_fix: str | None
    kedb_reference: str | None

    problem_metadata: dict[str, Any]
    version: int
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None

    class Config:
        from_attributes = True


class FiveWhysRequest(BaseModel):
    """Request schema for 5 Whys analysis."""

    initial_problem: str
    questions_answers: list[dict[str, str]] = Field(
        ...,
        description="List of {'why': question, 'because': answer} dicts"
    )


class FishboneRequest(BaseModel):
    """Request schema for Fishbone analysis."""

    categories: list[str] = Field(
        ...,
        description="Categories like People, Process, Materials, etc."
    )
    factors: dict[str, list[str]] = Field(
        ...,
        description="Contributing factors grouped by category"
    )
```

### 5.2 Process Schemas

```python
# File: src/tracertm/schemas/process.py

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class ProcessStage(BaseModel):
    """Schema for process stage definition."""

    id: str
    name: str
    description: str | None = None
    sequence: int
    entry_criteria: str | None = None
    exit_criteria: str | None = None


class ProcessSwimlane(BaseModel):
    """Schema for swimlane in BPMN diagram."""

    id: str
    name: str
    color: str | None = None
    responsibilities: list[str] = Field(default_factory=list)


class ProcessCreate(BaseModel):
    """Schema for creating a process."""

    name: str = Field(..., min_length=1, max_length=500)
    description: str | None = None

    category: str = Field(..., min_length=1, max_length=100)
    owner: str | None = None
    stakeholders: list[str] = Field(default_factory=list)

    stages: list[ProcessStage] = Field(default_factory=list)
    swimlanes: list[ProcessSwimlane] = Field(default_factory=list)

    entry_criteria: str | None = None
    exit_criteria: str | None = None

    sla_duration_hours: int | None = None
    target_cycle_time_minutes: int | None = None


class ProcessUpdate(BaseModel):
    """Schema for updating a process."""

    name: str | None = None
    description: str | None = None

    owner: str | None = None
    stakeholders: list[str] | None = None

    stages: list[ProcessStage] | None = None
    swimlanes: list[ProcessSwimlane] | None = None

    entry_criteria: str | None = None
    exit_criteria: str | None = None

    sla_duration_hours: int | None = None
    target_cycle_time_minutes: int | None = None


class ProcessVersionRequest(BaseModel):
    """Request schema for creating new process version."""

    changes: str = Field(..., description="Summary of changes")
    notes: str | None = None


class ProcessResponse(BaseModel):
    """Schema for process response."""

    id: str
    project_id: str

    name: str
    description: str | None

    category: str
    status: str
    version: int
    version_notes: str | None
    is_current_version: bool
    parent_process_id: str | None

    owner: str | None
    stakeholders: list[str]

    stages: list[ProcessStage]
    swimlanes: list[ProcessSwimlane]

    entry_criteria: str | None
    exit_criteria: str | None

    sla_duration_hours: int | None
    target_cycle_time_minutes: int | None

    documentation_url: str | None
    runbook: str | None

    process_metadata: dict[str, Any]

    activated_at: datetime | None
    deprecated_at: datetime | None

    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None

    class Config:
        from_attributes = True
```

---

## Part 6: Services Implementation

### 6.1 Problem Service

```python
# File: src/tracertm/services/problem_service.py

from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from tracertm.models.problem import Problem
from tracertm.models.problem_activity import ProblemActivity


class ProblemService:
    """Service for problem management and lifecycle."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_problem(
        self,
        project_id: str,
        title: str,
        description: str | None = None,
        category: str = "other",
        severity: str = "medium",
        reported_by: str | None = None,
        affected_systems: list[str] | None = None,
    ) -> Problem:
        """Create a new problem."""
        problem = Problem(
            id=str(uuid4()),
            project_id=project_id,
            title=title,
            description=description,
            category=category,
            severity=severity,
            status="open",
            reported_by=reported_by,
            reported_at=datetime.now(UTC),
            affected_systems=affected_systems or [],
        )
        self.session.add(problem)
        await self.session.flush()

        # Log activity
        await self._log_activity(
            problem_id=problem.id,
            activity_type="created",
            action_description=f"Problem '{title}' created",
        )

        return problem

    async def update_problem(
        self,
        problem_id: str,
        project_id: str,
        **kwargs: Any,
    ) -> Problem:
        """Update a problem."""
        problem = await self.get_by_id(problem_id, project_id)
        if not problem:
            raise ValueError(f"Problem {problem_id} not found")

        # Update fields
        for key, value in kwargs.items():
            if hasattr(problem, key) and value is not None:
                setattr(problem, key, value)

        await self.session.flush()

        # Log activity
        await self._log_activity(
            problem_id=problem_id,
            activity_type="updated",
            action_description="Problem updated",
        )

        return problem

    async def transition_status(
        self,
        problem_id: str,
        project_id: str,
        new_status: str,
        reason: str | None = None,
    ) -> Problem:
        """Transition problem status with validation."""
        problem = await self.get_by_id(problem_id, project_id)
        if not problem:
            raise ValueError(f"Problem {problem_id} not found")

        # Validate state transition
        if not self._is_valid_transition(problem.status, new_status):
            raise ValueError(
                f"Cannot transition from {problem.status} to {new_status}"
            )

        old_status = problem.status
        problem.status = new_status

        # Set resolved_at if closing
        if new_status == "closed":
            problem.resolved_at = datetime.now(UTC)

        await self.session.flush()

        # Log activity
        await self._log_activity(
            problem_id=problem_id,
            activity_type="status_changed",
            action_description=f"Status changed from {old_status} to {new_status}",
            previous_state={"status": old_status},
            new_state={"status": new_status},
        )

        return problem

    async def get_by_id(
        self,
        problem_id: str,
        project_id: str | None = None,
    ) -> Problem | None:
        """Get problem by ID."""
        query = select(Problem).where(
            Problem.id == problem_id,
            Problem.deleted_at.is_(None),
        )

        if project_id:
            query = query.where(Problem.project_id == project_id)

        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def list_problems(
        self,
        project_id: str,
        status: str | None = None,
        category: str | None = None,
        severity: str | None = None,
        owner: str | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> list[Problem]:
        """List problems with filters."""
        query = select(Problem).where(
            Problem.project_id == project_id,
            Problem.deleted_at.is_(None),
        )

        if status:
            query = query.where(Problem.status == status)
        if category:
            query = query.where(Problem.category == category)
        if severity:
            query = query.where(Problem.severity == severity)
        if owner:
            query = query.where(Problem.owner == owner)

        query = query.order_by(Problem.created_at.desc())
        query = query.offset(skip).limit(limit)

        result = await self.session.execute(query)
        return list(result.scalars().all())

    def _is_valid_transition(self, current_status: str, new_status: str) -> bool:
        """Validate status transitions according to state machine."""
        valid_transitions = {
            "open": ["in_investigation", "closed", "cancelled"],
            "in_investigation": [
                "pending_workaround",
                "known_error",
                "awaiting_fix",
                "closed",
                "cancelled",
            ],
            "pending_workaround": ["awaiting_fix", "closed", "cancelled"],
            "known_error": ["awaiting_fix", "closed", "cancelled"],
            "awaiting_fix": ["closed", "cancelled"],
            "closed": [],
            "cancelled": [],
        }
        return new_status in valid_transitions.get(current_status, [])

    async def _log_activity(
        self,
        problem_id: str,
        activity_type: str,
        action_description: str,
        previous_state: dict[str, Any] | None = None,
        new_state: dict[str, Any] | None = None,
    ) -> ProblemActivity:
        """Log problem activity."""
        activity = ProblemActivity(
            id=str(uuid4()),
            problem_id=problem_id,
            activity_type=activity_type,
            action_description=action_description,
            previous_state=previous_state or {},
            new_state=new_state or {},
        )
        self.session.add(activity)
        await self.session.flush()
        return activity
```

### 6.2 Root Cause Analysis Service

```python
# File: src/tracertm/services/root_cause_analysis_service.py

from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from tracertm.models.problem import Problem


class RootCauseAnalysisService:
    """Service for RCA workflow management."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def perform_5_whys(
        self,
        problem_id: str,
        project_id: str,
        initial_problem: str,
        questions_answers: list[dict[str, str]],
    ) -> Problem:
        """
        Perform 5 Whys root cause analysis.

        Args:
            problem_id: Problem ID
            project_id: Project ID
            initial_problem: Initial problem statement
            questions_answers: List of {why: q, because: a} dicts

        Returns:
            Updated problem with RCA data
        """
        problem = await self._get_problem(problem_id, project_id)

        # Build RCA analysis
        rca_data = {
            "method": "5_whys",
            "initial_problem": initial_problem,
            "questions_answers": questions_answers,
            "findings": [qa["because"] for qa in questions_answers],
            "depth": len(questions_answers),
            "completed_at": datetime.now(UTC).isoformat(),
        }

        problem.root_cause_analysis = rca_data

        # Extract potential root cause from deepest answer
        if questions_answers:
            problem.root_cause = questions_answers[-1].get("because")

        await self.session.flush()
        return problem

    async def perform_fishbone(
        self,
        problem_id: str,
        project_id: str,
        categories: list[str],
        factors: dict[str, list[str]],
    ) -> Problem:
        """
        Perform Fishbone (Ishikawa) diagram analysis.

        Common categories:
        - People (skills, knowledge, motivation)
        - Process (procedures, workflows)
        - Materials (components, resources)
        - Methods (techniques, approaches)
        - Machines (tools, equipment)
        - Environment (conditions, external factors)
        """
        problem = await self._get_problem(problem_id, project_id)

        rca_data = {
            "method": "fishbone",
            "categories": categories,
            "factors": factors,
            "factor_count": sum(len(v) for v in factors.values()),
            "completed_at": datetime.now(UTC).isoformat(),
        }

        problem.root_cause_analysis = rca_data

        # Identify most significant factors
        most_significant = self._get_significant_factors(factors)
        problem.root_cause = f"Multiple factors: {', '.join(most_significant)}"

        await self.session.flush()
        return problem

    def _get_significant_factors(
        self,
        factors: dict[str, list[str]],
        top_n: int = 3,
    ) -> list[str]:
        """Extract top N most significant factors."""
        # Flatten all factors and return top N
        all_factors = []
        for category, factor_list in factors.items():
            all_factors.extend(factor_list)
        return all_factors[:top_n]

    async def _get_problem(
        self,
        problem_id: str,
        project_id: str,
    ) -> Problem:
        """Get problem with validation."""
        from sqlalchemy import select

        query = select(Problem).where(
            Problem.id == problem_id,
            Problem.project_id == project_id,
            Problem.deleted_at.is_(None),
        )
        result = await self.session.execute(query)
        problem = result.scalar_one_or_none()

        if not problem:
            raise ValueError(f"Problem {problem_id} not found")

        return problem
```

### 6.3 Process Service

```python
# File: src/tracertm/services/process_service.py

from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from tracertm.models.process import Process


class ProcessService:
    """Service for process management and lifecycle."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_process(
        self,
        project_id: str,
        name: str,
        description: str | None = None,
        category: str = "other",
        owner: str | None = None,
        stages: list[dict[str, Any]] | None = None,
        swimlanes: list[dict[str, Any]] | None = None,
    ) -> Process:
        """Create a new process."""
        process = Process(
            id=str(uuid4()),
            project_id=project_id,
            name=name,
            description=description,
            category=category,
            status="draft",
            owner=owner,
            stages=stages or [],
            swimlanes=swimlanes or [],
            version=1,
            is_current_version=True,
        )
        self.session.add(process)
        await self.session.flush()
        return process

    async def activate_process(
        self,
        process_id: str,
        project_id: str,
    ) -> Process:
        """Activate a process (draft -> active)."""
        process = await self.get_by_id(process_id, project_id)
        if not process:
            raise ValueError(f"Process {process_id} not found")

        # Validate required fields
        if not process.stages:
            raise ValueError("Process must have at least one stage")
        if not process.entry_criteria or not process.exit_criteria:
            raise ValueError("Process must define entry and exit criteria")

        process.status = "active"
        process.activated_at = datetime.now(UTC)

        await self.session.flush()
        return process

    async def create_version(
        self,
        process_id: str,
        project_id: str,
        changes: str,
        notes: str | None = None,
    ) -> Process:
        """Create a new version of the process."""
        current = await self.get_by_id(process_id, project_id)
        if not current:
            raise ValueError(f"Process {process_id} not found")

        # Mark current as deprecated
        current.is_current_version = False
        if current.status == "active":
            current.status = "deprecated"
            current.deprecated_at = datetime.now(UTC)

        # Create new version
        new_version = Process(
            id=str(uuid4()),
            project_id=project_id,
            parent_process_id=current.id,
            name=current.name,
            description=current.description,
            category=current.category,
            owner=current.owner,
            stakeholders=current.stakeholders,
            stages=current.stages,
            swimlanes=current.swimlanes,
            status="draft",
            version=current.version + 1,
            version_notes=notes,
            is_current_version=True,
        )
        self.session.add(new_version)
        await self.session.flush()
        return new_version

    async def get_by_id(
        self,
        process_id: str,
        project_id: str | None = None,
    ) -> Process | None:
        """Get process by ID."""
        query = select(Process).where(
            Process.id == process_id,
            Process.deleted_at.is_(None),
        )

        if project_id:
            query = query.where(Process.project_id == project_id)

        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def list_processes(
        self,
        project_id: str,
        status: str | None = None,
        category: str | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> list[Process]:
        """List processes with filters."""
        query = select(Process).where(
            Process.project_id == project_id,
            Process.deleted_at.is_(None),
            Process.is_current_version.is_(True),  # Only current versions
        )

        if status:
            query = query.where(Process.status == status)
        if category:
            query = query.where(Process.category == category)

        query = query.order_by(Process.created_at.desc())
        query = query.offset(skip).limit(limit)

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_bpmn_definition(
        self,
        process_id: str,
        project_id: str,
        format: str = "json",
    ) -> dict[str, Any]:
        """Get BPMN definition in specified format."""
        process = await self.get_by_id(process_id, project_id)
        if not process:
            raise ValueError(f"Process {process_id} not found")

        if format == "json":
            return self._bpmn_to_json(process)
        elif format == "xml":
            return {"xml": self._bpmn_to_xml(process)}
        else:
            raise ValueError(f"Unsupported format: {format}")

    def _bpmn_to_json(self, process: Process) -> dict[str, Any]:
        """Convert process to BPMN JSON."""
        return {
            "id": process.id,
            "name": process.name,
            "stages": process.stages,
            "swimlanes": process.swimlanes,
            "metadata": process.process_metadata,
        }

    def _bpmn_to_xml(self, process: Process) -> str:
        """Convert process to BPMN XML (simplified)."""
        # TODO: Implement proper BPMN 2.0 XML generation
        return f"<bpmn><process id='{process.id}' name='{process.name}'/></bpmn>"
```

---

## Part 7: Repository Layer

### 7.1 Problem Repository

```python
# File: src/tracertm/repositories/problem_repository.py

from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from tracertm.models.problem import Problem


class ProblemRepository:
    """Repository for Problem CRUD operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self,
        project_id: str,
        title: str,
        category: str,
        severity: str = "medium",
        description: str | None = None,
        reported_by: str | None = None,
        owner: str | None = None,
        affected_systems: list[str] | None = None,
    ) -> Problem:
        """Create new problem."""
        problem = Problem(
            id=str(uuid4()),
            project_id=project_id,
            title=title,
            description=description,
            category=category,
            severity=severity,
            status="open",
            reported_by=reported_by,
            owner=owner,
            reported_at=datetime.now(UTC),
            affected_systems=affected_systems or [],
            version=1,
        )
        self.session.add(problem)
        await self.session.flush()
        await self.session.refresh(problem)
        return problem

    async def get_by_id(
        self,
        problem_id: str,
        project_id: str | None = None,
    ) -> Problem | None:
        """Get problem by ID."""
        query = select(Problem).where(
            Problem.id == problem_id,
            Problem.deleted_at.is_(None),
        )

        if project_id:
            query = query.where(Problem.project_id == project_id)

        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def update(
        self,
        problem_id: str,
        **kwargs: Any,
    ) -> Problem | None:
        """Update problem fields."""
        problem = await self.get_by_id(problem_id)
        if not problem:
            return None

        for key, value in kwargs.items():
            if hasattr(problem, key) and value is not None:
                setattr(problem, key, value)

        await self.session.flush()
        await self.session.refresh(problem)
        return problem

    async def delete(self, problem_id: str) -> bool:
        """Soft delete problem."""
        problem = await self.get_by_id(problem_id)
        if not problem:
            return False

        problem.deleted_at = datetime.now(UTC)
        await self.session.flush()
        return True

    async def list_all(
        self,
        project_id: str,
        include_deleted: bool = False,
    ) -> list[Problem]:
        """List all problems."""
        query = select(Problem).where(Problem.project_id == project_id)
        if not include_deleted:
            query = query.where(Problem.deleted_at.is_(None))

        query = query.order_by(Problem.created_at.desc())
        result = await self.session.execute(query)
        return list(result.scalars().all())
```

### 7.2 Process Repository

```python
# File: src/tracertm/repositories/process_repository.py

from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from tracertm.models.process import Process


class ProcessRepository:
    """Repository for Process CRUD operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self,
        project_id: str,
        name: str,
        category: str,
        description: str | None = None,
        owner: str | None = None,
        stages: list[dict[str, Any]] | None = None,
        swimlanes: list[dict[str, Any]] | None = None,
    ) -> Process:
        """Create new process."""
        process = Process(
            id=str(uuid4()),
            project_id=project_id,
            name=name,
            description=description,
            category=category,
            owner=owner,
            stages=stages or [],
            swimlanes=swimlanes or [],
            status="draft",
            version=1,
            is_current_version=True,
        )
        self.session.add(process)
        await self.session.flush()
        await self.session.refresh(process)
        return process

    async def get_by_id(
        self,
        process_id: str,
        project_id: str | None = None,
    ) -> Process | None:
        """Get process by ID."""
        query = select(Process).where(
            Process.id == process_id,
            Process.deleted_at.is_(None),
        )

        if project_id:
            query = query.where(Process.project_id == project_id)

        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def list_all(
        self,
        project_id: str,
        include_deleted: bool = False,
        current_only: bool = True,
    ) -> list[Process]:
        """List all processes."""
        query = select(Process).where(Process.project_id == project_id)
        if not include_deleted:
            query = query.where(Process.deleted_at.is_(None))
        if current_only:
            query = query.where(Process.is_current_version.is_(True))

        query = query.order_by(Process.created_at.desc())
        result = await self.session.execute(query)
        return list(result.scalars().all())
```

---

## Part 8: Phase Breakdown & Timeline

### Phase 1: MVP - Problem Entity (Weeks 1-4)

**Goals:**
- Functional problem CRUD operations
- Status state machine implementation
- Basic list and detail views
- Activity logging

**Deliverables:**
1. Database migration for Problem model
2. ProblemRepository with full CRUD
3. ProblemService with status transitions
4. API endpoints (create, read, update, list, delete, status)
5. Frontend: ProblemList, ProblemDetail, ProblemModal
6. Basic tests

**Success Metrics:**
- All problem CRUD operations functional
- Status transitions validated
- Activity log populated on state changes
- List view with filtering by status/severity
- 80% code coverage for problem operations

### Phase 2: Enhanced - Process Entity (Weeks 5-8)

**Goals:**
- Process CRUD and lifecycle management
- BPMN visualization support
- Swimlane diagram capabilities
- Process versioning

**Deliverables:**
1. Database migration for Process model
2. ProcessRepository with versioning logic
3. ProcessService with activation/deprecation
4. API endpoints (create, read, update, list, version)
5. Frontend: ProcessList, ProcessDetail, BPMNDiagram, SwimlaneEditor
6. BPMN JSON/XML generation
7. Tests for process lifecycle

**Success Metrics:**
- Process CRUD fully functional
- Version history maintained correctly
- BPMN visualization renders properly
- Swimlane diagrams display correctly
- 80% code coverage for process operations

### Phase 3: RCA & KEDB (Weeks 9-12)

**Goals:**
- Root Cause Analysis tools (5 Whys, Fishbone)
- Known Error Database integration
- Impact assessment framework
- Problem-to-solution linking

**Deliverables:**
1. RootCauseAnalysisService implementation
2. FiveWhysForm and FishboneForm components
3. RCAModal integration
4. KnownErrorDatabase model and service
5. Impact analysis API endpoint
6. Problem linking to items/processes
7. RCA tests and validation

**Success Metrics:**
- 5 Whys and Fishbone analyses functional
- RCA findings stored and retrievable
- KEDB entries linked to problems
- Impact analysis calculations accurate
- RCA workflows fully tested

### Phase 4: Knowledge Integration (Weeks 13-16)

**Goals:**
- Problem resolution recommendations
- Learning system integration
- Analytics and reporting
- Workflow automation

**Deliverables:**
1. ProblemAnalyticsService
2. Resolution recommendation engine
3. Problem trend analysis
4. Automated workflow triggers
5. Dashboard/reporting components
6. Integration tests
7. Documentation

**Success Metrics:**
- Recommendations accurate (>80% relevance)
- Analytics queries performant (<200ms)
- Automated workflows execute correctly
- Documentation complete
- End-to-end integration tests pass

---

## Part 9: File Structure

### New Files to Create

```
src/tracertm/
├── models/
│   ├── problem.py                 # Problem entity
│   ├── problem_activity.py        # Activity log
│   └── process.py                 # Process entity
│
├── repositories/
│   ├── problem_repository.py      # Problem CRUD
│   └── process_repository.py      # Process CRUD
│
├── services/
│   ├── problem_service.py         # Problem business logic
│   ├── root_cause_analysis_service.py  # RCA workflows
│   ├── process_service.py         # Process business logic
│   └── known_error_database_service.py # KEDB integration
│
├── schemas/
│   ├── problem.py                 # Problem Pydantic schemas
│   └── process.py                 # Process Pydantic schemas
│
└── api/
    └── routes/                    # (Update main.py with endpoints)
        ├── problems.py            # Problem endpoints
        └── processes.py           # Process endpoints

src/__tests__/
├── unit/
│   ├── models/
│   │   ├── test_problem_model.py
│   │   └── test_process_model.py
│   ├── repositories/
│   │   ├── test_problem_repository.py
│   │   └── test_process_repository.py
│   └── services/
│       ├── test_problem_service.py
│       ├── test_rca_service.py
│       └── test_process_service.py
│
└── integration/
    ├── test_problem_workflow.py
    └── test_process_workflow.py

src/components/
├── problems/
│   ├── ProblemList.tsx
│   ├── ProblemDetail.tsx
│   ├── ProblemModal.tsx
│   ├── ProblemStatusBadge.tsx
│   ├── ProblemSeverityBadge.tsx
│   ├── RCAModal.tsx
│   ├── FiveWhysForm.tsx
│   ├── FishboneForm.tsx
│   ├── KnownErrorModal.tsx
│   ├── ProblemActivityLog.tsx
│   └── index.ts
│
├── processes/
│   ├── ProcessList.tsx
│   ├── ProcessDetail.tsx
│   ├── ProcessModal.tsx
│   ├── ProcessActivationDialog.tsx
│   ├── BPMNDiagram.tsx
│   ├── SwimlaneEditor.tsx
│   ├── ProcessStageBuilder.tsx
│   ├── ProcessVersionHistory.tsx
│   └── index.ts

src/hooks/
├── useProblem.ts
├── useProblemFilters.ts
├── useProcess.ts
├── useProcessFilters.ts
├── useRCA.ts
└── index.ts

src/services/api/
├── problemsApi.ts
├── processesApi.ts
├── rcaApi.ts
└── index.ts

src/types/
├── problem.ts
├── process.ts
└── rca.ts

src/stores/
├── problemStore.ts
└── processStore.ts
```

---

## Part 10: Testing Strategy

### Unit Tests

```python
# File: tests/unit/services/test_problem_service.py

import pytest
from tracertm.services.problem_service import ProblemService
from tracertm.models.problem import Problem


@pytest.mark.asyncio
async def test_create_problem(session):
    """Test problem creation."""
    service = ProblemService(session)
    problem = await service.create_problem(
        project_id="proj-1",
        title="System unavailable",
        category="availability",
        severity="critical",
    )

    assert problem.id
    assert problem.status == "open"
    assert problem.created_at


@pytest.mark.asyncio
async def test_status_transition_valid(session):
    """Test valid status transition."""
    service = ProblemService(session)
    problem = await service.create_problem(
        project_id="proj-1",
        title="Test",
        category="test",
    )

    updated = await service.transition_status(
        problem_id=problem.id,
        project_id="proj-1",
        new_status="in_investigation",
    )

    assert updated.status == "in_investigation"


@pytest.mark.asyncio
async def test_status_transition_invalid(session):
    """Test invalid status transition."""
    service = ProblemService(session)
    problem = await service.create_problem(
        project_id="proj-1",
        title="Test",
        category="test",
    )

    with pytest.raises(ValueError):
        await service.transition_status(
            problem_id=problem.id,
            project_id="proj-1",
            new_status="invalid_status",
        )
```

### Integration Tests

```python
# File: tests/integration/test_problem_workflow.py

import pytest
from tracertm.services.problem_service import ProblemService
from tracertm.services.root_cause_analysis_service import RootCauseAnalysisService


@pytest.mark.asyncio
async def test_complete_problem_workflow(session):
    """Test complete problem lifecycle."""
    problem_service = ProblemService(session)
    rca_service = RootCauseAnalysisService(session)

    # 1. Create problem
    problem = await problem_service.create_problem(
        project_id="proj-1",
        title="Database connection pool exhausted",
        category="performance",
        severity="high",
    )

    # 2. Investigate
    await problem_service.transition_status(
        problem.id,
        "proj-1",
        "in_investigation",
    )

    # 3. Perform RCA
    problem = await rca_service.perform_5_whys(
        problem_id=problem.id,
        project_id="proj-1",
        initial_problem="Why are connections exhausted?",
        questions_answers=[
            {"why": "Why?", "because": "Application not releasing connections"},
            {"why": "Why?", "because": "Connection timeout too long"},
            {"why": "Why?", "because": "Poor configuration"},
        ],
    )

    # 4. Identify workaround
    await problem_service.update_problem(
        problem.id,
        "proj-1",
        workaround="Restart application service",
    )

    # 5. Transition to awaiting fix
    await problem_service.transition_status(
        problem.id,
        "proj-1",
        "awaiting_fix",
    )

    # 6. Verify final state
    final = await problem_service.get_by_id(problem.id, "proj-1")
    assert final.status == "awaiting_fix"
    assert final.root_cause is not None
    assert final.workaround is not None
```

---

## Part 11: Migration Strategy

### Database Migrations

```python
# File: src/tracertm/migrations/add_problems_and_processes.py

from alembic import op
import sqlalchemy as sa


def upgrade():
    """Create Problem and Process tables."""

    # Create problems table
    op.create_table(
        'problems',
        sa.Column('id', sa.String(255), primary_key=True),
        sa.Column('project_id', sa.String(255), sa.ForeignKey('projects.id', ondelete='CASCADE'), nullable=False),

        sa.Column('title', sa.String(500), nullable=False),
        sa.Column('description', sa.Text),
        sa.Column('problem_statement', sa.Text),

        sa.Column('status', sa.String(50), nullable=False, default='open'),
        sa.Column('category', sa.String(100), nullable=False),
        sa.Column('severity', sa.String(50), nullable=False, default='medium'),
        sa.Column('impact_level', sa.String(50), nullable=False, default='medium'),

        sa.Column('reported_by', sa.String(255)),
        sa.Column('owner', sa.String(255)),
        sa.Column('assignee', sa.String(255)),
        sa.Column('parent_problem_id', sa.String(255), sa.ForeignKey('problems.id')),

        sa.Column('reported_at', sa.DateTime(timezone=True)),
        sa.Column('first_occurrence', sa.DateTime(timezone=True)),
        sa.Column('last_occurrence', sa.DateTime(timezone=True)),
        sa.Column('resolved_at', sa.DateTime(timezone=True)),

        sa.Column('affected_systems', sa.JSON, nullable=False, default=list),
        sa.Column('affected_users_count', sa.Integer),
        sa.Column('estimated_business_impact', sa.Text),

        sa.Column('root_cause', sa.Text),
        sa.Column('root_cause_analysis', sa.JSON, nullable=False, default=dict),
        sa.Column('workaround', sa.Text),
        sa.Column('permanent_fix', sa.Text),
        sa.Column('kedb_reference', sa.String(255)),

        sa.Column('problem_metadata', sa.JSON, nullable=False, default=dict),
        sa.Column('version', sa.Integer, nullable=False, default=1),

        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('deleted_at', sa.DateTime(timezone=True)),
    )

    op.create_index('idx_problems_project_status', 'problems', ['project_id', 'status'])
    op.create_index('idx_problems_project_category', 'problems', ['project_id', 'category'])
    op.create_index('idx_problems_severity', 'problems', ['project_id', 'severity'])
    op.create_index('idx_problems_owner', 'problems', ['project_id', 'owner'])

    # Create problem_activities table
    op.create_table(
        'problem_activities',
        sa.Column('id', sa.String(255), primary_key=True),
        sa.Column('problem_id', sa.String(255), sa.ForeignKey('problems.id', ondelete='CASCADE'), nullable=False),

        sa.Column('activity_type', sa.String(50), nullable=False),
        sa.Column('actor', sa.String(255)),
        sa.Column('action_description', sa.Text, nullable=False),

        sa.Column('previous_state', sa.JSON, nullable=False, default=dict),
        sa.Column('new_state', sa.JSON, nullable=False, default=dict),
        sa.Column('metadata', sa.JSON, nullable=False, default=dict),

        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_index('idx_problem_activities_problem', 'problem_activities', ['problem_id'])
    op.create_index('idx_problem_activities_type', 'problem_activities', ['activity_type'])

    # Create processes table
    op.create_table(
        'processes',
        sa.Column('id', sa.String(255), primary_key=True),
        sa.Column('project_id', sa.String(255), sa.ForeignKey('projects.id', ondelete='CASCADE'), nullable=False),

        sa.Column('name', sa.String(500), nullable=False),
        sa.Column('description', sa.Text),

        sa.Column('category', sa.String(100), nullable=False),
        sa.Column('status', sa.String(50), nullable=False, default='draft'),
        sa.Column('version', sa.Integer, nullable=False, default=1),
        sa.Column('version_notes', sa.Text),
        sa.Column('is_current_version', sa.Boolean, nullable=False, default=True),
        sa.Column('parent_process_id', sa.String(255), sa.ForeignKey('processes.id')),

        sa.Column('owner', sa.String(255)),
        sa.Column('stakeholders', sa.JSON, nullable=False, default=list),

        sa.Column('stages', sa.JSON, nullable=False, default=list),
        sa.Column('bpmn_definition', sa.JSON, nullable=False, default=dict),
        sa.Column('swimlanes', sa.JSON, nullable=False, default=list),

        sa.Column('entry_criteria', sa.Text),
        sa.Column('exit_criteria', sa.Text),

        sa.Column('sla_duration_hours', sa.Integer),
        sa.Column('target_cycle_time_minutes', sa.Integer),

        sa.Column('documentation_url', sa.String(500)),
        sa.Column('runbook', sa.Text),

        sa.Column('process_metadata', sa.JSON, nullable=False, default=dict),

        sa.Column('activated_at', sa.DateTime(timezone=True)),
        sa.Column('deprecated_at', sa.DateTime(timezone=True)),

        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('deleted_at', sa.DateTime(timezone=True)),
    )

    op.create_index('idx_processes_project_status', 'processes', ['project_id', 'status'])
    op.create_index('idx_processes_project_category', 'processes', ['project_id', 'category'])
    op.create_index('idx_processes_owner', 'processes', ['project_id', 'owner'])


def downgrade():
    """Drop Problem and Process tables."""
    op.drop_table('problem_activities')
    op.drop_table('problems')
    op.drop_table('processes')
```

---

## Part 12: Success Criteria & Validation

### MVP Validation (Phase 1)

- [ ] Problem creation works with all required fields
- [ ] Status transitions follow state machine rules
- [ ] Invalid transitions are rejected
- [ ] Activity log entries created on state changes
- [ ] List view displays all problems with filtering
- [ ] Detail view shows complete problem information
- [ ] Soft delete functionality works
- [ ] Optimistic locking prevents conflicts
- [ ] API endpoints return correct HTTP status codes
- [ ] Permissions/ownership validated

### Enhanced Validation (Phase 2)

- [ ] Process creation with stages and swimlanes
- [ ] Version management transitions correctly
- [ ] Activation requires valid entry/exit criteria
- [ ] BPMN JSON generation is valid
- [ ] Swimlane diagrams render properly
- [ ] Version history is maintained
- [ ] Current version filtering works

### RCA Validation (Phase 3)

- [ ] 5 Whys analysis captures all questions/answers
- [ ] Fishbone factors are correctly categorized
- [ ] RCA findings are stored in root_cause_analysis field
- [ ] KEDB links are created correctly
- [ ] Impact assessment calculations are accurate

### Performance Targets

- [ ] Problem list query: <100ms (1000 items)
- [ ] Problem detail query: <50ms
- [ ] Status transition: <100ms
- [ ] Create problem: <200ms
- [ ] List processes with filtering: <100ms

---

## Part 13: Rollback & Mitigation

### Rollback Procedures

**If Problem entity causes issues:**
1. Disable Problem endpoints in API
2. Run database downgrade migration
3. Remove Problem components from UI
4. Roll back to previous commit
5. Notify users of status via status page

**If Process entity causes issues:**
1. Set all active processes to deprecated
2. Disable Process endpoints in API
3. Run database downgrade migration
4. Remove Process components from UI

**Data Recovery:**
- Maintain backups before each phase
- Soft deletes allow recovery of deleted data
- Activity logs provide audit trail
- Version control for process definitions

---

## Part 14: Documentation Roadmap

### Required Documentation

1. **API Documentation** (OpenAPI/Swagger)
   - Problem endpoints with examples
   - Process endpoints with examples
   - RCA workflow documentation
   - Error codes and handling

2. **Frontend Developer Guide**
   - Component prop specifications
   - Hook usage examples
   - State management patterns
   - Type definitions

3. **Backend Developer Guide**
   - Model relationships
   - Repository patterns
   - Service layer architecture
   - Testing guidelines

4. **User Guide**
   - Problem creation workflow
   - RCA tools usage
   - Process definition steps
   - BPMN visualization

5. **Administrator Guide**
   - Database management
   - Performance tuning
   - Backup/restore procedures
   - User permissions

---

## Summary

This implementation plan provides a complete blueprint for adding Problem and Process modeling to TraceRTM while maintaining architectural consistency with the existing codebase. The phased approach allows for iterative validation and reduces risk, while the hybrid model strategy balances specialization with backward compatibility.

**Key Strengths of This Approach:**
- Leverages existing patterns (repositories, JSONB metadata, soft deletes)
- Specialized entities for complex workflows
- Clear state machines prevent invalid transitions
- Comprehensive activity logging for audit trails
- RCA tools support evidence-based problem resolution
- BPMN support enables visual process documentation
- Version control for process definitions
- Extensible through metadata fields

**Next Steps:**
1. Review and approve design decisions
2. Create database migrations
3. Implement Phase 1 (MVP) entities and APIs
4. Build frontend components in parallel
5. Write and execute tests
6. Deploy to staging environment
7. Gather user feedback before Phase 2

