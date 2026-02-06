//go:build !integration && !e2e

package handlers

import (
	"bytes"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"

	"github.com/jackc/pgx/v5/pgxpool"
	"github.com/labstack/echo/v4"
	"github.com/stretchr/testify/assert"
)

// Note: setupSearchHandler requires real *pgxpool.Pool
// For unit tests, we'll test handlers that don't require database operations
// Database-dependent tests should be integration tests

// setupSearchHandlerForIntegration is kept for future integration tests
//
//nolint:unused // This function is used for integration tests
func setupSearchHandlerForIntegration(_ *testing.T, pool *pgxpool.Pool) *SearchHandler {
	// SearchHandler now requires SearchService
	// For integration tests, should use real service
	_ = pool // unused
	return NewSearchHandler(
		nil, // SearchService - should use mock or real service
	)
}

func TestSearchHandler_Search_Integration(t *testing.T) {
	// These tests require a real database pool
	t.Skip("Requires real database pool - integration test")
}

func TestSearchHandler_Search_Validation(t *testing.T) {
	e := echo.New()

	t.Run("invalid JSON", func(_ *testing.T) {
		// Test validation without database
		handler := &SearchHandler{} // Minimal handler for validation tests

		req := httptest.NewRequest(http.MethodPost, "/search", bytes.NewReader([]byte("invalid json")))
		req.Header.Set(echo.HeaderContentType, echo.MIMEApplicationJSON)
		rec := httptest.NewRecorder()
		c := e.NewContext(req, rec)

		err := handler.Search(c)
		// Bind should fail with invalid JSON
		if err != nil {
			he, ok := err.(*echo.HTTPError)
			if ok {
				assert.Equal(t, http.StatusBadRequest, he.Code)
			}
		} else {
			assert.Contains(t, rec.Body.String(), "error")
		}
	})

	t.Run("empty query validation", func(_ *testing.T) {
		handler := &SearchHandler{} // Minimal handler for validation tests

		reqBody := map[string]interface{}{
			"query": "",
		}
		bodyBytes, _ := json.Marshal(reqBody)
		req := httptest.NewRequest(http.MethodPost, "/search", bytes.NewReader(bodyBytes))
		req.Header.Set(echo.HeaderContentType, echo.MIMEApplicationJSON)
		rec := httptest.NewRecorder()
		c := e.NewContext(req, rec)

		err := handler.Search(c)
		// Should return 400 for empty query
		if err != nil {
			he, ok := err.(*echo.HTTPError)
			if ok {
				assert.Equal(t, http.StatusBadRequest, he.Code)
			}
		} else {
			assert.Contains(t, rec.Body.String(), "Query parameter is required")
		}
	})
}

func TestSearchHandler_SearchGet_Validation(t *testing.T) {
	e := echo.New()

	t.Run("missing query parameter", func(_ *testing.T) {
		handler := &SearchHandler{}

		req := httptest.NewRequest(http.MethodGet, "/search", nil)
		rec := httptest.NewRecorder()
		c := e.NewContext(req, rec)

		err := handler.SearchGet(c)
		// Should return 400 for missing query parameter
		if err != nil {
			he, ok := err.(*echo.HTTPError)
			if ok {
				assert.Equal(t, http.StatusBadRequest, he.Code)
			}
		} else {
			assert.Contains(t, rec.Body.String(), "Query parameter 'q' is required")
		}
	})
}

func TestSearchHandler_Suggest_Validation(t *testing.T) {
	e := echo.New()

	t.Run("missing prefix", func(_ *testing.T) {
		handler := &SearchHandler{}

		req := httptest.NewRequest(http.MethodGet, "/search/suggest", nil)
		rec := httptest.NewRecorder()
		c := e.NewContext(req, rec)

		err := handler.Suggest(c)
		// Handler validates prefix and returns 400 if missing
		// It may return error or set response directly
		if err != nil {
			he, ok := err.(*echo.HTTPError)
			if ok {
				assert.Equal(t, http.StatusBadRequest, he.Code)
			}
		} else {
			// Check response code and body (case-insensitive)
			assert.Equal(t, http.StatusBadRequest, rec.Code)
			assert.Contains(t, strings.ToLower(rec.Body.String()), "prefix")
		}
	})
}

func TestSearchHandler_IndexItem_Validation(t *testing.T) {
	e := echo.New()

	t.Run("missing item ID", func(_ *testing.T) {
		handler := &SearchHandler{}

		req := httptest.NewRequest(http.MethodPost, "/search/index/", nil)
		rec := httptest.NewRecorder()
		c := e.NewContext(req, rec)
		c.SetPath("/search/index/:id")
		c.SetParamNames("id")
		c.SetParamValues("")

		err := handler.IndexItem(c)
		// Should return 400 for missing/invalid item ID
		if err != nil {
			he, ok := err.(*echo.HTTPError)
			if ok {
				assert.Equal(t, http.StatusBadRequest, he.Code)
			}
		} else {
			assert.Equal(t, http.StatusBadRequest, rec.Code)
			assert.Contains(t, rec.Body.String(), "error")
		}
	})
}

