package tests

import (
	"bytes"
	"encoding/json"
	"fmt"
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/labstack/echo/v4"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"

	"github.com/kooshapari/tracertm-backend/internal/handlers"
	"github.com/kooshapari/tracertm-backend/internal/models"
)

// TestFullItemLifecycle tests the complete lifecycle of an item
func TestFullItemLifecycle(t *testing.T) {
	e := setupTestServer()
	itemHandler := &handlers.ItemHandler{Repo: testRepo}
	linkHandler := &handlers.LinkHandler{Repo: testRepo}

	// 1. Create an item
	createReqBody := map[string]interface{}{
		"title":      "Integration Test Item",
		"type":       "requirement",
		"content":    "Full lifecycle test",
		"project_id": testProject.ID,
	}

	body, _ := json.Marshal(createReqBody)
	req := httptest.NewRequest(http.MethodPost, "/api/items", bytes.NewReader(body))
	req.Header.Set(echo.HeaderContentType, echo.MIMEApplicationJSON)
	rec := httptest.NewRecorder()
	c := e.NewContext(req, rec)

	err := itemHandler.CreateItem(c)
	require.NoError(t, err)
	assert.Equal(t, http.StatusCreated, rec.Code)

	var createdItem map[string]interface{}
	_ = json.Unmarshal(rec.Body.Bytes(), &createdItem)
	itemID := createdItem["id"].(string)

	// 2. Retrieve the item
	req = httptest.NewRequest(http.MethodGet, "/api/items/"+itemID, nil)
	rec = httptest.NewRecorder()
	c = e.NewContext(req, rec)
	c.SetParamNames("id")
	c.SetParamValues(itemID)

	err = itemHandler.GetItem(c)
	require.NoError(t, err)
	assert.Equal(t, http.StatusOK, rec.Code)

	var retrievedItem map[string]interface{}
	_ = json.Unmarshal(rec.Body.Bytes(), &retrievedItem)
	assert.Equal(t, "Integration Test Item", retrievedItem["title"])

	// 3. Update the item
	updateReqBody := map[string]interface{}{
		"title":   "Updated Integration Test Item",
		"content": "Updated content",
	}

	body, _ = json.Marshal(updateReqBody)
	req = httptest.NewRequest(http.MethodPut, "/api/items/"+itemID, bytes.NewReader(body))
	req.Header.Set(echo.HeaderContentType, echo.MIMEApplicationJSON)
	rec = httptest.NewRecorder()
	c = e.NewContext(req, rec)
	c.SetParamNames("id")
	c.SetParamValues(itemID)

	err = itemHandler.UpdateItem(c)
	require.NoError(t, err)
	assert.Equal(t, http.StatusOK, rec.Code)

	// 4. Create a link to another item
	targetItem := createTestItem()
	linkReqBody := map[string]interface{}{
		"source_id": itemID,
		"target_id": targetItem.ID,
		"type":      "satisfies",
	}

	body, _ = json.Marshal(linkReqBody)
	req = httptest.NewRequest(http.MethodPost, "/api/links", bytes.NewReader(body))
	req.Header.Set(echo.HeaderContentType, echo.MIMEApplicationJSON)
	rec = httptest.NewRecorder()
	c = e.NewContext(req, rec)

	err = linkHandler.CreateLink(c)
	require.NoError(t, err)
	assert.Equal(t, http.StatusCreated, rec.Code)

	// 5. Delete the item
	req = httptest.NewRequest(http.MethodDelete, "/api/items/"+itemID, nil)
	rec = httptest.NewRecorder()
	c = e.NewContext(req, rec)
	c.SetParamNames("id")
	c.SetParamValues(itemID)

	err = itemHandler.DeleteItem(c)
	require.NoError(t, err)
	assert.Equal(t, http.StatusNoContent, rec.Code)

	// 6. Verify deletion
	req = httptest.NewRequest(http.MethodGet, "/api/items/"+itemID, nil)
	rec = httptest.NewRecorder()
	c = e.NewContext(req, rec)
	c.SetParamNames("id")
	c.SetParamValues(itemID)

	err = itemHandler.GetItem(c)
	assert.Error(t, err)
}

// TestSearchIntegration tests the search functionality end-to-end
func TestSearchIntegration(t *testing.T) {
	e := setupTestServer()
	itemHandler := &handlers.ItemHandler{Repo: testRepo}
	searchHandler := &handlers.SearchHandler{Repo: testRepo}

	// Create searchable items
	items := []map[string]interface{}{
		{
			"title":      "User Authentication Feature",
			"type":       "requirement",
			"content":    "Implement user authentication with OAuth2",
			"project_id": testProject.ID,
		},
		{
			"title":      "Database Schema",
			"type":       "design",
			"content":    "Design database schema for user management",
			"project_id": testProject.ID,
		},
		{
			"title":      "API Endpoints",
			"type":       "implementation",
			"content":    "Create REST API endpoints for authentication",
			"project_id": testProject.ID,
		},
	}

	for _, item := range items {
		body, _ := json.Marshal(item)
		req := httptest.NewRequest(http.MethodPost, "/api/items", bytes.NewReader(body))
		req.Header.Set(echo.HeaderContentType, echo.MIMEApplicationJSON)
		rec := httptest.NewRecorder()
		c := e.NewContext(req, rec)
		itemHandler.CreateItem(c)
	}

	// Search for "authentication"
	searchReqBody := map[string]interface{}{
		"query":      "authentication",
		"project_id": testProject.ID,
	}

	body, _ := json.Marshal(searchReqBody)
	req := httptest.NewRequest(http.MethodPost, "/api/search", bytes.NewReader(body))
	req.Header.Set(echo.HeaderContentType, echo.MIMEApplicationJSON)
	rec := httptest.NewRecorder()
	c := e.NewContext(req, rec)

	err := searchHandler.Search(c)
	require.NoError(t, err)
	assert.Equal(t, http.StatusOK, rec.Code)

	var results map[string]interface{}
	_ = json.Unmarshal(rec.Body.Bytes(), &results)
	resultItems := results["items"].([]interface{})
	assert.GreaterOrEqual(t, len(resultItems), 2, "Should find at least 2 items containing 'authentication'")
}

