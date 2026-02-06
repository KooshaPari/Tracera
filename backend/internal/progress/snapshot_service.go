package progress

import (
	"context"
	"database/sql"
	"encoding/json"
	"time"

	"github.com/google/uuid"
)

// SnapshotRepository defines storage operations for progress snapshots
type SnapshotRepository interface {
	CreateSnapshot(ctx context.Context, snapshot *Snapshot) (*Snapshot, error)
	GetSnapshot(ctx context.Context, id uuid.UUID) (*Snapshot, error)
	GetSnapshotsByProject(ctx context.Context, projectID uuid.UUID, limit int) ([]Snapshot, error)
	GetSnapshotsByDateRange(ctx context.Context, projectID uuid.UUID, startDate, endDate time.Time) ([]Snapshot, error)
}

// SnapshotService provides business logic for progress snapshots
type SnapshotService interface {
	CreateSnapshot(ctx context.Context, projectID uuid.UUID, metrics *ProjectMetrics) (*Snapshot, error)
	GetSnapshot(ctx context.Context, id uuid.UUID) (*Snapshot, error)
	GetSnapshots(ctx context.Context, projectID uuid.UUID, limit int) ([]Snapshot, error)
	GetSnapshotTrend(ctx context.Context, projectID uuid.UUID, days int) ([]Snapshot, error)
	RecordDailySnapshot(ctx context.Context, projectID uuid.UUID) (*Snapshot, error)
}

type snapshotService struct {
	repo           SnapshotRepository
	metricsService MetricsService
	db             *sql.DB
}

// NewSnapshotService creates a new snapshot service
func NewSnapshotService(repo SnapshotRepository, metricsService MetricsService, db *sql.DB) SnapshotService {
	return &snapshotService{
		repo:           repo,
		metricsService: metricsService,
		db:             db,
	}
}

func (s *snapshotService) CreateSnapshot(ctx context.Context, projectID uuid.UUID, metrics *ProjectMetrics) (*Snapshot, error) {
	metricsJSON, err := json.Marshal(metrics)
	if err != nil {
		return nil, err
	}

	snapshot := &Snapshot{
		ID:           uuid.New(),
		ProjectID:    projectID,
		SnapshotDate: time.Now(),
		Metrics:      metricsJSON,
		CreatedAt:    time.Now(),
	}

	return s.repo.CreateSnapshot(ctx, snapshot)
}

func (s *snapshotService) GetSnapshot(ctx context.Context, id uuid.UUID) (*Snapshot, error) {
	return s.repo.GetSnapshot(ctx, id)
}

func (s *snapshotService) GetSnapshots(ctx context.Context, projectID uuid.UUID, limit int) ([]Snapshot, error) {
	return s.repo.GetSnapshotsByProject(ctx, projectID, limit)
}

func (s *snapshotService) GetSnapshotTrend(ctx context.Context, projectID uuid.UUID, days int) ([]Snapshot, error) {
	endDate := time.Now()
	startDate := endDate.AddDate(0, 0, -days)

	return s.repo.GetSnapshotsByDateRange(ctx, projectID, startDate, endDate)
}

func (s *snapshotService) RecordDailySnapshot(ctx context.Context, projectID uuid.UUID) (*Snapshot, error) {
	// Calculate current metrics
	metrics, err := s.metricsService.CalculateProjectMetrics(ctx, projectID)
	if err != nil {
		return nil, err
	}

	// Create snapshot
	return s.CreateSnapshot(ctx, projectID, metrics)
}
