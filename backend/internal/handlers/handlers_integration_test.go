//go:build !integration && !e2e
// +build !integration,!e2e

package handlers

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/google/uuid"
	"github.com/jackc/pgx/v5/pgtype"
	"github.com/labstack/echo/v4"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"

	"github.com/kooshapari/tracertm-backend/internal/db"
	"github.com/kooshapari/tracertm-backend/internal/services"
)

// TestHelpers

// setupHandler creates a handler with mocked dependencies
func setupHandler(_ *MockQueries) *ProjectHandler {
	// Create a mock service - tests will set up the behavior they need
	mockService := &services.MockProjectService{}
	return &ProjectHandler{
		projectService:      mockService,
		cache:               nil,
		publisher:           nil,
		realtimeBroadcaster: &MockRealtimeBroadcaster{},
		authProvider:        nil,
		binder:              &TestBinder{},
	}
}

// setupItemHandler creates an item handler with mocked dependencies
func setupItemHandlerMock(_ *MockQueries) *ItemHandler {
	// Create a mock service - tests will set up the behavior they need
	mockService := &services.MockItemService{}
	return &ItemHandler{
		itemService:         mockService,
		cache:               nil,
		publisher:           nil,
		realtimeBroadcaster: &MockRealtimeBroadcaster{},
		authProvider:        nil,
		binder:              &TestBinder{},
	}
}

// setupLinkHandler creates a link handler with mocked dependencies
func setupLinkHandlerMock(_ *MockQueries) *LinkHandler {
	// Create a mock service - tests will set up the behavior they need
	mockService := &services.MockLinkService{}
	return &LinkHandler{
		linkService: mockService,
		itemService: nil,
		binder:      &TestBinder{},
	}
}

// makeRequest creates an echo context for testing
func makeRequest(method, path string, body interface{}) (echo.Context, *httptest.ResponseRecorder, error) {
	e := echo.New()
	var bodyReader *bytes.Reader

	if body != nil {
		bodyBytes, err := json.Marshal(body)
		if err != nil {
			return nil, nil, err
		}
		bodyReader = bytes.NewReader(bodyBytes)
	} else {
		bodyReader = bytes.NewReader([]byte{})
	}

	req := httptest.NewRequest(method, path, bodyReader)
	if body != nil {
		req.Header.Set("Content-Type", "application/json")
	}
	rec := httptest.NewRecorder()
	c := e.NewContext(req, rec)

	return c, rec, nil
}

// setParamValue sets path parameters for echo context
func setParamValue(c echo.Context, paramName, paramValue string) {
	c.SetPath("/api/v1/:id")
	c.SetParamNames(paramName)
	c.SetParamValues(paramValue)
}

// ============================================================================
// PROJECT HANDLER TESTS
// ============================================================================

// TestProjectHandler_CreateProject_Success tests successful project creation
func TestProjectHandler_CreateProject_Success(t *testing.T) {
	mockQueries := NewMockQueries()
	handler := setupHandler(mockQueries)

	c, rec, err := makeRequest(http.MethodPost, "/api/v1/projects", map[string]interface{}{
		"name":        "Test Project",
		"description": "A test project",
		"metadata":    map[string]interface{}{"key": "value"},
	})
	require.NoError(t, err)

	err = handler.CreateProject(c)
	require.NoError(t, err)

	assert.Equal(t, http.StatusCreated, rec.Code)

	var resp db.Project
	err = json.Unmarshal(rec.Body.Bytes(), &resp)
	require.NoError(t, err)

	assert.Equal(t, "Test Project", resp.Name)
	assert.Equal(t, "A test project", resp.Description.String)
}

// TestProjectHandler_CreateProject_EmptyName tests project creation with empty name
func TestProjectHandler_CreateProject_EmptyName(t *testing.T) {
	mockQueries := NewMockQueries()
	handler := setupHandler(mockQueries)

	c, rec, err := makeRequest(http.MethodPost, "/api/v1/projects", map[string]interface{}{
		"name":        "",
		"description": "A test project",
	})
	require.NoError(t, err)

	err = handler.CreateProject(c)
	require.NoError(t, err)

	assert.Equal(t, http.StatusBadRequest, rec.Code)
}

// TestProjectHandler_CreateProject_NilMetadata tests project creation with nil metadata
func TestProjectHandler_CreateProject_NilMetadata(t *testing.T) {
	mockQueries := NewMockQueries()
	handler := setupHandler(mockQueries)

	c, rec, err := makeRequest(http.MethodPost, "/api/v1/projects", map[string]interface{}{
		"name":        "Test",
		"description": "Test",
		"metadata":    nil,
	})
	require.NoError(t, err)

	err = handler.CreateProject(c)
	require.NoError(t, err)

	assert.Equal(t, http.StatusCreated, rec.Code)
}

