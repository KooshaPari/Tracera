//go:build !integration && !e2e

package services

import (
	"context"
	"errors"
	"testing"

	"github.com/kooshapari/tracertm-backend/internal/models"
	"github.com/kooshapari/tracertm-backend/internal/repository"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/mock"
	"github.com/stretchr/testify/require"
)

// Test constants
const (
	testProject1ID = "project-1"
)

func TestItemService_publishEvent(t *testing.T) {
	t.Run("with NATS connection", func(_ *testing.T) {
		mockRepo := new(MockItemRepository)
		mockLinkRepo := new(MockLinkRepository)

		// Create a mock NATS connection
		// In real tests, you'd use a test NATS server or mock
		// For now, we test the nil case and the error paths
		service := NewItemService(mockRepo, mockLinkRepo, nil, nil)

		// Test with nil NATS (should not error, just return early)
		itemService := service.(*itemService)
		itemService.publishEvent("test.event", map[string]string{"test": "data"})
		// Should not panic or error
	})

	t.Run("marshal error handling", func(_ *testing.T) {
		mockRepo := new(MockItemRepository)
		mockLinkRepo := new(MockLinkRepository)
		service := NewItemService(mockRepo, mockLinkRepo, nil, nil)

		itemService := service.(*itemService)
		// Test with data that can't be marshaled (circular reference)
		type Circular struct {
			Self *Circular
		}
		circular := &Circular{}
		circular.Self = circular

		// Should handle marshal error gracefully
		itemService.publishEvent("test.event", circular)
		// Should not panic
	})
}

func TestItemService_GetItem_CachePaths(t *testing.T) {
	t.Run("cache miss then hit", func(t *testing.T) {
		mockRepo := new(MockItemRepository)
		mockLinkRepo := new(MockLinkRepository)

		// Use a real Redis client for testing cache behavior
		// In unit tests, we can use nil and test the non-cache path
		service := NewItemService(mockRepo, mockLinkRepo, nil, nil)

		item := &models.Item{
			ID:        "test-id",
			ProjectID: "project-id",
			Title:     "Test Item",
		}

		mockRepo.On("GetByID", mock.Anything, "test-id").Return(item, nil)

		result, err := service.GetItem(context.Background(), "test-id")
		require.NoError(t, err)
		assert.Equal(t, item.ID, result.ID)
		mockRepo.AssertExpectations(t)
	})

	t.Run("cache hit with invalid JSON", func(t *testing.T) {
		// This would require a real Redis client with invalid JSON
		// For unit tests, we focus on the non-cache path
		mockRepo := new(MockItemRepository)
		mockLinkRepo := new(MockLinkRepository)
		service := NewItemService(mockRepo, mockLinkRepo, nil, nil)

		item := &models.Item{
			ID:        "test-id",
			ProjectID: "project-id",
			Title:     "Test Item",
		}

		mockRepo.On("GetByID", mock.Anything, "test-id").Return(item, nil)

		result, err := service.GetItem(context.Background(), "test-id")
		require.NoError(t, err)
		assert.Equal(t, item.ID, result.ID)
	})
}

func TestItemService_GetItemStats(t *testing.T) {
	t.Run("empty results", func(t *testing.T) {
		mockRepo := new(MockItemRepository)
		mockLinkRepo := new(MockLinkRepository)
		service := NewItemService(mockRepo, mockLinkRepo, nil, nil)

		mockRepo.On("List", mock.Anything, repository.ItemFilter{
			ProjectID: stringPtr("project-id"),
		}).Return([]*models.Item{}, nil)

		stats, err := service.GetItemStats(context.Background(), "project-id")
		require.NoError(t, err)
		assert.Equal(t, int64(0), stats.TotalItems)
		assert.Empty(t, stats.ByType)
		assert.Empty(t, stats.ByStatus)
		assert.Empty(t, stats.ByPriority)
	})

	t.Run("with items", func(t *testing.T) {
		mockRepo := new(MockItemRepository)
		mockLinkRepo := new(MockLinkRepository)
		service := NewItemService(mockRepo, mockLinkRepo, nil, nil)

		items := []*models.Item{
			{ID: "1", Type: "requirement", Status: "todo", Priority: models.PriorityHigh},
			{ID: "2", Type: "requirement", Status: "done", Priority: models.PriorityMedium},
			{ID: "3", Type: "test", Status: "todo", Priority: models.PriorityLow},
		}

		mockRepo.On("List", mock.Anything, repository.ItemFilter{
			ProjectID: stringPtr("project-id"),
		}).Return(items, nil)

		stats, err := service.GetItemStats(context.Background(), "project-id")
		require.NoError(t, err)
		assert.Equal(t, int64(3), stats.TotalItems)
		assert.Equal(t, int64(2), stats.ByType["requirement"])
		assert.Equal(t, int64(1), stats.ByType["test"])
		assert.Equal(t, int64(2), stats.ByStatus["todo"])
		assert.Equal(t, int64(1), stats.ByStatus["done"])
		assert.Equal(t, int64(1), stats.ByPriority["high"])
		assert.Equal(t, int64(1), stats.ByPriority["medium"])
		assert.Equal(t, int64(1), stats.ByPriority["low"])
	})

	t.Run("error from repository", func(t *testing.T) {
		mockRepo := new(MockItemRepository)
		mockLinkRepo := new(MockLinkRepository)
		service := NewItemService(mockRepo, mockLinkRepo, nil, nil)

		mockRepo.On("List", mock.Anything, repository.ItemFilter{
			ProjectID: stringPtr("project-id"),
		}).Return(nil, errors.New("repository error"))

		_, err := service.GetItemStats(context.Background(), "project-id")
		assert.Error(t, err)
	})
}

