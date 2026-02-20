//go:build !integration && !e2e

package services

import (
	"context"
	"errors"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/mock"
	"github.com/stretchr/testify/require"
)

func TestAnalyzeItemDependencies_Errors(t *testing.T) {
	service, itemRepo, _ := createTestGraphService(t)
	ctx := context.Background()

	t.Run("returns error for empty itemID", func(t *testing.T) {
		result, err := service.AnalyzeItemDependencies(ctx, "")
		require.Error(t, err)
		assert.Nil(t, result)
		assert.Contains(t, err.Error(), "itemID cannot be empty")
	})

	t.Run("returns error when item not found", func(t *testing.T) {
		itemID := testNonexistentID
		itemRepo.On("GetByID", mock.Anything, itemID).Return(nil, errors.New("item not found"))

		result, err := service.AnalyzeItemDependencies(ctx, itemID)
		require.Error(t, err)
		assert.Nil(t, result)
	})
}

func TestGetItemImpactAnalysis_Errors(t *testing.T) {
	service, itemRepo, _ := createTestGraphService(t)
	ctx := context.Background()

	t.Run("returns error for empty itemID", func(t *testing.T) {
		result, err := service.GetItemImpactAnalysis(ctx, "")
		require.Error(t, err)
		assert.Nil(t, result)
		assert.Contains(t, err.Error(), "itemID cannot be empty")
	})

	t.Run("returns error when item not found", func(t *testing.T) {
		itemID := testNonexistentID
		itemRepo.On("GetByID", mock.Anything, itemID).Return(nil, errors.New("not found"))

		result, err := service.GetItemImpactAnalysis(ctx, itemID)
		require.Error(t, err)
		assert.Nil(t, result)
	})
}

func TestVisualizeDependencyGraph_Errors(t *testing.T) {
	service, itemRepo, _ := createTestGraphService(t)
	ctx := context.Background()

	t.Run("returns error for empty itemID", func(t *testing.T) {
		result, err := service.VisualizeDependencyGraph(ctx, "")
		require.Error(t, err)
		assert.Empty(t, result)
		assert.Contains(t, err.Error(), "itemID cannot be empty")
	})

	t.Run("returns error when item not found", func(t *testing.T) {
		itemID := testNonexistentID
		itemRepo.On("GetByID", mock.Anything, itemID).Return(nil, errors.New("not found"))

		result, err := service.VisualizeDependencyGraph(ctx, itemID)
		require.Error(t, err)
		assert.Empty(t, result)
	})
}
