//go:build !integration && !e2e

package services

import (
	"context"
	"errors"
	"strings"
	"testing"

	"github.com/kooshapari/tracertm-backend/internal/models"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/mock"
	"github.com/stretchr/testify/suite"
)

// Mock project repository
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
	return args.Get(0).(*models.Project), args.Error(1)
}

func (m *MockProjectRepository) List(ctx context.Context) ([]*models.Project, error) {
	args := m.Called(ctx)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	return args.Get(0).([]*models.Project), args.Error(1)
}

func (m *MockProjectRepository) Update(ctx context.Context, project *models.Project) error {
	args := m.Called(ctx, project)
	return args.Error(0)
}

func (m *MockProjectRepository) Delete(ctx context.Context, id string) error {
	args := m.Called(ctx, id)
	return args.Error(0)
}

// ProjectServiceTestSuite provides test suite setup for project service tests
type ProjectServiceTestSuite struct {
	suite.Suite
	repo    *MockProjectRepository
	service ProjectService
	ctx     context.Context
}

func (suite *ProjectServiceTestSuite) SetupTest() {
	suite.repo = new(MockProjectRepository)
	suite.ctx = context.Background()
	suite.service = NewProjectService(suite.repo)
}

func (suite *ProjectServiceTestSuite) TearDownTest() {
	suite.repo.AssertExpectations(suite.T())
}

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

	assert.NoError(suite.T(), err)
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

	assert.NoError(suite.T(), err)
	assert.NotNil(suite.T(), result)
	assert.Equal(suite.T(), expectedProject.ID, result.ID)
	assert.Equal(suite.T(), expectedProject.Name, result.Name)
}

func (suite *ProjectServiceTestSuite) TestProjectService_Update_Success() {
	project := &models.Project{
		ID:          testProjectIDValue,
		Name:        "Updated Project",
		Description: "Updated Description",
	}

	suite.repo.On("Update", suite.ctx, project).Return(nil)

	err := suite.service.UpdateProject(suite.ctx, project)

	assert.NoError(suite.T(), err)
}

func (suite *ProjectServiceTestSuite) TestProjectService_Delete_Cascade() {
	// Tests that deleting a project triggers cascade deletion
	// (In a full implementation, this would also delete related items, links, agents)
	projectID := testProjectIDValue

	suite.repo.On("Delete", suite.ctx, projectID).Return(nil)

	err := suite.service.DeleteProject(suite.ctx, projectID)

	assert.NoError(suite.T(), err)
	// Verify repository delete was called (cascade handled at DB level)
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

	assert.NoError(suite.T(), err)
	assert.NotNil(suite.T(), result)
	assert.Len(suite.T(), result, 3)
	assert.Equal(suite.T(), expectedProjects[0].ID, result[0].ID)
	assert.Equal(suite.T(), expectedProjects[1].Name, result[1].Name)
}

// Additional unit tests without test suite

func TestProjectService_Create_ValidationError_NoName(t *testing.T) {
	repo := new(MockProjectRepository)
	service := NewProjectService(repo)

	project := &models.Project{
		Name:        "", // Empty name
		Description: "Test Description",
	}

	err := service.CreateProject(context.Background(), project)

	assert.Error(t, err)
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

	assert.Error(t, err)
	repo.AssertExpectations(t)
}

func TestProjectService_Get_NotFound(t *testing.T) {
	repo := new(MockProjectRepository)
	service := NewProjectService(repo)

	repo.On("GetByID", mock.Anything, "nonexistent").Return(nil, errors.New("project not found"))

	result, err := service.GetProject(context.Background(), "nonexistent")

	assert.Error(t, err)
	assert.Nil(t, result)
	repo.AssertExpectations(t)
}

func TestProjectService_Update_ValidationError_NoID(t *testing.T) {
	repo := new(MockProjectRepository)
	service := NewProjectService(repo)

	project := &models.Project{
		ID:   "", // Empty ID
		Name: "Test Project",
	}

	err := service.UpdateProject(context.Background(), project)

	assert.Error(t, err)
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

	assert.Error(t, err)
	repo.AssertExpectations(t)
}

func TestProjectService_Delete_RepositoryError(t *testing.T) {
	repo := new(MockProjectRepository)
	service := NewProjectService(repo)

	repo.On("Delete", mock.Anything, testProjectIDValue).Return(errors.New("database error"))

	err := service.DeleteProject(context.Background(), testProjectIDValue)

	assert.Error(t, err)
	repo.AssertExpectations(t)
}

