//go:build !integration && !e2e

package services

import (
	"context"
	"strings"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/mock"
	"github.com/stretchr/testify/require"

	"github.com/kooshapari/tracertm-backend/internal/models"
)

func TestProjectService_CRUDWorkflow(t *testing.T) {
	repo := new(MockProjectRepository)
	service := NewProjectService(repo)
	ctx := context.Background()

	// Create
	project := &models.Project{
		Name:        "Workflow Test",
		Description: "Testing CRUD workflow",
	}
	repo.On("Create", ctx, project).Return(nil).Once()
	err := service.CreateProject(ctx, project)
	require.NoError(t, err)

	// Read
	project.ID = testProjectIDValue
	repo.On("GetByID", ctx, project.ID).Return(project, nil).Once()
	retrieved, err := service.GetProject(ctx, project.ID)
	require.NoError(t, err)
	assert.Equal(t, project.Name, retrieved.Name)

	// Update
	project.Name = "Updated Workflow Test"
	repo.On("Update", ctx, project).Return(nil).Once()
	err = service.UpdateProject(ctx, project)
	require.NoError(t, err)

	// Delete
	repo.On("Delete", ctx, project.ID).Return(nil).Once()
	err = service.DeleteProject(ctx, project.ID)
	require.NoError(t, err)
}

func TestProjectService_Create_WithSpecialCharacters(t *testing.T) {
	repo := new(MockProjectRepository)
	service := NewProjectService(repo)

	project := &models.Project{
		Name:        "Project with 特殊文字 & émojis 🚀",
		Description: "Description with <html> & \"quotes\" 'apostrophes' and 中文",
	}

	repo.On("Create", mock.Anything, mock.MatchedBy(func(p *models.Project) bool {
		return p.Name == project.Name && p.Description == project.Description
	})).Return(nil)

	err := service.CreateProject(context.Background(), project)

	require.NoError(t, err)
}

func TestProjectService_Create_WithVeryLongName(t *testing.T) {
	repo := new(MockProjectRepository)
	service := NewProjectService(repo)

	longName := strings.Repeat("This is a very long project name component ", 50)

	project := &models.Project{
		Name:        longName,
		Description: "Project with extremely long name",
	}

	repo.On("Create", mock.Anything, project).Return(nil)

	err := service.CreateProject(context.Background(), project)

	require.NoError(t, err)
}

func TestProjectService_ConcurrentOperations(t *testing.T) {
	repo := new(MockProjectRepository)
	service := NewProjectService(repo)

	project1 := &models.Project{ID: "project-1", Name: "Project 1"}
	project2 := &models.Project{ID: "project-2", Name: "Project 2"}

	repo.On("GetByID", mock.Anything, "project-1").Return(project1, nil)
	repo.On("GetByID", mock.Anything, "project-2").Return(project2, nil)

	done := make(chan bool, 2)

	go func() {
		_, err := service.GetProject(context.Background(), "project-1")
		assert.NoError(t, err)
		done <- true
	}()

	go func() {
		_, err := service.GetProject(context.Background(), "project-2")
		assert.NoError(t, err)
		done <- true
	}()

	<-done
	<-done
}
