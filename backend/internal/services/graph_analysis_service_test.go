//go:build !integration && !e2e

package services

import (
	"context"
	"errors"
	"fmt"
	"strings"
	"testing"

	"github.com/kooshapari/tracertm-backend/internal/cache"
	"github.com/kooshapari/tracertm-backend/internal/models"
	"github.com/kooshapari/tracertm-backend/internal/repository"
	"github.com/nats-io/nats.go"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/mock"
	"github.com/stretchr/testify/require"
)

// ============================================================================
// MOCK REPOSITORIES
// ============================================================================

type GraphMockItemRepository struct {
	mock.Mock
}

func (m *GraphMockItemRepository) Create(ctx context.Context, item *models.Item) error {
	args := m.Called(ctx, item)
	return args.Error(0)
}

func (m *GraphMockItemRepository) GetByID(ctx context.Context, id string) (*models.Item, error) {
	args := m.Called(ctx, id)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	return args.Get(0).(*models.Item), args.Error(1)
}

func (m *GraphMockItemRepository) GetByProjectID(ctx context.Context, projectID string) ([]*models.Item, error) {
	args := m.Called(ctx, projectID)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	return args.Get(0).([]*models.Item), args.Error(1)
}

func (m *GraphMockItemRepository) List(ctx context.Context, filter repository.ItemFilter) ([]*models.Item, error) {
	args := m.Called(ctx, filter)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	return args.Get(0).([]*models.Item), args.Error(1)
}

func (m *GraphMockItemRepository) Update(ctx context.Context, item *models.Item) error {
	args := m.Called(ctx, item)
	return args.Error(0)
}

func (m *GraphMockItemRepository) Delete(ctx context.Context, id string) error {
	args := m.Called(ctx, id)
	return args.Error(0)
}

func (m *GraphMockItemRepository) Count(ctx context.Context, filter repository.ItemFilter) (int64, error) {
	args := m.Called(ctx, filter)
	return args.Get(0).(int64), args.Error(1)
}

type GraphMockLinkRepository struct {
	mock.Mock
}

func (m *GraphMockLinkRepository) Create(ctx context.Context, link *models.Link) error {
	args := m.Called(ctx, link)
	return args.Error(0)
}

func (m *GraphMockLinkRepository) GetByID(ctx context.Context, id string) (*models.Link, error) {
	args := m.Called(ctx, id)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	return args.Get(0).(*models.Link), args.Error(1)
}

func (m *GraphMockLinkRepository) GetBySourceID(ctx context.Context, sourceID string) ([]*models.Link, error) {
	args := m.Called(ctx, sourceID)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	return args.Get(0).([]*models.Link), args.Error(1)
}

func (m *GraphMockLinkRepository) GetByTargetID(ctx context.Context, targetID string) ([]*models.Link, error) {
	args := m.Called(ctx, targetID)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	return args.Get(0).([]*models.Link), args.Error(1)
}

func (m *GraphMockLinkRepository) List(ctx context.Context, filter repository.LinkFilter) ([]*models.Link, error) {
	args := m.Called(ctx, filter)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	return args.Get(0).([]*models.Link), args.Error(1)
}

func (m *GraphMockLinkRepository) Update(ctx context.Context, link *models.Link) error {
	args := m.Called(ctx, link)
	return args.Error(0)
}

func (m *GraphMockLinkRepository) Delete(ctx context.Context, id string) error {
	args := m.Called(ctx, id)
	return args.Error(0)
}

func (m *GraphMockLinkRepository) DeleteByItemID(ctx context.Context, itemID string) error {
	args := m.Called(ctx, itemID)
	return args.Error(0)
}

// GraphMockCache implements cache.Cache for tests
type GraphMockCache struct {
	mock.Mock
}

var _ cache.Cache = (*GraphMockCache)(nil)

func (m *GraphMockCache) Get(ctx context.Context, key string, dest interface{}) error {
	args := m.Called(ctx, key, dest)
	return args.Error(0)
}

func (m *GraphMockCache) Set(ctx context.Context, key string, value interface{}) error {
	args := m.Called(ctx, key, value)
	return args.Error(0)
}

func (m *GraphMockCache) Delete(ctx context.Context, keys ...string) error {
	args := m.Called(ctx, keys)
	return args.Error(0)
}

func (m *GraphMockCache) InvalidatePattern(ctx context.Context, pattern string) error {
	args := m.Called(ctx, pattern)
	return args.Error(0)
}

func (m *GraphMockCache) Close() error {
	return nil
}

// ============================================================================
// TEST FIXTURES
// ============================================================================

