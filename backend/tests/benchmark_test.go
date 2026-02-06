package tests

import (
	"bytes"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/labstack/echo/v4"

	"github.com/kooshapari/tracertm-backend/internal/handlers"
)

// BenchmarkCreateItem benchmarks the item creation endpoint
func BenchmarkCreateItem(b *testing.B) {
	e := setupTestServer()
	handler := &handlers.ItemHandler{Repo: testRepo}

	reqBody := map[string]interface{}{
		"title":      "Benchmark Item",
		"type":       "requirement",
		"content":    "This is a benchmark test item",
		"project_id": testProject.ID,
	}

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		body, _ := json.Marshal(reqBody)
		req := httptest.NewRequest(http.MethodPost, "/api/items", bytes.NewReader(body))
		req.Header.Set(echo.HeaderContentType, echo.MIMEApplicationJSON)
		rec := httptest.NewRecorder()
		c := e.NewContext(req, rec)

		handler.CreateItem(c)
	}
}

// BenchmarkGetItem benchmarks the item retrieval endpoint
func BenchmarkGetItem(b *testing.B) {
	e := setupTestServer()
	handler := &handlers.ItemHandler{Repo: testRepo}

	// Create a test item
	testItem := createTestItem()

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		req := httptest.NewRequest(http.MethodGet, "/api/items/"+testItem.ID, nil)
		rec := httptest.NewRecorder()
		c := e.NewContext(req, rec)
		c.SetParamNames("id")
		c.SetParamValues(testItem.ID)

		handler.GetItem(c)
	}
}

// BenchmarkListItems benchmarks the item listing endpoint
func BenchmarkListItems(b *testing.B) {
	e := setupTestServer()
	handler := &handlers.ItemHandler{Repo: testRepo}

	// Create test items
	for i := 0; i < 100; i++ {
		createTestItem()
	}

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		req := httptest.NewRequest(http.MethodGet, "/api/items?project_id="+testProject.ID, nil)
		rec := httptest.NewRecorder()
		c := e.NewContext(req, rec)

		handler.ListItems(c)
	}
}

// BenchmarkSearch benchmarks the search endpoint
func BenchmarkSearch(b *testing.B) {
	e := setupTestServer()
	handler := &handlers.SearchHandler{Repo: testRepo}

	// Create searchable items
	for i := 0; i < 100; i++ {
		createTestItem()
	}

	reqBody := map[string]interface{}{
		"query":      "benchmark",
		"project_id": testProject.ID,
	}

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		body, _ := json.Marshal(reqBody)
		req := httptest.NewRequest(http.MethodPost, "/api/search", bytes.NewReader(body))
		req.Header.Set(echo.HeaderContentType, echo.MIMEApplicationJSON)
		rec := httptest.NewRecorder()
		c := e.NewContext(req, rec)

		handler.Search(c)
	}
}

// BenchmarkCreateLink benchmarks the link creation endpoint
func BenchmarkCreateLink(b *testing.B) {
	e := setupTestServer()
	handler := &handlers.LinkHandler{Repo: testRepo}

	source := createTestItem()
	target := createTestItem()

	reqBody := map[string]interface{}{
		"source_id": source.ID,
		"target_id": target.ID,
		"type":      "satisfies",
	}

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		body, _ := json.Marshal(reqBody)
		req := httptest.NewRequest(http.MethodPost, "/api/links", bytes.NewReader(body))
		req.Header.Set(echo.HeaderContentType, echo.MIMEApplicationJSON)
		rec := httptest.NewRecorder()
		c := e.NewContext(req, rec)

		handler.CreateLink(c)
	}
}

// BenchmarkGraphTraversal benchmarks the graph traversal endpoint
func BenchmarkGraphTraversal(b *testing.B) {
	e := setupTestServer()
	handler := &handlers.GraphHandler{Repo: testRepo}

	// Create a small graph
	root := createTestItem()
	for i := 0; i < 10; i++ {
		child := createTestItem()
		createTestLink(root.ID, child.ID, "parent")
	}

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		req := httptest.NewRequest(http.MethodGet, "/api/graph/traverse/"+root.ID, nil)
		rec := httptest.NewRecorder()
		c := e.NewContext(req, rec)
		c.SetParamNames("id")
		c.SetParamValues(root.ID)

		handler.TraverseGraph(c)
	}
}

// BenchmarkConcurrentReads benchmarks concurrent read operations
func BenchmarkConcurrentReads(b *testing.B) {
	e := setupTestServer()
	handler := &handlers.ItemHandler{Repo: testRepo}

	testItem := createTestItem()

	b.RunParallel(func(pb *testing.PB) {
		for pb.Next() {
			req := httptest.NewRequest(http.MethodGet, "/api/items/"+testItem.ID, nil)
			rec := httptest.NewRecorder()
			c := e.NewContext(req, rec)
			c.SetParamNames("id")
			c.SetParamValues(testItem.ID)

			handler.GetItem(c)
		}
	})
}

// BenchmarkConcurrentWrites benchmarks concurrent write operations
func BenchmarkConcurrentWrites(b *testing.B) {
	e := setupTestServer()
	handler := &handlers.ItemHandler{Repo: testRepo}

	reqBody := map[string]interface{}{
		"title":      "Concurrent Item",
		"type":       "requirement",
		"content":    "Concurrent write test",
		"project_id": testProject.ID,
	}

	b.RunParallel(func(pb *testing.PB) {
		for pb.Next() {
			body, _ := json.Marshal(reqBody)
			req := httptest.NewRequest(http.MethodPost, "/api/items", bytes.NewReader(body))
			req.Header.Set(echo.HeaderContentType, echo.MIMEApplicationJSON)
			rec := httptest.NewRecorder()
			c := e.NewContext(req, rec)

			handler.CreateItem(c)
		}
	})
}
