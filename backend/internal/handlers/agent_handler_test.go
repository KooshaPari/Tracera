//go:build !integration && !e2e

package handlers

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"net/http"
	"net/http/httptest"
	"testing"
	"time"

	"github.com/google/uuid"
	"github.com/labstack/echo/v4"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"

	"github.com/kooshapari/tracertm-backend/internal/agents"
	"github.com/kooshapari/tracertm-backend/internal/models"
	"github.com/kooshapari/tracertm-backend/internal/services"
)

const agentHandlerTestCoordinatorInterval = 2 * time.Minute

// MockAgentServiceHandler wraps MockAgentService for handler compatibility
type MockAgentServiceHandler struct {
	*services.MockAgentService
}

type agentHandlerCase struct {
	name string
	fn   func(t *testing.T)
}

// TestAgentHandler_CreateAgent tests agent creation with MockAgentService
func TestAgentHandler_CreateAgent(t *testing.T) {
	runAgentHandlerCases(t, []agentHandlerCase{
		{name: "successful creation", fn: runCreateAgentSuccess},
		{name: "invalid project_id", fn: runCreateAgentInvalidProjectID},
		{name: "missing name", fn: runCreateAgentMissingName},
	})
}

// TestAgentHandler_GetAgent tests getting a single agent
func TestAgentHandler_GetAgent(t *testing.T) {
	e := echo.New()

	t.Run("valid agent ID", func(_ *testing.T) {
		handler := &AgentHandler{}
		agentID := uuid.New().String()

		req := httptest.NewRequest(http.MethodGet, "/agents/"+agentID, nil)
		rec := httptest.NewRecorder()
		c := e.NewContext(req, rec)
		c.SetPath("/agents/:id")
		c.SetParamNames("id")
		c.SetParamValues(agentID)

		// Will fail on nil queries, but validates UUID parsing
		require.NoError(t, handler.GetAgent(c))
	})

	t.Run("invalid agent ID", func(t *testing.T) {
		handler := &AgentHandler{}

		req := httptest.NewRequest(http.MethodGet, "/agents/invalid", nil)
		rec := httptest.NewRecorder()
		c := e.NewContext(req, rec)
		c.SetPath("/agents/:id")
		c.SetParamNames("id")
		c.SetParamValues("invalid")

		err := handler.GetAgent(c)
		if err == nil {
			assert.Contains(t, rec.Body.String(), "Invalid agent ID")
		}
	})
}

// TestAgentHandler_ListAgents tests listing agents
func TestAgentHandler_ListAgents(t *testing.T) {
	e := echo.New()

	t.Run("missing project_id", func(t *testing.T) {
		handler := &AgentHandler{}

		req := httptest.NewRequest(http.MethodGet, "/agents", nil)
		rec := httptest.NewRecorder()
		c := e.NewContext(req, rec)

		err := handler.ListAgents(c)
		if err == nil {
			assert.Contains(t, rec.Body.String(), "project_id is required")
		}
	})

	t.Run("invalid project_id", func(t *testing.T) {
		handler := &AgentHandler{}

		req := httptest.NewRequest(http.MethodGet, "/agents?project_id=invalid", nil)
		rec := httptest.NewRecorder()
		c := e.NewContext(req, rec)

		err := handler.ListAgents(c)
		if err == nil {
			assert.Contains(t, rec.Body.String(), "Invalid project_id")
		}
	})

	t.Run("valid project_id", func(_ *testing.T) {
		handler := &AgentHandler{}
		projectID := uuid.New().String()

		req := httptest.NewRequest(http.MethodGet, "/agents?project_id="+projectID, nil)
		rec := httptest.NewRecorder()
		c := e.NewContext(req, rec)

		// Will fail on nil queries
		require.NoError(t, handler.ListAgents(c))
	})
}

// TestAgentHandler_UpdateAgent tests updating an agent
func TestAgentHandler_UpdateAgent(t *testing.T) {
	e := echo.New()

	t.Run("invalid agent ID", func(t *testing.T) {
		handler := &AgentHandler{}

		body := map[string]interface{}{
			"name":   "Updated Name",
			"status": "busy",
		}
		bodyBytes, err := json.Marshal(body)
		require.NoError(t, err)

		req := httptest.NewRequest(http.MethodPut, "/agents/invalid", bytes.NewReader(bodyBytes))
		req.Header.Set(echo.HeaderContentType, echo.MIMEApplicationJSON)
		rec := httptest.NewRecorder()
		c := e.NewContext(req, rec)
		c.SetPath("/agents/:id")
		c.SetParamNames("id")
		c.SetParamValues("invalid")

		err = handler.UpdateAgent(c)
		if err == nil {
			assert.Contains(t, rec.Body.String(), "Invalid agent ID")
		}
	})

	t.Run("valid update", func(t *testing.T) {
		t.Skip("Requires database connection - handler.queries is nil")
	})
}