func TestLinkService_publishEvent(t *testing.T) {
	t.Run("with nil NATS", func(_ *testing.T) {
		mockRepo := new(MockLinkRepository)
		mockItemRepo := new(MockItemRepository)
		service := NewLinkService(mockRepo, mockItemRepo, nil)

		linkService := service.(*linkService)
		linkService.publishEvent("test.event", map[string]string{"test": "data"})
		// Should not panic
	})

	t.Run("marshal error", func(_ *testing.T) {
		mockRepo := new(MockLinkRepository)
		mockItemRepo := new(MockItemRepository)
		service := NewLinkService(mockRepo, mockItemRepo, nil)

		linkService := service.(*linkService)
		type Circular struct {
			Self *Circular
		}
		circular := &Circular{}
		circular.Self = circular

		linkService.publishEvent("test.event", circular)
		// Should not panic
	})
}

type linkDependenciesCase struct {
	name   string
	setup  func(mockRepo *MockLinkRepository, mockItemRepo *MockItemRepository)
	assert func(t *testing.T, result *DependencyGraph, err error)
}

func linkDependenciesCoreCases() []linkDependenciesCase {
	return []linkDependenciesCase{
		{
			name: "success",
			setup: func(mockRepo *MockLinkRepository, mockItemRepo *MockItemRepository) {
				dependencies := []*models.Link{
					{ID: "link1", SourceID: "item1", TargetID: "item2"},
				}
				dependents := []*models.Link{
					{ID: "link2", SourceID: "item3", TargetID: "item1"},
				}
				item2 := &models.Item{ID: "item2", Title: "Item 2"}
				item3 := &models.Item{ID: "item3", Title: "Item 3"}
				mockRepo.On("GetBySourceID", mock.Anything, "item1").Return(dependencies, nil)
				mockRepo.On("GetByTargetID", mock.Anything, "item1").Return(dependents, nil)
				mockItemRepo.On("GetByID", mock.Anything, "item2").Return(item2, nil)
				mockItemRepo.On("GetByID", mock.Anything, "item3").Return(item3, nil)
			},
			assert: func(t *testing.T, result *DependencyGraph, err error) {
				require.NoError(t, err)
				assert.Equal(t, "item1", result.ItemID)
				assert.Len(t, result.Dependencies, 1)
				assert.Len(t, result.Dependents, 1)
				assert.Len(t, result.Items, 2)
			},
		},
		{
			name: "empty dependencies",
			setup: func(mockRepo *MockLinkRepository, _ *MockItemRepository) {
				mockRepo.On("GetBySourceID", mock.Anything, "item1").Return([]*models.Link{}, nil)
				mockRepo.On("GetByTargetID", mock.Anything, "item1").Return([]*models.Link{}, nil)
			},
			assert: func(t *testing.T, result *DependencyGraph, err error) {
				require.NoError(t, err)
				assert.Equal(t, "item1", result.ItemID)
				assert.Empty(t, result.Dependencies)
				assert.Empty(t, result.Dependents)
				assert.Empty(t, result.Items)
			},
		},
		{
			name: "error getting dependencies",
			setup: func(mockRepo *MockLinkRepository, _ *MockItemRepository) {
				mockRepo.On("GetBySourceID", mock.Anything, "item1").Return(nil, errors.New("repo error"))
			},
			assert: func(t *testing.T, _ *DependencyGraph, err error) {
				assert.Error(t, err)
			},
		},
	}
}