func TestProjectService_List_EmptyResults(t *testing.T) {
	repo := new(MockProjectRepository)
	service := NewProjectService(repo)

	repo.On("List", mock.Anything).Return([]*models.Project{}, nil)

	result, err := service.ListProjects(context.Background())

	assert.NoError(t, err)
	assert.NotNil(t, result)
	assert.Len(t, result, 0)
	repo.AssertExpectations(t)
}

func TestProjectService_List_RepositoryError(t *testing.T) {
	repo := new(MockProjectRepository)
	service := NewProjectService(repo)

	repo.On("List", mock.Anything).Return(nil, errors.New("database error"))

	result, err := service.ListProjects(context.Background())

	assert.Error(t, err)
	assert.Nil(t, result)
	repo.AssertExpectations(t)
}

func TestProjectService_CRUDWorkflow(t *testing.T) {
	// Integration-style test of full CRUD workflow (still using mocks)
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
	assert.NoError(t, err)

	// Read
	project.ID = testProjectIDValue // Simulate ID generation
	repo.On("GetByID", ctx, project.ID).Return(project, nil).Once()
	retrieved, err := service.GetProject(ctx, project.ID)
	assert.NoError(t, err)
	assert.Equal(t, project.Name, retrieved.Name)

	// Update
	project.Name = "Updated Workflow Test"
	repo.On("Update", ctx, project).Return(nil).Once()
	err = service.UpdateProject(ctx, project)
	assert.NoError(t, err)

	// Delete
	repo.On("Delete", ctx, project.ID).Return(nil).Once()
	err = service.DeleteProject(ctx, project.ID)
	assert.NoError(t, err)

	repo.AssertExpectations(t)
}

func TestProjectService_MultipleProjects_Pagination(t *testing.T) {
	// Test listing with many projects (simulates pagination behavior)
	repo := new(MockProjectRepository)
	service := NewProjectService(repo)

	projects := make([]*models.Project, 0, 50)
	for i := 0; i < 50; i++ {
		projects = append(projects, &models.Project{
			ID:          string(rune('a' + i)),
			Name:        "Project " + string(rune('0'+i)),
			Description: "Description",
		})
	}

	repo.On("List", mock.Anything).Return(projects, nil)

	result, err := service.ListProjects(context.Background())

	assert.NoError(t, err)
	assert.Len(t, result, 50)
	repo.AssertExpectations(t)
}

func TestProjectService_ConcurrentOperations(t *testing.T) {
	// Test concurrent project operations
	repo := new(MockProjectRepository)
	service := NewProjectService(repo)

	project1 := &models.Project{ID: "project-1", Name: "Project 1"}
	project2 := &models.Project{ID: "project-2", Name: "Project 2"}

	repo.On("GetByID", mock.Anything, "project-1").Return(project1, nil)
	repo.On("GetByID", mock.Anything, "project-2").Return(project2, nil)

	// Simulate concurrent reads
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

	repo.AssertExpectations(t)
}

// Edge case tests for ProjectService

func TestProjectService_Create_WithSpecialCharacters(t *testing.T) {
	// Test creating project with special characters in name and description
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

	assert.NoError(t, err)
	repo.AssertExpectations(t)
}

func TestProjectService_Create_WithVeryLongName(t *testing.T) {
	// Test creating project with very long name (up to 500 characters)
	repo := new(MockProjectRepository)
	service := NewProjectService(repo)

	longName := strings.Repeat("This is a very long project name component ", 50)

	project := &models.Project{
		Name:        longName,
		Description: "Project with extremely long name",
	}

	repo.On("Create", mock.Anything, project).Return(nil)

	err := service.CreateProject(context.Background(), project)

	assert.NoError(t, err)
	repo.AssertExpectations(t)
}

func TestProjectService_Create_EmptyDescription(t *testing.T) {
	// Test creating project with empty description
	repo := new(MockProjectRepository)
	service := NewProjectService(repo)

	project := &models.Project{
		Name:        "Test Project",
		Description: "",
	}

	repo.On("Create", mock.Anything, project).Return(nil)

	err := service.CreateProject(context.Background(), project)

	assert.NoError(t, err)
	repo.AssertExpectations(t)
}

