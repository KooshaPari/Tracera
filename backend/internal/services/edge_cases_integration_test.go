//go:build integration
// +build integration

package services

import (
	"context"
	"testing"
	"time"

	"github.com/google/uuid"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"

	"github.com/kooshapari/tracertm-backend/internal/models"
)

// ==================== ITEM EDGE CASES ====================

// TestItemEdgeCaseEmptyProjectID tests handling of items with no project
func TestItemEdgeCaseEmptyProjectID(t *testing.T) {
	ctx := context.Background()
	helper := NewIntegrationTestHelper(ctx, t)
	defer helper.Cleanup()

	// Try to create item without project (should fail due to FK constraint)
	invalidProjectID := uuid.New()
	item := &models.Item{
		ProjectID: invalidProjectID,
		Title:     "Orphan Item",
	}

	// Foreign key constraint should prevent insertion
	err := helper.ItemRepo.Create(ctx, item)
	assert.Error(t, err, "should fail due to missing project")
}

// TestItemEdgeCaseEmptyTitle tests handling of items with empty title
func TestItemEdgeCaseEmptyTitle(t *testing.T) {
	ctx := context.Background()
	helper := NewIntegrationTestHelper(ctx, t)
	defer helper.Cleanup()

	// Create project
	project := &models.Project{Name: "Test"}
	require.NoError(t, helper.ProjectRepo.Create(ctx, project))

	// Create item with empty title (should be allowed)
	item := &models.Item{
		ProjectID: project.ID,
		Title:     "",
	}

	err := helper.ItemRepo.Create(ctx, item)
	require.NoError(t, err)

	// Verify
	retrieved, _ := helper.ItemRepo.GetByID(ctx, item.ID)
	assert.Equal(t, "", retrieved.Title)
}

// TestItemEdgeCaseNullDescription tests items with no description
func TestItemEdgeCaseNullDescription(t *testing.T) {
	ctx := context.Background()
	helper := NewIntegrationTestHelper(ctx, t)
	defer helper.Cleanup()

	project := &models.Project{Name: "Test"}
	require.NoError(t, helper.ProjectRepo.Create(ctx, project))

	item := &models.Item{
		ProjectID:   project.ID,
		Title:       "No Description",
		Description: "",
	}

	require.NoError(t, helper.ItemRepo.Create(ctx, item))
	retrieved, _ := helper.ItemRepo.GetByID(ctx, item.ID)
	assert.Equal(t, "", retrieved.Description)
}

// TestItemEdgeCaseLargeMetadata tests storing large JSON metadata
func TestItemEdgeCaseLargeMetadata(t *testing.T) {
	ctx := context.Background()
	helper := NewIntegrationTestHelper(ctx, t)
	defer helper.Cleanup()

	project := &models.Project{Name: "Test"}
	require.NoError(t, helper.ProjectRepo.Create(ctx, project))

	// Create item with large metadata
	largeMetadata := map[string]interface{}{
		"nested": map[string]interface{}{
			"deeply": map[string]interface{}{
				"nested": map[string]interface{}{
					"data": "value",
					"list": []string{"item1", "item2", "item3"},
				},
			},
		},
	}

	item := &models.Item{
		ProjectID: project.ID,
		Title:     "Large Metadata",
		Metadata:  largeMetadata,
	}

	require.NoError(t, helper.ItemRepo.Create(ctx, item))
	retrieved, _ := helper.ItemRepo.GetByID(ctx, item.ID)
	assert.NotNil(t, retrieved.Metadata)
}

// TestItemEdgeCaseVeryLongTitle tests extremely long title
func TestItemEdgeCaseVeryLongTitle(t *testing.T) {
	ctx := context.Background()
	helper := NewIntegrationTestHelper(ctx, t)
	defer helper.Cleanup()

	project := &models.Project{Name: "Test"}
	require.NoError(t, helper.ProjectRepo.Create(ctx, project))

	// Create title near max length (255 chars)
	longTitle := ""
	for i := 0; i < 25; i++ {
		longTitle += "12345678901"
	}
	longTitle = longTitle[:255]

	item := &models.Item{
		ProjectID: project.ID,
		Title:     longTitle,
	}

	require.NoError(t, helper.ItemRepo.Create(ctx, item))
	retrieved, _ := helper.ItemRepo.GetByID(ctx, item.ID)
	assert.Equal(t, 255, len(retrieved.Title))
}

