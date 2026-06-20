//go:build !integration && !e2e

package services

import (
	"context"
	"errors"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/mock"
	"github.com/stretchr/testify/require"

	"github.com/kooshapari/tracertm-backend/internal/models"
)

func TestProjectService_Create_ValidationError_NoName(t *testing.T) {
	repo := new(MockProjectRepository)
	service := NewProjectService(repo)

	project := &models.Project{
		Name:        "",
		Description: "Test Description",
	}

	err := service.CreateProject(context.Background(), project)

	require.Error(t, err)
	assert.Contains(t, err.Error(), "name is required")
}

func TestProjectService_Create_RepositoryError(t *testing.T) {
	repo := new(MockProjectRepository)
	service := NewProjectService(repo)

	project := &models.Project{
		Name:        "Test Project",
		Description: "Test Description",
	}

	repo.On("Create", mock.Anything, project).Return(errors.New("database error"))

	err := service.CreateProject(context.Background(), project)

	require.Error(t, err)
}

func TestProjectService_Get_NotFound(t *testing.T) {
	repo := new(MockProjectRepository)
	service := NewProjectService(repo)

	repo.On("GetByID", mock.Anything, "nonexistent").Return(nil, errors.New("project not found"))

	result, err := service.GetProject(context.Background(), "nonexistent")

	require.Error(t, err)
	assert.Nil(t, result)
}

func TestProjectService_Update_ValidationError_NoID(t *testing.T) {
	repo := new(MockProjectRepository)
	service := NewProjectService(repo)

	project := &models.Project{
		ID:   "",
		Name: "Test Project",
	}

	err := service.UpdateProject(context.Background(), project)

	require.Error(t, err)
	assert.Contains(t, err.Error(), "ID is required")
}

func TestProjectService_Update_RepositoryError(t *testing.T) {
	repo := new(MockProjectRepository)
	service := NewProjectService(repo)

	project := &models.Project{
		ID:   testProjectIDValue,
		Name: "Updated Project",
	}

	repo.On("Update", mock.Anything, project).Return(errors.New("database error"))

	err := service.UpdateProject(context.Background(), project)

	require.Error(t, err)
}

func TestProjectService_Delete_RepositoryError(t *testing.T) {
	repo := new(MockProjectRepository)
	service := NewProjectService(repo)

	repo.On("Delete", mock.Anything, testProjectIDValue).Return(errors.New("database error"))

	err := service.DeleteProject(context.Background(), testProjectIDValue)

	require.Error(t, err)
}

func TestProjectService_List_RepositoryError(t *testing.T) {
	repo := new(MockProjectRepository)
	service := NewProjectService(repo)

	repo.On("List", mock.Anything).Return(nil, errors.New("database error"))

	result, err := service.ListProjects(context.Background())

	require.Error(t, err)
	assert.Nil(t, result)
}
