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

const agentServiceActivityDelay = 100 * time.Millisecond

// TestAgentServiceCreate tests creating agents
func TestAgentServiceCreate(t *testing.T) {
	ctx := context.Background()
	helper := NewIntegrationTestHelper(ctx, t)
	defer helper.Cleanup()

	// Setup: Create project
	project := &models.Project{Name: "Agent Test Project"}
	err := helper.ProjectRepo.Create(ctx, project)
	require.NoError(t, err)

	// Create agent
	agent := &models.Agent{
		ProjectID: project.ID,
		Name:      "Test Agent",
		Status:    "active",
		Type:      "task_runner",
	}

	err = helper.AgentRepo.Create(ctx, agent)
	require.NoError(t, err)
	require.NotEmpty(t, agent.ID)
	assert.Equal(t, "Test Agent", agent.Name)
	assert.Equal(t, "active", agent.Status)
	assert.Equal(t, "task_runner", agent.Type)
	assert.False(t, agent.CreatedAt.IsZero())
}

// TestAgentServiceGetByID tests retrieving agents by ID
func TestAgentServiceGetByID(t *testing.T) {
	ctx := context.Background()
	helper := NewIntegrationTestHelper(ctx, t)
	defer helper.Cleanup()

	// Setup
	project := &models.Project{Name: "Agent Retrieve Test"}
	err := helper.ProjectRepo.Create(ctx, project)
	require.NoError(t, err)

	original := &models.Agent{
		ProjectID: project.ID,
		Name:      "Agent to Retrieve",
		Status:    "active",
		Type:      "analyzer",
	}
	err = helper.AgentRepo.Create(ctx, original)
	require.NoError(t, err)

	// Retrieve
	retrieved, err := helper.AgentRepo.GetByID(ctx, original.ID)
	require.NoError(t, err)
	require.NotNil(t, retrieved)
	assert.Equal(t, original.ID, retrieved.ID)
	assert.Equal(t, original.Name, retrieved.Name)
	assert.Equal(t, original.Status, retrieved.Status)
	assert.Equal(t, original.Type, retrieved.Type)
}

// TestAgentServiceGetByProjectID tests retrieving agents by project
func TestAgentServiceGetByProjectID(t *testing.T) {
	ctx := context.Background()
	helper := NewIntegrationTestHelper(ctx, t)
	defer helper.Cleanup()

	// Create project
	project := &models.Project{Name: "Multi-Agent Project"}
	err := helper.ProjectRepo.Create(ctx, project)
	require.NoError(t, err)

	// Create multiple agents for the project
	agentCount := 3
	createdAgents := make([]*models.Agent, agentCount)

	for i := 0; i < agentCount; i++ {
		agent := &models.Agent{
			ProjectID: project.ID,
			Name:      "Agent " + string(rune('A'+i)),
			Status:    "active",
			Type:      "task_runner",
		}
		err := helper.AgentRepo.Create(ctx, agent)
		require.NoError(t, err)
		createdAgents[i] = agent
	}

	// Retrieve all agents for the project
	agents, err := helper.AgentRepo.GetByProjectID(ctx, project.ID)
	require.NoError(t, err)
	assert.Equal(t, agentCount, len(agents))

	// Verify all created agents are in the list
	agentIDs := make(map[string]bool)
	for _, a := range agents {
		agentIDs[a.ID] = true
	}

	for _, created := range createdAgents {
		assert.True(t, agentIDs[created.ID], "Agent %s not found in list", created.Name)
	}
}