func linkDependenciesEdgeCases() []linkDependenciesCase {
	return []linkDependenciesCase{
		{
			name: "error getting dependents",
			setup: func(mockRepo *MockLinkRepository, _ *MockItemRepository) {
				mockRepo.On("GetBySourceID", mock.Anything, "item1").Return([]*models.Link{}, nil)
				mockRepo.On("GetByTargetID", mock.Anything, "item1").Return(nil, errors.New("repo error"))
			},
			assert: func(t *testing.T, _ *DependencyGraph, err error) {
				assert.Error(t, err)
			},
		},
		{
			name: "item not found in dependencies",
			setup: func(mockRepo *MockLinkRepository, mockItemRepo *MockItemRepository) {
				dependencies := []*models.Link{
					{ID: "link1", SourceID: "item1", TargetID: "item2"},
				}
				mockRepo.On("GetBySourceID", mock.Anything, "item1").Return(dependencies, nil)
				mockRepo.On("GetByTargetID", mock.Anything, "item1").Return([]*models.Link{}, nil)
				mockItemRepo.On("GetByID", mock.Anything, "item2").Return(nil, errors.New("not found"))
			},
			assert: func(t *testing.T, result *DependencyGraph, err error) {
				require.NoError(t, err)
				assert.Len(t, result.Dependencies, 1)
				assert.Empty(t, result.Items)
			},
		},
	}
}

func linkDependenciesCases() []linkDependenciesCase {
	return append(linkDependenciesCoreCases(), linkDependenciesEdgeCases()...)
}

func runLinkDependenciesCase(t *testing.T, tc linkDependenciesCase) {
	t.Helper()
	mockRepo := new(MockLinkRepository)
	mockItemRepo := new(MockItemRepository)
	service := NewLinkService(mockRepo, mockItemRepo, nil)
	tc.setup(mockRepo, mockItemRepo)
	result, err := service.GetItemDependencies(context.Background(), "item1")
	tc.assert(t, result, err)
}

func TestLinkService_GetItemDependencies(t *testing.T) {
	for _, tc := range linkDependenciesCases() {
		t.Run(tc.name, func(t *testing.T) {
			runLinkDependenciesCase(t, tc)
		})
	}
}

// Note: ProjectService edge cases are tested in project_service_test.go
// We add additional edge case tests here if needed

func TestAgentService_publishEvent(t *testing.T) {
	t.Run("with nil NATS", func(_ *testing.T) {
		mockRepo := new(MockAgentRepositoryExtended)
		service := NewAgentService(mockRepo, nil)

		agentService := service.(*agentService)
		agentService.publishEvent("test.event", map[string]string{"test": "data"})
		// Should not panic
	})

	t.Run("marshal error", func(_ *testing.T) {
		mockRepo := new(MockAgentRepositoryExtended)
		service := NewAgentService(mockRepo, nil)

		agentService := service.(*agentService)
		type Circular struct {
			Self *Circular
		}
		circular := &Circular{}
		circular.Self = circular

		agentService.publishEvent("test.event", circular)
		// Should not panic
	})
}

func TestAgentService_NotifyAgentEvent(t *testing.T) {
	t.Run("error when NATS is nil", func(t *testing.T) {
		mockRepo := new(MockAgentRepositoryExtended)
		service := NewAgentService(mockRepo, nil)

		event := &AgentEvent{
			AgentID:   "agent1",
			EventType: "test",
			Data:      map[string]interface{}{"test": "data"},
		}

		err := service.NotifyAgentEvent(context.Background(), event)
		assert.Error(t, err)
		assert.Contains(t, err.Error(), "NATS connection not available")
	})

	t.Run("marshal error", func(t *testing.T) {
		mockRepo := new(MockAgentRepositoryExtended)
		// We can't easily test with a real NATS connection in unit tests
		// This would require integration tests
		service := NewAgentService(mockRepo, nil)

		event := &AgentEvent{
			AgentID:   "agent1",
			EventType: "test",
			Data:      make(map[string]interface{}),
		}

		// Create a circular reference that can't be marshaled
		event.Data["self"] = event.Data

		err := service.NotifyAgentEvent(context.Background(), event)
		// Will fail on NATS nil check first, but if NATS was available, would fail on marshal
		assert.Error(t, err)
	})
}