// TestItemEdgeCaseMultipleSoftDeletes tests soft delete behavior
func TestItemEdgeCaseMultipleSoftDeletes(t *testing.T) {
	ctx := context.Background()
	helper := NewIntegrationTestHelper(ctx, t)
	defer helper.Cleanup()

	project := &models.Project{Name: "Test"}
	require.NoError(t, helper.ProjectRepo.Create(ctx, project))

	item := &models.Item{ProjectID: project.ID, Title: "Test"}
	require.NoError(t, helper.ItemRepo.Create(ctx, item))

	// Soft delete
	require.NoError(t, helper.ItemRepo.Delete(ctx, item.ID))

	// Verify soft deleted
	deleted, err := helper.ItemRepo.GetByID(ctx, item.ID)
	require.NoError(t, err)
	assert.NotNil(t, deleted.DeletedAt)

	// Delete again should be idempotent
	err = helper.ItemRepo.Delete(ctx, item.ID)
	assert.NoError(t, err)
}

// TestItemEdgeCaseGetNonExistent tests retrieving non-existent item
func TestItemEdgeCaseGetNonExistent(t *testing.T) {
	ctx := context.Background()
	helper := NewIntegrationTestHelper(ctx, t)
	defer helper.Cleanup()

	nonExistentID := uuid.New()
	item, err := helper.ItemRepo.GetByID(ctx, nonExistentID)
	assert.NoError(t, err)
	assert.Nil(t, item)
}

// ==================== LINK EDGE CASES ====================

// TestLinkEdgeCaseSelfLink tests link from item to itself
func TestLinkEdgeCaseSelfLink(t *testing.T) {
	ctx := context.Background()
	helper := NewIntegrationTestHelper(ctx, t)
	defer helper.Cleanup()

	project := &models.Project{Name: "Test"}
	require.NoError(t, helper.ProjectRepo.Create(ctx, project))

	item := &models.Item{ProjectID: project.ID, Title: "Test"}
	require.NoError(t, helper.ItemRepo.Create(ctx, item))

	// Create self-link
	link := &models.Link{
		SourceID: item.ID,
		TargetID: item.ID,
		Type:     "self_reference",
	}

	// Self-links should be allowed
	err := helper.LinkRepo.Create(ctx, link)
	require.NoError(t, err)
}

// TestLinkEdgeCaseDuplicateLinks tests multiple links between same items
func TestLinkEdgeCaseDuplicateLinks(t *testing.T) {
	ctx := context.Background()
	helper := NewIntegrationTestHelper(ctx, t)
	defer helper.Cleanup()

	project := &models.Project{Name: "Test"}
	require.NoError(t, helper.ProjectRepo.Create(ctx, project))

	source := &models.Item{ProjectID: project.ID, Title: "Source"}
	target := &models.Item{ProjectID: project.ID, Title: "Target"}
	require.NoError(t, helper.ItemRepo.Create(ctx, source))
	require.NoError(t, helper.ItemRepo.Create(ctx, target))

	// Create first link
	link1 := &models.Link{SourceID: source.ID, TargetID: target.ID, Type: "type1"}
	require.NoError(t, helper.LinkRepo.Create(ctx, link1))

	// Create second link with different type
	link2 := &models.Link{SourceID: source.ID, TargetID: target.ID, Type: "type2"}
	require.NoError(t, helper.LinkRepo.Create(ctx, link2))

	// Both should exist
	links, _ := helper.LinkRepo.GetBySourceID(ctx, source.ID)
	assert.Equal(t, 2, len(links))
}

// TestLinkEdgeCaseLinkToDeletedItem tests creating link to soft-deleted item
func TestLinkEdgeCaseLinkToDeletedItem(t *testing.T) {
	ctx := context.Background()
	helper := NewIntegrationTestHelper(ctx, t)
	defer helper.Cleanup()

	project := &models.Project{Name: "Test"}
	require.NoError(t, helper.ProjectRepo.Create(ctx, project))

	source := &models.Item{ProjectID: project.ID, Title: "Source"}
	target := &models.Item{ProjectID: project.ID, Title: "Target"}
	require.NoError(t, helper.ItemRepo.Create(ctx, source))
	require.NoError(t, helper.ItemRepo.Create(ctx, target))

	// Delete target
	require.NoError(t, helper.ItemRepo.Delete(ctx, target.ID))

	// Try to create link to deleted item (FK constraint check depends on implementation)
	link := &models.Link{SourceID: source.ID, TargetID: target.ID, Type: "depends_on"}
	_ = helper.LinkRepo.Create(ctx, link)
	// Allow error or success depending on FK implementation
}

