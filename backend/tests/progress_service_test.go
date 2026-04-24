package tests

import (
	"context"
	"database/sql"
	"testing"
	"time"

	"github.com/google/uuid"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"

	"github.com/kooshapari/tracertm-backend/internal/progress"
)

// MockMilestoneRepository implements progress.MilestoneRepository
type MockMilestoneRepository struct {
	milestones map[uuid.UUID]*progress.Milestone
	items      map[uuid.UUID][]uuid.UUID
}

func NewMockMilestoneRepository() *MockMilestoneRepository {
	return &MockMilestoneRepository{
		milestones: make(map[uuid.UUID]*progress.Milestone),
		items:      make(map[uuid.UUID][]uuid.UUID),
	}
}

func (m *MockMilestoneRepository) CreateMilestone(ctx context.Context, milestone *progress.Milestone) (*progress.Milestone, error) {
	m.milestones[milestone.ID] = milestone
	return milestone, nil
}

func (m *MockMilestoneRepository) GetMilestoneByID(ctx context.Context, id uuid.UUID) (*progress.Milestone, error) {
	if milestone, ok := m.milestones[id]; ok {
		return milestone, nil
	}
	return nil, sql.ErrNoRows
}

func (m *MockMilestoneRepository) GetMilestonesByProject(ctx context.Context, projectID uuid.UUID) ([]progress.Milestone, error) {
	var milestones []progress.Milestone
	for _, milestone := range m.milestones {
		if milestone.ProjectID == projectID {
			milestones = append(milestones, *milestone)
		}
	}
	return milestones, nil
}

func (m *MockMilestoneRepository) UpdateMilestone(ctx context.Context, milestone *progress.Milestone) (*progress.Milestone, error) {
	m.milestones[milestone.ID] = milestone
	return milestone, nil
}

func (m *MockMilestoneRepository) DeleteMilestone(ctx context.Context, id uuid.UUID) error {
	delete(m.milestones, id)
	return nil
}

func (m *MockMilestoneRepository) GetMilestonesByParent(ctx context.Context, parentID uuid.UUID) ([]progress.Milestone, error) {
	var milestones []progress.Milestone
	for _, milestone := range m.milestones {
		if milestone.ParentID != nil && *milestone.ParentID == parentID {
			milestones = append(milestones, *milestone)
		}
	}
	return milestones, nil
}

func (m *MockMilestoneRepository) AddItemToMilestone(ctx context.Context, milestoneID, itemID uuid.UUID) error {
	m.items[milestoneID] = append(m.items[milestoneID], itemID)
	return nil
}

func (m *MockMilestoneRepository) RemoveItemFromMilestone(ctx context.Context, milestoneID, itemID uuid.UUID) error {
	items := m.items[milestoneID]
	for i, id := range items {
		if id == itemID {
			m.items[milestoneID] = append(items[:i], items[i+1:]...)
			break
		}
	}
	return nil
}

func (m *MockMilestoneRepository) GetMilestoneItems(ctx context.Context, milestoneID uuid.UUID) ([]uuid.UUID, error) {
	return m.items[milestoneID], nil
}

func (m *MockMilestoneRepository) UpdateMilestoneRisk(ctx context.Context, milestoneID uuid.UUID, riskScore int, riskFactors []progress.RiskFactor) error {
	if milestone, ok := m.milestones[milestoneID]; ok {
		milestone.RiskScore = riskScore
		milestone.RiskFactors = riskFactors
	}
	return nil
}

func TestMilestoneService_CreateMilestone(t *testing.T) {
	repo := NewMockMilestoneRepository()
	service := progress.NewMilestoneService(repo, nil)

	projectID := uuid.New()
	targetDate := time.Now().AddDate(0, 0, 30)

	req := &progress.CreateMilestoneRequest{
		Name:       "v1.0 Release",
		Slug:       "v1-0-release",
		TargetDate: targetDate,
	}

	milestone, err := service.CreateMilestone(context.Background(), projectID, req)
	require.NoError(t, err)
	assert.NotNil(t, milestone)
	assert.Equal(t, "v1.0 Release", milestone.Name)
	assert.Equal(t, projectID, milestone.ProjectID)
	assert.Equal(t, progress.MilestoneNotStarted, milestone.Status)
	assert.Equal(t, progress.HealthUnknown, milestone.Health)
}

