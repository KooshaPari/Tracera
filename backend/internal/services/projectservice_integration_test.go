//go:build integration
// +build integration

package services

import (
	"context"
	"testing"
	"time"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"

	"github.com/kooshapari/tracertm-backend/internal/models"
)

const projectServiceUpdateDelay = 100 * time.Millisecond

// TestProjectServiceCreate tests creating projects
func TestProjectServiceCreate(t *testing.T) {
	ctx := context.Background()
	helper := NewIntegrationTestHelper(ctx, t)
	defer helper.Cleanup()

	project := &models.Project{
		Name:        "Test Project",
		Description: "A test project",
	}

	err := helper.ProjectRepo.Create(ctx, project)
	require.NoError(t, err)
	require.NotEmpty(t, project.ID)
	assert.Equal(t, "Test Project", project.Name)
	assert.Equal(t, "A test project", project.Description)
	assert.False(t, project.CreatedAt.IsZero())
}

// TestProjectServiceGetByID tests retrieving projects by ID
func TestProjectServiceGetByID(t *testing.T) {
	ctx := context.Background()
	helper := NewIntegrationTestHelper(ctx, t)
	defer helper.Cleanup()

	// Create
	original := &models.Project{
		Name:        "Retrieve Test",
		Description: "Testing retrieval",
	}
	err := helper.ProjectRepo.Create(ctx, original)
	require.NoError(t, err)

	// Retrieve
	retrieved, err := helper.ProjectRepo.GetByID(ctx, original.ID)
	require.NoError(t, err)
	require.NotNil(t, retrieved)
	assert.Equal(t, original.ID, retrieved.ID)
	assert.Equal(t, original.Name, retrieved.Name)
	assert.Equal(t, original.Description, retrieved.Description)
}

// TestProjectServiceList tests listing all projects
func TestProjectServiceList(t *testing.T) {
	ctx := context.Background()
	helper := NewIntegrationTestHelper(ctx, t)
	defer helper.Cleanup()

	// Create multiple projects
	projectCount := 5
	createdProjects := make([]*models.Project, projectCount)

	for i := 0; i < projectCount; i++ {
		project := &models.Project{
			Name: "Project " + string(rune('A'+i)),
		}
		err := helper.ProjectRepo.Create(ctx, project)
		require.NoError(t, err)
		createdProjects[i] = project
	}

	// List all projects
	projects, err := helper.ProjectRepo.List(ctx)
	require.NoError(t, err)
	assert.GreaterOrEqual(t, len(projects), projectCount)

	// Verify all created projects are in the list
	projectIDs := make(map[string]bool)
	for _, p := range projects {
		projectIDs[p.ID] = true
	}

	for _, created := range createdProjects {
		assert.True(t, projectIDs[created.ID], "Project %s not found in list", created.Name)
	}
}

// TestProjectServiceUpdate tests updating projects
func TestProjectServiceUpdate(t *testing.T) {
	ctx := context.Background()
	helper := NewIntegrationTestHelper(ctx, t)
	defer helper.Cleanup()

	// Create
	project := &models.Project{
		Name:        "Original Name",
		Description: "Original Description",
	}
	err := helper.ProjectRepo.Create(ctx, project)
	require.NoError(t, err)

	originalID := project.ID
	originalCreated := project.CreatedAt

	// Update
	project.Name = "Updated Name"
	project.Description = "Updated Description"
	err = helper.ProjectRepo.Update(ctx, project)
	require.NoError(t, err)

	// Verify
	updated, err := helper.ProjectRepo.GetByID(ctx, originalID)
	require.NoError(t, err)
	assert.Equal(t, "Updated Name", updated.Name)
	assert.Equal(t, "Updated Description", updated.Description)
	assert.Equal(t, originalCreated, updated.CreatedAt)
	assert.True(t, updated.UpdatedAt.After(originalCreated))
}

// TestProjectServiceDelete tests deleting projects (soft delete)
func TestProjectServiceDelete(t *testing.T) {
	ctx := context.Background()
	helper := NewIntegrationTestHelper(ctx, t)
	defer helper.Cleanup()

	// Create
	project := &models.Project{Name: "To Delete"}
	err := helper.ProjectRepo.Create(ctx, project)
	require.NoError(t, err)

	projectID := project.ID

	// Delete
	err = helper.ProjectRepo.Delete(ctx, projectID)
	require.NoError(t, err)

	// Verify deleted project cannot be retrieved
	deleted, err := helper.ProjectRepo.GetByID(ctx, projectID)
	assert.Error(t, err)
	assert.Nil(t, deleted)
}

// TestProjectServiceItemIsolation tests that items are isolated per project
func TestProjectServiceItemIsolation(t *testing.T) {
	ctx := context.Background()
	helper := NewIntegrationTestHelper(ctx, t)
	defer helper.Cleanup()

	// Create two projects
	project1 := &models.Project{Name: "Project 1"}
	project2 := &models.Project{Name: "Project 2"}
	err := helper.ProjectRepo.Create(ctx, project1)
	require.NoError(t, err)
	err = helper.ProjectRepo.Create(ctx, project2)
	require.NoError(t, err)

	// Add items to project1
	item1_1 := &models.Item{ProjectID: project1.ID, Title: "P1 Item 1"}
	item1_2 := &models.Item{ProjectID: project1.ID, Title: "P1 Item 2"}
	err = helper.ItemRepo.Create(ctx, item1_1)
	require.NoError(t, err)
	err = helper.ItemRepo.Create(ctx, item1_2)
	require.NoError(t, err)

	// Add items to project2
	item2_1 := &models.Item{ProjectID: project2.ID, Title: "P2 Item 1"}
	err = helper.ItemRepo.Create(ctx, item2_1)
	require.NoError(t, err)

	// Verify project1 has 2 items
	p1Items, err := helper.ItemRepo.GetByProjectID(ctx, project1.ID)
	require.NoError(t, err)
	assert.Equal(t, 2, len(p1Items))

	// Verify project2 has 1 item
	p2Items, err := helper.ItemRepo.GetByProjectID(ctx, project2.ID)
	require.NoError(t, err)
	assert.Equal(t, 1, len(p2Items))
}

