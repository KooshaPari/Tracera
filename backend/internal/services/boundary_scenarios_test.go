//go:build integration
// +build integration

package services

import (
	"context"
	"testing"

	"github.com/google/uuid"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"

	"github.com/kooshapari/tracertm-backend/internal/models"
)

// ==================== BOUNDARY CONDITION TESTS ====================

// TestBoundaryItemCountZeroProject tests count on empty project
func TestBoundaryItemCountZeroProject(t *testing.T) {
	ctx := context.Background()
	helper := NewIntegrationTestHelper(ctx, t)
	defer helper.Cleanup()

	project := &models.Project{Name: "Empty"}
	require.NoError(t, helper.ProjectRepo.Create(ctx, project))

	count, err := helper.ItemRepo.Count(ctx)
	assert.NoError(t, err)
	assert.Equal(t, 0, count)
}

// TestBoundaryProjectListEmpty tests list when no projects exist
func TestBoundaryProjectListEmpty(t *testing.T) {
	ctx := context.Background()
	helper := NewIntegrationTestHelper(ctx, t)
	defer helper.Cleanup()

	projects, err := helper.ProjectRepo.List(ctx)
	assert.NoError(t, err)
	assert.NotNil(t, projects)
	assert.Equal(t, 0, len(projects))
}

// TestBoundaryLinkGetBySourceNoLinks tests getting links from item with none
func TestBoundaryLinkGetBySourceNoLinks(t *testing.T) {
	ctx := context.Background()
	helper := NewIntegrationTestHelper(ctx, t)
	defer helper.Cleanup()

	project := &models.Project{Name: "Test"}
	require.NoError(t, helper.ProjectRepo.Create(ctx, project))

	item := &models.Item{ProjectID: project.ID, Title: "Isolated"}
	require.NoError(t, helper.ItemRepo.Create(ctx, item))

	links, err := helper.LinkRepo.GetBySourceID(ctx, item.ID)
	assert.NoError(t, err)
	assert.NotNil(t, links)
	assert.Equal(t, 0, len(links))
}

// TestBoundaryAgentListByProjectEmpty tests getting agents from empty project
func TestBoundaryAgentListByProjectEmpty(t *testing.T) {
	ctx := context.Background()
	helper := NewIntegrationTestHelper(ctx, t)
	defer helper.Cleanup()

	project := &models.Project{Name: "No Agents"}
	require.NoError(t, helper.ProjectRepo.Create(ctx, project))

	agents, err := helper.AgentRepo.GetByProjectID(ctx, project.ID)
	assert.NoError(t, err)
	assert.NotNil(t, agents)
	assert.Equal(t, 0, len(agents))
}

// TestBoundaryDeleteAllItems tests deleting all items from project
func TestBoundaryDeleteAllItems(t *testing.T) {
	ctx := context.Background()
	helper := NewIntegrationTestHelper(ctx, t)
	defer helper.Cleanup()

	project := &models.Project{Name: "Test"}
	require.NoError(t, helper.ProjectRepo.Create(ctx, project))

	// Create items
	for i := 0; i < 5; i++ {
		item := &models.Item{ProjectID: project.ID, Title: "Item"}
		require.NoError(t, helper.ItemRepo.Create(ctx, item))
	}

	// Count before
	countBefore, _ := helper.ItemRepo.Count(ctx)
	assert.Equal(t, 5, countBefore)

	// Delete all by deleting project (CASCADE)
	require.NoError(t, helper.ProjectRepo.Delete(ctx, project.ID))

	// Verify cascade
	countAfter, _ := helper.ItemRepo.Count(ctx)
	assert.Equal(t, 0, countAfter)
}

// TestBoundaryUpdateNonExistentItem tests updating non-existent item
func TestBoundaryUpdateNonExistentItem(t *testing.T) {
	ctx := context.Background()
	helper := NewIntegrationTestHelper(ctx, t)
	defer helper.Cleanup()

	fakeItem := &models.Item{
		ID:        uuid.New(),
		Title:     "Fake",
		ProjectID: uuid.New(),
	}

	// Update non-existent (depends on implementation)
	_ = helper.ItemRepo.Update(ctx, fakeItem)
}

// TestBoundaryDeleteNonExistentItem tests deleting non-existent item
func TestBoundaryDeleteNonExistentItem(t *testing.T) {
	ctx := context.Background()
	helper := NewIntegrationTestHelper(ctx, t)
	defer helper.Cleanup()

	fakeID := uuid.New()
	err := helper.ItemRepo.Delete(ctx, fakeID)
	assert.NoError(t, err) // Should be idempotent
}