func TestMilestoneService_UpdateMilestone(t *testing.T) {
	repo := NewMockMilestoneRepository()
	service := progress.NewMilestoneService(repo, nil)

	projectID := uuid.New()
	targetDate := time.Now().AddDate(0, 0, 30)

	// Create initial milestone
	milestone := &progress.Milestone{
		ID:         uuid.New(),
		ProjectID:  projectID,
		Name:       "v1.0 Release",
		Slug:       "v1-0-release",
		TargetDate: targetDate,
		Status:     progress.MilestoneNotStarted,
		Health:     progress.HealthUnknown,
		CreatedAt:  time.Now(),
		UpdatedAt:  time.Now(),
	}
	repo.CreateMilestone(context.Background(), milestone)

	// Update milestone
	newName := "v1.0 Final Release"
	newStatus := progress.MilestoneInProgress
	req := &progress.UpdateMilestoneRequest{
		Name:   &newName,
		Status: &newStatus,
	}

	updated, err := service.UpdateMilestone(context.Background(), milestone.ID, req)
	require.NoError(t, err)
	assert.Equal(t, newName, updated.Name)
	assert.Equal(t, newStatus, updated.Status)
}

func TestMilestoneService_GetMilestoneHierarchy(t *testing.T) {
	repo := NewMockMilestoneRepository()
	service := progress.NewMilestoneService(repo, nil)

	projectID := uuid.New()
	targetDate := time.Now().AddDate(0, 0, 30)

	// Create parent milestone
	parent := &progress.Milestone{
		ID:         uuid.New(),
		ProjectID:  projectID,
		Name:       "Q1 Release",
		Slug:       "q1-release",
		TargetDate: targetDate,
		Status:     progress.MilestoneInProgress,
		Health:     progress.HealthGreen,
		CreatedAt:  time.Now(),
		UpdatedAt:  time.Now(),
	}
	repo.CreateMilestone(context.Background(), parent)

	// Create child milestone
	child := &progress.Milestone{
		ID:         uuid.New(),
		ProjectID:  projectID,
		ParentID:   &parent.ID,
		Name:       "Feature A",
		Slug:       "feature-a",
		TargetDate: targetDate,
		Status:     progress.MilestoneNotStarted,
		Health:     progress.HealthUnknown,
		CreatedAt:  time.Now(),
		UpdatedAt:  time.Now(),
	}
	repo.CreateMilestone(context.Background(), child)

	// Get hierarchy (should return only parent)
	roots, err := service.GetMilestoneHierarchy(context.Background(), projectID)
	require.NoError(t, err)
	assert.Len(t, roots, 1)
	assert.Equal(t, parent.ID, roots[0].ID)
}

func TestMilestoneService_AddRemoveItems(t *testing.T) {
	repo := NewMockMilestoneRepository()
	service := progress.NewMilestoneService(repo, nil)

	milestoneID := uuid.New()
	itemID1 := uuid.New()
	itemID2 := uuid.New()

	// Add items
	err := service.AddItemToMilestone(context.Background(), milestoneID, itemID1)
	require.NoError(t, err)

	err = service.AddItemToMilestone(context.Background(), milestoneID, itemID2)
	require.NoError(t, err)

	// Get items
	items, err := repo.GetMilestoneItems(context.Background(), milestoneID)
	require.NoError(t, err)
	assert.Len(t, items, 2)

	// Remove item
	err = service.RemoveItemFromMilestone(context.Background(), milestoneID, itemID1)
	require.NoError(t, err)

	items, err = repo.GetMilestoneItems(context.Background(), milestoneID)
	require.NoError(t, err)
	assert.Len(t, items, 1)
	assert.Equal(t, itemID2, items[0])
}