func TestSearchHandler_ReindexAll_Integration(t *testing.T) {
	t.Skip("Requires real database pool - integration test")
}

func TestSearchHandler_IndexStats_Integration(t *testing.T) {
	t.Skip("Requires real database pool - integration test")
}

func TestSearchHandler_SearchHealth_Integration(t *testing.T) {
	t.Skip("Requires real database pool - integration test")
}

func TestSearchHandler_BatchIndex_Validation(t *testing.T) {
	e := echo.New()

	t.Run("empty item IDs", func(_ *testing.T) {
		handler := &SearchHandler{}

		reqBody := map[string]interface{}{
			"item_ids": []string{},
		}
		bodyBytes, _ := json.Marshal(reqBody)

		req := httptest.NewRequest(http.MethodPost, "/search/batch-index", bytes.NewReader(bodyBytes))
		req.Header.Set(echo.HeaderContentType, echo.MIMEApplicationJSON)
		rec := httptest.NewRecorder()
		c := e.NewContext(req, rec)

		err := handler.BatchIndex(c)
		// Should return 400 for empty item IDs
		if err != nil {
			he, ok := err.(*echo.HTTPError)
			if ok {
				assert.Equal(t, http.StatusBadRequest, he.Code)
			}
		} else {
			assert.Equal(t, http.StatusBadRequest, rec.Code)
			assert.Contains(t, rec.Body.String(), "error")
		}
	})

	t.Run("too many items", func(_ *testing.T) {
		handler := &SearchHandler{}

		itemIDs := make([]string, 101)
		for i := range itemIDs {
			itemIDs[i] = "item"
		}

		reqBody := map[string]interface{}{
			"item_ids": itemIDs,
		}
		bodyBytes, _ := json.Marshal(reqBody)

		req := httptest.NewRequest(http.MethodPost, "/search/batch-index", bytes.NewReader(bodyBytes))
		req.Header.Set(echo.HeaderContentType, echo.MIMEApplicationJSON)
		rec := httptest.NewRecorder()
		c := e.NewContext(req, rec)

		err := handler.BatchIndex(c)
		// Should return 400 for too many items
		if err != nil {
			he, ok := err.(*echo.HTTPError)
			if ok {
				assert.Equal(t, http.StatusBadRequest, he.Code)
			}
		} else {
			assert.Equal(t, http.StatusBadRequest, rec.Code)
			assert.Contains(t, rec.Body.String(), "error")
		}
	})
}

func TestSearchHandler_DeleteIndex_Validation(t *testing.T) {
	e := echo.New()

	t.Run("missing item ID", func(_ *testing.T) {
		handler := &SearchHandler{}

		req := httptest.NewRequest(http.MethodDelete, "/search/index/", nil)
		rec := httptest.NewRecorder()
		c := e.NewContext(req, rec)
		c.SetPath("/search/index/:id")
		c.SetParamNames("id")
		c.SetParamValues("")

		err := handler.DeleteIndex(c)
		// Should return 400 for missing/invalid item ID
		if err != nil {
			he, ok := err.(*echo.HTTPError)
			if ok {
				assert.Equal(t, http.StatusBadRequest, he.Code)
			}
		} else {
			assert.Equal(t, http.StatusBadRequest, rec.Code)
			assert.Contains(t, rec.Body.String(), "error")
		}
	})
}

/* DISABLED - getSearchCacheKey method removed
func TestSearchHandler_getSearchCacheKey(t *testing.T) {
	handler := &SearchHandler{}

	t.Run("basic key", func(_ *testing.T) {
		req := &search.Request{
			Query:     "test",
			Type:      search.TypeFullText,
			ProjectID: "project1",
		}

		key := handler.getSearchCacheKey(req)
		assert.Contains(t, key, "test")
		assert.Contains(t, key, "fulltext")
		assert.Contains(t, key, "project1")
	})

	t.Run("with filters", func(_ *testing.T) {
		req := &search.Request{
			Query:     "test",
			Type:      search.TypeFullText,
			ProjectID: "project1",
			ItemTypes: []string{"requirement", "test"},
			Status:    []string{"todo", "done"},
			Limit:     20,
			Offset:    10,
		}

		key := handler.getSearchCacheKey(req)
		assert.Contains(t, key, "requirement")
		assert.Contains(t, key, "todo")
		assert.Contains(t, key, "20")
		assert.Contains(t, key, "10")
	})
}
*/
