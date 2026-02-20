//go:build !integration && !e2e

package services

import (
	"context"
	"testing"

	"github.com/stretchr/testify/suite"

	"github.com/kooshapari/tracertm-backend/internal/models"
)

func TestProjectServiceSuite(t *testing.T) {
	suite.Run(t, new(ProjectServiceTestSuite))
}

func (suite *ProjectServiceTestSuite) TestProjectService_Create_Success() {
	project := &models.Project{
		Name:        "Test Project",
		Description: "Test Description",
	}

	suite.repo.On("Create", suite.ctx, project).Return(nil)

	err := suite.service.CreateProject(suite.ctx, project)

	suite.Require().NoError(err)
}

func (suite *ProjectServiceTestSuite) TestProjectService_Get_Success() {
	projectID := testProjectIDValue
	expectedProject := &models.Project{
		ID:          projectID,
		Name:        "Test Project",
		Description: "Test Description",
	}

	suite.repo.On("GetByID", suite.ctx, projectID).Return(expectedProject, nil)

	result, err := suite.service.GetProject(suite.ctx, projectID)

	suite.Require().NoError(err)
	suite.NotNil(result)
	suite.Equal(expectedProject.ID, result.ID)
	suite.Equal(expectedProject.Name, result.Name)
}

func (suite *ProjectServiceTestSuite) TestProjectService_Update_Success() {
	project := &models.Project{
		ID:          testProjectIDValue,
		Name:        "Updated Project",
		Description: "Updated Description",
	}

	suite.repo.On("Update", suite.ctx, project).Return(nil)

	err := suite.service.UpdateProject(suite.ctx, project)

	suite.Require().NoError(err)
}

func (suite *ProjectServiceTestSuite) TestProjectService_Delete_Cascade() {
	projectID := testProjectIDValue

	suite.repo.On("Delete", suite.ctx, projectID).Return(nil)

	err := suite.service.DeleteProject(suite.ctx, projectID)

	suite.Require().NoError(err)
	suite.repo.AssertCalled(suite.T(), "Delete", suite.ctx, projectID)
}

func (suite *ProjectServiceTestSuite) TestProjectService_List_Success() {
	expectedProjects := []*models.Project{
		{ID: "project-1", Name: "Project 1", Description: "Description 1"},
		{ID: "project-2", Name: "Project 2", Description: "Description 2"},
		{ID: "project-3", Name: "Project 3", Description: "Description 3"},
	}

	suite.repo.On("List", suite.ctx).Return(expectedProjects, nil)

	result, err := suite.service.ListProjects(suite.ctx)

	suite.Require().NoError(err)
	suite.NotNil(result)
	suite.Len(result, 3)
	suite.Equal(expectedProjects[0].ID, result[0].ID)
	suite.Equal(expectedProjects[1].Name, result[1].Name)
}

func (suite *ProjectServiceTestSuite) TestProjectService_GetProjectStats_Success() {
	projectID := testProjectIDValue
	ctx := context.Background()

	stats, err := suite.service.GetProjectStats(ctx, projectID)

	suite.Require().NoError(err)
	suite.NotNil(stats)
	suite.Equal(projectID, stats.ProjectID)
	suite.NotNil(stats.ItemsByType)
	suite.NotNil(stats.ItemsByStatus)
	suite.False(stats.UpdatedAt.IsZero())
}

func (suite *ProjectServiceTestSuite) TestProjectService_GetProjectStats_EmptyProject() {
	projectID := "empty-project"
	ctx := context.Background()

	stats, err := suite.service.GetProjectStats(ctx, projectID)

	suite.Require().NoError(err)
	suite.NotNil(stats)
	suite.Equal(int64(0), stats.TotalItems)
	suite.Equal(int64(0), stats.TotalLinks)
}
