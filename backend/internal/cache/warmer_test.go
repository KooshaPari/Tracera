package cache

import (
	"context"
	"testing"
	"time"

	"github.com/stretchr/testify/mock"
	"github.com/stretchr/testify/require"

	"github.com/kooshapari/tracertm-backend/internal/models"
	"github.com/kooshapari/tracertm-backend/internal/repository"
)

// MockCache is a mock implementation of Cache interface
type MockCache struct {
	mock.Mock
}

func (m *MockCache) Get(ctx context.Context, key string, dest interface{}) error {
	args := m.Called(ctx, key, dest)
	return args.Error(0)
}

func (m *MockCache) Set(ctx context.Context, key string, value interface{}) error {
	args := m.Called(ctx, key, value)
	return args.Error(0)
}

func (m *MockCache) Delete(ctx context.Context, keys ...string) error {
	args := m.Called(ctx, keys)
	return args.Error(0)
}

func (m *MockCache) InvalidatePattern(ctx context.Context, pattern string) error {
	args := m.Called(ctx, pattern)
	return args.Error(0)
}

func (m *MockCache) Close() error {
	args := m.Called()
	return args.Error(0)
}

// MockProjectRepository is a mock implementation
type MockProjectRepository struct {
	mock.Mock
}

func (m *MockProjectRepository) Create(ctx context.Context, project *models.Project) error {
	args := m.Called(ctx, project)
	return args.Error(0)
}

func (m *MockProjectRepository) GetByID(ctx context.Context, id string) (*models.Project, error) {
	args := m.Called(ctx, id)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	val, _ := args.Get(0).(*models.Project)
	return val, args.Error(1)
}

func (m *MockProjectRepository) List(ctx context.Context) ([]*models.Project, error) {
	args := m.Called(ctx)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	val, _ := args.Get(0).([]*models.Project)
	return val, args.Error(1)
}

func (m *MockProjectRepository) Update(ctx context.Context, project *models.Project) error {
	args := m.Called(ctx, project)
	return args.Error(0)
}

func (m *MockProjectRepository) Delete(ctx context.Context, id string) error {
	args := m.Called(ctx, id)
	return args.Error(0)
}

// MockItemRepository is a mock implementation
type MockItemRepository struct {
	mock.Mock
}

func (m *MockItemRepository) Create(ctx context.Context, item *models.Item) error {
	args := m.Called(ctx, item)
	return args.Error(0)
}

func (m *MockItemRepository) GetByID(ctx context.Context, id string) (*models.Item, error) {
	args := m.Called(ctx, id)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	val, _ := args.Get(0).(*models.Item)
	return val, args.Error(1)
}

func (m *MockItemRepository) List(ctx context.Context, filter repository.ItemFilter) ([]*models.Item, error) {
	args := m.Called(ctx, filter)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	val, _ := args.Get(0).([]*models.Item)
	return val, args.Error(1)
}

func (m *MockItemRepository) GetByProjectID(ctx context.Context, projectID string) ([]*models.Item, error) {
	args := m.Called(ctx, projectID)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	val, _ := args.Get(0).([]*models.Item)
	return val, args.Error(1)
}

func (m *MockItemRepository) Count(ctx context.Context, filter repository.ItemFilter) (int64, error) {
	args := m.Called(ctx, filter)
	val, _ := args.Get(0).(int64)
	return val, args.Error(1)
}

func (m *MockItemRepository) Update(ctx context.Context, item *models.Item) error {
	args := m.Called(ctx, item)
	return args.Error(0)
}

func (m *MockItemRepository) Delete(ctx context.Context, id string) error {
	args := m.Called(ctx, id)
	return args.Error(0)
}

// MockLinkRepository is a mock implementation
type MockLinkRepository struct {
	mock.Mock
}

func (m *MockLinkRepository) Create(ctx context.Context, link *models.Link) error {
	args := m.Called(ctx, link)
	return args.Error(0)
}

func (m *MockLinkRepository) GetByID(ctx context.Context, id string) (*models.Link, error) {
	args := m.Called(ctx, id)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	val, _ := args.Get(0).(*models.Link)
	return val, args.Error(1)
}

func (m *MockLinkRepository) GetBySourceID(ctx context.Context, sourceID string) ([]*models.Link, error) {
	args := m.Called(ctx, sourceID)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	val, _ := args.Get(0).([]*models.Link)
	return val, args.Error(1)
}

func (m *MockLinkRepository) GetByTargetID(ctx context.Context, targetID string) ([]*models.Link, error) {
	args := m.Called(ctx, targetID)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	val, _ := args.Get(0).([]*models.Link)
	return val, args.Error(1)
}

func (m *MockLinkRepository) List(ctx context.Context, filter repository.LinkFilter) ([]*models.Link, error) {
	args := m.Called(ctx, filter)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	val, _ := args.Get(0).([]*models.Link)
	return val, args.Error(1)
}

func (m *MockLinkRepository) Update(ctx context.Context, link *models.Link) error {
	args := m.Called(ctx, link)
	return args.Error(0)
}

func (m *MockLinkRepository) Delete(ctx context.Context, id string) error {
	args := m.Called(ctx, id)
	return args.Error(0)
}

func (m *MockLinkRepository) DeleteByItemID(ctx context.Context, itemID string) error {
	args := m.Called(ctx, itemID)
	return args.Error(0)
}