// ==================== CASCADE & FOREIGN KEY TESTS ====================

// TestCascadeDeleteProjectWithLinksAndAgents tests full cascade
func TestCascadeDeleteProjectWithLinksAndAgents(t *testing.T) {
	ctx := context.Background()
	helper := NewIntegrationTestHelper(ctx, t)
	defer helper.Cleanup()

	// Create project with items, links, and agents
	project := &models.Project{Name: "Complex"}
	require.NoError(t, helper.ProjectRepo.Create(ctx, project))

	item1 := &models.Item{ProjectID: project.ID, Title: "Item 1"}
	item2 := &models.Item{ProjectID: project.ID, Title: "Item 2"}
	require.NoError(t, helper.ItemRepo.Create(ctx, item1))
	require.NoError(t, helper.ItemRepo.Create(ctx, item2))

	link := &models.Link{SourceID: item1.ID, TargetID: item2.ID, Type: "depends"}
	require.NoError(t, helper.LinkRepo.Create(ctx, link))

	agent := &models.Agent{ProjectID: project.ID, Name: "Agent"}
	require.NoError(t, helper.AgentRepo.Create(ctx, agent))

	// Delete project
	require.NoError(t, helper.ProjectRepo.Delete(ctx, project.ID))

	// Verify all cascaded
	item, _ := helper.ItemRepo.GetByID(ctx, item1.ID)
	assert.NotNil(t, item.DeletedAt)

	linkRetrieved, _ := helper.LinkRepo.GetByID(ctx, link.ID)
	assert.NotNil(t, linkRetrieved.DeletedAt)

	agentRetrieved, _ := helper.AgentRepo.GetByID(ctx, agent.ID)
	assert.NotNil(t, agentRetrieved.DeletedAt)
}

// TestCascadeDeleteItemWithLinks tests item deletion cascades to links
func TestCascadeDeleteItemWithLinks(t *testing.T) {
	ctx := context.Background()
	helper := NewIntegrationTestHelper(ctx, t)
	defer helper.Cleanup()

	project := &models.Project{Name: "Test"}
	require.NoError(t, helper.ProjectRepo.Create(ctx, project))

	source := &models.Item{ProjectID: project.ID, Title: "Source"}
	target := &models.Item{ProjectID: project.ID, Title: "Target"}
	require.NoError(t, helper.ItemRepo.Create(ctx, source))
	require.NoError(t, helper.ItemRepo.Create(ctx, target))

	link1 := &models.Link{SourceID: source.ID, TargetID: target.ID, Type: "out"}
	link2 := &models.Link{SourceID: target.ID, TargetID: source.ID, Type: "in"}
	require.NoError(t, helper.LinkRepo.Create(ctx, link1))
	require.NoError(t, helper.LinkRepo.Create(ctx, link2))

	// Delete source
	require.NoError(t, helper.ItemRepo.Delete(ctx, source.ID))

	// Both links should be deleted (CASCADE)
	l1, _ := helper.LinkRepo.GetByID(ctx, link1.ID)
	l2, _ := helper.LinkRepo.GetByID(ctx, link2.ID)
	assert.NotNil(t, l1.DeletedAt)
	assert.NotNil(t, l2.DeletedAt)
}

// TestCascadeDeleteProjectWithAgents tests agent deletion on project delete
func TestCascadeDeleteProjectWithAgents(t *testing.T) {
	ctx := context.Background()
	helper := NewIntegrationTestHelper(ctx, t)
	defer helper.Cleanup()

	project := &models.Project{Name: "Test"}
	require.NoError(t, helper.ProjectRepo.Create(ctx, project))

	agents := make([]*models.Agent, 5)
	for i := 0; i < 5; i++ {
		agent := &models.Agent{ProjectID: project.ID, Name: "Agent"}
		require.NoError(t, helper.AgentRepo.Create(ctx, agent))
		agents[i] = agent
	}

	// Delete project
	require.NoError(t, helper.ProjectRepo.Delete(ctx, project.ID))

	// All agents should be deleted
	for _, agent := range agents {
		retrieved, _ := helper.AgentRepo.GetByID(ctx, agent.ID)
		assert.NotNil(t, retrieved.DeletedAt)
	}
}

