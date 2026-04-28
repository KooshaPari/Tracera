package services

import (
	"context"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/mock"
	"github.com/stretchr/testify/require"
)

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
	assert.Len(t, result, len(mrs))
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
