package services

import (
	"context"
	"encoding/json"
	"errors"
	"strings"
	"testing"
	"time"

	"github.com/kooshapari/tracertm-backend/internal/models"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/mock"
	"github.com/stretchr/testify/suite"
)

// ============================================================================
// Mock ViewRepository
// ============================================================================

// MockViewRepository is a mock implementation of ViewRepository
type MockViewRepository struct {
	mock.Mock
}

func (m *MockViewRepository) Create(ctx context.Context, view *models.View) error {
	args := m.Called(ctx, view)
	return args.Error(0)
}

func (m *MockViewRepository) GetByID(ctx context.Context, id string) (*models.View, error) {
	args := m.Called(ctx, id)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	return args.Get(0).(*models.View), args.Error(1)
}

func (m *MockViewRepository) GetByProjectID(ctx context.Context, projectID string) ([]*models.View, error) {
	args := m.Called(ctx, projectID)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	return args.Get(0).([]*models.View), args.Error(1)
}

func (m *MockViewRepository) List(ctx context.Context) ([]*models.View, error) {
	args := m.Called(ctx)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	return args.Get(0).([]*models.View), args.Error(1)
}

func (m *MockViewRepository) Update(ctx context.Context, view *models.View) error {
	args := m.Called(ctx, view)
	return args.Error(0)
}

func (m *MockViewRepository) Delete(ctx context.Context, id string) error {
	args := m.Called(ctx, id)
	return args.Error(0)
}

func (m *MockViewRepository) CountItemsByView(ctx context.Context, viewID string) (int64, error) {
	args := m.Called(ctx, viewID)
	return args.Get(0).(int64), args.Error(1)
}

// ============================================================================
// Test Suite
// ============================================================================

// ViewServiceTestSuite provides test suite setup for view service tests
type ViewServiceTestSuite struct {
	suite.Suite
	repo    *MockViewRepository
	cache   *MockCache
	service ViewService
	ctx     context.Context
}

func (suite *ViewServiceTestSuite) SetupTest() {
	suite.repo = new(MockViewRepository)
	suite.cache = new(MockCache)
	suite.ctx = context.Background()
	suite.service = NewViewServiceImpl(suite.repo, suite.cache, nil)
}

func (suite *ViewServiceTestSuite) TearDownTest() {
	suite.repo.AssertExpectations(suite.T())
	// Cache expectations are optional, so we don't assert them
}

func TestViewServiceSuite(t *testing.T) {
	suite.Run(t, new(ViewServiceTestSuite))
}

// ============================================================================
// Create View Tests
// ============================================================================

func (suite *ViewServiceTestSuite) TestCreateView_Success() {
	view := &models.View{
		ProjectID: "project-123",
		Name:      "Test View",
		Type:      "kanban",
		Config:    `{"columns": ["todo", "done"]}`,
	}

	suite.repo.On("Create", suite.ctx, mock.MatchedBy(func(v *models.View) bool {
		return v.Name == view.Name && v.ID != ""
	})).Return(nil)

	suite.cache.On("Delete", suite.ctx, []string{"views:project:project-123", "views:all"}).Return(nil)

	err := suite.service.CreateView(suite.ctx, view)

	assert.NoError(suite.T(), err)
	assert.NotEmpty(suite.T(), view.ID)
	assert.False(suite.T(), view.CreatedAt.IsZero())
	assert.False(suite.T(), view.UpdatedAt.IsZero())
}

func (suite *ViewServiceTestSuite) TestCreateView_ValidationError() {
	view := &models.View{
		ProjectID: "project-123",
		Name:      "", // Invalid: empty name
		Type:      "kanban",
	}

	err := suite.service.CreateView(suite.ctx, view)

	assert.Error(suite.T(), err)
	assert.Contains(suite.T(), err.Error(), "name is required")
}

func (suite *ViewServiceTestSuite) TestCreateView_InvalidType() {
	view := &models.View{
		ProjectID: "project-123",
		Name:      "Test View",
		Type:      "invalid-type",
	}

	err := suite.service.CreateView(suite.ctx, view)

	assert.Error(suite.T(), err)
	assert.Contains(suite.T(), err.Error(), "invalid view type")
}

