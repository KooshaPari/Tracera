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

// mockMilestoneRepo implements MilestoneRepository for testing
type mockMilestoneRepo struct {
	milestone  *Milestone
	milestones []Milestone
	itemIDs    []uuid.UUID
	err        error
}

func (m *mockMilestoneRepo) CreateMilestone(_ context.Context, milestone *Milestone) (*Milestone, error) {
	if m.err != nil {
		return nil, m.err
	}
	return milestone, nil
}

func (m *mockMilestoneRepo) GetMilestoneByID(_ context.Context, _ uuid.UUID) (*Milestone, error) {
	return m.milestone, m.err
}

func (m *mockMilestoneRepo) GetMilestonesByProject(_ context.Context, _ uuid.UUID) ([]Milestone, error) {
	return m.milestones, m.err
}

func (m *mockMilestoneRepo) UpdateMilestone(_ context.Context, milestone *Milestone) (*Milestone, error) {
	if m.err != nil {
		return nil, m.err
	}
	return milestone, nil
}
func (m *mockMilestoneRepo) DeleteMilestone(_ context.Context, _ uuid.UUID) error { return m.err }
func (m *mockMilestoneRepo) GetMilestonesByParent(_ context.Context, _ uuid.UUID) ([]Milestone, error) {
	return m.milestones, m.err
}

func (m *mockMilestoneRepo) AddItemToMilestone(_ context.Context, _, _ uuid.UUID) error {
	return m.err
}

func (m *mockMilestoneRepo) RemoveItemFromMilestone(_ context.Context, _, _ uuid.UUID) error {
	return m.err
}

func (m *mockMilestoneRepo) GetMilestoneItems(_ context.Context, _ uuid.UUID) ([]uuid.UUID, error) {
	return m.itemIDs, m.err
}

func (m *mockMilestoneRepo) UpdateMilestoneRisk(_ context.Context, _ uuid.UUID, _ int, _ []RiskFactor) error {
	return m.err
}

func TestNewMilestoneService(t *testing.T) {
	repo := &mockMilestoneRepo{}
	svc := NewMilestoneService(repo, nil)
	require.NotNil(t, svc)
}

func TestMilestoneService_CreateMilestone(t *testing.T) {
	repo := &mockMilestoneRepo{}
	svc := NewMilestoneService(repo, nil)

	req := &CreateMilestoneRequest{
		Name:       "Test Milestone",
		Slug:       "test-milestone",
		TargetDate: time.Now().AddDate(0, 1, 0),
	}

	result, err := svc.CreateMilestone(context.Background(), uuid.New(), req)
	require.NoError(t, err)
	require.NotNil(t, result)
	assert.Equal(t, "Test Milestone", result.Name)
	assert.Equal(t, "test-milestone", result.Slug)
	assert.Equal(t, MilestoneNotStarted, result.Status)
	assert.Equal(t, HealthUnknown, result.Health)
	assert.NotEqual(t, uuid.Nil, result.ID)
}

func TestMilestoneService_CreateMilestone_RepoError(t *testing.T) {
	repo := &mockMilestoneRepo{err: errors.New("db error")}
	svc := NewMilestoneService(repo, nil)

	req := &CreateMilestoneRequest{
		Name:       "Test",
		Slug:       "test",
		TargetDate: time.Now(),
	}

	result, err := svc.CreateMilestone(context.Background(), uuid.New(), req)
	require.Error(t, err)
	assert.Nil(t, result)
}

func TestMilestoneService_GetMilestone(t *testing.T) {
	id := uuid.New()
	repo := &mockMilestoneRepo{
		milestone: &Milestone{ID: id, Name: "Test"},
	}
	svc := NewMilestoneService(repo, nil)

	result, err := svc.GetMilestone(context.Background(), id)
	require.NoError(t, err)
	assert.Equal(t, id, result.ID)
}

func TestMilestoneService_GetMilestones(t *testing.T) {
	repo := &mockMilestoneRepo{
		milestones: []Milestone{{Name: "A"}, {Name: "B"}},
	}
	svc := NewMilestoneService(repo, nil)

	result, err := svc.GetMilestones(context.Background(), uuid.New())
	require.NoError(t, err)
	assert.Len(t, result, 2)
}