// TestProjectHandler_GetProject_Success tests successful project retrieval
func TestProjectHandler_GetProject_Success(t *testing.T) {
	t.Skip("Requires integration with real service layer - use project_handler_test.go for unit tests")
	mockQueries := NewMockQueries()
	handler := setupHandler(mockQueries)

	// Create a project first
	project, err := mockQueries.CreateProject(context.Background(), db.CreateProjectParams{
		Name:        "Test Project",
		Description: pgtype.Text{String: "Description", Valid: true},
		Metadata:    []byte("{}"),
	})
	require.NoError(t, err)

	// Create echo context and set params
	e := echo.New()
	req := httptest.NewRequest(http.MethodGet, "/api/v1/projects/:id", nil)
	rec := httptest.NewRecorder()
	c := e.NewContext(req, rec)
	c.SetPath("/api/v1/projects/:id")
	setParamValue(c, "id", project.ID.String())

	err = handler.GetProject(c)
	require.NoError(t, err)

	assert.Equal(t, http.StatusOK, rec.Code)

	var resp db.Project
	err = json.Unmarshal(rec.Body.Bytes(), &resp)
	require.NoError(t, err)

	assert.Equal(t, project.ID, resp.ID)
	assert.Equal(t, "Test Project", resp.Name)
}

// TestProjectHandler_GetProject_NotFound tests getting non-existent project
func TestProjectHandler_GetProject_NotFound(t *testing.T) {
	t.Skip("Requires integration with real service layer - use project_handler_test.go for unit tests")
	mockQueries := NewMockQueries()
	handler := setupHandler(mockQueries)

	e := echo.New()
	req := httptest.NewRequest(http.MethodGet, "/api/v1/projects/:id", nil)
	rec := httptest.NewRecorder()
	c := e.NewContext(req, rec)
	c.SetPath("/api/v1/projects/:id")
	setParamValue(c, "id", uuid.New().String())

	err := handler.GetProject(c)
	require.NoError(t, err)

	assert.Equal(t, http.StatusNotFound, rec.Code)

	var resp map[string]interface{}
	err = json.Unmarshal(rec.Body.Bytes(), &resp)
	require.NoError(t, err)
	typed218, ok := resp["error"].(string)
	require.True(t, ok)
	assert.Contains(t, typed218, "not found")
}

// TestProjectHandler_ListProjects_Success tests successful project listing
func TestProjectHandler_ListProjects_Success(t *testing.T) {
	t.Skip("Requires integration with real service layer - use project_handler_test.go for unit tests")
	mockQueries := NewMockQueries()
	handler := setupHandler(mockQueries)

	createProjects(t, mockQueries, 5)
	resp := listProjects(t, handler, "/api/v1/projects?limit=10&offset=0")
	assert.Len(t, resp, 5)
}

// TestProjectHandler_ListProjects_Pagination tests pagination in project listing
func TestProjectHandler_ListProjects_Pagination(t *testing.T) {
	t.Skip("Requires integration with real service layer - use project_handler_test.go for unit tests")
	mockQueries := NewMockQueries()
	handler := setupHandler(mockQueries)

	createProjects(t, mockQueries, 15)
	resp := listProjects(t, handler, "/api/v1/projects?limit=5&offset=5")
	assert.Len(t, resp, 5)
}

func createProjects(t *testing.T, mockQueries *MockQueries, count int) {
	t.Helper()

	for i := 0; i < count; i++ {
		_, err := mockQueries.CreateProject(context.Background(), db.CreateProjectParams{
			Name:        fmt.Sprintf("Project %d", i),
			Description: pgtype.Text{Valid: false},
			Metadata:    []byte("{}"),
		})
		require.NoError(t, err)
	}
}

func listProjects(t *testing.T, handler *ProjectHandler, url string) []db.Project {
	t.Helper()

	e := echo.New()
	req := httptest.NewRequest(http.MethodGet, url, nil)
	rec := httptest.NewRecorder()
	c := e.NewContext(req, rec)

	err := handler.ListProjects(c)
	require.NoError(t, err)

	assert.Equal(t, http.StatusOK, rec.Code)

	var resp []db.Project
	err = json.Unmarshal(rec.Body.Bytes(), &resp)
	require.NoError(t, err)

	return resp
}