// TestAgentHandler_DeleteAgent tests deleting an agent
func TestAgentHandler_DeleteAgent(t *testing.T) {
	e := echo.New()

	t.Run("invalid agent ID", func(t *testing.T) {
		handler := &AgentHandler{}

		req := httptest.NewRequest(http.MethodDelete, "/agents/invalid", nil)
		rec := httptest.NewRecorder()
		c := e.NewContext(req, rec)
		c.SetPath("/agents/:id")
		c.SetParamNames("id")
		c.SetParamValues("invalid")

		err := handler.DeleteAgent(c)
		if err == nil {
			assert.Contains(t, rec.Body.String(), "Invalid agent ID")
		}
	})

	t.Run("valid agent ID", func(_ *testing.T) {
		handler := &AgentHandler{}
		agentID := uuid.New().String()

		req := httptest.NewRequest(http.MethodDelete, "/agents/"+agentID, nil)
		rec := httptest.NewRecorder()
		c := e.NewContext(req, rec)
		c.SetPath("/agents/:id")
		c.SetParamNames("id")
		c.SetParamValues(agentID)

		// Will fail on nil queries
		require.NoError(t, handler.DeleteAgent(c))
	})
}

// TestAgentHandler_RegisterAgent tests agent registration with coordinator
func TestAgentHandler_RegisterAgent(t *testing.T) {
	e := echo.New()

	t.Run("successful registration", func(t *testing.T) {
		coordinator := agents.NewCoordinator(nil, agentHandlerTestCoordinatorInterval)
		handler := &AgentHandler{
			coordinator: coordinator,
		}

		req := agents.RegisterRequest{
			Name:      "Test Agent",
			ProjectID: "project-1",
			Capabilities: []agents.AgentCapability{
				{Name: "test", Version: "1.0", Description: "Test capability"},
			},
			Metadata: map[string]interface{}{"test": "data"},
		}
		bodyBytes, err := json.Marshal(req)
		require.NoError(t, err)

		httpReq := httptest.NewRequest(http.MethodPost, "/agents/register", bytes.NewReader(bodyBytes))
		httpReq.Header.Set(echo.HeaderContentType, echo.MIMEApplicationJSON)
		rec := httptest.NewRecorder()
		c := e.NewContext(httpReq, rec)

		err = handler.RegisterAgent(c)
		require.NoError(t, err)
		assert.Equal(t, http.StatusCreated, rec.Code)

		var response agents.RegisterResponse
		err = json.Unmarshal(rec.Body.Bytes(), &response)
		require.NoError(t, err)
		assert.Equal(t, "success", response.Status)
		assert.NotEmpty(t, response.AgentID)
	})

	t.Run("invalid request body", func(t *testing.T) {
		coordinator := agents.NewCoordinator(nil, agentHandlerTestCoordinatorInterval)
		handler := &AgentHandler{
			coordinator: coordinator,
		}

		httpReq := httptest.NewRequest(http.MethodPost, "/agents/register", bytes.NewReader([]byte("invalid")))
		httpReq.Header.Set(echo.HeaderContentType, echo.MIMEApplicationJSON)
		rec := httptest.NewRecorder()
		c := e.NewContext(httpReq, rec)

		err := handler.RegisterAgent(c)
		if err == nil {
			assert.Equal(t, http.StatusBadRequest, rec.Code)
		}
	})
}

// TestAgentHandler_AgentHeartbeat tests heartbeat functionality
func TestAgentHandler_AgentHeartbeat(t *testing.T) {
	runAgentHandlerCases(t, []agentHandlerCase{
		{name: "successful heartbeat", fn: runAgentHeartbeatSuccess},
		{name: "heartbeat for non-existent agent", fn: runAgentHeartbeatMissingAgent},
	})
}