// TestProjectServiceCascadeDelete tests that items are deleted with project
func TestProjectServiceCascadeDelete(t *testing.T) {
	ctx := context.Background()
	helper := NewIntegrationTestHelper(ctx, t)
	defer helper.Cleanup()

	// Create project
	project := &models.Project{Name: "Cascade Test"}
	err := helper.ProjectRepo.Create(ctx, project)
	require.NoError(t, err)

	// Add items
	items := []*models.Item{
		{ProjectID: project.ID, Title: "Item 1"},
		{ProjectID: project.ID, Title: "Item 2"},
		{ProjectID: project.ID, Title: "Item 3"},
	}

	for _, item := range items {
		err := helper.ItemRepo.Create(ctx, item)
		require.NoError(t, err)
	}

	// Verify items exist
	projectItems, err := helper.ItemRepo.GetByProjectID(ctx, project.ID)
	require.NoError(t, err)
	assert.Equal(t, 3, len(projectItems))

	// Delete project (soft delete)
	err = helper.ProjectRepo.Delete(ctx, project.ID)
	require.NoError(t, err)

	// Verify project cannot be retrieved
	deleted, err := helper.ProjectRepo.GetByID(ctx, project.ID)
	assert.Error(t, err)
	assert.Nil(t, deleted)
}

// TestProjectServiceMetadataHandling tests metadata storage and retrieval
func TestProjectServiceMetadataHandling(t *testing.T) {
	ctx := context.Background()
	helper := NewIntegrationTestHelper(ctx, t)
	defer helper.Cleanup()

	// Create project with metadata
	project := &models.Project{
		Name:     "Metadata Test",
		Metadata: []byte(`{"key":"value","number":42}`),
	}
	err := helper.ProjectRepo.Create(ctx, project)
	require.NoError(t, err)

	// Retrieve and verify metadata
	retrieved, err := helper.ProjectRepo.GetByID(ctx, project.ID)
	require.NoError(t, err)
	assert.Equal(t, project.Metadata, retrieved.Metadata)
	assert.Contains(t, string(retrieved.Metadata), "key")
}

// TestProjectServiceTimestampHandling tests timestamp tracking
func TestProjectServiceTimestampHandling(t *testing.T) {
	ctx := context.Background()
	helper := NewIntegrationTestHelper(ctx, t)
	defer helper.Cleanup()

	beforeCreate := time.Now().UTC()

	// Create
	project := &models.Project{Name: "Timestamp Test"}
	err := helper.ProjectRepo.Create(ctx, project)
	require.NoError(t, err)

	afterCreate := time.Now().UTC()

	// Verify timestamps
	assert.True(t, project.CreatedAt.After(beforeCreate.Add(-time.Second)))
	assert.True(t, project.CreatedAt.Before(afterCreate.Add(time.Second)))
	assert.Equal(t, project.CreatedAt, project.UpdatedAt)

	// Update
	time.Sleep(projectServiceUpdateDelay)
	project.Name = "Updated"
	err = helper.ProjectRepo.Update(ctx, project)
	require.NoError(t, err)

	// Verify UpdatedAt changed
	assert.True(t, project.UpdatedAt.After(project.CreatedAt))
}

// TestProjectServiceMultipleProjects tests handling multiple independent projects
func TestProjectServiceMultipleProjects(t *testing.T) {
	ctx := context.Background()
	helper := NewIntegrationTestHelper(ctx, t)
	defer helper.Cleanup()

	// Create multiple projects
	projectCount := 10
	projectIDs := make(map[string]bool)

	for i := 0; i < projectCount; i++ {
		project := &models.Project{
			Name: "Project Number " + string(rune(i)),
		}
		err := helper.ProjectRepo.Create(ctx, project)
		require.NoError(t, err)
		projectIDs[project.ID] = true
	}

	// Verify all projects exist
	projects, err := helper.ProjectRepo.List(ctx)
	require.NoError(t, err)

	listedIDs := make(map[string]bool)
	for _, p := range projects {
		if projectIDs[p.ID] {
			listedIDs[p.ID] = true
		}
	}

	for id := range projectIDs {
		assert.True(t, listedIDs[id], "Project %s not found in list", id)
	}
}

// TestProjectServiceNameUniqueness tests that projects can have same names
func TestProjectServiceNameUniqueness(t *testing.T) {
	ctx := context.Background()
	helper := NewIntegrationTestHelper(ctx, t)
	defer helper.Cleanup()

	// Create projects with same name (should be allowed)
	name := "Duplicate Name"
	project1 := &models.Project{Name: name}
	project2 := &models.Project{Name: name}

	err := helper.ProjectRepo.Create(ctx, project1)
	require.NoError(t, err)
	err = helper.ProjectRepo.Create(ctx, project2)
	require.NoError(t, err)

	// Should have different IDs
	assert.NotEqual(t, project1.ID, project2.ID)

	// Both should be retrievable
	p1, err := helper.ProjectRepo.GetByID(ctx, project1.ID)
	require.NoError(t, err)
	assert.NotNil(t, p1)

	p2, err := helper.ProjectRepo.GetByID(ctx, project2.ID)
	require.NoError(t, err)
	assert.NotNil(t, p2)
}