// TestProjectHandler_UpdateProject_Success tests successful project update
func TestProjectHandler_UpdateProject_Success(t *testing.T) {
	t.Skip("Requires integration with real service layer - use project_handler_test.go for unit tests")
	mockQueries := NewMockQueries()
	handler := setupHandler(mockQueries)

	// Create a project first
	project, err := mockQueries.CreateProject(context.Background(), db.CreateProjectParams{
		Name:        "Original Name",
		Description: pgtype.Text{String: "Original Description", Valid: true},
		Metadata:    []byte("{}"),
	})
	require.NoError(t, err)

	// Update the project
	body := map[string]interface{}{
		"name":        "Updated Name",
		"description": "Updated Description",
		"metadata":    map[string]interface{}{"updated": true},
	}

	c, rec, err := makeRequest(http.MethodPut, "/api/v1/projects/:id", body)
	require.NoError(t, err)

	c.SetPath("/api/v1/projects/:id")
	setParamValue(c, "id", project.ID.String())

	err = handler.UpdateProject(c)
	require.NoError(t, err)

	assert.Equal(t, http.StatusOK, rec.Code)

	var resp db.Project
	err = json.Unmarshal(rec.Body.Bytes(), &resp)
	require.NoError(t, err)

	assert.Equal(t, "Updated Name", resp.Name)
	assert.Equal(t, "Updated Description", resp.Description.String)
}

// TestProjectHandler_DeleteProject_Success tests successful project deletion
func TestProjectHandler_DeleteProject_Success(t *testing.T) {
	t.Skip("Requires integration with real service layer - use project_handler_test.go for unit tests")
	mockQueries := NewMockQueries()
	handler := setupHandler(mockQueries)

	// Create a project first
	project, err := mockQueries.CreateProject(context.Background(), db.CreateProjectParams{
		Name:        "To Delete",
		Description: pgtype.Text{Valid: false},
		Metadata:    []byte("{}"),
	})
	require.NoError(t, err)

	// Delete the project
	e := echo.New()
	req := httptest.NewRequest(http.MethodDelete, "/api/v1/projects/:id", nil)
	rec := httptest.NewRecorder()
	c := e.NewContext(req, rec)
	c.SetPath("/api/v1/projects/:id")
	setParamValue(c, "id", project.ID.String())

	err = handler.DeleteProject(c)
	require.NoError(t, err)

	assert.Equal(t, http.StatusOK, rec.Code)

	// Verify deletion
	_, err = mockQueries.GetProject(context.Background(), project.ID)
	assert.Error(t, err)
}

// ============================================================================
// ITEM HANDLER TESTS
// ============================================================================

// TestItemHandler_CreateItem_Success tests successful item creation
func TestItemHandler_CreateItem_Success(t *testing.T) {
	mockQueries := NewMockQueries()
	itemHandler := setupItemHandlerMock(mockQueries)

	// Create a project first
	project, err := mockQueries.CreateProject(context.Background(), db.CreateProjectParams{
		Name:        "Test Project",
		Description: pgtype.Text{Valid: false},
		Metadata:    []byte("{}"),
	})
	require.NoError(t, err)

	// Create an item
	body := map[string]interface{}{
		"project_id":  project.ID.String(),
		"title":       "Test Item",
		"description": "A test item",
		"type":        "requirement",
		"status":      "open",
		"priority":    1,
	}

	c, rec, err := makeRequest(http.MethodPost, "/api/v1/items", body)
	require.NoError(t, err)

	err = itemHandler.CreateItem(c)
	require.NoError(t, err)

	assert.Equal(t, http.StatusCreated, rec.Code)

	var resp db.CreateItemRow
	err = json.Unmarshal(rec.Body.Bytes(), &resp)
	require.NoError(t, err)

	assert.Equal(t, "Test Item", resp.Title)
	assert.Equal(t, project.ID, resp.ProjectID)
}

// TestItemHandler_CreateItem_InvalidProjectID tests item creation with invalid project ID
func TestItemHandler_CreateItem_InvalidProjectID(t *testing.T) {
	mockQueries := NewMockQueries()
	itemHandler := setupItemHandlerMock(mockQueries)

	body := map[string]interface{}{
		"project_id":  "invalid-uuid",
		"title":       "Test Item",
		"description": "A test item",
		"type":        "requirement",
		"status":      "open",
	}

	c, rec, err := makeRequest(http.MethodPost, "/api/v1/items", body)
	require.NoError(t, err)

	err = itemHandler.CreateItem(c)
	require.NoError(t, err)

	assert.Equal(t, http.StatusBadRequest, rec.Code)
}

