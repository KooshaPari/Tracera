//go:build !integration && !e2e

package services

import (
	"context"
	"strings"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/mock"
	"github.com/stretchr/testify/require"

	"github.com/kooshapari/tracertm-backend/internal/models"
)

func TestGetLinkStyle(t *testing.T) {
	service, _, _ := createTestGraphService(t)

	tests := []struct {
		name     string
		linkType string
		expected string
	}{
		{"depends_on uses blue", "depends_on", ", style=solid, color=blue"},
		{"blocks uses red", "blocks", ", style=bold, color=red"},
		{"implements uses green", "implements", ", style=dashed, color=green"},
		{"tests uses purple", "tests", ", style=dotted, color=purple"},
		{"unknown uses gray", "unknown", ", style=solid, color=gray"},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			result := service.getLinkStyle(tt.linkType)
			assert.Equal(t, tt.expected, result)
		})
	}
}

func TestCalculateComplexity(t *testing.T) {
	service, _, _ := createTestGraphService(t)

	tests := []struct {
		name             string
		directDependents int
		transitiveDeps   int
		expected         string
	}{
		{"zero is low", 0, 0, "low"},
		{"5 total is low", 2, 3, "low"},
		{"6 total is medium", 3, 3, "medium"},
		{"15 total is medium", 8, 7, "medium"},
		{"16 total is high", 10, 6, "high"},
		{"large numbers are high", 50, 100, "high"},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			result := service.calculateComplexity(tt.directDependents, tt.transitiveDeps)
			assert.Equal(t, tt.expected, result)
		})
	}
}

func TestCalculateRiskLevel(t *testing.T) {
	service, _, _ := createTestGraphService(t)

	tests := []struct {
		name           string
		directImpact   int
		indirectImpact int
		expected       string
	}{
		{"zero is low", 0, 0, "low"},
		{"3 total is low", 2, 1, "low"},
		{"4 total is medium", 2, 2, "medium"},
		{"10 total is medium", 5, 5, "medium"},
		{"11 total is high", 6, 5, "high"},
		{"large numbers are high", 20, 30, "high"},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			result := service.calculateRiskLevel(tt.directImpact, tt.indirectImpact)
			assert.Equal(t, tt.expected, result)
		})
	}
}

func TestVisualizeDependencyGraph_EdgeCases(t *testing.T) {
	ctx := context.Background()
	itemID := testItem1ID

	t.Run("escapes quotes in item titles", func(t *testing.T) {
		service, itemRepo, linkRepo := createTestGraphService(t)
		item := createTestItem(itemID, "Feature \"quoted\" 1", "feature")
		itemRepo.On("GetByID", mock.Anything, itemID).Return(item, nil)
		linkRepo.On("GetBySourceID", mock.Anything, itemID).Return([]*models.Link{}, nil)
		linkRepo.On("GetByTargetID", mock.Anything, itemID).Return([]*models.Link{}, nil)

		result, err := service.VisualizeDependencyGraph(ctx, itemID)
		require.NoError(t, err)
		assert.Contains(t, result, "Feature \\\"quoted\\\" 1")
	})

	t.Run("deduplicates edges in graph", func(t *testing.T) {
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
		edgeCount := strings.Count(result, itemID+"\" -> \"item-2\"")
		assert.Equal(t, 1, edgeCount)
	})
}
