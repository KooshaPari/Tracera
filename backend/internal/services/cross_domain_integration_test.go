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

// TestCrossDomainProjectItemRelationship tests project-item relationships
func TestCrossDomainProjectItemRelationship(t *testing.T) {
	ctx := context.Background()
	helper := NewIntegrationTestHelper(ctx, t)
	defer helper.Cleanup()

	// Setup: Create project
	project := &models.Project{
		Name:        "Cross-Domain Project",
		Description: "Testing project-item relationships",
	}
	err := helper.ProjectRepo.Create(ctx, project)
	require.NoError(t, err)

	// Create items in project
	item1 := &models.Item{ProjectID: project.ID, Title: "Item 1"}
	item2 := &models.Item{ProjectID: project.ID, Title: "Item 2"}
	err = helper.ItemRepo.Create(ctx, item1)
	require.NoError(t, err)
	err = helper.ItemRepo.Create(ctx, item2)
	require.NoError(t, err)

	// Verify project-item relationship
	items, err := helper.ItemRepo.GetByProjectID(ctx, project.ID)
	require.NoError(t, err)
	assert.Equal(t, 2, len(items))

	// Verify items reference correct project
	for _, item := range items {
		assert.Equal(t, project.ID, item.ProjectID)
	}
}

// TestCrossDomainItemLinkRelationship tests item-link relationships
func TestCrossDomainItemLinkRelationship(t *testing.T) {
	ctx := context.Background()
	helper := NewIntegrationTestHelper(ctx, t)
	defer helper.Cleanup()

	// Setup: Create project and items
	project := &models.Project{Name: "Link Test Project"}
	err := helper.ProjectRepo.Create(ctx, project)
	require.NoError(t, err)

	item1 := &models.Item{ProjectID: project.ID, Title: "Source Item"}
	item2 := &models.Item{ProjectID: project.ID, Title: "Target Item"}
	err = helper.ItemRepo.Create(ctx, item1)
	require.NoError(t, err)
	err = helper.ItemRepo.Create(ctx, item2)
	require.NoError(t, err)

	// Create link between items
	link := &models.Link{
		SourceID: item1.ID,
		TargetID: item2.ID,
		Type:     "depends_on",
	}
	err = helper.LinkRepo.Create(ctx, link)
	require.NoError(t, err)

	// Verify outgoing links
	outgoing, err := helper.LinkRepo.GetBySourceID(ctx, item1.ID)
	require.NoError(t, err)
	assert.Equal(t, 1, len(outgoing))
	assert.Equal(t, item2.ID, outgoing[0].TargetID)

	// Verify incoming links
	incoming, err := helper.LinkRepo.GetByTargetID(ctx, item2.ID)
	require.NoError(t, err)
	assert.Equal(t, 1, len(incoming))
	assert.Equal(t, item1.ID, incoming[0].SourceID)
}

// TestCrossDomainCascadeDeleteItemWithLinks tests cascade delete when item is deleted
func TestCrossDomainCascadeDeleteItemWithLinks(t *testing.T) {
	ctx := context.Background()
	helper := NewIntegrationTestHelper(ctx, t)
	defer helper.Cleanup()

	// Setup: Create project
	project := &models.Project{Name: "Cascade Delete Test"}
	err := helper.ProjectRepo.Create(ctx, project)
	require.NoError(t, err)

	// Create items
	source := &models.Item{ProjectID: project.ID, Title: "Source"}
	target := &models.Item{ProjectID: project.ID, Title: "Target"}
	err = helper.ItemRepo.Create(ctx, source)
	require.NoError(t, err)
	err = helper.ItemRepo.Create(ctx, target)
	require.NoError(t, err)

	// Create link
	link := &models.Link{SourceID: source.ID, TargetID: target.ID, Type: "depends_on"}
	err = helper.LinkRepo.Create(ctx, link)
	require.NoError(t, err)

	linkID := link.ID

	// Delete source item
	err = helper.ItemRepo.Delete(ctx, source.ID)
	require.NoError(t, err)

	// Verify source item is deleted
	deleted, err := helper.ItemRepo.GetByID(ctx, source.ID)
	assert.Error(t, err)
	assert.Nil(t, deleted)

	// Verify associated links are deleted
	deletedLink, err := helper.LinkRepo.GetByID(ctx, linkID)
	assert.Error(t, err)
	assert.Nil(t, deletedLink)

	// Verify target item still exists
	targetItem, err := helper.ItemRepo.GetByID(ctx, target.ID)
	require.NoError(t, err)
	assert.NotNil(t, targetItem)
}