func createTestGraphService(_ *testing.T) (*GraphAnalysisServiceImpl, *GraphMockItemRepository, *GraphMockLinkRepository) {
	itemRepo := &GraphMockItemRepository{}
	linkRepo := &GraphMockLinkRepository{}
	cache := &GraphMockCache{}
	var natsConn *nats.Conn // nil is OK for graph service

	service := NewGraphAnalysisServiceImpl(itemRepo, linkRepo, cache, natsConn)

	return service.(*GraphAnalysisServiceImpl), itemRepo, linkRepo
}

func createTestItem(id, title, itemType string) *models.Item {
	return &models.Item{
		ID:          id,
		ProjectID:   "test-project",
		Title:       title,
		Description: "Test description",
		Type:        itemType,
		Status:      "todo",
		Priority:    models.PriorityMedium,
	}
}

func createTestLink(id, sourceID, targetID, linkType string) *models.Link {
	return &models.Link{
		ID:       id,
		SourceID: sourceID,
		TargetID: targetID,
		Type:     linkType,
	}
}

// ============================================================================
// CONSTRUCTOR TESTS
// ============================================================================

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

// ============================================================================
// DEPENDENCY ANALYSIS TESTS
// ============================================================================

type analyzeDependenciesCase struct {
	name   string
	setup  func(ctx context.Context, itemRepo *GraphMockItemRepository, linkRepo *GraphMockLinkRepository, itemID string)
	assert func(t *testing.T, itemID string, result *DependencyAnalysis)
}

func analyzeItemDependenciesBasicCases() []analyzeDependenciesCase {
	return []analyzeDependenciesCase{
		{
			name: "analyzes item with no dependencies",
			setup: func(ctx context.Context, itemRepo *GraphMockItemRepository, linkRepo *GraphMockLinkRepository, itemID string) {
				item := createTestItem(itemID, "Feature 1", "feature")
				itemRepo.On("GetByID", ctx, itemID).Return(item, nil)
				linkRepo.On("GetByTargetID", ctx, itemID).Return([]*models.Link{}, nil)
				linkRepo.On("GetBySourceID", ctx, itemID).Return([]*models.Link{}, nil)
			},
			assert: func(t *testing.T, itemID string, result *DependencyAnalysis) {
				assert.NotNil(t, result)
				assert.Equal(t, itemID, result.ItemID)
				assert.Equal(t, 0, result.DirectDependents)
				assert.Equal(t, 0, result.TransitiveDeps)
				assert.Equal(t, "low", result.Complexity)
			},
		},
		{
			name: "analyzes item with direct dependents only",
			setup: func(ctx context.Context, itemRepo *GraphMockItemRepository, linkRepo *GraphMockLinkRepository, itemID string) {
				item := createTestItem(itemID, "Feature 1", "feature")
				links := []*models.Link{
					createTestLink("link-1", "item-2", itemID, "depends_on"),
					createTestLink("link-2", "item-3", itemID, "depends_on"),
				}
				itemRepo.On("GetByID", ctx, itemID).Return(item, nil)
				linkRepo.On("GetByTargetID", ctx, itemID).Return(links, nil)
				linkRepo.On("GetBySourceID", ctx, itemID).Return([]*models.Link{}, nil)
			},
			assert: func(t *testing.T, _ string, result *DependencyAnalysis) {
				assert.Equal(t, 2, result.DirectDependents)
				assert.Equal(t, 0, result.TransitiveDeps)
				assert.Equal(t, "low", result.Complexity)
			},
		},
		{
			name: "analyzes item with transitive dependencies",
			setup: func(ctx context.Context, itemRepo *GraphMockItemRepository, linkRepo *GraphMockLinkRepository, itemID string) {
				item := createTestItem(itemID, "Feature 1", "feature")
				outgoingLinks1 := []*models.Link{
					createTestLink("link-1", itemID, "item-2", "depends_on"),
				}
				outgoingLinks2 := []*models.Link{
					createTestLink("link-2", "item-2", "item-3", "depends_on"),
				}
				itemRepo.On("GetByID", ctx, itemID).Return(item, nil)
				linkRepo.On("GetByTargetID", ctx, itemID).Return([]*models.Link{}, nil)
				linkRepo.On("GetBySourceID", ctx, itemID).Return(outgoingLinks1, nil)
				linkRepo.On("GetBySourceID", ctx, "item-2").Return(outgoingLinks2, nil)
				linkRepo.On("GetBySourceID", ctx, "item-3").Return([]*models.Link{}, nil)
			},
			assert: func(t *testing.T, _ string, result *DependencyAnalysis) {
				assert.Equal(t, 0, result.DirectDependents)
				assert.Equal(t, 2, result.TransitiveDeps)
				assert.Equal(t, "low", result.Complexity)
			},
		},
	}
}