// Test milestone progress calculation
func TestMilestoneService_ComputeRiskFactors(t *testing.T) {
	repo := NewMockMilestoneRepository()
	service := progress.NewMilestoneService(repo, nil)

	projectID := uuid.New()
	// Create overdue milestone
	targetDate := time.Now().AddDate(0, 0, -5) // 5 days overdue
	milestone := &progress.Milestone{
		ID:         uuid.New(),
		ProjectID:  projectID,
		Name:       "Late Milestone",
		Slug:       "late-milestone",
		TargetDate: targetDate,
		Status:     progress.MilestoneInProgress,
		Health:     progress.HealthUnknown,
		CreatedAt:  time.Now(),
		UpdatedAt:  time.Now(),
	}
	repo.CreateMilestone(context.Background(), milestone)

	// Compute risk factors
	factors, score, err := service.ComputeRiskFactors(context.Background(), milestone.ID)
	require.NoError(t, err)
	assert.Greater(t, score, 0)
	assert.Greater(t, len(factors), 0)

	// Should have overdue risk
	hasOverdueRisk := false
	for _, factor := range factors {
		if factor.Type == "overdue" {
			hasOverdueRisk = true
			break
		}
	}
	assert.True(t, hasOverdueRisk)
}

// MockSprintRepository implements progress.SprintRepository
type MockSprintRepository struct {
	sprints      map[uuid.UUID]*progress.Sprint
	items        map[uuid.UUID][]uuid.UUID
	burndownData map[uuid.UUID][]progress.BurndownDataPoint
}

func NewMockSprintRepository() *MockSprintRepository {
	return &MockSprintRepository{
		sprints:      make(map[uuid.UUID]*progress.Sprint),
		items:        make(map[uuid.UUID][]uuid.UUID),
		burndownData: make(map[uuid.UUID][]progress.BurndownDataPoint),
	}
}

func (m *MockSprintRepository) CreateSprint(ctx context.Context, sprint *progress.Sprint) (*progress.Sprint, error) {
	m.sprints[sprint.ID] = sprint
	return sprint, nil
}

func (m *MockSprintRepository) GetSprintByID(ctx context.Context, id uuid.UUID) (*progress.Sprint, error) {
	if sprint, ok := m.sprints[id]; ok {
		return sprint, nil
	}
	return nil, sql.ErrNoRows
}

func (m *MockSprintRepository) GetSprintsByProject(ctx context.Context, projectID uuid.UUID) ([]progress.Sprint, error) {
	var sprints []progress.Sprint
	for _, sprint := range m.sprints {
		if sprint.ProjectID == projectID {
			sprints = append(sprints, *sprint)
		}
	}
	return sprints, nil
}

func (m *MockSprintRepository) GetActiveSprint(ctx context.Context, projectID uuid.UUID) (*progress.Sprint, error) {
	for _, sprint := range m.sprints {
		if sprint.ProjectID == projectID && sprint.Status == progress.SprintActive {
			return sprint, nil
		}
	}
	return nil, sql.ErrNoRows
}

func (m *MockSprintRepository) UpdateSprint(ctx context.Context, sprint *progress.Sprint) (*progress.Sprint, error) {
	m.sprints[sprint.ID] = sprint
	return sprint, nil
}

func (m *MockSprintRepository) DeleteSprint(ctx context.Context, id uuid.UUID) error {
	delete(m.sprints, id)
	return nil
}

func (m *MockSprintRepository) AddItemToSprint(ctx context.Context, sprintID, itemID uuid.UUID) error {
	m.items[sprintID] = append(m.items[sprintID], itemID)
	return nil
}