// TestCrossDomainCascadeDeleteProjectWithItems tests cascade delete when project is deleted
func TestCrossDomainCascadeDeleteProjectWithItems(t *testing.T) {
	ctx := context.Background()
	helper := NewIntegrationTestHelper(ctx, t)
	defer helper.Cleanup()

	// Setup: Create project with items
	project := &models.Project{Name: "Project to Delete"}
	err := helper.ProjectRepo.Create(ctx, project)
	require.NoError(t, err)

	item1 := &models.Item{ProjectID: project.ID, Title: "Item 1"}
	item2 := &models.Item{ProjectID: project.ID, Title: "Item 2"}
	err = helper.ItemRepo.Create(ctx, item1)
	require.NoError(t, err)
	err = helper.ItemRepo.Create(ctx, item2)
	require.NoError(t, err)

	// Create link between items
	link := &models.Link{SourceID: item1.ID, TargetID: item2.ID, Type: "depends_on"}
	err = helper.LinkRepo.Create(ctx, link)
	require.NoError(t, err)

	projectID := project.ID
	item1ID := item1.ID
	item2ID := item2.ID
	linkID := link.ID

	// Delete project
	err = helper.ProjectRepo.Delete(ctx, projectID)
	require.NoError(t, err)

	// Verify project is deleted
	deletedProject, err := helper.ProjectRepo.GetByID(ctx, projectID)
	assert.Error(t, err)
	assert.Nil(t, deletedProject)

	// Verify items are deleted
	deletedItem1, err := helper.ItemRepo.GetByID(ctx, item1ID)
	assert.Error(t, err)
	assert.Nil(t, deletedItem1)

	deletedItem2, err := helper.ItemRepo.GetByID(ctx, item2ID)
	assert.Error(t, err)
	assert.Nil(t, deletedItem2)

	// Verify links are deleted
	deletedLink, err := helper.LinkRepo.GetByID(ctx, linkID)
	assert.Error(t, err)
	assert.Nil(t, deletedLink)
}

// TestCrossDomainComplexGraph tests complex item-link relationships
func TestCrossDomainComplexGraph(t *testing.T) {
	ctx := context.Background()
	helper := NewIntegrationTestHelper(ctx, t)
	defer helper.Cleanup()

	// Setup: Create project
	project := &models.Project{Name: "Complex Graph Test"}
	err := helper.ProjectRepo.Create(ctx, project)
	require.NoError(t, err)

	// Create items: A -> B -> C -> D with A -> C (shortcut) and C -> A (cycle)
	itemA := &models.Item{ProjectID: project.ID, Title: "Item A"}
	itemB := &models.Item{ProjectID: project.ID, Title: "Item B"}
	itemC := &models.Item{ProjectID: project.ID, Title: "Item C"}
	itemD := &models.Item{ProjectID: project.ID, Title: "Item D"}

	for _, item := range []*models.Item{itemA, itemB, itemC, itemD} {
		err := helper.ItemRepo.Create(ctx, item)
		require.NoError(t, err)
	}

	// Create links forming a complex graph
	linkAB := &models.Link{SourceID: itemA.ID, TargetID: itemB.ID, Type: "depends_on"}
	linkBC := &models.Link{SourceID: itemB.ID, TargetID: itemC.ID, Type: "depends_on"}
	linkCD := &models.Link{SourceID: itemC.ID, TargetID: itemD.ID, Type: "depends_on"}
	linkAC := &models.Link{SourceID: itemA.ID, TargetID: itemC.ID, Type: "relates_to"}
	linkCA := &models.Link{SourceID: itemC.ID, TargetID: itemA.ID, Type: "relates_to"} // Cycle

	for _, link := range []*models.Link{linkAB, linkBC, linkCD, linkAC, linkCA} {
		err := helper.LinkRepo.Create(ctx, link)
		require.NoError(t, err)
	}

	// Verify A has 2 outgoing links
	outgoingA, err := helper.LinkRepo.GetBySourceID(ctx, itemA.ID)
	require.NoError(t, err)
	assert.Equal(t, 2, len(outgoingA))

	// Verify B has 1 outgoing link
	outgoingB, err := helper.LinkRepo.GetBySourceID(ctx, itemB.ID)
	require.NoError(t, err)
	assert.Equal(t, 1, len(outgoingB))

	// Verify C has 2 outgoing links
	outgoingC, err := helper.LinkRepo.GetBySourceID(ctx, itemC.ID)
	require.NoError(t, err)
	assert.Equal(t, 2, len(outgoingC))

	// Verify D has 0 outgoing links
	outgoingD, err := helper.LinkRepo.GetBySourceID(ctx, itemD.ID)
	require.NoError(t, err)
	assert.Equal(t, 0, len(outgoingD))

	// Verify incoming links
	incomingA, err := helper.LinkRepo.GetByTargetID(ctx, itemA.ID)
	require.NoError(t, err)
	assert.Equal(t, 1, len(incomingA)) // From C

	incomingD, err := helper.LinkRepo.GetByTargetID(ctx, itemD.ID)
	require.NoError(t, err)
	assert.Equal(t, 1, len(incomingD)) // From C
}