func TestProjectService_Get_MultipleCalls(t *testing.T) {
	// Test getting same project multiple times (no caching in ProjectService)
	repo := new(MockProjectRepository)
	service := NewProjectService(repo)

	projectID := testProjectIDValue
	expectedProject := &models.Project{
		ID:          projectID,
		Name:        "Test Project",
		Description: "Test Description",
	}

	// Repository should be called each time (no caching implemented)
	repo.On("GetByID", mock.Anything, projectID).Return(expectedProject, nil)

	// Get the same project twice
	result1, err1 := service.GetProject(context.Background(), projectID)
	assert.NoError(t, err1)
	assert.NotNil(t, result1)

	result2, err2 := service.GetProject(context.Background(), projectID)
	assert.NoError(t, err2)
	assert.NotNil(t, result2)

	// Both results should be equal
	assert.Equal(t, result1.ID, result2.ID)
	repo.AssertExpectations(t)
}

func TestProjectService_Update_WithSpecialCharacters(t *testing.T) {
	// Test updating project with special characters
	repo := new(MockProjectRepository)
	service := NewProjectService(repo)

	updatedProject := &models.Project{
		ID:          testProjectIDValue,
		Name:        "Updated Project 更新 ✨",
		Description: "Updated description with émojis 🎉",
	}

	repo.On("Update", mock.Anything, updatedProject).Return(nil)

	err := service.UpdateProject(context.Background(), updatedProject)

	assert.NoError(t, err)
	repo.AssertExpectations(t)
}

func TestProjectService_Update_SameProjectMultipleTimes(t *testing.T) {
	// Test updating same project multiple times
	repo := new(MockProjectRepository)
	service := NewProjectService(repo)

	projectID := testProjectIDValue

	project1 := &models.Project{
		ID:          projectID,
		Name:        "Version 1",
		Description: "First version",
	}

	project2 := &models.Project{
		ID:          projectID,
		Name:        "Version 2",
		Description: "Second version",
	}

	repo.On("Update", mock.Anything, project1).Return(nil)
	repo.On("Update", mock.Anything, project2).Return(nil)

	err1 := service.UpdateProject(context.Background(), project1)
	assert.NoError(t, err1)

	err2 := service.UpdateProject(context.Background(), project2)
	assert.NoError(t, err2)

	repo.AssertExpectations(t)
}

func TestProjectService_Delete_NonExistentProject(t *testing.T) {
	// Test deleting a project that doesn't exist
	repo := new(MockProjectRepository)
	service := NewProjectService(repo)

	projectID := "nonexistent-project"

	// Repository deletion should succeed even for non-existent items
	repo.On("Delete", mock.Anything, projectID).Return(nil)

	err := service.DeleteProject(context.Background(), projectID)

	assert.NoError(t, err)
	repo.AssertExpectations(t)
}

func TestProjectService_Delete_WithInvalidID(t *testing.T) {
	// Test deleting with empty or invalid ID
	repo := new(MockProjectRepository)
	service := NewProjectService(repo)

	invalidID := ""

	// Should still call repository (validation is optional)
	repo.On("Delete", mock.Anything, invalidID).Return(nil)

	err := service.DeleteProject(context.Background(), invalidID)

	assert.NoError(t, err)
	repo.AssertExpectations(t)
}

func TestProjectService_List_LargeResultSet(t *testing.T) {
	// Test listing with a large number of projects (1000+)
	repo := new(MockProjectRepository)
	service := NewProjectService(repo)

	projects := make([]*models.Project, 0, 1000)
	for i := 0; i < 1000; i++ {
		projects = append(projects, &models.Project{
			ID:          "project-" + string(rune(i)),
			Name:        "Project " + string(rune(i)),
			Description: "Description",
		})
	}

	repo.On("List", mock.Anything).Return(projects, nil)

	result, err := service.ListProjects(context.Background())

	assert.NoError(t, err)
	assert.Len(t, result, 1000)
	repo.AssertExpectations(t)
}

func TestProjectService_Create_AllDefaults(t *testing.T) {
	// Test creating project with minimal fields
	repo := new(MockProjectRepository)
	service := NewProjectService(repo)

	project := &models.Project{
		Name: "Minimal Project",
	}

	repo.On("Create", mock.Anything, project).Return(nil)

	err := service.CreateProject(context.Background(), project)

	assert.NoError(t, err)
	repo.AssertExpectations(t)
}

