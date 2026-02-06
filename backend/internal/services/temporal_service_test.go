package services

import (
	"context"
	"errors"
	"testing"
	"time"

	"github.com/kooshapari/tracertm-backend/internal/models"
	"github.com/kooshapari/tracertm-backend/internal/repository"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/mock"
	"github.com/stretchr/testify/require"
)

// Mock repositories
type mockBranchRepository struct {
	mock.Mock
}

func (m *mockBranchRepository) Create(ctx context.Context, branch interface{}) error {
	args := m.Called(ctx, branch)
	return args.Error(0)
}

func (m *mockBranchRepository) GetByID(ctx context.Context, id string) (interface{}, error) {
	args := m.Called(ctx, id)
	return args.Get(0), args.Error(1)
}

func (m *mockBranchRepository) ListByProject(ctx context.Context, projectID string) ([]interface{}, error) {
	args := m.Called(ctx, projectID)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	return args.Get(0).([]interface{}), args.Error(1)
}

func (m *mockBranchRepository) Update(ctx context.Context, branch interface{}) error {
	args := m.Called(ctx, branch)
	return args.Error(0)
}

func (m *mockBranchRepository) Delete(ctx context.Context, id string) error {
	args := m.Called(ctx, id)
	return args.Error(0)
}

type mockVersionRepository struct {
	mock.Mock
}

func (m *mockVersionRepository) Create(ctx context.Context, version interface{}) error {
	args := m.Called(ctx, version)
	return args.Error(0)
}

func (m *mockVersionRepository) GetByID(ctx context.Context, id string) (interface{}, error) {
	args := m.Called(ctx, id)
	return args.Get(0), args.Error(1)
}

func (m *mockVersionRepository) ListByBranch(ctx context.Context, branchID string) ([]interface{}, error) {
	args := m.Called(ctx, branchID)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	return args.Get(0).([]interface{}), args.Error(1)
}

func (m *mockVersionRepository) Update(ctx context.Context, version interface{}) error {
	args := m.Called(ctx, version)
	return args.Error(0)
}

func (m *mockVersionRepository) Delete(ctx context.Context, id string) error {
	args := m.Called(ctx, id)
	return args.Error(0)
}

type mockItemVersionRepository struct {
	mock.Mock
}

func (m *mockItemVersionRepository) Create(ctx context.Context, snapshot interface{}) error {
	args := m.Called(ctx, snapshot)
	return args.Error(0)
}

func (m *mockItemVersionRepository) GetByItemAndVersion(ctx context.Context, itemID, versionID string) (interface{}, error) {
	args := m.Called(ctx, itemID, versionID)
	return args.Get(0), args.Error(1)
}

func (m *mockItemVersionRepository) GetHistory(ctx context.Context, itemID, branchID string) ([]interface{}, error) {
	args := m.Called(ctx, itemID, branchID)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	return args.Get(0).([]interface{}), args.Error(1)
}

func (m *mockItemVersionRepository) Update(ctx context.Context, snapshot interface{}) error {
	args := m.Called(ctx, snapshot)
	return args.Error(0)
}

func (m *mockItemVersionRepository) Delete(ctx context.Context, id string) error {
	args := m.Called(ctx, id)
	return args.Error(0)
}

type mockAlternativeRepository struct {
	mock.Mock
}

func (m *mockAlternativeRepository) Create(ctx context.Context, alt interface{}) error {
	args := m.Called(ctx, alt)
	return args.Error(0)
}

func (m *mockAlternativeRepository) GetByID(ctx context.Context, id string) (interface{}, error) {
	args := m.Called(ctx, id)
	return args.Get(0), args.Error(1)
}

func (m *mockAlternativeRepository) ListByBase(ctx context.Context, baseItemID string) ([]interface{}, error) {
	args := m.Called(ctx, baseItemID)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	return args.Get(0).([]interface{}), args.Error(1)
}

func (m *mockAlternativeRepository) Update(ctx context.Context, alt interface{}) error {
	args := m.Called(ctx, alt)
	return args.Error(0)
}

func (m *mockAlternativeRepository) Delete(ctx context.Context, id string) error {
	args := m.Called(ctx, id)
	return args.Error(0)
}

type mockMergeRepository struct {
	mock.Mock
}

func (m *mockMergeRepository) Create(ctx context.Context, mr interface{}) error {
	args := m.Called(ctx, mr)
	return args.Error(0)
}

