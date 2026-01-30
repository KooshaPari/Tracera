# Progress Tracking and Sprint Management System

## Overview

This document describes the comprehensive milestone and sprint tracking system with a progress dashboard for monitoring project execution, team velocity, and health indicators.

## Architecture

### Database Schema

#### Core Tables

**milestones**
- `id` (uuid): Primary key
- `project_id` (uuid): Foreign key to projects
- `parent_id` (uuid): Optional parent milestone for hierarchy
- `name` (varchar): Milestone name
- `slug` (varchar): URL-friendly identifier
- `description` (text): Detailed description
- `objective` (text): Success criteria
- `start_date` (timestamp): Planned start
- `target_date` (timestamp): Target completion date
- `actual_date` (timestamp): Actual completion date
- `status` (varchar): not_started, in_progress, at_risk, blocked, completed, cancelled
- `health` (varchar): green, yellow, red, unknown
- `risk_score` (int): 0-100 risk assessment
- `risk_factors` (jsonb): Array of risk factors
- `owner_id` (uuid): Milestone owner
- `tags` (jsonb): Array of tags
- `metadata` (jsonb): Custom metadata

**milestone_items**
- Join table linking milestones to items
- Composite primary key: (milestone_id, item_id)

**sprints**
- `id` (uuid): Primary key
- `project_id` (uuid): Foreign key to projects
- `name` (varchar): Sprint name (e.g., "Sprint 23")
- `slug` (varchar): URL-friendly identifier
- `goal` (text): Sprint objective
- `start_date` (timestamp): Sprint start
- `end_date` (timestamp): Sprint end
- `status` (varchar): planning, active, completed, cancelled
- `health` (varchar): green, yellow, red, unknown
- `planned_capacity` (int): Story points or hours
- `actual_capacity` (int): Adjusted capacity
- `planned_points` (int): Total points in sprint
- `completed_points` (int): Completed points
- `remaining_points` (int): Points not yet done
- `added_points` (int): Scope added during sprint
- `removed_points` (int): Scope removed during sprint
- `metadata` (jsonb): Custom data

**sprint_items**
- Join table linking sprints to items
- Composite primary key: (sprint_id, item_id)

**burndown_data**
- `id` (uuid): Primary key
- `sprint_id` (uuid): Foreign key to sprints
- `recorded_date` (timestamp): When this data was recorded
- `remaining_points` (int): Remaining work
- `ideal_points` (int): Ideal burndown line
- `completed_points` (int): Cumulative completed
- `added_points` (int): Scope added on this date

**progress_snapshots**
- `id` (uuid): Primary key
- `project_id` (uuid): Foreign key to projects
- `snapshot_date` (timestamp): When snapshot was taken
- `metrics` (jsonb): ProjectMetrics data

**velocity_history**
- `id` (uuid): Primary key
- `project_id` (uuid): Foreign key to projects
- `period_start` (timestamp): Period start date
- `period_end` (timestamp): Period end date
- `period_label` (varchar): Period name (e.g., "Sprint 23")
- `planned_points` (int): Planned capacity
- `completed_points` (int): Actually completed
- `velocity` (int): Points completed per period

**milestone_dependencies**
- `dependent_id` (uuid): Milestone that depends
- `dependency_id` (uuid): Milestone being depended on
- `relationship_type` (varchar): depends_on, blocks

## Services

### MilestoneService

Provides CRUD and business logic for milestones.

**Methods:**
- `CreateMilestone(projectID, request)` - Create new milestone
- `GetMilestone(id)` - Retrieve single milestone
- `GetMilestones(projectID)` - List all milestones in project
- `GetMilestoneHierarchy(projectID)` - Get root milestones with tree structure
- `UpdateMilestone(id, request)` - Update milestone details
- `DeleteMilestone(id)` - Soft delete milestone
- `AddItemToMilestone(milestoneID, itemID)` - Associate item with milestone
- `RemoveItemFromMilestone(milestoneID, itemID)` - Unassociate item
- `GetMilestoneProgress(milestoneID)` - Calculate progress metrics
- `UpdateMilestoneHealth(milestoneID)` - Recompute health status
- `ComputeRiskFactors(milestoneID)` - Identify and score risks

**Risk Assessment:**
- Overdue milestones: +30 points
- Behind schedule: +20 points
- Blocked items: +25 points
- Low velocity: +20 points
- Scope creep: +15 points

Risk score capped at 100 points.

### SprintService

Manages sprint execution and tracking.

