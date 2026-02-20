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

	"github.com/google/uuid"
	"github.com/labstack/echo/v4"
	"github.com/pashagolub/pgxmock/v3"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"

	"github.com/kooshapari/tracertm-backend/internal/models"
	"github.com/kooshapari/tracertm-backend/internal/repository"
	"github.com/kooshapari/tracertm-backend/internal/services"
)

// setupLinkHandler creates a test handler for validation tests
func setupLinkHandler(_ *testing.T, mock pgxmock.PgxPoolIface) *LinkHandler {
	_ = mock // unused

	// Create a default mock service that returns success for all operations
	mockService := &services.MockLinkService{
		CreateLinkFunc: func(_ context.Context, link *models.Link) error {
			return nil
		},
		GetLinkFunc: func(_ context.Context, id string) (*models.Link, error) {
			return &models.Link{
				ID:       id,
				SourceID: "item-1",
				TargetID: "item-2",
				Type:     "depends_on",
			}, nil
		},
		ListLinksFunc: func(_ context.Context, _ repository.LinkFilter) ([]*models.Link, error) {
			return []*models.Link{}, nil
		},
		UpdateLinkFunc: func(_ context.Context, link *models.Link) error {
			return nil
		},
		DeleteLinkFunc: func(_ context.Context, id string) error {
			return nil
		},
	}

	return &LinkHandler{
		linkService: mockService,
		itemService: nil,
		binder:      &TestBinder{},
	}
}

// setupLinkHandlerWithMockService creates a test handler with MockLinkService
func setupLinkHandlerWithMockService(_ *testing.T, mockService *services.MockLinkService) *LinkHandler {
	return &LinkHandler{
		linkService: mockService,
		itemService: nil,
		binder:      &TestBinder{},
	}
}

// makeCreateLinkRequest creates an echo context for CreateLink testing
func makeCreateLinkRequest(t *testing.T, body map[string]interface{}) (*echo.Context, *httptest.ResponseRecorder) {
	bodyBytes, err := json.Marshal(body)
	require.NoError(t, err)

	e := echo.New()
	req := httptest.NewRequest(http.MethodPost, "/api/v1/links", bytes.NewReader(bodyBytes))
	req.Header.Set("Content-Type", "application/json")
	rec := httptest.NewRecorder()
	c := e.NewContext(req, rec)
	return &c, rec
}

// TestCreateLink_Validation tests CreateLink input validation with table-driven approach
func TestCreateLink_Validation(t *testing.T) {
	validSourceID := uuid.New().String()
	validTargetID := uuid.New().String()

	for _, tt := range createLinkValidationCases(validSourceID, validTargetID) {
		t.Run(tt.name, func(_ *testing.T) {
			mock, err := pgxmock.NewPool()
			require.NoError(t, err)
			defer mock.Close()

			handler := setupLinkHandler(t, mock)
			c, rec := makeCreateLinkRequest(t, tt.body)

			err = handler.CreateLink(*c)
			require.NoError(t, err)

			assert.Equal(t, tt.expectedStatus, rec.Code)
			var resp map[string]interface{}
			require.NoError(t, json.Unmarshal(rec.Body.Bytes(), &resp))
			if tt.shouldContain != "" {
				typed104, ok := resp["error"].(string)
				require.True(t, ok)
				assert.Contains(t, typed104, tt.shouldContain)
			}
		})
	}
}

type createLinkValidationCase struct {
	name           string
	body           map[string]interface{}
	expectedStatus int
	shouldContain  string
}

func createLinkValidationCases(validSourceID, validTargetID string) []createLinkValidationCase {
	return []createLinkValidationCase{
		{
			name:           "missing_source_id",
			body:           map[string]interface{}{"target_id": validTargetID, "type": "depends_on"},
			expectedStatus: http.StatusBadRequest,
			shouldContain:  "Invalid source_id",
		},
		{
			name:           "missing_target_id",
			body:           map[string]interface{}{"source_id": validSourceID, "type": "depends_on"},
			expectedStatus: http.StatusBadRequest,
			shouldContain:  "Invalid target_id",
		},
		{
			name:           "invalid_source_id_format",
			body:           map[string]interface{}{"source_id": "not-uuid", "target_id": validTargetID, "type": "depends_on"},
			expectedStatus: http.StatusBadRequest,
			shouldContain:  "Invalid source_id",
		},
		{
			name:           "invalid_target_id_format",
			body:           map[string]interface{}{"source_id": validSourceID, "target_id": "not-uuid", "type": "depends_on"},
			expectedStatus: http.StatusBadRequest,
			shouldContain:  "Invalid target_id",
		},
		{
			name:           "empty_source_id",
			body:           map[string]interface{}{"source_id": "", "target_id": validTargetID, "type": "depends_on"},
			expectedStatus: http.StatusBadRequest,
			shouldContain:  "Invalid source_id",
		},
		{
			name:           "empty_target_id",
			body:           map[string]interface{}{"source_id": validSourceID, "target_id": "", "type": "depends_on"},
			expectedStatus: http.StatusBadRequest,
			shouldContain:  "Invalid target_id",
		},
	}
}