func (m *mockMergeRepository) GetByID(ctx context.Context, id string) (interface{}, error) {
	args := m.Called(ctx, id)
	return args.Get(0), args.Error(1)
}

func (m *mockMergeRepository) ListByProject(ctx context.Context, projectID string, status string) ([]interface{}, error) {
	args := m.Called(ctx, projectID, status)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	return args.Get(0).([]interface{}), args.Error(1)
}

func (m *mockMergeRepository) Update(ctx context.Context, mr interface{}) error {
	args := m.Called(ctx, mr)
	return args.Error(0)
}

func (m *mockMergeRepository) Delete(ctx context.Context, id string) error {
	args := m.Called(ctx, id)
	return args.Error(0)
}

type mockItemRepository struct {
	mock.Mock
}

func (m *mockItemRepository) Create(ctx context.Context, item *models.Item) error {
	args := m.Called(ctx, item)
	return args.Error(0)
}

func (m *mockItemRepository) GetByID(ctx context.Context, id string) (*models.Item, error) {
	args := m.Called(ctx, id)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	return args.Get(0).(*models.Item), args.Error(1)
}

func (m *mockItemRepository) Update(ctx context.Context, item *models.Item) error {
	args := m.Called(ctx, item)
	return args.Error(0)
}

func (m *mockItemRepository) Delete(ctx context.Context, id string) error {
	args := m.Called(ctx, id)
	return args.Error(0)
}

func (m *mockItemRepository) GetByProjectID(ctx context.Context, projectID string) ([]*models.Item, error) {
	args := m.Called(ctx, projectID)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	return args.Get(0).([]*models.Item), args.Error(1)
}

func (m *mockItemRepository) List(ctx context.Context, filter repository.ItemFilter) ([]*models.Item, error) {
	args := m.Called(ctx, filter)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	return args.Get(0).([]*models.Item), args.Error(1)
}

func (m *mockItemRepository) Count(ctx context.Context, filter repository.ItemFilter) (int64, error) {
	args := m.Called(ctx, filter)
	return args.Get(0).(int64), args.Error(1)
}

// Tests
func TestCreateBranch(t *testing.T) {
	for _, tt := range createBranchCases() {
		t.Run(tt.name, func(t *testing.T) {
			runCreateBranchCase(t, tt)
		})
	}
}

func TestGetBranch(t *testing.T) {
	ctx := context.Background()
	expectedBranch := &VersionBranch{
		ID:        "branch-123",
		Name:      "main",
		ProjectID: "proj-123",
	}

	mockRepo := new(mockBranchRepository)
	mockRepo.On("GetByID", ctx, "branch-123").Return(expectedBranch, nil)

	service := NewTemporalService(
		mockRepo,
		new(mockVersionRepository),
		new(mockItemVersionRepository),
		new(mockAlternativeRepository),
		new(mockMergeRepository),
		nil,
		nil,
	)

	branch, err := service.GetBranch(ctx, "branch-123")
	require.NoError(t, err)
	assert.Equal(t, expectedBranch, branch)
}

func TestListBranches(t *testing.T) {
	ctx := context.Background()
	branches := []interface{}{
		&VersionBranch{ID: "b1", Name: "main", ProjectID: "proj-123"},
		&VersionBranch{ID: "b2", Name: "feature/test", ProjectID: "proj-123"},
	}

	mockRepo := new(mockBranchRepository)
	mockRepo.On("ListByProject", ctx, "proj-123").Return(branches, nil)

	service := NewTemporalService(
		mockRepo,
		new(mockVersionRepository),
		new(mockItemVersionRepository),
		new(mockAlternativeRepository),
		new(mockMergeRepository),
		nil,
		nil,
	)

	result, err := service.ListBranches(ctx, "proj-123")
	require.NoError(t, err)
	assert.Equal(t, len(branches), len(result))
}

func TestCreateVersion(t *testing.T) {
	ctx := context.Background()

	for _, tt := range createVersionCases(ctx) {
		t.Run(tt.name, func(t *testing.T) {
			runCreateVersionCase(ctx, t, tt)
		})
	}
}

type createBranchCase struct {
	name      string
	input     *VersionBranch
	setupMock func(*mockBranchRepository)
	wantErr   bool
	errMsg    string
}

type createVersionCase struct {
	name      string
	input     *Version
	setupMock func(*mockVersionRepository)
	wantErr   bool
}