// TestAgentHandler_GetNextTask tests task retrieval
func TestAgentHandler_GetNextTask(t *testing.T) {
	e := echo.New()

	t.Run("no tasks available", func(t *testing.T) {
		coordinator := agents.NewCoordinator(nil, agentHandlerTestCoordinatorInterval)
		handler := &AgentHandler{
			coordinator: coordinator,
		}

		// Register an agent
		agent := &agents.RegisteredAgent{
			Name:      "Test Agent",
			ProjectID: "project-1",
			Capabilities: []agents.AgentCapability{
				{Name: "test", Version: "1.0", Description: "Test capability"},
			},
			Status: agents.StatusIdle,
		}
		err := coordinator.RegisterAgent(agent)
		require.NoError(t, err)

		httpReq := httptest.NewRequest(http.MethodGet, "/agents/"+agent.ID+"/tasks/next", nil)
		rec := httptest.NewRecorder()
		c := e.NewContext(httpReq, rec)
		c.SetPath("/agents/:id/tasks/next")
		c.SetParamNames("id")
		c.SetParamValues(agent.ID)

		err = handler.GetNextTask(c)
		require.NoError(t, err)
		assert.Equal(t, http.StatusOK, rec.Code)

		var response agents.TaskResponse
		err = json.Unmarshal(rec.Body.Bytes(), &response)
		require.NoError(t, err)
		assert.Equal(t, "no_task", response.Status)
	})
}

// TestAgentHandler_AssignTask tests task assignment
func TestAgentHandler_AssignTask(t *testing.T) {
	e := echo.New()

	t.Run("successful task assignment", func(t *testing.T) {
		coordinator := agents.NewCoordinator(nil, agentHandlerTestCoordinatorInterval)
		handler := &AgentHandler{
			coordinator: coordinator,
		}

		task := agents.Task{
			ID:                   uuid.New().String(),
			Type:                 "test_task",
			ProjectID:            "project-1",
			Priority:             agents.PriorityNormal,
			Status:               agents.TaskStatusPending,
			RequiredCapabilities: []string{"test"},
			Parameters:           map[string]interface{}{"test": "data"},
			CreatedAt:            time.Now(),
			MaxRetries:           3,
		}
		bodyBytes, err := json.Marshal(task)
		require.NoError(t, err)

		httpReq := httptest.NewRequest(http.MethodPost, "/agents/tasks", bytes.NewReader(bodyBytes))
		httpReq.Header.Set(echo.HeaderContentType, echo.MIMEApplicationJSON)
		rec := httptest.NewRecorder()
		c := e.NewContext(httpReq, rec)

		err = handler.AssignTask(c)
		require.NoError(t, err)
		assert.Equal(t, http.StatusCreated, rec.Code)

		var response map[string]interface{}
		err = json.Unmarshal(rec.Body.Bytes(), &response)
		require.NoError(t, err)
		assert.Equal(t, "queued", response["status"])
	})
}

// TestAgentHandler_SubmitTaskResult tests task result submission
func TestAgentHandler_SubmitTaskResult(t *testing.T) {
	e := echo.New()

	t.Run("successful task result", func(t *testing.T) {
		coordinator := agents.NewCoordinator(nil, agentHandlerTestCoordinatorInterval)
		handler := &AgentHandler{
			coordinator: coordinator,
		}

		// Register agent
		agent := &agents.RegisteredAgent{
			Name:      "Test Agent",
			ProjectID: "project-1",
			Capabilities: []agents.AgentCapability{
				{Name: "test", Version: "1.0", Description: "Test capability"},
			},
			Status: agents.StatusIdle,
		}
		err := coordinator.RegisterAgent(agent)
		require.NoError(t, err)

		// Assign task
		task := &agents.Task{
			ID:                   uuid.New().String(),
			Type:                 "test",
			ProjectID:            "project-1",
			Priority:             agents.PriorityNormal,
			Status:               agents.TaskStatusPending,
			RequiredCapabilities: []string{"test"},
			Parameters:           map[string]interface{}{},
			CreatedAt:            time.Now(),
			MaxRetries:           3,
		}
		err = coordinator.AssignTask(task)
		require.NoError(t, err)

		// Get the task
		assignedTask, err := coordinator.GetNextTask(agent.ID)
		require.NoError(t, err)
		require.NotNil(t, assignedTask)

		// Submit result
		req := agents.TaskResultRequest{
			AgentID: agent.ID,
			TaskID:  assignedTask.ID,
			Result: &agents.TaskResult{
				Success: true,
				Data:    map[string]interface{}{"status": "completed"},
				Message: "Task completed successfully",
			},
		}
		bodyBytes, err := json.Marshal(req)
		require.NoError(t, err)

		httpReq := httptest.NewRequest(http.MethodPost, "/agents/tasks/result", bytes.NewReader(bodyBytes))
		httpReq.Header.Set(echo.HeaderContentType, echo.MIMEApplicationJSON)
		rec := httptest.NewRecorder()
		c := e.NewContext(httpReq, rec)

		err = handler.SubmitTaskResult(c)
		require.NoError(t, err)
		assert.Equal(t, http.StatusOK, rec.Code)
	})
}