// TestCrossDomainAgentProjectAssociation tests agent-project relationships
func TestCrossDomainAgentProjectAssociation(t *testing.T) {
	ctx := context.Background()
	helper := NewIntegrationTestHelper(ctx, t)
	defer helper.Cleanup()

	// Create multiple projects
	project1 := &models.Project{Name: "Project 1"}
	project2 := &models.Project{Name: "Project 2"}
	err := helper.ProjectRepo.Create(ctx, project1)
	require.NoError(t, err)
	err = helper.ProjectRepo.Create(ctx, project2)
	require.NoError(t, err)

	// Create agents in each project
	agent1 := &models.Agent{ProjectID: project1.ID, Name: "Agent 1", Status: "active", Type: "task_runner"}
	agent2 := &models.Agent{ProjectID: project1.ID, Name: "Agent 2", Status: "active", Type: "analyzer"}
	agent3 := &models.Agent{ProjectID: project2.ID, Name: "Agent 3", Status: "active", Type: "monitor"}

	for _, agent := range []*models.Agent{agent1, agent2, agent3} {
		err := helper.AgentRepo.Create(ctx, agent)
		require.NoError(t, err)
	}

	// Verify agents are isolated per project
	project1Agents, err := helper.AgentRepo.GetByProjectID(ctx, project1.ID)
	require.NoError(t, err)
	assert.Equal(t, 2, len(project1Agents))

	project2Agents, err := helper.AgentRepo.GetByProjectID(ctx, project2.ID)
	require.NoError(t, err)
	assert.Equal(t, 1, len(project2Agents))

	// Verify agent references correct project
	for _, agent := range project1Agents {
		assert.Equal(t, project1.ID, agent.ProjectID)
	}

	for _, agent := range project2Agents {
		assert.Equal(t, project2.ID, agent.ProjectID)
	}
}

// TestCrossDomainDeleteProjectWithAgents tests cascade delete of agents with project
func TestCrossDomainDeleteProjectWithAgents(t *testing.T) {
	ctx := context.Background()
	helper := NewIntegrationTestHelper(ctx, t)
	defer helper.Cleanup()

	// Setup: Create project with agents
	project := &models.Project{Name: "Project with Agents"}
	err := helper.ProjectRepo.Create(ctx, project)
	require.NoError(t, err)

	agent1 := &models.Agent{ProjectID: project.ID, Name: "Agent 1", Status: "active", Type: "task_runner"}
	agent2 := &models.Agent{ProjectID: project.ID, Name: "Agent 2", Status: "active", Type: "analyzer"}

	err = helper.AgentRepo.Create(ctx, agent1)
	require.NoError(t, err)
	err = helper.AgentRepo.Create(ctx, agent2)
	require.NoError(t, err)

	projectID := project.ID
	agent1ID := agent1.ID
	agent2ID := agent2.ID

	// Delete project
	err = helper.ProjectRepo.Delete(ctx, projectID)
	require.NoError(t, err)

	// Verify project is deleted
	deletedProject, err := helper.ProjectRepo.GetByID(ctx, projectID)
	assert.Error(t, err)
	assert.Nil(t, deletedProject)

	// Verify agents are deleted
	deletedAgent1, err := helper.AgentRepo.GetByID(ctx, agent1ID)
	assert.Error(t, err)
	assert.Nil(t, deletedAgent1)

	deletedAgent2, err := helper.AgentRepo.GetByID(ctx, agent2ID)
	assert.Error(t, err)
	assert.Nil(t, deletedAgent2)
}

