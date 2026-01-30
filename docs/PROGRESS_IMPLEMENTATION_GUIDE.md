# Progress Tracking Implementation Guide

## Quick Start

This guide helps you integrate and use the milestone and sprint tracking system.

## Step 1: Database Setup

### Run Migration

```bash
bun run migrate
```

This creates 8 new tables:
- `milestones` - Milestone tracking
- `milestone_items` - Milestone-item associations
- `sprints` - Sprint management
- `sprint_items` - Sprint-item associations
- `burndown_data` - Daily burndown tracking
- `progress_snapshots` - Point-in-time metrics
- `velocity_history` - Historical velocity data
- `milestone_dependencies` - Milestone relationships

### Verify Tables

```bash
psql $DATABASE_URL -c "
  SELECT tablename FROM pg_tables
  WHERE tablename LIKE 'milestone%' OR tablename LIKE 'sprint%' OR tablename LIKE 'burndown%' OR tablename LIKE 'progress%' OR tablename LIKE 'velocity%'
  ORDER BY tablename
"
```

Expected output:
```
       tablename
------------------------
 burndown_data
 milestone_dependencies
 milestone_items
 milestones
 progress_snapshots
 sprint_items
 sprints
 velocity_history
```

## Step 2: Backend Integration

### Register Services

In your main application setup:

```go
// In your main.go or app initialization

// Create repositories (implement based on your database layer)
milestoneRepo := repositories.NewMilestoneRepository(db)
sprintRepo := repositories.NewSprintRepository(db)
snapshotRepo := repositories.NewSnapshotRepository(db)

// Create services
milestoneService := progress.NewMilestoneService(milestoneRepo, db)
sprintService := progress.NewSprintService(sprintRepo, db)
metricsService := progress.NewMetricsService(db)
snapshotService := progress.NewSnapshotService(snapshotRepo, metricsService, db)

// Create handler
progressHandler := progress.NewHandler(
    milestoneService,
    sprintService,
    metricsService,
    snapshotService,
)

// Register routes (adjust base path as needed)
progressHandler.RegisterRoutes(router, "/api/v1/projects/{projectId}/progress")
```

### Implement Repositories

You need to implement the repository interfaces. Example structure:

```go
// In internal/repository/milestone_repository.go

type MilestoneRepository struct {
    db *sql.DB
}

func (r *MilestoneRepository) CreateMilestone(ctx context.Context, m *progress.Milestone) (*progress.Milestone, error) {
    query := `
        INSERT INTO milestones (id, project_id, name, slug, target_date, status, health, created_at, updated_at)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
        RETURNING *
    `
    err := r.db.QueryRowContext(ctx, query,
        m.ID, m.ProjectID, m.Name, m.Slug, m.TargetDate,
        m.Status, m.Health, m.CreatedAt, m.UpdatedAt,
    ).Scan(&m)
    return m, err
}

// Implement other methods similarly...
```

### Setup Scheduled Tasks

For daily snapshots and burndown recording:

```go
// In your scheduler setup

// Record daily snapshots
scheduler.Every(24).Hours().Do(func() {
    projects, _ := getActiveProjects(context.Background())
    for _, project := range projects {
        _, err := snapshotService.RecordDailySnapshot(context.Background(), project.ID)
        if err != nil {
            log.Printf("Error recording snapshot for project %s: %v", project.ID, err)
        }
    }
})

// Record daily burndown
scheduler.Every(24).Hours().Do(func() {
    sprints, _ := getActiveSprints(context.Background())
    for _, sprint := range sprints {
        err := sprintService.RecordBurndown(context.Background(), sprint.ID)
        if err != nil {
            log.Printf("Error recording burndown for sprint %s: %v", sprint.ID, err)
        }
    }
})

// Update milestone health
scheduler.Every(12).Hours().Do(func() {
    projects, _ := getActiveProjects(context.Background())
    for _, project := range projects {
        milestones, _ := milestoneService.GetMilestones(context.Background(), project.ID)
        for _, milestone := range milestones {
            milestoneService.UpdateMilestoneHealth(context.Background(), milestone.ID)
        }
    }
})
```