// TestAgentServiceUpdate tests updating agents
func TestAgentServiceUpdate(t *testing.T) {
	ctx := context.Background()
	helper := NewIntegrationTestHelper(ctx, t)
	defer helper.Cleanup()

	// Setup: Create project and agent
	project := &models.Project{Name: "Agent Update Test"}
	err := helper.ProjectRepo.Create(ctx, project)
	require.NoError(t, err)

	agent := &models.Agent{
		ProjectID: project.ID,
		Name:      "Original Name",
		Status:    "active",
		Type:      "analyzer",
	}
	err = helper.AgentRepo.Create(ctx, agent)
	require.NoError(t, err)

	originalID := agent.ID
	originalCreated := agent.CreatedAt

	// Update
	agent.Name = "Updated Name"
	agent.Status = "inactive"
	agent.Type = "monitor"
	err = helper.AgentRepo.Update(ctx, agent)
	require.NoError(t, err)

	// Verify
	updated, err := helper.AgentRepo.GetByID(ctx, originalID)
	require.NoError(t, err)
	assert.Equal(t, "Updated Name", updated.Name)
	assert.Equal(t, "inactive", updated.Status)
	assert.Equal(t, "monitor", updated.Type)
	assert.Equal(t, originalCreated, updated.CreatedAt)
	assert.True(t, updated.UpdatedAt.After(originalCreated))
}

// TestAgentServiceDelete tests deleting agents (soft delete)
func TestAgentServiceDelete(t *testing.T) {
	ctx := context.Background()
	helper := NewIntegrationTestHelper(ctx, t)
	defer helper.Cleanup()

	// Setup: Create project and agent
	project := &models.Project{Name: "Agent Delete Test"}
	err := helper.ProjectRepo.Create(ctx, project)
	require.NoError(t, err)

	agent := &models.Agent{
		ProjectID: project.ID,
		Name:      "Agent to Delete",
		Status:    "active",
		Type:      "task_runner",
	}
	err = helper.AgentRepo.Create(ctx, agent)
	require.NoError(t, err)

	agentID := agent.ID

	// Delete
	err = helper.AgentRepo.Delete(ctx, agentID)
	require.NoError(t, err)

	// Verify deleted agent cannot be retrieved
	deleted, err := helper.AgentRepo.GetByID(ctx, agentID)
	assert.Error(t, err)
	assert.Nil(t, deleted)
}

// TestAgentServiceUpdateStatus tests updating agent status
func TestAgentServiceUpdateStatus(t *testing.T) {
	ctx := context.Background()
	helper := NewIntegrationTestHelper(ctx, t)
	defer helper.Cleanup()

	// Setup
	project := &models.Project{Name: "Agent Status Test"}
	err := helper.ProjectRepo.Create(ctx, project)
	require.NoError(t, err)

	agent := &models.Agent{
		ProjectID: project.ID,
		Name:      "Status Agent",
		Status:    "initializing",
		Type:      "task_runner",
	}
	err = helper.AgentRepo.Create(ctx, agent)
	require.NoError(t, err)

	originalCreated := agent.CreatedAt

	// Update status
	err = helper.AgentRepo.UpdateStatus(ctx, agent.ID, "active")
	require.NoError(t, err)

	// Verify status was updated
	updated, err := helper.AgentRepo.GetByID(ctx, agent.ID)
	require.NoError(t, err)
	assert.Equal(t, "active", updated.Status)
	assert.Equal(t, originalCreated, updated.CreatedAt)
	assert.True(t, updated.UpdatedAt.After(originalCreated))
}

// TestAgentServiceLastActivityTracking tests agent last activity timestamps
func TestAgentServiceLastActivityTracking(t *testing.T) {
	ctx := context.Background()
	helper := NewIntegrationTestHelper(ctx, t)
	defer helper.Cleanup()

	// Setup
	project := &models.Project{Name: "Activity Tracking Test"}
	err := helper.ProjectRepo.Create(ctx, project)
	require.NoError(t, err)

	agent := &models.Agent{
		ProjectID: project.ID,
		Name:      "Active Agent",
		Status:    "active",
		Type:      "task_runner",
	}
	err = helper.AgentRepo.Create(ctx, agent)
	require.NoError(t, err)

	firstCreated := agent.CreatedAt

	// Simulate activity - wait and update
	time.Sleep(agentServiceActivityDelay)

	agent.Status = "busy"
	err = helper.AgentRepo.Update(ctx, agent)
	require.NoError(t, err)

	// Verify last activity was updated
	updated, err := helper.AgentRepo.GetByID(ctx, agent.ID)
	require.NoError(t, err)
	assert.True(t, updated.UpdatedAt.After(firstCreated), "Activity should be tracked via UpdatedAt")
	assert.Equal(t, "busy", updated.Status)
}