// TestItemHandler_GetItem_Success tests successful item retrieval
func TestItemHandler_GetItem_Success(t *testing.T) {
	t.Skip("Requires integration with real service layer - use item_handler_test.go for unit tests")
	mockQueries := NewMockQueries()
	itemHandler := setupItemHandlerMock(mockQueries)

	// Create project and item first
	project, err := mockQueries.CreateProject(context.Background(), db.CreateProjectParams{
		Name:        "Test Project",
		Description: pgtype.Text{Valid: false},
		Metadata:    []byte("{}"),
	})
	require.NoError(t, err)

	item, err := mockQueries.CreateItem(context.Background(), db.CreateItemParams{
		ProjectID:   project.ID,
		Title:       "Test Item",
		Description: pgtype.Text{Valid: false},
		Type:        "requirement",
		Status:      "open",
		Priority:    pgtype.Int4{Valid: false},
		Metadata:    []byte("{}"),
	})
	require.NoError(t, err)

	// Get the item
	e := echo.New()
	req := httptest.NewRequest(http.MethodGet, "/api/v1/items/:id", nil)
	rec := httptest.NewRecorder()
	c := e.NewContext(req, rec)
	c.SetPath("/api/v1/items/:id")
	setParamValue(c, "id", item.ID.String())

	err = itemHandler.GetItem(c)
	require.NoError(t, err)

	assert.Equal(t, http.StatusOK, rec.Code)

	var resp db.GetItemRow
	err = json.Unmarshal(rec.Body.Bytes(), &resp)
	require.NoError(t, err)

	assert.Equal(t, item.ID, resp.ID)
	assert.Equal(t, "Test Item", resp.Title)
}

// TestItemHandler_ListItems_Success tests successful item listing
func TestItemHandler_ListItems_Success(t *testing.T) {
	t.Skip("Requires integration with real service layer - use item_handler_test.go for unit tests")
	mockQueries := NewMockQueries()
	itemHandler := setupItemHandlerMock(mockQueries)

	// Create project and items
	project, err := mockQueries.CreateProject(context.Background(), db.CreateProjectParams{
		Name:        "Test Project",
		Description: pgtype.Text{Valid: false},
		Metadata:    []byte("{}"),
	})
	require.NoError(t, err)

	for i := 0; i < 5; i++ {
		_, err := mockQueries.CreateItem(context.Background(), db.CreateItemParams{
			ProjectID:   project.ID,
			Title:       fmt.Sprintf("Item %d", i),
			Description: pgtype.Text{Valid: false},
			Type:        "requirement",
			Status:      "open",
			Priority:    pgtype.Int4{Valid: false},
			Metadata:    []byte("{}"),
		})
		require.NoError(t, err)
	}

	e := echo.New()
	req := httptest.NewRequest(http.MethodGet, "/api/v1/items?project_id="+project.ID.String(), nil)
	rec := httptest.NewRecorder()
	c := e.NewContext(req, rec)

	err = itemHandler.ListItems(c)
	require.NoError(t, err)

	assert.Equal(t, http.StatusOK, rec.Code)

	var resp []db.ListItemsByProjectRow
	err = json.Unmarshal(rec.Body.Bytes(), &resp)
	require.NoError(t, err)

	assert.Len(t, resp, 5)
}

// TestItemHandler_UpdateItem_Success tests successful item update
func TestItemHandler_UpdateItem_Success(t *testing.T) {
	t.Skip("Requires integration with real service layer - use item_handler_test.go for unit tests")
	mockQueries := NewMockQueries()
	itemHandler := setupItemHandlerMock(mockQueries)

	// Create project and item
	project, err := mockQueries.CreateProject(context.Background(), db.CreateProjectParams{
		Name:        "Test Project",
		Description: pgtype.Text{Valid: false},
		Metadata:    []byte("{}"),
	})
	require.NoError(t, err)

	item, err := mockQueries.CreateItem(context.Background(), db.CreateItemParams{
		ProjectID:   project.ID,
		Title:       "Original Title",
		Description: pgtype.Text{Valid: false},
		Type:        "requirement",
		Status:      "open",
		Priority:    pgtype.Int4{Valid: false},
		Metadata:    []byte("{}"),
	})
	require.NoError(t, err)

	// Update the item
	body := map[string]interface{}{
		"title":       "Updated Title",
		"description": "Updated Description",
		"type":        "requirement",
		"status":      "closed",
		"priority":    2,
	}

	c, rec, err := makeRequest(http.MethodPut, "/api/v1/items/:id", body)
	require.NoError(t, err)

	c.SetPath("/api/v1/items/:id")
	setParamValue(c, "id", item.ID.String())

	err = itemHandler.UpdateItem(c)
	require.NoError(t, err)

	assert.Equal(t, http.StatusOK, rec.Code)

	var resp db.UpdateItemRow
	err = json.Unmarshal(rec.Body.Bytes(), &resp)
	require.NoError(t, err)

	assert.Equal(t, "Updated Title", resp.Title)
}