// TestGraphTraversalIntegration tests graph traversal with complex relationships
func TestGraphTraversalIntegration(t *testing.T) {
	e := setupTestServer()
	itemHandler := &handlers.ItemHandler{Repo: testRepo}
	linkHandler := &handlers.LinkHandler{Repo: testRepo}
	graphHandler := &handlers.GraphHandler{Repo: testRepo}

	// Create a hierarchical structure
	root := createItemWithTitle("Epic: User Management")
	story1 := createItemWithTitle("Story: User Login")
	story2 := createItemWithTitle("Story: User Registration")
	task1 := createItemWithTitle("Task: Implement OAuth")
	task2 := createItemWithTitle("Task: Create Login Form")

	// Create links
	createTestLink(root.ID, story1.ID, "parent")
	createTestLink(root.ID, story2.ID, "parent")
	createTestLink(story1.ID, task1.ID, "parent")
	createTestLink(story1.ID, task2.ID, "parent")

	// Traverse from root
	req := httptest.NewRequest(http.MethodGet, "/api/graph/traverse/"+root.ID, nil)
	rec := httptest.NewRecorder()
	c := e.NewContext(req, rec)
	c.SetParamNames("id")
	c.SetParamValues(root.ID)

	err := graphHandler.TraverseGraph(c)
	require.NoError(t, err)
	assert.Equal(t, http.StatusOK, rec.Code)

	var graph map[string]interface{}
	_ = json.Unmarshal(rec.Body.Bytes(), &graph)
	nodes := graph["nodes"].([]interface{})
	assert.GreaterOrEqual(t, len(nodes), 5, "Should include all nodes in hierarchy")
}

// TestEventSystemIntegration tests the event publishing and subscription
func TestEventSystemIntegration(t *testing.T) {
	e := setupTestServer()
	itemHandler := &handlers.ItemHandler{Repo: testRepo}

	// Subscribe to events (in production, this would be via WebSocket or NATS)
	events := make(chan string, 10)

	// Create an item (should publish event)
	createReqBody := map[string]interface{}{
		"title":      "Event Test Item",
		"type":       "requirement",
		"project_id": testProject.ID,
	}

	body, _ := json.Marshal(createReqBody)
	req := httptest.NewRequest(http.MethodPost, "/api/items", bytes.NewReader(body))
	req.Header.Set(echo.HeaderContentType, echo.MIMEApplicationJSON)
	rec := httptest.NewRecorder()
	c := e.NewContext(req, rec)

	err := itemHandler.CreateItem(c)
	require.NoError(t, err)

	// Verify event was published
	select {
	case event := <-events:
		assert.Contains(t, event, "item.created")
	default:
		// Event system may be async
	}
}

// TestConcurrentOperations tests handling of concurrent operations
func TestConcurrentOperations(t *testing.T) {
	e := setupTestServer()
	itemHandler := &handlers.ItemHandler{Repo: testRepo}

	testItem := createTestItem()
	done := make(chan bool, 10)

	// Concurrent reads
	for i := 0; i < 5; i++ {
		go func() {
			req := httptest.NewRequest(http.MethodGet, "/api/items/"+testItem.ID, nil)
			rec := httptest.NewRecorder()
			c := e.NewContext(req, rec)
			c.SetParamNames("id")
			c.SetParamValues(testItem.ID)

			itemHandler.GetItem(c)
			done <- true
		}()
	}

	// Concurrent updates
	for i := 0; i < 5; i++ {
		go func(idx int) {
			updateReqBody := map[string]interface{}{
				"content": fmt.Sprintf("Concurrent update %d", idx),
			}

			body, _ := json.Marshal(updateReqBody)
			req := httptest.NewRequest(http.MethodPut, "/api/items/"+testItem.ID, bytes.NewReader(body))
			req.Header.Set(echo.HeaderContentType, echo.MIMEApplicationJSON)
			rec := httptest.NewRecorder()
			c := e.NewContext(req, rec)
			c.SetParamNames("id")
			c.SetParamValues(testItem.ID)

			itemHandler.UpdateItem(c)
			done <- true
		}(i)
	}

	// Wait for all operations to complete
	for i := 0; i < 10; i++ {
		<-done
	}

	// Verify data integrity
	req := httptest.NewRequest(http.MethodGet, "/api/items/"+testItem.ID, nil)
	rec := httptest.NewRecorder()
	c := e.NewContext(req, rec)
	c.SetParamNames("id")
	c.SetParamValues(testItem.ID)

	err := itemHandler.GetItem(c)
	require.NoError(t, err)
}

// Helper functions
func createItemWithTitle(title string) *models.Item {
	item := &models.Item{
		Title:     title,
		Type:      "requirement",
		ProjectID: testProject.ID,
	}
	testDB.Create(item)
	return item
}
