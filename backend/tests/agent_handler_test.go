package tests

import (
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"

	"github.com/labstack/echo/v4"
	"github.com/stretchr/testify/assert"

	"github.com/kooshapari/tracertm-backend/internal/handlers"
	"github.com/kooshapari/tracertm-backend/internal/models"
)

func TestCreateAgent(t *testing.T) {
	db := setupTestDB(t)
	handler := handlers.NewAgentHandler(db)

	e := echo.New()
	agentJSON := `{
		"project_id": "project-123",
		"name": "Code Analyzer",
		"status": "active"
	}`

	req := httptest.NewRequest(http.MethodPost, "/api/v1/agents", strings.NewReader(agentJSON))
	req.Header.Set(echo.HeaderContentType, echo.MIMEApplicationJSON)
	rec := httptest.NewRecorder()
	c := e.NewContext(req, rec)

	err := handler.CreateAgent(c)
	assert.NoError(t, err)
	assert.Equal(t, http.StatusCreated, rec.Code)

	var agent models.Agent
	err = json.Unmarshal(rec.Body.Bytes(), &agent)
	assert.NoError(t, err)
	assert.NotEmpty(t, agent.ID)
	assert.Equal(t, "project-123", agent.ProjectID)
	assert.Equal(t, "Code Analyzer", agent.Name)
	assert.Equal(t, "active", agent.Status)
}

func TestCreateAgentInvalidJSON(t *testing.T) {
	db := setupTestDB(t)
	handler := handlers.NewAgentHandler(db)

	e := echo.New()
	req := httptest.NewRequest(http.MethodPost, "/api/v1/agents", strings.NewReader("{bad json}"))
	req.Header.Set(echo.HeaderContentType, echo.MIMEApplicationJSON)
	rec := httptest.NewRecorder()
	c := e.NewContext(req, rec)

	err := handler.CreateAgent(c)
	assert.NoError(t, err)
	assert.Equal(t, http.StatusBadRequest, rec.Code)
}

func TestListAgents(t *testing.T) {
	db := setupTestDB(t)
	handler := handlers.NewAgentHandler(db)

	// Create test agents
	agents := []models.Agent{
		{ProjectID: "project-1", Name: "Agent 1", Status: "active"},
		{ProjectID: "project-1", Name: "Agent 2", Status: "idle"},
		{ProjectID: "project-2", Name: "Agent 3", Status: "active"},
	}
	for _, agent := range agents {
		db.Create(&agent)
	}

	e := echo.New()
	req := httptest.NewRequest(http.MethodGet, "/api/v1/agents", nil)
	rec := httptest.NewRecorder()
	c := e.NewContext(req, rec)

	err := handler.ListAgents(c)
	assert.NoError(t, err)
	assert.Equal(t, http.StatusOK, rec.Code)

	var result []models.Agent
	err = json.Unmarshal(rec.Body.Bytes(), &result)
	assert.NoError(t, err)
	assert.Len(t, result, 3)
}

func TestListAgentsFilteredByProject(t *testing.T) {
	db := setupTestDB(t)
	handler := handlers.NewAgentHandler(db)

	// Create test agents
	agents := []models.Agent{
		{ProjectID: "project-1", Name: "Agent 1", Status: "active"},
		{ProjectID: "project-1", Name: "Agent 2", Status: "idle"},
		{ProjectID: "project-2", Name: "Agent 3", Status: "active"},
	}
	for _, agent := range agents {
		db.Create(&agent)
	}

	e := echo.New()
	req := httptest.NewRequest(http.MethodGet, "/api/v1/agents?project_id=project-1", nil)
	rec := httptest.NewRecorder()
	c := e.NewContext(req, rec)

	err := handler.ListAgents(c)
	assert.NoError(t, err)
	assert.Equal(t, http.StatusOK, rec.Code)

	var result []models.Agent
	err = json.Unmarshal(rec.Body.Bytes(), &result)
	assert.NoError(t, err)
	assert.Len(t, result, 2)
	for _, agent := range result {
		assert.Equal(t, "project-1", agent.ProjectID)
	}
}

func TestGetAgent(t *testing.T) {
	db := setupTestDB(t)
	handler := handlers.NewAgentHandler(db)

	// Create test agent
	agent := models.Agent{
		ID:        "agent-123",
		ProjectID: "project-1",
		Name:      "Test Agent",
		Status:    "active",
	}
	db.Create(&agent)

	e := echo.New()
	req := httptest.NewRequest(http.MethodGet, "/api/v1/agents/agent-123", nil)
	rec := httptest.NewRecorder()
	c := e.NewContext(req, rec)
	c.SetParamNames("id")
	c.SetParamValues("agent-123")

	err := handler.GetAgent(c)
	assert.NoError(t, err)
	assert.Equal(t, http.StatusOK, rec.Code)

	var result models.Agent
	err = json.Unmarshal(rec.Body.Bytes(), &result)
	assert.NoError(t, err)
	assert.Equal(t, "agent-123", result.ID)
	assert.Equal(t, "Test Agent", result.Name)
}

func TestGetAgentNotFound(t *testing.T) {
	db := setupTestDB(t)
	handler := handlers.NewAgentHandler(db)

	e := echo.New()
	req := httptest.NewRequest(http.MethodGet, "/api/v1/agents/nonexistent", nil)
	rec := httptest.NewRecorder()
	c := e.NewContext(req, rec)
	c.SetParamNames("id")
	c.SetParamValues("nonexistent")

	err := handler.GetAgent(c)
	assert.NoError(t, err)
	assert.Equal(t, http.StatusNotFound, rec.Code)
}

func TestUpdateAgent(t *testing.T) {
	db := setupTestDB(t)
	handler := handlers.NewAgentHandler(db)

	// Create test agent
	agent := models.Agent{
		ID:        "agent-123",
		ProjectID: "project-1",
		Name:      "Original Agent",
		Status:    "idle",
	}
	db.Create(&agent)

	e := echo.New()
	updateJSON := `{"name": "Updated Agent", "status": "active"}`
	req := httptest.NewRequest(http.MethodPut, "/api/v1/agents/agent-123", strings.NewReader(updateJSON))
	req.Header.Set(echo.HeaderContentType, echo.MIMEApplicationJSON)
	rec := httptest.NewRecorder()
	c := e.NewContext(req, rec)
	c.SetParamNames("id")
	c.SetParamValues("agent-123")

	err := handler.UpdateAgent(c)
	assert.NoError(t, err)
	assert.Equal(t, http.StatusOK, rec.Code)

	// Verify the update
	var updated models.Agent
	db.First(&updated, "id = ?", "agent-123")
	assert.Equal(t, "Updated Agent", updated.Name)
	assert.Equal(t, "active", updated.Status)
}

func TestDeleteAgent(t *testing.T) {
	db := setupTestDB(t)
	handler := handlers.NewAgentHandler(db)

	// Create test agent
	agent := models.Agent{
		ID:        "agent-123",
		ProjectID: "project-1",
		Name:      "To Delete",
		Status:    "idle",
	}
	db.Create(&agent)

	e := echo.New()
	req := httptest.NewRequest(http.MethodDelete, "/api/v1/agents/agent-123", nil)
	rec := httptest.NewRecorder()
	c := e.NewContext(req, rec)
	c.SetParamNames("id")
	c.SetParamValues("agent-123")

	err := handler.DeleteAgent(c)
	assert.NoError(t, err)
	assert.Equal(t, http.StatusOK, rec.Code)

	// Verify the deletion
	var count int64
	db.Model(&models.Agent{}).Where("id = ?", "agent-123").Count(&count)
	assert.Equal(t, int64(0), count)
}
