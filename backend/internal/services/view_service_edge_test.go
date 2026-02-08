package services

import (
	"encoding/json"
	"strings"
	"time"

	"github.com/kooshapari/tracertm-backend/internal/models"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/mock"
)

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
	longName := strings.Repeat("a", 201)
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