func analyzeItemDependenciesMediumCases() []analyzeDependenciesCase {
	return []analyzeDependenciesCase{
		{
			name: "calculates medium complexity",
			setup: func(ctx context.Context, itemRepo *GraphMockItemRepository, linkRepo *GraphMockLinkRepository, itemID string) {
				item := createTestItem(itemID, "Feature 1", "feature")
				links := []*models.Link{
					createTestLink("link-1", "item-2", itemID, "depends_on"),
					createTestLink("link-2", "item-3", itemID, "depends_on"),
					createTestLink("link-3", "item-4", itemID, "blocks"),
					createTestLink("link-4", "item-5", itemID, "requires"),
				}
				outgoingLinks := []*models.Link{
					createTestLink("link-5", itemID, "item-6", "depends_on"),
					createTestLink("link-6", itemID, "item-7", "depends_on"),
					createTestLink("link-7", itemID, "item-8", "depends_on"),
				}
				itemRepo.On("GetByID", ctx, itemID).Return(item, nil)
				linkRepo.On("GetByTargetID", ctx, itemID).Return(links, nil)
				linkRepo.On("GetBySourceID", ctx, itemID).Return(outgoingLinks, nil)
				linkRepo.On("GetBySourceID", ctx, "item-6").Return([]*models.Link{}, nil)
				linkRepo.On("GetBySourceID", ctx, "item-7").Return([]*models.Link{}, nil)
				linkRepo.On("GetBySourceID", ctx, "item-8").Return([]*models.Link{}, nil)
			},
			assert: func(t *testing.T, _ string, result *DependencyAnalysis) {
				assert.Equal(t, 4, result.DirectDependents)
				assert.Equal(t, 3, result.TransitiveDeps)
				assert.Equal(t, "medium", result.Complexity)
			},
		},
	}
}

func analyzeItemDependenciesHighCases() []analyzeDependenciesCase {
	return []analyzeDependenciesCase{
		{
			name: "calculates high complexity",
			setup: func(ctx context.Context, itemRepo *GraphMockItemRepository, linkRepo *GraphMockLinkRepository, itemID string) {
				item := createTestItem(itemID, "Feature 1", "feature")
				directLinks := make([]*models.Link, 10)
				for i := 0; i < 10; i++ {
					directLinks[i] = createTestLink(
						fmt.Sprintf("link-%d", i),
						fmt.Sprintf("item-%d", i+2),
						itemID,
						"depends_on",
					)
				}
				transitiveLinks := make([]*models.Link, 8)
				for i := 0; i < 8; i++ {
					transitiveLinks[i] = createTestLink(
						fmt.Sprintf("link-t-%d", i),
						itemID,
						fmt.Sprintf("item-dep-%d", i),
						"depends_on",
					)
				}
				itemRepo.On("GetByID", ctx, itemID).Return(item, nil)
				linkRepo.On("GetByTargetID", ctx, itemID).Return(directLinks, nil)
				linkRepo.On("GetBySourceID", ctx, itemID).Return(transitiveLinks, nil)
				for i := 0; i < 8; i++ {
					linkRepo.On("GetBySourceID", ctx, fmt.Sprintf("item-dep-%d", i)).Return([]*models.Link{}, nil)
				}
			},
			assert: func(t *testing.T, _ string, result *DependencyAnalysis) {
				assert.Equal(t, 10, result.DirectDependents)
				assert.Equal(t, 8, result.TransitiveDeps)
				assert.Equal(t, "high", result.Complexity)
			},
		},
	}
}

func analyzeItemDependenciesComplexCases() []analyzeDependenciesCase {
	return append(analyzeItemDependenciesMediumCases(), analyzeItemDependenciesHighCases()...)
}

func analyzeItemDependenciesCoreCases() []analyzeDependenciesCase {
	return append(analyzeItemDependenciesBasicCases(), analyzeItemDependenciesComplexCases()...)
}