func TestCacheWarmer_WarmProjects(t *testing.T) {
	mockCache := new(MockCache)
	mockProjectRepo := new(MockProjectRepository)
	mockItemRepo := new(MockItemRepository)
	mockLinkRepo := new(MockLinkRepository)

	warmer := NewCacheWarmer(mockCache, mockProjectRepo, mockItemRepo, mockLinkRepo)

	// Setup mock data
	projects := []*models.Project{
		{ID: "project1", Name: "Project 1"},
		{ID: "project2", Name: "Project 2"},
	}

	mockProjectRepo.On("List", mock.Anything).Return(projects, nil)
	mockCache.On("Set", mock.Anything, "project:project1", projects[0]).Return(nil)
	mockCache.On("Set", mock.Anything, "project:project2", projects[1]).Return(nil)

	// Execute
	err := warmer.warmProjects(context.Background())

	// Verify
	require.NoError(t, err)
	mockProjectRepo.AssertExpectations(t)
	mockCache.AssertExpectations(t)
}

func TestCacheWarmer_WarmRecentItems(t *testing.T) {
	mockCache := new(MockCache)
	mockProjectRepo := new(MockProjectRepository)
	mockItemRepo := new(MockItemRepository)
	mockLinkRepo := new(MockLinkRepository)

	warmer := NewCacheWarmer(mockCache, mockProjectRepo, mockItemRepo, mockLinkRepo)

	// Setup mock data
	items := []*models.Item{
		{ID: "item1", Title: "Item 1"},
		{ID: "item2", Title: "Item 2"},
	}

	mockItemRepo.On("List", mock.Anything, mock.Anything).Return(items, nil)
	mockCache.On("Set", mock.Anything, "item:item1", items[0]).Return(nil)
	mockCache.On("Set", mock.Anything, "item:item2", items[1]).Return(nil)

	// Execute
	err := warmer.warmRecentItems(context.Background())

	// Verify
	require.NoError(t, err)
	mockItemRepo.AssertExpectations(t)
	mockCache.AssertExpectations(t)
}

func TestCacheWarmer_WarmProject(t *testing.T) {
	mockCache := new(MockCache)
	mockProjectRepo := new(MockProjectRepository)
	mockItemRepo := new(MockItemRepository)
	mockLinkRepo := new(MockLinkRepository)

	warmer := NewCacheWarmer(mockCache, mockProjectRepo, mockItemRepo, mockLinkRepo)

	// Setup mock data
	project := &models.Project{ID: "project1", Name: "Project 1"}
	items := []*models.Item{
		{ID: "item1", Title: "Item 1", ProjectID: "project1"},
		{ID: "item2", Title: "Item 2", ProjectID: "project1"},
	}

	mockProjectRepo.On("GetByID", mock.Anything, "project1").Return(project, nil)
	mockItemRepo.On("List", mock.Anything, mock.Anything).Return(items, nil)
	mockCache.On("Set", mock.Anything, "project:project1", project).Return(nil)
	mockCache.On("Set", mock.Anything, "item:item1", items[0]).Return(nil)
	mockCache.On("Set", mock.Anything, "item:item2", items[1]).Return(nil)

	// Execute
	err := warmer.WarmProject(context.Background(), "project1")

	// Verify
	require.NoError(t, err)
	mockProjectRepo.AssertExpectations(t)
	mockItemRepo.AssertExpectations(t)
	mockCache.AssertExpectations(t)
}

func TestCacheWarmer_WarmRelatedItems(t *testing.T) {
	mockCache := new(MockCache)
	mockProjectRepo := new(MockProjectRepository)
	mockItemRepo := new(MockItemRepository)
	mockLinkRepo := new(MockLinkRepository)

	warmer := NewCacheWarmer(mockCache, mockProjectRepo, mockItemRepo, mockLinkRepo)

	// Setup mock data
	links := []*models.Link{
		{ID: "link1", SourceID: "item1", TargetID: "item2"},
		{ID: "link2", SourceID: "item1", TargetID: "item3"},
	}
	item2 := &models.Item{ID: "item2", Title: "Item 2"}
	item3 := &models.Item{ID: "item3", Title: "Item 3"}

	mockLinkRepo.On("GetBySourceID", mock.Anything, "item1").Return(links, nil)
	mockItemRepo.On("GetByID", mock.Anything, "item2").Return(item2, nil)
	mockItemRepo.On("GetByID", mock.Anything, "item3").Return(item3, nil)
	mockCache.On("Set", mock.Anything, "item:item2", item2).Return(nil)
	mockCache.On("Set", mock.Anything, "item:item3", item3).Return(nil)

	// Execute
	err := warmer.WarmRelatedItems(context.Background(), "item1")

	// Verify
	require.NoError(t, err)
	mockLinkRepo.AssertExpectations(t)
	mockItemRepo.AssertExpectations(t)
	mockCache.AssertExpectations(t)
}

func TestCacheWarmer_WarmOnStartup(t *testing.T) {
	mockCache := new(MockCache)
	mockProjectRepo := new(MockProjectRepository)
	mockItemRepo := new(MockItemRepository)
	mockLinkRepo := new(MockLinkRepository)

	warmer := NewCacheWarmer(mockCache, mockProjectRepo, mockItemRepo, mockLinkRepo)

	// Setup mock data
	projects := []*models.Project{
		{ID: "project1", Name: "Project 1"},
	}
	items := []*models.Item{
		{ID: "item1", Title: "Item 1", UpdatedAt: time.Now()},
	}

	mockProjectRepo.On("List", mock.Anything).Return(projects, nil)
	mockItemRepo.On("List", mock.Anything, mock.Anything).Return(items, nil)
	mockCache.On("Set", mock.Anything, mock.Anything, mock.Anything).Return(nil)

	// Execute
	err := warmer.WarmOnStartup(context.Background())

	// Verify
	require.NoError(t, err)
	mockProjectRepo.AssertExpectations(t)
	mockItemRepo.AssertExpectations(t)
}
