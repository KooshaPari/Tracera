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

	"github.com/labstack/echo/v4"
	"github.com/pashagolub/pgxmock/v3"
	"github.com/stretchr/testify/require"

	"github.com/kooshapari/tracertm-backend/internal/models"
	"github.com/kooshapari/tracertm-backend/internal/repository"
	"github.com/kooshapari/tracertm-backend/internal/services"
)

// setupItemHandler creates a test handler with a mock ItemService
func setupItemHandler(_ *testing.T, mock pgxmock.PgxPoolIface) *ItemHandler {
	_ = mock // unused in current setup

	// Create a default mock service that returns success for all operations
	mockService := &services.MockItemService{
		OnCreateItem: func(_ context.Context, item *models.Item) error {
			// Validate title is not empty
			if item.Title == "" {
				return errors.New("title is required")
			}
			return nil
		},
		OnGetItem: func(_ context.Context, id string) (*models.Item, error) {
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
		OnListItems: func(_ context.Context, _ repository.ItemFilter) ([]*models.Item, error) {
			return []*models.Item{}, nil
		},
		OnUpdateItem: func(_ context.Context, item *models.Item) error {
			return nil
		},
		OnDeleteItem: func(_ context.Context, id string) error {
			return nil
		},
		OnItemExists: func(_ context.Context, id string) (bool, error) {
			return true, nil
		},
	}

	handler := &ItemHandler{
		itemService:  mockService,
		cache:        nil,
		publisher:    nil,
		authProvider: nil,
		binder:       &TestBinder{},
	}
	return handler
}

// makeCreateItemRequest creates an echo context for CreateItem testing
func makeCreateItemRequest(t *testing.T, body map[string]interface{}) (*echo.Context, *httptest.ResponseRecorder) {
	bodyBytes, err := json.Marshal(body)
	require.NoError(t, err)

	e := echo.New()
	req := httptest.NewRequest(http.MethodPost, "/api/v1/items", bytes.NewReader(bodyBytes))
	req.Header.Set("Content-Type", "application/json")
	rec := httptest.NewRecorder()
	c := e.NewContext(req, rec)
	return &c, rec
}

// makeGetRequest creates an echo context for GET requests
func makeGetRequest(_ *testing.T, path string, paramName, paramValue string) (*echo.Context, *httptest.ResponseRecorder) {
	e := echo.New()
	req := httptest.NewRequest(http.MethodGet, path, nil)
	rec := httptest.NewRecorder()
	c := e.NewContext(req, rec)
	if paramName != "" {
		c.SetPath(path)
		c.SetParamNames(paramName)
		c.SetParamValues(paramValue)
	}
	return &c, rec
}

// makeUpdateRequest creates an echo context for PUT requests
func makeUpdateRequest(
	t *testing.T, path, paramName, paramValue string, body map[string]interface{},
) (*echo.Context, *httptest.ResponseRecorder) {
	bodyBytes, err := json.Marshal(body)
	require.NoError(t, err)

	e := echo.New()
	req := httptest.NewRequest(http.MethodPut, path, bytes.NewReader(bodyBytes))
	req.Header.Set("Content-Type", "application/json")
	rec := httptest.NewRecorder()
	c := e.NewContext(req, rec)
	c.SetPath(path)
	c.SetParamNames(paramName)
	c.SetParamValues(paramValue)
	return &c, rec
}

// makeDeleteRequest creates an echo context for DELETE requests
func makeDeleteRequest(_ *testing.T, path string, paramName, paramValue string) (*echo.Context, *httptest.ResponseRecorder) {
	e := echo.New()
	req := httptest.NewRequest(http.MethodDelete, path, nil)
	rec := httptest.NewRecorder()
	c := e.NewContext(req, rec)
	c.SetPath(path)
	c.SetParamNames(paramName)
	c.SetParamValues(paramValue)
	return &c, rec
}