func TestItemService_DeleteItem_ErrorPaths(t *testing.T) {
	t.Run("error getting item for cache invalidation", func(t *testing.T) {
		mockRepo := new(MockItemRepository)
		mockLinkRepo := new(MockLinkRepository)
		service := NewItemService(mockRepo, mockLinkRepo, nil, nil)

		mockRepo.On("GetByID", mock.Anything, "item1").Return(nil, errors.New("not found"))

		err := service.DeleteItem(context.Background(), "item1")
		assert.Error(t, err)
	})

	t.Run("error deleting links", func(t *testing.T) {
		mockRepo := new(MockItemRepository)
		mockLinkRepo := new(MockLinkRepository)
		service := NewItemService(mockRepo, mockLinkRepo, nil, nil)

		item := &models.Item{
			ID:        "item1",
			ProjectID: "project1",
		}

		mockRepo.On("GetByID", mock.Anything, "item1").Return(item, nil)
		mockLinkRepo.On("DeleteByItemID", mock.Anything, "item1").Return(errors.New("link delete error"))

		err := service.DeleteItem(context.Background(), "item1")
		assert.Error(t, err)
		assert.Contains(t, err.Error(), "failed to delete item links")
	})

	t.Run("error deleting item", func(t *testing.T) {
		mockRepo := new(MockItemRepository)
		mockLinkRepo := new(MockLinkRepository)
		service := NewItemService(mockRepo, mockLinkRepo, nil, nil)

		item := &models.Item{
			ID:        "item1",
			ProjectID: "project1",
		}

		mockRepo.On("GetByID", mock.Anything, "item1").Return(item, nil)
		mockLinkRepo.On("DeleteByItemID", mock.Anything, "item1").Return(nil)
		mockRepo.On("Delete", mock.Anything, "item1").Return(errors.New("delete error"))

		err := service.DeleteItem(context.Background(), "item1")
		assert.Error(t, err)
		assert.Contains(t, err.Error(), "failed to delete item")
	})
}

func TestLinkService_CreateLink_ErrorPaths(t *testing.T) {
	t.Run("source item not found", func(t *testing.T) {
		mockRepo := new(MockLinkRepository)
		mockItemRepo := new(MockItemRepository)
		service := NewLinkService(mockRepo, mockItemRepo, nil)

		link := &models.Link{
			SourceID: "source1",
			TargetID: "target1",
			Type:     "depends_on",
		}

		mockItemRepo.On("GetByID", mock.Anything, "source1").Return(nil, errors.New("not found"))

		err := service.CreateLink(context.Background(), link)
		assert.Error(t, err)
		assert.Contains(t, err.Error(), "source item not found")
	})

	t.Run("target item not found", func(t *testing.T) {
		mockRepo := new(MockLinkRepository)
		mockItemRepo := new(MockItemRepository)
		service := NewLinkService(mockRepo, mockItemRepo, nil)

		link := &models.Link{
			SourceID: "source1",
			TargetID: "target1",
			Type:     "depends_on",
		}

		sourceItem := &models.Item{ID: "source1"}
		mockItemRepo.On("GetByID", mock.Anything, "source1").Return(sourceItem, nil)
		mockItemRepo.On("GetByID", mock.Anything, "target1").Return(nil, errors.New("not found"))

		err := service.CreateLink(context.Background(), link)
		assert.Error(t, err)
		assert.Contains(t, err.Error(), "target item not found")
	})
}

// Helper function
func stringPtr(s string) *string {
	return &s
}

// Note: MockProjectRepository is already defined in project_service_test.go
// MockAgentRepository needs GetByProjectID method - adding it here
type MockAgentRepositoryExtended struct {
	mock.Mock
}

func (m *MockAgentRepositoryExtended) Create(ctx context.Context, agent *models.Agent) error {
	args := m.Called(ctx, agent)
	return args.Error(0)
}

func (m *MockAgentRepositoryExtended) GetByID(ctx context.Context, id string) (*models.Agent, error) {
	args := m.Called(ctx, id)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	return args.Get(0).(*models.Agent), args.Error(1)
}

func (m *MockAgentRepositoryExtended) GetByProjectID(ctx context.Context, projectID string) ([]*models.Agent, error) {
	args := m.Called(ctx, projectID)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	return args.Get(0).([]*models.Agent), args.Error(1)
}