func createBranchCases() []createBranchCase {
	return []createBranchCase{
		{
			name: "successful branch creation",
			input: &VersionBranch{
				Name:       "feature/payment-flow",
				ProjectID:  "proj-123",
				BranchType: "feature",
				Status:     "active",
			},
			setupMock: func(m *mockBranchRepository) {
				m.On("Create", mock.Anything, mock.MatchedBy(func(b *VersionBranch) bool {
					return b.Name == "feature/payment-flow" && b.ProjectID == "proj-123"
				})).Return(nil)
			},
		},
		{
			name:      "nil branch error",
			input:     nil,
			setupMock: func(_ *mockBranchRepository) {},
			wantErr:   true,
			errMsg:    "branch cannot be nil",
		},
		{
			name: "missing name error",
			input: &VersionBranch{
				ProjectID: "proj-123",
			},
			setupMock: func(_ *mockBranchRepository) {},
			wantErr:   true,
			errMsg:    "branch name and project_id are required",
		},
		{
			name: "repository error",
			input: &VersionBranch{
				Name:      "feature/test",
				ProjectID: "proj-123",
			},
			setupMock: func(m *mockBranchRepository) {
				m.On("Create", mock.Anything, mock.Anything).Return(errors.New("db error"))
			},
			wantErr: true,
			errMsg:  "failed to create branch",
		},
	}
}

func createVersionCases(ctx context.Context) []createVersionCase {
	return []createVersionCase{
		{
			name: "successful version creation",
			input: &Version{
				BranchID:  "branch-123",
				ProjectID: "proj-123",
				Message:   "Initial version",
				Status:    "draft",
			},
			setupMock: func(m *mockVersionRepository) {
				m.On("Create", ctx, mock.MatchedBy(func(v *Version) bool {
					return v.BranchID == "branch-123"
				})).Return(nil)
			},
		},
		{
			name:      "nil version error",
			input:     nil,
			setupMock: func(_ *mockVersionRepository) {},
			wantErr:   true,
		},
		{
			name: "missing required fields",
			input: &Version{
				BranchID: "branch-123",
			},
			setupMock: func(_ *mockVersionRepository) {},
			wantErr:   true,
		},
	}
}

func runCreateBranchCase(t *testing.T, tc createBranchCase) {
	mockRepo := new(mockBranchRepository)
	tc.setupMock(mockRepo)

	service := NewTemporalService(
		mockRepo,
		new(mockVersionRepository),
		new(mockItemVersionRepository),
		new(mockAlternativeRepository),
		new(mockMergeRepository),
		nil,
		nil,
	)

	_, err := service.CreateBranch(context.Background(), tc.input)
	if tc.wantErr {
		assert.Error(t, err)
		assert.Contains(t, err.Error(), tc.errMsg)
		return
	}
	assert.NoError(t, err)
}

func runCreateVersionCase(ctx context.Context, t *testing.T, tc createVersionCase) {
	mockVersionRepo := new(mockVersionRepository)
	tc.setupMock(mockVersionRepo)

	service := NewTemporalService(
		new(mockBranchRepository),
		mockVersionRepo,
		new(mockItemVersionRepository),
		new(mockAlternativeRepository),
		new(mockMergeRepository),
		nil,
		nil,
	)

	_, err := service.CreateVersion(ctx, tc.input)
	if tc.wantErr {
		assert.Error(t, err)
		return
	}
	assert.NoError(t, err)
}

func TestApproveVersion(t *testing.T) {
	ctx := context.Background()
	version := &Version{
		ID:     "v-123",
		Status: "draft",
	}

	mockRepo := new(mockVersionRepository)
	mockRepo.On("GetByID", ctx, "v-123").Return(version, nil)
	mockRepo.On("Update", ctx, mock.MatchedBy(func(v *Version) bool {
		return v.Status == "approved" && v.ApprovedBy == "user-123"
	})).Return(nil)

	service := NewTemporalService(
		new(mockBranchRepository),
		mockRepo,
		new(mockItemVersionRepository),
		new(mockAlternativeRepository),
		new(mockMergeRepository),
		nil,
		nil,
	)

	err := service.ApproveVersion(ctx, "v-123", "user-123")
	assert.NoError(t, err)
}

func TestRejectVersion(t *testing.T) {
	ctx := context.Background()
	version := &Version{
		ID:     "v-123",
		Status: "pending_review",
	}

	mockRepo := new(mockVersionRepository)
	mockRepo.On("GetByID", ctx, "v-123").Return(version, nil)
	mockRepo.On("Update", ctx, mock.MatchedBy(func(v *Version) bool {
		return v.Status == "rejected"
	})).Return(nil)

	service := NewTemporalService(
		new(mockBranchRepository),
		mockRepo,
		new(mockItemVersionRepository),
		new(mockAlternativeRepository),
		new(mockMergeRepository),
		nil,
		nil,
	)

	err := service.RejectVersion(ctx, "v-123", "Needs more work")
	assert.NoError(t, err)
}