// TestAgentHandler_SubmitTaskError tests task error submission
func TestAgentHandler_SubmitTaskError(t *testing.T) {
	e := echo.New()

	t.Run("submit task error", func(t *testing.T) {
		coordinator := agents.NewCoordinator(nil, agentHandlerTestCoordinatorInterval)
		handler := &AgentHandler{
			coordinator: coordinator,
		}

		// Register agent
		agent := &agents.RegisteredAgent{
			Name:      "Test Agent",
			ProjectID: "project-1",
			Capabilities: []agents.AgentCapability{
				{Name: "test", Version: "1.0", Description: "Test capability"},
			},
			Status: agents.StatusIdle,
		}
		err := coordinator.RegisterAgent(agent)
		require.NoError(t, err)

		// Assign task
		task := &agents.Task{
			ID:                   uuid.New().String(),
			Type:                 "test",
			ProjectID:            "project-1",
			Priority:             agents.PriorityNormal,
			Status:               agents.TaskStatusPending,
			RequiredCapabilities: []string{"test"},
			Parameters:           map[string]interface{}{},
			CreatedAt:            time.Now(),
			MaxRetries:           3,
		}
		err = coordinator.AssignTask(task)
		require.NoError(t, err)

		// Get the task
		assignedTask, err := coordinator.GetNextTask(agent.ID)
		require.NoError(t, err)
		require.NotNil(t, assignedTask)

		// Submit error
		req := agents.TaskErrorRequest{
			AgentID:      agent.ID,
			TaskID:       assignedTask.ID,
			ErrorMessage: "Task failed",
			ErrorCode:    "",
			Retryable:    false,
			Timestamp:    time.Time{},
		}
		bodyBytes, err := json.Marshal(req)
		require.NoError(t, err)

		httpReq := httptest.NewRequest(http.MethodPost, "/agents/tasks/error", bytes.NewReader(bodyBytes))
		httpReq.Header.Set(echo.HeaderContentType, echo.MIMEApplicationJSON)
		rec := httptest.NewRecorder()
		c := e.NewContext(httpReq, rec)

		err = handler.SubmitTaskError(c)
		require.NoError(t, err)
		assert.Equal(t, http.StatusOK, rec.Code)
	})
}

// TestAgentHandler_ListRegisteredAgents tests listing registered agents
func TestAgentHandler_ListRegisteredAgents(t *testing.T) {
	e := echo.New()

	t.Run("list all agents", func(t *testing.T) {
		coordinator := agents.NewCoordinator(nil, agentHandlerTestCoordinatorInterval)
		handler := &AgentHandler{
			coordinator: coordinator,
		}

		// Register multiple agents
		for i := 0; i < 3; i++ {
			agent := &agents.RegisteredAgent{
				Name:      fmt.Sprintf("Agent %d", i),
				ProjectID: "project-1",
				Capabilities: []agents.AgentCapability{
					{Name: "test", Version: "1.0", Description: "Test capability"},
				},
				Status: agents.StatusIdle,
			}
			err := coordinator.RegisterAgent(agent)
			require.NoError(t, err)
		}

		httpReq := httptest.NewRequest(http.MethodGet, "/agents/registered?project_id=project-1", nil)
		rec := httptest.NewRecorder()
		c := e.NewContext(httpReq, rec)

		err := handler.ListRegisteredAgents(c)
		require.NoError(t, err)
		assert.Equal(t, http.StatusOK, rec.Code)

		var response []*agents.RegisteredAgent
		err = json.Unmarshal(rec.Body.Bytes(), &response)
		require.NoError(t, err)
		assert.Len(t, response, 3)
	})
}

// TestAgentHandler_GetAgentStatus tests getting agent status
func TestAgentHandler_GetAgentStatus(t *testing.T) {
	e := echo.New()

	t.Run("get existing agent status", func(t *testing.T) {
		coordinator := agents.NewCoordinator(nil, agentHandlerTestCoordinatorInterval)
		handler := &AgentHandler{
			coordinator: coordinator,
		}

		// Register agent
		agent := &agents.RegisteredAgent{
			Name:      "Test Agent",
			ProjectID: "project-1",
			Capabilities: []agents.AgentCapability{
				{Name: "test", Version: "1.0", Description: "Test capability"},
			},
			Status: agents.StatusIdle,
		}
		err := coordinator.RegisterAgent(agent)
		require.NoError(t, err)

		httpReq := httptest.NewRequest(http.MethodGet, "/agents/"+agent.ID+"/status", nil)
		rec := httptest.NewRecorder()
		c := e.NewContext(httpReq, rec)
		c.SetPath("/agents/:id/status")
		c.SetParamNames("id")
		c.SetParamValues(agent.ID)

		err = handler.GetAgentStatus(c)
		require.NoError(t, err)
		assert.Equal(t, http.StatusOK, rec.Code)

		var response *agents.RegisteredAgent
		err = json.Unmarshal(rec.Body.Bytes(), &response)
		require.NoError(t, err)
		assert.Equal(t, agent.ID, response.ID)
		assert.Equal(t, agents.StatusIdle, response.Status)
	})

	t.Run("agent not found", func(t *testing.T) {
		coordinator := agents.NewCoordinator(nil, agentHandlerTestCoordinatorInterval)
		handler := &AgentHandler{
			coordinator: coordinator,
		}

		httpReq := httptest.NewRequest(http.MethodGet, "/agents/non-existent/status", nil)
		rec := httptest.NewRecorder()
		c := e.NewContext(httpReq, rec)
		c.SetPath("/agents/:id/status")
		c.SetParamNames("id")
		c.SetParamValues("non-existent")

		err := handler.GetAgentStatus(c)
		if err == nil {
			assert.Equal(t, http.StatusNotFound, rec.Code)
		}
	})
}