func (suite *ViewServiceTestSuite) TestCreateView_InvalidJSON() {
	view := &models.View{
		ProjectID: "project-123",
		Name:      "Test View",
		Type:      "kanban",
		Config:    `{invalid json`,
	}

	err := suite.service.CreateView(suite.ctx, view)

	assert.Error(suite.T(), err)
	assert.Contains(suite.T(), err.Error(), "invalid config JSON")
}

func (suite *ViewServiceTestSuite) TestCreateView_RepositoryError() {
	view := &models.View{
		ProjectID: "project-123",
		Name:      "Test View",
		Type:      "kanban",
	}

	suite.repo.On("Create", suite.ctx, mock.Anything).Return(errors.New("database error"))

	err := suite.service.CreateView(suite.ctx, view)

	assert.Error(suite.T(), err)
	assert.Contains(suite.T(), err.Error(), "failed to create view")
}

// ============================================================================
// Get View Tests
// ============================================================================

func (suite *ViewServiceTestSuite) TestGetView_Success() {
	viewID := testViewID
	expectedView := &models.View{
		ID:        viewID,
		ProjectID: "project-123",
		Name:      "Test View",
		Type:      "kanban",
		CreatedAt: time.Now(),
		UpdatedAt: time.Now(),
	}

	suite.cache.On("Get", suite.ctx, mock.MatchedBy(func(key string) bool {
		return strings.HasPrefix(key, "view:") && !strings.HasPrefix(key, "view:stats:")
	})).Return("", errors.New("cache miss"))
	suite.repo.On("GetByID", suite.ctx, viewID).Return(expectedView, nil)
	suite.cache.On("Set", suite.ctx, mock.MatchedBy(func(key string) bool {
		return strings.HasPrefix(key, "view:") && !strings.HasPrefix(key, "view:stats:")
	}), mock.Anything, mock.Anything).Return(nil)

	result, err := suite.service.GetView(suite.ctx, viewID)

	assert.NoError(suite.T(), err)
	assert.NotNil(suite.T(), result)
	assert.Equal(suite.T(), expectedView.ID, result.ID)
	assert.Equal(suite.T(), expectedView.Name, result.Name)
}

func (suite *ViewServiceTestSuite) TestGetView_CacheHit() {
	viewID := testViewID
	cachedView := &models.View{
		ID:        viewID,
		ProjectID: "project-123",
		Name:      "Cached View",
		Type:      "kanban",
	}

	cachedData, _ := json.Marshal(cachedView)
	suite.cache.On("Get", suite.ctx, mock.MatchedBy(func(key string) bool {
		return strings.HasPrefix(key, "view:") && !strings.HasPrefix(key, "view:stats:")
	})).Return(string(cachedData), nil)

	result, err := suite.service.GetView(suite.ctx, viewID)

	assert.NoError(suite.T(), err)
	assert.NotNil(suite.T(), result)
	assert.Equal(suite.T(), cachedView.ID, result.ID)
	assert.Equal(suite.T(), cachedView.Name, result.Name)
}

func (suite *ViewServiceTestSuite) TestGetView_EmptyID() {
	result, err := suite.service.GetView(suite.ctx, "")

	assert.Error(suite.T(), err)
	assert.Nil(suite.T(), result)
	assert.Contains(suite.T(), err.Error(), "cannot be empty")
}

func (suite *ViewServiceTestSuite) TestGetView_NotFound() {
	viewID := testNonexistentID

	suite.cache.On("Get", suite.ctx, mock.MatchedBy(func(key string) bool {
		return strings.HasPrefix(key, "view:") && !strings.HasPrefix(key, "view:stats:")
	})).Return("", errors.New("cache miss"))
	suite.repo.On("GetByID", suite.ctx, viewID).Return(nil, errors.New("view not found"))

	result, err := suite.service.GetView(suite.ctx, viewID)

	assert.Error(suite.T(), err)
	assert.Nil(suite.T(), result)
}

// ============================================================================
// Get Views By Project Tests
// ============================================================================