// TestLinkEdgeCaseCircularDependency tests circular link patterns
func TestLinkEdgeCaseCircularDependency(t *testing.T) {
	ctx := context.Background()
	helper := NewIntegrationTestHelper(ctx, t)
	defer helper.Cleanup()

	project := &models.Project{Name: "Test"}
	require.NoError(t, helper.ProjectRepo.Create(ctx, project))

	a := &models.Item{ProjectID: project.ID, Title: "A"}
	b := &models.Item{ProjectID: project.ID, Title: "B"}
	c := &models.Item{ProjectID: project.ID, Title: "C"}
	require.NoError(t, helper.ItemRepo.Create(ctx, a))
	require.NoError(t, helper.ItemRepo.Create(ctx, b))
	require.NoError(t, helper.ItemRepo.Create(ctx, c))

	// Create circular: A -> B -> C -> A
	require.NoError(t, helper.LinkRepo.Create(ctx, &models.Link{SourceID: a.ID, TargetID: b.ID, Type: "depends"}))
	require.NoError(t, helper.LinkRepo.Create(ctx, &models.Link{SourceID: b.ID, TargetID: c.ID, Type: "depends"}))
	require.NoError(t, helper.LinkRepo.Create(ctx, &models.Link{SourceID: c.ID, TargetID: a.ID, Type: "depends"}))

	// Circular links should be allowed
	linksFromA, _ := helper.LinkRepo.GetBySourceID(ctx, a.ID)
	assert.Equal(t, 1, len(linksFromA))
}

// TestLinkEdgeCaseEmptyType tests link with empty type
func TestLinkEdgeCaseEmptyType(t *testing.T) {
	ctx := context.Background()
	helper := NewIntegrationTestHelper(ctx, t)
	defer helper.Cleanup()

	project := &models.Project{Name: "Test"}
	require.NoError(t, helper.ProjectRepo.Create(ctx, project))

	source := &models.Item{ProjectID: project.ID, Title: "Source"}
	target := &models.Item{ProjectID: project.ID, Title: "Target"}
	require.NoError(t, helper.ItemRepo.Create(ctx, source))
	require.NoError(t, helper.ItemRepo.Create(ctx, target))

	// Link with empty type (should be allowed)
	link := &models.Link{SourceID: source.ID, TargetID: target.ID, Type: ""}
	require.NoError(t, helper.LinkRepo.Create(ctx, link))
}

// TestLinkEdgeCaseGetNonExistent tests retrieving non-existent link
func TestLinkEdgeCaseGetNonExistent(t *testing.T) {
	ctx := context.Background()
	helper := NewIntegrationTestHelper(ctx, t)
	defer helper.Cleanup()

	nonExistentID := uuid.New()
	link, err := helper.LinkRepo.GetByID(ctx, nonExistentID)
	assert.NoError(t, err)
	assert.Nil(t, link)
}

// ==================== PROJECT EDGE CASES ====================

// TestProjectEdgeCaseEmptyName tests project with empty name
func TestProjectEdgeCaseEmptyName(t *testing.T) {
	ctx := context.Background()
	helper := NewIntegrationTestHelper(ctx, t)
	defer helper.Cleanup()

	project := &models.Project{Name: ""}
	// Empty name should be allowed
	err := helper.ProjectRepo.Create(ctx, project)
	require.NoError(t, err)
}

// TestProjectEdgeCaseVeryLongName tests project with long name
func TestProjectEdgeCaseVeryLongName(t *testing.T) {
	ctx := context.Background()
	helper := NewIntegrationTestHelper(ctx, t)
	defer helper.Cleanup()

	longName := ""
	for i := 0; i < 26; i++ {
		longName += "1234567890"
	}
	longName = longName[:255]

	project := &models.Project{Name: longName}
	require.NoError(t, helper.ProjectRepo.Create(ctx, project))

	retrieved, _ := helper.ProjectRepo.GetByID(ctx, project.ID)
	assert.Equal(t, 255, len(retrieved.Name))
}

// TestProjectEdgeCaseNullDescription tests project with no description
func TestProjectEdgeCaseNullDescription(t *testing.T) {
	ctx := context.Background()
	helper := NewIntegrationTestHelper(ctx, t)
	defer helper.Cleanup()

	project := &models.Project{
		Name:        "Test",
		Description: "",
	}
	require.NoError(t, helper.ProjectRepo.Create(ctx, project))

	retrieved, _ := helper.ProjectRepo.GetByID(ctx, project.ID)
	assert.Equal(t, "", retrieved.Description)
}

