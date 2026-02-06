//go:build e2e

package e2e

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"net/http"
	"testing"
	"time"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

// TestE2E_RegisterAgents_AssignTasks_Complete tests basic agent workflow
func TestE2E_RegisterAgents_AssignTasks_Complete(t *testing.T) {
	ctx := setupE2ETest(t)
	defer ctx.Cleanup()

	client := &http.Client{Timeout: 30 * time.Second}
	baseURL := ctx.ServerURL
	token, projectID := createUserAndProject(t, client, baseURL, "agent.user@test.com")

	// Register multiple agents
	agentIDs := make([]string, 3)
	agentTypes := []string{"analyzer", "executor", "validator"}

	for i, agentType := range agentTypes {
		agentReq := map[string]interface{}{
			"name":         fmt.Sprintf("%s-agent-%d", agentType, i),
			"type":         agentType,
			"capabilities": []string{"task_processing", "data_analysis"},
			"metadata": map[string]interface{}{
				"version": "1.0.0",
				"status":  "active",
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
			ID   string `json:"id"`
			Name string `json:"name"`
		}
		json.NewDecoder(resp.Body).Decode(&agentResp)
		resp.Body.Close()
		agentIDs[i] = agentResp.ID
	}

	// Create tasks for agents
	taskIDs := make([]string, 3)
	for i := 0; i < 3; i++ {
		taskReq := map[string]interface{}{
			"project_id":  projectID,
			"title":       fmt.Sprintf("Agent Task %d", i),
			"description": "Task to be processed by agent",
			"type":        "agent_task",
			"metadata": map[string]interface{}{
				"priority": 3,
			},
		}
		taskBody, _ := json.Marshal(taskReq)
		req, _ := http.NewRequestWithContext(context.Background(), "POST", baseURL+"/api/v1/items", bytes.NewBuffer(taskBody))
		req.Header.Set("Authorization", "Bearer "+token)
		req.Header.Set("Content-Type", "application/json")

		resp, err := client.Do(req)
		require.NoError(t, err)

		var taskResp struct {
			ID string `json:"id"`
		}
		json.NewDecoder(resp.Body).Decode(&taskResp)
		resp.Body.Close()
		taskIDs[i] = taskResp.ID
	}

	// Assign tasks to agents
	for i, taskID := range taskIDs {
		assignReq := map[string]interface{}{
			"agent_id": agentIDs[i],
			"task_id":  taskID,
		}
		assignBody, _ := json.Marshal(assignReq)
		req, _ := http.NewRequestWithContext(context.Background(), "POST", baseURL+"/api/v1/agents/"+agentIDs[i]+"/assign", bytes.NewBuffer(assignBody))
		req.Header.Set("Authorization", "Bearer "+token)
		req.Header.Set("Content-Type", "application/json")

		resp, err := client.Do(req)
		require.NoError(t, err)
		require.Equal(t, http.StatusOK, resp.StatusCode)
		resp.Body.Close()
	}

	// Verify task assignments
	for i, agentID := range agentIDs {
		req, _ := http.NewRequestWithContext(context.Background(), "GET", baseURL+"/api/v1/agents/"+agentID+"/tasks", nil)
		req.Header.Set("Authorization", "Bearer "+token)

		resp, err := client.Do(req)
		require.NoError(t, err)

		var tasksResp struct {
			Tasks []struct {
				ID     string `json:"id"`
				Status string `json:"status"`
			} `json:"tasks"`
		}
		json.NewDecoder(resp.Body).Decode(&tasksResp)
		resp.Body.Close()

		assert.GreaterOrEqual(t, len(tasksResp.Tasks), 1)
		assert.Equal(t, taskIDs[i], tasksResp.Tasks[0].ID)
	}

	// Complete tasks
	for i, taskID := range taskIDs {
		completeReq := map[string]interface{}{
			"status": "completed",
			"result": map[string]interface{}{
				"output":  fmt.Sprintf("Task %d completed successfully", i),
				"metrics": map[string]int{"processed": 100},
			},
		}
		completeBody, _ := json.Marshal(completeReq)
		req, _ := http.NewRequestWithContext(context.Background(), "POST", baseURL+"/api/v1/agents/"+agentIDs[i]+"/tasks/"+taskID+"/complete", bytes.NewBuffer(completeBody))
		req.Header.Set("Authorization", "Bearer "+token)
		req.Header.Set("Content-Type", "application/json")

		resp, err := client.Do(req)
		require.NoError(t, err)
		require.Equal(t, http.StatusOK, resp.StatusCode)
		resp.Body.Close()
	}

	// Verify all tasks completed
	req, _ := http.NewRequestWithContext(context.Background(), "GET", baseURL+"/api/v1/projects/"+projectID+"/tasks?status=completed", nil)
	req.Header.Set("Authorization", "Bearer "+token)

	resp, err := client.Do(req)
	require.NoError(t, err)

	var completedResp struct {
		Tasks []struct {
			ID string `json:"id"`
		} `json:"tasks"`
	}
	json.NewDecoder(resp.Body).Decode(&completedResp)
	resp.Body.Close()

	assert.Equal(t, 3, len(completedResp.Tasks))
}

// TestE2E_AgentFailover_TaskReassignment tests agent failure and task reassignment
func TestE2E_AgentFailover_TaskReassignment(t *testing.T) {
	ctx := setupE2ETest(t)
	defer ctx.Cleanup()

	client := &http.Client{Timeout: 30 * time.Second}
	baseURL := ctx.ServerURL
	token, projectID := createUserAndProject(t, client, baseURL, "failover.user@test.com")

	// Register two agents
	agentIDs := make([]string, 2)
	for i := 0; i < 2; i++ {
		agentReq := map[string]interface{}{
			"name":         fmt.Sprintf("worker-agent-%d", i),
			"type":         "worker",
			"capabilities": []string{"processing"},
		}
		agentBody, _ := json.Marshal(agentReq)
		req, _ := http.NewRequestWithContext(context.Background(), "POST", baseURL+"/api/v1/agents", bytes.NewBuffer(agentBody))
		req.Header.Set("Authorization", "Bearer "+token)
		req.Header.Set("Content-Type", "application/json")

		resp, err := client.Do(req)
		require.NoError(t, err)

		var agentResp struct {
			ID string `json:"id"`
		}
		json.NewDecoder(resp.Body).Decode(&agentResp)
		resp.Body.Close()
		agentIDs[i] = agentResp.ID
	}

	// Create task
	taskReq := map[string]interface{}{
		"project_id": projectID,
		"title":      "Critical Task",
		"type":       "agent_task",
	}
	taskBody, _ := json.Marshal(taskReq)
	req, _ := http.NewRequestWithContext(context.Background(), "POST", baseURL+"/api/v1/items", bytes.NewBuffer(taskBody))
	req.Header.Set("Authorization", "Bearer "+token)
	req.Header.Set("Content-Type", "application/json")

	resp, err := client.Do(req)
	require.NoError(t, err)

	var taskResp struct {
		ID string `json:"id"`
	}
	json.NewDecoder(resp.Body).Decode(&taskResp)
	resp.Body.Close()
	taskID := taskResp.ID

	// Assign to first agent
	assignReq := map[string]interface{}{
		"agent_id": agentIDs[0],
		"task_id":  taskID,
	}
	assignBody, _ := json.Marshal(assignReq)
	req, _ = http.NewRequestWithContext(context.Background(), "POST", baseURL+"/api/v1/agents/"+agentIDs[0]+"/assign", bytes.NewBuffer(assignBody))
	req.Header.Set("Authorization", "Bearer "+token)
	req.Header.Set("Content-Type", "application/json")

	resp, err = client.Do(req)
	require.NoError(t, err)
	resp.Body.Close()

	// Simulate agent failure
	failReq := map[string]interface{}{
		"status": "failed",
		"reason": "Agent crashed unexpectedly",
	}
	failBody, _ := json.Marshal(failReq)
	req, _ = http.NewRequestWithContext(context.Background(), "POST", baseURL+"/api/v1/agents/"+agentIDs[0]+"/status", bytes.NewBuffer(failBody))
	req.Header.Set("Authorization", "Bearer "+token)
	req.Header.Set("Content-Type", "application/json")

	resp, err = client.Do(req)
	require.NoError(t, err)
	resp.Body.Close()

	// Reassign task to second agent
	reassignReq := map[string]interface{}{
		"from_agent": agentIDs[0],
		"to_agent":   agentIDs[1],
		"task_id":    taskID,
	}
	reassignBody, _ := json.Marshal(reassignReq)
	req, _ = http.NewRequestWithContext(context.Background(), "POST", baseURL+"/api/v1/agents/reassign", bytes.NewBuffer(reassignBody))
	req.Header.Set("Authorization", "Bearer "+token)
	req.Header.Set("Content-Type", "application/json")

	resp, err = client.Do(req)
	require.NoError(t, err)
	require.Equal(t, http.StatusOK, resp.StatusCode)
	resp.Body.Close()

	// Verify task is now assigned to second agent
	req, _ = http.NewRequestWithContext(context.Background(), "GET", baseURL+"/api/v1/agents/"+agentIDs[1]+"/tasks", nil)
	req.Header.Set("Authorization", "Bearer "+token)

	resp, err = client.Do(req)
	require.NoError(t, err)

	var tasksResp struct {
		Tasks []struct {
			ID string `json:"id"`
		} `json:"tasks"`
	}
	json.NewDecoder(resp.Body).Decode(&tasksResp)
	resp.Body.Close()

	assert.GreaterOrEqual(t, len(tasksResp.Tasks), 1)
	assert.Equal(t, taskID, tasksResp.Tasks[0].ID)
}

// TestE2E_MultipleAgents_LoadBalancing tests load balancing across agents
func TestE2E_MultipleAgents_LoadBalancing(t *testing.T) {
	ctx := setupE2ETest(t)
	defer ctx.Cleanup()

	client := &http.Client{Timeout: 30 * time.Second}
	baseURL := ctx.ServerURL
	token, projectID := createUserAndProject(t, client, baseURL, "loadbalance.user@test.com")

	// Register 5 agents
	agentCount := 5
	agentIDs := make([]string, agentCount)

	for i := 0; i < agentCount; i++ {
		agentReq := map[string]interface{}{
			"name":         fmt.Sprintf("lb-agent-%d", i),
			"type":         "worker",
			"capabilities": []string{"processing"},
			"metadata": map[string]interface{}{
				"max_tasks": 3,
			},
		}
		agentBody, _ := json.Marshal(agentReq)
		req, _ := http.NewRequestWithContext(context.Background(), "POST", baseURL+"/api/v1/agents", bytes.NewBuffer(agentBody))
		req.Header.Set("Authorization", "Bearer "+token)
		req.Header.Set("Content-Type", "application/json")

		resp, err := client.Do(req)
		require.NoError(t, err)

		var agentResp struct {
			ID string `json:"id"`
		}
		json.NewDecoder(resp.Body).Decode(&agentResp)
		resp.Body.Close()
		agentIDs[i] = agentResp.ID
	}

	// Create 15 tasks
	taskCount := 15
	taskIDs := make([]string, taskCount)

	for i := 0; i < taskCount; i++ {
		taskReq := map[string]interface{}{
			"project_id": projectID,
			"title":      fmt.Sprintf("LB Task %d", i),
			"type":       "agent_task",
		}
		taskBody, _ := json.Marshal(taskReq)
		req, _ := http.NewRequestWithContext(context.Background(), "POST", baseURL+"/api/v1/items", bytes.NewBuffer(taskBody))
		req.Header.Set("Authorization", "Bearer "+token)
		req.Header.Set("Content-Type", "application/json")

		resp, err := client.Do(req)
		require.NoError(t, err)

		var taskResp struct {
			ID string `json:"id"`
		}
		json.NewDecoder(resp.Body).Decode(&taskResp)
		resp.Body.Close()
		taskIDs[i] = taskResp.ID
	}

	// Distribute tasks using load balancer
	distributeReq := map[string]interface{}{
		"task_ids":  taskIDs,
		"agent_ids": agentIDs,
		"strategy":  "round_robin",
	}
	distributeBody, _ := json.Marshal(distributeReq)
	req, _ := http.NewRequestWithContext(context.Background(), "POST", baseURL+"/api/v1/agents/distribute", bytes.NewBuffer(distributeBody))
	req.Header.Set("Authorization", "Bearer "+token)
	req.Header.Set("Content-Type", "application/json")

	resp, err := client.Do(req)
	require.NoError(t, err)

	var distributeResp struct {
		Distributed  int                 `json:"distributed"`
		Distribution map[string][]string `json:"distribution"`
	}
	json.NewDecoder(resp.Body).Decode(&distributeResp)
	resp.Body.Close()

	assert.Equal(t, taskCount, distributeResp.Distributed)

	// Verify load is balanced (each agent should have 3 tasks)
	taskCounts := make(map[string]int)
	for agentID, tasks := range distributeResp.Distribution {
		taskCounts[agentID] = len(tasks)
	}

	for _, count := range taskCounts {
		assert.Equal(t, 3, count, "Tasks should be evenly distributed")
	}

	// Verify via agent endpoints
	for _, agentID := range agentIDs {
		req, _ := http.NewRequestWithContext(context.Background(), "GET", baseURL+"/api/v1/agents/"+agentID+"/tasks", nil)
		req.Header.Set("Authorization", "Bearer "+token)

		resp, err := client.Do(req)
		require.NoError(t, err)

		var tasksResp struct {
			Tasks []struct {
				ID string `json:"id"`
			} `json:"tasks"`
		}
		json.NewDecoder(resp.Body).Decode(&tasksResp)
		resp.Body.Close()

		assert.Equal(t, 3, len(tasksResp.Tasks))
	}
}