func (suite *ViewServiceTestSuite) TestGetViewsByProject_Success() {
	projectID := "project-123"
	expectedViews := []*models.View{
		{ID: "view-1", ProjectID: projectID, Name: "View 1", Type: "kanban"},
		{ID: "view-2", ProjectID: projectID, Name: "View 2", Type: "timeline"},
	}

	suite.cache.On("Get", suite.ctx, "views:project:project-123").Return("", errors.New("cache miss"))
	suite.repo.On("GetByProjectID", suite.ctx, projectID).Return(expectedViews, nil)
	suite.cache.On("Set", suite.ctx, "views:project:project-123", mock.Anything, mock.Anything).Return(nil)

	result, err := suite.service.GetViewsByProject(suite.ctx, projectID)

	assert.NoError(suite.T(), err)
	assert.Len(suite.T(), result, 2)
	assert.Equal(suite.T(), expectedViews[0].ID, result[0].ID)
}

func (suite *ViewServiceTestSuite) TestGetViewsByProject_EmptyProjectID() {
	result, err := suite.service.GetViewsByProject(suite.ctx, "")

	assert.Error(suite.T(), err)
	assert.Nil(suite.T(), result)
	assert.Contains(suite.T(), err.Error(), "cannot be empty")
}

// ============================================================================
// List Views Tests
// ============================================================================

func (suite *ViewServiceTestSuite) TestListViews_Success() {
	expectedViews := []*models.View{
		{ID: "view-1", ProjectID: "project-1", Name: "View 1", Type: "kanban"},
		{ID: "view-2", ProjectID: "project-2", Name: "View 2", Type: "timeline"},
	}

	suite.cache.On("Get", suite.ctx, "views:all").Return("", errors.New("cache miss"))
	suite.repo.On("List", suite.ctx).Return(expectedViews, nil)
	suite.cache.On("Set", suite.ctx, "views:all", mock.Anything, mock.Anything).Return(nil)

	result, err := suite.service.ListViews(suite.ctx)

	assert.NoError(suite.T(), err)
	assert.Len(suite.T(), result, 2)
}

func (suite *ViewServiceTestSuite) TestListViews_RepositoryError() {
	suite.cache.On("Get", suite.ctx, "views:all").Return("", errors.New("cache miss"))
	suite.repo.On("List", suite.ctx).Return(nil, errors.New("database error"))

	result, err := suite.service.ListViews(suite.ctx)

	assert.Error(suite.T(), err)
	assert.Nil(suite.T(), result)
}

// ============================================================================
// Update View Tests
// ============================================================================

func (suite *ViewServiceTestSuite) TestUpdateView_Success() {
	existingView := &models.View{
		ID:        testViewID,
		ProjectID: "project-123",
		Name:      "Original Name",
		Type:      "kanban",
		CreatedAt: time.Now().Add(-24 * time.Hour),
	}

	updatedView := &models.View{
		ID:        testViewID,
		ProjectID: "project-123",
		Name:      "Updated Name",
		Type:      "kanban",
	}

	suite.repo.On("GetByID", suite.ctx, testViewID).Return(existingView, nil)
	suite.repo.On("Update", suite.ctx, mock.MatchedBy(func(v *models.View) bool {
		return v.Name == "Updated Name"
	})).Return(nil)
	suite.cache.On("Delete", suite.ctx, mock.Anything).Return(nil)

	err := suite.service.UpdateView(suite.ctx, updatedView)

	assert.NoError(suite.T(), err)
	assert.Equal(suite.T(), existingView.CreatedAt, updatedView.CreatedAt)
}

func (suite *ViewServiceTestSuite) TestUpdateView_NilView() {
	err := suite.service.UpdateView(suite.ctx, nil)

	assert.Error(suite.T(), err)
	assert.Contains(suite.T(), err.Error(), "cannot be nil")
}

func (suite *ViewServiceTestSuite) TestUpdateView_ValidationError() {
	view := &models.View{
		ID:        testViewID,
		ProjectID: "project-123",
		Name:      "", // Invalid: empty name
		Type:      "kanban",
	}

	err := suite.service.UpdateView(suite.ctx, view)

	assert.Error(suite.T(), err)
	assert.Contains(suite.T(), err.Error(), "validation failed")
}

func (suite *ViewServiceTestSuite) TestUpdateView_NotFound() {
	view := &models.View{
		ID:        testNonexistentID,
		ProjectID: "project-123",
		Name:      "Test",
		Type:      "kanban",
	}

	suite.repo.On("GetByID", suite.ctx, testNonexistentID).Return(nil, errors.New("view not found"))

	err := suite.service.UpdateView(suite.ctx, view)

	assert.Error(suite.T(), err)
	assert.Contains(suite.T(), err.Error(), "view not found")
}