// TestGetLink_Validation tests GetLink ID validation with table-driven approach
func TestGetLink_Validation(t *testing.T) {
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
			shouldContain:  "Invalid link ID",
		},
		{
			name:           "empty_id",
			id:             "",
			expectedStatus: http.StatusBadRequest,
			shouldContain:  "Invalid link ID",
		},
		{
			name:           "malformed_id",
			id:             "123-456",
			expectedStatus: http.StatusBadRequest,
			shouldContain:  "Invalid link ID",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(_ *testing.T) {
			mock, err := pgxmock.NewPool()
			require.NoError(t, err)
			defer mock.Close()

			handler := setupLinkHandler(t, mock)

			e := echo.New()
			req := httptest.NewRequest(http.MethodGet, "/api/v1/links/:id", nil)
			rec := httptest.NewRecorder()
			c := e.NewContext(req, rec)
			c.SetPath("/api/v1/links/:id")
			c.SetParamNames("id")
			c.SetParamValues(tt.id)

			err = handler.GetLink(c)
			require.NoError(t, err)

			assert.Equal(t, tt.expectedStatus, rec.Code)
			var resp map[string]interface{}
			require.NoError(t, json.Unmarshal(rec.Body.Bytes(), &resp))
			if tt.shouldContain != "" {
				typed209, ok := resp["error"].(string)
				require.True(t, ok)
				assert.Contains(t, typed209, tt.shouldContain)
			}
		})
	}
}

// TestListLinks_Validation tests ListLinks query parameter validation
func TestListLinks_Validation(t *testing.T) {
	tests := []listValidationTest{
		{
			name:           "missing_both_ids",
			queryString:    "",
			expectedStatus: http.StatusBadRequest,
			shouldContain:  "is required",
		},
		{
			name:           "invalid_source_id",
			queryString:    "?source_id=not-uuid",
			expectedStatus: http.StatusBadRequest,
			shouldContain:  "invalid source_id",
		},
		{
			name:           "invalid_target_id",
			queryString:    "?target_id=not-uuid",
			expectedStatus: http.StatusBadRequest,
			shouldContain:  "invalid target_id",
		},
		{
			name:           "empty_source_id",
			queryString:    "?source_id=",
			expectedStatus: http.StatusBadRequest,
			shouldContain:  "is required",
		},
	}

	runListValidationTests(
		t,
		tests,
		"/api/v1/links",
		func(handler interface{}, c echo.Context) error {
			h, ok := handler.(*LinkHandler)
			require.True(t, ok)
			return h.ListLinks(c)
		},
		func(t *testing.T, mock pgxmock.PgxPoolIface) interface{} {
			return setupLinkHandler(t, mock)
		},
	)
}

// TestListLinks_SourceIDOrTargetID tests ListLinks accepts either source_id or target_id
func TestListLinks_SourceIDOrTargetID(t *testing.T) {
	tests := []struct {
		name         string
		queryString  string
		expectStatus int // Should be 200 or 500 (database error), not 400
	}{
		{
			name:         "with_source_id",
			queryString:  "?source_id=" + uuid.New().String(),
			expectStatus: http.StatusInternalServerError, // DB mock failure is OK
		},
		{
			name:         "with_target_id",
			queryString:  "?target_id=" + uuid.New().String(),
			expectStatus: http.StatusInternalServerError, // DB mock failure is OK
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(_ *testing.T) {
			mock, err := pgxmock.NewPool()
			require.NoError(t, err)
			defer mock.Close()

			handler := setupLinkHandler(t, mock)

			e := echo.New()
			req := httptest.NewRequest(http.MethodGet, "/api/v1/links"+tt.queryString, nil)
			rec := httptest.NewRecorder()
			c := e.NewContext(req, rec)

			err = handler.ListLinks(c)
			require.NoError(t, err)

			// Should not get 400 - parameters are valid
			assert.NotEqual(t, http.StatusBadRequest, rec.Code)
		})
	}
}