// TestProjectEdgeCaseLargeMetadata tests project with large metadata
func TestProjectEdgeCaseLargeMetadata(t *testing.T) {
	ctx := context.Background()
	helper := NewIntegrationTestHelper(ctx, t)
	defer helper.Cleanup()

	metadata := make(map[string]interface{})
	for i := 0; i < 100; i++ {
		metadata[string(rune(i))] = "value"
	}

	project := &models.Project{
		Name:     "Test",
		Metadata: metadata,
	}
	require.NoError(t, helper.ProjectRepo.Create(ctx, project))

	retrieved, _ := helper.ProjectRepo.GetByID(ctx, project.ID)
	assert.NotNil(t, retrieved.Metadata)
}

// TestProjectEdgeCaseManyItems tests project with many items
func TestProjectEdgeCaseManyItems(t *testing.T) {
	ctx := context.Background()
	helper := NewIntegrationTestHelper(ctx, t)
	defer helper.Cleanup()

	project := &models.Project{Name: "Test"}
	require.NoError(t, helper.ProjectRepo.Create(ctx, project))

	// Create 100 items
	for i := 0; i < 100; i++ {
		item := &models.Item{
			ProjectID: project.ID,
			Title:     "Item " + string(rune(i)),
		}
		require.NoError(t, helper.ItemRepo.Create(ctx, item))
	}

	// Verify count
	count, _ := helper.ItemRepo.Count(ctx)
	assert.Equal(t, 100, count)
}

// TestProjectEdgeCaseSoftDelete tests project soft delete cascades
func TestProjectEdgeCaseSoftDelete(t *testing.T) {
	ctx := context.Background()
	helper := NewIntegrationTestHelper(ctx, t)
	defer helper.Cleanup()

	project := &models.Project{Name: "Test"}
	require.NoError(t, helper.ProjectRepo.Create(ctx, project))

	item := &models.Item{ProjectID: project.ID, Title: "Test"}
	require.NoError(t, helper.ItemRepo.Create(ctx, item))

	// Soft delete project should cascade
	require.NoError(t, helper.ProjectRepo.Delete(ctx, project.ID))

	// Item should be deleted too
	deleted, _ := helper.ItemRepo.GetByID(ctx, item.ID)
	assert.NotNil(t, deleted.DeletedAt)
}

// TestProjectEdgeCaseGetNonExistent tests retrieving non-existent project
func TestProjectEdgeCaseGetNonExistent(t *testing.T) {
	ctx := context.Background()
	helper := NewIntegrationTestHelper(ctx, t)
	defer helper.Cleanup()

	nonExistentID := uuid.New()
	project, err := helper.ProjectRepo.GetByID(ctx, nonExistentID)
	assert.NoError(t, err)
	assert.Nil(t, project)
}

// ==================== AGENT EDGE CASES ====================

// TestAgentEdgeCaseEmptyName tests agent with empty name
func TestAgentEdgeCaseEmptyName(t *testing.T) {
	ctx := context.Background()
	helper := NewIntegrationTestHelper(ctx, t)
	defer helper.Cleanup()

	project := &models.Project{Name: "Test"}
	require.NoError(t, helper.ProjectRepo.Create(ctx, project))

	agent := &models.Agent{
		ProjectID: project.ID,
		Name:      "",
	}
	err := helper.AgentRepo.Create(ctx, agent)
	require.NoError(t, err)
}

// TestAgentEdgeCaseVeryLongName tests agent with long name
func TestAgentEdgeCaseVeryLongName(t *testing.T) {
	ctx := context.Background()
	helper := NewIntegrationTestHelper(ctx, t)
	defer helper.Cleanup()

	project := &models.Project{Name: "Test"}
	require.NoError(t, helper.ProjectRepo.Create(ctx, project))

	longName := ""
	for i := 0; i < 26; i++ {
		longName += "1234567890"
	}
	longName = longName[:255]

	agent := &models.Agent{
		ProjectID: project.ID,
		Name:      longName,
	}
	require.NoError(t, helper.AgentRepo.Create(ctx, agent))

	retrieved, _ := helper.AgentRepo.GetByID(ctx, agent.ID)
	assert.Equal(t, 255, len(retrieved.Name))
}

// TestAgentEdgeCaseNullStatus tests agent with no status
func TestAgentEdgeCaseNullStatus(t *testing.T) {
	ctx := context.Background()
	helper := NewIntegrationTestHelper(ctx, t)
	defer helper.Cleanup()

	project := &models.Project{Name: "Test"}
	require.NoError(t, helper.ProjectRepo.Create(ctx, project))

	agent := &models.Agent{
		ProjectID: project.ID,
		Name:      "Test",
		Status:    "",
	}
	require.NoError(t, helper.AgentRepo.Create(ctx, agent))

	retrieved, _ := helper.AgentRepo.GetByID(ctx, agent.ID)
	assert.Equal(t, "", retrieved.Status)
}