func analyzeItemDependenciesEdgeCases() []analyzeDependenciesCase {
	return []analyzeDependenciesCase{
		{
			name: "filters non-dependency link types",
			setup: func(ctx context.Context, itemRepo *GraphMockItemRepository, linkRepo *GraphMockLinkRepository, itemID string) {
				item := createTestItem(itemID, "Feature 1", "feature")
				links := []*models.Link{
					createTestLink("link-1", "item-2", itemID, "depends_on"),
					createTestLink("link-2", "item-3", itemID, "implements"),
					createTestLink("link-3", "item-4", itemID, "tests"),
					createTestLink("link-4", "item-5", itemID, "blocks"),
				}
				itemRepo.On("GetByID", ctx, itemID).Return(item, nil)
				linkRepo.On("GetByTargetID", ctx, itemID).Return(links, nil)
				linkRepo.On("GetBySourceID", ctx, itemID).Return([]*models.Link{}, nil)
			},
			assert: func(t *testing.T, _ string, result *DependencyAnalysis) {
				assert.Equal(t, 2, result.DirectDependents)
			},
		},
		{
			name: "handles circular dependencies",
			setup: func(ctx context.Context, itemRepo *GraphMockItemRepository, linkRepo *GraphMockLinkRepository, itemID string) {
				item := createTestItem(itemID, "Feature 1", "feature")
				links1 := []*models.Link{
					createTestLink("link-1", itemID, "item-2", "depends_on"),
				}
				links2 := []*models.Link{
					createTestLink("link-2", "item-2", "item-3", "depends_on"),
				}
				links3 := []*models.Link{
					createTestLink("link-3", "item-3", itemID, "depends_on"),
				}
				itemRepo.On("GetByID", ctx, itemID).Return(item, nil)
				linkRepo.On("GetByTargetID", ctx, itemID).Return([]*models.Link{}, nil)
				linkRepo.On("GetBySourceID", ctx, itemID).Return(links1, nil)
				linkRepo.On("GetBySourceID", ctx, "item-2").Return(links2, nil)
				linkRepo.On("GetBySourceID", ctx, "item-3").Return(links3, nil)
			},
			assert: func(t *testing.T, _ string, result *DependencyAnalysis) {
				assert.NotNil(t, result)
				assert.Equal(t, 2, result.TransitiveDeps)
			},
		},
	}
}

func analyzeItemDependenciesCases() []analyzeDependenciesCase {
	return append(analyzeItemDependenciesCoreCases(), analyzeItemDependenciesEdgeCases()...)
}

func runAnalyzeItemDependenciesCase(
	ctx context.Context,
	t *testing.T,
	service *GraphAnalysisServiceImpl,
	itemRepo *GraphMockItemRepository,
	linkRepo *GraphMockLinkRepository,
	itemID string,
	tc analyzeDependenciesCase,
) {
	t.Helper()
	tc.setup(ctx, itemRepo, linkRepo, itemID)
	result, err := service.AnalyzeItemDependencies(ctx, itemID)
	require.NoError(t, err)
	tc.assert(t, itemID, result)
}

func TestAnalyzeItemDependencies_Success(t *testing.T) {
	ctx := context.Background()

	for _, tc := range analyzeItemDependenciesCases() {
		t.Run(tc.name, func(t *testing.T) {
			service, itemRepo, linkRepo := createTestGraphService(t)
			runAnalyzeItemDependenciesCase(ctx, t, service, itemRepo, linkRepo, testItem1ID, tc)
		})
	}
}

func TestAnalyzeItemDependencies_Errors(t *testing.T) {
	service, itemRepo, _ := createTestGraphService(t)
	ctx := context.Background()

	t.Run("returns error for empty itemID", func(t *testing.T) {
		result, err := service.AnalyzeItemDependencies(ctx, "")
		assert.Error(t, err)
		assert.Nil(t, result)
		assert.Contains(t, err.Error(), "itemID cannot be empty")
	})

	t.Run("returns error when item not found", func(t *testing.T) {
		itemID := testNonexistentID
		itemRepo.On("GetByID", ctx, itemID).Return(nil, errors.New("item not found"))

		result, err := service.AnalyzeItemDependencies(ctx, itemID)
		assert.Error(t, err)
		assert.Nil(t, result)
		assert.Contains(t, err.Error(), "failed to get item")
	})

	t.Run("returns error when item is nil", func(t *testing.T) {
		itemID := testItem1ID
		itemRepo.On("GetByID", ctx, itemID).Return(nil, nil)

		result, err := service.AnalyzeItemDependencies(ctx, itemID)
		assert.Error(t, err)
		assert.Nil(t, result)
		assert.Contains(t, err.Error(), "item not found")
	})

	t.Run("returns error when linkRepo fails", func(t *testing.T) {
		itemID := testItem1ID
		item := createTestItem(itemID, "Feature 1", "feature")

		itemRepo.On("GetByID", ctx, itemID).Return(item, nil)
		linkRepo := &GraphMockLinkRepository{}
		linkRepo.On("GetByTargetID", ctx, itemID).Return(nil, errors.New("database error"))

		service := NewGraphAnalysisServiceImpl(itemRepo, linkRepo, &GraphMockCache{}, nil)

		result, err := service.AnalyzeItemDependencies(ctx, itemID)
		assert.Error(t, err)
		assert.Nil(t, result)
		assert.Contains(t, err.Error(), "failed to get direct dependents")
	})
}

// ============================================================================
// IMPACT ANALYSIS TESTS
// ============================================================================

type impactAnalysisCase struct {
	name   string
	setup  func(ctx context.Context, itemRepo *GraphMockItemRepository, linkRepo *GraphMockLinkRepository, itemID string)
	assert func(t *testing.T, itemID string, result *ImpactAnalysis)
}