**Methods:**
- `CreateSprint(projectID, request)` - Create new sprint
- `GetSprint(id)` - Retrieve sprint
- `GetSprints(projectID)` - List sprints
- `GetActiveSprint(projectID)` - Get currently active sprint
- `UpdateSprint(id, request)` - Update sprint status/points
- `CloseSprint(id)` - Mark sprint complete
- `AddItemToSprint(sprintID, itemID)` - Add item to sprint
- `RemoveItemFromSprint(sprintID, itemID)` - Remove item from sprint
- `RecordBurndown(sprintID)` - Record daily burndown
- `UpdateSprintHealth(sprintID)` - Recompute health
- `DeleteSprint(id)` - Soft delete sprint

**Health Calculation:**
- Red: Actual < Ideal - 20%
- Yellow: Ideal - 20% ≤ Actual < Ideal - 10%
- Green: Actual ≥ Ideal - 10%

### MetricsService

Calculates project metrics and trends.

**Methods:**
- `CalculateProjectMetrics(projectID)` - Get overall project metrics
- `CalculateVelocity(projectID, periods)` - Average velocity over N periods
- `GetVelocityHistory(projectID)` - Historical velocity data
- `CalculateCycleTime(projectID)` - Average days from start to done
- `EstimateCompletion(sprintID)` - Project sprint completion date
- `RecordVelocity(sprintID)` - Record sprint velocity

**Metrics Included:**
- Item counts by status, priority, type
- Completed items this/last week
- Velocity (items/day)
- Blocked item count
- At-risk item count
- Overdue item count
- Test/doc/trace coverage
- Average cycle time and lead time

### SnapshotService

Captures point-in-time progress data for trending.

**Methods:**
- `CreateSnapshot(projectID, metrics)` - Create new snapshot
- `GetSnapshot(id)` - Retrieve snapshot
- `GetSnapshots(projectID, limit)` - List recent snapshots
- `GetSnapshotTrend(projectID, days)` - Get trend over date range
- `RecordDailySnapshot(projectID)` - Auto-record today's metrics

## Frontend Components

### ProgressDashboard

Main dashboard component displaying overall project health.

**Props:**
```typescript
interface ProgressDashboardProps {
  projectId: string;
  milestones: Milestone[];
  sprints: Sprint[];
  snapshots: ProgressSnapshot[];
  metrics: ProjectMetrics;
  onMilestoneClick?: (milestone: Milestone) => void;
  onSprintClick?: (sprint: Sprint) => void;
}
```

**Features:**
- Summary cards (total, at-risk, blockers, velocity)
- Milestone tree visualization with progress
- Sprint timeline with progress bars
- Active sprint highlighted
- Health status distribution
- Recent progress snapshots

### BurndownChart

Sprint burndown visualization.

**Props:**
```typescript
interface BurndownChartProps {
  sprint: Sprint;
  data?: BurndownDataPoint[];
  height?: number;
}
```

**Features:**
- Ideal vs actual burndown lines
- Daily burndown rate indicators
- Points breakdown
- Scope change visibility

### VelocityChart

Team velocity trending over time.

**Props:**
```typescript
interface VelocityChartProps {
  projectId: string;
  history?: VelocityDataPoint[];
  height?: number;
}
```

**Features:**
- Planned vs completed points
- Velocity trend (improving/stable/declining)
- Average velocity calculations
- Best sprint indicator
- Multiple period view

### ProgressRing

Circular progress indicator for milestones.

**Props:**
```typescript
interface ProgressRingProps {
  percentage: number;
  radius?: number;
  strokeWidth?: number;
  size?: 'sm' | 'md' | 'lg';
  animated?: boolean;
  showLabel?: boolean;
  color?: string;
}
```

**Features:**
- Color coding by percentage (green/blue/yellow/red)
- Animated transitions
- Customizable sizing
- Optional percentage label

### ProgressBar

Linear progress indicator.

**Props:**
```typescript
interface ProgressBarProps {
  percentage: number;
  height?: 'sm' | 'md' | 'lg';
  showLabel?: boolean;
  color?: string;
  animated?: boolean;
}
```

### LinearProgress

Progress with label and value display.

```typescript
interface LinearProgressProps {
  value: number;
  max: number;
  label?: string;
  color?: string;
  showLabel?: boolean;
}
```

## API Endpoints

### Milestone Endpoints

```
GET    /api/v1/projects/{id}/milestones
POST   /api/v1/projects/{id}/milestones
GET    /api/v1/projects/{id}/milestones/{id}
PUT    /api/v1/projects/{id}/milestones/{id}
DELETE /api/v1/projects/{id}/milestones/{id}
GET    /api/v1/projects/{id}/milestones/{id}/progress
POST   /api/v1/projects/{id}/milestones/{id}/health
POST   /api/v1/projects/{id}/milestones/{id}/items/{itemId}
DELETE /api/v1/projects/{id}/milestones/{id}/items/{itemId}
```

