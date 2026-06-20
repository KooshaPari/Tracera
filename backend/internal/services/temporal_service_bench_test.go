package services

import (
	"context"
	"testing"

	"github.com/stretchr/testify/mock"
	"github.com/stretchr/testify/require"
)

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
		_, err := service.CreateBranch(context.Background(), branch)
		require.NoError(b, err)
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
		_, err := service.ComparVersions(context.Background(), "v-1", "v-2")
		require.NoError(b, err)
	}
}