func (m *MockSprintRepository) RemoveItemFromSprint(ctx context.Context, sprintID, itemID uuid.UUID) error {
	items := m.items[sprintID]
	for i, id := range items {
		if id == itemID {
			m.items[sprintID] = append(items[:i], items[i+1:]...)
			break
		}
	}
	return nil
}

func (m *MockSprintRepository) GetSprintItems(ctx context.Context, sprintID uuid.UUID) ([]uuid.UUID, error) {
	return m.items[sprintID], nil
}

func (m *MockSprintRepository) AddBurndownData(ctx context.Context, sprintID uuid.UUID, data *progress.BurndownDataPoint) error {
	m.burndownData[sprintID] = append(m.burndownData[sprintID], *data)
	return nil
}

func (m *MockSprintRepository) GetBurndownData(ctx context.Context, sprintID uuid.UUID) ([]progress.BurndownDataPoint, error) {
	return m.burndownData[sprintID], nil
}

func TestSprintService_CreateSprint(t *testing.T) {
	repo := NewMockSprintRepository()
	service := progress.NewSprintService(repo, nil)

	projectID := uuid.New()
	startDate := time.Now()
	endDate := time.Now().AddDate(0, 0, 14)

	req := &progress.CreateSprintRequest{
		Name:      "Sprint 1",
		Slug:      "sprint-1",
		StartDate: startDate,
		EndDate:   endDate,
	}

	sprint, err := service.CreateSprint(context.Background(), projectID, req)
	require.NoError(t, err)
	assert.NotNil(t, sprint)
	assert.Equal(t, "Sprint 1", sprint.Name)
	assert.Equal(t, projectID, sprint.ProjectID)
	assert.Equal(t, progress.SprintPlanning, sprint.Status)
}

func TestSprintService_UpdateSprint(t *testing.T) {
	repo := NewMockSprintRepository()
	service := progress.NewSprintService(repo, nil)

	projectID := uuid.New()
	startDate := time.Now()
	endDate := time.Now().AddDate(0, 0, 14)

	sprint := &progress.Sprint{
		ID:        uuid.New(),
		ProjectID: projectID,
		Name:      "Sprint 1",
		Slug:      "sprint-1",
		StartDate: startDate,
		EndDate:   endDate,
		Status:    progress.SprintPlanning,
		Health:    progress.HealthUnknown,
		CreatedAt: time.Now(),
		UpdatedAt: time.Now(),
	}
	repo.CreateSprint(context.Background(), sprint)

	newStatus := progress.SprintActive
	newPoints := 50
	req := &progress.UpdateSprintRequest{
		Status:        &newStatus,
		PlannedPoints: &newPoints,
	}

	updated, err := service.UpdateSprint(context.Background(), sprint.ID, req)
	require.NoError(t, err)
	assert.Equal(t, newStatus, updated.Status)
	assert.Equal(t, newPoints, updated.PlannedPoints)
}

func TestSprintService_CloseSprint(t *testing.T) {
	repo := NewMockSprintRepository()
	service := progress.NewSprintService(repo, nil)

	projectID := uuid.New()
	startDate := time.Now().AddDate(0, 0, -14)
	endDate := time.Now()

	sprint := &progress.Sprint{
		ID:        uuid.New(),
		ProjectID: projectID,
		Name:      "Sprint 1",
		Slug:      "sprint-1",
		StartDate: startDate,
		EndDate:   endDate,
		Status:    progress.SprintActive,
		Health:    progress.HealthGreen,
		CreatedAt: startDate,
		UpdatedAt: time.Now(),
	}
	repo.CreateSprint(context.Background(), sprint)

	err := service.CloseSprint(context.Background(), sprint.ID)
	require.NoError(t, err)

	closed, err := repo.GetSprintByID(context.Background(), sprint.ID)
	require.NoError(t, err)
	assert.Equal(t, progress.SprintCompleted, closed.Status)
	assert.NotNil(t, closed.CompletedAt)
}
