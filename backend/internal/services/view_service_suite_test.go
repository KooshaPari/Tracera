package services

import (
	"errors"
	"strings"
	"testing"
	"time"

	"github.com/stretchr/testify/mock"
	"github.com/stretchr/testify/suite"

	"github.com/kooshapari/tracertm-backend/internal/models"
)

func TestViewServiceSuite(t *testing.T) {
	suite.Run(t, new(ViewServiceTestSuite))
}

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

	suite.Require().NoError(err)
	suite.NotEmpty(view.ID)
	suite.False(view.CreatedAt.IsZero())
	suite.False(view.UpdatedAt.IsZero())
}

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

	suite.Require().NoError(err)
	suite.NotNil(result)
	suite.Equal(expectedView.ID, result.ID)
	suite.Equal(expectedView.Name, result.Name)
}

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

	suite.Require().NoError(err)
	suite.Len(result, 2)
	suite.Equal(expectedViews[0].ID, result[0].ID)
}

func (suite *ViewServiceTestSuite) TestListViews_Success() {
	expectedViews := []*models.View{
		{ID: "view-1", ProjectID: "project-1", Name: "View 1", Type: "kanban"},
		{ID: "view-2", ProjectID: "project-2", Name: "View 2", Type: "timeline"},
	}

	suite.cache.On("Get", suite.ctx, "views:all").Return("", errors.New("cache miss"))
	suite.repo.On("List", suite.ctx).Return(expectedViews, nil)
	suite.cache.On("Set", suite.ctx, "views:all", mock.Anything, mock.Anything).Return(nil)

	result, err := suite.service.ListViews(suite.ctx)

	suite.Require().NoError(err)
	suite.Len(result, 2)
}

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

	suite.Require().NoError(err)
	suite.Equal(existingView.CreatedAt, updatedView.CreatedAt)
}

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

	suite.Require().NoError(err)
}

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

	suite.Require().NoError(err)
	suite.NotNil(result)
	suite.Equal(viewID, result.ViewID)
	suite.Equal(int64(42), result.ItemCount)
}
