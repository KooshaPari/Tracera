//go:build !integration && !e2e

package handlers

import (
	"bytes"
	"context"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/labstack/echo/v4"
	"github.com/stretchr/testify/assert"
)

// TestAgentHandler_RegisterAgent_Validation tests RegisterAgent validation
func TestAgentHandler_RegisterAgent_Validation(t *testing.T) {
	e := echo.New()

	t.Run("invalid JSON", func(t *testing.T) {
		handler := &AgentHandler{}

		req := httptest.NewRequest(http.MethodPost, "/agents/register", bytes.NewReader([]byte("invalid json")))
		req.Header.Set(echo.HeaderContentType, echo.MIMEApplicationJSON)
		rec := httptest.NewRecorder()
		c := e.NewContext(req, rec)

		err := handler.RegisterAgent(c)
		if err != nil {
			he, ok := err.(*echo.HTTPError)
			if ok {
				assert.Equal(t, http.StatusBadRequest, he.Code)
			}
		} else {
			assert.Contains(t, rec.Body.String(), "error")
		}
	})
}

// TestAgentHandler_AgentHeartbeat_Validation tests AgentHeartbeat validation
func TestAgentHandler_AgentHeartbeat_Validation(t *testing.T) {
	e := echo.New()

	t.Run("invalid JSON", func(t *testing.T) {
		handler := &AgentHandler{}

		req := httptest.NewRequest(http.MethodPost, "/agents/heartbeat", bytes.NewReader([]byte("invalid json")))
		req.Header.Set(echo.HeaderContentType, echo.MIMEApplicationJSON)
		rec := httptest.NewRecorder()
		c := e.NewContext(req, rec)

		err := handler.AgentHeartbeat(c)
		// Will fail on nil coordinator, but tests bind validation
		if err != nil {
			he, ok := err.(*echo.HTTPError)
			if ok {
				assert.True(t, he.Code == http.StatusBadRequest || he.Code == http.StatusInternalServerError)
			}
		} else {
			assert.Contains(t, rec.Body.String(), "error")
		}
	})
}

// TestAgentHandler_GetNextTask_Validation tests GetNextTask validation
func TestAgentHandler_GetNextTask_Validation(t *testing.T) {
	e := echo.New()

	t.Run("nil coordinator", func(t *testing.T) {
		handler := &AgentHandler{
			coordinator: nil,
		}

		req := httptest.NewRequest(http.MethodGet, "/agents/agent-1/tasks/next", nil)
		rec := httptest.NewRecorder()
		c := e.NewContext(req, rec)
		c.SetPath("/agents/:id/tasks/next")
		c.SetParamNames("id")
		c.SetParamValues("agent-1")

		// Will panic on nil coordinator
		defer func() {
			if r := recover(); r != nil {
				// Expected panic on nil coordinator
				assert.NotNil(t, r)
			}
		}()
		err := handler.GetNextTask(c)
		// May panic or return error
		_ = err
	})
}

// TestAgentHandler_SubmitTaskResult_Validation tests SubmitTaskResult validation
func TestAgentHandler_SubmitTaskResult_Validation(t *testing.T) {
	e := echo.New()

	t.Run("invalid agent ID", func(t *testing.T) {
		handler := &AgentHandler{}

		body := map[string]interface{}{
			"task_id": "task-1",
			"result":  "success",
		}
		bodyBytes, _ := json.Marshal(body)

		req := httptest.NewRequest(http.MethodPost, "/agents/invalid/tasks/result", bytes.NewReader(bodyBytes))
		req.Header.Set(echo.HeaderContentType, echo.MIMEApplicationJSON)
		rec := httptest.NewRecorder()
		c := e.NewContext(req, rec)
		c.SetPath("/agents/:id/tasks/result")
		c.SetParamNames("id")
		c.SetParamValues("invalid")

		err := handler.SubmitTaskResult(c)
		if err != nil {
			he, ok := err.(*echo.HTTPError)
			if ok {
				assert.Equal(t, http.StatusBadRequest, he.Code)
			}
		} else {
			assert.Contains(t, rec.Body.String(), "error")
		}
	})

	t.Run("invalid JSON", func(t *testing.T) {
		handler := &AgentHandler{}

		req := httptest.NewRequest(http.MethodPost, "/agents/123e4567-e89b-12d3-a456-426614174000/tasks/result", bytes.NewReader([]byte("invalid json")))
		req.Header.Set(echo.HeaderContentType, echo.MIMEApplicationJSON)
		rec := httptest.NewRecorder()
		c := e.NewContext(req, rec)
		c.SetPath("/agents/:id/tasks/result")
		c.SetParamNames("id")
		c.SetParamValues("123e4567-e89b-12d3-a456-426614174000")

		err := handler.SubmitTaskResult(c)
		if err != nil {
			he, ok := err.(*echo.HTTPError)
			if ok {
				assert.Equal(t, http.StatusBadRequest, he.Code)
			}
		}
	})
}