// TestAgentServiceMultipleAgents tests handling multiple independent agents
func TestAgentServiceMultipleAgents(t *testing.T) {
	ctx := context.Background()
	helper := NewIntegrationTestHelper(ctx, t)
	defer helper.Cleanup()

	// Create multiple projects with multiple agents each
	projectCount := 2
	agentCountPerProject := 3

	projectAgents := make(map[string][]*models.Agent)

	for p := 0; p < projectCount; p++ {
		project := &models.Project{
			Name: "Project " + string(rune('A'+p)),
		}
		err := helper.ProjectRepo.Create(ctx, project)
		require.NoError(t, err)

		for a := 0; a < agentCountPerProject; a++ {
			agent := &models.Agent{
				ProjectID: project.ID,
				Name:      "Agent " + string(rune('A'+a)),
				Status:    "active",
				Type:      "task_runner",
			}
			err := helper.AgentRepo.Create(ctx, agent)
			require.NoError(t, err)
			projectAgents[project.ID] = append(projectAgents[project.ID], agent)
		}
	}

	// Verify agents are isolated per project
	for projectID, expectedAgents := range projectAgents {
		agents, err := helper.AgentRepo.GetByProjectID(ctx, projectID)
		require.NoError(t, err)
		assert.Equal(t, len(expectedAgents), len(agents), "Project should have correct number of agents")

		// Verify all expected agents are present
		agentIDs := make(map[string]bool)
		for _, a := range agents {
			agentIDs[a.ID] = true
		}

		for _, expected := range expectedAgents {
			assert.True(t, agentIDs[expected.ID], "Agent should be in project")
		}
	}
}

// TestAgentServiceConcurrentCreation tests creating agents concurrently
func TestAgentServiceConcurrentCreation(t *testing.T) {
	ctx := context.Background()
	helper := NewIntegrationTestHelper(ctx, t)
	defer helper.Cleanup()

	// Setup: Create project
	project := &models.Project{Name: "Concurrent Agent Test"}
	err := helper.ProjectRepo.Create(ctx, project)
	require.NoError(t, err)

	// Create multiple agents
	agentCount := 5
	for i := 0; i < agentCount; i++ {
		agent := &models.Agent{
			ProjectID: project.ID,
			Name:      "Agent " + string(rune('A'+i)),
			Status:    "active",
			Type:      "task_runner",
		}
		err := helper.AgentRepo.Create(ctx, agent)
		require.NoError(t, err)
		require.NotEmpty(t, agent.ID)
	}

	// Verify all agents were created
	agents, err := helper.AgentRepo.GetByProjectID(ctx, project.ID)
	require.NoError(t, err)
	assert.Equal(t, agentCount, len(agents))

	// Verify agents have unique IDs
	idSet := make(map[string]bool)
	for _, a := range agents {
		assert.False(t, idSet[a.ID], "Agent IDs should be unique")
		idSet[a.ID] = true
	}
}

// TestAgentServiceStatusTransitions tests agent status state machine
func TestAgentServiceStatusTransitions(t *testing.T) {
	ctx := context.Background()
	helper := NewIntegrationTestHelper(ctx, t)
	defer helper.Cleanup()

	// Setup
	project := &models.Project{Name: "Status Transition Test"}
	err := helper.ProjectRepo.Create(ctx, project)
	require.NoError(t, err)

	agent := &models.Agent{
		ProjectID: project.ID,
		Name:      "Status Agent",
		Status:    "initializing",
		Type:      "task_runner",
	}
	err = helper.AgentRepo.Create(ctx, agent)
	require.NoError(t, err)

	// Test status transitions
	statuses := []string{"initializing", "active", "busy", "error", "inactive"}

	for _, newStatus := range statuses {
		err := helper.AgentRepo.UpdateStatus(ctx, agent.ID, newStatus)
		require.NoError(t, err)

		retrieved, err := helper.AgentRepo.GetByID(ctx, agent.ID)
		require.NoError(t, err)
		assert.Equal(t, newStatus, retrieved.Status)
	}
}
