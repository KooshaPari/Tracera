//go:build !integration && !e2e
// +build !integration,!e2e

package handlers

import (
	"bytes"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/google/uuid"
	"github.com/labstack/echo/v4"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

// ===== CONSTRUCTOR AND INITIALIZATION TESTS =====

// ===== LINK HANDLER TESTS - COVERAGE EXPANSION =====

// ===== BINDER TESTS =====

// TestTestBinder_Bind_WithValidJSON tests TestBinder with valid JSON
func TestTestBinder_Bind_WithValidJSON(t *testing.T) {
	binder := &TestBinder{}
	e := echo.New()

	reqBody := map[string]string{
		"name": "test",
	}
	body, _ := json.Marshal(reqBody)

	req := httptest.NewRequest(http.MethodPost, "/test", bytes.NewReader(body))
	req.Header.Set("Content-Type", "application/json")
	rec := httptest.NewRecorder()
	c := e.NewContext(req, rec)

	var result map[string]string
	err := binder.Bind(c, &result)

	assert.NoError(t, err)
	assert.Equal(t, "test", result["name"])
}

// TestTestBinder_Bind_WithEmptyBody tests TestBinder with empty body
func TestTestBinder_Bind_WithEmptyBody(t *testing.T) {
	binder := &TestBinder{}
	e := echo.New()

	req := httptest.NewRequest(http.MethodPost, "/test", bytes.NewReader([]byte("")))
	req.ContentLength = 0
	rec := httptest.NewRecorder()
	c := e.NewContext(req, rec)

	var result map[string]string
	err := binder.Bind(c, &result)

	assert.NoError(t, err)
}

// ===== ERROR RESPONSE TESTS =====

// TestErrorResponse_Serialization tests error response JSON serialization
func TestErrorResponse_Serialization(t *testing.T) {
	errResp := ErrorResponse{
		Error: "test error message",
	}

	data, err := json.Marshal(errResp)
	require.NoError(t, err)

	var unmarshaled ErrorResponse
	err = json.Unmarshal(data, &unmarshaled)
	require.NoError(t, err)

	assert.Equal(t, errResp.Error, unmarshaled.Error)
}

// ===== CONTEXT AND VALIDATION TESTS =====

// TestContextParsing_InvalidUUID tests invalid UUID parsing
func TestContextParsing_InvalidUUID(t *testing.T) {
	handler := createMockProjectHandler()
	e := echo.New()

	req := httptest.NewRequest(http.MethodGet, "/projects/not-a-uuid", nil)
	rec := httptest.NewRecorder()
	c := e.NewContext(req, rec)
	c.SetParamNames("id")
	c.SetParamValues("not-a-uuid")

	err := handler.GetProject(c)
	assert.NoError(t, err)
	assert.Equal(t, http.StatusBadRequest, rec.Code)
}

// TestContextParsing_ValidUUID tests valid UUID parsing
func TestContextParsing_ValidUUID(t *testing.T) {
	handler := createMockProjectHandler()
	testID := uuid.New().String()

	// Cache key generation should work with valid UUID
	key := handler.getCacheKey(testID)
	assert.NotEmpty(t, key)
	assert.Contains(t, key, testID)
}

// ===== HELPER FUNCTIONS FOR MOCKING =====

func createMockProjectHandler() *ProjectHandler {
	return &ProjectHandler{
		cache:               nil,
		publisher:           nil,
		realtimeBroadcaster: nil,
		authProvider:        nil,
		binder:              &TestBinder{},
	}
}

func createMockItemHandler() *ItemHandler {
	return &ItemHandler{
		cache:               nil,
		publisher:           nil,
		realtimeBroadcaster: nil,
		authProvider:        nil,
		binder:              &TestBinder{},
	}
}

func createMockLinkHandler() *LinkHandler {
	return &LinkHandler{
		linkService: nil,
		itemService: nil,
		binder:      &TestBinder{},
	}
}

// ===== EDGE CASE TESTS =====

func TestLinkHandler_ListLinks_ServiceNotInitialized(t *testing.T) {
	handler := createMockLinkHandler()
	e := echo.New()

	req := httptest.NewRequest(http.MethodGet, "/links", nil)
	rec := httptest.NewRecorder()
	c := e.NewContext(req, rec)

	err := handler.ListLinks(c)
	require.NoError(t, err)
	assert.Equal(t, http.StatusInternalServerError, rec.Code)
}

// TestProjectHandler_UpdateProject_InvalidID tests update with invalid project ID
func TestProjectHandler_UpdateProject_InvalidID(t *testing.T) {
	handler := createMockProjectHandler()
	e := echo.New()

	reqBody := map[string]interface{}{
		"name": "Updated Name",
	}

	body, _ := json.Marshal(reqBody)
	req := httptest.NewRequest(http.MethodPut, "/projects/invalid-id", bytes.NewReader(body))
	req.Header.Set("Content-Type", "application/json")
	rec := httptest.NewRecorder()
	c := e.NewContext(req, rec)
	c.SetParamNames("id")
	c.SetParamValues("invalid-id")

	handler.binder = &TestBinder{}
	err := handler.UpdateProject(c)
	assert.NoError(t, err)
	assert.Equal(t, http.StatusBadRequest, rec.Code)
}

// TestProjectHandler_DeleteProject_InvalidID tests delete with invalid project ID
func TestProjectHandler_DeleteProject_InvalidID(t *testing.T) {
	handler := createMockProjectHandler()
	e := echo.New()

	req := httptest.NewRequest(http.MethodDelete, "/projects/invalid-id", nil)
	rec := httptest.NewRecorder()
	c := e.NewContext(req, rec)
	c.SetParamNames("id")
	c.SetParamValues("invalid-id")

	err := handler.DeleteProject(c)
	assert.NoError(t, err)
	assert.Equal(t, http.StatusBadRequest, rec.Code)
}

// TestItemHandler_UpdateItem_InvalidID tests update with invalid item ID
func TestItemHandler_UpdateItem_InvalidID(t *testing.T) {
	handler := createMockItemHandler()
	e := echo.New()

	reqBody := map[string]interface{}{
		"title": "Updated Title",
	}

	body, _ := json.Marshal(reqBody)
	req := httptest.NewRequest(http.MethodPut, "/items/invalid-id", bytes.NewReader(body))
	req.Header.Set("Content-Type", "application/json")
	rec := httptest.NewRecorder()
	c := e.NewContext(req, rec)
	c.SetParamNames("id")
	c.SetParamValues("invalid-id")

	handler.binder = &TestBinder{}
	err := handler.UpdateItem(c)
	assert.NoError(t, err)
	assert.Equal(t, http.StatusBadRequest, rec.Code)
}

// TestItemHandler_DeleteItem_InvalidID tests delete with invalid item ID
func TestItemHandler_DeleteItem_InvalidID(t *testing.T) {
	handler := createMockItemHandler()
	e := echo.New()

	req := httptest.NewRequest(http.MethodDelete, "/items/invalid-id", nil)
	rec := httptest.NewRecorder()
	c := e.NewContext(req, rec)
	c.SetParamNames("id")
	c.SetParamValues("invalid-id")

	err := handler.DeleteItem(c)
	assert.NoError(t, err)
	assert.Equal(t, http.StatusBadRequest, rec.Code)
}

// TestItemHandler_GetItem_InvalidID tests get with invalid item ID
func TestItemHandler_GetItem_InvalidID(t *testing.T) {
	handler := createMockItemHandler()
	e := echo.New()

	req := httptest.NewRequest(http.MethodGet, "/items/invalid-id", nil)
	rec := httptest.NewRecorder()
	c := e.NewContext(req, rec)
	c.SetParamNames("id")
	c.SetParamValues("invalid-id")

	err := handler.GetItem(c)
	assert.NoError(t, err)
	assert.Equal(t, http.StatusBadRequest, rec.Code)
}
