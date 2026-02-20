//go:build !integration && !e2e
// +build !integration,!e2e

package handlers

import (
	"bytes"
	"context"
	"encoding/json"
	"errors"
	"net/http"
	"net/http/httptest"
	"testing"
	"time"

	"github.com/google/uuid"
	"github.com/labstack/echo/v4"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"

	"github.com/kooshapari/tracertm-backend/internal/db"
	"github.com/kooshapari/tracertm-backend/internal/models"
	"github.com/kooshapari/tracertm-backend/internal/services"
)

// setupProjectHandler creates a test handler with mocked dependencies
func setupProjectHandler(_ *testing.T, mockService *services.MockProjectService) *ProjectHandler {
	if mockService == nil {
		mockService = &services.MockProjectService{}
	}
	return &ProjectHandler{
		projectService:      mockService,
		cache:               nil,
		publisher:           nil,
		realtimeBroadcaster: &MockRealtimeBroadcaster{},
		authProvider:        nil,
		binder:              &TestBinder{},
	}
}

// TestGetProject_Validation tests GetProject ID validation with table-driven approach
func TestGetProject_Validation(t *testing.T) {
	tests := []struct {
		name           string
		id             string
		expectedStatus int
		shouldContain  string
	}{
		{
			name:           "invalid_id_format",
			id:             "not-uuid",
			expectedStatus: http.StatusBadRequest,
			shouldContain:  "Invalid project ID",
		},
		{
			name:           "empty_id",
			id:             "",
			expectedStatus: http.StatusBadRequest,
			shouldContain:  "Invalid project ID",
		},
		{
			name:           "malformed_id",
			id:             "123-456",
			expectedStatus: http.StatusBadRequest,
			shouldContain:  "Invalid project ID",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(_ *testing.T) {
			mockService := &services.MockProjectService{}
			handler := setupProjectHandler(t, mockService)

			e := echo.New()
			req := httptest.NewRequest(http.MethodGet, "/api/v1/projects/:id", nil)
			rec := httptest.NewRecorder()
			c := e.NewContext(req, rec)
			c.SetPath("/api/v1/projects/:id")
			c.SetParamNames("id")
			c.SetParamValues(tt.id)

			err := handler.GetProject(c)
			require.NoError(t, err)

			assert.Equal(t, tt.expectedStatus, rec.Code)
			var resp map[string]interface{}
			require.NoError(t, json.Unmarshal(rec.Body.Bytes(), &resp))
			if tt.shouldContain != "" {
				typed89, ok := resp["error"].(string)
				require.True(t, ok)
				assert.Contains(t, typed89, tt.shouldContain)
			}
		})
	}
}

// TestGetProject_Success tests successful project retrieval
func TestGetProject_Success(t *testing.T) {
	projectID := uuid.New().String()
	now := time.Now().UTC()

	mockProject := &models.Project{
		ID:          projectID,
		Name:        "Test Project",
		Description: "Test Description",
		CreatedAt:   now,
		UpdatedAt:   now,
	}

	mockService := &services.MockProjectService{
		OnGetProject: func(_ context.Context, id string) (*models.Project, error) {
			assert.Equal(t, projectID, id)
			return mockProject, nil
		},
	}

	handler := setupProjectHandler(t, mockService)

	e := echo.New()
	req := httptest.NewRequest(http.MethodGet, "/api/v1/projects/"+projectID, nil)
	rec := httptest.NewRecorder()
	c := e.NewContext(req, rec)
	c.SetPath("/api/v1/projects/:id")
	c.SetParamNames("id")
	c.SetParamValues(projectID)

	err := handler.GetProject(c)
	require.NoError(t, err)

	assert.Equal(t, http.StatusOK, rec.Code)
	var resp db.Project
	err = json.Unmarshal(rec.Body.Bytes(), &resp)
	require.NoError(t, err)
	assert.True(t, resp.ID.Valid)
	assert.Equal(t, "Test Project", resp.Name)
}

// TestGetProject_NotFound tests when project is not found
func TestGetProject_NotFound(t *testing.T) {
	projectID := uuid.New().String()

	mockService := &services.MockProjectService{
		OnGetProject: func(_ context.Context, _ string) (*models.Project, error) {
			return nil, errors.New("project not found")
		},
	}

	handler := setupProjectHandler(t, mockService)

	e := echo.New()
	req := httptest.NewRequest(http.MethodGet, "/api/v1/projects/"+projectID, nil)
	rec := httptest.NewRecorder()
	c := e.NewContext(req, rec)
	c.SetPath("/api/v1/projects/:id")
	c.SetParamNames("id")
	c.SetParamValues(projectID)

	err := handler.GetProject(c)
	require.NoError(t, err)

	assert.Equal(t, http.StatusNotFound, rec.Code)
}