func impactAnalysisBasicCases() []impactAnalysisCase {
	return []impactAnalysisCase{
		{
			name: "analyzes item with no impact",
			setup: func(ctx context.Context, itemRepo *GraphMockItemRepository, linkRepo *GraphMockLinkRepository, itemID string) {
				item := createTestItem(itemID, "Feature 1", "feature")
				itemRepo.On("GetByID", ctx, itemID).Return(item, nil)
				linkRepo.On("GetByTargetID", ctx, itemID).Return([]*models.Link{}, nil)
			},
			assert: func(t *testing.T, itemID string, result *ImpactAnalysis) {
				assert.NotNil(t, result)
				assert.Equal(t, itemID, result.ItemID)
				assert.Empty(t, result.DirectImpact)
				assert.Empty(t, result.IndirectImpact)
				assert.Equal(t, "low", result.RiskLevel)
			},
		},
		{
			name: "analyzes item with direct impact",
			setup: func(ctx context.Context, itemRepo *GraphMockItemRepository, linkRepo *GraphMockLinkRepository, itemID string) {
				item := createTestItem(itemID, "Feature 1", "feature")
				links := []*models.Link{
					createTestLink("link-1", "item-2", itemID, "depends_on"),
					createTestLink("link-2", "item-3", itemID, "depends_on"),
				}
				itemRepo.On("GetByID", ctx, itemID).Return(item, nil)
				linkRepo.On("GetByTargetID", ctx, itemID).Return(links, nil)
				linkRepo.On("GetByTargetID", ctx, "item-2").Return([]*models.Link{}, nil)
				linkRepo.On("GetByTargetID", ctx, "item-3").Return([]*models.Link{}, nil)
			},
			assert: func(t *testing.T, _ string, result *ImpactAnalysis) {
				assert.Len(t, result.DirectImpact, 2)
				assert.Contains(t, result.DirectImpact, "item-2")
				assert.Contains(t, result.DirectImpact, "item-3")
				assert.Empty(t, result.IndirectImpact)
				assert.Equal(t, "low", result.RiskLevel)
			},
		},
	}
}

func impactAnalysisComplexCases() []impactAnalysisCase {
	return []impactAnalysisCase{
		{
			name: "analyzes item with indirect impact",
			setup: func(ctx context.Context, itemRepo *GraphMockItemRepository, linkRepo *GraphMockLinkRepository, itemID string) {
				item := createTestItem(itemID, "Feature 1", "feature")
				links1 := []*models.Link{
					createTestLink("link-1", "item-2", itemID, "depends_on"),
				}
				links2 := []*models.Link{
					createTestLink("link-2", "item-3", "item-2", "depends_on"),
				}
				itemRepo.On("GetByID", ctx, itemID).Return(item, nil)
				linkRepo.On("GetByTargetID", ctx, itemID).Return(links1, nil)
				linkRepo.On("GetByTargetID", ctx, "item-2").Return(links2, nil)
				linkRepo.On("GetByTargetID", ctx, "item-3").Return([]*models.Link{}, nil)
			},
			assert: func(t *testing.T, _ string, result *ImpactAnalysis) {
				assert.Len(t, result.DirectImpact, 1)
				assert.Contains(t, result.DirectImpact, "item-2")
				assert.Len(t, result.IndirectImpact, 1)
				assert.Contains(t, result.IndirectImpact, "item-3")
				assert.Equal(t, "low", result.RiskLevel)
			},
		},
		{
			name: "calculates medium risk level",
			setup: func(ctx context.Context, itemRepo *GraphMockItemRepository, linkRepo *GraphMockLinkRepository, itemID string) {
				item := createTestItem(itemID, "Feature 1", "feature")
				directLinks := []*models.Link{
					createTestLink("link-1", "item-2", itemID, "depends_on"),
					createTestLink("link-2", "item-3", itemID, "depends_on"),
					createTestLink("link-3", "item-4", itemID, "depends_on"),
				}
				indirectLinks1 := []*models.Link{
					createTestLink("link-4", "item-5", "item-2", "depends_on"),
				}
				indirectLinks2 := []*models.Link{
					createTestLink("link-5", "item-6", "item-3", "depends_on"),
				}
				itemRepo.On("GetByID", ctx, itemID).Return(item, nil)
				linkRepo.On("GetByTargetID", ctx, itemID).Return(directLinks, nil)
				linkRepo.On("GetByTargetID", ctx, "item-2").Return(indirectLinks1, nil)
				linkRepo.On("GetByTargetID", ctx, "item-3").Return(indirectLinks2, nil)
				linkRepo.On("GetByTargetID", ctx, "item-4").Return([]*models.Link{}, nil)
				linkRepo.On("GetByTargetID", ctx, "item-5").Return([]*models.Link{}, nil)
				linkRepo.On("GetByTargetID", ctx, "item-6").Return([]*models.Link{}, nil)
			},
			assert: func(t *testing.T, _ string, result *ImpactAnalysis) {
				assert.Equal(t, "medium", result.RiskLevel)
			},
		},
	}
}