func TestMilestoneService_GetMilestoneHierarchy(t *testing.T) {
	parentID := uuid.New()
	repo := &mockMilestoneRepo{
		milestones: []Milestone{
			{Name: "Root", ParentID: nil},
			{Name: "Child", ParentID: &parentID},
			{Name: "Root2", ParentID: nil},
		},
	}
	svc := NewMilestoneService(repo, nil)

	result, err := svc.GetMilestoneHierarchy(context.Background(), uuid.New())
	require.NoError(t, err)
	assert.Len(t, result, 2) // Only roots
}

func TestMilestoneService_UpdateMilestone(t *testing.T) {
	id := uuid.New()
	now := time.Now()
	repo := &mockMilestoneRepo{
		milestone: &Milestone{
			ID:         id,
			Name:       "Old Name",
			Slug:       "old-slug",
			TargetDate: now,
			Status:     MilestoneNotStarted,
		},
	}
	svc := NewMilestoneService(repo, nil)

	newName := "New Name"
	newSlug := "new-slug"
	newStatus := MilestoneInProgress
	req := &UpdateMilestoneRequest{
		Name:   &newName,
		Slug:   &newSlug,
		Status: &newStatus,
	}

	result, err := svc.UpdateMilestone(context.Background(), id, req)
	require.NoError(t, err)
	assert.Equal(t, "New Name", result.Name)
	assert.Equal(t, "new-slug", result.Slug)
	assert.Equal(t, MilestoneInProgress, result.Status)
}

func TestMilestoneService_DeleteMilestone(t *testing.T) {
	id := uuid.New()
	repo := &mockMilestoneRepo{
		milestone: &Milestone{ID: id, Name: "To Delete"},
	}
	svc := NewMilestoneService(repo, nil)

	err := svc.DeleteMilestone(context.Background(), id)
	require.NoError(t, err)
}

func TestMilestoneService_DeleteMilestone_NotFound(t *testing.T) {
	repo := &mockMilestoneRepo{err: errors.New("not found")}
	svc := NewMilestoneService(repo, nil)

	err := svc.DeleteMilestone(context.Background(), uuid.New())
	require.Error(t, err)
}

func TestMilestoneService_AddItemToMilestone(t *testing.T) {
	repo := &mockMilestoneRepo{}
	svc := NewMilestoneService(repo, nil)

	err := svc.AddItemToMilestone(context.Background(), uuid.New(), uuid.New())
	assert.NoError(t, err)
}

func TestMilestoneService_RemoveItemFromMilestone(t *testing.T) {
	repo := &mockMilestoneRepo{}
	svc := NewMilestoneService(repo, nil)

	err := svc.RemoveItemFromMilestone(context.Background(), uuid.New(), uuid.New())
	assert.NoError(t, err)
}

func TestMilestoneService_CalculateExpectedProgress(t *testing.T) {
	svc := &milestoneService{}

	t.Run("nil start date returns 0", func(t *testing.T) {
		m := &Milestone{TargetDate: time.Now().AddDate(0, 0, 10)}
		result := svc.calculateExpectedProgress(m)
		assert.InDelta(t, 0.0, result, 1e-9)
	})

	t.Run("past target returns 1.0", func(t *testing.T) {
		start := time.Now().AddDate(0, 0, -20)
		m := &Milestone{
			StartDate:  &start,
			TargetDate: time.Now().AddDate(0, 0, -1),
		}
		result := svc.calculateExpectedProgress(m)
		assert.InEpsilon(t, 1.0, result, 1e-9)
	})

	t.Run("before start returns 0.0", func(t *testing.T) {
		start := time.Now().AddDate(0, 0, 5)
		m := &Milestone{
			StartDate:  &start,
			TargetDate: time.Now().AddDate(0, 0, 15),
		}
		result := svc.calculateExpectedProgress(m)
		assert.InDelta(t, 0.0, result, 1e-9)
	})

	t.Run("midway returns approximately 0.5", func(t *testing.T) {
		start := time.Now().AddDate(0, 0, -10)
		m := &Milestone{
			StartDate:  &start,
			TargetDate: time.Now().AddDate(0, 0, 10),
		}
		result := svc.calculateExpectedProgress(m)
		assert.InDelta(t, 0.5, result, 0.05)
	})
}
