//go:build e2e

package e2e

import (
	"bytes"
	"context"
	"encoding/json"
	"net/http"
	"testing"
	"time"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

// TestE2E_ServiceLayer_AgentCoordinationWorkflow tests agent collaboration
// Scenario: Create agents -> Assign tasks -> Monitor coordination -> Complete workflow
func TestE2E_ServiceLayer_AgentCoordinationWorkflow(t *testing.T) {
	ctx := setupE2ETest(t)
	defer ctx.Cleanup()

	client := &http.Client{Timeout: 30 * time.Second}
	baseURL := ctx.ServerURL

	// Setup
	token, projectID := setupUserAndProject(t, client, baseURL, "agent.coord@test.com", "Agent Coordination Project")

	// Step 1: Create work items
	itemIDs := make([]string, 3)
	itemTypes := []string{"analyze_requirements", "generate_code", "review_code"}

	for i, itemType := range itemTypes {
		itemIDs[i] = createItem(t, client, baseURL, token, projectID, map[string]interface{}{
			"title":  "Task for " + itemType,
			"type":   "task",
			"status": "todo",
			"metadata": map[string]interface{}{
				"agent_capability": itemType,
			},
		})
	}

	// Step 2: Create specialized agents
	agentIDs := make(map[string]string)
	agents := []struct {
		name       string
		capability string
	}{
		{"RequirementsAnalyzer", "analyze_requirements"},
		{"CodeGenerator", "generate_code"},
		{"CodeReviewer", "review_code"},
	}

	for _, agent := range agents {
		agentReq := map[string]interface{}{
			"project_id": projectID,
			"name":       agent.name,
			"status":     "idle",
			"metadata": map[string]interface{}{
				"capability":           agent.capability,
				"max_concurrent_tasks": 3,
			},
		}
		agentBody, _ := json.Marshal(agentReq)
		req, _ := http.NewRequestWithContext(context.Background(), "POST", baseURL+"/api/v1/agents", bytes.NewBuffer(agentBody))
		req.Header.Set("Authorization", "Bearer "+token)
		req.Header.Set("Content-Type", "application/json")

		resp, err := client.Do(req)
		require.NoError(t, err)
		require.Equal(t, http.StatusCreated, resp.StatusCode)

		var agentResp struct {
			ID string `json:"id"`
		}
		json.NewDecoder(resp.Body).Decode(&agentResp)
		resp.Body.Close()

		agentIDs[agent.name] = agentResp.ID
	}

	// Step 3: Assign tasks to agents (simulated via metadata update)
	for i, itemID := range itemIDs {
		agentName := agents[i].name
		updateItem(t, client, baseURL, token, itemID, map[string]interface{}{
			"status": "assigned",
			"metadata": map[string]interface{}{
				"assigned_agent_id": agentIDs[agentName],
				"assigned_at":       time.Now().Format(time.RFC3339),
			},
		})
	}

	// Step 4: Update agent statuses to active
	for _, agentID := range agentIDs {
		updateAgent(t, client, baseURL, token, agentID, map[string]interface{}{
			"status": "active",
		})
	}

	// Step 5: Simulate work progression
	time.Sleep(100 * time.Millisecond)

	// First agent completes requirements analysis
	updateItem(t, client, baseURL, token, itemIDs[0], map[string]interface{}{
		"status": "completed",
	})

	// Second agent starts code generation
	updateItem(t, client, baseURL, token, itemIDs[1], map[string]interface{}{
		"status": "in_progress",
	})

	// Step 6: Create dependency link (code gen depends on requirements)
	createLink(t, client, baseURL, token, itemIDs[1], itemIDs[0], "depends_on", map[string]interface{}{
		"dependency_type": "sequential",
	})

	// Step 7: Complete code generation
	updateItem(t, client, baseURL, token, itemIDs[1], map[string]interface{}{
		"status": "completed",
	})

	// Step 8: Code review starts
	updateItem(t, client, baseURL, token, itemIDs[2], map[string]interface{}{
		"status": "in_progress",
	})
	createLink(t, client, baseURL, token, itemIDs[2], itemIDs[1], "reviews", map[string]interface{}{
		"review_type": "automated",
	})

	// Step 9: Verify final states
	for i, itemID := range itemIDs[:2] {
		item := getItem(t, client, baseURL, token, itemID)
		assert.Equal(t, "completed", item["status"], "Item %d should be completed", i)
	}

	reviewItem := getItem(t, client, baseURL, token, itemIDs[2])
	assert.Equal(t, "in_progress", reviewItem["status"])

	// Step 10: Verify all agents are still active
	for _, agentID := range agentIDs {
		agent := getAgent(t, client, baseURL, token, agentID)
		assert.Equal(t, "active", agent["status"])
	}
}
