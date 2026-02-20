package equivalence

import (
	"bytes"
	"context"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"
	"time"

	"github.com/google/uuid"
	"github.com/labstack/echo/v4"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

// TestGetSuggestions tests the GET /equivalences/suggestions endpoint
func TestGetSuggestions(t *testing.T) {
	// Setup
	e := echo.New()
	mockRepo := NewMockRepository()
	service := NewService(mockRepo, nil)
	handler := NewHandler(service)

	projectID := uuid.New()

	// Test case: invalid project_id
	req := httptest.NewRequest(http.MethodGet, "/api/v1/equivalences/suggestions?project_id=invalid", nil)
	rec := httptest.NewRecorder()
	c := e.NewContext(req, rec)

	err := handler.GetSuggestions(c)
	require.NoError(t, err)
	assert.Equal(t, http.StatusBadRequest, rec.Code)

	// Test case: valid request
	req = httptest.NewRequest(http.MethodGet, "/api/v1/equivalences/suggestions?project_id="+projectID.String(), nil)
	rec = httptest.NewRecorder()
	c = e.NewContext(req, rec)

	err = handler.GetSuggestions(c)
	require.NoError(t, err)
	assert.Equal(t, http.StatusOK, rec.Code)
}

// TestConfirmSuggestion tests the POST /equivalences/suggestions/:id/confirm endpoint
func TestConfirmSuggestion(t *testing.T) {
	// Setup
	e := echo.New()
	mockRepo := NewMockRepository()
	service := NewService(mockRepo, nil)
	handler := NewHandler(service)

	suggestionID := uuid.New()
	userID := uuid.New()

	// Create a mock suggestion
	mockSuggestion := &Suggestion{
		ID:            suggestionID,
		ProjectID:     uuid.New(),
		SourceItemID:  uuid.New(),
		TargetItemID:  uuid.New(),
		Confidence:    0.8,
		SuggestedType: "same_as",
		CreatedAt:     time.Now(),
	}
	require.NoError(t, mockRepo.SaveSuggestion(context.TODO(), mockSuggestion))

	// Test case: invalid suggestion id
	req := httptest.NewRequest(http.MethodPost, "/api/v1/equivalences/suggestions/invalid/confirm", nil)
	rec := httptest.NewRecorder()
	c := e.NewContext(req, rec)
	c.SetParamNames("id")
	c.SetParamValues("invalid")

	err := handler.ConfirmSuggestion(c)
	require.NoError(t, err)
	assert.Equal(t, http.StatusBadRequest, rec.Code)

	// Test case: valid confirmation
	req = httptest.NewRequest(http.MethodPost, "/api/v1/equivalences/suggestions/"+suggestionID.String()+"/confirm",
		bytes.NewReader([]byte(`{}`)))
	req.Header.Set("Content-Type", "application/json")
	rec = httptest.NewRecorder()
	c = e.NewContext(req, rec)
	c.SetParamNames("id")
	c.SetParamValues(suggestionID.String())
	c.Set("user_id", userID)

	err = handler.ConfirmSuggestion(c)
	require.NoError(t, err)
	assert.Equal(t, http.StatusOK, rec.Code)

	var resp Link
	err = json.Unmarshal(rec.Body.Bytes(), &resp)
	require.NoError(t, err)
	assert.NotEqual(t, uuid.Nil, resp.ID)
	assert.Equal(t, StatusConfirmed, resp.Status)
}

// TestRejectSuggestion tests the POST /equivalences/suggestions/:id/reject endpoint
func TestRejectSuggestion(t *testing.T) {
	// Setup
	e := echo.New()
	mockRepo := NewMockRepository()
	service := NewService(mockRepo, nil)
	handler := NewHandler(service)

	suggestionID := uuid.New()

	// Test case: invalid suggestion id
	req := httptest.NewRequest(http.MethodPost, "/api/v1/equivalences/suggestions/invalid/reject", nil)
	rec := httptest.NewRecorder()
	c := e.NewContext(req, rec)
	c.SetParamNames("id")
	c.SetParamValues("invalid")

	err := handler.RejectSuggestion(c)
	require.NoError(t, err)
	assert.Equal(t, http.StatusBadRequest, rec.Code)

	// Test case: valid rejection
	req = httptest.NewRequest(http.MethodPost, "/api/v1/equivalences/suggestions/"+suggestionID.String()+"/reject", nil)
	rec = httptest.NewRecorder()
	c = e.NewContext(req, rec)
	c.SetParamNames("id")
	c.SetParamValues(suggestionID.String())

	err = handler.RejectSuggestion(c)
	require.NoError(t, err)
	assert.Equal(t, http.StatusNoContent, rec.Code)
}

// TestBulkConfirmEquivalences tests the POST /equivalences/bulk-confirm endpoint
func TestBulkConfirmEquivalences(t *testing.T) {
	// Setup
	e := echo.New()
	mockRepo := NewMockRepository()
	service := NewService(mockRepo, nil)
	handler := NewHandler(service)

	userID := uuid.New()
	suggestionID := uuid.New()

	// Create a mock suggestion
	mockSuggestion := &Suggestion{
		ID:            suggestionID,
		ProjectID:     uuid.New(),
		SourceItemID:  uuid.New(),
		TargetItemID:  uuid.New(),
		Confidence:    0.8,
		SuggestedType: "same_as",
		CreatedAt:     time.Now(),
	}
	require.NoError(t, mockRepo.SaveSuggestion(context.TODO(), mockSuggestion))

	// Test case: empty equivalence_ids
	req := httptest.NewRequest(
		http.MethodPost,
		"/api/v1/equivalences/bulk-confirm",
		bytes.NewReader([]byte(`{"equivalence_ids":[]}`)),
	)
	req.Header.Set("Content-Type", "application/json")
	rec := httptest.NewRecorder()
	c := e.NewContext(req, rec)

	err := handler.BulkConfirmEquivalences(c)
	require.NoError(t, err)
	assert.Equal(t, http.StatusBadRequest, rec.Code)

	// Test case: valid bulk confirmation
	bulkReq := BulkConfirmRequest{
		EquivalenceIDs: []uuid.UUID{suggestionID},
	}
	body, err := json.Marshal(bulkReq)
	require.NoError(t, err)

	req = httptest.NewRequest(http.MethodPost, "/api/v1/equivalences/bulk-confirm", bytes.NewReader(body))
	req.Header.Set("Content-Type", "application/json")
	rec = httptest.NewRecorder()
	c = e.NewContext(req, rec)
	c.Set("user_id", userID)

	err = handler.BulkConfirmEquivalences(c)
	require.NoError(t, err)
	assert.Equal(t, http.StatusOK, rec.Code)

	var resp BulkConfirmResponse
	err = json.Unmarshal(rec.Body.Bytes(), &resp)
	require.NoError(t, err)
	assert.Positive(t, resp.Confirmed)
}

// TestBulkRejectEquivalences tests the POST /equivalences/bulk-reject endpoint
func TestBulkRejectEquivalences(t *testing.T) {
	// Setup
	e := echo.New()
	mockRepo := NewMockRepository()
	service := NewService(mockRepo, nil)
	handler := NewHandler(service)

	userID := uuid.New()
	suggestionID := uuid.New()

	// Test case: empty equivalence_ids
	req := httptest.NewRequest(
		http.MethodPost,
		"/api/v1/equivalences/bulk-reject",
		bytes.NewReader([]byte(`{"equivalence_ids":[]}`)),
	)
	req.Header.Set("Content-Type", "application/json")
	rec := httptest.NewRecorder()
	c := e.NewContext(req, rec)

	err := handler.BulkRejectEquivalences(c)
	require.NoError(t, err)
	assert.Equal(t, http.StatusBadRequest, rec.Code)

	// Test case: valid bulk rejection
	bulkReq := BulkRejectRequest{
		EquivalenceIDs: []uuid.UUID{suggestionID},
	}
	body, err := json.Marshal(bulkReq)
	require.NoError(t, err)

	req = httptest.NewRequest(http.MethodPost, "/api/v1/equivalences/bulk-reject", bytes.NewReader(body))
	req.Header.Set("Content-Type", "application/json")
	rec = httptest.NewRecorder()
	c = e.NewContext(req, rec)
	c.Set("user_id", userID)

	err = handler.BulkRejectEquivalences(c)
	require.NoError(t, err)
	assert.Equal(t, http.StatusOK, rec.Code)

	var resp BulkRejectResponse
	err = json.Unmarshal(rec.Body.Bytes(), &resp)
	require.NoError(t, err)
}