func impactAnalysisCoreCases() []impactAnalysisCase {
	return append(impactAnalysisBasicCases(), impactAnalysisComplexCases()...)
}

func impactAnalysisEdgeCases() []impactAnalysisCase {
	return []impactAnalysisCase{
		{
			name: "calculates high risk level",
			setup: func(ctx context.Context, itemRepo *GraphMockItemRepository, linkRepo *GraphMockLinkRepository, itemID string) {
				item := createTestItem(itemID, "Feature 1", "feature")
				directLinks := make([]*models.Link, 8)
				for i := 0; i < 8; i++ {
					directLinks[i] = createTestLink(
						fmt.Sprintf("link-%d", i),
						fmt.Sprintf("item-%d", i+2),
						itemID,
						"depends_on",
					)
				}
				itemRepo.On("GetByID", ctx, itemID).Return(item, nil)
				linkRepo.On("GetByTargetID", ctx, itemID).Return(directLinks, nil)
				for i := 0; i < 8; i++ {
					indirectLink := []*models.Link{
						createTestLink(
							fmt.Sprintf("link-i-%d", i),
							fmt.Sprintf("item-ind-%d", i),
							fmt.Sprintf("item-%d", i+2),
							"depends_on",
						),
					}
					linkRepo.On("GetByTargetID", ctx, fmt.Sprintf("item-%d", i+2)).Return(indirectLink, nil)
					linkRepo.On("GetByTargetID", ctx, fmt.Sprintf("item-ind-%d", i)).Return([]*models.Link{}, nil)
				}
			},
			assert: func(t *testing.T, _ string, result *ImpactAnalysis) {
				assert.Equal(t, "high", result.RiskLevel)
			},
		},
	}
}

func impactAnalysisCases() []impactAnalysisCase {
	return append(impactAnalysisCoreCases(), impactAnalysisEdgeCases()...)
}

func runImpactAnalysisCase(
	ctx context.Context,
	t *testing.T,
	service *GraphAnalysisServiceImpl,
	itemRepo *GraphMockItemRepository,
	linkRepo *GraphMockLinkRepository,
	itemID string,
	tc impactAnalysisCase,
) {
	t.Helper()
	tc.setup(ctx, itemRepo, linkRepo, itemID)
	result, err := service.GetItemImpactAnalysis(ctx, itemID)
	require.NoError(t, err)
	tc.assert(t, itemID, result)
}

func TestGetItemImpactAnalysis_Success(t *testing.T) {
	ctx := context.Background()

	for _, tc := range impactAnalysisCases() {
		t.Run(tc.name, func(t *testing.T) {
			service, itemRepo, linkRepo := createTestGraphService(t)
			runImpactAnalysisCase(ctx, t, service, itemRepo, linkRepo, testItem1ID, tc)
		})
	}
}

func TestGetItemImpactAnalysis_Errors(t *testing.T) {
	service, itemRepo, _ := createTestGraphService(t)
	ctx := context.Background()

	t.Run("returns error for empty itemID", func(t *testing.T) {
		result, err := service.GetItemImpactAnalysis(ctx, "")
		assert.Error(t, err)
		assert.Nil(t, result)
		assert.Contains(t, err.Error(), "itemID cannot be empty")
	})

	t.Run("returns error when item not found", func(t *testing.T) {
		itemID := testNonexistentID
		itemRepo.On("GetByID", ctx, itemID).Return(nil, errors.New("not found"))

		result, err := service.GetItemImpactAnalysis(ctx, itemID)
		assert.Error(t, err)
		assert.Nil(t, result)
	})
}

// ============================================================================
// GRAPH VISUALIZATION TESTS
// ============================================================================

type visualizeDependencyGraphCase struct {
	name   string
	setup  func(ctx context.Context, itemRepo *GraphMockItemRepository, linkRepo *GraphMockLinkRepository, itemID string)
	assert func(t *testing.T, itemID string, result string)
}