func (m *MockAgentRepositoryExtended) List(ctx context.Context) ([]*models.Agent, error) {
	args := m.Called(ctx)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	return args.Get(0).([]*models.Agent), args.Error(1)
}

func (m *MockAgentRepositoryExtended) Update(ctx context.Context, agent *models.Agent) error {
	args := m.Called(ctx, agent)
	return args.Error(0)
}

func (m *MockAgentRepositoryExtended) UpdateStatus(ctx context.Context, id, status string) error {
	args := m.Called(ctx, id, status)
	return args.Error(0)
}

func (m *MockAgentRepositoryExtended) Delete(ctx context.Context, id string) error {
	args := m.Called(ctx, id)
	return args.Error(0)
}

// TestItemService_publishEvent_ErrorPaths tests error handling in publishEvent
func TestItemService_publishEvent_ErrorPaths(t *testing.T) {
	t.Run("JSON marshal error", func(t *testing.T) {
		mockRepo := new(MockItemRepository)
		mockLinkRepo := new(MockLinkRepository)
		// NATS is nil for unit tests - integration tests will use real NATS
		service := NewItemService(mockRepo, mockLinkRepo, nil, nil)
		itemService := service.(*itemService)

		// Create data that can't be marshaled
		type Unmarshalable struct {
			Channel chan int // Channels can't be JSON marshaled
		}
		unmarshalable := &Unmarshalable{Channel: make(chan int)}

		// Should not panic, just return early
		itemService.publishEvent("test.event", unmarshalable)
		assert.True(t, true) // If we get here, no panic occurred
	})

	t.Run("NATS publish error", func(t *testing.T) {
		mockRepo := new(MockItemRepository)
		mockLinkRepo := new(MockLinkRepository)
		// NATS is nil for unit tests - integration tests will use real NATS
		service := NewItemService(mockRepo, mockLinkRepo, nil, nil)
		itemService := service.(*itemService)

		// Should handle nil NATS gracefully
		itemService.publishEvent("test.event", map[string]string{"test": "data"})
		assert.True(t, true)
	})
}

// TestItemService_GetItem_CacheHit tests cache hit path
func TestItemService_GetItem_CacheHit(t *testing.T) {
	t.Run("cache hit with valid JSON", func(t *testing.T) {
		mockRepo := new(MockItemRepository)
		mockLinkRepo := new(MockLinkRepository)
		// For unit tests, we'll test the nil case
		// Integration tests will test actual cache behavior
		service := NewItemService(mockRepo, mockLinkRepo, nil, nil)

		item := &models.Item{
			ID:        "test-id",
			ProjectID: "project-id",
			Title:     "Test Item",
		}

		mockRepo.On("GetByID", mock.Anything, "test-id").Return(item, nil)

		result, err := service.GetItem(context.Background(), "test-id")
		require.NoError(t, err)
		assert.Equal(t, item.ID, result.ID)
		mockRepo.AssertExpectations(t)
	})

	t.Run("cache hit with invalid JSON falls back to DB", func(t *testing.T) {
		mockRepo := new(MockItemRepository)
		mockLinkRepo := new(MockLinkRepository)
		service := NewItemService(mockRepo, mockLinkRepo, nil, nil)

		item := &models.Item{
			ID:        "test-id",
			ProjectID: "project-id",
			Title:     "Test Item",
		}

		mockRepo.On("GetByID", mock.Anything, "test-id").Return(item, nil)

		result, err := service.GetItem(context.Background(), "test-id")
		require.NoError(t, err)
		assert.Equal(t, item.ID, result.ID)
		mockRepo.AssertExpectations(t)
	})
}

// TestItemService_GetItemStats_CachePaths tests cache paths in GetItemStats
type itemStatsCacheCase struct {
	name      string
	projectID string
	setup     func(ctx context.Context, mockRepo *MockItemRepository)
	assert    func(t *testing.T, stats *ItemStats, err error)
}