// TestItemHandler_DeleteItem_Success tests successful item deletion
func TestItemHandler_DeleteItem_Success(t *testing.T) {
	t.Skip("Requires integration with real service layer - use item_handler_test.go for unit tests")
	mockQueries := NewMockQueries()
	itemHandler := setupItemHandlerMock(mockQueries)

	// Create project and item
	project, err := mockQueries.CreateProject(context.Background(), db.CreateProjectParams{
		Name:        "Test Project",
		Description: pgtype.Text{Valid: false},
		Metadata:    []byte("{}"),
	})
	require.NoError(t, err)

	item, err := mockQueries.CreateItem(context.Background(), db.CreateItemParams{
		ProjectID:   project.ID,
		Title:       "To Delete",
		Description: pgtype.Text{Valid: false},
		Type:        "requirement",
		Status:      "open",
		Priority:    pgtype.Int4{Valid: false},
		Metadata:    []byte("{}"),
	})
	require.NoError(t, err)

	// Delete the item
	e := echo.New()
	req := httptest.NewRequest(http.MethodDelete, "/api/v1/items/:id", nil)
	rec := httptest.NewRecorder()
	c := e.NewContext(req, rec)
	c.SetPath("/api/v1/items/:id")
	setParamValue(c, "id", item.ID.String())

	err = itemHandler.DeleteItem(c)
	require.NoError(t, err)

	assert.Equal(t, http.StatusOK, rec.Code)

	// Verify deletion
	_, err = mockQueries.GetItem(context.Background(), item.ID)
	assert.Error(t, err)
}

// ============================================================================
// LINK HANDLER TESTS
// ============================================================================

// TestLinkHandler_CreateLink_Success tests successful link creation
func TestLinkHandler_CreateLink_Success(t *testing.T) {
	t.Skip("Requires integration with real service layer - use link_handler_test.go for unit tests")
	mockQueries := NewMockQueries()
	linkHandler := setupLinkHandlerMock(mockQueries)

	// Create project and items first
	project, err := mockQueries.CreateProject(context.Background(), db.CreateProjectParams{
		Name:        "Test Project",
		Description: pgtype.Text{Valid: false},
		Metadata:    []byte("{}"),
	})
	require.NoError(t, err)

	sourceItem, err := mockQueries.CreateItem(context.Background(), db.CreateItemParams{
		ProjectID:   project.ID,
		Title:       "Source Item",
		Description: pgtype.Text{Valid: false},
		Type:        "requirement",
		Status:      "open",
		Priority:    pgtype.Int4{Valid: false},
		Metadata:    []byte("{}"),
	})
	require.NoError(t, err)

	targetItem, err := mockQueries.CreateItem(context.Background(), db.CreateItemParams{
		ProjectID:   project.ID,
		Title:       "Target Item",
		Description: pgtype.Text{Valid: false},
		Type:        "requirement",
		Status:      "open",
		Priority:    pgtype.Int4{Valid: false},
		Metadata:    []byte("{}"),
	})
	require.NoError(t, err)

	// Create a link
	body := map[string]interface{}{
		"source_id": sourceItem.ID.String(),
		"target_id": targetItem.ID.String(),
		"type":      "depends_on",
	}

	c, rec, err := makeRequest(http.MethodPost, "/api/v1/links", body)
	require.NoError(t, err)

	err = linkHandler.CreateLink(c)
	require.NoError(t, err)

	assert.Equal(t, http.StatusCreated, rec.Code)

	var resp db.Link
	err = json.Unmarshal(rec.Body.Bytes(), &resp)
	require.NoError(t, err)

	assert.Equal(t, "depends_on", resp.Type)
}

// TestLinkHandler_CreateLink_InvalidSourceID_Integration tests link creation with invalid source ID
func TestLinkHandler_CreateLink_InvalidSourceID_Integration(t *testing.T) {
	mockQueries := NewMockQueries()
	linkHandler := setupLinkHandlerMock(mockQueries)

	body := map[string]interface{}{
		"source_id": "invalid-uuid",
		"target_id": uuid.New().String(),
		"type":      "depends_on",
	}

	c, rec, err := makeRequest(http.MethodPost, "/api/v1/links", body)
	require.NoError(t, err)

	err = linkHandler.CreateLink(c)
	require.NoError(t, err)

	assert.Equal(t, http.StatusBadRequest, rec.Code)
}

