package services

import (
	"context"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/mock"
	"github.com/stretchr/testify/require"
)

func TestCreateVersion(t *testing.T) {
	ctx := context.Background()

	for _, tt := range createVersionCases(ctx) {
		t.Run(tt.name, func(t *testing.T) {
			runCreateVersionCase(ctx, t, tt)
		})
	}
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
	assert.Equal(t, 1, diff.VersionANumber)
	assert.Equal(t, 2, diff.VersionBNumber)
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
	assert.Len(t, result, len(versions))
}

type createVersionCase struct {
	name      string
	input     *Version
	setupMock func(*mockVersionRepository)
	wantErr   bool
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