func visualizeDependencyGraphBasicCases() []visualizeDependencyGraphCase {
	return []visualizeDependencyGraphCase{
		{
			name: "generates DOT graph for single item",
			setup: func(ctx context.Context, itemRepo *GraphMockItemRepository, linkRepo *GraphMockLinkRepository, itemID string) {
				item := createTestItem(itemID, "Feature 1", "feature")
				itemRepo.On("GetByID", ctx, itemID).Return(item, nil)
				linkRepo.On("GetBySourceID", ctx, itemID).Return([]*models.Link{}, nil)
				linkRepo.On("GetByTargetID", ctx, itemID).Return([]*models.Link{}, nil)
			},
			assert: func(t *testing.T, itemID string, result string) {
				assert.Contains(t, result, "digraph dependencies")
				assert.Contains(t, result, itemID)
				assert.Contains(t, result, "Feature 1")
				assert.Contains(t, result, "lightgreen")
			},
		},
		{
			name: "generates DOT graph with dependencies",
			setup: func(ctx context.Context, itemRepo *GraphMockItemRepository, linkRepo *GraphMockLinkRepository, itemID string) {
				item1 := createTestItem(itemID, "Feature 1", "feature")
				item2 := createTestItem("item-2", "Feature 2", "feature")
				link := createTestLink("link-1", itemID, "item-2", "depends_on")
				itemRepo.On("GetByID", ctx, itemID).Return(item1, nil)
				itemRepo.On("GetByID", ctx, "item-2").Return(item2, nil)
				linkRepo.On("GetBySourceID", ctx, itemID).Return([]*models.Link{link}, nil)
				linkRepo.On("GetByTargetID", ctx, itemID).Return([]*models.Link{}, nil)
				linkRepo.On("GetBySourceID", ctx, "item-2").Return([]*models.Link{}, nil)
				linkRepo.On("GetByTargetID", ctx, "item-2").Return([]*models.Link{link}, nil)
			},
			assert: func(t *testing.T, itemID string, result string) {
				assert.Contains(t, result, itemID)
				assert.Contains(t, result, "item-2")
				assert.Contains(t, result, "depends_on")
				assert.Contains(t, result, "->")
			},
		},
	}
}

func visualizeDependencyGraphStyleCases() []visualizeDependencyGraphCase {
	return []visualizeDependencyGraphCase{
		{
			name: "applies different styles for link types",
			setup: func(ctx context.Context, itemRepo *GraphMockItemRepository, linkRepo *GraphMockLinkRepository, itemID string) {
				item1 := createTestItem(itemID, "Feature 1", "feature")
				item2 := createTestItem("item-2", "Task 1", "task")
				link := createTestLink("link-1", itemID, "item-2", "blocks")
				itemRepo.On("GetByID", ctx, itemID).Return(item1, nil)
				itemRepo.On("GetByID", ctx, "item-2").Return(item2, nil)
				linkRepo.On("GetBySourceID", ctx, itemID).Return([]*models.Link{link}, nil)
				linkRepo.On("GetByTargetID", ctx, itemID).Return([]*models.Link{}, nil)
				linkRepo.On("GetBySourceID", ctx, "item-2").Return([]*models.Link{}, nil)
				linkRepo.On("GetByTargetID", ctx, "item-2").Return([]*models.Link{link}, nil)
			},
			assert: func(t *testing.T, _ string, result string) {
				assert.Contains(t, result, "blocks")
				assert.Contains(t, result, "color=red")
			},
		},
		{
			name: "escapes quotes in item titles",
			setup: func(ctx context.Context, itemRepo *GraphMockItemRepository, linkRepo *GraphMockLinkRepository, itemID string) {
				item := createTestItem(itemID, "Feature \"quoted\" 1", "feature")
				itemRepo.On("GetByID", ctx, itemID).Return(item, nil)
				linkRepo.On("GetBySourceID", ctx, itemID).Return([]*models.Link{}, nil)
				linkRepo.On("GetByTargetID", ctx, itemID).Return([]*models.Link{}, nil)
			},
			assert: func(t *testing.T, _ string, result string) {
				assert.Contains(t, result, "Feature \\\"quoted\\\" 1")
			},
		},
	}
}

func visualizeDependencyGraphCoreCases() []visualizeDependencyGraphCase {
	return append(visualizeDependencyGraphBasicCases(), visualizeDependencyGraphStyleCases()...)
}