// TestLinkHandler_GetLink_Success tests successful link retrieval
func TestLinkHandler_GetLink_Success(t *testing.T) {
	t.Skip("Requires integration with real service layer - use link_handler_test.go for unit tests")
	mockQueries := NewMockQueries()
	linkHandler := setupLinkHandlerMock(mockQueries)

	// Create project and items
	project, err := mockQueries.CreateProject(context.Background(), db.CreateProjectParams{
		Name:        "Test Project",
		Description: pgtype.Text{Valid: false},
		Metadata:    []byte("{}"),
	})
	require.NoError(t, err)

	sourceItem, err := mockQueries.CreateItem(context.Background(), db.CreateItemParams{
		ProjectID:   project.ID,
		Title:       "Source",
		Description: pgtype.Text{Valid: false},
		Type:        "requirement",
		Status:      "open",
		Priority:    pgtype.Int4{Valid: false},
		Metadata:    []byte("{}"),
	})
	require.NoError(t, err)

	targetItem, err := mockQueries.CreateItem(context.Background(), db.CreateItemParams{
		ProjectID:   project.ID,
		Title:       "Target",
		Description: pgtype.Text{Valid: false},
		Type:        "requirement",
		Status:      "open",
		Priority:    pgtype.Int4{Valid: false},
		Metadata:    []byte("{}"),
	})
	require.NoError(t, err)

	link, err := mockQueries.CreateLink(context.Background(), db.CreateLinkParams{
		SourceID: sourceItem.ID,
		TargetID: targetItem.ID,
		Type:     "depends_on",
		Metadata: []byte("{}"),
	})
	require.NoError(t, err)

	// Get the link
	e := echo.New()
	req := httptest.NewRequest(http.MethodGet, "/api/v1/links/:id", nil)
	rec := httptest.NewRecorder()
	c := e.NewContext(req, rec)
	c.SetPath("/api/v1/links/:id")
	setParamValue(c, "id", link.ID.String())

	err = linkHandler.GetLink(c)
	require.NoError(t, err)

	assert.Equal(t, http.StatusOK, rec.Code)

	var resp db.Link
	err = json.Unmarshal(rec.Body.Bytes(), &resp)
	require.NoError(t, err)

	assert.Equal(t, link.ID, resp.ID)
	assert.Equal(t, "depends_on", resp.Type)
}

// TestLinkHandler_ListLinks_Success tests successful link listing
func TestLinkHandler_ListLinks_Success(t *testing.T) {
	t.Skip("Integration test - use link_handler_test.go for unit tests")
	mockQueries := NewMockQueries()
	linkHandler := setupLinkHandlerMock(mockQueries)

	// Create project and items
	project, err := mockQueries.CreateProject(context.Background(), db.CreateProjectParams{
		Name:        "Test Project",
		Description: pgtype.Text{Valid: false},
		Metadata:    []byte("{}"),
	})
	require.NoError(t, err)

	sourceItem, err := mockQueries.CreateItem(context.Background(), db.CreateItemParams{
		ProjectID:   project.ID,
		Title:       "Source",
		Description: pgtype.Text{Valid: false},
		Type:        "requirement",
		Status:      "open",
		Priority:    pgtype.Int4{Valid: false},
		Metadata:    []byte("{}"),
	})
	require.NoError(t, err)

	// Create multiple links from source
	for i := 0; i < 3; i++ {
		targetItem, err := mockQueries.CreateItem(context.Background(), db.CreateItemParams{
			ProjectID:   project.ID,
			Title:       fmt.Sprintf("Target %d", i),
			Description: pgtype.Text{Valid: false},
			Type:        "requirement",
			Status:      "open",
			Priority:    pgtype.Int4{Valid: false},
			Metadata:    []byte("{}"),
		})
		require.NoError(t, err)

		_, err = mockQueries.CreateLink(context.Background(), db.CreateLinkParams{
			SourceID: sourceItem.ID,
			TargetID: targetItem.ID,
			Type:     "depends_on",
			Metadata: []byte("{}"),
		})
		require.NoError(t, err)
	}

	// List links
	e := echo.New()
	req := httptest.NewRequest(http.MethodGet, "/api/v1/links?source_id="+sourceItem.ID.String(), nil)
	rec := httptest.NewRecorder()
	c := e.NewContext(req, rec)

	err = linkHandler.ListLinks(c)
	require.NoError(t, err)

	assert.Equal(t, http.StatusOK, rec.Code)

	var resp []db.Link
	err = json.Unmarshal(rec.Body.Bytes(), &resp)
	require.NoError(t, err)

	assert.Len(t, resp, 3)
}

// TestLinkHandler_UpdateLink_Success tests successful link update
func TestLinkHandler_UpdateLink_Success(t *testing.T) {
	t.Skip("Integration test - use link_handler_test.go for unit tests")
	mockQueries := NewMockQueries()
	linkHandler := setupLinkHandlerMock(mockQueries)

	// Create project, items, and link
	project, err := mockQueries.CreateProject(context.Background(), db.CreateProjectParams{
		Name:        "Test Project",
		Description: pgtype.Text{Valid: false},
		Metadata:    []byte("{}"),
	})
	require.NoError(t, err)

	sourceItem, err := mockQueries.CreateItem(context.Background(), db.CreateItemParams{
		ProjectID:   project.ID,
		Title:       "Source",
		Description: pgtype.Text{Valid: false},
		Type:        "requirement",
		Status:      "open",
		Priority:    pgtype.Int4{Valid: false},
		Metadata:    []byte("{}"),
	})
	require.NoError(t, err)

	targetItem, err := mockQueries.CreateItem(context.Background(), db.CreateItemParams{
		ProjectID:   project.ID,
		Title:       "Target",
		Description: pgtype.Text{Valid: false},
		Type:        "requirement",
		Status:      "open",
		Priority:    pgtype.Int4{Valid: false},
		Metadata:    []byte("{}"),
	})
	require.NoError(t, err)

	link, err := mockQueries.CreateLink(context.Background(), db.CreateLinkParams{
		SourceID: sourceItem.ID,
		TargetID: targetItem.ID,
		Type:     "depends_on",
		Metadata: []byte("{}"),
	})
	require.NoError(t, err)

	// Update the link
	body := map[string]interface{}{
		"type": "relates_to",
	}

	c, rec, err := makeRequest(http.MethodPut, "/api/v1/links/:id", body)
	require.NoError(t, err)

	c.SetPath("/api/v1/links/:id")
	setParamValue(c, "id", link.ID.String())

	err = linkHandler.UpdateLink(c)
	require.NoError(t, err)

	assert.Equal(t, http.StatusOK, rec.Code)

	var resp db.Link
	err = json.Unmarshal(rec.Body.Bytes(), &resp)
	require.NoError(t, err)

	assert.Equal(t, "relates_to", resp.Type)
}