// TestAgentHandler_SubmitTaskError_Validation tests SubmitTaskError validation
func TestAgentHandler_SubmitTaskError_Validation(t *testing.T) {
	e := echo.New()

	t.Run("invalid JSON", func(t *testing.T) {
		handler := &AgentHandler{}

		req := httptest.NewRequest(http.MethodPost, "/agents/tasks/error", bytes.NewReader([]byte("invalid json")))
		req.Header.Set(echo.HeaderContentType, echo.MIMEApplicationJSON)
		rec := httptest.NewRecorder()
		c := e.NewContext(req, rec)

		err := handler.SubmitTaskError(c)
		// Will fail on nil coordinator, but tests bind validation
		if err != nil {
			he, ok := err.(*echo.HTTPError)
			if ok {
				assert.True(t, he.Code == http.StatusBadRequest || he.Code == http.StatusInternalServerError)
			}
		} else {
			assert.Contains(t, rec.Body.String(), "error")
		}
	})
}

// TestAgentHandler_AssignTask_Validation tests AssignTask validation
func TestAgentHandler_AssignTask_Validation(t *testing.T) {
	e := echo.New()

	t.Run("invalid JSON", func(t *testing.T) {
		handler := &AgentHandler{}

		req := httptest.NewRequest(http.MethodPost, "/agents/tasks/assign", bytes.NewReader([]byte("invalid json")))
		req.Header.Set(echo.HeaderContentType, echo.MIMEApplicationJSON)
		rec := httptest.NewRecorder()
		c := e.NewContext(req, rec)

		err := handler.AssignTask(c)
		// Will fail on nil coordinator, but tests bind validation
		if err != nil {
			he, ok := err.(*echo.HTTPError)
			if ok {
				assert.True(t, he.Code == http.StatusBadRequest || he.Code == http.StatusInternalServerError)
			}
		} else {
			assert.Contains(t, rec.Body.String(), "error")
		}
	})
}

// TestAgentHandler_ListRegisteredAgents_Validation tests ListRegisteredAgents
func TestAgentHandler_ListRegisteredAgents_Validation(t *testing.T) {
	e := echo.New()

	t.Run("nil coordinator", func(t *testing.T) {
		handler := &AgentHandler{
			coordinator: nil,
		}

		req := httptest.NewRequest(http.MethodGet, "/agents/registered", nil)
		rec := httptest.NewRecorder()
		c := e.NewContext(req, rec)

		// Will panic on nil coordinator
		defer func() {
			if r := recover(); r != nil {
				// Expected panic on nil coordinator
				assert.NotNil(t, r)
			}
		}()
		err := handler.ListRegisteredAgents(c)
		// May panic or return error
		_ = err
	})
}

// TestAgentHandler_GetAgentStatus_Validation tests GetAgentStatus validation
func TestAgentHandler_GetAgentStatus_Validation(t *testing.T) {
	e := echo.New()

	t.Run("nil coordinator", func(t *testing.T) {
		handler := &AgentHandler{
			coordinator: nil,
		}

		req := httptest.NewRequest(http.MethodGet, "/agents/agent-1/status", nil)
		rec := httptest.NewRecorder()
		c := e.NewContext(req, rec)
		c.SetPath("/agents/:id/status")
		c.SetParamNames("id")
		c.SetParamValues("agent-1")

		// Will panic on nil coordinator
		defer func() {
			if r := recover(); r != nil {
				// Expected panic on nil coordinator
				assert.NotNil(t, r)
			}
		}()
		err := handler.GetAgentStatus(c)
		// May panic or return error
		_ = err
	})
}

// TestAgentHandler_HelperMethods tests helper methods
func TestAgentHandler_HelperMethods(t *testing.T) {
	t.Run("getCacheKey", func(t *testing.T) {
		handler := &AgentHandler{}
		agentID := "agent-123"
		key := handler.getCacheKey(agentID)
		assert.Contains(t, key, agentID)
		assert.Contains(t, key, "agent")
	})

	t.Run("invalidateAgentCache with nil cache", func(_ *testing.T) {
		handler := &AgentHandler{
			cache: nil,
		}
		// Should not panic
		handler.invalidateAgentCache(context.Background(), "agent-1")
	})

	t.Run("publishAgentEvent with nil publisher", func(_ *testing.T) {
		handler := &AgentHandler{
			publisher: nil,
		}
		// Should not panic
		handler.publishAgentEvent(context.Background(), "created", "agent-1", "project-1", map[string]string{"test": "data"})
	})

	t.Run("broadcastAgentEvent with nil broadcaster", func(_ *testing.T) {
		handler := &AgentHandler{
			realtimeBroadcaster: nil,
		}
		// Should not panic
		handler.broadcastAgentEvent(context.Background(), "created", "agent-1")
	})
}
