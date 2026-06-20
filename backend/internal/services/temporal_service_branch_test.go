package services

import (
	"context"
	"errors"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/mock"
	"github.com/stretchr/testify/require"
)

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
	assert.Len(t, result, len(branches))
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
	require.NoError(t, err)
}

type createBranchCase struct {
	name      string
	input     *VersionBranch
	setupMock func(*mockBranchRepository)
	wantErr   bool
	errMsg    string
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
		require.Error(t, err)
		assert.Contains(t, err.Error(), tc.errMsg)
		return
	}
	require.NoError(t, err)
}