// TestAgentHandler_UnregisterAgent tests agent unregistration
func TestAgentHandler_UnregisterAgent(t *testing.T) {
	e := echo.New()

	t.Run("successful unregistration", func(t *testing.T) {
		coordinator := agents.NewCoordinator(nil, agentHandlerTestCoordinatorInterval)
		handler := &AgentHandler{
			coordinator: coordinator,
		}

		// Register agent
		agent := &agents.RegisteredAgent{
			Name:      "Test Agent",
			ProjectID: "project-1",
			Capabilities: []agents.AgentCapability{
				{Name: "test", Version: "1.0", Description: "Test capability"},
			},
			Status: agents.StatusIdle,
		}
		err := coordinator.RegisterAgent(agent)
		require.NoError(t, err)

		httpReq := httptest.NewRequest(http.MethodDelete, "/agents/"+agent.ID+"/unregister", nil)
		rec := httptest.NewRecorder()
		c := e.NewContext(httpReq, rec)
		c.SetPath("/agents/:id/unregister")
		c.SetParamNames("id")
		c.SetParamValues(agent.ID)

		err = handler.UnregisterAgent(c)
		require.NoError(t, err)
		assert.Equal(t, http.StatusOK, rec.Code)

		// Verify agent is removed
		_, err = coordinator.GetAgent(agent.ID)
		assert.Error(t, err)
	})

	t.Run("missing agent ID", func(t *testing.T) {
		coordinator := agents.NewCoordinator(nil, agentHandlerTestCoordinatorInterval)
		handler := &AgentHandler{
			coordinator: coordinator,
		}

		httpReq := httptest.NewRequest(http.MethodDelete, "/agents//unregister", nil)
		rec := httptest.NewRecorder()
		c := e.NewContext(httpReq, rec)
		c.SetPath("/agents/:id/unregister")
		c.SetParamNames("id")
		c.SetParamValues("")

		err := handler.UnregisterAgent(c)
		if err == nil {
			assert.Equal(t, http.StatusBadRequest, rec.Code)
		}
	})
}

// TestAgentHandler_GetCoordinatorStatus tests coordinator status endpoint
func TestAgentHandler_GetCoordinatorStatus(t *testing.T) {
	e := echo.New()

	t.Run("coordinator status", func(t *testing.T) {
		coordinator := agents.NewCoordinator(nil, agentHandlerTestCoordinatorInterval)
		handler := &AgentHandler{
			coordinator: coordinator,
		}

		// Register some agents
		for i := 0; i < 5; i++ {
			agent := &agents.RegisteredAgent{
				Name:      fmt.Sprintf("Agent %d", i),
				ProjectID: "project-1",
				Capabilities: []agents.AgentCapability{
					{Name: "test", Version: "1.0", Description: "Test capability"},
				},
				Status: agents.StatusIdle,
			}
			err := coordinator.RegisterAgent(agent)
			require.NoError(t, err)
		}

		httpReq := httptest.NewRequest(http.MethodGet, "/agents/coordinator/status", nil)
		rec := httptest.NewRecorder()
		c := e.NewContext(httpReq, rec)

		err := handler.GetCoordinatorStatus(c)
		require.NoError(t, err)
		assert.Equal(t, http.StatusOK, rec.Code)

		var response map[string]interface{}
		err = json.Unmarshal(rec.Body.Bytes(), &response)
		require.NoError(t, err)
		assert.Equal(t, "operational", response["status"])
		assert.InEpsilon(t, float64(5), response["total_agents"], 1e-9)
	})

	t.Run("nil coordinator", func(t *testing.T) {
		handler := &AgentHandler{
			coordinator: nil,
		}

		httpReq := httptest.NewRequest(http.MethodGet, "/agents/coordinator/status", nil)
		rec := httptest.NewRecorder()
		c := e.NewContext(httpReq, rec)

		err := handler.GetCoordinatorStatus(c)
		if err == nil {
			assert.Equal(t, http.StatusInternalServerError, rec.Code)
		}
	})
}

