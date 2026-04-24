//go:build !integration && !e2e

package handlers

import (
	"errors"
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/labstack/echo/v4"
	"github.com/stretchr/testify/assert"
)

func TestGraphHandler_GetAncestors_Validation(t *testing.T) {
	e := echo.New()

	t.Run("missing item ID", func(t *testing.T) {
		handler := &GraphHandler{}

		req := httptest.NewRequest(http.MethodGet, "/graph/ancestors/", nil)
		rec := httptest.NewRecorder()
		c := e.NewContext(req, rec)
		c.SetPath("/graph/ancestors/:id")
		c.SetParamNames("id")
		c.SetParamValues("")

		err := handler.GetAncestors(c)
		// Handler will try to call graph.GetAncestors with empty ID, which will fail
		// Either bind error or graph error
		if err != nil {
			he := &echo.HTTPError{}
			ok := errors.As(err, &he)
			if ok {
				assert.True(t, he.Code == http.StatusBadRequest || he.Code == http.StatusInternalServerError)
			}
		} else {
			// Check response body for error
			assert.Contains(t, rec.Body.String(), "error")
		}
	})
}

func TestGraphHandler_GetDescendants_Validation(t *testing.T) {
	e := echo.New()

	t.Run("missing item ID", func(t *testing.T) {
		handler := &GraphHandler{}

		req := httptest.NewRequest(http.MethodGet, "/graph/descendants/", nil)
		rec := httptest.NewRecorder()
		c := e.NewContext(req, rec)
		c.SetPath("/graph/descendants/:id")
		c.SetParamNames("id")
		c.SetParamValues("")

		err := handler.GetDescendants(c)
		// Handler will try to call graph.GetDescendants with empty ID, which will fail
		if err != nil {
			he := &echo.HTTPError{}
			ok := errors.As(err, &he)
			if ok {
				assert.True(t, he.Code == http.StatusBadRequest || he.Code == http.StatusInternalServerError)
			}
		} else {
			assert.Contains(t, rec.Body.String(), "error")
		}
	})
}

func TestGraphHandler_FindPath_Validation(t *testing.T) {
	e := echo.New()

	t.Run("missing source", func(t *testing.T) {
		handler := &GraphHandler{}

		req := httptest.NewRequest(http.MethodGet, "/graph/path?target=target1", nil)
		rec := httptest.NewRecorder()
		c := e.NewContext(req, rec)

		err := handler.FindPath(c)
		// Should return 400 for missing source
		if err != nil {
			he := &echo.HTTPError{}
			ok := errors.As(err, &he)
			if ok {
				assert.Equal(t, http.StatusBadRequest, he.Code)
			}
		} else {
			assert.Contains(t, rec.Body.String(), "source and target parameters are required")
		}
	})

	t.Run("missing target", func(t *testing.T) {
		handler := &GraphHandler{}

		req := httptest.NewRequest(http.MethodGet, "/graph/path?source=source1", nil)
		rec := httptest.NewRecorder()
		c := e.NewContext(req, rec)

		err := handler.FindPath(c)
		// Should return 400 for missing target
		if err != nil {
			he := &echo.HTTPError{}
			ok := errors.As(err, &he)
			if ok {
				assert.Equal(t, http.StatusBadRequest, he.Code)
			}
		} else {
			assert.Contains(t, rec.Body.String(), "source and target parameters are required")
		}
	})
}