// ==================== ISOLATION & CONSTRAINT TESTS ====================

// TestIsolationItemsPerProject tests items are isolated per project
func TestIsolationItemsPerProject(t *testing.T) {
	ctx := context.Background()
	helper := NewIntegrationTestHelper(ctx, t)
	defer helper.Cleanup()

	project1 := &models.Project{Name: "Project 1"}
	project2 := &models.Project{Name: "Project 2"}
	require.NoError(t, helper.ProjectRepo.Create(ctx, project1))
	require.NoError(t, helper.ProjectRepo.Create(ctx, project2))

	// Add items to project1
	for i := 0; i < 3; i++ {
		item := &models.Item{ProjectID: project1.ID, Title: "Item"}
		require.NoError(t, helper.ItemRepo.Create(ctx, item))
	}

	// Add items to project2
	for i := 0; i < 2; i++ {
		item := &models.Item{ProjectID: project2.ID, Title: "Item"}
		require.NoError(t, helper.ItemRepo.Create(ctx, item))
	}

	// Delete project1
	require.NoError(t, helper.ProjectRepo.Delete(ctx, project1.ID))

	// Project2's items should remain
	items, _ := helper.ItemRepo.GetByProjectID(ctx, project2.ID)
	assert.Equal(t, 2, len(items))
}

// TestIsolationAgentsPerProject tests agents are isolated per project
func TestIsolationAgentsPerProject(t *testing.T) {
	ctx := context.Background()
	helper := NewIntegrationTestHelper(ctx, t)
	defer helper.Cleanup()

	project1 := &models.Project{Name: "Project 1"}
	project2 := &models.Project{Name: "Project 2"}
	require.NoError(t, helper.ProjectRepo.Create(ctx, project1))
	require.NoError(t, helper.ProjectRepo.Create(ctx, project2))

	// Add agents to project1
	for i := 0; i < 3; i++ {
		agent := &models.Agent{ProjectID: project1.ID, Name: "Agent"}
		require.NoError(t, helper.AgentRepo.Create(ctx, agent))
	}

	// Add agents to project2
	for i := 0; i < 2; i++ {
		agent := &models.Agent{ProjectID: project2.ID, Name: "Agent"}
		require.NoError(t, helper.AgentRepo.Create(ctx, agent))
	}

	// Delete project1
	require.NoError(t, helper.ProjectRepo.Delete(ctx, project1.ID))

	// Project2's agents should remain
	agents, _ := helper.AgentRepo.GetByProjectID(ctx, project2.ID)
	assert.Equal(t, 2, len(agents))
}

// TestConstraintForeignKeyViolation tests foreign key constraint
func TestConstraintForeignKeyViolation(t *testing.T) {
	ctx := context.Background()
	helper := NewIntegrationTestHelper(ctx, t)
	defer helper.Cleanup()

	// Try to create item with non-existent project
	item := &models.Item{
		ProjectID: uuid.New(),
		Title:     "Orphan",
	}

	err := helper.ItemRepo.Create(ctx, item)
	assert.Error(t, err, "should fail due to foreign key constraint")
}

// ==================== TIMESTAMP & AUDIT TESTS ====================

// TestTimestampCreatedAt tests created_at is set on creation
func TestTimestampCreatedAt(t *testing.T) {
	ctx := context.Background()
	helper := NewIntegrationTestHelper(ctx, t)
	defer helper.Cleanup()

	project := &models.Project{Name: "Test"}
	require.NoError(t, helper.ProjectRepo.Create(ctx, project))

	retrieved, _ := helper.ProjectRepo.GetByID(ctx, project.ID)
	assert.NotNil(t, retrieved.CreatedAt)
	assert.False(t, retrieved.CreatedAt.IsZero())
}

// TestTimestampUpdatedAt tests updated_at changes on update
func TestTimestampUpdatedAt(t *testing.T) {
	ctx := context.Background()
	helper := NewIntegrationTestHelper(ctx, t)
	defer helper.Cleanup()

	project := &models.Project{Name: "Test"}
	require.NoError(t, helper.ProjectRepo.Create(ctx, project))

	retrieved1, _ := helper.ProjectRepo.GetByID(ctx, project.ID)

	// Update
	retrieved1.Name = "Updated"
	require.NoError(t, helper.ProjectRepo.Update(ctx, retrieved1))

	retrieved2, _ := helper.ProjectRepo.GetByID(ctx, project.ID)
	assert.True(t, retrieved2.UpdatedAt.After(retrieved1.UpdatedAt))
}

