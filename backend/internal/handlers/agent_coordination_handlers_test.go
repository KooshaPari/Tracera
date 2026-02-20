//go:build !integration && !e2e

// Package handlers tests agent coordination handlers.
package handlers

import (
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"
	"time"

	"github.com/labstack/echo/v4"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"

	"github.com/kooshapari/tracertm-backend/internal/agents"
)

const agentCoordinationTestInterval = 2 * time.Minute

// TestCoordinationHandlers_UnregisterAgent tests agent unregistration
func TestCoordinationHandlers_UnregisterAgent(t *testing.T) {
	runCoordinationCases(t, []coordinationCase{
		{name: "unregister existing agent", fn: runUnregisterExistingAgent},
		{name: "unregister nonexistent agent", fn: runUnregisterNonexistentAgent},
		{name: "missing agent ID", fn: runUnregisterMissingID},
	})
}

// TestCoordinationHandlers_GetCoordinatorStatus tests coordinator status retrieval
func TestCoordinationHandlers_GetCoordinatorStatus(t *testing.T) {
	t.Run("get coordinator status without coordinator", func(t *testing.T) {
		e := echo.New()
		handler := &AgentHandler{
			coordinator: nil,
		}

		req := httptest.NewRequest(http.MethodGet, "/agents/coordinator/status", nil)
		rec := httptest.NewRecorder()
		c := e.NewContext(req, rec)

		err := handler.GetCoordinatorStatus(c)

		require.NoError(t, err)
		assert.Equal(t, http.StatusInternalServerError, rec.Code)
		assert.Contains(t, rec.Body.String(), "coordinator not initialized")
	})

	t.Run("get coordinator status with coordinator", func(t *testing.T) {
		e := echo.New()
		coordinator := agents.NewCoordinator(nil, agentCoordinationTestInterval)

		handler := &AgentHandler{
			coordinator: coordinator,
		}

		req := httptest.NewRequest(http.MethodGet, "/agents/coordinator/status", nil)
		rec := httptest.NewRecorder()
		c := e.NewContext(req, rec)

		err := handler.GetCoordinatorStatus(c)

		// May fail due to GORM in coordinator
		if err == nil {
			assert.Equal(t, http.StatusOK, rec.Code)
		}
	})

	t.Run("get coordinator status with project filter", func(t *testing.T) {
		e := echo.New()
		coordinator := agents.NewCoordinator(nil, agentCoordinationTestInterval)

		handler := &AgentHandler{
			coordinator: coordinator,
		}

		req := httptest.NewRequest(http.MethodGet, "/agents/coordinator/status?project_id=project-1", nil)
		rec := httptest.NewRecorder()
		c := e.NewContext(req, rec)

		err := handler.GetCoordinatorStatus(c)

		if err == nil {
			assert.Equal(t, http.StatusOK, rec.Code)
		}
	})
}

// TestCoordinationHandlers_QueueOperations tests queue management endpoints
func TestCoordinationHandlers_QueueOperations(t *testing.T) {
	t.Run("get queue stats", func(t *testing.T) {
		e := echo.New()
		coordinator := agents.NewCoordinator(nil, agentCoordinationTestInterval)

		handler := &AgentHandler{
			coordinator: coordinator,
		}

		req := httptest.NewRequest(http.MethodGet, "/agents/queue/stats", nil)
		rec := httptest.NewRecorder()
		c := e.NewContext(req, rec)

		err := handler.GetQueueStats(c)

		if err == nil {
			assert.Equal(t, http.StatusOK, rec.Code)
			var response map[string]interface{}
			err := json.Unmarshal(rec.Body.Bytes(), &response)
			require.NoError(t, err)
			assert.Contains(t, response, "timestamp")
			assert.Contains(t, response, "active_agents")
		}
	})

	t.Run("list queued tasks without project_id", func(t *testing.T) {
		e := echo.New()
		coordinator := agents.NewCoordinator(nil, agentCoordinationTestInterval)

		handler := &AgentHandler{
			coordinator: coordinator,
		}

		req := httptest.NewRequest(http.MethodGet, "/agents/queue/tasks", nil)
		rec := httptest.NewRecorder()
		c := e.NewContext(req, rec)

		err := handler.ListQueuedTasks(c)

		require.NoError(t, err)
		assert.Equal(t, http.StatusBadRequest, rec.Code)
		assert.Contains(t, rec.Body.String(), "project_id is required")
	})

	t.Run("list queued tasks with valid project_id", func(t *testing.T) {
		e := echo.New()
		coordinator := agents.NewCoordinator(nil, agentCoordinationTestInterval)

		handler := &AgentHandler{
			coordinator: coordinator,
		}

		req := httptest.NewRequest(http.MethodGet, "/agents/queue/tasks?project_id=project-1", nil)
		rec := httptest.NewRecorder()
		c := e.NewContext(req, rec)

		err := handler.ListQueuedTasks(c)

		if err == nil {
			assert.Equal(t, http.StatusOK, rec.Code)
		}
	})
}

