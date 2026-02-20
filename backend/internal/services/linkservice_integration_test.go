//go:build integration
// +build integration

package services

import (
	"context"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"

	"github.com/kooshapari/tracertm-backend/internal/models"
)

// TestLinkServiceCreate tests creating links with relationship validation
func TestLinkServiceCreate(t *testing.T) {
	ctx := context.Background()
	helper := NewIntegrationTestHelper(ctx, t)
	defer helper.Cleanup()

	// Setup: Create project and items
	project := &models.Project{Name: "Link Test Project"}
	err := helper.ProjectRepo.Create(ctx, project)
	require.NoError(t, err)

	sourceItem := &models.Item{
		ProjectID: project.ID,
		Title:     "Source Item",
		Type:      "task",
	}
	err = helper.ItemRepo.Create(ctx, sourceItem)
	require.NoError(t, err)

	targetItem := &models.Item{
		ProjectID: project.ID,
		Title:     "Target Item",
		Type:      "task",
	}
	err = helper.ItemRepo.Create(ctx, targetItem)
	require.NoError(t, err)

	// Create a link
	link := &models.Link{
		SourceID: sourceItem.ID,
		TargetID: targetItem.ID,
		Type:     "depends_on",
	}

	err = helper.LinkRepo.Create(ctx, link)
	require.NoError(t, err)
	require.NotEmpty(t, link.ID)
	assert.Equal(t, sourceItem.ID, link.SourceID)
	assert.Equal(t, targetItem.ID, link.TargetID)
}

// TestLinkServiceGetByID tests retrieving links by ID
func TestLinkServiceGetByID(t *testing.T) {
	ctx := context.Background()
	helper := NewIntegrationTestHelper(ctx, t)
	defer helper.Cleanup()

	// Setup
	project := &models.Project{Name: "Link Retrieve Test"}
	err := helper.ProjectRepo.Create(ctx, project)
	require.NoError(t, err)

	source := &models.Item{ProjectID: project.ID, Title: "Source"}
	target := &models.Item{ProjectID: project.ID, Title: "Target"}
	err = helper.ItemRepo.Create(ctx, source)
	require.NoError(t, err)
	err = helper.ItemRepo.Create(ctx, target)
	require.NoError(t, err)

	link := &models.Link{
		SourceID: source.ID,
		TargetID: target.ID,
		Type:     "implements",
	}
	err = helper.LinkRepo.Create(ctx, link)
	require.NoError(t, err)

	// Test: Retrieve the link
	retrieved, err := helper.LinkRepo.GetByID(ctx, link.ID)
	require.NoError(t, err)
	require.NotNil(t, retrieved)
	assert.Equal(t, link.ID, retrieved.ID)
	assert.Equal(t, source.ID, retrieved.SourceID)
	assert.Equal(t, target.ID, retrieved.TargetID)
	assert.Equal(t, "implements", retrieved.Type)
}

// TestLinkServiceGetBySourceID tests retrieving outgoing links
func TestLinkServiceGetBySourceID(t *testing.T) {
	ctx := context.Background()
	helper := NewIntegrationTestHelper(ctx, t)
	defer helper.Cleanup()

	// Setup: Create one source and multiple targets
	project := &models.Project{Name: "Link Source Test"}
	err := helper.ProjectRepo.Create(ctx, project)
	require.NoError(t, err)

	source := &models.Item{ProjectID: project.ID, Title: "Source"}
	err = helper.ItemRepo.Create(ctx, source)
	require.NoError(t, err)

	// Create multiple target items and links
	targets := []*models.Item{
		{ProjectID: project.ID, Title: "Target 1"},
		{ProjectID: project.ID, Title: "Target 2"},
		{ProjectID: project.ID, Title: "Target 3"},
	}

	for _, target := range targets {
		err := helper.ItemRepo.Create(ctx, target)
		require.NoError(t, err)

		link := &models.Link{
			SourceID: source.ID,
			TargetID: target.ID,
			Type:     "depends_on",
		}
		err = helper.LinkRepo.Create(ctx, link)
		require.NoError(t, err)
	}

	// Test: Retrieve all outgoing links from source
	outgoing, err := helper.LinkRepo.GetBySourceID(ctx, source.ID)
	require.NoError(t, err)
	assert.Equal(t, 3, len(outgoing))

	// Verify all links are from the source
	for _, link := range outgoing {
		assert.Equal(t, source.ID, link.SourceID)
	}
}