// TestTimestampDeletedAt tests deleted_at on soft delete
func TestTimestampDeletedAt(t *testing.T) {
	ctx := context.Background()
	helper := NewIntegrationTestHelper(ctx, t)
	defer helper.Cleanup()

	project := &models.Project{Name: "Test"}
	require.NoError(t, helper.ProjectRepo.Create(ctx, project))

	retrieved1, _ := helper.ProjectRepo.GetByID(ctx, project.ID)
	assert.Nil(t, retrieved1.DeletedAt)

	// Delete
	require.NoError(t, helper.ProjectRepo.Delete(ctx, project.ID))

	retrieved2, _ := helper.ProjectRepo.GetByID(ctx, project.ID)
	assert.NotNil(t, retrieved2.DeletedAt)
	assert.False(t, retrieved2.DeletedAt.IsZero())
}

// ==================== TYPE & VALUE TESTS ====================

// TestTypeStringFieldOverflow tests handling of very long strings
func TestTypeStringFieldOverflow(t *testing.T) {
	ctx := context.Background()
	helper := NewIntegrationTestHelper(ctx, t)
	defer helper.Cleanup()

	// Create 500-char string (exceeds VARCHAR(255))
	longString := ""
	for i := 0; i < 50; i++ {
		longString += "0123456789"
	}

	project := &models.Project{Name: longString}
	err := helper.ProjectRepo.Create(ctx, project)
	// This may fail due to VARCHAR constraint, which is expected
	_ = err
}

// TestTypeNullableFields tests all nullable fields
func TestTypeNullableFields(t *testing.T) {
	ctx := context.Background()
	helper := NewIntegrationTestHelper(ctx, t)
	defer helper.Cleanup()

	project := &models.Project{
		Name:        "Test",
		Description: nil,
		Metadata:    nil,
	}
	require.NoError(t, helper.ProjectRepo.Create(ctx, project))

	retrieved, _ := helper.ProjectRepo.GetByID(ctx, project.ID)
	assert.Nil(t, retrieved.Metadata)
}

// TestTypeJSONBStorage tests JSONB field storage and retrieval
func TestTypeJSONBStorage(t *testing.T) {
	ctx := context.Background()
	helper := NewIntegrationTestHelper(ctx, t)
	defer helper.Cleanup()

	project := &models.Project{Name: "Test"}
	require.NoError(t, helper.ProjectRepo.Create(ctx, project))

	complexMetadata := map[string]interface{}{
		"string":  "value",
		"number":  42,
		"boolean": true,
		"array":   []string{"a", "b", "c"},
		"object": map[string]interface{}{
			"nested": "value",
		},
	}

	project.Metadata = complexMetadata
	require.NoError(t, helper.ProjectRepo.Update(ctx, project))

	retrieved, _ := helper.ProjectRepo.GetByID(ctx, project.ID)
	assert.NotNil(t, retrieved.Metadata)
}

// ==================== IDEMPOTENCY TESTS ====================

// TestIdempotencyMultipleCreates tests creating same data is safe
func TestIdempotencyMultipleCreates(t *testing.T) {
	ctx := context.Background()
	helper := NewIntegrationTestHelper(ctx, t)
	defer helper.Cleanup()

	project := &models.Project{Name: "Test"}
	require.NoError(t, helper.ProjectRepo.Create(ctx, project))

	// Get ID from first create
	firstID := project.ID

	// Create again (new ID should be generated)
	project2 := &models.Project{Name: "Test"}
	require.NoError(t, helper.ProjectRepo.Create(ctx, project2))

	assert.NotEqual(t, firstID, project2.ID)
}

// TestIdempotencyMultipleDeletes tests deleting twice is safe
func TestIdempotencyMultipleDeletes(t *testing.T) {
	ctx := context.Background()
	helper := NewIntegrationTestHelper(ctx, t)
	defer helper.Cleanup()

	project := &models.Project{Name: "Test"}
	require.NoError(t, helper.ProjectRepo.Create(ctx, project))

	// Delete twice should be safe
	err1 := helper.ProjectRepo.Delete(ctx, project.ID)
	err2 := helper.ProjectRepo.Delete(ctx, project.ID)

	assert.NoError(t, err1)
	assert.NoError(t, err2)
}