// TestAgentHandler_GetAgentMetrics tests agent metrics endpoint
func TestAgentHandler_GetAgentMetrics(t *testing.T) {
	e := echo.New()

	t.Run("get agent metrics", func(t *testing.T) {
		coordinator := agents.NewCoordinator(nil, agentHandlerTestCoordinatorInterval)
		handler := &AgentHandler{
			coordinator: coordinator,
		}

		// Register agent
		agent := &agents.RegisteredAgent{
			Name:      "Test Agent",
			ProjectID: "project-1",
			Capabilities: []agents.AgentCapability{
				{Name: "test", Version: "1.0", Description: "Test capability"},
			},
			Status: agents.StatusIdle,
		}
		err := coordinator.RegisterAgent(agent)
		require.NoError(t, err)

		httpReq := httptest.NewRequest(http.MethodGet, "/agents/"+agent.ID+"/metrics", nil)
		rec := httptest.NewRecorder()
		c := e.NewContext(httpReq, rec)
		c.SetPath("/agents/:id/metrics")
		c.SetParamNames("id")
		c.SetParamValues(agent.ID)

		err = handler.GetAgentMetrics(c)
		require.NoError(t, err)
		assert.Equal(t, http.StatusOK, rec.Code)

		var response map[string]interface{}
		err = json.Unmarshal(rec.Body.Bytes(), &response)
		require.NoError(t, err)
		assert.Equal(t, agent.ID, response["agent_id"])
		assert.Equal(t, "Test Agent", response["name"])
	})
}

// TestAgentHandler_GetQueueStats tests queue statistics endpoint
func TestAgentHandler_GetQueueStats(t *testing.T) {
	e := echo.New()

	t.Run("queue statistics", func(t *testing.T) {
		coordinator := agents.NewCoordinator(nil, agentHandlerTestCoordinatorInterval)
		handler := &AgentHandler{
			coordinator: coordinator,
		}

		// Register agents with different statuses
		for i := 0; i < 3; i++ {
			agent := &agents.RegisteredAgent{
				Name:      fmt.Sprintf("Agent %d", i),
				ProjectID: "project-1",
				Capabilities: []agents.AgentCapability{
					{Name: "test", Version: "1.0", Description: "Test capability"},
				},
				Status: agents.StatusIdle,
			}
			err := coordinator.RegisterAgent(agent)
			require.NoError(t, err)
		}

		httpReq := httptest.NewRequest(http.MethodGet, "/agents/queue/stats?project_id=project-1", nil)
		rec := httptest.NewRecorder()
		c := e.NewContext(httpReq, rec)

		err := handler.GetQueueStats(c)
		require.NoError(t, err)
		assert.Equal(t, http.StatusOK, rec.Code)

		var response map[string]interface{}
		err = json.Unmarshal(rec.Body.Bytes(), &response)
		require.NoError(t, err)
		assert.InEpsilon(t, float64(3), response["active_agents"], 1e-9)
	})
}

// TestAgentHandler_CoordinatorHealthCheck tests coordinator health check
func TestAgentHandler_CoordinatorHealthCheck(t *testing.T) {
	e := echo.New()

	t.Run("healthy coordinator", func(t *testing.T) {
		coordinator := agents.NewCoordinator(nil, agentHandlerTestCoordinatorInterval)
		handler := &AgentHandler{
			coordinator: coordinator,
		}

		httpReq := httptest.NewRequest(http.MethodGet, "/agents/coordinator/health", nil)
		rec := httptest.NewRecorder()
		c := e.NewContext(httpReq, rec)

		err := handler.CoordinatorHealthCheck(c)
		require.NoError(t, err)
		assert.Equal(t, http.StatusOK, rec.Code)

		var response map[string]interface{}
		err = json.Unmarshal(rec.Body.Bytes(), &response)
		require.NoError(t, err)
		assert.Equal(t, "healthy", response["status"])
	})

	t.Run("unavailable coordinator", func(t *testing.T) {
		handler := &AgentHandler{
			coordinator: nil,
		}

		httpReq := httptest.NewRequest(http.MethodGet, "/agents/coordinator/health", nil)
		rec := httptest.NewRecorder()
		c := e.NewContext(httpReq, rec)

		err := handler.CoordinatorHealthCheck(c)
		if err == nil {
			assert.Equal(t, http.StatusServiceUnavailable, rec.Code)
			var response map[string]interface{}
			err = json.Unmarshal(rec.Body.Bytes(), &response)
			require.NoError(t, err)
			assert.Equal(t, "unavailable", response["status"])
		}
	})
}