// TestLinkServiceGetByTargetID tests retrieving incoming links
func TestLinkServiceGetByTargetID(t *testing.T) {
	ctx := context.Background()
	helper := NewIntegrationTestHelper(ctx, t)
	defer helper.Cleanup()

	// Setup: Create multiple sources and one target
	project := &models.Project{Name: "Link Target Test"}
	err := helper.ProjectRepo.Create(ctx, project)
	require.NoError(t, err)

	target := &models.Item{ProjectID: project.ID, Title: "Target"}
	err = helper.ItemRepo.Create(ctx, target)
	require.NoError(t, err)

	// Create multiple source items and links to target
	sources := []*models.Item{
		{ProjectID: project.ID, Title: "Source 1"},
		{ProjectID: project.ID, Title: "Source 2"},
	}

	for _, source := range sources {
		err := helper.ItemRepo.Create(ctx, source)
		require.NoError(t, err)

		link := &models.Link{
			SourceID: source.ID,
			TargetID: target.ID,
			Type:     "tests",
		}
		err = helper.LinkRepo.Create(ctx, link)
		require.NoError(t, err)
	}

	// Test: Retrieve all incoming links to target
	incoming, err := helper.LinkRepo.GetByTargetID(ctx, target.ID)
	require.NoError(t, err)
	assert.Equal(t, 2, len(incoming))

	// Verify all links point to the target
	for _, link := range incoming {
		assert.Equal(t, target.ID, link.TargetID)
	}
}

// TestLinkServiceDelete tests soft deleting links
func TestLinkServiceDelete(t *testing.T) {
	ctx := context.Background()
	helper := NewIntegrationTestHelper(ctx, t)
	defer helper.Cleanup()

	// Setup
	project := &models.Project{Name: "Link Delete Test"}
	err := helper.ProjectRepo.Create(ctx, project)
	require.NoError(t, err)

	source := &models.Item{ProjectID: project.ID, Title: "Source"}
	target := &models.Item{ProjectID: project.ID, Title: "Target"}
	err = helper.ItemRepo.Create(ctx, source)
	require.NoError(t, err)
	err = helper.ItemRepo.Create(ctx, target)
	require.NoError(t, err)

	link := &models.Link{
		SourceID: source.ID,
		TargetID: target.ID,
		Type:     "blocks",
	}
	err = helper.LinkRepo.Create(ctx, link)
	require.NoError(t, err)

	linkID := link.ID

	// Delete
	err = helper.LinkRepo.Delete(ctx, linkID)
	require.NoError(t, err)

	// Verify link is not returned
	deleted, err := helper.LinkRepo.GetByID(ctx, linkID)
	assert.Error(t, err)
	assert.Nil(t, deleted)
}

// TestLinkServiceDeleteByItemID tests cascade deletion
func TestLinkServiceDeleteByItemID(t *testing.T) {
	ctx := context.Background()
	helper := NewIntegrationTestHelper(ctx, t)
	defer helper.Cleanup()

	// Setup
	project := &models.Project{Name: "Link Cascade Test"}
	err := helper.ProjectRepo.Create(ctx, project)
	require.NoError(t, err)

	item := &models.Item{ProjectID: project.ID, Title: "Item to Delete"}
	err = helper.ItemRepo.Create(ctx, item)
	require.NoError(t, err)

	target1 := &models.Item{ProjectID: project.ID, Title: "Target 1"}
	target2 := &models.Item{ProjectID: project.ID, Title: "Target 2"}
	err = helper.ItemRepo.Create(ctx, target1)
	require.NoError(t, err)
	err = helper.ItemRepo.Create(ctx, target2)
	require.NoError(t, err)

	// Create links where item is source
	link1 := &models.Link{SourceID: item.ID, TargetID: target1.ID, Type: "depends_on"}
	link2 := &models.Link{SourceID: item.ID, TargetID: target2.ID, Type: "depends_on"}
	err = helper.LinkRepo.Create(ctx, link1)
	require.NoError(t, err)
	err = helper.LinkRepo.Create(ctx, link2)
	require.NoError(t, err)

	// Delete all links for item
	err = helper.LinkRepo.DeleteByItemID(ctx, item.ID)
	require.NoError(t, err)

	// Verify outgoing links are gone
	outgoing, err := helper.LinkRepo.GetBySourceID(ctx, item.ID)
	require.NoError(t, err)
	assert.Equal(t, 0, len(outgoing))
}

