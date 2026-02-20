//go:build !integration && !e2e

package services

import (
	"context"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/mock"
	"github.com/stretchr/testify/require"

	"github.com/kooshapari/tracertm-backend/internal/models"
)

func TestNewGraphAnalysisServiceImpl(t *testing.T) {
	t.Run("creates service successfully", func(t *testing.T) {
		service, _, _ := createTestGraphService(t)
		assert.NotNil(t, service)
	})

	t.Run("panics when itemRepo is nil", func(t *testing.T) {
		assert.Panics(t, func() {
			NewGraphAnalysisServiceImpl(nil, &GraphMockLinkRepository{}, &GraphMockCache{}, nil)
		})
	})

	t.Run("panics when linkRepo is nil", func(t *testing.T) {
		assert.Panics(t, func() {
			NewGraphAnalysisServiceImpl(&GraphMockItemRepository{}, nil, &GraphMockCache{}, nil)
		})
	})
}

func TestAnalyzeItemDependencies_Success(t *testing.T) {
	ctx := context.Background()
	itemID := testItem1ID

	t.Run("analyzes item with no dependencies", func(t *testing.T) {
		service, itemRepo, linkRepo := createTestGraphService(t)
		item := createTestItem(itemID, "Feature 1", "feature")
		itemRepo.On("GetByID", mock.Anything, itemID).Return(item, nil)
		linkRepo.On("GetByTargetID", mock.Anything, itemID).Return([]*models.Link{}, nil)
		linkRepo.On("GetBySourceID", mock.Anything, itemID).Return([]*models.Link{}, nil)

		result, err := service.AnalyzeItemDependencies(ctx, itemID)
		require.NoError(t, err)
		assert.NotNil(t, result)
		assert.Equal(t, itemID, result.ItemID)
		assert.Equal(t, 0, result.DirectDependents)
		assert.Equal(t, 0, result.TransitiveDeps)
		assert.Equal(t, "low", result.Complexity)
	})

	t.Run("analyzes item with transitive dependencies", func(t *testing.T) {
		service, itemRepo, linkRepo := createTestGraphService(t)
		item := createTestItem(itemID, "Feature 1", "feature")
		outgoingLinks1 := []*models.Link{
			createTestLink("link-1", itemID, "item-2", "depends_on"),
		}
		outgoingLinks2 := []*models.Link{
			createTestLink("link-2", "item-2", "item-3", "depends_on"),
		}
		itemRepo.On("GetByID", mock.Anything, itemID).Return(item, nil)
		linkRepo.On("GetByTargetID", mock.Anything, itemID).Return([]*models.Link{}, nil)
		linkRepo.On("GetBySourceID", mock.Anything, itemID).Return(outgoingLinks1, nil)
		linkRepo.On("GetBySourceID", mock.Anything, "item-2").Return(outgoingLinks2, nil)
		linkRepo.On("GetBySourceID", mock.Anything, "item-3").Return([]*models.Link{}, nil)

		result, err := service.AnalyzeItemDependencies(ctx, itemID)
		require.NoError(t, err)
		assert.Equal(t, 0, result.DirectDependents)
		assert.Equal(t, 2, result.TransitiveDeps)
	})
}

func TestGetItemImpactAnalysis_Success(t *testing.T) {
	ctx := context.Background()
	itemID := testItem1ID

	t.Run("analyzes item with direct impact", func(t *testing.T) {
		service, itemRepo, linkRepo := createTestGraphService(t)
		item := createTestItem(itemID, "Feature 1", "feature")
		links := []*models.Link{
			createTestLink("link-1", "item-2", itemID, "depends_on"),
			createTestLink("link-2", "item-3", itemID, "depends_on"),
		}
		itemRepo.On("GetByID", mock.Anything, itemID).Return(item, nil)
		linkRepo.On("GetByTargetID", mock.Anything, itemID).Return(links, nil)
		linkRepo.On("GetByTargetID", mock.Anything, "item-2").Return([]*models.Link{}, nil)
		linkRepo.On("GetByTargetID", mock.Anything, "item-3").Return([]*models.Link{}, nil)

		result, err := service.GetItemImpactAnalysis(ctx, itemID)
		require.NoError(t, err)
		assert.Len(t, result.DirectImpact, 2)
		assert.Contains(t, result.DirectImpact, "item-2")
		assert.Contains(t, result.DirectImpact, "item-3")
		assert.Empty(t, result.IndirectImpact)
	})
}

func TestVisualizeDependencyGraph_Success(t *testing.T) {
	ctx := context.Background()
	itemID := testItem1ID

	t.Run("generates DOT graph with dependencies", func(t *testing.T) {
		service, itemRepo, linkRepo := createTestGraphService(t)
		item1 := createTestItem(itemID, "Feature 1", "feature")
		item2 := createTestItem("item-2", "Feature 2", "feature")
		link := createTestLink("link-1", itemID, "item-2", "depends_on")
		itemRepo.On("GetByID", mock.Anything, itemID).Return(item1, nil)
		itemRepo.On("GetByID", mock.Anything, "item-2").Return(item2, nil)
		linkRepo.On("GetBySourceID", mock.Anything, itemID).Return([]*models.Link{link}, nil)
		linkRepo.On("GetByTargetID", mock.Anything, itemID).Return([]*models.Link{}, nil)
		linkRepo.On("GetBySourceID", mock.Anything, "item-2").Return([]*models.Link{}, nil)
		linkRepo.On("GetByTargetID", mock.Anything, "item-2").Return([]*models.Link{link}, nil)

		result, err := service.VisualizeDependencyGraph(ctx, itemID)
		require.NoError(t, err)
		assert.Contains(t, result, itemID)
		assert.Contains(t, result, "item-2")
		assert.Contains(t, result, "depends_on")
		assert.Contains(t, result, "->")
	})
}
