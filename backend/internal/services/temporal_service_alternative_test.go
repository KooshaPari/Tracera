package services

import (
	"context"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/mock"
	"github.com/stretchr/testify/require"
)

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
	assert.Len(t, result, len(alts))
}