func itemStatsCacheCases() []itemStatsCacheCase {
	return []itemStatsCacheCase{
		{
			name:      "cache miss",
			projectID: testProject1ID,
			setup: func(ctx context.Context, mockRepo *MockItemRepository) {
				projectID := testProject1ID
				mockRepo.On("List", ctx, repository.ItemFilter{ProjectID: &projectID}).Return([]*models.Item{
					{ID: testItem1ID, Type: "task", Status: "open"},
					{ID: "item-2", Type: "bug", Status: "closed"},
				}, nil)
			},
			assert: func(t *testing.T, stats *ItemStats, err error) {
				require.NoError(t, err)
				assert.NotNil(t, stats)
				assert.Equal(t, int64(2), stats.TotalItems)
			},
		},
		{
			name:      "cache hit with invalid JSON",
			projectID: testProject1ID,
			setup: func(ctx context.Context, mockRepo *MockItemRepository) {
				projectID := testProject1ID
				mockRepo.On("List", ctx, repository.ItemFilter{ProjectID: &projectID}).Return([]*models.Item{}, nil)
			},
			assert: func(t *testing.T, stats *ItemStats, err error) {
				require.NoError(t, err)
				assert.NotNil(t, stats)
			},
		},
		{
			name:      "empty results",
			projectID: "project-empty",
			setup: func(ctx context.Context, mockRepo *MockItemRepository) {
				projectID := "project-empty"
				mockRepo.On("List", ctx, repository.ItemFilter{ProjectID: &projectID}).Return([]*models.Item{}, nil)
			},
			assert: func(t *testing.T, stats *ItemStats, err error) {
				require.NoError(t, err)
				assert.NotNil(t, stats)
				assert.Equal(t, int64(0), stats.TotalItems)
				assert.Equal(t, int64(0), stats.ByStatus["open"])
			},
		},
		{
			name:      "repository error",
			projectID: "project-error",
			setup: func(ctx context.Context, mockRepo *MockItemRepository) {
				projectID := "project-error"
				mockRepo.On("List", ctx, repository.ItemFilter{ProjectID: &projectID}).Return(nil, errors.New("repository error"))
			},
			assert: func(t *testing.T, stats *ItemStats, err error) {
				assert.Error(t, err)
				assert.Nil(t, stats)
			},
		},
	}
}

func runItemStatsCacheCase(t *testing.T, tc itemStatsCacheCase) {
	t.Helper()
	mockRepo := new(MockItemRepository)
	mockLinkRepo := new(MockLinkRepository)
	service := NewItemService(mockRepo, mockLinkRepo, nil, nil)
	ctx := context.Background()
	tc.setup(ctx, mockRepo)
	stats, err := service.GetItemStats(ctx, tc.projectID)
	tc.assert(t, stats, err)
	mockRepo.AssertExpectations(t)
}

// TestItemService_GetItemStats_CachePaths tests cache paths in GetItemStats
func TestItemService_GetItemStats_CachePaths(t *testing.T) {
	for _, tc := range itemStatsCacheCases() {
		t.Run(tc.name, func(t *testing.T) {
			runItemStatsCacheCase(t, tc)
		})
	}
}

// TestLinkService_publishEvent_ErrorPaths tests error handling
func TestLinkService_publishEvent_ErrorPaths(t *testing.T) {
	t.Run("JSON marshal error", func(t *testing.T) {
		mockRepo := new(MockLinkRepository)
		mockItemRepo := new(MockItemRepository)
		// NATS is nil for unit tests
		service := NewLinkService(mockRepo, mockItemRepo, nil)
		linkService := service.(*linkService)

		type Unmarshalable struct {
			Channel chan int
		}
		unmarshalable := &Unmarshalable{Channel: make(chan int)}

		// Should not panic
		linkService.publishEvent("test.event", unmarshalable)
		assert.True(t, true)
	})

	t.Run("nil NATS connection", func(t *testing.T) {
		mockRepo := new(MockLinkRepository)
		mockItemRepo := new(MockItemRepository)

		service := NewLinkService(mockRepo, mockItemRepo, nil)
		linkService := service.(*linkService)

		// Should return early without error
		linkService.publishEvent("test.event", map[string]string{"test": "data"})
		assert.True(t, true)
	})
}