### Sprint Endpoints

```
GET    /api/v1/projects/{id}/sprints
POST   /api/v1/projects/{id}/sprints
GET    /api/v1/projects/{id}/sprints/{id}
PUT    /api/v1/projects/{id}/sprints/{id}
DELETE /api/v1/projects/{id}/sprints/{id}
POST   /api/v1/projects/{id}/sprints/{id}/close
POST   /api/v1/projects/{id}/sprints/{id}/burndown
POST   /api/v1/projects/{id}/sprints/{id}/health
POST   /api/v1/projects/{id}/sprints/{id}/items/{itemId}
DELETE /api/v1/projects/{id}/sprints/{id}/items/{itemId}
```

### Metrics Endpoints

```
GET /api/v1/projects/{id}/progress/metrics
GET /api/v1/projects/{id}/progress/metrics/velocity
GET /api/v1/projects/{id}/progress/metrics/velocity/history
GET /api/v1/projects/{id}/progress/metrics/cycle-time
```

### Snapshot Endpoints

```
GET    /api/v1/projects/{id}/progress/snapshots
POST   /api/v1/projects/{id}/progress/snapshots
GET    /api/v1/projects/{id}/progress/snapshots/{id}
```

## Types

### Enums

**MilestoneStatus:** not_started | in_progress | at_risk | blocked | completed | cancelled

**SprintStatus:** planning | active | completed | cancelled

**HealthStatus:** green | yellow | red | unknown

**RiskFactorType:** blocked_dependency | overdue | scope_creep | low_velocity | resource_constraint | technical_risk | external_dependency

### Key Interfaces

See `/frontend/packages/types/src/progress.ts` for complete type definitions.

## Testing

### Backend Tests

Located in `/backend/tests/`:
- `progress_service_test.go` - Service logic tests
- `progress_metrics_test.go` - Metrics calculation tests

Test coverage:
- CRUD operations for milestones and sprints
- Progress calculation
- Risk factor computation
- Health status updates
- Velocity tracking
- Burndown rate calculation

### Frontend Tests

Located in `/frontend/apps/web/src/__tests__/components/`:
- `ProgressDashboard.test.tsx` - Dashboard rendering and interactions
- `ProgressRing.test.tsx` - Progress indicator tests

Test coverage:
- Component rendering
- Callback handlers
- Milestone/sprint selection
- Progress calculations
- Health status display
- Edge cases (empty lists, overdue items)

## Usage Examples

### Creating a Milestone

```typescript
const response = await fetch(`/api/v1/projects/${projectId}/milestones`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    name: 'v1.0 Release',
    slug: 'v1-0-release',
    targetDate: '2026-06-30T00:00:00Z',
    description: 'Initial production release'
  })
});
```

### Creating a Sprint

```typescript
const response = await fetch(`/api/v1/projects/${projectId}/sprints`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    name: 'Sprint 1',
    slug: 'sprint-1',
    startDate: '2026-02-10T00:00:00Z',
    endDate: '2026-02-24T00:00:00Z',
    goal: 'Complete core features'
  })
});
```

### Recording Burndown

```typescript
const response = await fetch(
  `/api/v1/projects/${projectId}/sprints/${sprintId}/burndown`,
  { method: 'POST' }
);
```

### Getting Metrics

```typescript
const response = await fetch(
  `/api/v1/projects/${projectId}/progress/metrics`
);
const metrics = await response.json();
```

## Best Practices

1. **Daily Snapshots**: Record daily snapshots for trend analysis
2. **Burndown Tracking**: Record burndown daily for accurate forecasting
3. **Risk Management**: Review risk factors weekly and take mitigation actions
4. **Health Updates**: Update health status as items progress
5. **Velocity Tracking**: Record sprint velocity for better planning
6. **Goal Setting**: Set clear sprint goals and success criteria
7. **Regular Reviews**: Review metrics weekly to identify patterns

## Performance Considerations

- Metrics calculations are cached daily via snapshots
- Burndown data is indexed by sprint_id and recorded_date
- Milestone queries use parent_id index for hierarchy traversal
- Velocity history limited to last 52 periods (1 year)
- Consider archiving old milestones/sprints after 1 year

## Future Enhancements

- Predictive analytics for completion forecasting
- Anomaly detection for unusual patterns
- Custom metric definitions
- Historical comparison reports
- Drill-down analysis by team/component
- Automated health alerts
- Custom sprint templates
- Resource capacity planning