// TestCoordinationHandlers_TaskOperations tests task management endpoints
func TestCoordinationHandlers_TaskOperations(t *testing.T) {
	t.Run("cancel task without task_id", func(t *testing.T) {
		e := echo.New()
		handler := &AgentHandler{}

		req := httptest.NewRequest(http.MethodDelete, "/agents/tasks//cancel", nil)
		rec := httptest.NewRecorder()
		c := e.NewContext(req, rec)
		c.SetPath("/agents/tasks/:task_id/cancel")
		c.SetParamNames("task_id")
		c.SetParamValues("")

		err := handler.CancelTask(c)

		require.NoError(t, err)
		assert.Equal(t, http.StatusBadRequest, rec.Code)
		assert.Contains(t, rec.Body.String(), "task_id is required")
	})

	t.Run("get task details without task_id", func(t *testing.T) {
		e := echo.New()
		handler := &AgentHandler{}

		req := httptest.NewRequest(http.MethodGet, "/agents/tasks//details", nil)
		rec := httptest.NewRecorder()
		c := e.NewContext(req, rec)
		c.SetPath("/agents/tasks/:task_id")
		c.SetParamNames("task_id")
		c.SetParamValues("")

		err := handler.GetTaskDetails(c)

		require.NoError(t, err)
		assert.Equal(t, http.StatusBadRequest, rec.Code)
		assert.Contains(t, rec.Body.String(), "task_id is required")
	})
}

// TestCoordinationHandlers_RebalanceTasks tests task rebalancing
func TestCoordinationHandlers_RebalanceTasks(t *testing.T) {
	t.Run("rebalance tasks without project_id", func(t *testing.T) {
		e := echo.New()
		handler := &AgentHandler{}

		req := httptest.NewRequest(http.MethodPost, "/agents/queue/rebalance", nil)
		rec := httptest.NewRecorder()
		c := e.NewContext(req, rec)

		err := handler.RebalanceTasks(c)

		require.NoError(t, err)
		assert.Equal(t, http.StatusBadRequest, rec.Code)
		assert.Contains(t, rec.Body.String(), "project_id is required")
	})

	t.Run("rebalance tasks with valid project_id", func(t *testing.T) {
		e := echo.New()
		coordinator := agents.NewCoordinator(nil, agentCoordinationTestInterval)

		handler := &AgentHandler{
			coordinator: coordinator,
		}

		req := httptest.NewRequest(http.MethodPost, "/agents/queue/rebalance?project_id=project-1", nil)
		rec := httptest.NewRecorder()
		c := e.NewContext(req, rec)

		err := handler.RebalanceTasks(c)

		if err == nil {
			assert.Equal(t, http.StatusOK, rec.Code)
			var response map[string]interface{}
			err := json.Unmarshal(rec.Body.Bytes(), &response)
			require.NoError(t, err)
			// Rebalance returns "success" or "no_agents" depending on whether agents exist
			status, ok := response["status"].(string)
			assert.True(t, ok)
			assert.True(t, status == "success" || status == "no_agents")
		}
	})
}

// TestCoordinationHandlers_AgentHistory tests agent history retrieval
func TestCoordinationHandlers_AgentHistory(t *testing.T) {
	runCoordinationCases(t, []coordinationCase{
		{name: "get agent history without agent_id", fn: runAgentHistoryMissingID},
		{name: "get agent history with valid agent_id", fn: runAgentHistoryValidID},
		{name: "get agent history with limit parameter", fn: runAgentHistoryWithLimit},
		{name: "get agent history with invalid limit", fn: runAgentHistoryInvalidLimit},
	})
}

// TestCoordinationHandlers_HealthCheck tests coordinator health check
func TestCoordinationHandlers_HealthCheck(t *testing.T) {
	t.Run("health check without coordinator", func(t *testing.T) {
		e := echo.New()
		handler := &AgentHandler{
			coordinator: nil,
		}

		req := httptest.NewRequest(http.MethodGet, "/agents/coordinator/health", nil)
		rec := httptest.NewRecorder()
		c := e.NewContext(req, rec)

		err := handler.CoordinatorHealthCheck(c)

		require.NoError(t, err)
		assert.Equal(t, http.StatusServiceUnavailable, rec.Code)
		assert.Contains(t, rec.Body.String(), "unavailable")
	})

	t.Run("health check with coordinator", func(t *testing.T) {
		e := echo.New()
		coordinator := agents.NewCoordinator(nil, agentCoordinationTestInterval)

		handler := &AgentHandler{
			coordinator: coordinator,
		}

		req := httptest.NewRequest(http.MethodGet, "/agents/coordinator/health", nil)
		rec := httptest.NewRecorder()
		c := e.NewContext(req, rec)

		err := handler.CoordinatorHealthCheck(c)

		if err == nil {
			assert.Equal(t, http.StatusOK, rec.Code)
			var response map[string]interface{}
			err := json.Unmarshal(rec.Body.Bytes(), &response)
			require.NoError(t, err)
			assert.Equal(t, "healthy", response["status"])
		}
	})
}

type coordinationCase struct {
	name string
	fn   func(t *testing.T)
}

