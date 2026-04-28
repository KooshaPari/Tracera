package services

import (
	"errors"
	"strings"

	"github.com/stretchr/testify/mock"

	"github.com/kooshapari/tracertm-backend/internal/models"
)

func (suite *ViewServiceTestSuite) TestCreateView_ValidationError() {
	view := &models.View{
		ProjectID: "project-123",
		Name:      "",
		Type:      "kanban",
	}

	err := suite.service.CreateView(suite.ctx, view)

	suite.Require().Error(err)
	suite.Contains(err.Error(), "name is required")
}

func (suite *ViewServiceTestSuite) TestCreateView_InvalidType() {
	view := &models.View{
		ProjectID: "project-123",
		Name:      "Test View",
		Type:      "invalid-type",
	}

	err := suite.service.CreateView(suite.ctx, view)

	suite.Require().Error(err)
	suite.Contains(err.Error(), "invalid view type")
}

func (suite *ViewServiceTestSuite) TestCreateView_InvalidJSON() {
	view := &models.View{
		ProjectID: "project-123",
		Name:      "Test View",
		Type:      "kanban",
		Config:    `{invalid json`,
	}

	err := suite.service.CreateView(suite.ctx, view)

	suite.Require().Error(err)
	suite.Contains(err.Error(), "invalid config JSON")
}

func (suite *ViewServiceTestSuite) TestCreateView_RepositoryError() {
	view := &models.View{
		ProjectID: "project-123",
		Name:      "Test View",
		Type:      "kanban",
	}

	suite.repo.On("Create", suite.ctx, mock.Anything).Return(errors.New("database error"))

	err := suite.service.CreateView(suite.ctx, view)

	suite.Require().Error(err)
	suite.Contains(err.Error(), "failed to create view")
}

func (suite *ViewServiceTestSuite) TestGetView_EmptyID() {
	result, err := suite.service.GetView(suite.ctx, "")

	suite.Require().Error(err)
	suite.Nil(result)
	suite.Contains(err.Error(), "cannot be empty")
}

func (suite *ViewServiceTestSuite) TestGetView_NotFound() {
	viewID := testNonexistentID

	suite.cache.On("Get", suite.ctx, mock.MatchedBy(func(key string) bool {
		return strings.HasPrefix(key, "view:") && !strings.HasPrefix(key, "view:stats:")
	})).Return("", errors.New("cache miss"))
	suite.repo.On("GetByID", suite.ctx, viewID).Return(nil, errors.New("view not found"))

	result, err := suite.service.GetView(suite.ctx, viewID)

	suite.Require().Error(err)
	suite.Nil(result)
}

func (suite *ViewServiceTestSuite) TestGetViewsByProject_EmptyProjectID() {
	result, err := suite.service.GetViewsByProject(suite.ctx, "")

	suite.Require().Error(err)
	suite.Nil(result)
	suite.Contains(err.Error(), "cannot be empty")
}

func (suite *ViewServiceTestSuite) TestListViews_RepositoryError() {
	suite.cache.On("Get", suite.ctx, "views:all").Return("", errors.New("cache miss"))
	suite.repo.On("List", suite.ctx).Return(nil, errors.New("database error"))

	result, err := suite.service.ListViews(suite.ctx)

	suite.Require().Error(err)
	suite.Nil(result)
}

func (suite *ViewServiceTestSuite) TestUpdateView_NilView() {
	err := suite.service.UpdateView(suite.ctx, nil)

	suite.Require().Error(err)
	suite.Contains(err.Error(), "cannot be nil")
}

func (suite *ViewServiceTestSuite) TestUpdateView_ValidationError() {
	view := &models.View{
		ID:        testViewID,
		ProjectID: "project-123",
		Name:      "",
		Type:      "kanban",
	}

	err := suite.service.UpdateView(suite.ctx, view)

	suite.Require().Error(err)
	suite.Contains(err.Error(), "validation failed")
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

	suite.Require().Error(err)
	suite.Contains(err.Error(), "view not found")
}

func (suite *ViewServiceTestSuite) TestDeleteView_EmptyID() {
	err := suite.service.DeleteView(suite.ctx, "")

	suite.Require().Error(err)
	suite.Contains(err.Error(), "cannot be empty")
}

func (suite *ViewServiceTestSuite) TestDeleteView_NotFound() {
	viewID := testNonexistentID

	suite.repo.On("GetByID", suite.ctx, viewID).Return(nil, errors.New("view not found"))

	err := suite.service.DeleteView(suite.ctx, viewID)

	suite.Require().Error(err)
	suite.Contains(err.Error(), "view not found")
}

func (suite *ViewServiceTestSuite) TestGetViewStats_EmptyID() {
	result, err := suite.service.GetViewStats(suite.ctx, "")

	suite.Require().Error(err)
	suite.Nil(result)
	suite.Contains(err.Error(), "cannot be empty")
}

func (suite *ViewServiceTestSuite) TestGetViewStats_ViewNotFound() {
	viewID := testNonexistentID

	suite.cache.On("Get", suite.ctx, mock.MatchedBy(func(key string) bool {
		return strings.HasPrefix(key, "view:stats:")
	})).Return("", errors.New("cache miss"))
	suite.repo.On("GetByID", suite.ctx, viewID).Return(nil, errors.New("view not found"))

	result, err := suite.service.GetViewStats(suite.ctx, viewID)

	suite.Require().Error(err)
	suite.Nil(result)
}
