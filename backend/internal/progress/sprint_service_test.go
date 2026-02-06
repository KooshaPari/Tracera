//go:build !integration

package progress

import (
	"context"
	"errors"
	"testing"
	"time"

	"github.com/google/uuid"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

// mockSprintRepo implements SprintRepository for testing
type mockSprintRepo struct {
	sprint     *Sprint
	sprints    []Sprint
	itemIDs    []uuid.UUID
	burndown   []BurndownDataPoint
	err        error
	addBurnErr error
}

func (m *mockSprintRepo) CreateSprint(_ context.Context, sprint *Sprint) (*Sprint, error) {
	if m.err != nil {
		return nil, m.err
	}
	return sprint, nil
}

func (m *mockSprintRepo) GetSprintByID(_ context.Context, _ uuid.UUID) (*Sprint, error) {
	return m.sprint, m.err
}

func (m *mockSprintRepo) GetSprintsByProject(_ context.Context, _ uuid.UUID) ([]Sprint, error) {
	return m.sprints, m.err
}

func (m *mockSprintRepo) GetActiveSprint(_ context.Context, _ uuid.UUID) (*Sprint, error) {
	return m.sprint, m.err
}

func (m *mockSprintRepo) UpdateSprint(_ context.Context, sprint *Sprint) (*Sprint, error) {
	if m.err != nil {
		return nil, m.err
	}
	return sprint, nil
}
func (m *mockSprintRepo) DeleteSprint(_ context.Context, _ uuid.UUID) error { return m.err }
func (m *mockSprintRepo) AddItemToSprint(_ context.Context, _, _ uuid.UUID) error {
	return m.err
}

func (m *mockSprintRepo) RemoveItemFromSprint(_ context.Context, _, _ uuid.UUID) error {
	return m.err
}

func (m *mockSprintRepo) GetSprintItems(_ context.Context, _ uuid.UUID) ([]uuid.UUID, error) {
	return m.itemIDs, m.err
}

func (m *mockSprintRepo) AddBurndownData(_ context.Context, _ uuid.UUID, _ *BurndownDataPoint) error {
	return m.addBurnErr
}

func (m *mockSprintRepo) GetBurndownData(_ context.Context, _ uuid.UUID) ([]BurndownDataPoint, error) {
	return m.burndown, m.err
}

func TestNewSprintService(t *testing.T) {
	repo := &mockSprintRepo{}
	svc := NewSprintService(repo, nil)
	require.NotNil(t, svc)
}

func TestSprintService_CreateSprint(t *testing.T) {
	repo := &mockSprintRepo{}
	svc := NewSprintService(repo, nil)

	req := &CreateSprintRequest{
		Name:      "Sprint 1",
		Slug:      "sprint-1",
		StartDate: time.Now(),
		EndDate:   time.Now().AddDate(0, 0, 14),
	}

	result, err := svc.CreateSprint(context.Background(), uuid.New(), req)
	require.NoError(t, err)
	require.NotNil(t, result)
	assert.Equal(t, "Sprint 1", result.Name)
	assert.Equal(t, SprintPlanning, result.Status)
	assert.Equal(t, HealthUnknown, result.Health)
	assert.NotNil(t, result.Metadata)
}

func TestSprintService_CreateSprint_Error(t *testing.T) {
	repo := &mockSprintRepo{err: errors.New("fail")}
	svc := NewSprintService(repo, nil)

	req := &CreateSprintRequest{
		Name:      "S1",
		Slug:      "s1",
		StartDate: time.Now(),
		EndDate:   time.Now().AddDate(0, 0, 7),
	}

	result, err := svc.CreateSprint(context.Background(), uuid.New(), req)
	require.Error(t, err)
	assert.Nil(t, result)
}

func TestSprintService_GetSprint(t *testing.T) {
	id := uuid.New()
	repo := &mockSprintRepo{sprint: &Sprint{ID: id, Name: "S1"}}
	svc := NewSprintService(repo, nil)

	result, err := svc.GetSprint(context.Background(), id)
	require.NoError(t, err)
	assert.Equal(t, id, result.ID)
}

func TestSprintService_GetSprints(t *testing.T) {
	repo := &mockSprintRepo{sprints: []Sprint{{Name: "A"}, {Name: "B"}}}
	svc := NewSprintService(repo, nil)

	result, err := svc.GetSprints(context.Background(), uuid.New())
	require.NoError(t, err)
	assert.Len(t, result, 2)
}

func TestSprintService_UpdateSprint(t *testing.T) {
	id := uuid.New()
	repo := &mockSprintRepo{
		sprint: &Sprint{
			ID:            id,
			Name:          "Old",
			Slug:          "old",
			Status:        SprintPlanning,
			PlannedPoints: 20,
		},
	}
	svc := NewSprintService(repo, nil)

	newName := "Updated"
	newStatus := SprintActive
	completedPts := 5
	req := &UpdateSprintRequest{
		Name:            &newName,
		Status:          &newStatus,
		CompletedPoints: &completedPts,
	}

	result, err := svc.UpdateSprint(context.Background(), id, req)
	require.NoError(t, err)
	assert.Equal(t, "Updated", result.Name)
	assert.Equal(t, SprintActive, result.Status)
	assert.Equal(t, 5, result.CompletedPoints)
	assert.Equal(t, 15, result.RemainingPoints) // 20 - 5
}

func TestSprintService_DeleteSprint(t *testing.T) {
	id := uuid.New()
	repo := &mockSprintRepo{sprint: &Sprint{ID: id}}
	svc := NewSprintService(repo, nil)

	err := svc.DeleteSprint(context.Background(), id)
	require.NoError(t, err)
}

func TestSprintService_DeleteSprint_NotFound(t *testing.T) {
	repo := &mockSprintRepo{err: errors.New("not found")}
	svc := NewSprintService(repo, nil)

	err := svc.DeleteSprint(context.Background(), uuid.New())
	require.Error(t, err)
}

func TestSprintService_AddItemToSprint(t *testing.T) {
	repo := &mockSprintRepo{}
	svc := NewSprintService(repo, nil)

	err := svc.AddItemToSprint(context.Background(), uuid.New(), uuid.New())
	assert.NoError(t, err)
}

func TestSprintService_RemoveItemFromSprint(t *testing.T) {
	repo := &mockSprintRepo{}
	svc := NewSprintService(repo, nil)

	err := svc.RemoveItemFromSprint(context.Background(), uuid.New(), uuid.New())
	assert.NoError(t, err)
}

func TestSprintService_CloseSprint(t *testing.T) {
	id := uuid.New()
	repo := &mockSprintRepo{sprint: &Sprint{ID: id, Status: SprintActive}}
	svc := NewSprintService(repo, nil)

	err := svc.CloseSprint(context.Background(), id)
	require.NoError(t, err)
}

func TestSprintService_GetActiveSprint(t *testing.T) {
	repo := &mockSprintRepo{sprint: &Sprint{Status: SprintActive}}
	svc := NewSprintService(repo, nil)

	result, err := svc.GetActiveSprint(context.Background(), uuid.New())
	require.NoError(t, err)
	assert.Equal(t, SprintActive, result.Status)
}