// TestLinkHandler_DeleteLink_Success tests successful link deletion
func TestLinkHandler_DeleteLink_Success(t *testing.T) {
	t.Skip("Integration test - use link_handler_test.go for unit tests")
	mockQueries := NewMockQueries()
	linkHandler := setupLinkHandlerMock(mockQueries)

	// Create project, items, and link
	project, err := mockQueries.CreateProject(context.Background(), db.CreateProjectParams{
		Name:        "Test Project",
		Description: pgtype.Text{Valid: false},
		Metadata:    []byte("{}"),
	})
	require.NoError(t, err)

	sourceItem, err := mockQueries.CreateItem(context.Background(), db.CreateItemParams{
		ProjectID:   project.ID,
		Title:       "Source",
		Description: pgtype.Text{Valid: false},
		Type:        "requirement",
		Status:      "open",
		Priority:    pgtype.Int4{Valid: false},
		Metadata:    []byte("{}"),
	})
	require.NoError(t, err)

	targetItem, err := mockQueries.CreateItem(context.Background(), db.CreateItemParams{
		ProjectID:   project.ID,
		Title:       "Target",
		Description: pgtype.Text{Valid: false},
		Type:        "requirement",
		Status:      "open",
		Priority:    pgtype.Int4{Valid: false},
		Metadata:    []byte("{}"),
	})
	require.NoError(t, err)

	link, err := mockQueries.CreateLink(context.Background(), db.CreateLinkParams{
		SourceID: sourceItem.ID,
		TargetID: targetItem.ID,
		Type:     "depends_on",
		Metadata: []byte("{}"),
	})
	require.NoError(t, err)

	// Delete the link
	e := echo.New()
	req := httptest.NewRequest(http.MethodDelete, "/api/v1/links/:id", nil)
	rec := httptest.NewRecorder()
	c := e.NewContext(req, rec)
	c.SetPath("/api/v1/links/:id")
	setParamValue(c, "id", link.ID.String())

	err = linkHandler.DeleteLink(c)
	require.NoError(t, err)

	assert.Equal(t, http.StatusOK, rec.Code)

	// Verify deletion
	_, err = mockQueries.GetLink(context.Background(), link.ID)
	assert.Error(t, err)
}

// ============================================================================
// GRAPH HANDLER TESTS
// ============================================================================

// TestGraphHandler_GetAncestors_Success tests retrieving ancestors
func TestGraphHandler_GetAncestors_Success(t *testing.T) {
	mockQueries := NewMockQueries()

	// Create project and items
	project, err := mockQueries.CreateProject(context.Background(), db.CreateProjectParams{
		Name:        "Test Project",
		Description: pgtype.Text{Valid: false},
		Metadata:    []byte("{}"),
	})
	require.NoError(t, err)

	// Create items in a hierarchy
	item1, err := mockQueries.CreateItem(context.Background(), db.CreateItemParams{
		ProjectID:   project.ID,
		Title:       "Item 1",
		Description: pgtype.Text{Valid: false},
		Type:        "requirement",
		Status:      "open",
		Priority:    pgtype.Int4{Valid: false},
		Metadata:    []byte("{}"),
	})
	require.NoError(t, err)

	item2, err := mockQueries.CreateItem(context.Background(), db.CreateItemParams{
		ProjectID:   project.ID,
		Title:       "Item 2",
		Description: pgtype.Text{Valid: false},
		Type:        "requirement",
		Status:      "open",
		Priority:    pgtype.Int4{Valid: false},
		Metadata:    []byte("{}"),
	})
	require.NoError(t, err)

	// Create link: item1 -> item2
	_, err = mockQueries.CreateLink(context.Background(), db.CreateLinkParams{
		SourceID: item1.ID,
		TargetID: item2.ID,
		Type:     "depends_on",
		Metadata: []byte("{}"),
	})
	require.NoError(t, err)

	// Get ancestors of item2 (should find item1)
	ancestors, err := mockQueries.GetAncestors(context.Background(), item2.ID)
	require.NoError(t, err)

	assert.Len(t, ancestors, 1)
	assert.Equal(t, item1.ID, ancestors[0].ItemID)
}

