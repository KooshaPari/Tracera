package services

import (
	"context"
	"testing"
	"time"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/mock"
	"github.com/stretchr/testify/require"
)

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
	assert.Len(t, result, len(history))
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
