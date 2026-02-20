//go:build !integration

package progress

import (
	"context"
	"encoding/json"
	"errors"
	"testing"
	"time"

	"github.com/google/uuid"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

// mockSnapshotRepo implements SnapshotRepository
type mockSnapshotRepo struct {
	snapshot  *Snapshot
	snapshots []Snapshot
	err       error
}

func (m *mockSnapshotRepo) CreateSnapshot(_ context.Context, snapshot *Snapshot) (*Snapshot, error) {
	if m.err != nil {
		return nil, m.err
	}
	return snapshot, nil
}

func (m *mockSnapshotRepo) GetSnapshot(_ context.Context, _ uuid.UUID) (*Snapshot, error) {
	return m.snapshot, m.err
}

func (m *mockSnapshotRepo) GetSnapshotsByProject(_ context.Context, _ uuid.UUID, _ int) ([]Snapshot, error) {
	return m.snapshots, m.err
}

func (m *mockSnapshotRepo) GetSnapshotsByDateRange(_ context.Context, _ uuid.UUID, _, _ time.Time) ([]Snapshot, error) {
	return m.snapshots, m.err
}

func TestNewSnapshotService(t *testing.T) {
	svc := NewSnapshotService(&mockSnapshotRepo{}, &mockMetricsService{}, nil)
	require.NotNil(t, svc)
}

func TestSnapshotService_CreateSnapshot(t *testing.T) {
	repo := &mockSnapshotRepo{}
	svc := NewSnapshotService(repo, &mockMetricsService{}, nil)

	metrics := &ProjectMetrics{TotalItems: 10}
	result, err := svc.CreateSnapshot(context.Background(), uuid.New(), metrics)
	require.NoError(t, err)
	require.NotNil(t, result)
	assert.NotEqual(t, uuid.Nil, result.ID)
	assert.False(t, result.SnapshotDate.IsZero())

	// Verify metrics are serialized
	var decoded ProjectMetrics
	err = json.Unmarshal(result.Metrics, &decoded)
	require.NoError(t, err)
	assert.Equal(t, 10, decoded.TotalItems)
}

func TestSnapshotService_CreateSnapshot_RepoError(t *testing.T) {
	repo := &mockSnapshotRepo{err: errors.New("db error")}
	svc := NewSnapshotService(repo, &mockMetricsService{}, nil)

	result, err := svc.CreateSnapshot(context.Background(), uuid.New(), &ProjectMetrics{})
	require.Error(t, err)
	assert.Nil(t, result)
}

func TestSnapshotService_GetSnapshot(t *testing.T) {
	id := uuid.New()
	repo := &mockSnapshotRepo{snapshot: &Snapshot{ID: id}}
	svc := NewSnapshotService(repo, &mockMetricsService{}, nil)

	result, err := svc.GetSnapshot(context.Background(), id)
	require.NoError(t, err)
	assert.Equal(t, id, result.ID)
}

func TestSnapshotService_GetSnapshots(t *testing.T) {
	repo := &mockSnapshotRepo{snapshots: []Snapshot{{}, {}}}
	svc := NewSnapshotService(repo, &mockMetricsService{}, nil)

	result, err := svc.GetSnapshots(context.Background(), uuid.New(), 10)
	require.NoError(t, err)
	assert.Len(t, result, 2)
}

func TestSnapshotService_GetSnapshotTrend(t *testing.T) {
	repo := &mockSnapshotRepo{snapshots: []Snapshot{{}, {}, {}}}
	svc := NewSnapshotService(repo, &mockMetricsService{}, nil)

	result, err := svc.GetSnapshotTrend(context.Background(), uuid.New(), 30)
	require.NoError(t, err)
	assert.Len(t, result, 3)
}

func TestSnapshotService_RecordDailySnapshot(t *testing.T) {
	repo := &mockSnapshotRepo{}
	metricsSvc := &mockMetricsService{
		metrics: &ProjectMetrics{TotalItems: 42},
	}
	svc := NewSnapshotService(repo, metricsSvc, nil)

	result, err := svc.RecordDailySnapshot(context.Background(), uuid.New())
	require.NoError(t, err)
	require.NotNil(t, result)
}

func TestSnapshotService_RecordDailySnapshot_MetricsError(t *testing.T) {
	repo := &mockSnapshotRepo{}
	metricsSvc := &mockMetricsService{err: errors.New("metrics fail")}
	svc := NewSnapshotService(repo, metricsSvc, nil)

	result, err := svc.RecordDailySnapshot(context.Background(), uuid.New())
	require.Error(t, err)
	assert.Nil(t, result)
}