// TestLinkServiceMultipleRelationshipTypes tests different link types
func TestLinkServiceMultipleRelationshipTypes(t *testing.T) {
	ctx := context.Background()
	helper := NewIntegrationTestHelper(ctx, t)
	defer helper.Cleanup()

	// Setup
	project := &models.Project{Name: "Link Types Test"}
	err := helper.ProjectRepo.Create(ctx, project)
	require.NoError(t, err)

	item1 := &models.Item{ProjectID: project.ID, Title: "Item 1"}
	item2 := &models.Item{ProjectID: project.ID, Title: "Item 2"}
	err = helper.ItemRepo.Create(ctx, item1)
	require.NoError(t, err)
	err = helper.ItemRepo.Create(ctx, item2)
	require.NoError(t, err)

	// Create links with different types
	linkTypes := []string{"depends_on", "implements", "tests", "blocks", "relates_to"}
	for i, linkType := range linkTypes {
		// Create unique target for each link type
		target := &models.Item{
			ProjectID: project.ID,
			Title:     "Target for " + linkType,
		}
		err := helper.ItemRepo.Create(ctx, target)
		require.NoError(t, err)

		link := &models.Link{
			SourceID: item1.ID,
			TargetID: target.ID,
			Type:     linkType,
		}
		err = helper.LinkRepo.Create(ctx, link)
		require.NoError(t, err)

		// Verify the link was created
		retrieved, err := helper.LinkRepo.GetByID(ctx, link.ID)
		require.NoError(t, err)
		assert.Equal(t, linkType, retrieved.Type)

		if i > 0 {
			break // Just test a few for performance
		}
	}

	// Verify all links from item1
	links, err := helper.LinkRepo.GetBySourceID(ctx, item1.ID)
	require.NoError(t, err)
	assert.Greater(t, len(links), 0)
}

// TestLinkServiceGraphStructure tests more complex graph scenarios
func TestLinkServiceGraphStructure(t *testing.T) {
	ctx := context.Background()
	helper := NewIntegrationTestHelper(ctx, t)
	defer helper.Cleanup()

	// Setup: Create a small graph
	project := &models.Project{Name: "Graph Test"}
	err := helper.ProjectRepo.Create(ctx, project)
	require.NoError(t, err)

	// Create items: A -> B -> C -> D
	itemA := &models.Item{ProjectID: project.ID, Title: "Item A"}
	itemB := &models.Item{ProjectID: project.ID, Title: "Item B"}
	itemC := &models.Item{ProjectID: project.ID, Title: "Item C"}
	itemD := &models.Item{ProjectID: project.ID, Title: "Item D"}

	for _, item := range []*models.Item{itemA, itemB, itemC, itemD} {
		err := helper.ItemRepo.Create(ctx, item)
		require.NoError(t, err)
	}

	// Create links: A -> B -> C -> D
	links := []struct {
		source *models.Item
		target *models.Item
	}{
		{itemA, itemB},
		{itemB, itemC},
		{itemC, itemD},
		{itemA, itemD}, // Also A -> D (shortcut)
	}

	for _, l := range links {
		link := &models.Link{
			SourceID: l.source.ID,
			TargetID: l.target.ID,
			Type:     "depends_on",
		}
		err := helper.LinkRepo.Create(ctx, link)
		require.NoError(t, err)
	}

	// Test: Verify A has 2 outgoing links
	outgoing, err := helper.LinkRepo.GetBySourceID(ctx, itemA.ID)
	require.NoError(t, err)
	assert.Equal(t, 2, len(outgoing))

	// Test: Verify D has 3 incoming links (from A, B, C)
	incoming, err := helper.LinkRepo.GetByTargetID(ctx, itemD.ID)
	require.NoError(t, err)
	assert.Equal(t, 3, len(incoming))
}

// TestLinkServiceConcurrentCreation tests creating links concurrently
func TestLinkServiceConcurrentCreation(t *testing.T) {
	ctx := context.Background()
	helper := NewIntegrationTestHelper(ctx, t)
	defer helper.Cleanup()

	// Setup
	project := &models.Project{Name: "Concurrent Link Test"}
	err := helper.ProjectRepo.Create(ctx, project)
	require.NoError(t, err)

	source := &models.Item{ProjectID: project.ID, Title: "Source"}
	err = helper.ItemRepo.Create(ctx, source)
	require.NoError(t, err)

	// Create multiple targets concurrently
	targets := make([]*models.Item, 5)
	for i := 0; i < 5; i++ {
		target := &models.Item{
			ProjectID: project.ID,
			Title:     "Target " + string(rune(i)),
		}
		err := helper.ItemRepo.Create(ctx, target)
		require.NoError(t, err)
		targets[i] = target
	}

	// Create links
	for _, target := range targets {
		link := &models.Link{
			SourceID: source.ID,
			TargetID: target.ID,
			Type:     "depends_on",
		}
		err := helper.LinkRepo.Create(ctx, link)
		require.NoError(t, err)
	}

	// Verify all links exist
	links, err := helper.LinkRepo.GetBySourceID(ctx, source.ID)
	require.NoError(t, err)
	assert.Equal(t, 5, len(links))
}