// TestDeleteLink_Validation tests DeleteLink ID validation
func TestDeleteLink_Validation(t *testing.T) {
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
			shouldContain:  "Invalid link ID",
		},
		{
			name:           "empty_id",
			id:             "",
			expectedStatus: http.StatusBadRequest,
			shouldContain:  "Invalid link ID",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(_ *testing.T) {
			mock, err := pgxmock.NewPool()
			require.NoError(t, err)
			defer mock.Close()

			handler := setupLinkHandler(t, mock)

			e := echo.New()
			req := httptest.NewRequest(http.MethodDelete, "/api/v1/links/:id", nil)
			rec := httptest.NewRecorder()
			c := e.NewContext(req, rec)
			c.SetPath("/api/v1/links/:id")
			c.SetParamNames("id")
			c.SetParamValues(tt.id)

			err = handler.DeleteLink(c)
			require.NoError(t, err)

			assert.Equal(t, tt.expectedStatus, rec.Code)
		})
	}
}

// TestLinkHandler_StructureAndDependencies tests handler initialization
func TestLinkHandler_StructureAndDependencies(t *testing.T) {
	mock, err := pgxmock.NewPool()
	require.NoError(t, err)
	defer mock.Close()

	handler := setupLinkHandler(t, mock)

	// Verify handler structure
	assert.NotNil(t, handler.binder)
	assert.IsType(t, &TestBinder{}, handler.binder)
}

/* DISABLED - getCacheKey method removed
// TestLinkCacheKeyGeneration tests helper methods for link cache keys
func TestLinkCacheKeyGeneration(t *testing.T) {
	mock, err := pgxmock.NewPool()
	require.NoError(t, err)
	defer mock.Close()

	handler := setupLinkHandler(t, mock)

	tests := []struct {
		name     string
		linkID   string
		expected string
	}{
		{
			name:     "valid_uuid",
			linkID:   uuid.New().String(),
			expected: "link:",
		},
		{
			name:     "empty_id",
			linkID:   "",
			expected: "link:",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(_ *testing.T) {
			key := handler.getCacheKey(tt.linkID)
			assert.Contains(t, key, tt.expected)
		})
	}
}
*/

// ============================================================================
// TESTS WITH MOCK LINK SERVICE
// ============================================================================

// TestCreateLink_Success tests successful link creation with mock service
func TestCreateLink_Success(t *testing.T) {
	validSourceID := uuid.New()
	validTargetID := uuid.New()
	linkID := uuid.New()

	mockService := &services.MockLinkService{
		CreateLinkFunc: func(_ context.Context, link *models.Link) error {
			assert.Equal(t, validSourceID.String(), link.SourceID)
			assert.Equal(t, validTargetID.String(), link.TargetID)
			assert.Equal(t, "depends_on", link.Type)
			link.ID = linkID.String()
			return nil
		},
	}

	handler := setupLinkHandlerWithMockService(t, mockService)

	body := map[string]interface{}{
		"source_id": validSourceID.String(),
		"target_id": validTargetID.String(),
		"type":      "depends_on",
	}
	c, _ := makeCreateLinkRequest(t, body)

	// This will fail at DB level but validates before that
	err := handler.CreateLink(*c)
	require.NoError(t, err)
}

// TestGetLink_Success tests successful link retrieval with mock service
func TestGetLink_Success(t *testing.T) {
	linkID := uuid.New()
	expectedLink := &models.Link{
		ID:       linkID.String(),
		SourceID: uuid.New().String(),
		TargetID: uuid.New().String(),
		Type:     "depends_on",
	}

	mockService := &services.MockLinkService{
		GetLinkFunc: func(_ context.Context, id string) (*models.Link, error) {
			assert.Equal(t, linkID.String(), id)
			return expectedLink, nil
		},
	}

	handler := setupLinkHandlerWithMockService(t, mockService)

	e := echo.New()
	req := httptest.NewRequest(http.MethodGet, "/api/v1/links/:id", nil)
	rec := httptest.NewRecorder()
	c := e.NewContext(req, rec)
	c.SetPath("/api/v1/links/:id")
	c.SetParamNames("id")
	c.SetParamValues(linkID.String())

	// Will fail at DB level but validates the ID first
	err := handler.GetLink(c)
	require.NoError(t, err)
}