func visualizeDependencyGraphEdgeCases() []visualizeDependencyGraphCase {
	return []visualizeDependencyGraphCase{
		{
			name: "respects max depth limit",
			setup: func(ctx context.Context, itemRepo *GraphMockItemRepository, linkRepo *GraphMockLinkRepository, itemID string) {
				item1 := createTestItem(itemID, "Feature 1", "feature")
				item2 := createTestItem("item-2", "Feature 2", "feature")
				item3 := createTestItem("item-3", "Feature 3", "feature")
				item4 := createTestItem("item-4", "Feature 4", "feature")
				link1 := createTestLink("link-1", itemID, "item-2", "depends_on")
				link2 := createTestLink("link-2", "item-2", "item-3", "depends_on")
				link3 := createTestLink("link-3", "item-3", "item-4", "depends_on")
				itemRepo.On("GetByID", ctx, itemID).Return(item1, nil)
				itemRepo.On("GetByID", ctx, "item-2").Return(item2, nil)
				itemRepo.On("GetByID", ctx, "item-3").Return(item3, nil)
				itemRepo.On("GetByID", ctx, "item-4").Return(item4, nil)
				linkRepo.On("GetBySourceID", ctx, itemID).Return([]*models.Link{link1}, nil)
				linkRepo.On("GetByTargetID", ctx, itemID).Return([]*models.Link{}, nil)
				linkRepo.On("GetBySourceID", ctx, "item-2").Return([]*models.Link{link2}, nil)
				linkRepo.On("GetByTargetID", ctx, "item-2").Return([]*models.Link{link1}, nil)
				linkRepo.On("GetBySourceID", ctx, "item-3").Return([]*models.Link{link3}, nil)
				linkRepo.On("GetByTargetID", ctx, "item-3").Return([]*models.Link{link2}, nil)
				linkRepo.On("GetBySourceID", ctx, "item-4").Return([]*models.Link{}, nil)
				linkRepo.On("GetByTargetID", ctx, "item-4").Return([]*models.Link{link3}, nil)
			},
			assert: func(t *testing.T, itemID string, result string) {
				assert.Contains(t, result, itemID)
				assert.Contains(t, result, "item-2")
				assert.Contains(t, result, "item-3")
			},
		},
		{
			name: "deduplicates edges in graph",
			setup: func(ctx context.Context, itemRepo *GraphMockItemRepository, linkRepo *GraphMockLinkRepository, itemID string) {
				item1 := createTestItem(itemID, "Feature 1", "feature")
				item2 := createTestItem("item-2", "Feature 2", "feature")
				link := createTestLink("link-1", itemID, "item-2", "depends_on")
				itemRepo.On("GetByID", ctx, itemID).Return(item1, nil)
				itemRepo.On("GetByID", ctx, "item-2").Return(item2, nil)
				linkRepo.On("GetBySourceID", ctx, itemID).Return([]*models.Link{link}, nil)
				linkRepo.On("GetByTargetID", ctx, itemID).Return([]*models.Link{}, nil)
				linkRepo.On("GetBySourceID", ctx, "item-2").Return([]*models.Link{}, nil)
				linkRepo.On("GetByTargetID", ctx, "item-2").Return([]*models.Link{link}, nil)
			},
			assert: func(t *testing.T, _ string, result string) {
				edgeCount := strings.Count(result, "item-1\" -> \"item-2\"")
				assert.Equal(t, 1, edgeCount, "Edge should appear only once in graph")
			},
		},
	}
}

func visualizeDependencyGraphCases() []visualizeDependencyGraphCase {
	return append(visualizeDependencyGraphCoreCases(), visualizeDependencyGraphEdgeCases()...)
}

func runVisualizeDependencyGraphCase(
	ctx context.Context,
	t *testing.T,
	service *GraphAnalysisServiceImpl,
	itemRepo *GraphMockItemRepository,
	linkRepo *GraphMockLinkRepository,
	itemID string,
	tc visualizeDependencyGraphCase,
) {
	t.Helper()
	tc.setup(ctx, itemRepo, linkRepo, itemID)
	result, err := service.VisualizeDependencyGraph(ctx, itemID)
	require.NoError(t, err)
	tc.assert(t, itemID, result)
}

func TestVisualizeDependencyGraph_Success(t *testing.T) {
	ctx := context.Background()

	for _, tc := range visualizeDependencyGraphCases() {
		t.Run(tc.name, func(t *testing.T) {
			service, itemRepo, linkRepo := createTestGraphService(t)
			runVisualizeDependencyGraphCase(ctx, t, service, itemRepo, linkRepo, testItem1ID, tc)
		})
	}
}

func TestVisualizeDependencyGraph_Errors(t *testing.T) {
	service, itemRepo, _ := createTestGraphService(t)
	ctx := context.Background()

	t.Run("returns error for empty itemID", func(t *testing.T) {
		result, err := service.VisualizeDependencyGraph(ctx, "")
		assert.Error(t, err)
		assert.Empty(t, result)
		assert.Contains(t, err.Error(), "itemID cannot be empty")
	})

	t.Run("returns error when item not found", func(t *testing.T) {
		itemID := testNonexistentID
		itemRepo.On("GetByID", ctx, itemID).Return(nil, errors.New("not found"))

		result, err := service.VisualizeDependencyGraph(ctx, itemID)
		assert.Error(t, err)
		assert.Empty(t, result)
	})

	t.Run("returns error when item is nil", func(t *testing.T) {
		itemID := testItem1ID
		itemRepo.On("GetByID", ctx, itemID).Return(nil, nil)

		result, err := service.VisualizeDependencyGraph(ctx, itemID)
		assert.Error(t, err)
		assert.Empty(t, result)
	})
}

// ============================================================================
// HELPER FUNCTION TESTS
// ============================================================================

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