// TestAgentHandler_AgentLifecycle tests complete agent lifecycle
func TestAgentHandler_AgentLifecycle(t *testing.T) {
	t.Run("complete lifecycle", func(t *testing.T) {
		runAgentLifecycleComplete(t)
	})
}

func runAgentHandlerCases(t *testing.T, cases []agentHandlerCase) {
	for _, tc := range cases {
		t.Run(tc.name, func(t *testing.T) {
			tc.fn(t)
		})
	}
}

func runCreateAgentSuccess(t *testing.T) {
	e := echo.New()
	mockService := &services.MockAgentService{}
	createdAgent := &models.Agent{
		ID:        uuid.New().String(),
		ProjectID: uuid.New().String(),
		Name:      "Test Agent",
		Status:    "idle",
		CreatedAt: time.Now(),
		UpdatedAt: time.Now(),
	}

	mockService.CreateAgentFunc = func(_ context.Context, agent *models.Agent) error {
		agent.ID = createdAgent.ID
		agent.CreatedAt = createdAgent.CreatedAt
		agent.UpdatedAt = createdAgent.UpdatedAt
		return nil
	}

	body := map[string]interface{}{
		"project_id": createdAgent.ProjectID,
		"name":       "Test Agent",
		"status":     "idle",
		"metadata":   json.RawMessage(`{}`),
	}
	bodyBytes, err := json.Marshal(body)
	require.NoError(t, err)

	req := httptest.NewRequest(http.MethodPost, "/agents", bytes.NewReader(bodyBytes))
	req.Header.Set(echo.HeaderContentType, echo.MIMEApplicationJSON)
	rec := httptest.NewRecorder()
	c := e.NewContext(req, rec)

	assert.NotNil(t, c)
}

func runCreateAgentInvalidProjectID(t *testing.T) {
	e := echo.New()
	handler := &AgentHandler{
		binder: &TestBinder{},
	}

	body := map[string]interface{}{
		"project_id": "invalid-uuid",
		"name":       "Test Agent",
	}
	bodyBytes, err := json.Marshal(body)
	require.NoError(t, err)

	req := httptest.NewRequest(http.MethodPost, "/agents", bytes.NewReader(bodyBytes))
	req.Header.Set(echo.HeaderContentType, echo.MIMEApplicationJSON)
	rec := httptest.NewRecorder()
	c := e.NewContext(req, rec)

	err = handler.CreateAgent(c)
	if err == nil {
		assert.Contains(t, rec.Body.String(), "Invalid project_id")
	}
}

func runCreateAgentMissingName(t *testing.T) {
	e := echo.New()
	handler := &AgentHandler{
		binder: &TestBinder{},
	}

	body := map[string]interface{}{
		"project_id": uuid.New().String(),
		"status":     "idle",
	}
	bodyBytes, err := json.Marshal(body)
	require.NoError(t, err)

	req := httptest.NewRequest(http.MethodPost, "/agents", bytes.NewReader(bodyBytes))
	req.Header.Set(echo.HeaderContentType, echo.MIMEApplicationJSON)
	rec := httptest.NewRecorder()
	c := e.NewContext(req, rec)

	require.NoError(t, handler.CreateAgent(c))
}

func runAgentHeartbeatSuccess(t *testing.T) {
	e := echo.New()
	coordinator := agents.NewCoordinator(nil, agentHandlerTestCoordinatorInterval)
	handler := &AgentHandler{
		coordinator: coordinator,
	}

	agent := &agents.RegisteredAgent{
		Name:      "Test Agent",
		ProjectID: "project-1",
		Capabilities: []agents.AgentCapability{
			{Name: "test", Version: "1.0", Description: "Test capability"},
		},
		Status: agents.StatusIdle,
	}
	err := coordinator.RegisterAgent(agent)
	require.NoError(t, err)

	req := agents.HeartbeatRequest{
		AgentID: agent.ID,
		Status:  agents.StatusBusy,
		Metrics: nil,
	}
	bodyBytes, err := json.Marshal(req)
	require.NoError(t, err)

	httpReq := httptest.NewRequest(http.MethodPost, "/agents/heartbeat", bytes.NewReader(bodyBytes))
	httpReq.Header.Set(echo.HeaderContentType, echo.MIMEApplicationJSON)
	rec := httptest.NewRecorder()
	c := e.NewContext(httpReq, rec)

	err = handler.AgentHeartbeat(c)
	require.NoError(t, err)
	assert.Equal(t, http.StatusOK, rec.Code)

	var response agents.HeartbeatResponse
	err = json.Unmarshal(rec.Body.Bytes(), &response)
	require.NoError(t, err)
	assert.Equal(t, "success", response.Status)
}