## Step 3: Frontend Integration

### Import Components

```typescript
import { ProgressDashboard } from '@/components/temporal/ProgressDashboard';
import { BurndownChart } from '@/components/temporal/BurndownChart';
import { VelocityChart } from '@/components/temporal/VelocityChart';
import { ProgressRing, ProgressBar, LinearProgress } from '@/components/temporal/ProgressRing';
```

### Fetch Data from API

```typescript
// Example in a React component

const [milestones, setMilestones] = useState<Milestone[]>([]);
const [sprints, setSprints] = useState<Sprint[]>([]);
const [metrics, setMetrics] = useState<ProjectMetrics | null>(null);
const [snapshots, setSnapshots] = useState<ProgressSnapshot[]>([]);
const [loading, setLoading] = useState(true);

useEffect(() => {
  const fetchData = async () => {
    try {
      const [milestonesRes, sprintsRes, metricsRes, snapshotsRes] = await Promise.all([
        fetch(`/api/v1/projects/${projectId}/progress/milestones`),
        fetch(`/api/v1/projects/${projectId}/progress/sprints`),
        fetch(`/api/v1/projects/${projectId}/progress/metrics`),
        fetch(`/api/v1/projects/${projectId}/progress/snapshots`),
      ]);

      const milestonesData = await milestonesRes.json();
      const sprintsData = await sprintsRes.json();
      const metricsData = await metricsRes.json();
      const snapshotsData = await snapshotsRes.json();

      setMilestones(milestonesData);
      setSprints(sprintsData);
      setMetrics(metricsData);
      setSnapshots(snapshotsData);
    } finally {
      setLoading(false);
    }
  };

  fetchData();
}, [projectId]);
```

### Render Dashboard

```typescript
if (loading || !metrics) {
  return <div>Loading...</div>;
}

return (
  <ProgressDashboard
    projectId={projectId}
    milestones={milestones}
    sprints={sprints}
    metrics={metrics}
    snapshots={snapshots}
    onMilestoneClick={(milestone) => {
      // Handle milestone selection
      console.log('Selected milestone:', milestone);
    }}
    onSprintClick={(sprint) => {
      // Handle sprint selection
      console.log('Selected sprint:', sprint);
    }}
  />
);
```

## Step 4: API Usage Examples

### Create a Milestone

```bash
curl -X POST http://localhost:8000/api/v1/projects/proj-123/progress/milestones \
  -H "Content-Type: application/json" \
  -d '{
    "name": "v1.0 Release",
    "slug": "v1-0-release",
    "targetDate": "2026-06-30T00:00:00Z",
    "description": "Initial production release",
    "objective": "Ship core features to customers"
  }'
```

### Create a Sprint

```bash
curl -X POST http://localhost:8000/api/v1/projects/proj-123/progress/sprints \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Sprint 1",
    "slug": "sprint-1",
    "startDate": "2026-02-10T00:00:00Z",
    "endDate": "2026-02-24T00:00:00Z",
    "goal": "Complete authentication system"
  }'
```

### Add Item to Milestone

```bash
curl -X POST http://localhost:8000/api/v1/projects/proj-123/progress/milestones/mile-123/items/item-456 \
  -H "Content-Type: application/json"
```

### Record Burndown

```bash
curl -X POST http://localhost:8000/api/v1/projects/proj-123/progress/sprints/sprint-123/burndown \
  -H "Content-Type: application/json"
```

### Get Project Metrics

```bash
curl http://localhost:8000/api/v1/projects/proj-123/progress/metrics
```

### Get Velocity History

```bash
curl http://localhost:8000/api/v1/projects/proj-123/progress/metrics/velocity/history
```