// ============================================================================
// Delete View Tests
// ============================================================================

func (suite *ViewServiceTestSuite) TestDeleteView_Success() {
	viewID := testViewID
	existingView := &models.View{
		ID:        viewID,
		ProjectID: "project-123",
		Name:      "Test View",
		Type:      "kanban",
	}

	suite.repo.On("GetByID", suite.ctx, viewID).Return(existingView, nil)
	suite.repo.On("Delete", suite.ctx, viewID).Return(nil)
	suite.cache.On("Delete", suite.ctx, mock.Anything).Return(nil)

	err := suite.service.DeleteView(suite.ctx, viewID)

	assert.NoError(suite.T(), err)
}

func (suite *ViewServiceTestSuite) TestDeleteView_EmptyID() {
	err := suite.service.DeleteView(suite.ctx, "")

	assert.Error(suite.T(), err)
	assert.Contains(suite.T(), err.Error(), "cannot be empty")
}

func (suite *ViewServiceTestSuite) TestDeleteView_NotFound() {
	viewID := testNonexistentID

	suite.repo.On("GetByID", suite.ctx, viewID).Return(nil, errors.New("view not found"))

	err := suite.service.DeleteView(suite.ctx, viewID)

	assert.Error(suite.T(), err)
	assert.Contains(suite.T(), err.Error(), "view not found")
}

// ============================================================================
// Get View Stats Tests
// ============================================================================

func (suite *ViewServiceTestSuite) TestGetViewStats_Success() {
	viewID := testViewID
	view := &models.View{
		ID:        viewID,
		ProjectID: "project-123",
		Name:      "Test View",
		Type:      "kanban",
		UpdatedAt: time.Now(),
	}

	suite.cache.On("Get", suite.ctx, mock.MatchedBy(func(key string) bool {
		return strings.HasPrefix(key, "view:stats:")
	})).Return("", errors.New("cache miss"))
	suite.repo.On("GetByID", suite.ctx, viewID).Return(view, nil)
	suite.repo.On("CountItemsByView", suite.ctx, viewID).Return(int64(42), nil)
	suite.cache.On("Set", suite.ctx, mock.MatchedBy(func(key string) bool {
		return strings.HasPrefix(key, "view:stats:")
	}), mock.Anything, mock.Anything).Return(nil)

	result, err := suite.service.GetViewStats(suite.ctx, viewID)

	assert.NoError(suite.T(), err)
	assert.NotNil(suite.T(), result)
	assert.Equal(suite.T(), viewID, result.ViewID)
	assert.Equal(suite.T(), int64(42), result.ItemCount)
}

func (suite *ViewServiceTestSuite) TestGetViewStats_EmptyID() {
	result, err := suite.service.GetViewStats(suite.ctx, "")

	assert.Error(suite.T(), err)
	assert.Nil(suite.T(), result)
	assert.Contains(suite.T(), err.Error(), "cannot be empty")
}

func (suite *ViewServiceTestSuite) TestGetViewStats_ViewNotFound() {
	viewID := testNonexistentID

	suite.cache.On("Get", suite.ctx, mock.MatchedBy(func(key string) bool {
		return strings.HasPrefix(key, "view:stats:")
	})).Return("", errors.New("cache miss"))
	suite.repo.On("GetByID", suite.ctx, viewID).Return(nil, errors.New("view not found"))

	result, err := suite.service.GetViewStats(suite.ctx, viewID)

	assert.Error(suite.T(), err)
	assert.Nil(suite.T(), result)
}

// ============================================================================
// Validation Tests
// ============================================================================

func (suite *ViewServiceTestSuite) TestValidateView_NilView() {
	err := suite.service.ValidateView(nil)

	assert.Error(suite.T(), err)
	assert.Contains(suite.T(), err.Error(), "cannot be nil")
}

func (suite *ViewServiceTestSuite) TestValidateView_MissingName() {
	view := &models.View{
		ProjectID: "project-123",
		Type:      "kanban",
	}

	err := suite.service.ValidateView(view)

	assert.Error(suite.T(), err)
	assert.Contains(suite.T(), err.Error(), "name is required")
}