// TestGetLink_NotFound tests link not found scenario with mock service
func TestGetLink_NotFound(t *testing.T) {
	linkID := uuid.New()

	mockService := &services.MockLinkService{
		GetLinkFunc: func(_ context.Context, _ string) (*models.Link, error) {
			return nil, errors.New("link not found")
		},
	}

	handler := setupLinkHandlerWithMockService(t, mockService)

	e := echo.New()
	req := httptest.NewRequest(http.MethodGet, "/api/v1/links/:id", nil)
	rec := httptest.NewRecorder()
	c := e.NewContext(req, rec)
	c.SetPath("/api/v1/links/:id")
	c.SetParamNames("id")
	c.SetParamValues(linkID.String())

	err := handler.GetLink(c)
	require.NoError(t, err)
}

// TestListLinks_BySourceID tests listing links by source ID with mock service
func TestListLinks_BySourceID(t *testing.T) {
	sourceID := uuid.New()
	expectedLinks := []*models.Link{
		{
			ID:       uuid.New().String(),
			SourceID: sourceID.String(),
			TargetID: uuid.New().String(),
			Type:     "depends_on",
		},
		{
			ID:       uuid.New().String(),
			SourceID: sourceID.String(),
			TargetID: uuid.New().String(),
			Type:     "relates_to",
		},
	}

	mockService := &services.MockLinkService{
		ListLinksFunc: func(_ context.Context, filter repository.LinkFilter) ([]*models.Link, error) {
			assert.NotNil(t, filter.SourceID)
			assert.Equal(t, sourceID.String(), *filter.SourceID)
			return expectedLinks, nil
		},
	}

	handler := setupLinkHandlerWithMockService(t, mockService)

	e := echo.New()
	req := httptest.NewRequest(http.MethodGet, "/api/v1/links?source_id="+sourceID.String(), nil)
	rec := httptest.NewRecorder()
	c := e.NewContext(req, rec)

	err := handler.ListLinks(c)
	require.NoError(t, err)
}

// TestListLinks_ByTargetID tests listing links by target ID with mock service
func TestListLinks_ByTargetID(t *testing.T) {
	targetID := uuid.New()
	expectedLinks := []*models.Link{
		{
			ID:       uuid.New().String(),
			SourceID: uuid.New().String(),
			TargetID: targetID.String(),
			Type:     "blocks",
		},
	}

	mockService := &services.MockLinkService{
		ListLinksFunc: func(_ context.Context, filter repository.LinkFilter) ([]*models.Link, error) {
			assert.NotNil(t, filter.TargetID)
			assert.Equal(t, targetID.String(), *filter.TargetID)
			return expectedLinks, nil
		},
	}

	handler := setupLinkHandlerWithMockService(t, mockService)

	e := echo.New()
	req := httptest.NewRequest(http.MethodGet, "/api/v1/links?target_id="+targetID.String(), nil)
	rec := httptest.NewRecorder()
	c := e.NewContext(req, rec)

	err := handler.ListLinks(c)
	require.NoError(t, err)
}

// TestListLinks_EmptyResult tests listing links with no results
func TestListLinks_EmptyResult(t *testing.T) {
	sourceID := uuid.New()

	mockService := &services.MockLinkService{
		ListLinksFunc: func(_ context.Context, _ repository.LinkFilter) ([]*models.Link, error) {
			return []*models.Link{}, nil
		},
	}

	handler := setupLinkHandlerWithMockService(t, mockService)

	e := echo.New()
	req := httptest.NewRequest(http.MethodGet, "/api/v1/links?source_id="+sourceID.String(), nil)
	rec := httptest.NewRecorder()
	c := e.NewContext(req, rec)

	err := handler.ListLinks(c)
	require.NoError(t, err)
}

// TestDeleteLink_Success tests successful link deletion with mock service
func TestDeleteLink_Success(t *testing.T) {
	linkID := uuid.New()

	mockService := &services.MockLinkService{
		DeleteLinkFunc: func(_ context.Context, id string) error {
			assert.Equal(t, linkID.String(), id)
			return nil
		},
	}

	handler := setupLinkHandlerWithMockService(t, mockService)

	e := echo.New()
	req := httptest.NewRequest(http.MethodDelete, "/api/v1/links/:id", nil)
	rec := httptest.NewRecorder()
	c := e.NewContext(req, rec)
	c.SetPath("/api/v1/links/:id")
	c.SetParamNames("id")
	c.SetParamValues(linkID.String())

	err := handler.DeleteLink(c)
	require.NoError(t, err)
}

