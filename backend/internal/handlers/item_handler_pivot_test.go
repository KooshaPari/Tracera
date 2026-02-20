package handlers

import (
	"context"
	"encoding/json"
	"errors"
	"net/http"
	"testing"
	"time"

	"github.com/google/uuid"
	"github.com/labstack/echo/v4"
	"github.com/pashagolub/pgxmock/v3"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"

	"github.com/kooshapari/tracertm-backend/internal/models"
	"github.com/kooshapari/tracertm-backend/internal/services"
)

// TestGetPivotTargets_Validation tests GetPivotTargets ID validation
func TestGetPivotTargets_Validation(t *testing.T) {
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
			shouldContain:  "Invalid item ID",
		},
		{
			name:           "empty_id",
			id:             "",
			expectedStatus: http.StatusBadRequest,
			shouldContain:  "Invalid item ID",
		},
		{
			name:           "malformed_uuid",
			id:             "123-456-789",
			expectedStatus: http.StatusBadRequest,
			shouldContain:  "Invalid item ID",
		},
	}

	runItemIDValidationTests(t, tests, "/api/v1/items/:id/pivot-targets", func(handler *ItemHandler, c *echo.Context) error {
		return handler.GetPivotTargets(*c)
	})
}

// TestGetPivotTargets_ItemNotFound tests GetPivotTargets with non-existent item
func TestGetPivotTargets_ItemNotFound(t *testing.T) {
	mock, err := pgxmock.NewPool()
	require.NoError(t, err)
	defer mock.Close()

	// Create a handler with a custom mock that returns "not found" for this test
	itemID := uuid.New().String()
	mockService := &services.MockItemService{
		OnGetItem: func(_ context.Context, id string) (*models.Item, error) {
			// Return not found for the specific item we're testing
			if id == itemID {
				return nil, errors.New("item not found")
			}
			return &models.Item{
				ID:        id,
				ProjectID: "project-1",
				Title:     "Test Item",
				Type:      "requirement",
				Status:    "open",
				CreatedAt: time.Now().UTC(),
				UpdatedAt: time.Now().UTC(),
			}, nil
		},
		OnItemExists: func(_ context.Context, id string) (bool, error) {
			return id != itemID, nil
		},
	}

	handler := &ItemHandler{
		itemService:  mockService,
		cache:        nil,
		publisher:    nil,
		authProvider: nil,
		binder:       &TestBinder{},
	}

	c, rec := makeGetRequest(t, "/api/v1/items/:id/pivot-targets", "id", itemID)

	err = handler.GetPivotTargets(*c)
	require.NoError(t, err)

	assert.Equal(t, http.StatusNotFound, rec.Code)
	var resp map[string]interface{}
	require.NoError(t, json.Unmarshal(rec.Body.Bytes(), &resp))
	typed99, ok := resp["error"].(string)
	require.True(t, ok)
	assert.Contains(t, typed99, "Item not found")
}

// TestGetPivotTargets_Success tests GetPivotTargets with valid item
func TestGetPivotTargets_Success(t *testing.T) {
	mock, err := pgxmock.NewPool()
	require.NoError(t, err)
	defer mock.Close()

	// Set up test data
	projectID := uuid.New()
	itemID := uuid.New()

	// Mock the GetItem query
	mock.ExpectQuery("SELECT").WithArgs(itemID).WillReturnRows(
		pgxmock.NewRows([]string{
			"id", "project_id", "title", "description", "type",
			"status", "priority", "metadata", "created_at", "updated_at",
		}).
			AddRow(itemID, projectID, "Test Item", "A test item", "requirement", "open", nil, []byte("{}"), time.Now(), time.Now()),
	)

	handler := setupItemHandler(t, mock)
	c, rec := makeGetRequest(t, "/api/v1/items/:id/pivot-targets", "id", itemID.String())

	err = handler.GetPivotTargets(*c)
	require.NoError(t, err)

	assert.Equal(t, http.StatusOK, rec.Code)

	var resp PivotTargetsResponse
	err = json.Unmarshal(rec.Body.Bytes(), &resp)
	require.NoError(t, err)

	// Verify response structure
	assert.Equal(t, itemID.String(), resp.ItemID)
	assert.Equal(t, "requirement", resp.ItemType)
	assert.Equal(t, "Test Item", resp.Title)
	assert.Equal(t, "open", resp.Status)
}

// TestGetPivotTargets_ResponseStructure tests that response has all required fields
func TestGetPivotTargets_ResponseStructure(t *testing.T) {
	mock, err := pgxmock.NewPool()
	require.NoError(t, err)
	defer mock.Close()

	projectID := uuid.New()
	itemID := uuid.New()

	mock.ExpectQuery("SELECT").WithArgs(itemID).WillReturnRows(
		pgxmock.NewRows([]string{
			"id", "project_id", "title", "description", "type",
			"status", "priority", "metadata", "created_at", "updated_at",
		}).
			AddRow(itemID, projectID, "Test", "", "type", "status", nil, []byte("{}"), time.Now(), time.Now()),
	)

	handler := setupItemHandler(t, mock)
	c, rec := makeGetRequest(t, "/api/v1/items/:id/pivot-targets", "id", itemID.String())

	err = handler.GetPivotTargets(*c)
	require.NoError(t, err)

	var resp map[string]interface{}
	err = json.Unmarshal(rec.Body.Bytes(), &resp)
	require.NoError(t, err)

	// Verify all required fields exist
	requiredFields := []string{"item_id", "item_type", "title", "status", "perspectives", "targets"}
	for _, field := range requiredFields {
		assert.Contains(t, resp, field, "Response should contain field: "+field)
	}

	// Verify perspectives and targets are arrays
	assert.IsType(t, []interface{}{}, resp["perspectives"])
	assert.IsType(t, []interface{}{}, resp["targets"])
}