func TestProjectService_Concurrent_MixedOperations(t *testing.T) {
	// Test concurrent mixed CRUD operations
	repo := new(MockProjectRepository)
	service := NewProjectService(repo)

	projects := []*models.Project{
		{ID: "p1", Name: "Project 1"},
		{ID: "p2", Name: "Project 2"},
		{ID: "p3", Name: "Project 3"},
	}

	repo.On("GetByID", mock.Anything, "p1").Return(projects[0], nil)
	repo.On("GetByID", mock.Anything, "p2").Return(projects[1], nil)
	repo.On("GetByID", mock.Anything, "p3").Return(projects[2], nil)
	repo.On("Create", mock.Anything, mock.AnythingOfType("*models.Project")).Return(nil)
	repo.On("Update", mock.Anything, mock.AnythingOfType("*models.Project")).Return(nil)
	repo.On("Delete", mock.Anything, mock.AnythingOfType("string")).Return(nil)

	done := make(chan bool, 9)

	// 3 concurrent reads
	for i := 0; i < 3; i++ {
		go func(idx int) {
			_, err := service.GetProject(context.Background(), projects[idx].ID)
			assert.NoError(t, err)
			done <- true
		}(i)
	}

	// 2 concurrent creates
	for i := 0; i < 2; i++ {
		go func() {
			err := service.CreateProject(context.Background(), &models.Project{Name: "New Project"})
			assert.NoError(t, err)
			done <- true
		}()
	}

	// 2 concurrent updates
	for i := 0; i < 2; i++ {
		go func(idx int) {
			err := service.UpdateProject(context.Background(), projects[idx])
			assert.NoError(t, err)
			done <- true
		}(i)
	}

	// 2 concurrent deletes
	for i := 0; i < 2; i++ {
		go func(idx int) {
			err := service.DeleteProject(context.Background(), projects[idx].ID)
			assert.NoError(t, err)
			done <- true
		}(i)
	}

	// Wait for all goroutines to finish
	for i := 0; i < 9; i++ {
		<-done
	}

	repo.AssertExpectations(t)
}

func TestProjectService_Update_PreservesID(t *testing.T) {
	// Test that updating a project preserves its ID
	repo := new(MockProjectRepository)
	service := NewProjectService(repo)

	projectID := testProjectIDValue
	updatedProject := &models.Project{
		ID:          projectID,
		Name:        "Updated Name",
		Description: "Updated Description",
	}

	repo.On("Update", mock.Anything, mock.MatchedBy(func(p *models.Project) bool {
		return p.ID == projectID
	})).Return(nil)

	err := service.UpdateProject(context.Background(), updatedProject)

	assert.NoError(t, err)
	assert.Equal(t, projectID, updatedProject.ID)
	repo.AssertExpectations(t)
}

// GetProjectStats tests

func TestProjectService_GetProjectStats_Success(t *testing.T) {
	repo := new(MockProjectRepository)
	service := NewProjectService(repo)

	projectID := testProjectIDValue
	ctx := context.Background()

	stats, err := service.GetProjectStats(ctx, projectID)

	assert.NoError(t, err)
	assert.NotNil(t, stats)
	assert.Equal(t, projectID, stats.ProjectID)
	assert.NotNil(t, stats.ItemsByType)
	assert.NotNil(t, stats.ItemsByStatus)
	assert.False(t, stats.UpdatedAt.IsZero())
}

func TestProjectService_GetProjectStats_EmptyProject(t *testing.T) {
	repo := new(MockProjectRepository)
	service := NewProjectService(repo)

	projectID := "empty-project"
	ctx := context.Background()

	stats, err := service.GetProjectStats(ctx, projectID)

	assert.NoError(t, err)
	assert.NotNil(t, stats)
	assert.Equal(t, int64(0), stats.TotalItems)
	assert.Equal(t, int64(0), stats.TotalLinks)
}

func TestProjectService_GetProjectStats_WithContext(t *testing.T) {
	repo := new(MockProjectRepository)
	service := NewProjectService(repo)

	projectID := "project-456"
	ctx := context.Background()

	stats, err := service.GetProjectStats(ctx, projectID)

	assert.NoError(t, err)
	assert.NotNil(t, stats)
	assert.Equal(t, projectID, stats.ProjectID)
}