func (suite *ViewServiceTestSuite) TestValidateView_MissingProjectID() {
	view := &models.View{
		Name: "Test View",
		Type: "kanban",
	}

	err := suite.service.ValidateView(view)

	assert.Error(suite.T(), err)
	assert.Contains(suite.T(), err.Error(), "project ID is required")
}

func (suite *ViewServiceTestSuite) TestValidateView_MissingType() {
	view := &models.View{
		Name:      "Test View",
		ProjectID: "project-123",
	}

	err := suite.service.ValidateView(view)

	assert.Error(suite.T(), err)
	assert.Contains(suite.T(), err.Error(), "type is required")
}

func (suite *ViewServiceTestSuite) TestValidateView_NameTooLong() {
	longName := string(make([]byte, 201))
	view := &models.View{
		Name:      longName,
		ProjectID: "project-123",
		Type:      "kanban",
	}

	err := suite.service.ValidateView(view)

	assert.Error(suite.T(), err)
	assert.Contains(suite.T(), err.Error(), "cannot exceed 200 characters")
}

func (suite *ViewServiceTestSuite) TestValidateView_AllTypes() {
	validTypes := []string{"kanban", "timeline", "matrix", "graph", "table", "board", "list"}

	for _, viewType := range validTypes {
		view := &models.View{
			Name:      "Test View",
			ProjectID: "project-123",
			Type:      viewType,
		}

		err := suite.service.ValidateView(view)
		assert.NoError(suite.T(), err, "Type %s should be valid", viewType)
	}
}

// ============================================================================
// Additional Edge Case Tests
// ============================================================================

func (suite *ViewServiceTestSuite) TestCreateView_PreservesExistingID() {
	existingID := "existing-id-123"
	view := &models.View{
		ID:        existingID,
		ProjectID: "project-123",
		Name:      "Test View",
		Type:      "kanban",
	}

	suite.repo.On("Create", suite.ctx, mock.MatchedBy(func(v *models.View) bool {
		return v.ID == existingID
	})).Return(nil)
	suite.cache.On("Delete", suite.ctx, mock.Anything).Return(nil)

	err := suite.service.CreateView(suite.ctx, view)

	assert.NoError(suite.T(), err)
	assert.Equal(suite.T(), existingID, view.ID)
}

func (suite *ViewServiceTestSuite) TestGetViewsByProject_CacheHit() {
	projectID := "project-123"
	cachedViews := []*models.View{
		{ID: "view-1", ProjectID: projectID, Name: "View 1", Type: "kanban"},
	}

	cachedData, _ := json.Marshal(cachedViews)
	suite.cache.On("Get", suite.ctx, "views:project:project-123").Return(string(cachedData), nil)

	result, err := suite.service.GetViewsByProject(suite.ctx, projectID)

	assert.NoError(suite.T(), err)
	assert.Len(suite.T(), result, 1)
	assert.Equal(suite.T(), cachedViews[0].ID, result[0].ID)
}

func (suite *ViewServiceTestSuite) TestListViews_CacheHit() {
	cachedViews := []*models.View{
		{ID: "view-1", ProjectID: "project-1", Name: "View 1", Type: "kanban"},
	}

	cachedData, _ := json.Marshal(cachedViews)
	suite.cache.On("Get", suite.ctx, "views:all").Return(string(cachedData), nil)

	result, err := suite.service.ListViews(suite.ctx)

	assert.NoError(suite.T(), err)
	assert.Len(suite.T(), result, 1)
}

func (suite *ViewServiceTestSuite) TestGetViewStats_CacheHit() {
	viewID := testViewID
	cachedStats := &models.ViewStats{
		ViewID:    viewID,
		ItemCount: 100,
		UpdatedAt: time.Now(),
	}

	cachedData, _ := json.Marshal(cachedStats)
	suite.cache.On("Get", suite.ctx, mock.MatchedBy(func(key string) bool {
		return strings.HasPrefix(key, "view:stats:")
	})).Return(string(cachedData), nil)

	result, err := suite.service.GetViewStats(suite.ctx, viewID)

	assert.NoError(suite.T(), err)
	assert.NotNil(suite.T(), result)
	assert.Equal(suite.T(), int64(100), result.ItemCount)
}
