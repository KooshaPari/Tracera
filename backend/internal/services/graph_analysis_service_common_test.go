//go:build !integration && !e2e

package services

import (
	"context"
	"testing"

	"github.com/nats-io/nats.go"
	"github.com/stretchr/testify/mock"

	"github.com/kooshapari/tracertm-backend/internal/cache"
	"github.com/kooshapari/tracertm-backend/internal/models"
	"github.com/kooshapari/tracertm-backend/internal/repository"
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
	val, _ := args.Get(0).(*models.Item)
	return val, args.Error(1)
}

func (m *GraphMockItemRepository) GetByProjectID(ctx context.Context, projectID string) ([]*models.Item, error) {
	args := m.Called(ctx, projectID)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	val, _ := args.Get(0).([]*models.Item)
	return val, args.Error(1)
}

func (m *GraphMockItemRepository) List(ctx context.Context, filter repository.ItemFilter) ([]*models.Item, error) {
	args := m.Called(ctx, filter)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	val, _ := args.Get(0).([]*models.Item)
	return val, args.Error(1)
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
	val, _ := args.Get(0).(int64)
	return val, args.Error(1)
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
	val, _ := args.Get(0).(*models.Link)
	return val, args.Error(1)
}

func (m *GraphMockLinkRepository) GetBySourceID(ctx context.Context, sourceID string) ([]*models.Link, error) {
	args := m.Called(ctx, sourceID)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	val, _ := args.Get(0).([]*models.Link)
	return val, args.Error(1)
}

func (m *GraphMockLinkRepository) GetByTargetID(ctx context.Context, targetID string) ([]*models.Link, error) {
	args := m.Called(ctx, targetID)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	val, _ := args.Get(0).([]*models.Link)
	return val, args.Error(1)
}

func (m *GraphMockLinkRepository) List(ctx context.Context, filter repository.LinkFilter) ([]*models.Link, error) {
	args := m.Called(ctx, filter)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	val, _ := args.Get(0).([]*models.Link)
	return val, args.Error(1)
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
	var natsConn *nats.Conn

	service := NewGraphAnalysisServiceImpl(itemRepo, linkRepo, cache, natsConn)

	impl, ok := service.(*GraphAnalysisServiceImpl)
	if !ok {
		panic("NewGraphAnalysisServiceImpl did not return *GraphAnalysisServiceImpl")
	}
	return impl, itemRepo, linkRepo
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