// TestListProjects_Success tests successful project listing
func TestListProjects_Success(t *testing.T) {
	now := time.Now().UTC()
	mockProjects := []*models.Project{
		{
			ID:          uuid.New().String(),
			Name:        "Project 1",
			Description: "Description 1",
			CreatedAt:   now,
			UpdatedAt:   now,
		},
		{
			ID:          uuid.New().String(),
			Name:        "Project 2",
			Description: "Description 2",
			CreatedAt:   now,
			UpdatedAt:   now,
		},
	}

	mockService := &services.MockProjectService{
		OnListProjects: func(_ context.Context) ([]*models.Project, error) {
			return mockProjects, nil
		},
	}

	handler := setupProjectHandler(t, mockService)

	e := echo.New()
	req := httptest.NewRequest(http.MethodGet, "/api/v1/projects", nil)
	rec := httptest.NewRecorder()
	c := e.NewContext(req, rec)

	err := handler.ListProjects(c)
	require.NoError(t, err)

	assert.Equal(t, http.StatusOK, rec.Code)
	var resp []*db.Project
	err = json.Unmarshal(rec.Body.Bytes(), &resp)
	require.NoError(t, err)
	assert.Len(t, resp, 2)
	assert.Equal(t, "Project 1", resp[0].Name)
	assert.Equal(t, "Project 2", resp[1].Name)
}

// TestListProjects_EmptyList tests when no projects exist
func TestListProjects_EmptyList(t *testing.T) {
	mockService := &services.MockProjectService{
		OnListProjects: func(_ context.Context) ([]*models.Project, error) {
			return []*models.Project{}, nil
		},
	}

	handler := setupProjectHandler(t, mockService)

	e := echo.New()
	req := httptest.NewRequest(http.MethodGet, "/api/v1/projects", nil)
	rec := httptest.NewRecorder()
	c := e.NewContext(req, rec)

	err := handler.ListProjects(c)
	require.NoError(t, err)

	assert.Equal(t, http.StatusOK, rec.Code)
	var resp []*models.Project
	err = json.Unmarshal(rec.Body.Bytes(), &resp)
	require.NoError(t, err)
	assert.Empty(t, resp)
}

// TestListProjects_Error tests error handling in project listing
func TestListProjects_Error(t *testing.T) {
	mockService := &services.MockProjectService{
		OnListProjects: func(_ context.Context) ([]*models.Project, error) {
			return nil, errors.New("database error")
		},
	}

	handler := setupProjectHandler(t, mockService)

	e := echo.New()
	req := httptest.NewRequest(http.MethodGet, "/api/v1/projects", nil)
	rec := httptest.NewRecorder()
	c := e.NewContext(req, rec)

	err := handler.ListProjects(c)
	require.NoError(t, err)

	assert.Equal(t, http.StatusInternalServerError, rec.Code)
}

// TestCreateProject_Success tests successful project creation
func TestCreateProject_Success(t *testing.T) {
	mockService := &services.MockProjectService{
		OnCreateProject: func(_ context.Context, project *models.Project) error {
			project.ID = uuid.New().String()
			project.CreatedAt = time.Now().UTC()
			project.UpdatedAt = time.Now().UTC()
			return nil
		},
	}

	handler := setupProjectHandler(t, mockService)

	body := map[string]interface{}{
		"name":        "New Project",
		"description": "New Description",
	}
	bodyBytes, err := json.Marshal(body)
	require.NoError(t, err)

	e := echo.New()
	req := httptest.NewRequest(http.MethodPost, "/api/v1/projects", bytes.NewReader(bodyBytes))
	req.Header.Set("Content-Type", "application/json")
	rec := httptest.NewRecorder()
	c := e.NewContext(req, rec)

	err = handler.CreateProject(c)
	require.NoError(t, err)

	assert.Equal(t, http.StatusCreated, rec.Code)
	var resp db.Project
	err = json.Unmarshal(rec.Body.Bytes(), &resp)
	require.NoError(t, err)
	assert.True(t, resp.ID.Valid)
	assert.Equal(t, "New Project", resp.Name)
}