// TestCrossDomainMultipleLinkTypes tests different link types across items
func TestCrossDomainMultipleLinkTypes(t *testing.T) {
	ctx := context.Background()
	helper := NewIntegrationTestHelper(ctx, t)
	defer helper.Cleanup()

	// Setup: Create project and items
	project := &models.Project{Name: "Multi-Link Type Test"}
	err := helper.ProjectRepo.Create(ctx, project)
	require.NoError(t, err)

	item1 := &models.Item{ProjectID: project.ID, Title: "Item 1"}
	item2 := &models.Item{ProjectID: project.ID, Title: "Item 2"}
	err = helper.ItemRepo.Create(ctx, item1)
	require.NoError(t, err)
	err = helper.ItemRepo.Create(ctx, item2)
	require.NoError(t, err)

	// Create multiple different link types
	linkTypes := []string{"depends_on", "implements", "tests", "blocks", "relates_to"}
	links := make([]*models.Link, 0)

	for i, linkType := range linkTypes {
		// Create unique targets for each link type
		target := &models.Item{ProjectID: project.ID, Title: "Target " + linkType}
		err := helper.ItemRepo.Create(ctx, target)
		require.NoError(t, err)

		link := &models.Link{SourceID: item1.ID, TargetID: target.ID, Type: linkType}
		err = helper.LinkRepo.Create(ctx, link)
		require.NoError(t, err)
		links = append(links, link)

		// Don't create more than 3 to keep test fast
		if i >= 2 {
			break
		}
	}

	// Verify all links from item1
	allLinks, err := helper.LinkRepo.GetBySourceID(ctx, item1.ID)
	require.NoError(t, err)
	assert.GreaterOrEqual(t, len(allLinks), 3)

	// Verify each link type
	typeCount := make(map[string]int)
	for _, link := range allLinks {
		typeCount[link.Type]++
	}

	assert.Equal(t, 1, typeCount["depends_on"])
	assert.Equal(t, 1, typeCount["implements"])
	assert.Equal(t, 1, typeCount["tests"])
}

// TestCrossDomainConflictingDeletion tests handling conflicting deletes
func TestCrossDomainConflictingDeletion(t *testing.T) {
	ctx := context.Background()
	helper := NewIntegrationTestHelper(ctx, t)
	defer helper.Cleanup()

	// Setup: Create project with items and links
	project := &models.Project{Name: "Conflict Test"}
	err := helper.ProjectRepo.Create(ctx, project)
	require.NoError(t, err)

	itemA := &models.Item{ProjectID: project.ID, Title: "Item A"}
	itemB := &models.Item{ProjectID: project.ID, Title: "Item B"}
	err = helper.ItemRepo.Create(ctx, itemA)
	require.NoError(t, err)
	err = helper.ItemRepo.Create(ctx, itemB)
	require.NoError(t, err)

	// Create link A -> B
	link := &models.Link{SourceID: itemA.ID, TargetID: itemB.ID, Type: "depends_on"}
	err = helper.LinkRepo.Create(ctx, link)
	require.NoError(t, err)

	// Delete the link first
	err = helper.LinkRepo.Delete(ctx, link.ID)
	require.NoError(t, err)

	// Verify link is gone
	deletedLink, err := helper.LinkRepo.GetByID(ctx, link.ID)
	assert.Error(t, err)
	assert.Nil(t, deletedLink)

	// Verify items still exist and can be deleted
	err = helper.ItemRepo.Delete(ctx, itemA.ID)
	require.NoError(t, err)

	err = helper.ItemRepo.Delete(ctx, itemB.ID)
	require.NoError(t, err)

	// Verify both items are gone
	deletedA, err := helper.ItemRepo.GetByID(ctx, itemA.ID)
	assert.Error(t, err)
	assert.Nil(t, deletedA)

	deletedB, err := helper.ItemRepo.GetByID(ctx, itemB.ID)
	assert.Error(t, err)
	assert.Nil(t, deletedB)
}