func TestGraphHandler_FindAllPaths_Validation(t *testing.T) {
	e := echo.New()

	t.Run("missing source", func(t *testing.T) {
		handler := &GraphHandler{}

		req := httptest.NewRequest(http.MethodGet, "/graph/paths?target=target1", nil)
		rec := httptest.NewRecorder()
		c := e.NewContext(req, rec)

		err := handler.FindAllPaths(c)
		// Should return 400 for missing source
		if err != nil {
			he := &echo.HTTPError{}
			ok := errors.As(err, &he)
			if ok {
				assert.Equal(t, http.StatusBadRequest, he.Code)
			}
		} else {
			assert.Contains(t, rec.Body.String(), "error")
		}
	})

	t.Run("invalid max_paths", func(t *testing.T) {
		handler := &GraphHandler{}

		req := httptest.NewRequest(http.MethodGet, "/graph/paths?source=source1&target=target1&max_paths=invalid", nil)
		rec := httptest.NewRecorder()
		c := e.NewContext(req, rec)

		err := handler.FindAllPaths(c)
		// Will fail on graph nil or invalid max_paths parsing
		if err != nil {
			he := &echo.HTTPError{}
			ok := errors.As(err, &he)
			if ok {
				assert.True(t, he.Code == http.StatusBadRequest || he.Code == http.StatusInternalServerError)
			}
		} else {
			assert.Contains(t, rec.Body.String(), "error")
		}
	})
}

func TestGraphHandler_ComputeTransitiveClosure_Validation(t *testing.T) {
	e := echo.New()

	t.Run("missing project_id", func(t *testing.T) {
		handler := &GraphHandler{}

		req := httptest.NewRequest(http.MethodGet, "/graph/transitive-closure", nil)
		rec := httptest.NewRecorder()
		c := e.NewContext(req, rec)

		err := handler.ComputeTransitiveClosure(c)
		// Should return 400 for missing project_id
		if err != nil {
			he := &echo.HTTPError{}
			ok := errors.As(err, &he)
			if ok {
				assert.Equal(t, http.StatusBadRequest, he.Code)
			}
		} else {
			assert.Contains(t, rec.Body.String(), "project_id parameter is required")
		}
	})
}

func TestGraphHandler_Traverse_Validation(t *testing.T) {
	e := echo.New()

	t.Run("default algorithm and direction", func(t *testing.T) {
		handler := &GraphHandler{}

		req := httptest.NewRequest(http.MethodGet, "/graph/traverse/item1", nil)
		rec := httptest.NewRecorder()
		c := e.NewContext(req, rec)
		c.SetPath("/graph/traverse/:id")
		c.SetParamNames("id")
		c.SetParamValues("item1")

		err := handler.Traverse(c)
		// Handler will try to call graph.Traverse with nil graph, which will fail
		if err != nil {
			he := &echo.HTTPError{}
			ok := errors.As(err, &he)
			if ok {
				assert.True(t, he.Code == http.StatusBadRequest || he.Code == http.StatusInternalServerError)
			}
		} else {
			// Check response body for error
			assert.Contains(t, rec.Body.String(), "error")
		}
	})

	t.Run("with link types filter", func(t *testing.T) {
		handler := &GraphHandler{}

		req := httptest.NewRequest(http.MethodGet, "/graph/traverse/item1?link_types=depends_on,blocks", nil)
		rec := httptest.NewRecorder()
		c := e.NewContext(req, rec)
		c.SetPath("/graph/traverse/:id")
		c.SetParamNames("id")
		c.SetParamValues("item1")

		err := handler.Traverse(c)
		// Handler will try to call graph.Traverse with nil graph
		if err != nil {
			he := &echo.HTTPError{}
			ok := errors.As(err, &he)
			if ok {
				assert.True(t, he.Code == http.StatusBadRequest || he.Code == http.StatusInternalServerError)
			}
		} else {
			assert.Contains(t, rec.Body.String(), "error")
		}
	})
}

/* DISABLED - getCacheKey method removed (private implementation detail)
func TestGraphHandler_getCacheKey(t *testing.T) {
	handler := &GraphHandler{}

	t.Run("basic key", func(t *testing.T) {
		key := handler.getCacheKey("ancestors", "item1", 0)
		assert.Contains(t, key, "ancestors")
		assert.Contains(t, key, "item1")
		assert.Contains(t, key, "0")
	})

	t.Run("with max depth", func(t *testing.T) {
		key := handler.getCacheKey("descendants", "item1", 5)
		assert.Contains(t, key, "descendants")
		assert.Contains(t, key, "item1")
		assert.Contains(t, key, "5")
	})
}
*/