### Record Daily Snapshot

```bash
curl -X POST http://localhost:8000/api/v1/projects/proj-123/progress/snapshots \
  -H "Content-Type: application/json"
```

## Step 5: Testing

### Run Backend Tests

```bash
# Test services
go test ./internal/progress -v

# Test with coverage
go test ./internal/progress -cover -coverprofile=coverage.out
go tool cover -html=coverage.out

# Specific test
go test -run TestMilestoneService_CreateMilestone -v
```

### Run Frontend Tests

```bash
# Run all progress component tests
bun test ProgressDashboard.test ProgressRing.test

# Run with coverage
bun test --coverage

# Watch mode
bun test --watch
```

## Step 6: Monitoring and Maintenance

### Check Health of Recent Milestones

```bash
SELECT name, status, health, risk_score, target_date
FROM milestones
WHERE project_id = 'proj-123'
  AND deleted_at IS NULL
ORDER BY target_date;
```

### Check Sprint Progress

```bash
SELECT name, status, planned_points, completed_points,
       (completed_points::float / planned_points * 100)::int as completion_pct
FROM sprints
WHERE project_id = 'proj-123'
  AND deleted_at IS NULL
ORDER BY start_date DESC;
```

### Review Recent Snapshots

```bash
SELECT snapshot_date, metrics
FROM progress_snapshots
WHERE project_id = 'proj-123'
ORDER BY snapshot_date DESC
LIMIT 10;
```

### Check Velocity Trend

```bash
SELECT period_label, planned_points, completed_points, velocity
FROM velocity_history
WHERE project_id = 'proj-123'
ORDER BY period_start DESC
LIMIT 12;
```

## Configuration

### Environment Variables

```bash
# Optional: Adjust snapshot retention
PROGRESS_SNAPSHOT_RETENTION_DAYS=90  # Keep 3 months of snapshots

# Optional: Adjust burndown history
PROGRESS_BURNDOWN_RETENTION_DAYS=365  # Keep 1 year of burndown data

# Optional: Velocity history window
PROGRESS_VELOCITY_PERIODS=52  # Track 52 periods (1 year)
```

## Performance Tips

1. **Snapshots**: Run daily snapshot recording in off-peak hours
2. **Indexes**: Ensure all indexes are created (migration handles this)
3. **Cleanup**: Archive or delete old data after 1 year
4. **Caching**: Cache metrics for 1 hour in the frontend
5. **Queries**: Use burndown data for trending, not raw items

## Troubleshooting

### Migration Fails

Ensure your database user has permissions:
```sql
GRANT USAGE ON SCHEMA public TO your_user;
GRANT CREATE ON SCHEMA public TO your_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO your_user;
```

### Services Not Responding

Verify repository implementations match the interfaces in `handler.go`.

### Tests Failing

Ensure test database is clean:
```bash
# Reset test database
psql $TEST_DATABASE_URL -c "DROP SCHEMA IF EXISTS public CASCADE; CREATE SCHEMA public;"
```

### Frontend Components Not Rendering

Check that all imports are correct and types are matching the API responses.

## Next Steps

1. Integrate with your webhook system to update milestones when items change
2. Create automated alerts for health changes (red status)
3. Setup dashboard visualizations for executive reporting
4. Implement burndown forecast improvements using linear regression
5. Add custom metric definitions for your team

## Support

For issues or questions:
1. Check `/docs/PROGRESS_TRACKING.md` for detailed documentation
2. Review test files for usage examples
3. Check `/backend/internal/progress/README.md` for service details

## Additional Resources

- Type Definitions: `/frontend/packages/types/src/progress.ts`
- Database Schema: `/backend/internal/db/migrations/20250210000000_create_progress_tables.sql`
- API Documentation: `/docs/PROGRESS_TRACKING.md#api-endpoints`
- Component Guide: `/frontend/apps/web/src/components/temporal/README.md`
