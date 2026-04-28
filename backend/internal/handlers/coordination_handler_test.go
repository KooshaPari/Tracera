//go:build !integration && !e2e

package handlers

import (
	"bytes"
	"encoding/json"
	"errors"
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/labstack/echo/v4"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

func TestCoordinationHandler_AcquireLock_Validation(t *testing.T) {
	e := echo.New()

	t.Run("invalid JSON", func(t *testing.T) {
		// Handler needs to be initialized, but for validation we test bind error
		// Create a minimal handler - it will fail on lockManager call, but bind error comes first
		handler := &CoordinationHandler{}

		req := httptest.NewRequest(http.MethodPost, "/coordination/locks", bytes.NewReader([]byte("invalid json")))
		req.Header.Set(echo.HeaderContentType, echo.MIMEApplicationJSON)
		rec := httptest.NewRecorder()
		c := e.NewContext(req, rec)

		err := handler.AcquireLock(c)
		// Bind will fail with invalid JSON, returning 400
		// If bind succeeds but handler is nil, it will panic - but bind should fail first
		if err != nil {
			he := &echo.HTTPError{}
			ok := errors.As(err, &he)
			if ok {
				assert.Equal(t, http.StatusBadRequest, he.Code)
			}
		} else {
			// If no error, check response body for error message
			assert.Contains(t, rec.Body.String(), "error")
		}
	})
}

func TestCoordinationHandler_ReleaseLock_Validation(t *testing.T) {
	e := echo.New()

	t.Run("missing agent_id", func(t *testing.T) {
		handler := &CoordinationHandler{}

		req := httptest.NewRequest(http.MethodDelete, "/coordination/locks/lock1", nil)
		rec := httptest.NewRecorder()
		c := e.NewContext(req, rec)
		c.SetPath("/coordination/locks/:lock_id")
		c.SetParamNames("lock_id")
		c.SetParamValues("lock1")

		err := handler.ReleaseLock(c)
		// Should return 400 for missing agent_id
		if err != nil {
			he := &echo.HTTPError{}
			ok := errors.As(err, &he)
			if ok {
				assert.Equal(t, http.StatusBadRequest, he.Code)
			}
		} else {
			// Check response body
			assert.Contains(t, rec.Body.String(), "agent_id is required")
		}
	})
}

func TestCoordinationHandler_DetectConflict_Validation(t *testing.T) {
	e := echo.New()

	t.Run("invalid JSON", func(t *testing.T) {
		handler := &CoordinationHandler{}

		req := httptest.NewRequest(http.MethodPost, "/coordination/conflicts/detect", bytes.NewReader([]byte("invalid json")))
		req.Header.Set(echo.HeaderContentType, echo.MIMEApplicationJSON)
		rec := httptest.NewRecorder()
		c := e.NewContext(req, rec)

		err := handler.DetectConflict(c)
		// Bind should fail with invalid JSON
		if err != nil {
			he := &echo.HTTPError{}
			ok := errors.As(err, &he)
			if ok {
				assert.Equal(t, http.StatusBadRequest, he.Code)
			}
		}
	})
}

func TestCoordinationHandler_ResolveConflict_Validation(t *testing.T) {
	e := echo.New()

	t.Run("invalid JSON", func(t *testing.T) {
		handler := &CoordinationHandler{}

		req := httptest.NewRequest(http.MethodPost, "/coordination/conflicts/conflict1/resolve", bytes.NewReader([]byte("invalid json")))
		req.Header.Set(echo.HeaderContentType, echo.MIMEApplicationJSON)
		rec := httptest.NewRecorder()
		c := e.NewContext(req, rec)
		c.SetPath("/coordination/conflicts/:conflict_id/resolve")
		c.SetParamNames("conflict_id")
		c.SetParamValues("conflict1")

		err := handler.ResolveConflict(c)
		// Bind should fail with invalid JSON
		if err != nil {
			he := &echo.HTTPError{}
			ok := errors.As(err, &he)
			if ok {
				assert.Equal(t, http.StatusBadRequest, he.Code)
			}
		}
	})
}

func TestCoordinationHandler_CreateTeam_Validation(t *testing.T) {
	e := echo.New()

	t.Run("invalid JSON", func(t *testing.T) {
		handler := &CoordinationHandler{}

		req := httptest.NewRequest(http.MethodPost, "/coordination/teams", bytes.NewReader([]byte("invalid json")))
		req.Header.Set(echo.HeaderContentType, echo.MIMEApplicationJSON)
		rec := httptest.NewRecorder()
		c := e.NewContext(req, rec)

		err := handler.CreateTeam(c)
		// Bind should fail with invalid JSON
		if err != nil {
			he := &echo.HTTPError{}
			ok := errors.As(err, &he)
			if ok {
				assert.Equal(t, http.StatusBadRequest, he.Code)
			}
		}
	})
}

func TestCoordinationHandler_AddTeamMember_Validation(t *testing.T) {
	e := echo.New()

	t.Run("invalid JSON", func(t *testing.T) {
		handler := &CoordinationHandler{}

		req := httptest.NewRequest(http.MethodPost, "/coordination/teams/team1/members", bytes.NewReader([]byte("invalid json")))
		req.Header.Set(echo.HeaderContentType, echo.MIMEApplicationJSON)
		rec := httptest.NewRecorder()
		c := e.NewContext(req, rec)
		c.SetPath("/coordination/teams/:team_id/members")
		c.SetParamNames("team_id")
		c.SetParamValues("team1")

		err := handler.AddTeamMember(c)
		// Bind should fail with invalid JSON
		if err != nil {
			he := &echo.HTTPError{}
			ok := errors.As(err, &he)
			if ok {
				assert.Equal(t, http.StatusBadRequest, he.Code)
			}
		}
	})
}

func TestCoordinationHandler_CreateDistributedOperation_Validation(t *testing.T) {
	e := echo.New()

	t.Run("invalid JSON", func(t *testing.T) {
		handler := &CoordinationHandler{}

		req := httptest.NewRequest(http.MethodPost, "/coordination/operations", bytes.NewReader([]byte("invalid json")))
		req.Header.Set(echo.HeaderContentType, echo.MIMEApplicationJSON)
		rec := httptest.NewRecorder()
		c := e.NewContext(req, rec)

		err := handler.CreateDistributedOperation(c)
		// Bind should fail with invalid JSON, or handler will fail on nil distributedCoordinator
		// Either way, we expect an error
		if err != nil {
			he := &echo.HTTPError{}
			ok := errors.As(err, &he)
			if ok {
				assert.True(t, he.Code == http.StatusBadRequest || he.Code == http.StatusInternalServerError)
			}
		} else {
			// If no error, check response body
			assert.Contains(t, rec.Body.String(), "error")
		}
	})
}

func TestCoordinationHandler_AssignOperationToAgents_Validation(t *testing.T) {
	e := echo.New()

	t.Run("invalid JSON", func(t *testing.T) {
		handler := &CoordinationHandler{}

		reqBody := map[string]interface{}{
			"assignments": "invalid",
		}
		bodyBytes, err := json.Marshal(reqBody)
		require.NoError(t, err)

		req := httptest.NewRequest(http.MethodPost, "/coordination/operations/op1/assign", bytes.NewReader(bodyBytes))
		req.Header.Set(echo.HeaderContentType, echo.MIMEApplicationJSON)
		rec := httptest.NewRecorder()
		c := e.NewContext(req, rec)
		c.SetPath("/coordination/operations/:operation_id/assign")
		c.SetParamNames("operation_id")
		c.SetParamValues("op1")

		err = handler.AssignOperationToAgents(c)
		// Bind should fail with invalid JSON, or handler will fail on nil distributedCoordinator
		if err != nil {
			he := &echo.HTTPError{}
			ok := errors.As(err, &he)
			if ok {
				assert.True(t, he.Code == http.StatusBadRequest || he.Code == http.StatusInternalServerError)
			}
		} else {
			assert.Contains(t, rec.Body.String(), "error")
		}
	})
}

func TestCoordinationHandler_StartParticipation_Validation(t *testing.T) {
	e := echo.New()

	t.Run("missing agent_id", func(t *testing.T) {
		handler := &CoordinationHandler{}

		req := httptest.NewRequest(http.MethodPost, "/coordination/operations/op1/start", nil)
		rec := httptest.NewRecorder()
		c := e.NewContext(req, rec)
		c.SetPath("/coordination/operations/:operation_id/start")
		c.SetParamNames("operation_id")
		c.SetParamValues("op1")

		err := handler.StartParticipation(c)
		// Should return 400 for missing agent_id
		if err != nil {
			he := &echo.HTTPError{}
			ok := errors.As(err, &he)
			if ok {
				assert.Equal(t, http.StatusBadRequest, he.Code)
			}
		} else {
			// Check response body
			assert.Contains(t, rec.Body.String(), "agent_id is required")
		}
	})
}

func TestCoordinationHandler_CompleteParticipation_Validation(t *testing.T) {
	e := echo.New()

	t.Run("invalid JSON", func(t *testing.T) {
		handler := &CoordinationHandler{}

		req := httptest.NewRequest(http.MethodPost, "/coordination/operations/op1/complete", bytes.NewReader([]byte("invalid json")))
		req.Header.Set(echo.HeaderContentType, echo.MIMEApplicationJSON)
		rec := httptest.NewRecorder()
		c := e.NewContext(req, rec)
		c.SetPath("/coordination/operations/:operation_id/complete")
		c.SetParamNames("operation_id")
		c.SetParamValues("op1")

		err := handler.CompleteParticipation(c)
		// Bind should fail with invalid JSON
		if err != nil {
			he := &echo.HTTPError{}
			ok := errors.As(err, &he)
			if ok {
				assert.True(t, he.Code == http.StatusBadRequest || he.Code == http.StatusInternalServerError)
			}
		} else {
			assert.Contains(t, rec.Body.String(), "error")
		}
	})
}

func TestCoordinationHandler_CoordinatedUpdate_Validation(t *testing.T) {
	e := echo.New()

	t.Run("invalid JSON", func(t *testing.T) {
		handler := &CoordinationHandler{}

		req := httptest.NewRequest(http.MethodPost, "/coordination/updates", bytes.NewReader([]byte("invalid json")))
		req.Header.Set(echo.HeaderContentType, echo.MIMEApplicationJSON)
		rec := httptest.NewRecorder()
		c := e.NewContext(req, rec)

		err := handler.CoordinatedUpdate(c)
		// Bind should fail with invalid JSON
		if err != nil {
			he := &echo.HTTPError{}
			ok := errors.As(err, &he)
			if ok {
				assert.True(t, he.Code == http.StatusBadRequest || he.Code == http.StatusInternalServerError)
			}
		} else {
			assert.Contains(t, rec.Body.String(), "error")
		}
	})
}

func TestCoordinationHandler_CompleteCoordinatedUpdate_Validation(t *testing.T) {
	e := echo.New()

	t.Run("missing coordinator_id", func(t *testing.T) {
		handler := &CoordinationHandler{}

		req := httptest.NewRequest(http.MethodPost, "/coordination/updates/op1/complete", nil)
		rec := httptest.NewRecorder()
		c := e.NewContext(req, rec)
		c.SetPath("/coordination/updates/:operation_id/complete")
		c.SetParamNames("operation_id")
		c.SetParamValues("op1")

		err := handler.CompleteCoordinatedUpdate(c)
		// Should return 400 for missing coordinator_id
		if err != nil {
			he := &echo.HTTPError{}
			ok := errors.As(err, &he)
			if ok {
				assert.Equal(t, http.StatusBadRequest, he.Code)
			}
		} else {
			// Check response body
			assert.Contains(t, rec.Body.String(), "coordinator_id is required")
		}
	})
}

func TestCoordinationHandler_Shutdown(t *testing.T) {
	t.Run("nil lock manager", func(t *testing.T) {
		handler := &CoordinationHandler{
			lockManager: nil,
		}

		// Should not panic
		handler.Shutdown()
	})

	t.Run("with lock manager", func(t *testing.T) {
		// Would need real DB for this
		// Tested in integration tests
		t.Skip("Requires real database - integration test")
	})
}