// TestCreateProject_ValidationError tests validation errors
func TestCreateProject_ValidationError(t *testing.T) {
	mockService := &services.MockProjectService{}
	handler := setupProjectHandler(t, mockService)

	body := map[string]interface{}{
		"name": "", // Empty name should fail validation
	}
	bodyBytes, err := json.Marshal(body)
	require.NoError(t, err)

	e := echo.New()
	req := httptest.NewRequest(http.MethodPost, "/api/v1/projects", bytes.NewReader(bodyBytes))
	req.Header.Set("Content-Type", "application/json")
	rec := httptest.NewRecorder()
	c := e.NewContext(req, rec)

	err = handler.CreateProject(c)
	require.NoError(t, err)

	assert.Equal(t, http.StatusBadRequest, rec.Code)
}

// TestUpdateProject_Validation tests UpdateProject ID validation
func TestUpdateProject_Validation(t *testing.T) {
	tests := []struct {
		name           string
		id             string
		expectedStatus int
		shouldContain  string
	}{
		{
			name:           "invalid_id_format",
			id:             "not-uuid",
			expectedStatus: http.StatusBadRequest,
			shouldContain:  "Invalid project ID",
		},
		{
			name:           "empty_id",
			id:             "",
			expectedStatus: http.StatusBadRequest,
			shouldContain:  "Invalid project ID",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(_ *testing.T) {
			mockService := &services.MockProjectService{}
			handler := setupProjectHandler(t, mockService)

			body := map[string]interface{}{"name": "Updated"}
			bodyBytes, err := json.Marshal(body)
			require.NoError(t, err)

			e := echo.New()
			req := httptest.NewRequest(http.MethodPut, "/api/v1/projects/:id", bytes.NewReader(bodyBytes))
			req.Header.Set("Content-Type", "application/json")
			rec := httptest.NewRecorder()
			c := e.NewContext(req, rec)
			c.SetPath("/api/v1/projects/:id")
			c.SetParamNames("id")
			c.SetParamValues(tt.id)

			err = handler.UpdateProject(c)
			require.NoError(t, err)

			assert.Equal(t, tt.expectedStatus, rec.Code)
		})
	}
}

// TestUpdateProject_Success tests successful project update
func TestUpdateProject_Success(t *testing.T) {
	projectID := uuid.New().String()

	mockService := &services.MockProjectService{
		OnUpdateProject: func(_ context.Context, project *models.Project) error {
			assert.Equal(t, projectID, project.ID)
			project.UpdatedAt = time.Now().UTC()
			return nil
		},
	}

	handler := setupProjectHandler(t, mockService)

	body := map[string]interface{}{
		"name":        "Updated Project",
		"description": "Updated Description",
	}
	bodyBytes, err := json.Marshal(body)
	require.NoError(t, err)

	e := echo.New()
	req := httptest.NewRequest(http.MethodPut, "/api/v1/projects/"+projectID, bytes.NewReader(bodyBytes))
	req.Header.Set("Content-Type", "application/json")
	rec := httptest.NewRecorder()
	c := e.NewContext(req, rec)
	c.SetPath("/api/v1/projects/:id")
	c.SetParamNames("id")
	c.SetParamValues(projectID)

	err = handler.UpdateProject(c)
	require.NoError(t, err)

	assert.Equal(t, http.StatusOK, rec.Code)
}

// TestDeleteProject_Validation tests DeleteProject ID validation
func TestDeleteProject_Validation(t *testing.T) {
	tests := []struct {
		name           string
		id             string
		expectedStatus int
		shouldContain  string
	}{
		{
			name:           "invalid_id_format",
			id:             "not-uuid",
			expectedStatus: http.StatusBadRequest,
			shouldContain:  "Invalid project ID",
		},
		{
			name:           "empty_id",
			id:             "",
			expectedStatus: http.StatusBadRequest,
			shouldContain:  "Invalid project ID",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(_ *testing.T) {
			mockService := &services.MockProjectService{}
			handler := setupProjectHandler(t, mockService)

			e := echo.New()
			req := httptest.NewRequest(http.MethodDelete, "/api/v1/projects/:id", nil)
			rec := httptest.NewRecorder()
			c := e.NewContext(req, rec)
			c.SetPath("/api/v1/projects/:id")
			c.SetParamNames("id")
			c.SetParamValues(tt.id)

			err := handler.DeleteProject(c)
			require.NoError(t, err)

			assert.Equal(t, tt.expectedStatus, rec.Code)
		})
	}
}