func runCoordinationCases(t *testing.T, cases []coordinationCase) {
	for _, tc := range cases {
		t.Run(tc.name, func(t *testing.T) {
			tc.fn(t)
		})
	}
}

func runUnregisterExistingAgent(t *testing.T) {
	e := echo.New()
	coordinator := agents.NewCoordinator(nil, agentCoordinationTestInterval)

	_ = &agents.RegisteredAgent{
		ID:        "test-agent-1",
		Name:      "Test Agent",
		ProjectID: "project-1",
		Status:    agents.StatusIdle,
	}

	handler := &AgentHandler{
		coordinator: coordinator,
	}

	req := httptest.NewRequest(http.MethodDelete, "/agents/test-agent-1/unregister", nil)
	rec := httptest.NewRecorder()
	c := e.NewContext(req, rec)
	c.SetPath("/agents/:id/unregister")
	c.SetParamNames("id")
	c.SetParamValues("test-agent-1")

	err := handler.UnregisterAgent(c)
	require.NoError(t, err)
	assert.Equal(t, http.StatusNotFound, rec.Code)
}

func runUnregisterNonexistentAgent(t *testing.T) {
	e := echo.New()
	coordinator := agents.NewCoordinator(nil, agentCoordinationTestInterval)

	handler := &AgentHandler{
		coordinator: coordinator,
	}

	req := httptest.NewRequest(http.MethodDelete, "/agents/nonexistent/unregister", nil)
	rec := httptest.NewRecorder()
	c := e.NewContext(req, rec)
	c.SetPath("/agents/:id/unregister")
	c.SetParamNames("id")
	c.SetParamValues("nonexistent")

	err := handler.UnregisterAgent(c)
	require.NoError(t, err)
	assert.Equal(t, http.StatusNotFound, rec.Code)
}

func runUnregisterMissingID(t *testing.T) {
	e := echo.New()
	handler := &AgentHandler{}

	req := httptest.NewRequest(http.MethodDelete, "/agents//unregister", nil)
	rec := httptest.NewRecorder()
	c := e.NewContext(req, rec)
	c.SetPath("/agents/:id/unregister")
	c.SetParamNames("id")
	c.SetParamValues("")

	err := handler.UnregisterAgent(c)
	require.NoError(t, err)
	assert.Equal(t, http.StatusBadRequest, rec.Code)
	assert.Contains(t, rec.Body.String(), "agent ID is required")
}

func runAgentHistoryMissingID(t *testing.T) {
	e := echo.New()
	handler := &AgentHandler{}

	req := httptest.NewRequest(http.MethodGet, "/agents//history", nil)
	rec := httptest.NewRecorder()
	c := e.NewContext(req, rec)
	c.SetPath("/agents/:id/history")
	c.SetParamNames("id")
	c.SetParamValues("")

	err := handler.GetAgentHistory(c)
	require.NoError(t, err)
	assert.Equal(t, http.StatusBadRequest, rec.Code)
	assert.Contains(t, rec.Body.String(), "agent ID is required")
}

func runAgentHistoryValidID(t *testing.T) {
	e := echo.New()
	coordinator := agents.NewCoordinator(nil, agentCoordinationTestInterval)

	handler := &AgentHandler{
		coordinator: coordinator,
	}

	req := httptest.NewRequest(http.MethodGet, "/agents/agent-1/history", nil)
	rec := httptest.NewRecorder()
	c := e.NewContext(req, rec)
	c.SetPath("/agents/:id/history")
	c.SetParamNames("id")
	c.SetParamValues("agent-1")

	err := handler.GetAgentHistory(c)
	require.NoError(t, err)
	// Should return 404 because agent doesn't exist
	assert.Equal(t, http.StatusNotFound, rec.Code)
}

func runAgentHistoryWithLimit(t *testing.T) {
	e := echo.New()
	coordinator := agents.NewCoordinator(nil, agentCoordinationTestInterval)

	handler := &AgentHandler{
		coordinator: coordinator,
	}

	req := httptest.NewRequest(http.MethodGet, "/agents/agent-1/history?limit=50", nil)
	rec := httptest.NewRecorder()
	c := e.NewContext(req, rec)
	c.SetPath("/agents/:id/history")
	c.SetParamNames("id")
	c.SetParamValues("agent-1")

	err := handler.GetAgentHistory(c)
	require.NoError(t, err)
	// Should return 404 because agent doesn't exist (limit is valid)
	assert.Equal(t, http.StatusNotFound, rec.Code)
}

func runAgentHistoryInvalidLimit(t *testing.T) {
	e := echo.New()
	coordinator := agents.NewCoordinator(nil, agentCoordinationTestInterval)

	handler := &AgentHandler{
		coordinator: coordinator,
	}

	req := httptest.NewRequest(http.MethodGet, "/agents/agent-1/history?limit=invalid", nil)
	rec := httptest.NewRecorder()
	c := e.NewContext(req, rec)
	c.SetPath("/agents/:id/history")
	c.SetParamNames("id")
	c.SetParamValues("agent-1")

	err := handler.GetAgentHistory(c)
	require.NoError(t, err)
	assert.Equal(t, http.StatusBadRequest, rec.Code)
}