func TestCreateAlternative(t *testing.T) {
	ctx := context.Background()
	alt := &ItemAlternative{
		ProjectID:         "proj-123",
		BaseItemID:        "item-1",
		AlternativeItemID: "item-2",
		Relationship:      "alternative_to",
	}

	mockRepo := new(mockAlternativeRepository)
	mockRepo.On("Create", ctx, mock.MatchedBy(func(a *ItemAlternative) bool {
		return a.BaseItemID == "item-1"
	})).Return(nil)

	service := NewTemporalService(
		new(mockBranchRepository),
		new(mockVersionRepository),
		new(mockItemVersionRepository),
		mockRepo,
		new(mockMergeRepository),
		nil,
		nil,
	)

	_, err := service.CreateAlternative(ctx, alt)
	assert.NoError(t, err)
}

func TestSelectAlternative(t *testing.T) {
	ctx := context.Background()
	alt := &ItemAlternative{
		ID:       "alt-123",
		IsChosen: false,
	}

	mockRepo := new(mockAlternativeRepository)
	mockRepo.On("GetByID", ctx, "alt-123").Return(alt, nil)
	mockRepo.On("Update", ctx, mock.MatchedBy(func(a *ItemAlternative) bool {
		return a.IsChosen && a.ChosenBy == "user-123"
	})).Return(nil)

	service := NewTemporalService(
		new(mockBranchRepository),
		new(mockVersionRepository),
		new(mockItemVersionRepository),
		mockRepo,
		new(mockMergeRepository),
		nil,
		nil,
	)

	err := service.SelectAlternative(ctx, "alt-123", "user-123", "Best solution")
	assert.NoError(t, err)
}

func TestCreateMergeRequest(t *testing.T) {
	ctx := context.Background()
	mr := &MergeRequest{
		ProjectID:      "proj-123",
		SourceBranchID: "feature/test",
		TargetBranchID: "main",
		Title:          "Add new feature",
		CreatedBy:      "user-123",
	}

	mockRepo := new(mockMergeRepository)
	mockRepo.On("Create", ctx, mock.MatchedBy(func(m *MergeRequest) bool {
		return m.Title == "Add new feature"
	})).Return(nil)

	service := NewTemporalService(
		new(mockBranchRepository),
		new(mockVersionRepository),
		new(mockItemVersionRepository),
		new(mockAlternativeRepository),
		mockRepo,
		nil,
		nil,
	)

	_, err := service.CreateMergeRequest(ctx, mr)
	assert.NoError(t, err)
}

func TestMergeBranches(t *testing.T) {
	ctx := context.Background()
	mr := &MergeRequest{
		ID:             "mr-123",
		Status:         "approved",
		SourceBranchID: "feature/test",
		TargetBranchID: "main",
	}

	sourceBranch := &VersionBranch{
		ID:   "branch-1",
		Name: "feature/test",
	}

	mockMergeRepo := new(mockMergeRepository)
	mockMergeRepo.On("GetByID", ctx, "mr-123").Return(mr, nil)
	mockMergeRepo.On("Update", ctx, mock.MatchedBy(func(m *MergeRequest) bool {
		return m.Status == "merged"
	})).Return(nil)

	mockBranchRepo := new(mockBranchRepository)
	mockBranchRepo.On("GetByID", ctx, "feature/test").Return(sourceBranch, nil)
	mockBranchRepo.On("Update", ctx, mock.Anything).Return(nil)

	service := NewTemporalService(
		mockBranchRepo,
		new(mockVersionRepository),
		new(mockItemVersionRepository),
		new(mockAlternativeRepository),
		mockMergeRepo,
		nil,
		nil,
	)

	// Note: This test will need redis mock or nil redis handling
	// For now, we'll test the logic without redis
	err := service.MergeBranches(ctx, "mr-123", "user-123")
	assert.NoError(t, err)
}