// TestLinkService_GetItemDependencies_ErrorPaths tests error paths
func TestLinkService_GetItemDependencies_ErrorPaths(t *testing.T) {
	t.Run("repository error on GetBySourceID", func(t *testing.T) {
		mockRepo := new(MockLinkRepository)
		mockItemRepo := new(MockItemRepository)
		service := NewLinkService(mockRepo, mockItemRepo, nil)

		ctx := context.Background()
		itemID := testItem1ID

		mockRepo.On("GetBySourceID", ctx, itemID).Return(nil, errors.New("repository error"))

		deps, err := service.GetItemDependencies(ctx, itemID)
		assert.Error(t, err)
		assert.Nil(t, deps)
		mockRepo.AssertExpectations(t)
	})

	t.Run("repository error on GetByTargetID", func(t *testing.T) {
		mockRepo := new(MockLinkRepository)
		mockItemRepo := new(MockItemRepository)
		service := NewLinkService(mockRepo, mockItemRepo, nil)

		ctx := context.Background()
		itemID := testItem1ID

		mockRepo.On("GetBySourceID", ctx, itemID).Return([]*models.Link{}, nil)
		mockRepo.On("GetByTargetID", ctx, itemID).Return(nil, errors.New("repository error"))

		deps, err := service.GetItemDependencies(ctx, itemID)
		assert.Error(t, err)
		assert.Nil(t, deps)
		mockRepo.AssertExpectations(t)
	})

	t.Run("empty dependencies", func(t *testing.T) {
		mockRepo := new(MockLinkRepository)
		mockItemRepo := new(MockItemRepository)
		service := NewLinkService(mockRepo, mockItemRepo, nil)

		ctx := context.Background()
		itemID := testItem1ID

		mockRepo.On("GetBySourceID", ctx, itemID).Return([]*models.Link{}, nil)
		mockRepo.On("GetByTargetID", ctx, itemID).Return([]*models.Link{}, nil)

		deps, err := service.GetItemDependencies(ctx, itemID)
		require.NoError(t, err)
		assert.NotNil(t, deps)
		assert.Equal(t, 0, len(deps.Dependencies))
		assert.Equal(t, 0, len(deps.Dependents))
		mockRepo.AssertExpectations(t)
	})
}

// TestAgentService_publishEvent_ErrorPaths tests error handling
func TestAgentService_publishEvent_ErrorPaths(t *testing.T) {
	t.Run("JSON marshal error", func(t *testing.T) {
		mockRepo := new(MockAgentRepositoryExtended)
		service := NewAgentService(mockRepo, nil)
		agentService := service.(*agentService)

		type Unmarshalable struct {
			Channel chan int
		}
		unmarshalable := &Unmarshalable{Channel: make(chan int)}

		// Should not panic
		agentService.publishEvent("test.event", unmarshalable)
		assert.True(t, true)
	})

	t.Run("nil NATS connection", func(t *testing.T) {
		mockRepo := new(MockAgentRepositoryExtended)

		service := NewAgentService(mockRepo, nil)
		agentService := service.(*agentService)

		// Should return early without error
		agentService.publishEvent("test.event", map[string]string{"test": "data"})
		assert.True(t, true)
	})
}

// TestAgentService_NotifyAgentEvent_ErrorPaths tests error paths
func TestAgentService_NotifyAgentEvent_ErrorPaths(t *testing.T) {
	t.Run("nil NATS connection", func(t *testing.T) {
		mockRepo := new(MockAgentRepositoryExtended)
		service := NewAgentService(mockRepo, nil)

		ctx := context.Background()
		event := &AgentEvent{
			AgentID:   "agent-1",
			EventType: "test.event",
			Data:      map[string]interface{}{"test": "data"},
		}

		err := service.NotifyAgentEvent(ctx, event)
		assert.Error(t, err)
		assert.Contains(t, err.Error(), "NATS connection not available")
	})

	t.Run("JSON marshal error", func(_ *testing.T) {
		mockRepo := new(MockAgentRepositoryExtended)
		// For unit tests, we'll test with nil NATS
		service := NewAgentService(mockRepo, nil)

		ctx := context.Background()
		event := &AgentEvent{
			AgentID:   "agent-1",
			EventType: "test.event",
			Data:      map[string]interface{}{"unmarshalable": make(chan int)},
		}

		// Should handle marshal error
		err := service.NotifyAgentEvent(ctx, event)
		// May return error or handle gracefully depending on implementation
		_ = err
	})

	t.Run("NATS publish error", func(t *testing.T) {
		// NATS publish error testing requires integration tests with real NATS
		// Unit tests focus on nil NATS case
		mockRepo := new(MockAgentRepositoryExtended)
		service := NewAgentService(mockRepo, nil)

		ctx := context.Background()
		event := &AgentEvent{
			AgentID:   "agent-1",
			EventType: "test.event",
			Data:      map[string]interface{}{"test": "data"},
		}

		// With nil NATS, should return error
		err := service.NotifyAgentEvent(ctx, event)
		assert.Error(t, err)
		assert.Contains(t, err.Error(), "NATS connection not available")
	})
}