// TestDeleteProject_Success tests successful project deletion
func TestDeleteProject_Success(t *testing.T) {
	projectID := uuid.New().String()

	mockService := &services.MockProjectService{
		OnDeleteProject: func(_ context.Context, id string) error {
			assert.Equal(t, projectID, id)
			return nil
		},
	}

	handler := setupProjectHandler(t, mockService)

	e := echo.New()
	req := httptest.NewRequest(http.MethodDelete, "/api/v1/projects/"+projectID, nil)
	rec := httptest.NewRecorder()
	c := e.NewContext(req, rec)
	c.SetPath("/api/v1/projects/:id")
	c.SetParamNames("id")
	c.SetParamValues(projectID)

	err := handler.DeleteProject(c)
	require.NoError(t, err)

	assert.Equal(t, http.StatusNoContent, rec.Code)
}

// TestDeleteProject_NotFound tests deletion of non-existent project
func TestDeleteProject_NotFound(t *testing.T) {
	projectID := uuid.New().String()

	mockService := &services.MockProjectService{
		OnDeleteProject: func(_ context.Context, _ string) error {
			return errors.New("project not found")
		},
	}

	handler := setupProjectHandler(t, mockService)

	e := echo.New()
	req := httptest.NewRequest(http.MethodDelete, "/api/v1/projects/"+projectID, nil)
	rec := httptest.NewRecorder()
	c := e.NewContext(req, rec)
	c.SetPath("/api/v1/projects/:id")
	c.SetParamNames("id")
	c.SetParamValues(projectID)

	err := handler.DeleteProject(c)
	require.NoError(t, err)

	assert.Equal(t, http.StatusInternalServerError, rec.Code)
}

// TestProjectHandler_StructureAndDependencies tests handler initialization
func TestProjectHandler_StructureAndDependencies(t *testing.T) {
	mockService := &services.MockProjectService{}
	handler := setupProjectHandler(t, mockService)

	// Verify handler structure
	assert.NotNil(t, handler.projectService)
	assert.NotNil(t, handler.binder)
	assert.IsType(t, &TestBinder{}, handler.binder)
	assert.NotNil(t, handler.realtimeBroadcaster)
}

// TestProjectCacheKeyGeneration tests helper methods for project cache keys
func TestProjectCacheKeyGeneration(t *testing.T) {
	mockService := &services.MockProjectService{}
	handler := setupProjectHandler(t, mockService)

	tests := []struct {
		name      string
		projectID string
		expected  string
	}{
		{
			name:      "valid_uuid",
			projectID: uuid.New().String(),
			expected:  "project:",
		},
		{
			name:      "empty_id",
			projectID: "",
			expected:  "project:",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(_ *testing.T) {
			key := handler.getCacheKey(tt.projectID)
			assert.Contains(t, key, tt.expected)
		})
	}
}

// TestProjectService_CreateError tests error handling during creation
func TestProjectService_CreateError(t *testing.T) {
	mockService := &services.MockProjectService{
		OnCreateProject: func(_ context.Context, _ *models.Project) error {
			return errors.New("database constraint violation")
		},
	}

	handler := setupProjectHandler(t, mockService)

	body := map[string]interface{}{
		"name":        "Test Project",
		"description": "Test Description",
	}
	bodyBytes, err := json.Marshal(body)
	require.NoError(t, err)

	e := echo.New()
	req := httptest.NewRequest(http.MethodPost, "/api/v1/projects", bytes.NewReader(bodyBytes))
	req.Header.Set("Content-Type", "application/json")
	rec := httptest.NewRecorder()
	c := e.NewContext(req, rec)

	err = handler.CreateProject(c)
	require.NoError(t, err)

	assert.Equal(t, http.StatusInternalServerError, rec.Code)
}

// TestProjectService_UpdateError tests error handling during update
func TestProjectService_UpdateError(t *testing.T) {
	projectID := uuid.New().String()

	mockService := &services.MockProjectService{
		OnUpdateProject: func(_ context.Context, _ *models.Project) error {
			return errors.New("concurrent modification error")
		},
	}

	handler := setupProjectHandler(t, mockService)

	body := map[string]interface{}{
		"name":        "Updated Project",
		"description": "Updated Description",
	}
	bodyBytes, err := json.Marshal(body)
	require.NoError(t, err)

	e := echo.New()
	req := httptest.NewRequest(http.MethodPut, "/api/v1/projects/"+projectID, bytes.NewReader(bodyBytes))
	req.Header.Set("Content-Type", "application/json")
	rec := httptest.NewRecorder()
	c := e.NewContext(req, rec)
	c.SetPath("/api/v1/projects/:id")
	c.SetParamNames("id")
	c.SetParamValues(projectID)

	err = handler.UpdateProject(c)
	require.NoError(t, err)

	assert.Equal(t, http.StatusInternalServerError, rec.Code)
}