func TestCompareVersions(t *testing.T) {
	ctx := context.Background()
	versionA := &Version{
		ID:            "v-1",
		VersionNumber: 1,
	}
	versionB := &Version{
		ID:            "v-2",
		VersionNumber: 2,
	}

	mockRepo := new(mockVersionRepository)
	mockRepo.On("GetByID", ctx, "v-1").Return(versionA, nil)
	mockRepo.On("GetByID", ctx, "v-2").Return(versionB, nil)

	service := NewTemporalService(
		new(mockBranchRepository),
		mockRepo,
		new(mockItemVersionRepository),
		new(mockAlternativeRepository),
		new(mockMergeRepository),
		nil,
		nil,
	)

	diff, err := service.ComparVersions(ctx, "v-1", "v-2")
	require.NoError(t, err)
	assert.Equal(t, "v-1", diff.VersionAID)
	assert.Equal(t, "v-2", diff.VersionBID)
	assert.Equal(t, 1, diff.VersionANum)
	assert.Equal(t, 2, diff.VersionBNum)
}

func TestGetItemVersion(t *testing.T) {
	ctx := context.Background()
	snapshot := &ItemVersionSnapshot{
		ID:        "iv-123",
		ItemID:    "item-1",
		VersionID: "v-1",
	}

	mockRepo := new(mockItemVersionRepository)
	mockRepo.On("GetByItemAndVersion", ctx, "item-1", "v-1").Return(snapshot, nil)

	service := NewTemporalService(
		new(mockBranchRepository),
		new(mockVersionRepository),
		mockRepo,
		new(mockAlternativeRepository),
		new(mockMergeRepository),
		nil,
		nil,
	)

	result, err := service.GetItemVersion(ctx, "item-1", "v-1")
	require.NoError(t, err)
	assert.Equal(t, snapshot, result)
}

func TestGetItemVersionHistory(t *testing.T) {
	ctx := context.Background()
	history := []interface{}{
		&ItemVersionSnapshot{ID: "iv-1", ItemID: "item-1", VersionID: "v-1"},
		&ItemVersionSnapshot{ID: "iv-2", ItemID: "item-1", VersionID: "v-2"},
	}

	mockRepo := new(mockItemVersionRepository)
	mockRepo.On("GetHistory", ctx, "item-1", "branch-1").Return(history, nil)

	service := NewTemporalService(
		new(mockBranchRepository),
		new(mockVersionRepository),
		mockRepo,
		new(mockAlternativeRepository),
		new(mockMergeRepository),
		nil,
		nil,
	)

	result, err := service.GetItemVersionHistory(ctx, "item-1", "branch-1")
	require.NoError(t, err)
	assert.Equal(t, len(history), len(result))
}

func TestUpdateBranch(t *testing.T) {
	ctx := context.Background()
	branch := &VersionBranch{
		ID:        "branch-123",
		Name:      "main",
		ProjectID: "proj-123",
	}

	mockRepo := new(mockBranchRepository)
	mockRepo.On("Update", ctx, mock.MatchedBy(func(b *VersionBranch) bool {
		return b.ID == "branch-123"
	})).Return(nil)

	service := NewTemporalService(
		mockRepo,
		new(mockVersionRepository),
		new(mockItemVersionRepository),
		new(mockAlternativeRepository),
		new(mockMergeRepository),
		nil,
		nil,
	)

	result, err := service.UpdateBranch(ctx, branch)
	require.NoError(t, err)
	assert.Equal(t, branch.ID, result.ID)
}

func TestUpdateBranchError(t *testing.T) {
	ctx := context.Background()

	service := NewTemporalService(
		new(mockBranchRepository),
		new(mockVersionRepository),
		new(mockItemVersionRepository),
		new(mockAlternativeRepository),
		new(mockMergeRepository),
		nil,
		nil,
	)

	_, err := service.UpdateBranch(ctx, nil)
	assert.Error(t, err)
	assert.Contains(t, err.Error(), "branch and branch.id are required")
}

func TestDeleteBranch(t *testing.T) {
	ctx := context.Background()

	mockRepo := new(mockBranchRepository)
	mockRepo.On("Delete", ctx, "branch-123").Return(nil)

	service := NewTemporalService(
		mockRepo,
		new(mockVersionRepository),
		new(mockItemVersionRepository),
		new(mockAlternativeRepository),
		new(mockMergeRepository),
		nil,
		nil,
	)

	err := service.DeleteBranch(ctx, "branch-123")
	assert.NoError(t, err)
}

func TestDeleteBranchError(t *testing.T) {
	ctx := context.Background()

	service := NewTemporalService(
		new(mockBranchRepository),
		new(mockVersionRepository),
		new(mockItemVersionRepository),
		new(mockAlternativeRepository),
		new(mockMergeRepository),
		nil,
		nil,
	)

	err := service.DeleteBranch(ctx, "")
	assert.Error(t, err)
	assert.Contains(t, err.Error(), "branch_id is required")
}

