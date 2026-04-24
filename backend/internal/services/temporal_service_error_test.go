package services

import (
	"context"
	"testing"
	"time"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

// Additional error cases
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
	require.Error(t, err)
	assert.Contains(t, err.Error(), "branch and branch.id are required")
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
	require.Error(t, err)
	assert.Contains(t, err.Error(), "branch_id is required")
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
	require.Error(t, err)
	assert.Contains(t, err.Error(), "item_id is required")
}

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
	require.Error(t, err)
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
	require.Error(t, err)
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
	require.Error(t, err)
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
	require.Error(t, err)
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
	require.Error(t, err)
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
	require.Error(t, err)
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
	require.Error(t, err)
	assert.Contains(t, err.Error(), "project_id is required")
}