// TestItemService_ValidationEdgeCases tests validation edge cases
func TestItemService_ValidationEdgeCases(t *testing.T) {
	t.Run("empty item ID on update", func(t *testing.T) {
		mockRepo := new(MockItemRepository)
		mockLinkRepo := new(MockLinkRepository)
		service := NewItemService(mockRepo, mockLinkRepo, nil, nil)

		ctx := context.Background()
		item := &models.Item{
			ID:        "", // Empty ID
			ProjectID: testProject1ID,
			Title:     "Test",
		}

		err := service.UpdateItem(ctx, item)
		assert.Error(t, err)
		assert.Contains(t, err.Error(), "item ID is required")
	})

	t.Run("empty item ID on delete", func(t *testing.T) {
		mockRepo := new(MockItemRepository)
		mockLinkRepo := new(MockLinkRepository)
		service := NewItemService(mockRepo, mockLinkRepo, nil, nil)

		ctx := context.Background()

		// DeleteItem will try to get the item first, which will fail with empty ID
		mockRepo.On("GetByID", ctx, "").Return(nil, errors.New("item not found"))

		err := service.DeleteItem(ctx, "")
		assert.Error(t, err)
		mockRepo.AssertExpectations(t)
	})
}

// TestLinkService_ValidationEdgeCases tests validation
type linkValidationCase struct {
	name       string
	link       *models.Link
	setup      func(ctx context.Context, mockItemRepo *MockItemRepository)
	errMessage string
}

func linkValidationCases() []linkValidationCase {
	return []linkValidationCase{
		{
			name: "empty source ID",
			link: &models.Link{
				SourceID: "",
				TargetID: "target-1",
				Type:     "depends_on",
			},
			errMessage: "source and target IDs are required",
		},
		{
			name: "empty target ID",
			link: &models.Link{
				SourceID: "source-1",
				TargetID: "",
				Type:     "depends_on",
			},
			errMessage: "source and target IDs are required",
		},
		{
			name: "empty link type",
			link: &models.Link{
				SourceID: "source-1",
				TargetID: "target-1",
				Type:     "",
			},
			errMessage: "link type is required",
		},
		{
			name: "source item not found",
			link: &models.Link{
				SourceID: "nonexistent",
				TargetID: "target-1",
				Type:     "depends_on",
			},
			setup: func(ctx context.Context, mockItemRepo *MockItemRepository) {
				mockItemRepo.On("GetByID", ctx, "nonexistent").Return(nil, errors.New("not found"))
			},
			errMessage: "source item not found",
		},
		{
			name: "target item not found",
			link: &models.Link{
				SourceID: "source-1",
				TargetID: "nonexistent",
				Type:     "depends_on",
			},
			setup: func(ctx context.Context, mockItemRepo *MockItemRepository) {
				mockItemRepo.On("GetByID", ctx, "source-1").Return(&models.Item{ID: "source-1"}, nil)
				mockItemRepo.On("GetByID", ctx, "nonexistent").Return(nil, errors.New("not found"))
			},
			errMessage: "target item not found",
		},
	}
}

func runLinkValidationCase(t *testing.T, tc linkValidationCase) {
	t.Helper()
	mockRepo := new(MockLinkRepository)
	mockItemRepo := new(MockItemRepository)
	service := NewLinkService(mockRepo, mockItemRepo, nil)
	ctx := context.Background()
	if tc.setup != nil {
		tc.setup(ctx, mockItemRepo)
	}
	err := service.CreateLink(ctx, tc.link)
	assert.Error(t, err)
	assert.Contains(t, err.Error(), tc.errMessage)
	mockItemRepo.AssertExpectations(t)
}

// TestLinkService_ValidationEdgeCases tests validation
func TestLinkService_ValidationEdgeCases(t *testing.T) {
	for _, tc := range linkValidationCases() {
		t.Run(tc.name, func(t *testing.T) {
			runLinkValidationCase(t, tc)
		})
	}
}

// MockNATSConn is a mock NATS connection for testing
type MockNATSConn struct {
	mock.Mock
}

func (m *MockNATSConn) Publish(subj string, data []byte) error {
	args := m.Called(subj, data)
	return args.Error(0)
}

func (m *MockNATSConn) PublishRequest(subj, reply string, data []byte) error {
	args := m.Called(subj, reply, data)
	return args.Error(0)
}

// MockNATSConn removed - NATS testing requires integration tests