func TestGetVersion(t *testing.T) {
	ctx := context.Background()
	version := &Version{
		ID:            "v-123",
		VersionNumber: 1,
	}

	mockRepo := new(mockVersionRepository)
	mockRepo.On("GetByID", ctx, "v-123").Return(version, nil)

	service := NewTemporalService(
		new(mockBranchRepository),
		mockRepo,
		new(mockItemVersionRepository),
		new(mockAlternativeRepository),
		new(mockMergeRepository),
		nil,
		nil,
	)

	result, err := service.GetVersion(ctx, "v-123")
	require.NoError(t, err)
	assert.Equal(t, version.ID, result.ID)
}

func TestGetVersionsByBranch(t *testing.T) {
	ctx := context.Background()
	versions := []interface{}{
		&Version{ID: "v-1", BranchID: "branch-123"},
		&Version{ID: "v-2", BranchID: "branch-123"},
	}

	mockRepo := new(mockVersionRepository)
	mockRepo.On("ListByBranch", ctx, "branch-123").Return(versions, nil)

	service := NewTemporalService(
		new(mockBranchRepository),
		mockRepo,
		new(mockItemVersionRepository),
		new(mockAlternativeRepository),
		new(mockMergeRepository),
		nil,
		nil,
	)

	result, err := service.GetVersionsByBranch(ctx, "branch-123")
	require.NoError(t, err)
	assert.Equal(t, len(versions), len(result))
}

func TestGetItemAtTime(t *testing.T) {
	ctx := context.Background()
	now := time.Now()
	pastTime := now.Add(-1 * time.Hour)
	futureTime := now.Add(1 * time.Hour)

	history := []interface{}{
		&ItemVersionSnapshot{
			ID:        "iv-1",
			ItemID:    "item-1",
			VersionID: "v-1",
			CreatedAt: pastTime,
		},
		&ItemVersionSnapshot{
			ID:        "iv-2",
			ItemID:    "item-1",
			VersionID: "v-2",
			CreatedAt: now,
		},
	}

	mockRepo := new(mockItemVersionRepository)
	mockRepo.On("GetHistory", ctx, "item-1", "").Return(history, nil)

	service := NewTemporalService(
		new(mockBranchRepository),
		new(mockVersionRepository),
		mockRepo,
		new(mockAlternativeRepository),
		new(mockMergeRepository),
		nil,
		nil,
	)

	// Test getting version at current time
	result, err := service.GetItemAtTime(ctx, "item-1", now)
	require.NoError(t, err)
	assert.Equal(t, "iv-2", result.ID)

	// Test getting version at past time
	result, err = service.GetItemAtTime(ctx, "item-1", pastTime)
	require.NoError(t, err)
	assert.Equal(t, "iv-1", result.ID)

	// Test getting version at future time (should return latest)
	mockRepo2 := new(mockItemVersionRepository)
	mockRepo2.On("GetHistory", ctx, "item-1", "").Return(history, nil)
	service2 := NewTemporalService(
		new(mockBranchRepository),
		new(mockVersionRepository),
		mockRepo2,
		new(mockAlternativeRepository),
		new(mockMergeRepository),
		nil,
		nil,
	)
	result, err = service2.GetItemAtTime(ctx, "item-1", futureTime)
	require.NoError(t, err)
	assert.Equal(t, "iv-2", result.ID)
}

func TestGetItemAtTimeError(t *testing.T) {
	ctx := context.Background()

	service := NewTemporalService(
		new(mockBranchRepository),
		new(mockVersionRepository),
		new(mockItemVersionRepository),
		new(mockAlternativeRepository),
		new(mockMergeRepository),
		nil,
		nil,
	)

	_, err := service.GetItemAtTime(ctx, "", time.Now())
	assert.Error(t, err)
	assert.Contains(t, err.Error(), "item_id is required")
}