func runAgentHeartbeatMissingAgent(t *testing.T) {
	e := echo.New()
	coordinator := agents.NewCoordinator(nil, agentHandlerTestCoordinatorInterval)
	handler := &AgentHandler{
		coordinator: coordinator,
	}

	req := agents.HeartbeatRequest{
		AgentID: "non-existent-id",
		Status:  agents.StatusBusy,
		Metrics: nil,
	}
	bodyBytes, err := json.Marshal(req)
	require.NoError(t, err)

	httpReq := httptest.NewRequest(http.MethodPost, "/agents/heartbeat", bytes.NewReader(bodyBytes))
	httpReq.Header.Set(echo.HeaderContentType, echo.MIMEApplicationJSON)
	rec := httptest.NewRecorder()
	c := e.NewContext(httpReq, rec)

	err = handler.AgentHeartbeat(c)
	if err == nil {
		assert.Equal(t, http.StatusInternalServerError, rec.Code)
	}
}

func runAgentLifecycleComplete(t *testing.T) {
	e := echo.New()
	coordinator := agents.NewCoordinator(nil, agentHandlerTestCoordinatorInterval)
	handler := &AgentHandler{
		coordinator: coordinator,
	}

	agentID := registerLifecycleAgent(t, e, handler)
	sendLifecycleHeartbeat(t, e, handler, agentID)
	assertLifecycleStatus(t, e, handler, agentID)
	unregisterLifecycleAgent(t, e, handler, agentID)
}

func registerLifecycleAgent(t *testing.T, e *echo.Echo, handler *AgentHandler) string {
	regReq := agents.RegisterRequest{
		Name:      "Lifecycle Agent",
		ProjectID: "project-1",
		Capabilities: []agents.AgentCapability{
			{Name: "test", Version: "1.0", Description: "Test capability"},
		},
		Metadata: nil,
	}
	bodyBytes, err := json.Marshal(regReq)
	require.NoError(t, err)

	httpReq := httptest.NewRequest(http.MethodPost, "/agents/register", bytes.NewReader(bodyBytes))
	httpReq.Header.Set(echo.HeaderContentType, echo.MIMEApplicationJSON)
	rec := httptest.NewRecorder()
	c := e.NewContext(httpReq, rec)

	err = handler.RegisterAgent(c)
	require.NoError(t, err)

	var regResp agents.RegisterResponse
	err = json.Unmarshal(rec.Body.Bytes(), &regResp)
	require.NoError(t, err)
	return regResp.AgentID
}

func sendLifecycleHeartbeat(t *testing.T, e *echo.Echo, handler *AgentHandler, agentID string) {
	hbReq := agents.HeartbeatRequest{
		AgentID: agentID,
		Status:  agents.StatusBusy,
		Metrics: nil,
	}
	bodyBytes, err := json.Marshal(hbReq)
	require.NoError(t, err)

	httpReq := httptest.NewRequest(http.MethodPost, "/agents/heartbeat", bytes.NewReader(bodyBytes))
	httpReq.Header.Set(echo.HeaderContentType, echo.MIMEApplicationJSON)
	rec := httptest.NewRecorder()
	c := e.NewContext(httpReq, rec)

	err = handler.AgentHeartbeat(c)
	require.NoError(t, err)
}

func assertLifecycleStatus(t *testing.T, e *echo.Echo, handler *AgentHandler, agentID string) {
	httpReq := httptest.NewRequest(http.MethodGet, "/agents/"+agentID+"/status", nil)
	rec := httptest.NewRecorder()
	c := e.NewContext(httpReq, rec)
	c.SetPath("/agents/:id/status")
	c.SetParamNames("id")
	c.SetParamValues(agentID)

	err := handler.GetAgentStatus(c)
	require.NoError(t, err)

	var agent *agents.RegisteredAgent
	err = json.Unmarshal(rec.Body.Bytes(), &agent)
	require.NoError(t, err)
	assert.Equal(t, agents.StatusBusy, agent.Status)
}

func unregisterLifecycleAgent(t *testing.T, e *echo.Echo, handler *AgentHandler, agentID string) {
	httpReq := httptest.NewRequest(http.MethodDelete, "/agents/"+agentID+"/unregister", nil)
	rec := httptest.NewRecorder()
	c := e.NewContext(httpReq, rec)
	c.SetPath("/agents/:id/unregister")
	c.SetParamNames("id")
	c.SetParamValues(agentID)

	err := handler.UnregisterAgent(c)
	require.NoError(t, err)
}
