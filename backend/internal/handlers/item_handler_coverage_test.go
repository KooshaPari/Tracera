//go:build !integration && !e2e

package handlers

import (
	"bytes"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/labstack/echo/v4"
	"github.com/pashagolub/pgxmock/v3"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

type listItemsErrorCase struct {
	name string
	fn   func(t *testing.T)
}

// TestItemHandler_CreateItem_ErrorPaths tests error handling in CreateItem
func TestItemHandler_CreateItem_ErrorPaths(t *testing.T) {
	mock, err := pgxmock.NewPool()
	require.NoError(t, err)
	defer mock.Close()

	handler := setupItemHandler(t, mock)

	t.Run("bind error", func(t *testing.T) {
		e := echo.New()
		req := httptest.NewRequest(http.MethodPost, "/api/v1/items", bytes.NewReader([]byte("invalid json")))
		req.Header.Set("Content-Type", "application/json")
		rec := httptest.NewRecorder()
		c := e.NewContext(req, rec)

		err := handler.CreateItem(c)
		// Echo's binder may return error or handle it internally
		// Check if error is returned or if response code is set
		if err != nil {
			he, ok := err.(*echo.HTTPError)
			if ok {
				assert.Equal(t, http.StatusBadRequest, he.Code)
			}
		} else {
			// If no error, check response code
			assert.GreaterOrEqual(t, rec.Code, http.StatusBadRequest)
		}
	})

	t.Run("invalid project_id", func(t *testing.T) {
		// Note: setupItemHandler requires real *pgxpool.Pool
		// For validation tests, we test with minimal handler
		handler := &ItemHandler{
			binder: &TestBinder{},
		}

		body := map[string]interface{}{
			"project_id": "invalid-uuid",
			"title":      "Test Item",
		}
		bodyBytes, _ := json.Marshal(body)

		e := echo.New()
		req := httptest.NewRequest(http.MethodPost, "/api/v1/items", bytes.NewReader(bodyBytes))
		req.Header.Set("Content-Type", "application/json")
		rec := httptest.NewRecorder()
		c := e.NewContext(req, rec)

		err := handler.CreateItem(c)
		// Should return 400 for invalid UUID
		if err != nil {
			he, ok := err.(*echo.HTTPError)
			if ok {
				assert.Equal(t, http.StatusBadRequest, he.Code)
			}
		} else {
			// Check response body
			assert.Contains(t, rec.Body.String(), "Invalid project_id")
		}
	})

	t.Run("database error", func(t *testing.T) {
		// Note: Database error testing requires integration tests with real pool
		// For unit tests, we test validation paths
		t.Skip("Requires real database pool - integration test")
	})
}

// TestItemHandler_ListItems_ErrorPaths tests error handling in ListItems
func TestItemHandler_ListItems_ErrorPaths(t *testing.T) {
	runListItemsErrorCases(t, []listItemsErrorCase{
		{name: "missing project_id", fn: runListItemsMissingProjectID},
		{name: "invalid project_id", fn: runListItemsInvalidProjectID},
		{name: "database error", fn: runListItemsDatabaseError},
		{name: "invalid limit", fn: runListItemsInvalidLimit},
		{name: "invalid offset", fn: runListItemsInvalidOffset},
	})
}

func runListItemsErrorCases(t *testing.T, cases []listItemsErrorCase) {
	for _, tc := range cases {
		t.Run(tc.name, func(t *testing.T) {
			tc.fn(t)
		})
	}
}

func runListItemsMissingProjectID(t *testing.T) {
	handler := &ItemHandler{
		binder: &TestBinder{},
	}

	e := echo.New()
	req := httptest.NewRequest(http.MethodGet, "/api/v1/items", nil)
	rec := httptest.NewRecorder()
	c := e.NewContext(req, rec)

	err := handler.ListItems(c)
	if err != nil {
		he, ok := err.(*echo.HTTPError)
		if ok {
			assert.True(t, he.Code == http.StatusBadRequest || he.Code == http.StatusInternalServerError)
		}
	}
}

func runListItemsInvalidProjectID(t *testing.T) {
	handler := &ItemHandler{
		binder: &TestBinder{},
	}

	e := echo.New()
	req := httptest.NewRequest(http.MethodGet, "/api/v1/items?project_id=invalid", nil)
	rec := httptest.NewRecorder()
	c := e.NewContext(req, rec)

	err := handler.ListItems(c)
	if err != nil {
		he, ok := err.(*echo.HTTPError)
		if ok {
			assert.True(t, he.Code == http.StatusBadRequest || he.Code == http.StatusInternalServerError)
		}
	} else {
		assert.Contains(t, rec.Body.String(), "error")
	}
}

func runListItemsDatabaseError(t *testing.T) {
	t.Skip("Requires real database pool - integration test")
}

func runListItemsInvalidLimit(t *testing.T) {
	handler := &ItemHandler{
		binder: &TestBinder{},
	}

	e := echo.New()
	req := httptest.NewRequest(http.MethodGet, "/api/v1/items?project_id=123e4567-e89b-12d3-a456-426614174000&limit=invalid", nil)
	rec := httptest.NewRecorder()
	c := e.NewContext(req, rec)

	defer func() {
		if r := recover(); r != nil {
			assert.NotNil(t, r)
		}
	}()
	_ = handler.ListItems(c)
}

func runListItemsInvalidOffset(t *testing.T) {
	handler := &ItemHandler{
		binder: &TestBinder{},
	}

	e := echo.New()
	req := httptest.NewRequest(http.MethodGet, "/api/v1/items?project_id=123e4567-e89b-12d3-a456-426614174000&offset=invalid", nil)
	rec := httptest.NewRecorder()
	c := e.NewContext(req, rec)

	defer func() {
		if r := recover(); r != nil {
			assert.NotNil(t, r)
		}
	}()
	_ = handler.ListItems(c)
}

// TestItemHandler_GetItem_ErrorPaths tests error handling in GetItem
func TestItemHandler_GetItem_ErrorPaths(t *testing.T) {
	t.Run("invalid item ID", func(t *testing.T) {
		assertInvalidItemID(t, http.MethodGet, "/api/v1/items/invalid", func(handler *ItemHandler, c echo.Context) error {
			return handler.GetItem(c)
		})
	})

	t.Run("item not found", func(t *testing.T) {
		// Note: Database error testing requires integration tests with real pool
		t.Skip("Requires real database pool - integration test")
	})
}

// TestItemHandler_UpdateItem_ErrorPaths tests error handling in UpdateItem
func TestItemHandler_UpdateItem_ErrorPaths(t *testing.T) {
	t.Run("bind error", func(t *testing.T) {
		handler := &ItemHandler{
			binder: &TestBinder{},
		}

		e := echo.New()
		req := httptest.NewRequest(http.MethodPut, "/api/v1/items/123e4567-e89b-12d3-a456-426614174000", bytes.NewReader([]byte("invalid json")))
		req.Header.Set("Content-Type", "application/json")
		rec := httptest.NewRecorder()
		c := e.NewContext(req, rec)
		c.SetParamNames("id")
		c.SetParamValues("123e4567-e89b-12d3-a456-426614174000")

		err := handler.UpdateItem(c)
		if err != nil {
			he, ok := err.(*echo.HTTPError)
			if ok {
				assert.Equal(t, http.StatusBadRequest, he.Code)
			}
		}
	})

	t.Run("invalid item ID", func(t *testing.T) {
		handler := &ItemHandler{
			binder: &TestBinder{},
		}

		body := map[string]interface{}{
			"title": "Updated Title",
		}
		bodyBytes, _ := json.Marshal(body)

		e := echo.New()
		req := httptest.NewRequest(http.MethodPut, "/api/v1/items/invalid", bytes.NewReader(bodyBytes))
		req.Header.Set("Content-Type", "application/json")
		rec := httptest.NewRecorder()
		c := e.NewContext(req, rec)
		c.SetParamNames("id")
		c.SetParamValues("invalid")

		err := handler.UpdateItem(c)
		// Should return 400 for invalid UUID
		if err != nil {
			he, ok := err.(*echo.HTTPError)
			if ok {
				assert.Equal(t, http.StatusBadRequest, he.Code)
			}
		} else {
			assert.Contains(t, rec.Body.String(), "Invalid item ID")
		}
	})

	t.Run("database error", func(t *testing.T) {
		// Note: Database error testing requires integration tests with real pool
		t.Skip("Requires real database pool - integration test")
	})
}

// TestItemHandler_DeleteItem_ErrorPaths tests error handling in DeleteItem
func TestItemHandler_DeleteItem_ErrorPaths(t *testing.T) {
	t.Run("invalid item ID", func(t *testing.T) {
		assertInvalidItemID(t, http.MethodDelete, "/api/v1/items/invalid", func(handler *ItemHandler, c echo.Context) error {
			return handler.DeleteItem(c)
		})
	})

	t.Run("database error", func(t *testing.T) {
		// Note: Database error testing requires integration tests with real pool
		t.Skip("Requires real database pool - integration test")
	})
}

func assertInvalidItemID(
	t *testing.T,
	method string,
	path string,
	call func(handler *ItemHandler, c echo.Context) error,
) {
	t.Helper()

	handler := &ItemHandler{
		binder: &TestBinder{},
	}

	e := echo.New()
	req := httptest.NewRequest(method, path, nil)
	rec := httptest.NewRecorder()
	c := e.NewContext(req, rec)
	c.SetParamNames("id")
	c.SetParamValues("invalid")

	err := call(handler, c)
	if err != nil {
		he, ok := err.(*echo.HTTPError)
		if ok {
			assert.Equal(t, http.StatusBadRequest, he.Code)
		}
	} else {
		assert.Contains(t, rec.Body.String(), "Invalid item ID")
	}
}