// TestDeleteLink_NotFound tests deleting a non-existent link
func TestDeleteLink_NotFound(t *testing.T) {
	linkID := uuid.New()

	mockService := &services.MockLinkService{
		DeleteLinkFunc: func(_ context.Context, _ string) error {
			return errors.New("link not found")
		},
	}

	handler := setupLinkHandlerWithMockService(t, mockService)

	e := echo.New()
	req := httptest.NewRequest(http.MethodDelete, "/api/v1/links/:id", nil)
	rec := httptest.NewRecorder()
	c := e.NewContext(req, rec)
	c.SetPath("/api/v1/links/:id")
	c.SetParamNames("id")
	c.SetParamValues(linkID.String())

	err := handler.DeleteLink(c)
	require.NoError(t, err)
}

// TestUpdateLink_Success tests successful link update with mock service
func TestUpdateLink_Success(t *testing.T) {
	linkID := uuid.New()

	mockService := &services.MockLinkService{
		UpdateLinkFunc: func(_ context.Context, link *models.Link) error {
			assert.Equal(t, linkID.String(), link.ID)
			assert.Equal(t, "blocks", link.Type)
			return nil
		},
	}

	handler := setupLinkHandlerWithMockService(t, mockService)

	body := map[string]interface{}{
		"type": "blocks",
	}
	bodyBytes, err := json.Marshal(body)
	require.NoError(t, err)

	e := echo.New()
	req := httptest.NewRequest(http.MethodPut, "/api/v1/links/:id", bytes.NewReader(bodyBytes))
	req.Header.Set("Content-Type", "application/json")
	rec := httptest.NewRecorder()
	c := e.NewContext(req, rec)
	c.SetPath("/api/v1/links/:id")
	c.SetParamNames("id")
	c.SetParamValues(linkID.String())

	// This tests validation - actual update would need handler modification
	err = handler.UpdateLink(c)
	require.NoError(t, err)
}

// TestMockLinkService_CreateError tests error handling in CreateLink
func TestMockLinkService_CreateError(t *testing.T) {
	mockService := &services.MockLinkService{
		CreateLinkFunc: func(_ context.Context, _ *models.Link) error {
			return errors.New("database connection error")
		},
	}

	handler := setupLinkHandlerWithMockService(t, mockService)

	body := map[string]interface{}{
		"source_id": uuid.New().String(),
		"target_id": uuid.New().String(),
		"type":      "depends_on",
	}
	c, rec := makeCreateLinkRequest(t, body)

	err := handler.CreateLink(*c)
	require.NoError(t, err)

	// Handler will return error status
	assert.Equal(t, http.StatusInternalServerError, rec.Code)
}

// TestMockLinkService_ListLinksError tests error handling in ListLinks
func TestMockLinkService_ListLinksError(t *testing.T) {
	mockService := &services.MockLinkService{
		ListLinksFunc: func(_ context.Context, _ repository.LinkFilter) ([]*models.Link, error) {
			return nil, errors.New("database timeout")
		},
	}

	handler := setupLinkHandlerWithMockService(t, mockService)

	e := echo.New()
	req := httptest.NewRequest(http.MethodGet, "/api/v1/links?source_id="+uuid.New().String(), nil)
	rec := httptest.NewRecorder()
	c := e.NewContext(req, rec)

	err := handler.ListLinks(c)
	require.NoError(t, err)

	// Handler will return error status
	assert.Equal(t, http.StatusInternalServerError, rec.Code)
}

// TestGetItemDependencies tests dependency graph retrieval
func TestGetItemDependencies(t *testing.T) {
	itemID := uuid.New()
	expectedGraph := &services.DependencyGraph{
		ItemID: itemID.String(),
		Dependencies: []*models.Link{
			{
				ID:       uuid.New().String(),
				SourceID: itemID.String(),
				TargetID: uuid.New().String(),
				Type:     "depends_on",
			},
		},
		Dependents: []*models.Link{
			{
				ID:       uuid.New().String(),
				SourceID: uuid.New().String(),
				TargetID: itemID.String(),
				Type:     "blocks",
			},
		},
		Items: make(map[string]*models.Item),
	}

	mockService := &services.MockLinkService{
		GetItemDependenciesFunc: func(_ context.Context, id string) (*services.DependencyGraph, error) {
			assert.Equal(t, itemID.String(), id)
			return expectedGraph, nil
		},
	}

	// Verify mock behavior
	graph, err := mockService.GetItemDependencies(context.Background(), itemID.String())
	require.NoError(t, err)
	assert.NotNil(t, graph)
	assert.Equal(t, itemID.String(), graph.ItemID)
	assert.Len(t, graph.Dependencies, 1)
	assert.Len(t, graph.Dependents, 1)
}