func TestRestoreItemVersion(t *testing.T) {
	ctx := context.Background()
	snapshot := &ItemVersionSnapshot{
		ID:        "iv-123",
		ItemID:    "item-1",
		VersionID: "v-1",
		State:     map[string]interface{}{"title": "Test Item"},
	}

	mockItemVersionRepo := new(mockItemVersionRepository)
	mockItemVersionRepo.On("GetByItemAndVersion", ctx, "item-1", "v-1").Return(snapshot, nil)

	mockItemRepo := new(mockItemRepository)
	mockItemRepo.On("Update", ctx, mock.Anything).Return(nil)

	service := NewTemporalService(
		new(mockBranchRepository),
		new(mockVersionRepository),
		mockItemVersionRepo,
		new(mockAlternativeRepository),
		new(mockMergeRepository),
		mockItemRepo,
		nil,
	)

	err := service.RestoreItemVersion(ctx, "item-1", "v-1")
	assert.NoError(t, err)
}

func TestGetAlternatives(t *testing.T) {
	ctx := context.Background()
	alts := []interface{}{
		&ItemAlternative{ID: "alt-1", BaseItemID: "item-1"},
		&ItemAlternative{ID: "alt-2", BaseItemID: "item-1"},
	}

	mockRepo := new(mockAlternativeRepository)
	mockRepo.On("ListByBase", ctx, "item-1").Return(alts, nil)

	service := NewTemporalService(
		new(mockBranchRepository),
		new(mockVersionRepository),
		new(mockItemVersionRepository),
		mockRepo,
		new(mockMergeRepository),
		nil,
		nil,
	)

	result, err := service.GetAlternatives(ctx, "item-1")
	require.NoError(t, err)
	assert.Equal(t, len(alts), len(result))
}

func TestGetMergeRequest(t *testing.T) {
	ctx := context.Background()
	mr := &MergeRequest{
		ID:             "mr-123",
		SourceBranchID: "feature/test",
		TargetBranchID: "main",
	}

	mockRepo := new(mockMergeRepository)
	mockRepo.On("GetByID", ctx, "mr-123").Return(mr, nil)

	service := NewTemporalService(
		new(mockBranchRepository),
		new(mockVersionRepository),
		new(mockItemVersionRepository),
		new(mockAlternativeRepository),
		mockRepo,
		nil,
		nil,
	)

	result, err := service.GetMergeRequest(ctx, "mr-123")
	require.NoError(t, err)
	assert.Equal(t, mr.ID, result.ID)
}

func TestListMergeRequests(t *testing.T) {
	ctx := context.Background()
	mrs := []interface{}{
		&MergeRequest{ID: "mr-1", Status: "open"},
		&MergeRequest{ID: "mr-2", Status: "open"},
	}

	mockRepo := new(mockMergeRepository)
	mockRepo.On("ListByProject", ctx, "proj-123", "open").Return(mrs, nil)

	service := NewTemporalService(
		new(mockBranchRepository),
		new(mockVersionRepository),
		new(mockItemVersionRepository),
		new(mockAlternativeRepository),
		mockRepo,
		nil,
		nil,
	)

	result, err := service.ListMergeRequests(ctx, "proj-123", "open")
	require.NoError(t, err)
	assert.Equal(t, len(mrs), len(result))
}

func TestComputeMergeDiff(t *testing.T) {
	ctx := context.Background()
	mr := &MergeRequest{
		ID:              "mr-123",
		SourceVersionID: "v-2",
		BaseVersionID:   "v-1",
	}

	versionA := &Version{ID: "v-1", VersionNumber: 1}
	versionB := &Version{ID: "v-2", VersionNumber: 2}

	mockMergeRepo := new(mockMergeRepository)
	mockMergeRepo.On("GetByID", ctx, "mr-123").Return(mr, nil)

	mockVersionRepo := new(mockVersionRepository)
	mockVersionRepo.On("GetByID", ctx, "v-2").Return(versionB, nil)
	mockVersionRepo.On("GetByID", ctx, "v-1").Return(versionA, nil)

	service := NewTemporalService(
		new(mockBranchRepository),
		mockVersionRepo,
		new(mockItemVersionRepository),
		new(mockAlternativeRepository),
		mockMergeRepo,
		nil,
		nil,
	)

	diff, err := service.ComputeMergeDiff(ctx, "mr-123")
	require.NoError(t, err)
	assert.NotNil(t, diff)
	assert.Equal(t, "v-2", diff.VersionAID)
	assert.Equal(t, "v-1", diff.VersionBID)
}

// Additional error cases
func TestGetBranchError(t *testing.T) {
	ctx := context.Background()

	service := NewTemporalService(
		new(mockBranchRepository),
		new(mockVersionRepository),
		new(mockItemVersionRepository),
		new(mockAlternativeRepository),
		new(mockMergeRepository),
		nil,
		nil,
	)

	_, err := service.GetBranch(ctx, "")
	assert.Error(t, err)
	assert.Contains(t, err.Error(), "branch_id is required")
}