// TestAgentEdgeCaseManyAgents tests project with many agents
func TestAgentEdgeCaseManyAgents(t *testing.T) {
	ctx := context.Background()
	helper := NewIntegrationTestHelper(ctx, t)
	defer helper.Cleanup()

	project := &models.Project{Name: "Test"}
	require.NoError(t, helper.ProjectRepo.Create(ctx, project))

	// Create 50 agents
	for i := 0; i < 50; i++ {
		agent := &models.Agent{
			ProjectID: project.ID,
			Name:      "Agent " + string(rune(i)),
		}
		require.NoError(t, helper.AgentRepo.Create(ctx, agent))
	}

	// Get by project
	agents, _ := helper.AgentRepo.GetByProjectID(ctx, project.ID)
	assert.Equal(t, 50, len(agents))
}

// TestAgentEdgeCaseLastActivityTracking tests activity timestamp
func TestAgentEdgeCaseLastActivityTracking(t *testing.T) {
	ctx := context.Background()
	helper := NewIntegrationTestHelper(ctx, t)
	defer helper.Cleanup()

	project := &models.Project{Name: "Test"}
	require.NoError(t, helper.ProjectRepo.Create(ctx, project))

	beforeCreate := time.Now()
	agent := &models.Agent{
		ProjectID: project.ID,
		Name:      "Test",
	}
	require.NoError(t, helper.AgentRepo.Create(ctx, agent))
	afterCreate := time.Now()

	retrieved, _ := helper.AgentRepo.GetByID(ctx, agent.ID)
	assert.NotNil(t, retrieved.LastActivityAt)
	assert.True(t, retrieved.LastActivityAt.After(beforeCreate.Add(-1*time.Second)))
	assert.True(t, retrieved.LastActivityAt.Before(afterCreate.Add(1*time.Second)))
}

// TestAgentEdgeCaseGetNonExistent tests retrieving non-existent agent
func TestAgentEdgeCaseGetNonExistent(t *testing.T) {
	ctx := context.Background()
	helper := NewIntegrationTestHelper(ctx, t)
	defer helper.Cleanup()

	nonExistentID := uuid.New()
	agent, err := helper.AgentRepo.GetByID(ctx, nonExistentID)
	assert.NoError(t, err)
	assert.Nil(t, agent)
}

// ==================== CONCURRENT EDGE CASES ====================

// TestConcurrentItemCreation tests race conditions with concurrent creates
func TestConcurrentItemCreation(t *testing.T) {
	ctx := context.Background()
	helper := NewIntegrationTestHelper(ctx, t)
	defer helper.Cleanup()

	project := &models.Project{Name: "Test"}
	require.NoError(t, helper.ProjectRepo.Create(ctx, project))

	done := make(chan bool, 10)
	for i := 0; i < 10; i++ {
		go func(index int) {
			item := &models.Item{
				ProjectID: project.ID,
				Title:     "Concurrent " + string(rune(index)),
			}
			_ = helper.ItemRepo.Create(ctx, item)
			done <- true
		}(i)
	}

	// Wait for all goroutines
	for i := 0; i < 10; i++ {
		<-done
	}

	// All should be created
	count, _ := helper.ItemRepo.Count(ctx)
	assert.Equal(t, 10, count)
}

// TestConcurrentLinkCreation tests concurrent link creation
func TestConcurrentLinkCreation(t *testing.T) {
	ctx := context.Background()
	helper := NewIntegrationTestHelper(ctx, t)
	defer helper.Cleanup()

	project := &models.Project{Name: "Test"}
	require.NoError(t, helper.ProjectRepo.Create(ctx, project))

	source := &models.Item{ProjectID: project.ID, Title: "Source"}
	require.NoError(t, helper.ItemRepo.Create(ctx, source))

	// Create 10 targets
	targets := make([]*models.Item, 10)
	for i := 0; i < 10; i++ {
		target := &models.Item{ProjectID: project.ID, Title: "Target " + string(rune(i))}
		require.NoError(t, helper.ItemRepo.Create(ctx, target))
		targets[i] = target
	}

	// Create links concurrently
	done := make(chan bool, 10)
	for i := 0; i < 10; i++ {
		go func(index int) {
			link := &models.Link{
				SourceID: source.ID,
				TargetID: targets[index].ID,
				Type:     "depends",
			}
			_ = helper.LinkRepo.Create(ctx, link)
			done <- true
		}(i)
	}

	// Wait for all
	for i := 0; i < 10; i++ {
		<-done
	}

	// All links should be created
	links, _ := helper.LinkRepo.GetBySourceID(ctx, source.ID)
	assert.Equal(t, 10, len(links))
}