// TestGraphHandler_GetDescendants_Success tests retrieving descendants
func TestGraphHandler_GetDescendants_Success(t *testing.T) {
	mockQueries := NewMockQueries()

	// Create project and items
	project, err := mockQueries.CreateProject(context.Background(), db.CreateProjectParams{
		Name:        "Test Project",
		Description: pgtype.Text{Valid: false},
		Metadata:    []byte("{}"),
	})
	require.NoError(t, err)

	// Create items
	item1, err := mockQueries.CreateItem(context.Background(), db.CreateItemParams{
		ProjectID:   project.ID,
		Title:       "Parent Item",
		Description: pgtype.Text{Valid: false},
		Type:        "requirement",
		Status:      "open",
		Priority:    pgtype.Int4{Valid: false},
		Metadata:    []byte("{}"),
	})
	require.NoError(t, err)

	// Create multiple descendants
	for i := 0; i < 3; i++ {
		child, err := mockQueries.CreateItem(context.Background(), db.CreateItemParams{
			ProjectID:   project.ID,
			Title:       fmt.Sprintf("Child Item %d", i),
			Description: pgtype.Text{Valid: false},
			Type:        "requirement",
			Status:      "open",
			Priority:    pgtype.Int4{Valid: false},
			Metadata:    []byte("{}"),
		})
		require.NoError(t, err)

		_, err = mockQueries.CreateLink(context.Background(), db.CreateLinkParams{
			SourceID: item1.ID,
			TargetID: child.ID,
			Type:     "depends_on",
			Metadata: []byte("{}"),
		})
		require.NoError(t, err)
	}

	// Get descendants of item1
	descendants, err := mockQueries.GetDescendants(context.Background(), item1.ID)
	require.NoError(t, err)

	assert.Len(t, descendants, 3)
	// Verify all descendants are returned (descendants only have ItemID, LinkType, and Depth)
	for _, desc := range descendants {
		assert.NotEqual(t, pgtype.UUID{}, desc.ItemID)
	}
}

// TestGraphHandler_GetAncestors_NoResults tests getting ancestors when none exist
func TestGraphHandler_GetAncestors_NoResults(t *testing.T) {
	mockQueries := NewMockQueries()

	// Create project and item without ancestors
	project, err := mockQueries.CreateProject(context.Background(), db.CreateProjectParams{
		Name:        "Test Project",
		Description: pgtype.Text{Valid: false},
		Metadata:    []byte("{}"),
	})
	require.NoError(t, err)

	item, err := mockQueries.CreateItem(context.Background(), db.CreateItemParams{
		ProjectID:   project.ID,
		Title:       "Isolated Item",
		Description: pgtype.Text{Valid: false},
		Type:        "requirement",
		Status:      "open",
		Priority:    pgtype.Int4{Valid: false},
		Metadata:    []byte("{}"),
	})
	require.NoError(t, err)

	// Get ancestors (should return empty)
	ancestors, err := mockQueries.GetAncestors(context.Background(), item.ID)
	require.NoError(t, err)

	assert.Empty(t, ancestors)
}

// TestMockQueries_ConcurrentAccess tests thread safety of MockQueries
func TestMockQueries_ConcurrentAccess(t *testing.T) {
	mockQueries := NewMockQueries()

	// Create a project first
	project, err := mockQueries.CreateProject(context.Background(), db.CreateProjectParams{
		Name:        "Test Project",
		Description: pgtype.Text{Valid: false},
		Metadata:    []byte("{}"),
	})
	require.NoError(t, err)

	// Concurrent read/write operations
	done := make(chan bool, 10)

	// Writers
	for i := 0; i < 5; i++ {
		go func(index int) {
			_, err := mockQueries.CreateItem(context.Background(), db.CreateItemParams{
				ProjectID:   project.ID,
				Title:       fmt.Sprintf("Item %d", index),
				Description: pgtype.Text{Valid: false},
				Type:        "requirement",
				Status:      "open",
				Priority:    pgtype.Int4{Valid: false},
				Metadata:    []byte("{}"),
			})
			assert.NoError(t, err)
			done <- true
		}(i)
	}

	// Readers
	for i := 0; i < 5; i++ {
		go func() {
			_, err := mockQueries.ListProjects(context.Background(), db.ListProjectsParams{
				Limit:  10,
				Offset: 0,
			})
			assert.NoError(t, err)
			done <- true
		}()
	}

	// Wait for all goroutines
	for i := 0; i < 10; i++ {
		<-done
	}
}