func TestGetBranchInvalidType(t *testing.T) {
	ctx := context.Background()

	mockRepo := new(mockBranchRepository)
	mockRepo.On("GetByID", ctx, "branch-123").Return("invalid-type", nil)

	service := NewTemporalService(
		mockRepo,
		new(mockVersionRepository),
		new(mockItemVersionRepository),
		new(mockAlternativeRepository),
		new(mockMergeRepository),
		nil,
		nil,
	)

	_, err := service.GetBranch(ctx, "branch-123")
	assert.Error(t, err)
	assert.Contains(t, err.Error(), "invalid branch type")
}

func TestGetVersionError(t *testing.T) {
	ctx := context.Background()

	service := NewTemporalService(
		new(mockBranchRepository),
		new(mockVersionRepository),
		new(mockItemVersionRepository),
		new(mockAlternativeRepository),
		new(mockMergeRepository),
		nil,
		nil,
	)

	_, err := service.GetVersion(ctx, "")
	assert.Error(t, err)
	assert.Contains(t, err.Error(), "version_id is required")
}

func TestGetItemVersionError(t *testing.T) {
	ctx := context.Background()

	service := NewTemporalService(
		new(mockBranchRepository),
		new(mockVersionRepository),
		new(mockItemVersionRepository),
		new(mockAlternativeRepository),
		new(mockMergeRepository),
		nil,
		nil,
	)

	_, err := service.GetItemVersion(ctx, "", "v-1")
	assert.Error(t, err)
	assert.Contains(t, err.Error(), "item_id and version_id are required")
}

func TestGetAlternativesError(t *testing.T) {
	ctx := context.Background()

	service := NewTemporalService(
		new(mockBranchRepository),
		new(mockVersionRepository),
		new(mockItemVersionRepository),
		new(mockAlternativeRepository),
		new(mockMergeRepository),
		nil,
		nil,
	)

	_, err := service.GetAlternatives(ctx, "")
	assert.Error(t, err)
	assert.Contains(t, err.Error(), "base_item_id is required")
}

func TestGetMergeRequestError(t *testing.T) {
	ctx := context.Background()

	service := NewTemporalService(
		new(mockBranchRepository),
		new(mockVersionRepository),
		new(mockItemVersionRepository),
		new(mockAlternativeRepository),
		new(mockMergeRepository),
		nil,
		nil,
	)

	_, err := service.GetMergeRequest(ctx, "")
	assert.Error(t, err)
	assert.Contains(t, err.Error(), "merge request id is required")
}

func TestListMergeRequestsError(t *testing.T) {
	ctx := context.Background()

	service := NewTemporalService(
		new(mockBranchRepository),
		new(mockVersionRepository),
		new(mockItemVersionRepository),
		new(mockAlternativeRepository),
		new(mockMergeRepository),
		nil,
		nil,
	)

	_, err := service.ListMergeRequests(ctx, "", "open")
	assert.Error(t, err)
	assert.Contains(t, err.Error(), "project_id is required")
}

// Benchmark tests
func BenchmarkCreateBranch(b *testing.B) {
	mockRepo := new(mockBranchRepository)
	mockRepo.On("Create", mock.Anything, mock.Anything).Return(nil)

	service := NewTemporalService(
		mockRepo,
		new(mockVersionRepository),
		new(mockItemVersionRepository),
		new(mockAlternativeRepository),
		new(mockMergeRepository),
		nil,
		nil,
	)

	branch := &VersionBranch{
		Name:      "feature/test",
		ProjectID: "proj-123",
	}

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		_, _ = service.CreateBranch(context.Background(), branch)
	}
}

func BenchmarkCompareVersions(b *testing.B) {
	versionA := &Version{ID: "v-1", VersionNumber: 1}
	versionB := &Version{ID: "v-2", VersionNumber: 2}

	mockRepo := new(mockVersionRepository)
	mockRepo.On("GetByID", mock.Anything, "v-1").Return(versionA, nil)
	mockRepo.On("GetByID", mock.Anything, "v-2").Return(versionB, nil)

	service := NewTemporalService(
		new(mockBranchRepository),
		mockRepo,
		new(mockItemVersionRepository),
		new(mockAlternativeRepository),
		new(mockMergeRepository),
		nil,
		nil,
	)

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		_, _ = service.ComparVersions(context.Background(), "v-1", "v-2")
	}
}
